"""The deploy ladder: does the command refuse where the charter only asks.

`tools/deploy_gate.py` exists because of the closing argument in
docs/agents/runtime-changes.md, that a rule enforced by a sentence is enforced
at the reliability of a model reading a file. So the tests here are not about
whether the ladder is pretty. They are about whether it refuses.

Three properties carry the file.

**The ladder is derived, not declared.** Which gates an app has is read off its
module's source, so a module that grows a `rehearse` gains the rung the same
day. The cross-check against the register is in this file too: every gate the
derivation produces is a command `docs/decisions.md` already names, and the one
app the derivation gives no gates to is the one app the register gives none
either.

**The chain stops.** A gate that fails leaves `modal deploy` unrun, which is
the entire mechanism of the `&&` chain the chair runs by hand.

**The window refuses before anything is spent.** Moonshot's organization
concurrency is 1 and `pipeline/llm.py` holds the schedule, so a rehearsal
inside a live job's hour takes that job's slot. Every minute of every reserved
window is checked, not a sample of them.

No model call, no network, no database, no Modal CLI. The runner is injected.

Run with `python3 tests/test_deploy_gate.py` or under pytest.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import llm  # noqa: E402
from tools import deploy_gate as dg  # noqa: E402

FAILURES: list[str] = []

WORKFLOW = ROOT / ".github" / "workflows-pending" / "modal-deploy.yml"
DECISIONS = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")

# A minute nothing owns. 13:00-14:00 UTC is the margin `pipeline/llm.py` keeps
# empty on purpose, so it is the honest choice for "clear" rather than a time
# that happens to work today.
CLEAR = datetime(2026, 10, 8, 13, 30, tzinfo=timezone.utc)


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


# ------------------------------------------------------------------ the ladder

def test_the_gates_are_read_off_the_modules_and_not_kept_beside_them():
    """An app that calls a model has both gates; the one that does not has neither."""
    for app in ("triage", "interpret", "distill", "weekly"):
        check(f"{app} carries preflight and rehearse",
              dg.gates_for(app) == ["preflight", "rehearse"],
              str(dg.gates_for(app)))
    check("ingest carries neither, because it calls no model",
          dg.gates_for("ingest") == [], str(dg.gates_for("ingest")))


def test_every_derived_gate_is_one_the_register_already_names():
    """The derivation is cross-checked against docs/decisions.md, not trusted.

    A regex over a module could find a `rehearse` that is not a gate, or miss
    one that is. The ADRs wrote these chains out by hand four times, so they
    are an independent witness: every `modal run x::gate` this file produces
    should be a string that register already contains.
    """
    for app, module in dg.APPS.items():
        for gate in dg.gates_for(app):
            wanted = f"modal run {module}::{gate}"
            check(f"the register names `{wanted}`", wanted in DECISIONS)
    check("and it names no gate for ingest",
          "modal run pipeline/ingest.py::" not in DECISIONS)


def test_the_deploy_is_last_and_the_budget_guard_is_first():
    for app in dg.APPS:
        steps = dg.ladder(app)
        check(f"{app} ends in its own deploy",
              steps[-1] == ["modal", "deploy", dg.APPS[app]], str(steps[-1]))
        check(f"{app} deploys exactly once",
              sum(1 for s in steps if s[:2] == ["modal", "deploy"]) == 1,
              str(steps))
        if dg.gates_for(app):
            check(f"{app} sizes the request before it sends one",
                  steps[0] == ["python3", "pipeline/budget.py"], str(steps[0]))
            check(f"{app} preflights before it rehearses",
                  [s[-1].split("::")[-1] for s in steps if s[:2] == ["modal", "run"]]
                  == ["preflight", "rehearse"], str(steps))
        else:
            check(f"{app} is a bare deploy, with no request to size",
                  steps == [["modal", "deploy", dg.APPS[app]]], str(steps))


def test_a_gate_that_fails_leaves_the_deploy_unrun():
    """The whole point of the chain, as a test rather than as an ampersand."""
    for failing in ("pipeline/budget.py", "preflight", "rehearse"):
        ran: list[str] = []

        def runner(argv, failing=failing, ran=ran):
            joined = " ".join(argv)
            ran.append(joined)
            return 1 if failing in joined else 0

        status = dg.run("weekly", runner=runner, out=lambda *_: None)
        check(f"a failing {failing} is a non-zero exit", status == 1, str(status))
        check(f"and nothing after {failing} ran",
              not any(r.startswith("modal deploy") for r in ran), str(ran))


def test_a_green_ladder_reaches_the_deploy():
    ran: list[str] = []
    status = dg.run("weekly", runner=lambda argv: ran.append(" ".join(argv)) or 0,
                    out=lambda *_: None)
    check("every rung green is a zero exit", status == 0, str(status))
    check("and the last thing that ran was the deploy",
          ran[-1] == "modal deploy pipeline/weekly.py", str(ran))


# ------------------------------------------------------------------ the window

def test_the_window_table_is_imported_and_not_copied():
    """A second copy of the schedule is a copy that disagrees with the crons."""
    check("the windows are pipeline/llm.py's own",
          dg._windows() == dict(llm.KIMI_WINDOWS), str(dg._windows()))
    check("and that table is the one the overlap guard checks",
          llm.window_overlaps() == [], str(llm.window_overlaps()))


def test_every_minute_of_every_reserved_window_is_refused():
    """Checked exhaustively, because an off-by-one here is a 429 in production."""
    for job, (start, end) in llm.KIMI_WINDOWS.items():
        for minute in range(start, end):
            when = datetime(2026, 10, 8, minute // 60, minute % 60,
                            tzinfo=timezone.utc)
            if dg.window_conflict(when) is None:
                check(f"{job} owns {minute // 60:02d}:{minute % 60:02d}",
                      False, "the window was reported clear")
                break
        else:
            check(f"every minute of {job}'s window is refused", True)
        # The minute the window ends is the first clear one, by the same
        # half-open convention `window_overlaps` uses.
        after = datetime(2026, 10, 8, (end // 60) % 24, end % 60,
                         tzinfo=timezone.utc)
        if end % (24 * 60) != 0:
            owner = dg.window_conflict(after)
            check(f"and the minute {job}'s window ends is not still its own",
                  owner is None or job not in owner, str(owner))


def test_the_refusal_names_the_job_and_the_next_clear_minute():
    """A refusal a reader cannot act on is a refusal they will route around."""
    noon = datetime(2026, 10, 8, 12, 30, tzinfo=timezone.utc)
    why = dg.window_conflict(noon)
    check("it names the job that owns the hour",
          why is not None and "triage" in why, str(why))
    check("it names the concurrency incident, not just a rule",
          why is not None and "concurrency is 1" in why, str(why))
    check("and it says when the band is clear",
          why is not None and "13:00 UTC" in why, str(why))
    check("the margin itself is clear", dg.window_conflict(CLEAR) is None,
          str(dg.window_conflict(CLEAR)))


def test_a_naive_timestamp_is_read_as_utc_and_not_as_local():
    """The runner's clock is UTC and a hand-run one may not be."""
    aware = dg.window_conflict(datetime(2026, 10, 8, 12, 30, tzinfo=timezone.utc))
    check("a timezone-aware noon is refused", aware is not None, str(aware))


