#!/usr/bin/env python3
"""Every flag in `tools/` that names something, enumerated rather than sampled.

    python3 tools/target_census.py --check     # is every flag classified?
    python3 tools/target_census.py --probe     # do the roster flags refuse?
    python3 tools/target_census.py --list      # the census, as a table

## Why this file exists

`INC-2026-11-02-the-confident-zero-class-was-measured-in-three-more-tools-and-two-sweeps-had-covered-four-of-fifty-six`
ends with the piece of work this file is: "Making the 56 an enumerated set that
each tool must declare against is the next day-sized piece of work." Its own
repair, `tools/resolve_target.py`, shipped with a probe that is a hand list of
three, and the incident says so in its last paragraph: a hand list "cannot tell
the difference between a tool that resolves its target and a tool nobody has
looked at".

The skill seat reached the same shape from the other side on 2026-11-02 and
handed it over in those words: its `GATES` was a hand list of five, "so the
probe cannot tell a gate that refuses from a gate nobody registered", and the
first step it carded was to derive the list with `ast` and fail when a module is
missing from it. That is what `census` does here.

## The two halves, and why neither is the other

`census` is derived. It parses every `add_argument` call under `tools/` with
`ast` and needs no maintenance, so a flag added tomorrow is in it tomorrow.

`DECLARED` is a judgment, and it is a judgment no parser carries. Whether
`--status` names a closed roster and `--body` names free prose is knowledge
about the tool, which is why the incident recorded it as "handed over as
per-tool knowledge" rather than as a rule. So it is written down once, with the
help text beside it, so a reader can re-perform each judgment without reading
45 files.

The gate between them is the point: `undeclared()` must be empty. A new flag
that names a target is then a red pull request on the day it lands, rather than
the forty-ninth unprobed flag in a tree somebody already called clean.

## The counts move, so they are printed and never asserted

The incident's headline numbers were 246 arguments, 242 flag-carried and 56
naming a target. This file counted 245 distinct `(file, flag)` pairs and 118
needing a judgment on the branch it was written on, and both are right: the
incident counted call sites on `origin/main`, and `board.py` alone declares
`--id` three times. A census whose total is asserted goes red on a tool that
gains a flag, which trains a reader to raise the number rather than to classify
the flag. So `--check` prints its denominator, asserts only that it is not
zero, and fails on the one thing that is actually wrong: a flag nobody has
classified.
"""

from __future__ import annotations

import argparse
import ast
import pathlib
import subprocess
import sys
from typing import NamedTuple

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: Clean. Every flag is classified and every probeable roster flag refuses.
EXIT_OK = 0
#: A flag nobody has classified, or a roster flag that answered a zero.
EXIT_PROBLEM = 1
#: The input was empty. The skill seat's finding of 2026-11-02: a `--check`
#: handed nothing printed its pass sentence over a denominator of zero, and
#: `trigger_test.py` already reserved 2 for a data error. A census of no files
#: is a data error and never a pass.
EXIT_EMPTY = 2

#: `action=` values that make a flag carry no value at all, so there is nothing
#: to resolve and no judgment to record.
SWITCH_ACTIONS = {"store_true", "store_false", "count", "version", "help"}


class Flag(NamedTuple):
    file: str
    flag: str
    #: "switch", "choices", "number", or "" when a judgment is needed.
    derived: str
    help: str


class Judgment(NamedTuple):
    #: One of KINDS.
    kind: str
    #: For a roster flag: "" when this module probes it, or the reason it
    #: cannot be probed offline. Empty for every other kind.
    offline: str = ""


#: What a flag's value can be, and the only one of these that can answer a
#: confident zero about a subject it never found is `roster`.
KINDS = {
    # A closed set this repository carries: a seat, a skill, a status, a
    # workflow, a surface. A value off the set has to refuse by name.
    "roster",
    # A path. Absent is already an error in every tool measured, because open()
    # raises, and the ones that write rather than read must not refuse.
    "path",
    # A date or an ISO stamp. There is no roster, and a malformed one raises.
    "date",
    # Free prose a person wrote: a title, a body, a reason. Nothing to resolve.
    "text",
    # An id or token only an external service can judge: a board item id, an
    # unsubscribe token, a model name a provider owns.
    "opaque",
    # A number, a window or a count carried without `type=int`.
    "number",
}


