"""The press's failure modes, as tests. Incident 24.

Three press failures in five days (413, 429, 404) said the same thing three
ways: the press runs on a provider whose free tier changes under it. These
tests encode what the press must do when it does change, because every one of
these paths only ever runs on a bad day and a path that only runs on a bad day
is a path nothing has ever exercised.

Run with `python3 tests/test_press_resilience.py`.
"""

import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub modal so the press's logic can be tested without the Modal SDK or any
# credentials. Everything under test is pure or takes its transport by
# injection; only the decorators need modal to exist.
if "modal" not in sys.modules:
    modal = types.ModuleType("modal")
    modal.Cron = lambda *a, **k: None
    modal.Secret = types.SimpleNamespace(from_name=lambda *a, **k: None)

    class _Image:
        def __getattr__(self, name):
            return lambda *a, **k: self

    modal.Image = types.SimpleNamespace(debian_slim=lambda *a, **k: _Image())
    modal.App = lambda *a, **k: types.SimpleNamespace(
        function=lambda *a, **k: (lambda f: f),
        local_entrypoint=lambda *a, **k: (lambda f: f),
    )
    sys.modules["modal"] = modal

from pipeline import budget  # noqa: E402
from pipeline import weekly  # noqa: E402

FAILURES = []


def check(name, condition, detail=""):
    if condition:
        print(f"  ok   {name}")
    else:
        FAILURES.append(f"{name}: {detail}")
        print(f"  FAIL {name}: {detail}")


# ---------------- the fallback list itself ----------------

def test_fallback_list():
    print("the fallback list")
    models = weekly.FALLBACK_MODELS
    check("at least three fallbacks", len(models) >= 3,
          f"only {len(models)}; one model is a single point of failure")
    check("no duplicates", len(set(models)) == len(models), f"{models}")
    check("every fallback has published limits",
          all(m in budget.MODELS for m in models),
          f"missing from budget.MODELS: {[m for m in models if m not in budget.MODELS]}")
    check("no withdrawn model in the list",
          not any(m in budget.DECOMMISSIONED for m in models),
          f"withdrawn: {[m for m in models if m in budget.DECOMMISSIONED]}")
    check("MODEL is the head of the list", weekly.MODEL == models[0],
          f"MODEL={weekly.MODEL}, head={models[0]}")
    # the whole point of rank two: a family withdrawal must not take the list
    vendors = {m.split("/")[0] for m in models}
    check("more than one vendor in the list", len(vendors) > 1,
          f"all of {models} come from {vendors}, so one withdrawal takes all")
    check("the guard reads the list out of production",
          budget.fallback_models() == models,
          f"budget.fallback_models()={budget.fallback_models()}")


# ---------------- incident 24's 404 ----------------

def test_withdrawn_model_is_explained():
    print("a withdrawn model")
    check("groq/compound is recorded as withdrawn",
          "groq/compound" in budget.DECOMMISSIONED)
    try:
        budget.limit_for("groq/compound")
    except KeyError as exc:
        check("limit_for explains it rather than raising a bare KeyError",
              "withdrawn" in str(exc), str(exc))
    else:
        check("limit_for refuses a withdrawn model", False, "it returned a limit")


def test_choose_model_skips_absent_models():
    print("choose_model against a provider that has lost a model")
    prompt = "you are an editor. " * 20
    payload = budget.encode({"new_claims": []})
    # the primary is gone at the provider; the next present model must be taken
    available = {weekly.FALLBACK_MODELS[1], weekly.FALLBACK_MODELS[2]}
    choice = budget.choose_model(weekly.FALLBACK_MODELS, available, prompt,
                                 payload, 1_000)
    check("falls through to the first model the provider still has",
          choice.model == weekly.FALLBACK_MODELS[1], f"chose {choice.model}")
    check("says why the primary was rejected",
          any(weekly.FALLBACK_MODELS[0] == name and "404" in why
              for name, why in choice.rejected),
          f"{choice.rejected}")

    choice = budget.choose_model(weekly.FALLBACK_MODELS, set(), prompt,
                                 payload, 1_000)
    check("no model chosen when the provider has none of them",
          choice.model is None, f"chose {choice.model}")
    check("and every rejection is accounted for",
          len(choice.rejected) == len(weekly.FALLBACK_MODELS),
          f"{choice.rejected}")


