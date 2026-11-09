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
    # Added 2026-11-09 with `incidents.py prior`, the register's lookup half.
    # `query` is the failure a seat has in hand, in whatever shape it arrived,
    # and the tool's own claim is that nothing is required of its shape, so
    # there is no roster and nothing to refuse. `--file` reads that query out
    # of a log instead, so it is a path, and an unreadable one is reported by
    # name with exit 2 rather than being treated as an empty query, because a
    # lookup that silently searched for nothing would read as "never filed
    # before", which is the one wrong answer this tool must not give.
    ("incidents.py", "query"): Judgment("text"),
    ("incidents.py", "--file"): Judgment("path"),
    # Added 2026-11-09 by the engineer seat, for a flag that reached `main` in
    # the ExO seat's #886 and was declared by nobody. It is the repository root
    # the tool reads `docs/standards/` under, so it is a path on the same
    # footing as `anchor_contention.py --root` and `cron_firing.py --root`
    # above. Declaring it is not a judgment about the tool: four tests in
    # `tests/test_target_census.py` fail on an undeclared flag, and they were
    # failing on live `main` until this row.
    ("kill_vocabulary.py", "--root"): Judgment("path"),
    # Added 2026-11-09 by the engineer seat, the FOURTH tool in one day to
    # reach `main` with its targets undeclared, after prose_symbols.py on
    # 11-08, pr_backlog.py and kill_vocabulary.py earlier today. This pair
    # arrived in #895. `--now` pretends it is an instant and bounds the runs
    # read as well as the clock, so it is a date. `--root` carries no help
    # text and defaults to a log tree, so it is a path.
    ("burn_shares.py", "--now"): Judgment("date"),
    ("burn_shares.py", "--root"): Judgment("path"),
    # Added 2026-11-09 with the vendored copy of HQ's register merger. The
    # three positionals are files the tool opens, so `open()` raises on an
    # absent one and `path` is exactly right for them.
    ("merge_register.py", "base"): Judgment("path"),
    ("merge_register.py", "ours"): Judgment("path"),
    ("merge_register.py", "theirs"): Judgment("path"),
    # The five pattern flags are the first REGEX-valued flags in this census,
    # and none of the six kinds fits them. `text` is the closest and it is
    # declared here under protest, because the clause that justifies `text` is
    # "nothing to resolve" and a regex has plenty to resolve: a `--heading`
    # that matches nothing does not raise and does not refuse, it parses the
    # register as one block and merges it at exit 0. That is a confident zero,
    # which the comment above KINDS says only `roster` can produce.
    #
    # So the census is one kind short rather than these flags being `text`, and
    # the gap is filed as a ledger idea rather than fixed here, because adding
    # a seventh kind re-opens all 148 declared rows and this run is a break-fix
    # plus a handoff. `tests/test_merge_register.py` carries the floor
    # assertions that stand in for the missing kind's probe in the meantime.
    ("merge_register.py", "--heading"): Judgment("text"),
    ("merge_register.py", "--identifier"): Judgment("text"),
    ("merge_register.py", "--key"): Judgment("text"),
    ("merge_register.py", "--section"): Judgment("text"),
    ("merge_register.py", "--section-end"): Judgment("text"),
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
    # These two rows were declared twice, once by #813's reader and once by the
    # engineer seat on 2026-11-09, and a dict literal keeps the last of each.
    # Both reasons are kept here because both were written and only one of each
    # pair was ever attached to anything. #813's: `prose_symbols.py` arrived on
    # `main` unaccounted for, and a tree that reads files takes `path` for
    # both, `--root` being the tree to read and `paths` narrowing it. The
    # engineer seat's: absent is already an error through `open()` and there is
    # no roster either value could be checked against, which is the same pair
    # of judgments `cron_firing.py` carries for the same reason. The agreement
    # is the point. Two readers reached one answer twice, and the table printed
    # one of them. `repeated_declarations` below is why that cannot recur.
    ("prose_symbols.py", "--root"): Judgment("path"),
    ("prose_symbols.py", "paths"): Judgment("path"),
    ("provider_cycle.py", "--root"): Judgment("path"),
    ("provider_cycle.py", "--now"): Judgment("date"),
    # Added 2026-11-09 by the engineer seat. `tools/pr_backlog.py` landed on
    # `main` with #836 at 06:26Z and left four targets undeclared, so this
    # census, `main`, and every open pull request inheriting `main` were red
    # until these rows. `--prs` and `--merged` are both a file of `gh pr list
    # --json` output, read with a bare `json.load(open(...))`, so an absent one
    # raises before any count is reported and neither can shrink a backlog
    # quietly. `--since` and `--now` go through `_dt`, which is
    # `fromisoformat`, so a malformed stamp raises there. `--now` is the test
    # hook for the clock and it is a `date` rather than `opaque` for that
    # reason: it is compared against row timestamps and nothing else resolves
    # it.
    ("pr_backlog.py", "--prs"): Judgment("path"),
    ("pr_backlog.py", "--merged"): Judgment("path"),
    ("pr_backlog.py", "--since"): Judgment("date"),
    ("pr_backlog.py", "--now"): Judgment("date"),
    ("press_watch.py", "--today"): Judgment("date"),
    ("press_watch.py", "--company"): Judgment(
        "roster", "same roster as board.py --company, same API"),
    ("read_paper.py", "ids"): Judgment("opaque"),
    ("read_paper.py", "--cache-dir"): Judgment("path"),
    ("receipt_ranking.py", "--results"): Judgment("path"),
    ("receipt_ranking.py", "--skills"): Judgment("path"),
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
    # Six judgments for `sentinel.py`, added 2026-11-09 with the tool, because
    # this gate turned red on the pull request that added it. That is the
    # behaviour its own docstring argues for, so the flags are classified here
    # rather than the test being loosened.
    #
    # `paths` and `--out` are both files and they point opposite ways, which is
    # the distinction `path` already carries: `paths` is read and a missing one
    # is the finding rather than an error, since an output file that was never
    # created is what a killed run leaves and the tool answers `absent` for it.
    # `--out` is written and must not refuse.
    ("sentinel.py", "paths"): Judgment("path"),
    ("sentinel.py", "--out"): Judgment("path"),
    # `--label` is free prose that names the work in the verdict line.
    # `--expect-label` is the same prose read back, and it does refuse by name
    # when the file's verdict carries another seat's label, which is `stale`.
    # It is `text` and not `roster` because there is no roster of labels in
    # this repository and inventing one would be a closed set of one seat's
    # habits.
    ("sentinel.py", "--label"): Judgment("text"),
    ("sentinel.py", "--expect-label"): Judgment("text"),
    # `--part` is `name=value`, so the name is prose and the value is parsed to
    # a float by `parse_part`, which refuses a non-number by name.
    ("sentinel.py", "--part"): Judgment("text"),
    # `--unit` is the word printed beside every figure, `GiB` or `papers`.
    ("sentinel.py", "--unit"): Judgment("text"),
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


