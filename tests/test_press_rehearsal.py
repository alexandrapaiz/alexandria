"""The rehearsal print, as tests. INC-2026-09-24-press-provider-migration.

The press moved to a new provider and failed four times in one evening. Each
failure was an integration property that only a real call reveals, and the org
had no way to make one real call without writing to the database of record and
mailing the subscribers. `rehearse()` is that call, specified in
docs/agents/press-rehearsal.md and enforced as gate 3 of
docs/agents/runtime-changes.md's ladder.

These tests hold the two promises that make a rehearsal safe to run, because
both are promises about what does *not* happen and neither leaves a trace when
it is kept: it never writes to `digests`, and it never sends. They also hold
the promises that make it useful, which are the four failures rendered as
output a human can read before a deploy rather than an alarm email after one.

No Modal, no provider, no database. Run with
`python3 tests/test_press_rehearsal.py`.
"""

import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub modal and psycopg the way tests/test_press_resilience.py stubs modal:
# everything under test is pure or takes its transport by injection, and only
# the decorators and the connect() call need the libraries to exist.
if "modal" not in sys.modules:
    modal = types.ModuleType("modal")
    modal.Cron = lambda *a, **k: None
    modal.Secret = types.SimpleNamespace(from_name=lambda name: f"secret:{name}")

    class _Image:
        def __getattr__(self, name):
            return lambda *a, **k: self

    modal.Image = types.SimpleNamespace(debian_slim=lambda *a, **k: _Image())
    modal.App = lambda *a, **k: types.SimpleNamespace(
        function=lambda *a, **k: (lambda f: f),
        local_entrypoint=lambda *a, **k: (lambda f: f),
    )
    sys.modules["modal"] = modal

from pipeline import weekly  # noqa: E402

SOURCE = (Path(__file__).resolve().parents[1] / "pipeline" / "weekly.py").read_text()
SCHEMA = (Path(__file__).resolve().parents[1] / "db" / "schema.sql").read_text()

FAILURES = []


def check(name, condition, detail=""):
    if condition:
        print(f"  ok   {name}")
    else:
        FAILURES.append(f"{name}: {detail}")
        print(f"  FAIL {name}: {detail}")


# ---------------- a database that records instead of storing ----------------

class FakeCursor:
    def __init__(self, row):
        self._row = row

    def fetchone(self):
        return self._row

    def fetchall(self):
        return [self._row] if self._row else []


class FakeConn:
    """Records every statement, and hands back the row the test scripted."""

    def __init__(self, log, rows):
        self.log = log
        self.rows = rows

    def execute(self, sql, params=None):
        self.log.append(("sql", " ".join(sql.split()).lower(), params))
        for fragment, row in self.rows.items():
            if fragment in " ".join(sql.split()).lower():
                return FakeCursor(row)
        return FakeCursor(None)

    def commit(self):
        self.log.append(("commit", None, None))

    def __enter__(self):
        self.log.append(("open", None, None))
        return self

    def __exit__(self, *exc):
        self.log.append(("close", None, None))
        return False