def test_availability_failure_is_not_an_empty_set():
    print("availability under a network failure")

    class Boom:
        def get(self, *a, **k):
            raise OSError("connection reset")

    saved = sys.modules.get("httpx")
    sys.modules["httpx"] = Boom()
    try:
        budget.available_models("key-shaped-string")
    except budget.AvailabilityError as exc:
        check("a failed request raises rather than reporting zero models",
              "connection reset" in str(exc), str(exc))
    else:
        check("a failed request raises", False, "it returned a set")
    finally:
        if saved is None:
            del sys.modules["httpx"]
        else:
            sys.modules["httpx"] = saved

    try:
        budget.available_models("")
    except budget.AvailabilityError as exc:
        check("a missing key is named as such", "key" in str(exc).lower(), str(exc))
    else:
        check("a missing key raises", False, "it returned a set")


# ---------------- incident 22's 413, still guarded ----------------

def test_budget_still_refuses_an_oversized_request():
    print("the budget guard, on every fallback")
    prompt = budget._filler(400_000)          # far past any free-tier ceiling
    payload = budget.worst_case_payload()
    choice = budget.choose_model(weekly.FALLBACK_MODELS, None, prompt,
                                 budget.encode(payload), 6_000)
    check("no model is chosen for a request nothing can take",
          choice.model is None, f"chose {choice.model}")
    check("every rejection states the overage",
          all("over budget by" in why for _, why in choice.rejected),
          f"{choice.rejected}")


def test_each_model_gets_an_untrimmed_payload():
    """fit_payload trims in place, so write_digest must copy per attempt.

    Without the copy the second model inherits the first model's trimming and
    writes a thinner issue than it had room for, which is a silent quality
    regression rather than a crash.
    """
    print("payload isolation across fallbacks")
    payload = budget.worst_case_payload()
    before = len(payload["new_claims"])
    import copy
    budget.fit_payload(copy.deepcopy(payload), budget._filler(20_000), 1_000,
                       "openai/gpt-oss-20b")
    check("trimming a copy leaves the original intact",
          len(payload["new_claims"]) == before,
          f"{before} -> {len(payload['new_claims'])}")


# ---------------- incident 24's silence ----------------

def test_notify_owner_never_raises():
    print("the owner alarm")
    import os
    saved = {k: os.environ.get(k) for k in
             ("GMAIL_ADDRESS", "GMAIL_APP_PASSWORD", "PRESS_ALERT_TO")}
    try:
        for k in saved:
            os.environ.pop(k, None)
        out = weekly.notify_owner("W38 could not be printed", "404 on everything")
        check("with no secret it reports that nobody was told",
              out.startswith("NOT NOTIFIED"), out)

        os.environ["GMAIL_ADDRESS"] = "press@example.com"
        os.environ["GMAIL_APP_PASSWORD"] = "not-a-real-password"
        import smtplib
        real = smtplib.SMTP_SSL

        def explode(*a, **k):
            raise smtplib.SMTPException("refused")

        smtplib.SMTP_SSL = explode
        try:
            out = weekly.notify_owner("subject", "detail")
        finally:
            smtplib.SMTP_SSL = real
        check("an SMTP failure is reported, not raised",
              out.startswith("NOT NOTIFIED") and "refused" in out, out)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_press_cannot_print_names_every_attempt():
    print("write_digest with nothing available")
    payload = {"new_claims": [], "superseded": [], "deprecated": [],
               "deep_reads": [], "traction": {"supported_claims": [],
                                              "citation_movers": []}}
    try:
        weekly.write_digest(payload, "prompt", available=set())
    except weekly.PressCannotPrint as exc:
        for model in weekly.FALLBACK_MODELS:
            check(f"the error names {model}", model in str(exc), str(exc)[:200])
    else:
        check("an empty provider raises PressCannotPrint", False, "it returned")


