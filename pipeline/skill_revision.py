"""The daily job that makes "revised when the research moves" true.

    modal run pipeline/skill_revision.py::preflight     # gate: read everything, write nothing
    modal deploy pipeline/skill_revision.py             # then, and only then, deploy

    modal run pipeline/skill_revision.py                # manual run
    modal run pipeline/skill_revision.py --dry-run      # what it would do, and nothing else

ADR-36 and ADR-37, both accepted 2026-09-29. The site says a skill is revised
when the research moves and retired with an explanation when it is overturned.
The view that would find those skills, `skills_needing_revision`, has existed in
`db/schema.sql` since the founding and has never returned a row, because it joins
`promotions` and nothing ever registered a skill. Seven claims are deprecated and
no skill knows.

This job closes the loop, once a day, in five steps.

1. **Register.** Every skill on main gets its `promotions` row, derived from its
   own provenance block by `tools/skill_registrar.py`. Missing rows are written
   and stale ones are updated, so a skill merged yesterday is watched today. A
   row that had to be created is itself a finding: it means a merge shipped a
   skill that nothing was watching, and the owner is told.

2. **Review.** All three of ADR-13's reviewers run over the same skills and
   each files its own `panel_verdicts` row per skill.
   `tools/panel_provenance.py` asks whether the claim ids a skill cites exist
   in the corpus and whether it attributes the papers behind them.
   `tools/panel_adversary.py` asks the opposite question: whether the claim
   graph has since contradicted or refined anything the skill cites, and
   whether it was ever asked at all. `tools/panel_validator.py` asks whether a
   trial exists, measured this text, pointed the right way, and was
   pre-registered. All three read and none merges, so the only write is the
   verdict row, and a `fail` from any of them mails the owner for the same
   reason an unregistered skill does. They run here rather than in CI because
   the first two need Neon and CI holds no database credential anywhere.

3. **Run all four triggers.** ADR-37 names four things that make a skill stale
   and the first pass of this job read one of them. `tools/skill_triggers.py`
   computes them all:

       deprecated   a cited claim is the target of a confident contradiction,
                    which is what `skills_needing_revision` returns
       refines      a cited claim gained a `refines` neighbour at confidence
                    0.7 or better, recorded after the skill's version date
       citations    a cited paper's citation count moved by more than 2x, or
                    by 20 or more, between the slow loop's last two checks
       eval         the skill's last eval regressed on the current subject
                    model, or the budget table's subject has moved under it

4. **Queue the reading.** Each new finding is appended to
   `docs/research/reading-queue.md` in the format that file documents, which is
   the same queue the skill seat writes into by hand under ADR-35 and the
   research seat drains. Every line carries a `key:`, and only findings whose
   key the file does not already hold are appended, so a skill that waits a week
   for its revision does not collect seven identical lines.

4. **Dispatch the skill seat once**, with the whole list in its owner
   instructions, and only when step 3 appended something. One dispatch a day
   whatever the trigger count, because a cron that dispatches a seat every day
   about the same unfinished job is a cron nobody reads.

5. **Publish the claim-status snapshot.** `docs/research/claim-status.json` says
   which claim ids exist and which are deprecated, with the date it was
   measured. It exists because the gate in `tools/skill_gate.py` runs in GitHub
   Actions, where this organization holds no database credential at all, and
   ADR-37's gate requires that a revision's provenance resolve to claims that
   exist and are not deprecated. This job is the only thing in the org that can
   answer that question daily, so it writes the answer down with a date on it,
   and a snapshot the gate finds stale is a failing gate rather than a passing
   one. Claim ids are stored as ranges, which keeps a file rewritten daily at a
   few hundred bytes.

## Why this is a Modal job and not a GitHub Action

Because steps 1 to 3 need Neon, and the only place in this organization
that holds a Neon credential unattended is Modal (`pending-workflow-changes`
item 6 is still waiting on a hand for the engineer seat's read-only URL). A
scheduled Action would have to be given a database secret to do the same work.

## Its slot, and why it does not contend

16:00 UTC. `pipeline/llm.py` KIMI_WINDOWS reserves 09:00-11:00 for the press,
12:00-13:00 for triage and 14:00-15:00 for interpret, with 13:00-14:00 kept as
margin, because Moonshot's organization concurrency is 1 and failure 2 of
INC-2026-09-24-press-provider-migration was two Kimi calls at once. This job
calls no model at all, so it cannot collide with any of them, and 16:00 is
chosen to sit after the last one rather than because it has to. It is recorded
in the schedule comment in `pipeline/llm.py` and deliberately NOT added to
KIMI_WINDOWS, because that table is the Kimi concurrency ledger and putting a
job in it that never calls Kimi would make `check_kimi_windows` lie.

## Status: DORMANT until the `github` secret exists

L-A16 in docs/standards/lessons.md: configured is not in effect. Steps 1 to 3
need only the `neon` secret, which exists. Steps 4 and 5 write to GitHub, and
this job holds no GitHub credential today. Without one it does every read, prints
the exact lines it would have appended and the dispatch it would have sent, tells
the owner once, and exits 0. Nothing here has run against a real repository.

Activation is one command by the chair, and the token needs `contents: write` on
this repository plus `actions: write` to dispatch:

    modal secret create github GITHUB_TOKEN=<paste> GITHUB_REPO=alexandrapaiz/alexandria

**One thing in here is an authority the owner has not granted before**, and it
should be read rather than skimmed: step 4 commits to `main` without review.
The reading queue is an append-only ledger and the directive asks for the
append, so that is what this does, but `QUEUE_BRANCH` below is one constant and
setting it to a branch name turns the append into a pull request the skill seat
picks up instead. Say which you want and it is a one-line change.
"""