def _h(*parts: str) -> str:
    return " ".join(parts)


#: The 118 flags that `ast` cannot classify, each with the judgment and the
#: reason. Keyed on `(file, flag)`, which is what `census` returns.
#:
#: The `roster` rows are the population the incident sized at 56 and probed 8
#: of. Each one either refuses under `--probe` or says why it cannot be probed
#: without a network, and "nobody has looked" is not one of the two.
DECLARED: dict[tuple[str, str], Judgment] = {
    ("anchor_contention.py", "--prs"): Judgment("path"),
    ("anchor_contention.py", "--root"): Judgment("path"),
    ("ban_list.py", "paths"): Judgment("path"),
    ("ban_list.py", "--allow"): Judgment("text"),
    ("blind_prose_benchmark.py", "--issue"): Judgment("path"),
    ("blind_prose_benchmark.py", "--comparison"): Judgment("path"),
    ("blind_prose_benchmark.py", "--out"): Judgment("path"),
    ("blind_prose_benchmark.py", "--scores"): Judgment("path"),
    ("blind_prose_benchmark.py", "--date"): Judgment("date"),
    ("blind_prose_benchmark.py", "--write"): Judgment("path"),
    ("board.py", "--company"): Judgment(
        "roster", "reaches the board API to learn which companies exist"),
    ("board.py", "--seat"): Judgment(
        "roster", "repaired already and probed by tests/test_board_inbox.py; "
        "exits EXIT_UNKNOWN_SEAT=4 against the roster, which needs the API"),
    ("board.py", "--id"): Judgment("opaque"),
    ("board.py", "--title"): Judgment("text"),
    ("board.py", "--body"): Judgment("text"),
    ("board.py", "--column"): Judgment(
        "roster", "the columns are the board's own, so the set needs the API"),
    ("board.py", "--subject"): Judgment("text"),
    ("board.py", "--to-seat"): Judgment(
        "roster", "same roster as --seat, same API"),
    ("board.py", "--to-company"): Judgment(
        "roster", "same roster as --company, same API"),
    ("board.py", "--ref"): Judgment("opaque"),
    ("board.py", "--reasoning"): Judgment("text"),
    ("board.py", "--data"): Judgment("text"),
    ("board.py", "--report"): Judgment("text"),
    ("board.py", "--branch"): Judgment("opaque"),
    ("board.py", "--started-at"): Judgment("date"),
    ("board.py", "--ended-at"): Judgment("date"),
    ("board.py", "--model"): Judgment("opaque"),
    ("board.py", "--item"): Judgment("opaque"),
    ("buyer_path.py", "--surface"): Judgment("roster"),
    ("buyer_path.py", "--url"): Judgment("opaque"),
    ("check_authority.py", "--range"): Judgment("opaque"),
    ("check_authority.py", "--base"): Judgment("opaque"),
    ("check_digest_quality.py", "paths"): Judgment("path"),
    ("check_plugin_manifest.py", "--root"): Judgment("path"),
    ("check_pr_green.py", "--branch"): Judgment("opaque"),
    ("check_pr_green.py", "--base"): Judgment("opaque"),
    ("check_pr_green.py", "--suite"): Judgment("text"),
    ("checkout_watch.py", "--today"): Judgment("date"),
    ("checkout_watch.py", "--company"): Judgment(
        "roster", "same roster as board.py --company, same API"),
    ("ci_coverage.py", "--only"): Judgment("path"),
    ("ci_coverage.py", "--workflows"): Judgment("path"),
    ("corrections.py", "--skill"): Judgment("roster"),
    ("cron_firing.py", "--day"): Judgment("date"),
    ("cron_firing.py", "--seat"): Judgment("roster"),
    ("cron_firing.py", "--root"): Judgment("path"),
    ("cron_firing.py", "--now"): Judgment("date"),
    ("cron_firing.py", "--prs"): Judgment("path"),
    ("cron_firing.py", "--claims"): Judgment("path"),
    ("cron_firing.py", "--audit"): Judgment("path"),
    ("delivery_health.py", "--today"): Judgment("date"),
    ("drift_watch.py", "--today"): Judgment("date"),
    ("drift_watch.py", "--company"): Judgment(
        "roster", "same roster as board.py --company, same API"),
    ("feed_health.py", "--only"): Judgment("roster"),
    ("feed_health.py", "--census"): Judgment("path"),
    ("feed_health.py", "--sources"): Judgment("path"),
    ("fulltext_density.py", "--papers"): Judgment("opaque"),
    ("fulltext_density.py", "--model"): Judgment("opaque"),
    ("fulltext_density.py", "--write"): Judgment("path"),
    ("graph_audit.py", "--labels"): Judgment("path"),
    ("graph_audit.py", "--seed"): Judgment("number"),
    ("graph_audit.py", "--snapshot"): Judgment("path"),
    # Added 2026-11-09 with tools/host_headroom.py. `--path` is a mount point
    # and `--compose` is a list of NAME=PATH pairs, so both are paths; neither
    # raises on an absent one, because the tool reports an unreadable component
    # by name rather than letting it silently shrink the residual, which is a
    # regression test in tests/test_host_headroom.py.
    ("host_headroom.py", "--path"): Judgment("path"),
    ("host_headroom.py", "--compose"): Judgment("path"),
    ("incidents.py", "--base"): Judgment("opaque"),
    ("incidents.py", "--slug"): Judgment("text"),
    ("incidents.py", "--date"): Judgment("date"),
    ("incidents.py", "--seat"): Judgment("text"),
    ("incidents.py", "--title"): Judgment("text"),
    ("ledger.py", "--ledger"): Judgment("path"),
    ("ledger.py", "--status"): Judgment("roster"),
    ("ledger.py", "--patch"): Judgment("opaque"),
    # The inbox of 2026-11-09. `--base` is a git ref and takes `--patch`'s
    # judgment above for the same reason: git owns the namespace, the tool
    # cannot enumerate it, and a ref this checkout does not carry is reported
    # as a skip rather than a failure.
    ("ledger.py", "--base"): Judgment("opaque"),
    ("ledger.py", "--date"): Judgment("date"),
    ("ledger.py", "--inbox-dir"): Judgment("path"),
    # The slug half of an inbox filename. Validated against the slug alphabet
    # rather than a roster, because the whole point is that it is new: there is
    # nothing yet for it to resolve against.
    ("ledger.py", "--inbox-new"): Judgment("text"),
    ("ledger.py", "--title"): Judgment("text"),
    # Probed offline, which no other `roster` row here can say. `company.yaml`
    # carries all twelve seat names and needs no credential, so this refuses by
    # name on a typo instead of writing `(enginer seat)` into a heading.
    ("ledger.py", "--seat"): Judgment(
        "roster", ""),
    ("loop_close.py", "--proposals"): Judgment("path"),
    ("loop_close.py", "--receipt"): Judgment("path"),
    ("loop_close.py", "--repo-root"): Judgment("path"),
    ("loop_close.py", "--today"): Judgment("date"),
    ("merge_order.py", "--base"): Judgment("opaque"),
    ("panel_adversary.py", "--skill"): Judgment("roster"),
    ("panel_provenance.py", "--skill"): Judgment("roster"),
    ("panel_validator.py", "--skill"): Judgment("roster"),
    # Both of these arrived on `main` with #813 and were unaccounted for there,
    # so this gate was already failing before this branch added to it. A tree
    # that reads files takes `path` for both: `--root` is the tree to read and
    # `paths` narrows it.
    ("prose_symbols.py", "--root"): Judgment("path"),
    ("prose_symbols.py", "paths"): Judgment("path"),
    # Both are the same two judgments `cron_firing.py` already carries, and for
    # the same reason: this tool reads that one's log root through that one's
    # reader, so a divergence here would be a second answer to one question.
    # Added 2026-11-09 by the engineer seat. `tools/prose_symbols.py` landed on
    # 2026-11-08 and its two targets were left undeclared, so this census was
    # red on `main` for every seat until these rows. Both are paths and neither
    # needs a reading: `--root` is the tree to read and `paths` limits the run
    # to named files or directories, so absent is already an error through
    # `open()` and there is no roster either could be checked against.
    ("prose_symbols.py", "--root"): Judgment("path"),
    ("prose_symbols.py", "paths"): Judgment("path"),
    ("provider_cycle.py", "--root"): Judgment("path"),
    ("provider_cycle.py", "--now"): Judgment("date"),
    ("press_watch.py", "--today"): Judgment("date"),
    ("press_watch.py", "--company"): Judgment(
        "roster", "same roster as board.py --company, same API"),
    ("read_paper.py", "ids"): Judgment("opaque"),
    ("read_paper.py", "--cache-dir"): Judgment("path"),
    ("rehearse_email.py", "key"): Judgment("roster"),
    ("rehearse_email.py", "--to"): Judgment("text"),
    ("rehearse_email.py", "--out"): Judgment("path"),
    ("rehearse_email.py", "--token"): Judgment("opaque"),
    ("resolve_register_conflict.py", "--check"): Judgment("opaque"),
    ("resolve_register_conflict.py", "--repo"): Judgment("path"),
    # A root path. It is compared as a name against git's own list of
    # additions rather than opened, so `path`'s "absent is already an error"
    # does not hold by `open()` raising. The tool says so itself instead: an
    # `--allow` value that matched no stray is printed as unused.
    ("root_scratch.py", "--allow"): Judgment("path"),
    ("run_report.py", "--workflow"): Judgment("text"),
    ("run_report.py", "--status"): Judgment("text"),
    ("run_report.py", "--branch"): Judgment("opaque"),
    ("runtime_provenance.py", "--checkout"): Judgment("path"),
    ("runtime_provenance.py", "--install"): Judgment("path"),
    ("runtime_provenance.py", "--staged"): Judgment("path"),
    # Probed offline from 2026-11-09, and the reason the declaration changed is
    # worth keeping. It read "reaches the board API", and that was never true:
    # `tools/ship_first.py` makes no network call, asks no roster and runs no
    # subprocess. The false cause came from the 2026-11-02 incident and was
    # copied here, which is how a wrong reason earns an exemption. The flag
    # refuses in 0.36s because the roster check runs before `collect()` reads
    # the transcripts, so the one thing that made it unprobeable is gone.
    ("ship_first.py", "--company"): Judgment("roster"),
    ("ship_first.py", "--seat"): Judgment(
        "roster", "`collect()` parses every transcript on the host, 2.7 GB on "
        "2026-11-09, before the selector filters anything, so any value costs "
        "what `--all` costs. Not the board and not a roster fetch, which is "
        "the correction to the 2026-11-02 carding; carried as a ledger entry "
        "with the fix's design"),
    ("ship_first.py", "--session"): Judgment("opaque"),
    ("ship_first.py", "--projects"): Judgment("path"),
    ("ship_first.py", "--audit"): Judgment("path"),
    ("skill_eval.py", "--skill"): Judgment("roster"),
    ("skill_eval.py", "--subject"): Judgment("opaque"),
    ("skill_eval.py", "--judge"): Judgment("opaque"),
    ("skill_eval.py", "--written-against"): Judgment("opaque"),
    ("skill_eval.py", "--trigger"): Judgment("text"),
    ("skill_gate.py", "--base"): Judgment("opaque"),
    ("skill_gate.py", "--comment"): Judgment("path"),
    ("skill_gate.py", "--github-output"): Judgment("path"),
    ("skill_registrar.py", "--deprecated"): Judgment("opaque"),
    ("skill_scope.py", "--query"): Judgment("text"),
    ("skill_scope.py", "--distractors"): Judgment("number"),
    ("skill_scope.py", "--json"): Judgment("path"),
    ("skill_scope.py", "--root"): Judgment("path"),
    ("skill_triggers.py", "--snapshot"): Judgment("path"),
    ("wake_routes.py", "--company"): Judgment("roster"),
    ("wake_routes.py", "--roster"): Judgment("path"),
    ("wake_routes.py", "--prompts"): Judgment("path"),
    ("wake_routes.py", "--audit"): Judgment("path"),
    ("wake_routes.py", "--company-yaml"): Judgment("path"),
    ("wake_routes.py", "--seat"): Judgment("roster"),
    # The same two judgments `cron_firing.py` and `provider_cycle.py` carry,
    # for the third time and the same reason: this tool walks that one's log
    # root through that one's reader, so a different answer here would be a
    # second answer to one question.
    ("wall_encounters.py", "--root"): Judgment("path"),
    ("wall_encounters.py", "--seat"): Judgment("roster"),
}