def run_rehearse(*, model=None, rows=None, prompt="the editorial instruction"):
    """Drive rehearse() with a scripted database and a scripted press.

    Returns (result_or_exception, log, printed). The model call itself is
    stubbed, because what these tests hold is rehearse()'s own structure: what
    it writes, what it refuses, and the order it does things in. The model
    call's own behaviour is tests/test_press_resilience.py's subject.
    """
    import os

    model = model or weekly.FALLBACK_MODELS[0]
    log = []
    # the scratch table is there unless a test scripts it away
    rows = {"to_regclass": ("press_rehearsals",), **(rows or {})}
    printed = []

    saved = {
        "psycopg": sys.modules.get("psycopg"),
        "gather": weekly.gather,
        "write_digest": weekly.write_digest,
        "check_availability": weekly.check_availability,
        "open": weekly.__dict__.get("open"),
        "print": weekly.__dict__.get("print"),
        "url": os.environ.get("DATABASE_URL"),
    }

    fake_psycopg = types.ModuleType("psycopg")
    fake_psycopg.connect = lambda url: FakeConn(log, rows)
    sys.modules["psycopg"] = fake_psycopg
    os.environ["DATABASE_URL"] = "postgres://scripted"

    weekly.check_availability = lambda: set(weekly.FALLBACK_MODELS)
    weekly.gather = lambda conn: {
        "stats": {"papers_ingested": 40, "claims_distilled": 12, "edges_drawn": 9},
        "new_claims": [{"claim": "x"}], "superseded": [], "deprecated": [],
        "deep_reads": [], "traction": {"supported_claims": [], "citation_movers": []},
    }

    def fake_write_digest(payload, prompt_text, available=None, trace=None):
        log.append(("model_call", model, None))
        if trace is not None:
            trace.update({"model": model, "finish_reason": "stop",
                          "elapsed_seconds": 74.2,
                          "usage": {"completion_tokens": 1103}})
        return "# What the week actually settled\n\nA paragraph.", model

    weekly.write_digest = fake_write_digest
    weekly.open = lambda path, *a, **k: types.SimpleNamespace(
        read=lambda: prompt, __enter__=lambda s: s, __exit__=lambda *e: False)
    weekly.print = lambda *a, **k: printed.append(" ".join(str(x) for x in a))

    try:
        return weekly.rehearse(), log, printed
    except Exception as exc:
        return exc, log, printed
    finally:
        for name in ("gather", "write_digest", "check_availability"):
            setattr(weekly, name, saved[name])
        for name in ("open", "print"):
            if saved[name] is None:
                weekly.__dict__.pop(name, None)
            else:
                weekly.__dict__[name] = saved[name]
        if saved["psycopg"] is None:
            sys.modules.pop("psycopg", None)
        else:
            sys.modules["psycopg"] = saved["psycopg"]
        if saved["url"] is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = saved["url"]


# ---------------- the two promises that make it safe ----------------

def test_a_rehearsal_never_writes_to_the_digests_table():
    """The digests row is the record the site and the readers depend on."""
    print("a rehearsal writes to press_rehearsals and never to digests")
    sha = weekly.hashlib.sha256(b"the editorial instruction").hexdigest()[:12]
    result, log, _ = run_rehearse(
        rows={"insert into press_rehearsals": (7,),
              "select model, prompt_sha": (weekly.FALLBACK_MODELS[0], sha)})
    statements = [sql for kind, sql, _ in log if kind == "sql"]
    check("it succeeded on the happy path", isinstance(result, str), repr(result))
    check("nothing was inserted into digests",
          not any("insert into digests" in s for s in statements), f"{statements}")
    check("one row went into press_rehearsals",
          sum("insert into press_rehearsals" in s for s in statements) == 1,
          f"{statements}")
    check("the scratch row is named in the return value",
          isinstance(result, str) and "press_rehearsals 7" in result, repr(result))
    check("the return value says it sent to nobody",
          isinstance(result, str) and "sent to nobody" in result, repr(result))


def test_a_rehearsal_cannot_send_because_it_has_no_credential():
    """Not a missing call. A missing secret, which code review cannot undo."""
    print("the rehearsal container holds no mail credential")
    decorator = SOURCE.split("def rehearse")[0].split("@app.function")[-1]
    # the comment above the list says the word "Gmail", so read the list
    mounted = decorator.split("secrets=[")[1].split("]")[0]
    check("neither Gmail secret is mounted on rehearse",
          "Gmail" not in mounted and "gmail_pass" not in mounted, mounted)
    check("the model providers are mounted, so the call is real",
          "moonshot" in mounted and "groq" in mounted, mounted)
    check("neon is mounted, so the payload is the real payload",
          "neon" in mounted, mounted)
    body = SOURCE.split("def rehearse")[1].split("@app.function")[0]
    check("send_newsletter is never called in rehearse",
          "send_newsletter(" not in body)
    check("notify_owner is never called in rehearse",
          "notify_owner(" not in body)


# ---------------- the four failures, made visible ----------------