from __future__ import annotations

import base64
import datetime as dt
import json
import pathlib

import modal

# Where the queue lives, and which branch the append lands on. See the authority
# note in this module's docstring before changing the second one.
QUEUE_PATH = "docs/research/reading-queue.md"
QUEUE_BRANCH = "main"

# Step 5's file. Read by tools/skill_gate.py on every skills-only pull request,
# because CI has no database and ADR-37's gate has a clause about the graph.
SNAPSHOT_PATH = "docs/research/claim-status.json"

# Guardrail 2 of ADR-37's amendment of 2026-09-29: a file at this path on main
# pauses automatic skill maintenance. Any seat may create it with a reason and
# only the owner or the chair removes it. This job is where the loop starts, so
# this is the cheapest place for the switch to be read: no dispatch, no queue
# line, and the run says whose reason stopped it.
PAUSE_PATH = "skills/MAINTENANCE_PAUSED"

# The seat that does the revising, and the input its workflow declares.
SKILL_WORKFLOW = "agent-skill.yml"
DISPATCH_INPUT = "owner_instructions"

# How many pairs one dispatch names. A skill seat run revises one skill (ADR-37:
# revisions before new skills), so a list of thirty is a list it cannot act on.
# The rest are still queued in the file, which is the durable half.
MAX_PAIRS_PER_DISPATCH = 6

# How many triggers one run will queue at all. Four triggers over six skills can
# produce a long list on the day the slow loop refreshes citations, and a queue
# file that grows by forty lines in one morning is a file the research seat stops
# reading. The rest are not lost: they are recomputed tomorrow, because every
# trigger is derived from the corpus rather than from a cursor.
MAX_QUEUED_PER_RUN = 12

# `tools` lands as a directory rather than as loose files on purpose. Both tools
# resolve the repository root as the parent of their own directory, so a file
# copied to /root would compute `/skills` and find nothing, and the trigger that
# reads a skill's eval policy would silently fall back to the default subject.
image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1")
    .add_local_file("tools/skill_registrar.py", "/root/skill_registrar.py")
    .add_local_file("tools/panel_provenance.py", "/root/panel_provenance.py")
    .add_local_file("tools/panel.py", "/root/panel.py")
    .add_local_file("tools/panel_adversary.py", "/root/panel_adversary.py")
    .add_local_file("tools/panel_validator.py", "/root/panel_validator.py")
    # The validator calls tools/skill_eval.py's `gate_problems` rather than
    # keeping a second copy of "why is this result not a pass". That is one
    # import, and this is the line that makes it resolve inside the image.
    # `skill_eval` pulls in no third-party package at module scope, so it costs
    # nothing but the file.
    .add_local_file("tools/skill_eval.py", "/root/skill_eval.py")
    # ADR-37's four triggers, which step 3 runs. It imports `skill_registrar`
    # and `skill_eval`, both already above, and nothing third-party.
    .add_local_file("tools/skill_triggers.py", "/root/skill_triggers.py")
    .add_local_dir("skills", "/root/skills")
)

app = modal.App("alexandria-skill-revision", image=image)


def tools():
    """(registrar, triggers), wherever this is running from.

    Three places, in this order: `/root`, where this image mounts each tool it
    needs as a single file, `/root/tools` for an image that mounted the whole
    directory, and the repository's own `tools/` when a person runs it locally.
    The flat `/root` form is first because it is what the image above actually
    builds, and a missing entry here is an ImportError at 16:00 UTC rather than
    a test failure.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent.parent / "tools")
    for path in ("/root", "/root/tools", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import skill_registrar
    import skill_triggers

    return skill_registrar, skill_triggers


def registrar():
    """Kept because `tests/test_skill_registrar.py` and the first pass call it."""
    return tools()[0]


def _reviewer(module_name: str):
    """A reviewer module, by the same two-path trick as registrar().

    `/root` when Modal built the image, the repository when a person runs this
    locally. Both reviewers and the vocabulary they share are added to the
    image above, so a reviewer that is not in that list fails here loudly
    rather than being skipped quietly.
    """
    import importlib
    import sys

    here = str(pathlib.Path(__file__).resolve().parent.parent / "tools")
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    return importlib.import_module(module_name)


def panel():
    """ADR-13's provenance reviewer, the first of the three."""
    return _reviewer("panel_provenance")