#: A value nothing carries, for the probe. Spelled so that a tool which happens
#: to accept free text cannot match it by accident.
NO_SUCH = "no-such-target-7f3a9c"

#: How long one probe gets before it is reported as a hang rather than a pass.
#: `ship_first.py --seat` did not answer in 25 seconds on 2026-11-02, which is
#: the behaviour this bound exists to name.
PROBE_TIMEOUT = 40


def census(root: pathlib.Path | None = None) -> list[Flag]:
    """Every distinct `(file, flag)` under `tools/`, derived with `ast`.

    One row per pair and not per call site, because `board.py` declares `--id`
    on three subcommands and they are one judgment. Parsed rather than
    imported, so a module that reaches a network at import time cannot make the
    census hang, and a module with a syntax error is a loud failure here rather
    than a silently shorter census.
    """
    base = (root or ROOT) / "tools"
    rows: dict[tuple[str, str], Flag] = {}
    for path in sorted(base.glob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "add_argument"):
                continue
            names = [a.value for a in node.args
                     if isinstance(a, ast.Constant) and isinstance(a.value, str)]
            if not names:
                continue
            kw = {k.arg: k.value for k in node.keywords if k.arg}
            action = kw.get("action")
            kind = ""
            if (isinstance(action, ast.Constant)
                    and action.value in SWITCH_ACTIONS):
                kind = "switch"
            elif "choices" in kw:
                kind = "choices"
            else:
                typ = kw.get("type")
                if isinstance(typ, ast.Name) and typ.id in ("int", "float"):
                    kind = "number"
            helped = kw.get("help")
            rows.setdefault((path.name, names[0]), Flag(
                file=path.name,
                flag=names[0],
                derived=kind,
                help=(helped.value if isinstance(helped, ast.Constant)
                      and isinstance(helped.value, str) else ""),
            ))
    return [rows[k] for k in sorted(rows)]