def test_the_report_shows_every_failure_the_incident_found():
    print("the report renders all four failures of the migration incident")
    report = weekly.rehearsal_report(
        model="kimi-k2.6", body="# A title\n\nSome words here to count.",
        prompt_sha="abc123def456",
        stats_line="2026-W39: {'papers_ingested': 40} | new_claims=1 deprecated=0",
        finish_reason="stop", elapsed_seconds=74.2, row_id=7,
        success_subject="What the week actually settled")
    # failure 1: an empty response with finish_reason 'length' was silent
    check("finish_reason is printed", "finish_reason: 'stop'" in report, report)
    # failure 1's other half: the reservation that was spent on hidden thinking
    check("the output reservation is printed",
          f"reservation: {weekly.MAX_COMPLETION_TOKENS}" in report, report)
    # failure 2: the client read timeout
    check("the client timeout is printed",
          f"timeout: {weekly.CLIENT_TIMEOUT_SECONDS}s" in report, report)
    # failure 4: an alarm subject is prose only a bad day renders
    check("the success subject is printed",
          "What the week actually settled" in report, report)
    check("the cannot-print alarm subject is printed",
          weekly.ALARM_SUBJECT_CANNOT_PRINT in report, report)
    check("the written-but-not-sent alarm subject is printed",
          weekly.ALARM_SUBJECT_NOT_SENT in report, report)
    subjects = [ln for ln in report.splitlines() if "subject" in ln]
    check("three subjects are shown", len(subjects) == 3, f"{subjects}")
    check("no subject carries a week id or a bracket tag",
          not any("[alexandria]" in ln or "2026-W39" in ln for ln in subjects),
          f"{subjects}")
    check("the model, the word count and the seconds lead the report",
          report.startswith("rehearsal: kimi-k2.6 wrote 7 words in 74.2s"),
          report.splitlines()[0])
    check("the payload stats line is printed", "papers_ingested" in report, report)
    check("the scratch row id is printed",
          "saved to press_rehearsals id 7" in report, report)
    check("the body itself is shown", "# A title" in report, report)


def test_the_alarm_subjects_printed_are_the_ones_weekly_actually_sends():
    """A rehearsal that prints a copy of the subject proves nothing."""
    print("the alarm subjects are shared, not copied")
    weekly_body = SOURCE.split("def weekly()")[1].split("@app.function")[0]
    check("weekly passes ALARM_SUBJECT_CANNOT_PRINT to notify_owner",
          "ALARM_SUBJECT_CANNOT_PRINT" in weekly_body, weekly_body[-400:])
    check("weekly passes ALARM_SUBJECT_NOT_SENT to notify_owner",
          "ALARM_SUBJECT_NOT_SENT" in weekly_body, weekly_body[-400:])
    check("no alarm subject survives as a literal at its call site",
          "notify_owner(\n            \"" not in SOURCE)


def test_the_client_timeout_is_one_name_in_two_places():
    """Failure 2. A number typed twice is a number that drifts."""
    print("the timeout the rehearsal prints is the timeout the press sends")
    import os

    sent = {}

    class Resp:
        status_code = 200
        text = "{}"
        headers = {}

        def json(self):
            return {"choices": [{"finish_reason": "stop", "usage": None,
                                 "message": {"content": "# Issue\n\nbody"}}],
                    "usage": {"completion_tokens": 1103}}

    class Fake:
        def post(self, url, **kw):
            sent.update(kw)
            return Resp()

    saved_httpx = sys.modules.get("httpx")
    saved_key = os.environ.get("MOONSHOT_API_KEY")
    sys.modules["httpx"] = Fake()
    os.environ["MOONSHOT_API_KEY"] = "moonshot-test-key"
    try:
        trace = {}
        weekly.call_model(weekly.MODEL, "prompt", "user", trace)
        check("the request carries CLIENT_TIMEOUT_SECONDS",
              sent.get("timeout") == weekly.CLIENT_TIMEOUT_SECONDS,
              f"sent {sent.get('timeout')}, constant {weekly.CLIENT_TIMEOUT_SECONDS}")
        check("it is long enough for a model that reasons for minutes",
              weekly.CLIENT_TIMEOUT_SECONDS >= 600,
              f"{weekly.CLIENT_TIMEOUT_SECONDS}s; 300s timed out on 2026-09-24")
        check("and it fits inside the Modal function timeout",
              weekly.CLIENT_TIMEOUT_SECONDS < 1800,
              f"{weekly.CLIENT_TIMEOUT_SECONDS}s against a 1800s function")
        check("the trace carries the finish_reason",
              trace.get("finish_reason") == "stop", f"{trace}")
        check("the trace carries how long the call took",
              isinstance(trace.get("elapsed_seconds"), float), f"{trace}")
        check("the trace carries the provider's own usage numbers",
              trace.get("usage") == {"completion_tokens": 1103}, f"{trace}")
    finally:
        if saved_httpx is None:
            sys.modules.pop("httpx", None)
        else:
            sys.modules["httpx"] = saved_httpx
        if saved_key is None:
            os.environ.pop("MOONSHOT_API_KEY", None)
        else:
            os.environ["MOONSHOT_API_KEY"] = saved_key