def adversary():
    """ADR-13's adversary, the second. It has no half that runs in CI."""
    return _reviewer("panel_adversary")


def validator():
    """ADR-13's validator, the third, which completes the panel.

    The only one of the three whose verdict needs no credential: every finding
    it makes is a fact about a file in the repository. It still runs here, for
    the reason the other two do, which is that `panel_verdicts` is where a
    verdict is durable and this is the job that holds a writable URL.
    """
    return _reviewer("panel_validator")


# ------------------------------------------------------------ pure functions
# Everything below this line is testable with no database, no network and no
# Modal, which is the only way any of it is tested at all: this organization runs
# no Postgres in CI and the dispatch it sends is a real dispatch.


def paused(gh, ref: str) -> str:
    """The reason maintenance is paused, or an empty string.

    Read from `main` rather than from the image, for the same reason the skills
    are: a switch that only takes effect at the next deploy is not a switch.
    """
    try:
        text, _ = gh.read_file(PAUSE_PATH, ref)
    except RuntimeError:
        return ""
    return " ".join(text.split()) or "no reason given in the file"


def pair_key(skill_path: str, claim_id: int) -> str:
    return f"{skill_path}#{claim_id}"


def as_records(rows: list[dict]) -> list[dict]:
    """Legacy `skills_needing_revision` dicts, or records, as records.

    The first pass of this job passed the view's rows around directly and its
    tests still do. `tools/skill_triggers.py` is the one place that knows what a
    finding looks like now, so everything here converts and delegates rather
    than keeping a second format alive.
    """
    _, triggers = tools()
    out = []
    for row in rows:
        if "trigger" in row:
            out.append(row)
            continue
        out.append(triggers.deprecated_record(
            row["skill_path"], row["deprecated_claim_id"],
            row.get("deprecated_claim") or ""))
    return out


def queue_line(skill_path: str, claim_id: int, claim: str, today: str) -> str:
    """One line in the format `docs/research/reading-queue.md` documents.

    That file's format is `- [ ] arxiv:<id> \u2014 why \u2014 asked by
    skills/<slug> \u2014 YYYY-MM-DD`, and `pipeline/reading_queue.py` reads it: a
    line with an arXiv id is a paper to fetch and a line without one is a
    question for the research seat. No line this job writes carries an arXiv id,
    and for the deprecated trigger the reason is that the paper which deprecated
    the claim is not known here. Finding it is the reading, and inventing an id
    would put a fetch request in front of distill for a paper nobody named. For
    the citation trigger the reason is the opposite one: the paper is already in
    the corpus, so naming it as an id would ask distill to fetch what it has.
    """
    _, triggers = tools()
    return triggers.line(
        triggers.deprecated_record(skill_path, claim_id, claim), today)


def new_pairs(queue_text: str, rows: list[dict]) -> list[dict]:
    """The findings this file does not already carry.

    Idempotence lives in `skill_triggers.fresh` and nowhere else. The match is on
    the finding's key rather than on the whole line, because the evidence text in
    the line may be truncated or may have been edited by whoever struck the line,
    and a line struck with an `[x]` still counts as carried: the research seat
    has already read it.
    """
    _, triggers = tools()
    keep = {r["key"] for r in triggers.fresh(queue_text, as_records(rows))}
    out, seen = [], set()
    for row, rec in zip(rows, as_records(rows)):
        if rec["key"] in keep and rec["key"] not in seen:
            seen.add(rec["key"])
            out.append(row)
    return out


def queue_block(pairs: list[dict], today: str) -> str:
    """The section appended to the queue, heading and all."""
    _, triggers = tools()
    return triggers.block(as_records(pairs), today)