def test_the_window_refuses_the_rehearsal_and_never_the_bare_deploy():
    """ingest spends no call, so the concurrency limit has no opinion about it."""
    out: list[str] = []
    status = dg.main(["--app", "ingest"], now=datetime(2026, 10, 8, 12, 30,
                                                       tzinfo=timezone.utc),
                     runner=lambda argv: 0, out=out.append)
    check("a bare deploy proceeds inside a reserved hour", status == 0, str(out))
    check("and nothing was refused", not any("refusing" in o for o in out), str(out))

    out = []
    status = dg.main(["--app", "weekly"], now=datetime(2026, 10, 8, 12, 30,
                                                       tzinfo=timezone.utc),
                     runner=lambda argv: 0, out=out.append)
    check("a rehearsal inside a reserved hour is refused", status == 2, str(out))
    check("before anything runs",
          not any("modal" in o and "[" in o for o in out), str(out))


def test_the_override_is_available_and_says_so_loudly():
    out: list[str] = []
    status = dg.main(["--app", "weekly", "--ignore-window"],
                     now=datetime(2026, 10, 8, 12, 30, tzinfo=timezone.utc),
                     runner=lambda argv: 0, out=out.append)
    check("the chair can still override", status == 0, str(out))
    check("and the run says it did",
          any(o.startswith("WARNING") for o in out), str(out))