def test_the_scheduled_run_is_unchanged_by_the_trace():
    """weekly() passes no trace, so its call is byte-for-byte what it was."""
    print("the trace is an addition to the rehearsal, not to Monday")
    weekly_body = SOURCE.split("def weekly()")[1].split("@app.function")[0]
    check("weekly calls write_digest without a trace",
          "write_digest(payload, prompt, available)" in weekly_body,
          weekly_body[-800:])
    check("trace defaults to None on call_model",
          "trace: dict | None = None" in SOURCE)


def test_the_read_connection_closes_before_the_model_call():
    """Failure 3: Neon killed a transaction held open across the call."""
    print("no database connection is held open across the model call")
    sha = weekly.hashlib.sha256(b"the editorial instruction").hexdigest()[:12]
    _, log, _ = run_rehearse(
        rows={"insert into press_rehearsals": (7,),
              "select model, prompt_sha": (weekly.FALLBACK_MODELS[0], sha)})
    kinds = [kind for kind, _, _ in log]
    call = kinds.index("model_call")
    opens_before = [i for i, k in enumerate(kinds[:call]) if k == "open"]
    closes_before = [i for i, k in enumerate(kinds[:call]) if k == "close"]
    check("a connection was opened before the call", len(opens_before) == 1, f"{kinds}")
    check("and closed again before the call",
          len(closes_before) == 1, f"{kinds}")
    check("a second connection opens after the call, to save",
          kinds[call:].count("open") == 1, f"{kinds}")


def test_a_missing_scratch_table_costs_nothing():
    """Gate 3 must not spend a model call to discover it has nowhere to write."""
    print("no scratch table, no spending")
    result, log, _ = run_rehearse(rows={"to_regclass": (None,)})
    check("it raises before the model call",
          isinstance(result, weekly.PressCannotPrint), repr(result))
    check("no model was called",
          not any(kind == "model_call" for kind, _, _ in log),
          f"{[k for k, _, _ in log]}")
    check("the message names the command that fixes it",
          "db_setup.py::apply_schema" in str(result), str(result))
    check("and says plainly that nothing was spent",
          "Nothing was spent" in str(result), str(result))


# ---------------- the receipt, which is what makes it a gate ----------------

def test_a_receipt_from_a_different_model_is_not_a_receipt():
    print("the receipt must name what is about to be deployed")
    sha = weekly.hashlib.sha256(b"the editorial instruction").hexdigest()[:12]
    fallback = weekly.FALLBACK_MODELS[1]
    result, log, _ = run_rehearse(
        model=fallback,
        rows={"insert into press_rehearsals": (9,),
              "select model, prompt_sha": (fallback, sha)})
    check("it raises rather than passing the gate",
          isinstance(result, weekly.PressCannotPrint), repr(result))
    check("the message names the model that wrote",
          fallback in str(result), str(result)[:300])
    check("and the model that is about to be deployed",
          weekly.FALLBACK_MODELS[0] in str(result), str(result)[:300])
    statements = [sql for kind, sql, _ in log if kind == "sql"]
    check("the row was still written, because it is the evidence",
          any("insert into press_rehearsals" in s for s in statements),
          f"{statements}")


def test_a_receipt_from_a_different_prompt_is_not_a_receipt():
    print("a stale prompt hash fails the gate too")
    result, _, _ = run_rehearse(
        rows={"insert into press_rehearsals": (11,),
              "select model, prompt_sha": (weekly.FALLBACK_MODELS[0], "000000000000")})
    check("it raises", isinstance(result, weekly.PressCannotPrint), repr(result))
    check("the message names both prompt hashes",
          "000000000000" in str(result)
          and weekly.hashlib.sha256(b"the editorial instruction").hexdigest()[:12]
          in str(result), str(result)[:400])