def dispatch_instructions(pairs: list[dict], today: str) -> str:
    """The owner instructions the skill seat's run receives.

    One dispatch a day, whatever the trigger count, with the whole list in it.
    """
    _, triggers = tools()
    records = as_records(pairs)
    named = records[:MAX_PAIRS_PER_DISPATCH]
    counts = {}
    for rec in records:
        counts[rec["trigger"]] = counts.get(rec["trigger"], 0) + 1
    body = [
        f"Automated maintenance dispatch, {today}, from "
        "pipeline/skill_revision.py under ADR-36 and ADR-37. Read ADR-37 in "
        "docs/decisions.md first: a revision outranks a new skill.",
        "",
        "The four triggers ADR-37 names found "
        + ", ".join(f"{n} {triggers.LABELS[t]}"
                    for t, n in sorted(counts.items(),
                                       key=lambda kv: triggers.TRIGGERS.index(kv[0])))
        + ". The same lines were appended to docs/research/reading-queue.md "
        "this run, each with the key that stops it being queued twice.",
        "",
    ]
    for rec in named:
        body.append(f"- [{rec['trigger']}] {rec['skill_path']}: "
                    f"{rec['evidence']}")
    if len(records) > len(named):
        body += ["", f"{len(records) - len(named)} further findings are in the "
                 "queue file and are not named here, because one run revises "
                 "one skill."]
    body += [
        "",
        "Before you accept a trigger, check it. The research seat's brief of "
        "2026-09-28 judged four of the six `contradicts` edges in the graph "
        "wrong, mostly same-paper co-reported results read as refutations. A "
        "deprecation that is itself a misclassification is a finding about the "
        "graph, not a reason to rewrite a skill. The same caution applies to a "
        "`refines` edge and to a citation count that moved because Semantic "
        "Scholar merged two records. Say which one you found, and re-run the "
        "skill's eval either way (ADR-36).",
        "",
        "Your pull request carries the before and after eval result, the "
        "trigger in the version history, and nothing outside skills/<slug>/. "
        "That last one is not style: it is what ADR-37's gate checks, and a "
        "diff that touches anything else cannot merge on its own.",
    ]
    return "\n".join(body)


# ------------------------------------------------------------ github

class GitHub:
    """The three calls this job makes. Nothing here prints the token."""

    def __init__(self, token: str, repo: str):
        import httpx

        self.repo = repo
        self.client = httpx.Client(
            base_url="https://api.github.com",
            headers={"Authorization": f"Bearer {token}",
                     "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28"},
            timeout=60.0,
        )

    def read_file(self, path: str, ref: str) -> tuple[str, str]:
        """(text, blob sha). Raises on anything but 200, with no token in it."""
        resp = self.client.get(f"/repos/{self.repo}/contents/{path}",
                               params={"ref": ref})
        if resp.status_code != 200:
            raise RuntimeError(
                f"GET contents/{path}@{ref} answered {resp.status_code}: "
                f"{resp.text[:300]}")
        payload = resp.json()
        return (base64.b64decode(payload["content"]).decode(), payload["sha"])

    def append(self, path: str, branch: str, sha: str, text: str,
               message: str) -> str:
        """Write `text` to `path`. `sha` is None for a file that does not exist.

        The snapshot in step 5 is the first file this job may have to create
        rather than append to, and the contents API answers 422 for a PUT that
        carries a sha for a path it cannot find.
        """
        body = {"message": message, "branch": branch,
                "content": base64.b64encode(text.encode()).decode()}
        if sha:
            body["sha"] = sha
        resp = self.client.put(f"/repos/{self.repo}/contents/{path}", json=body)
        if resp.status_code not in (200, 201):
            raise RuntimeError(
                f"PUT contents/{path} answered {resp.status_code}: "
                f"{resp.text[:300]}")
        return resp.json()["commit"]["sha"][:12]

    def dispatch(self, workflow: str, ref: str, inputs: dict) -> None:
        resp = self.client.post(
            f"/repos/{self.repo}/actions/workflows/{workflow}/dispatches",
            json={"ref": ref, "inputs": inputs},
        )
        if resp.status_code != 204:
            raise RuntimeError(
                f"POST dispatches for {workflow} answered {resp.status_code}: "
                f"{resp.text[:300]}")