def needs_judgment(rows) -> list[Flag]:
    """The flags `ast` cannot classify, which is the population `DECLARED` owns."""
    return [f for f in rows if not f.derived]


def undeclared(rows) -> list[Flag]:
    """A flag nobody has classified. The one thing `--check` fails on."""
    return [f for f in needs_judgment(rows)
            if (f.file, f.flag) not in DECLARED]


def stale_declarations(rows) -> list[tuple[str, str]]:
    """A `DECLARED` row for a flag that is no longer there, or no longer needs one.

    A declaration file that only ever grows becomes its own kind of hand list:
    it would carry the judgment for a tool that was deleted, and a reader could
    not tell that row from a live one.
    """
    live = {(f.file, f.flag) for f in needs_judgment(rows)}
    return sorted(k for k in DECLARED if k not in live)


def bad_kinds() -> list[tuple[str, str]]:
    """A declaration whose kind is not one of `KINDS`, or an `offline` reason
    attached to something that is not a roster flag."""
    bad = []
    for key, j in sorted(DECLARED.items()):
        if j.kind not in KINDS or (j.offline and j.kind != "roster"):
            bad.append(key)
    return bad


def roster_flags(*, probeable: bool) -> list[tuple[str, str]]:
    """The roster flags, split by whether this module can probe them offline."""
    return sorted(k for k, j in DECLARED.items()
                  if j.kind == "roster" and bool(j.offline) != probeable)