class CannotRead(Exception):
    """The source could not be read for the question asked of it."""


def repeated_declarations(
    source: str | None = None,
) -> list[tuple[tuple[str, str], list[int]]]:
    """A `(file, flag)` key declared more than once in `DECLARED`'s source.

    The dict cannot be asked. By the time `DECLARED` is a dict the duplicate is
    gone, because a dict literal keeps the last value for a repeated key and
    says nothing. So this reads the module's own text with `ast`, which is the
    same instrument the census uses on every other tool in the tree.

    Two rows of this table were declared twice on 2026-11-09 and the gate
    printed `137 declared` over 139 written rows. Both pairs happened to agree
    on the judgment, so nothing was wrong in the answer. What was thrown away
    was a reason: each pair carried two comment blocks explaining itself and
    only one of them was attached to a live row, and a reader could not tell
    which.

    alexandria/exo found the identical shape in `tools/sentinel.py` the same
    morning, where `dict(args.part)` dropped a part somebody had named. One
    name carrying two readings is the ambiguity, and last-wins hides which.
    """
    text = source if source is not None else pathlib.Path(__file__).read_text()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        is_declared = (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "DECLARED"
            and isinstance(node.value, ast.Dict)
        )
        if not is_declared:
            continue
        lines: dict[tuple[str, str], list[int]] = {}
        for key in node.value.keys:
            try:
                literal = ast.literal_eval(key)
            except ValueError:  # a computed key, which this table does not use
                continue
            lines.setdefault(literal, []).append(key.lineno)
        return sorted((k, v) for k, v in lines.items() if len(v) > 1)
    # No `DECLARED` annotated assignment at all is itself a finding, because
    # every caller below reads a silent empty list as "no repeats".
    raise CannotRead("DECLARED is not an annotated dict literal in this file")


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
    for (file, flag), lines in repeated_declarations():
        problems += 1
        print(f"FAIL: {file} {flag} is declared {len(lines)} times, at lines "
              f"{', '.join(str(n) for n in lines)}. A dict literal keeps the "
              f"last one, so the reasons above the others are attached to "
              f"nothing and the count this gate prints is short by "
              f"{len(lines) - 1}.", file=out)
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