def skills_from_github(gh: GitHub, ref: str) -> tuple[list, list[str], pathlib.Path]:
    """Every skill on `ref`, read from GitHub rather than from this image.

    Deliberately not the bundled copy. The image is built at deploy time and
    this job runs daily, so a skill merged after the last deploy would be
    invisible to a job reading its own filesystem. That is the exact failure
    incident 24 and PR #110 are both instances of, and it costs a handful of API
    calls to avoid. The bundled copy is the fallback, and the run says which it
    used.

    The eval files come down with the SKILL.md, because trigger 4 is computed
    from `evals/results.json` and the subject model is pre-registered in
    `evals/evals.json`. A trigger read from a stale copy of a results file is
    worse than no trigger: it would dispatch the skill seat about a regression
    that was fixed the day before.
    """
    import tempfile

    reg, _ = tools()
    resp = gh.client.get(f"/repos/{gh.repo}/contents/skills", params={"ref": ref})
    if resp.status_code != 200:
        raise RuntimeError(f"GET contents/skills@{ref} answered "
                           f"{resp.status_code}: {resp.text[:300]}")
    root = pathlib.Path(tempfile.mkdtemp()) / "skills"
    root.mkdir(parents=True)
    for entry in resp.json():
        if entry["type"] != "dir" or entry["name"] in reg.NOT_A_SKILL:
            continue
        slug = entry["name"]
        (root / slug).mkdir()
        try:
            skill_md, _ = gh.read_file(f"skills/{slug}/SKILL.md", ref)
        except RuntimeError:
            continue        # read_skills reports the missing SKILL.md itself
        (root / entry["name"] / "SKILL.md").write_text(text)
    # The directory comes back too, because step 2's reviewers re-read the body
    # of each SKILL.md and have to read the same text that was registered.
    rows, problems = reg.read_skills(root)
    for row in rows:
        receipts_from_github(gh, ref, root, row.slug)
    trigger_receipt_from_github(gh, ref, root)
    return rows, problems, root


# The files ADR-13's validator reads besides the SKILL.md, and the only reason
# this function exists. Written 2026-10-03 with the third reviewer.
#
# The validator's whole input is files, so a validator pointed at a directory
# nobody wrote reports every skill unmeasured, in a voice indistinguishable
# from the truth about a library that genuinely has no evals. That is the
# merged-but-inert failure this sprint was called to close, arriving one level
# down: the skill seat would merge six suites and six results, the daily
# reviewer would keep filing `unknown`, and the first person to notice would be
# whoever eventually asked why a passing library never passed.
#
# Two names for the suite because `tools/skill_eval.py` accepts two; it reads
# `evals.json` first and the alias second, and the list here is in that order.
EVAL_FILES = ("evals.json", "tasks.json", "results.json")


def receipts_from_github(gh: GitHub, ref: str, root: pathlib.Path,
                         slug: str) -> list[str]:
    """One skill's `evals/` files, written next to the SKILL.md already there.

    One listing call per skill rather than three reads, because the common case
    today is that the directory does not exist at all and a listing says so
    once. Absence is not an error here and never raises: a skill with no eval is
    the honest majority state of the library on 2026-10-03, and the validator
    is the thing that reports it.
    """
    resp = gh.client.get(f"/repos/{gh.repo}/contents/skills/{slug}/evals",
                         params={"ref": ref})
    if resp.status_code != 200:
        return []
    payload = resp.json()
    if not isinstance(payload, list):
        return []
    wanted = {e["name"] for e in payload
              if e.get("type") == "file" and e.get("name") in EVAL_FILES}
    written = []
    for name in EVAL_FILES:
        if name not in wanted:
            continue
        try:
            text, _ = gh.read_file(f"skills/{slug}/evals/{name}", ref)
        except RuntimeError:
            continue
        target = root / slug / "evals" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        written.append(name)
    return written


def trigger_receipt_from_github(gh: GitHub, ref: str,
                                root: pathlib.Path) -> str:
    """The newest trigger-test receipt, which the validator records as evidence.

    One file, not the directory. There are fifteen receipts in
    `skills/_validation/results/` and the reviewer reads exactly one of them,
    the newest whose engine is the one the library runs, so fetching the rest
    would be fourteen API calls to produce the same note. The names lead with
    the date, which is what makes the newest one pickable from the listing
    alone.
    """
    resp = gh.client.get(f"/repos/{gh.repo}/contents/skills/_validation/results",
                         params={"ref": ref})
    if resp.status_code != 200:
        return ""
    payload = resp.json()
    if not isinstance(payload, list):
        return ""
    names = sorted((e["name"] for e in payload
                    if e.get("type") == "file"
                    and e.get("name", "").endswith(".json")
                    and "experiment" not in e["name"]
                    and "retired" not in e["name"]), reverse=True)
    if not names:
        return ""
    try:
        text, _ = gh.read_file(
            f"skills/_validation/results/{names[0]}", ref)
    except RuntimeError:
        return ""
    target = root / "_validation" / "results" / names[0]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    return names[0]


# ------------------------------------------------------------ step 2

# The marker the owner alarm keys on, the same way "registered skills/" is the
# marker for an unwatched skill. One string, in one place, so the test can hold
# the pair together.
VERDICT_ALARM = "panel verdict failing:"