def probe_one(file: str, flag: str, root: pathlib.Path | None = None):
    """Hand one roster flag a value nothing carries. `(ok, exit code, said)`.

    `ok` is "it refused", which is any non-zero exit. Exit 4 is the number this
    tree agreed on in `tools/resolve_target.py`, and it is reported rather than
    required, because two of the four tools the incident found already refusing
    exit 2 and they were refusing correctly.
    """
    base = (root or ROOT) / "tools" / file
    argv = [sys.executable, str(base)]
    argv += [NO_SUCH] if not flag.startswith("-") else [flag, NO_SUCH]
    try:
        done = subprocess.run(argv, capture_output=True, text=True,
                              timeout=PROBE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return False, None, f"no answer in {PROBE_TIMEOUT}s"
    said = (done.stdout + done.stderr).strip()
    return done.returncode != 0, done.returncode, said


def check(root: pathlib.Path | None = None, *, stream=None) -> int:
    """Is every flag in the tree classified? Prints what it was computed over."""
    out = stream or sys.stdout
    rows = census(root)
    judged = needs_judgment(rows)
    print(f"{len(rows)} distinct (file, flag) pairs under tools/, "
          f"{len(judged)} needing a judgment, {len(DECLARED)} declared",
          file=out)
    if not rows:
        print("refused: the census is empty, so there is nothing to pass",
              file=out)
        return EXIT_EMPTY
    problems = 0
    for flag in undeclared(rows):
        problems += 1
        print(f"FAIL: {flag.file} {flag.flag} is classified by nobody. "
              f"Its help says: {flag.help or '(no help text)'}", file=out)
    for file, flag in stale_declarations(rows):
        problems += 1
        print(f"FAIL: {file} {flag} is declared and no longer in the tree",
              file=out)
    for file, flag in bad_kinds():
        problems += 1
        print(f"FAIL: {file} {flag} declares a kind outside {sorted(KINDS)}",
              file=out)
    counts: dict[str, int] = {}
    for key in DECLARED:
        if key in {(f.file, f.flag) for f in judged}:
            counts[DECLARED[key].kind] = counts.get(DECLARED[key].kind, 0) + 1
    print("by kind: " + ", ".join(f"{k} {counts[k]}" for k in sorted(counts)),
          file=out)
    if problems:
        print(f"FAIL: {problems} flag(s) unaccounted for", file=out)
        return EXIT_PROBLEM
    print(f"ok: all {len(judged)} judgment-needing flags are classified, "
          f"{len(roster_flags(probeable=True))} roster flags probeable and "
          f"{len(roster_flags(probeable=False))} declared offline", file=out)
    return EXIT_OK


def probe(root: pathlib.Path | None = None, *, stream=None) -> int:
    """Does every probeable roster flag refuse a value nothing carries?"""
    out = stream or sys.stdout
    targets = roster_flags(probeable=True)
    print(f"probing {len(targets)} roster flag(s) with {NO_SUCH!r}", file=out)
    if not targets:
        print("refused: nothing to probe, so there is nothing to pass",
              file=out)
        return EXIT_EMPTY
    failed = 0
    for file, flag in targets:
        ok, code, said = probe_one(file, flag, root)
        head = said.splitlines()[0][:90] if said else "(said nothing)"
        if ok:
            print(f"ok:   {file} {flag} exits {code}: {head}", file=out)
        else:
            failed += 1
            print(f"FAIL: {file} {flag} exits {code}: {head}", file=out)
    if failed:
        print(f"FAIL: {failed} of {len(targets)} answered a value nothing "
              f"carries without refusing", file=out)
        return EXIT_PROBLEM
    print(f"ok: all {len(targets)} roster flags refused", file=out)
    return EXIT_OK


def listing(root: pathlib.Path | None = None, *, stream=None) -> int:
    out = stream or sys.stdout
    rows = census(root)
    if not rows:
        print("refused: the census is empty", file=out)
        return EXIT_EMPTY
    for flag in rows:
        j = DECLARED.get((flag.file, flag.flag))
        kind = flag.derived or (j.kind if j else "UNCLASSIFIED")
        note = f"  [{j.offline}]" if j and j.offline else ""
        print(f"{flag.file:32s} {flag.flag:22s} {kind}{note}", file=out)
    return EXIT_OK


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="target_census.py",
        description="Every flag in tools/ that names something, enumerated.")
    ap.add_argument("--check", action="store_true",
                    help="fail when a flag is classified by nobody")
    ap.add_argument("--probe", action="store_true",
                    help="hand every probeable roster flag a value nothing "
                         "carries and require a refusal")
    ap.add_argument("--list", action="store_true",
                    help="the census as a table")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.list:
        return listing()
    if args.probe and args.check:
        return max(check(), probe())
    if args.probe:
        return probe()
    if args.check:
        return check()
    print(__doc__.strip())
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