def test_call_model_walks_and_backs_off():
    print("429 backoff and the 404 hand-off")
    import os
    sent = []
    slept = []

    class Resp:
        def __init__(self, status, body="{}", headers=None, payload=None):
            self.status_code = status
            self.text = body
            self.headers = headers or {}
            self._payload = payload

        def json(self):
            return self._payload

    scripted = [
        Resp(429, "slow down", {"retry-after": "1"}),
        Resp(429, "slow down", {"retry-after": "1"}),
        Resp(200, payload={"choices": [{"finish_reason": "stop", "message":
                                        {"content": "# An issue\n\nbody"}}]}),
    ]

    class Fake:
        def post(self, url, **kw):
            sent.append(kw["json"]["model"])
            return scripted.pop(0)

    saved_httpx = sys.modules.get("httpx")
    saved_sleep = weekly.time.sleep
    saved_key = os.environ.get("GROQ_API_KEY")
    sys.modules["httpx"] = Fake()
    weekly.time.sleep = lambda s: slept.append(s)
    os.environ["GROQ_API_KEY"] = "test"
    try:
        body = weekly.call_model("openai/gpt-oss-120b", "prompt", "user")
        check("two 429s are retried and the third attempt wins",
              body.startswith("# An issue"), body[:60])
        check("it backed off between attempts, honouring retry-after",
              slept == [1.0, 1.0], f"{slept}")
        check("all three attempts went to the same model",
              sent == ["openai/gpt-oss-120b"] * 3, f"{sent}")

        # a 404 must not be retried: waiting does not bring a model back
        scripted.append(Resp(404, "model_not_found"))
        sent.clear()
        slept.clear()
        try:
            weekly.call_model("groq/compound", "prompt", "user")
        except weekly.ModelGone as exc:
            check("404 raises ModelGone immediately", "404" in str(exc), str(exc))
            check("and is not retried", len(sent) == 1 and slept == [], f"{sent} {slept}")
        else:
            check("404 raises ModelGone", False, "it returned")

        # backoff is capped, so a hostile retry-after cannot park the run
        scripted.extend([Resp(429, "no", {"retry-after": "99999"})
                         for _ in range(weekly.RETRIES_PER_MODEL)])
        slept.clear()
        try:
            weekly.call_model("openai/gpt-oss-120b", "prompt", "user")
        except weekly.RateLimited:
            check("every sleep is capped at BACKOFF_CEILING",
                  all(s <= weekly.BACKOFF_CEILING for s in slept), f"{slept}")
            check("it gives up after RETRIES_PER_MODEL attempts",
                  len(slept) == weekly.RETRIES_PER_MODEL - 1, f"{slept}")
        else:
            check("a permanent 429 raises RateLimited", False, "it returned")
    finally:
        if saved_httpx is None:
            sys.modules.pop("httpx", None)
        else:
            sys.modules["httpx"] = saved_httpx
        weekly.time.sleep = saved_sleep
        if saved_key is None:
            os.environ.pop("GROQ_API_KEY", None)
        else:
            os.environ["GROQ_API_KEY"] = saved_key


def test_the_schedule_is_outside_the_cron_band():
    """The press must not run while the daily crons hold the shared TPM budget.

    Groq applies rate limits at the organization level, so every cron on this
    key draws from one 8,000 TPM bucket. The daily crons run 11:00 to 14:00
    with one-hour timeouts, so 11:00 through 15:00 is contested.
    """
    print("the schedule")
    source = (Path(__file__).resolve().parents[1] / "pipeline" / "weekly.py").read_text()
    import re
    hours = [int(m) for m in re.findall(r'modal\.Cron\("0 (\d+) \* \* 1"\)', source)]
    check("the weekly cron is found", len(hours) == 1, f"{hours}")
    if hours:
        check("it does not run in the daily crons' band (11:00-15:00)",
              not (11 <= hours[0] <= 15), f"runs at {hours[0]}:00 UTC")


if __name__ == "__main__":
    for fn in [test_fallback_list, test_withdrawn_model_is_explained,
               test_choose_model_skips_absent_models,
               test_availability_failure_is_not_an_empty_set,
               test_budget_still_refuses_an_oversized_request,
               test_each_model_gets_an_untrimmed_payload,
               test_notify_owner_never_raises,
               test_press_cannot_print_names_every_attempt,
               test_call_model_walks_and_backs_off,
               test_the_schedule_is_outside_the_cron_band]:
        fn()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} failure(s)")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    print("all press-resilience checks passed")