def review_pass(reviewer, label: str, conn, rows, problems, skills_root,
                dry_run: bool) -> list[str]:
    """One reviewer of ADR-13's panel over the skills step 1 just registered.

    Read-only apart from the verdict rows themselves. A `fail` is a skill on
    main that did not hold up, which is the one thing in this job that the
    library's own promise to its readers depends on, so it goes in the log with
    the marker the owner alarm reads.

    Both reviewers get the same arguments and write the same verdict shape, so
    this pass is written once. What it must not do is merge their findings:
    each files its own row, because `panel_consensus` counts one verdict per
    reviewer and a pass that summarised two reviewers into one row would make a
    panel of two read as a panel of one.
    """
    verdicts = reviewer.review(skills_dir=skills_root, conn=conn,
                               rows=rows, problems=problems)
    counts = {}
    for verdict in verdicts:
        counts[verdict["verdict"]] = counts.get(verdict["verdict"], 0) + 1
    shape = ", ".join(f"{n} {name}" for name, n in sorted(counts.items()))
    log = [f"{label}: {len(verdicts)} skills reviewed ({shape})"]

    if dry_run:
        log.append("dry run: no verdict row was filed")
    else:
        ids = reviewer.file_verdicts(conn, verdicts, reviewer.reviewer_sha())
        log.append(f"filed {len(ids)} panel_verdicts rows: {ids}")

    for verdict in verdicts:
        for finding in verdict["findings"]:
            if finding["severity"] == "fail":
                log.append(f"{VERDICT_ALARM} {verdict['target']}: "
                           f"{finding['check']}: {finding['detail']}")
    return log


def reviewed(conn, rows, problems, skills_root, dry_run: bool) -> list[str]:
    """Reviewer 1, provenance: does the skill's own evidence hold up."""
    return review_pass(panel(), "provenance reviewer", conn, rows, problems,
                       skills_root, dry_run)


def adversary_reviewed(conn, rows, problems, skills_root,
                       dry_run: bool) -> list[str]:
    """Reviewer 2, the adversary: does the claim graph disagree with the skill.

    It runs here and nowhere else. Nothing it decides is in a SKILL.md, so it
    has no `--files-only` half and no step in `checks.yml`; see the "no half
    that runs in CI" section of tools/panel_adversary.py for why an empty green
    step there would be worse than no step at all.
    """
    return review_pass(adversary(), "adversary", conn, rows, problems,
                       skills_root, dry_run)


def validator_reviewed(conn, rows, problems, skills_root,
                       dry_run: bool) -> list[str]:
    """Reviewer 3, the validator: did a builder do better work with the skill.

    Third because its question comes last in time. Provenance asks whether the
    evidence behind the skill holds, the adversary asks whether the corpus has
    since disagreed, and this one asks whether the finished text changed what a
    builder produced. A reader wants them in that order.
    """
    return review_pass(validator(), "validator", conn, rows, problems,
                       skills_root, dry_run)

def snapshot_text(doc: dict) -> str:
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"


def publish_snapshot(gh: GitHub, doc: dict, today: str) -> str:
    """Step 5. Write `docs/research/claim-status.json` when it has moved.

    Unchanged content is not committed, so the file's history is a record of the
    days the graph actually changed rather than one commit a day forever.
    """
    fresh = snapshot_text(doc)
    try:
        current, blob = gh.read_file(SNAPSHOT_PATH, QUEUE_BRANCH)
    except RuntimeError:
        current, blob = "", ""
    if current:
        try:
            before = json.loads(current)
            before.pop("generated_at", None)
            after = json.loads(fresh)
            after.pop("generated_at", None)
            if before == after:
                return (f"{SNAPSHOT_PATH} already says what the graph says "
                        "today, so nothing was committed")
        except json.JSONDecodeError:
            pass
    commit = gh.append(SNAPSHOT_PATH, QUEUE_BRANCH, blob, fresh,
                       f"claim status: {len(doc['deprecated_claim_ids'])} "
                       f"deprecated claims as of {today}")
    return (f"wrote {SNAPSHOT_PATH} in {commit}: "
            f"{len(doc['deprecated_claim_ids'])} deprecated claims, "
            f"{len(doc['claim_id_ranges'])} id ranges")


# ------------------------------------------------------------ the run

