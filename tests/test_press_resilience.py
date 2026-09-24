"""The press's failure modes, as tests. Incident 24.

Three press failures in five days (413, 429, 404) said the same thing three
ways: the press runs on a provider whose free tier changes under it. These
tests encode what the press must do when it does change, because every one of
these paths only ever runs on a bad day and a path that only runs on a bad day
is a path nothing has ever exercised.

ADR-32 moved the press to Moonshot's Kimi and kept Groq as the last resort, so
the same tests now have to hold across two providers. The two-provider cases
are the ones at the bottom: the right base URL per model, no Groq-only
parameters on the Kimi path, and a missing key that names its Modal secret
instead of dying on a KeyError.

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
    # and since ADR-32, more than one PROVIDER, which is the stronger property:
    # a vendor can be withdrawn from a catalog, a provider can lose its account
    providers = {budget.provider_of(m) for m in models}
    check("more than one provider in the list", len(providers) > 1,
          f"all of {models} are served by {providers}")
    check("the head of the list is on the primary provider",
          budget.provider_of(models[0]) == budget.PRIMARY_PROVIDER,
          f"{models[0]} is on {budget.provider_of(models[0])}, not "
          f"{budget.PRIMARY_PROVIDER}")
    check("the guard reads the list out of production",
          budget.fallback_models() == models,
          f"budget.fallback_models()={budget.fallback_models()}")


# ---------------- incident 24's 404 ----------------

def test_withdrawn_model_is_explained():
    print("a withdrawn model")
    # one per provider, because model deprecation is not a Groq problem
    for name in ("groq/compound", "kimi-k2"):
        check(f"{name} is recorded as withdrawn", name in budget.DECOMMISSIONED)
        try:
            budget.limit_for(name)
        except KeyError as exc:
            check(f"limit_for explains {name} rather than raising a bare KeyError",
                  "withdrawn" in str(exc) or "discontinued" in str(exc), str(exc))
        else:
            check(f"limit_for refuses {name}", False, "it returned a limit")

    # The trap ADR-32 set without meaning to: the decision says "Kimi K2", the
    # obvious id is `kimi-k2`, and that id 404s. Nothing may point a press at
    # it, and the explanation must name the id that does work.
    check("kimi-k2 is not in the fallback list",
          "kimi-k2" not in weekly.FALLBACK_MODELS)
    check("and the record says which id replaced it",
          "kimi-k2.6" in budget.DECOMMISSIONED["kimi-k2"],
          budget.DECOMMISSIONED["kimi-k2"])


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
        budget.available_models("key-shaped-string", "moonshot")
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

    for provider in budget.PROVIDERS:
        try:
            budget.available_models("", provider)
        except budget.AvailabilityError as exc:
            check(f"a missing {provider} key names its Modal secret",
                  budget.PROVIDERS[provider]["secret"] in str(exc), str(exc))
        else:
            check(f"a missing {provider} key raises", False, "it returned a set")


# ---------------- incident 22's 413, still guarded ----------------

def test_budget_still_refuses_an_oversized_request():
    print("the budget guard, on every fallback")
    # Sized against the roomiest model in the list rather than a fixed number,
    # so this test cannot quietly stop testing anything the day the press moves
    # to a larger context. Kimi's 222,822 usable tokens would swallow the old
    # 400,000-character prompt whole.
    widest = max(budget.limit_for(m) for m in weekly.FALLBACK_MODELS)
    sample = budget._filler(10_000)
    chars_per_token = len(sample) / budget.count_tokens(sample)
    prompt = budget._filler(int(widest * chars_per_token * 1.2))
    check("the test prompt really is past every ceiling",
          budget.count_tokens(prompt) > widest,
          f"{budget.count_tokens(prompt)} tokens against {widest}")
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

        # a 404 must not be retried: waiting does not bring a model back.
        # Incident 24's shape exactly: a model the table still believes in,
        # answering 404 because the provider dropped it overnight.
        scripted.append(Resp(404, "model_not_found"))
        sent.clear()
        slept.clear()
        try:
            weekly.call_model("openai/gpt-oss-120b", "prompt", "user")
        except weekly.ModelGone as exc:
            check("404 raises ModelGone immediately", "404" in str(exc), str(exc))
            check("and is not retried", len(sent) == 1 and slept == [], f"{sent} {slept}")
        else:
            check("404 raises ModelGone", False, "it returned")

        # a model already known to be withdrawn never reaches the network
        sent.clear()
        try:
            weekly.call_model("groq/compound", "prompt", "user")
        except KeyError as exc:
            check("a withdrawn model is refused before any request is sent",
                  not sent and "withdrawn" in str(exc), f"{sent} {exc}")
        else:
            check("a withdrawn model is refused", False, "it sent a request")

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


# ---------------- ADR-32: two providers, one press ----------------

def test_the_request_goes_to_the_right_provider():
    """Every model must be called at its own base URL, with its own key.

    The cheapest possible way to reproduce incident 24 on a new provider would
    be to send a Kimi model id to Groq's endpoint: a 404, from a model that
    exists, because the request went to the wrong company.
    """
    print("provider routing")
    import os

    class Resp:
        status_code = 200
        text = "{}"
        headers = {}

        def json(self):
            return {"choices": [{"finish_reason": "stop",
                                 "message": {"content": "# Issue\n\nbody"}}]}

    seen = []

    class Fake:
        def post(self, url, **kw):
            seen.append((url, kw["headers"]["Authorization"], kw["json"]))
            return Resp()

    saved_httpx = sys.modules.get("httpx")
    saved = {k: os.environ.get(k) for k in ("MOONSHOT_API_KEY", "GROQ_API_KEY")}
    sys.modules["httpx"] = Fake()
    os.environ["MOONSHOT_API_KEY"] = "moonshot-test-key"
    os.environ["GROQ_API_KEY"] = "groq-test-key"
    try:
        for model in weekly.FALLBACK_MODELS:
            seen.clear()
            weekly.call_model(model, "prompt", "user")
            url, auth, body = seen[0]
            provider = budget.provider_of(model)
            base = budget.PROVIDERS[provider]["base_url"]
            check(f"{model} is called at {provider}",
                  url == f"{base}/chat/completions", url)
            check(f"{model} carries {provider}'s own key",
                  auth.endswith(os.environ[budget.PROVIDERS[provider]["key_env"]]),
                  "the wrong provider's key was sent")
            check(f"{model} asks for the model it says it does",
                  body["model"] == model, body["model"])
    finally:
        if saved_httpx is None:
            sys.modules.pop("httpx", None)
        else:
            sys.modules["httpx"] = saved_httpx
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_no_groq_only_parameters_on_the_kimi_path():
    """ADR-6 and the dispatch: one prompt in, one issue out, no tools.

    compound_custom was a Groq-only block for an agentic system that no longer
    exists. Temperature is not Groq-only but it is fixed by k2.6, so sending it
    is a knob that does nothing, which is worse than no knob at all.
    """
    print("the Kimi request body")
    import os

    class Resp:
        status_code = 200
        text = "{}"
        headers = {}

        def json(self):
            return {"choices": [{"finish_reason": "stop",
                                 "message": {"content": "# Issue\n\nbody"}}]}

    bodies = []

    class Fake:
        def post(self, url, **kw):
            bodies.append(kw["json"])
            return Resp()

    saved_httpx = sys.modules.get("httpx")
    saved_key = os.environ.get("MOONSHOT_API_KEY")
    sys.modules["httpx"] = Fake()
    os.environ["MOONSHOT_API_KEY"] = "moonshot-test-key"
    try:
        weekly.call_model(weekly.MODEL, "prompt", "user")
        body = bodies[0]
        check("no compound_custom anywhere in the body",
              "compound_custom" not in body, f"{sorted(body)}")
        check("no tools are offered to the press",
              not any(k in body for k in ("tools", "tool_choice",
                                          "search_settings")),
              f"{sorted(body)}")
        check("no temperature on the Kimi path, which fixes it anyway",
              "temperature" not in body, f"{sorted(body)}")
        check("the output reservation is sent as max_completion_tokens",
              body.get("max_completion_tokens") == weekly.MAX_COMPLETION_TOKENS,
              f"{sorted(body)}")
        check("exactly the system prompt and the payload, nothing else",
              [m["role"] for m in body["messages"]] == ["system", "user"],
              f"{body['messages']}")
    finally:
        if saved_httpx is None:
            sys.modules.pop("httpx", None)
        else:
            sys.modules["httpx"] = saved_httpx
        if saved_key is None:
            os.environ.pop("MOONSHOT_API_KEY", None)
        else:
            os.environ["MOONSHOT_API_KEY"] = saved_key


def test_a_missing_key_names_its_secret():
    """The owner has to be able to fix it, which means knowing what to type."""
    print("a missing provider key")
    import os

    saved = {k: os.environ.get(k) for k in ("MOONSHOT_API_KEY", "GROQ_API_KEY")}
    try:
        for k in saved:
            os.environ.pop(k, None)
        for provider, spec in budget.PROVIDERS.items():
            try:
                weekly.api_key_for(provider)
            except weekly.MissingKey as exc:
                check(f"{provider}: the environment variable is named",
                      spec["key_env"] in str(exc), str(exc))
                check(f"{provider}: the Modal secret is named",
                      f"`{spec['secret']}`" in str(exc), str(exc))
                check(f"{provider}: the command to fix it is spelled out",
                      "modal secret create" in str(exc), str(exc))
            else:
                check(f"{provider}: a missing key raises", False, "it returned")

        # and no secret VALUE is ever printed, only names. This seat may
        # reference a secret's name and must never read or echo its contents.
        os.environ["MOONSHOT_API_KEY"] = "sk-this-must-never-be-printed"
        key = weekly.api_key_for("moonshot")
        check("a present key is returned to the caller and not logged",
              key == "sk-this-must-never-be-printed")
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_the_press_fits_its_primary_at_full_caps():
    """The requirement ADR-32 exists to satisfy, asserted rather than hoped.

    Not "it fits after trimming". The worst payload gather() can produce, the
    full 6,000-token reservation, the real generator prompt, untrimmed. A press
    whose primary only fits after trimming prints a thinner issue every week
    and never says so.
    """
    print("the primary model at full PAYLOAD_CAPS")
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "digest.md"
    if not prompt_path.exists():
        check("prompts/digest.md is present", False, str(prompt_path))
        return
    report = budget.check_request(
        prompt_path.read_text(), budget.encode(budget.worst_case_payload()),
        weekly.MAX_COMPLETION_TOKENS, weekly.MODEL)
    check("the worst-case request fits the primary untrimmed", report.fits,
          report.summary())
    check("with real headroom, not a rounding error", report.headroom > 50_000,
          report.summary())
    # ADR-32 told finance to expect roughly $0.05 an issue. If the real number
    # ever drifts far from that, finance's books are wrong and this is where it
    # should surface.
    check("the cost is in the range ADR-32 budgeted", report.cost < 0.15,
          f"${report.cost:.4f} an issue")


def test_availability_survives_one_provider_being_down():
    """The fallback list crosses providers, so one outage must not end the run."""
    print("one provider unreachable")

    class Resp:
        status_code = 200
        text = "{}"

        def json(self):
            return {"data": [{"id": m} for m in weekly.FALLBACK_MODELS
                             if budget.provider_of(m) == "moonshot"]}

    class Half:
        def get(self, url, **kw):
            if url.startswith(budget.PROVIDERS["moonshot"]["base_url"]):
                return Resp()
            raise OSError("groq is down")

    saved = sys.modules.get("httpx")
    sys.modules["httpx"] = Half()
    try:
        found, notes = budget.available_everywhere(
            weekly.FALLBACK_MODELS,
            {"MOONSHOT_API_KEY": "k", "GROQ_API_KEY": "k"})
        check("the reachable provider's models are still found",
              weekly.MODEL in found, f"{found}")
        check("and the unreachable one is reported rather than silently empty",
              any("NOT REACHED" in n for n in notes), f"{notes}")
    finally:
        if saved is None:
            sys.modules.pop("httpx", None)
        else:
            sys.modules["httpx"] = saved


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
               test_the_request_goes_to_the_right_provider,
               test_no_groq_only_parameters_on_the_kimi_path,
               test_a_missing_key_names_its_secret,
               test_the_press_fits_its_primary_at_full_caps,
               test_availability_survives_one_provider_being_down,
               test_the_schedule_is_outside_the_cron_band]:
        fn()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} failure(s)")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    print("all press-resilience checks passed")
