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

2. **Review.** Two of ADR-13's three reviewers run over the same skills and
   each files its own `panel_verdicts` row per skill.
   `tools/panel_provenance.py` asks whether the claim ids a skill cites exist
   in the corpus and whether it attributes the papers behind them.
   `tools/panel_adversary.py` asks the opposite question: whether the claim
   graph has since contradicted or refined anything the skill cites, and
   whether it was ever asked at all. Both read and neither merges, so the only
   write is the verdict row, and a `fail` from either mails the owner for the
   same reason an unregistered skill does. They run here rather than in CI
   because both questions need Neon and CI holds no database credential
   anywhere. The validator is the third and is not built: it runs the A/B
   trial (`tools/skill_eval.py`) and needs a model key in this job, which is
   the open question `docs/product/reviewer-panel.md` records.

3. **Read the view.** `skills_needing_revision` returns one row per (skill,
   deprecated claim) pair.

4. **Queue the reading.** Each new pair is appended to
   `docs/research/reading-queue.md` in the format that file documents, which is
   the same queue the skill seat writes into by hand under ADR-35 and the
   research seat drains. Only NEW pairs are appended, so a skill that waits a
   week for its revision does not collect seven identical lines.

5. **Dispatch the skill seat**, with the list in its owner instructions, and
   only when step 4 appended something. A cron that dispatches a seat every day
   about the same unfinished job is a cron nobody reads.

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

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1")
    .add_local_file("tools/skill_registrar.py", "/root/skill_registrar.py")
    .add_local_file("tools/panel_provenance.py", "/root/panel_provenance.py")
    .add_local_file("tools/panel.py", "/root/panel.py")
    .add_local_file("tools/panel_adversary.py", "/root/panel_adversary.py")
    .add_local_dir("skills", "/root/skills")
)

app = modal.App("alexandria-skill-revision", image=image)