def run(dry_run: bool = False) -> str:
    import os

    import psycopg

    reg, triggers = tools()
    today = dt.date.today().isoformat()
    log: list[str] = []

    token = (os.environ.get("GITHUB_TOKEN") or "").strip()
    repo = (os.environ.get("GITHUB_REPO") or "").strip()
    gh = GitHub(token, repo) if token and repo else None
    if gh is None:
        log.append(
            "DORMANT: no GITHUB_TOKEN and GITHUB_REPO in this environment, so "
            "nothing was queued, no snapshot was written and nobody was "
            "dispatched. Steps 1 and 2 ran. `modal secret create github "
            "GITHUB_TOKEN=<paste> GITHUB_REPO=alexandrapaiz/alexandria` is the "
            "whole activation.")

    # Step 1. Read main, or the image's own copy, and register what is there.
    if gh is not None:
        rows, problems, skills_root = skills_from_github(gh, QUEUE_BRANCH)
        log.append(f"read {len(rows)} skills from {repo}@{QUEUE_BRANCH}")
    else:
        skills_root = (pathlib.Path("/root/skills")
                       if pathlib.Path("/root/skills").exists() else None)
        rows, problems = reg.read_skills(skills_root)
        log.append(f"read {len(rows)} skills from this image's own copy, which "
                   "is as old as the last deploy")
    for line in problems:
        log.append(f"failing: {line}")

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        registered = reg.registered_paths(conn)
        missing = reg.unregistered(rows, registered)
        out_of_date = reg.stale(rows, registered)
        if dry_run:
            log.append(f"dry run: would register {len(missing)} missing and "
                       f"{len(out_of_date)} stale rows")
        elif missing or out_of_date:
            for line in reg.backfill(conn, missing + out_of_date):
                log.append(f"registered {line}")
        else:
            log.append(f"all {len(rows)} skills already registered")

        # Step 2, the panel. Inside this connection and before the early
        # return below, because a day with nothing to revise is still a day the
        # library's evidence is either sound or it is not.
        #
        # All three of ADR-13's reviewers run here as of 2026-10-03, in their
        # own passes filing their own rows. The order is the order the three
        # questions come in time: whether the evidence behind the skill holds,
        # whether the corpus has since disagreed, and whether the finished text
        # changed what a builder produced. With the third one filing,
        # `panel_consensus`'s unanimous is reachable for the first time; it has
        # counted to three since the table was written and never could.
        log.extend(reviewed(conn, rows, problems, skills_root, dry_run))
        log.extend(adversary_reviewed(conn, rows, problems, skills_root, dry_run))
        log.extend(validator_reviewed(conn, rows, problems, skills_root, dry_run))

        # Step 3. All four triggers, and the snapshot the gate reads. Trigger 1
        # is `skills_needing_revision`, which `triggers.live` reads itself, so
        # the view has one caller rather than two answers.
        pending, unmeasured = triggers.live(conn, skills_dir=skills_root,
                                            today=today)
        status = triggers.claim_status(conn, today)

    counts = {t: sum(1 for r in pending if r["trigger"] == t)
              for t in triggers.TRIGGERS}
    log.append("triggers: " + ", ".join(f"{t} {n}" for t, n in counts.items()))
    for line in unmeasured:
        log.append(f"unmeasured: {line}")
    log.append(f"{len(status['deprecated_claim_ids'])} deprecated claims in the "
               "corpus today")

    # Step 6 runs whatever the triggers found, because the gate needs today's
    # answer on a day nothing is stale as much as on a day something is.
    if gh is not None and not dry_run:
        log.append(publish_snapshot(gh, status, today))
    elif gh is not None:
        log.append(f"dry run: would write {SNAPSHOT_PATH} with "
                   f"{len(status['deprecated_claim_ids'])} deprecated claims")

    if not pending:
        return "\n".join(log + ["nothing needs maintenance today"])

    # Guardrail 2, before anything is queued or dispatched. Registration in
    # step 1 still ran, because knowing which skills exist is not maintenance,
    # and so did the snapshot, because pausing maintenance is not a reason to
    # blind the gate.
    if gh is not None:
        why = paused(gh, QUEUE_BRANCH)
        if why:
            return "\n".join(log + [
                f"PAUSED: {PAUSE_PATH} is on {QUEUE_BRANCH}, so nothing was "
                f"queued and nobody was dispatched. The file says: {why}",
                "Only the owner or the chair removes it (ADR-37, amended "
                "2026-09-29, guardrail 2)."])

    # Step 4, the queue.
    if gh is None:
        for rec in pending:
            log.append("would queue: " + triggers.line(rec, today))
        log.append("would dispatch " + SKILL_WORKFLOW)
        return "\n".join(log)

    text, blob = gh.read_file(QUEUE_PATH, QUEUE_BRANCH)
    fresh = triggers.fresh(text, pending)
    if not fresh:
        return "\n".join(log + [
            f"every finding is already in {QUEUE_PATH}, so nothing was appended "
            "and the skill seat was not dispatched again"])
    if len(fresh) > MAX_QUEUED_PER_RUN:
        log.append(f"{len(fresh)} findings, queueing the first "
                   f"{MAX_QUEUED_PER_RUN}; the rest are recomputed tomorrow "
                   "because every trigger is derived, not consumed")
        fresh = fresh[:MAX_QUEUED_PER_RUN]

    block = triggers.block(fresh, today)
    if dry_run:
        return "\n".join(log + ["dry run, would append:", block])

    commit = gh.append(QUEUE_PATH, QUEUE_BRANCH, blob,
                       text.rstrip() + "\n" + block,
                       f"reading queue: {len(fresh)} skill maintenance "
                       f"findings ({today})")
    log.append(f"appended {len(fresh)} lines to {QUEUE_PATH} in {commit}")

    # Step 4, the one dispatch. Only because step 3 appended something.
    gh.dispatch(SKILL_WORKFLOW, QUEUE_BRANCH,
                {DISPATCH_INPUT: dispatch_instructions(fresh, today)})
    log.append(f"dispatched {SKILL_WORKFLOW} with {len(fresh)} findings")
    return "\n".join(log)