# ---------------- the gate lives in the command ----------------

def test_the_deploy_chain_refuses_without_a_rehearsal():
    """A rule enforced by a charter line runs at the reliability of a model
    reading a file. A rule enforced by an `&&` runs at the reliability of a
    shell. docs/agents/runtime-changes.md, 2026-09-24."""
    print("the deploy command has the third link")
    chain = SOURCE.split("As one line")[1].split("No guard in that chain")[0]
    links = [ln.strip().rstrip("\\").strip() for ln in chain.splitlines()
             if ln.strip() and not ln.strip().startswith("&&") or "&&" in ln]
    joined = " ".join(chain.split())
    check("budget comes first", "python3 pipeline/budget.py" in joined, joined)
    check("preflight is in the chain",
          "modal run pipeline/weekly.py::preflight" in joined, joined)
    check("rehearse is in the chain",
          "modal run pipeline/weekly.py::rehearse" in joined, joined)
    check("rehearse comes before the deploy",
          joined.index("::rehearse") < joined.index("modal deploy"), joined)
    check("every link is joined by &&, so a failure stops the chain",
          joined.count("&&") >= 4, joined)
    del links


def test_the_scratch_table_cannot_shadow_a_published_week():
    print("the press_rehearsals table")
    block = SCHEMA.split("create table if not exists press_rehearsals")[1] \
        .split(");")[0]
    check("the table exists", block, "not found in db/schema.sql")
    for column in ("week", "body", "model", "prompt_sha", "elapsed_seconds",
                   "finish_reason", "payload_stats", "created_at"):
        check(f"it holds {column}", column in block, block)
    # strip the trailing comments before looking for constraints, since one
    # of them says the word
    code = "\n".join(ln.split("--")[0] for ln in block.splitlines())
    check("week is not unique, because many rehearsals of one week are normal",
          "unique" not in code.lower(), code)
    digests = SCHEMA.split("create table if not exists digests")[1].split(");")[0]
    check("digests still holds its unique week, untouched",
          "unique" in digests.lower(), digests)


def test_the_stats_line_is_the_one_weekly_prints():
    print("the payload line, shared between the rehearsal and Monday")
    payload = {"stats": {"papers_ingested": 40}, "new_claims": [1, 2],
               "deprecated": [], "superseded": [1],
               "traction": {"supported_claims": [], "citation_movers": [1]},
               "deep_reads": []}
    line = weekly.payload_line("2026-W39", payload)
    check("the week leads it", line.startswith("2026-W39:"), line)
    check("it counts the new claims", "new_claims=2" in line, line)
    check("it counts the deprecations", "deprecated=0" in line, line)
    weekly_body = SOURCE.split("def weekly()")[1].split("@app.function")[0]
    check("weekly prints it through the same function",
          "payload_line(week, payload)" in weekly_body, weekly_body[:900])
    counts = weekly.payload_counts(payload)
    check("the scratch row records every section's count",
          counts["superseded"] == 1 and counts["citation_movers"] == 1
          and counts["deep_reads"] == 0, f"{counts}")


if __name__ == "__main__":
    for fn in [test_a_rehearsal_never_writes_to_the_digests_table,
               test_a_rehearsal_cannot_send_because_it_has_no_credential,
               test_the_report_shows_every_failure_the_incident_found,
               test_the_alarm_subjects_printed_are_the_ones_weekly_actually_sends,
               test_the_client_timeout_is_one_name_in_two_places,
               test_the_scheduled_run_is_unchanged_by_the_trace,
               test_the_read_connection_closes_before_the_model_call,
               test_a_missing_scratch_table_costs_nothing,
               test_a_receipt_from_a_different_model_is_not_a_receipt,
               test_a_receipt_from_a_different_prompt_is_not_a_receipt,
               test_the_deploy_chain_refuses_without_a_rehearsal,
               test_the_scratch_table_cannot_shadow_a_published_week,
               test_the_stats_line_is_the_one_weekly_prints]:
        fn()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} failure(s)")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    print("all rehearsal checks passed")