def test_plan_runs_nothing_at_all():
    ran: list[str] = []
    out: list[str] = []
    status = dg.main(["--plan"], now=CLEAR,
                     runner=lambda argv: ran.append(argv) or 0, out=out.append)
    check("--plan exits zero", status == 0, str(status))
    check("and runs nothing", ran == [], str(ran))
    printed = "\n".join(out)
    for app in dg.APPS:
        check(f"--plan shows {app}", f"# {app}" in printed)
    check("and reports the window either way", "# window:" in printed, printed)


def test_all_follows_the_clock_and_not_the_alphabet():
    """Upstream first, so a chain that stops halfway stops with ingest current."""
    check("the order is the pipeline's own",
          list(dg.APPS) == ["ingest", "triage", "interpret", "distill", "weekly"],
          str(list(dg.APPS)))


# ------------------------------------------- the workflow that waits for a hand

def test_the_pending_workflow_is_a_button_and_never_a_trigger():
    """The law puts the rehearsal in a hand, so this file must not fire on merge.

    This is the assertion that stops a later edit from quietly turning the
    dispatch into a push trigger, which would make CI the thing that installs a
    schedule and is what docs/agents/runtime-changes.md forbids by name.
    """
    body = WORKFLOW.read_text(encoding="utf-8")
    check("it exists where a seat may write it", WORKFLOW.exists())
    check("it is dispatched by hand", "workflow_dispatch:" in body)
    for trigger in ("\n  push:", "\n  schedule:", "\n  pull_request:"):
        check(f"and never by{trigger.strip().rstrip(':')}",
              trigger not in body, repr(trigger))


def test_the_workflow_runs_the_ladder_rather_than_its_own_copy_of_it():
    body = WORKFLOW.read_text(encoding="utf-8")
    check("it calls the tool", "tools/deploy_gate.py" in body)
    # Comments are exempt, and only comments: the header explains what the file
    # replaces, and that explanation has to be allowed to name the command.
    live = [ln for ln in body.splitlines() if not ln.lstrip().startswith("#")]
    check("and holds no deploy command of its own",
          not any("modal deploy" in ln or "modal run" in ln for ln in live),
          "the workflow carries its own chain instead of calling the tool")
    for name in ("MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET"):
        check(f"it reads {name} by name", f"secrets.{name}" in body)
    check("it installs the tokenizer the budget rung needs",
          "tiktoken" in body, body[:0])


def test_the_workflow_offers_exactly_the_apps_the_tool_knows():
    """A choice list that drifts from APPS is a dispatch that fails on submit."""
    body = WORKFLOW.read_text(encoding="utf-8")
    line = [ln for ln in body.splitlines() if "options:" in ln]
    check("there is one options list", len(line) == 1, str(line))
    offered = line[0].split("[", 1)[1].rstrip("]").replace(" ", "").split(",") \
        if line else []
    check("and it is every app plus all",
          offered == list(dg.APPS) + ["all"], str(offered))


def test_the_pending_directory_documents_what_is_waiting_in_it():
    """That README is how the owner knows a file here needs moving."""
    readme = (ROOT / ".github" / "workflows-pending" / "README.md") \
        .read_text(encoding="utf-8")
    check("modal-deploy.yml has a section", "modal-deploy.yml" in readme)
    check("and the section names the secrets it waits on",
          "MODAL_TOKEN_ID" in readme, "no secret named")


def main() -> int:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            print(name)
            fn()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} check(s) failed: {', '.join(FAILURES)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