def registrar():
    """tools/skill_registrar.py, wherever this is running from.

    The same two-path trick weekly.py and llm.py use: `/root` when Modal built
    the image, the repository when a person runs it locally.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent.parent / "tools")
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import skill_registrar as module

    return module


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


def queue_line(skill_path: str, claim_id: int, claim: str, today: str) -> str:
    """One line in the format `docs/research/reading-queue.md` documents.

    That file's format is `- [ ] arxiv:<id> — why — asked by skills/<slug> —
    YYYY-MM-DD`, and `pipeline/reading_queue.py` reads it: a line with an arXiv
    id is a paper to fetch and a line without one is a question for the research
    seat. This line has no arXiv id on purpose. The paper that deprecated the
    claim is not known here, finding it is the reading, and inventing an id
    would put a fetch request in front of distill for a paper nobody named.
    """
    text = " ".join((claim or "").split())
    if len(text) > 240:
        text = text[:237] + "..."
    return (f"- [ ] Revision: {skill_path} cites claim {claim_id}, which the "
            f"graph now marks deprecated. The claim says: \u201c{text}\u201d. "
            f"Read what contradicts it, then either revise the skill or retire "
            f"it with the reason \u2014 asked by {skill_path} \u2014 {today}")


def new_pairs(queue_text: str, rows: list[dict]) -> list[dict]:
    """The (skill, claim) pairs this file does not already carry.

    Idempotence lives here and nowhere else. The match is on the pair rather
    than on the whole line, because the claim text in the line may be truncated
    or may have been edited by whoever struck the line, and a line struck with
    an `[x]` still counts as carried: the research seat has already read it.
    """
    out = []
    for row in rows:
        path = row["skill_path"]
        claim_id = row["deprecated_claim_id"]
        needle = f"{path} cites claim {claim_id},"
        if needle in queue_text:
            continue
        if not any(p["skill_path"] == path
                   and p["deprecated_claim_id"] == claim_id for p in out):
            out.append(row)
    return out


def queue_block(pairs: list[dict], today: str) -> str:
    """The section appended to the queue, heading and all."""
    lines = [f"\n## Queued {today} by pipeline/skill_revision.py\n",
             "Every line below is a skill whose evidence moved: a claim in its "
             "provenance block is now the target of a confident `contradicts` "
             "edge, so `skills_needing_revision` returns it. ADR-37 makes the "
             "revision the skill seat's first job, ahead of new skills.\n"]
    for row in pairs:
        lines.append(queue_line(row["skill_path"], row["deprecated_claim_id"],
                                row.get("deprecated_claim") or "", today))
    return "\n".join(lines) + "\n"


def dispatch_instructions(pairs: list[dict], today: str) -> str:
    """The owner instructions the skill seat's run receives."""
    named = pairs[:MAX_PAIRS_PER_DISPATCH]
    body = [
        f"Automated revision dispatch, {today}, from "
        "pipeline/skill_revision.py under ADR-36 and ADR-37. Read ADR-37 in "
        "docs/decisions.md first: a revision outranks a new skill.",
        "",
        "`skills_needing_revision` returns the pairs below. Each one is a skill "
        "whose provenance cites a claim the graph now marks deprecated. The "
        "same lines were appended to docs/research/reading-queue.md this run.",
        "",
    ]
    for row in named:
        body.append(f"- {row['skill_path']}, claim "
                    f"{row['deprecated_claim_id']}")
    if len(pairs) > len(named):
        body += ["", f"{len(pairs) - len(named)} further pairs are in the queue "
                 "file and are not named here, because one run revises one "
                 "skill."]
    body += [
        "",
        "Before you accept the trigger, check it. The research seat's brief of "
        "2026-09-28 judged four of the six `contradicts` edges in the graph "
        "wrong, mostly same-paper co-reported results read as refutations. A "
        "deprecation that is itself a misclassification is a finding about the "
        "graph, not a reason to rewrite a skill. Say which one you found, and "
        "re-run the skill's eval either way (ADR-36).",
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
        resp = self.client.put(
            f"/repos/{self.repo}/contents/{path}",
            json={"message": message, "branch": branch, "sha": sha,
                  "content": base64.b64encode(text.encode()).decode()},
        )
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
    incident 24 and PR #110 are both instances of, and it costs one API call to
    avoid. The bundled copy is the fallback, and the run says which it used.
    """
    import tempfile

    reg = registrar()
    resp = gh.client.get(f"/repos/{gh.repo}/contents/skills", params={"ref": ref})
    if resp.status_code != 200:
        raise RuntimeError(f"GET contents/skills@{ref} answered "
                           f"{resp.status_code}: {resp.text[:300]}")
    root = pathlib.Path(tempfile.mkdtemp()) / "skills"
    root.mkdir(parents=True)
    for entry in resp.json():
        if entry["type"] != "dir" or entry["name"] in reg.NOT_A_SKILL:
            continue
        (root / entry["name"]).mkdir()
        try:
            text, _ = gh.read_file(f"skills/{entry['name']}/SKILL.md", ref)
        except RuntimeError:
            continue        # read_skills reports the missing SKILL.md itself
        (root / entry["name"] / "SKILL.md").write_text(text)
    # The directory comes back too, because step 2's reviewer re-reads the body
    # of each SKILL.md and has to read the same text that was registered.
    rows, problems = reg.read_skills(root)
    return rows, problems, root


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


# ------------------------------------------------------------ the run

def run(dry_run: bool = False) -> str:
    import os

    import psycopg

    reg = registrar()
    today = dt.date.today().isoformat()
    log: list[str] = []

    token = (os.environ.get("GITHUB_TOKEN") or "").strip()
    repo = (os.environ.get("GITHUB_REPO") or "").strip()
    gh = GitHub(token, repo) if token and repo else None
    if gh is None:
        log.append(
            "DORMANT: no GITHUB_TOKEN and GITHUB_REPO in this environment, so "
            "nothing was queued and nobody was dispatched. Steps 1 and 2 ran. "
            "`modal secret create github GITHUB_TOKEN=<paste> "
            "GITHUB_REPO=alexandrapaiz/alexandria` is the whole activation.")

    # Step 1, and 2. Read main, register, then ask the view.
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
        live = reg.registered_paths(conn)
        missing = reg.unregistered(rows, live)
        out_of_date = reg.stale(rows, live)
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
        # Two of ADR-13's three reviewers run here as of 2026-10-03, in their
        # own passes filing their own rows. The adversary is second on purpose:
        # its findings are about what the corpus learned after a skill was
        # written, so reading them under the provenance report is the order a
        # person would want them in.
        log.extend(reviewed(conn, rows, problems, skills_root, dry_run))
        log.extend(adversary_reviewed(conn, rows, problems, skills_root, dry_run))

        pending = reg.revisions(conn)

    log.append(f"skills_needing_revision returns {len(pending)} pairs")
    if not pending:
        return "\n".join(log + ["nothing needs revision today"])

    # Guardrail 2, before anything is written or dispatched. Registration in
    # step 1 still ran, because knowing which skills exist is not maintenance.
    if gh is not None:
        why = paused(gh, QUEUE_BRANCH)
        if why:
            return "\n".join(log + [
                f"PAUSED: {PAUSE_PATH} is on {QUEUE_BRANCH}, so nothing was "
                f"queued and nobody was dispatched. The file says: {why}",
                "Only the owner or the chair removes it (ADR-37, amended "
                "2026-09-29, guardrail 2)."])

    # Step 3, the queue.
    if gh is None:
        for row in pending:
            log.append("would queue: " + queue_line(
                row["skill_path"], row["deprecated_claim_id"],
                row.get("deprecated_claim") or "", today))
        log.append("would dispatch " + SKILL_WORKFLOW)
        return "\n".join(log)

    text, blob = gh.read_file(QUEUE_PATH, QUEUE_BRANCH)
    fresh = new_pairs(text, pending)
    if not fresh:
        return "\n".join(log + [
            f"every pair is already in {QUEUE_PATH}, so nothing was appended "
            "and the skill seat was not dispatched again"])

    block = queue_block(fresh, today)
    if dry_run:
        return "\n".join(log + ["dry run, would append:", block])

    commit = gh.append(QUEUE_PATH, QUEUE_BRANCH, blob, text.rstrip() + "\n" + block,
                       f"reading queue: {len(fresh)} skill revisions the graph "
                       f"asked for ({today})")
    log.append(f"appended {len(fresh)} lines to {QUEUE_PATH} in {commit}")

    # Step 4, the dispatch. Only because step 3 appended something.
    gh.dispatch(SKILL_WORKFLOW, QUEUE_BRANCH,
                {DISPATCH_INPUT: dispatch_instructions(fresh, today)})
    log.append(f"dispatched {SKILL_WORKFLOW} with {len(fresh)} pairs")
    return "\n".join(log)


@app.function(
    # 16:00 UTC. This job calls no model, so it contends with nothing; the slot
    # sits after interpret's window anyway. See this module's docstring and the
    # schedule comment in pipeline/llm.py.
    schedule=modal.Cron("0 16 * * *"),
    secrets=[modal.Secret.from_name("neon"),
             modal.Secret.from_name("github"),
             modal.Secret.from_name("gmail")],
    timeout=900,
)
def skill_revision(dry_run: bool = False) -> str:
    from notify import notify_owner

    try:
        out = run(dry_run=dry_run)
    except Exception as exc:
        detail = (f"pipeline/skill_revision.py raised {type(exc).__name__}: "
                  f"{exc}\n\nNo skill was registered and no revision was "
                  "queued on this run, which means the library's "
                  "revise-when-the-research-moves promise is not being kept "
                  "today.")
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