@app.function(
    # NO SCHEDULE, and that is the design rather than an omission.
    #
    # This declared `schedule=modal.Cron("0 16 * * *")` until 2026-10-05. Modal's
    # free tier caps scheduled functions at five and ADR-12 recorded all five as
    # taken (ingest, triage, interpret, distill, the Monday press), so this was a
    # sixth and the plan does not run it: ADR-37's daily maintenance pass had a
    # cron on paper and no pass in fact. The 16:00 slot was also inside distill's
    # 15:00-16:30 window, which `test_the_schedule_sits_outside_every_reserved_window`
    # had been failing about.
    #
    # The owner's directive of 2026-10-05 folds the trigger into interpret's
    # scheduled run instead: `pipeline/interpret.py`'s `maintenance_step` spawns
    # this function as its first step, every day, in its own container. So this
    # job runs daily, keeps its own timeout and its own secrets, calls no model,
    # and occupies no row in Modal's schedule budget. Do not add a cron back here
    # without reading that module and docs/agents/runtime-changes.md.
    secrets=[modal.Secret.from_name("neon"),
             modal.Secret.from_name("github"),
             modal.Secret.from_name("Gmail"), modal.Secret.from_name("gmail_pass")],
    timeout=900,
)
def skill_revision(dry_run: bool = False) -> str:
    from notify import notify_owner

    try:
        out = run(dry_run=dry_run)
    except Exception as exc:
        detail = (f"pipeline/skill_revision.py raised {type(exc).__name__}: "
                  f"{exc}\n\nNo skill was registered, no trigger was "
                  "computed and no revision was queued on this run, which "
                  "means the library's revise-when-the-research-moves promise "
                  "is not being kept today. The claim-status snapshot the "
                  "skills-only gate reads is also a day older, and a stale "
                  "snapshot fails that gate rather than passing it, so skill "
                  "revisions will stop merging on their own until this run "
                  "succeeds again.")
        print(notify_owner("alexandria: the skill revision job failed",
                           detail,
                           ["modal app logs alexandria-skill-revision",
                            "python3 tools/skill_registrar.py --check, with "
                            "DATABASE_URL set",
                            "whether the `github` secret still carries a token "
                            "with contents:write and actions:write"],
                           sender="alexandria skills"))
        raise
    print(out)
    # A row that had to be written means a merge shipped a skill nothing was
    # watching. Worth one mail, because the check that should have caught it is
    # in CI and CI cannot see the database.
    if "registered skills/" in out:
        print(notify_owner(
            "alexandria: a skill was on main with no promotions row",
            out,
            ["whether checks.yml ran the skill registration step on that "
             "skill's pull request",
             "python3 tools/skill_registrar.py --files-only"],
            sender="alexandria skills"))
    # A reviewer failed a skill that is already on main and already published
    # on the site. The library's product claim is that every finding carries
    # evidence a reader can check, so this is worth a mail on the day it
    # appears rather than on the day somebody reads the table. One mail covers
    # both reviewers because the log line names which one failed, and two mails
    # about one morning's run is how an alarm becomes noise.
    if VERDICT_ALARM in out:
        print(notify_owner(
            "alexandria: the panel failed a skill",
            out,
            ["python3 tools/panel_provenance.py --files-only, for a "
             "provenance finding",
             "python3 tools/panel_adversary.py, with NEON_RO_URL set, for an "
             "adversary finding: it has no file-only half",
             "the skill's provenance block against the claim ids it cites",
             "select * from panel_latest order by target, reviewer"],
            sender="alexandria skills"))
    return out


@app.function(
    secrets=[modal.Secret.from_name("neon"), modal.Secret.from_name("github")],
    timeout=900,
)
def preflight() -> str:
    """Gate before the deploy: every read this job makes, and no write at all.

    docs/agents/runtime-changes.md wants a rehearsal behind a scheduled job
    before it goes live. This job calls no model, so the rehearsal is cheap and
    it is exactly this: read main, read the view, and print the lines it would
    have appended and the dispatch it would have sent.
    """
    return run(dry_run=True)


@app.local_entrypoint()
def main(dry_run: bool = False):
    print(skill_revision.remote(dry_run=dry_run))
