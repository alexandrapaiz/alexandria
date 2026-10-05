"""Distill: read the paper, extract claims into silver, embed them.

Production model: **kimi-k2.6 on Moonshot**, with Groq's free tier behind it as
the fallback list. Claims are embedded in-process with Qwen3-Embedding-0.6B
(pinned open weights; the embedding model must never change silently, because
all vectors must come from one model).

    python3 pipeline/budget.py                       # gate 1: does it fit
    modal run pipeline/distill.py::preflight         # gate 2: does the model exist
    modal run pipeline/distill.py::rehearse          # gate 3: one real call, no write
    modal deploy pipeline/distill.py                 # then, and only then, deploy

    modal run pipeline/distill.py::drain             # plan the drain, spend nothing
    modal run pipeline/distill.py --max-papers 5     # manual production run

The smoke run, before the schedule is trusted, is one paper for pennies:

    modal run pipeline/distill.py --max-papers 1 --cap-usd 0.15

And on the deploy that first installs this, triage goes with it, because the
standing thread list moved into `pipeline/priority.py` and both jobs import it:

    python3 pipeline/budget.py \
      && modal run pipeline/distill.py::preflight \
      && modal run pipeline/distill.py::rehearse \
      && modal run pipeline/triage.py::preflight \
      && modal run pipeline/triage.py::rehearse \
      && modal deploy pipeline/distill.py \
      && modal deploy pipeline/triage.py

## Why this file changed on 2026-09-30

The owner's directive of 2026-09-29: "the fact that we have so many papers,
only ~1 was read, and no skill was created" is the issue to fix, and reading is
the bottleneck. This job was the bottleneck's last mile. It ran on Groq's free
tier, where 8,000 tokens a minute is less than one paper, so `FULLTEXT_CHARS`
had to be 12,000 characters, `FULLTEXT_MAX_PER_RUN` had to be 15, and the
sentence the product printed above every issue, "read in full", was true of 164
papers out of 8,956.

Three things follow, and none of them is a prompt change.

**The model.** Triage and interpret moved to Moonshot's Kimi on 2026-09-26 and
this job did not, so it was the one corpus job still calling a provider
directly instead of through `pipeline/llm.py`. It goes through the shared
client now, which brings the fallback walk, the measured spend cap and the
pacing with it, and it means one file decides how this org talks to a model.

**The window.** kimi-k2.6 has a 262,144-token context, of which 222,822 is
usable after the guard's margin. `FULLTEXT_CHARS` is 250,000 characters, which
is about 98,800 tokens at the worst density the org has measured: thirteen of
the fourteen papers in docs/evals/2026-09-30-fulltext-token-density.json arrive
COMPLETE at that size, and the fourteenth is Llama 3, whose tail is appendices.
That receipt was re-measured at this window rather than reused, and measuring
it found two defects that a 12,000-character window had hidden for the life of
the guard: `budget.count_tokens` raised on any paper containing the literal
`<|endoftext|>`, and a whole paper runs 2.53 chars/token against the 3.35 the
guard assumed from a paper's first 12,000 characters. Both are fixed in
`pipeline/budget.py`.

**The order.** The reading queue first, then the owner's four standing threads,
then the day's intake. The threads were honoured by triage and not here, which
is a priority with a hole in it: triage decides which papers are worth reading
and this job decides when each one is actually read. `pipeline/priority.py` is
now the one list both jobs use.

## What one run costs, and why the caps are where they are

Measured, not assumed: `python3 pipeline/budget.py` prints the same arithmetic
and `modal run pipeline/distill.py::drain` prints it against the live queue.

    per paper, expected     $0.042   (38,069 payload tokens, the measured mean)
    per paper, ceiling      $0.103   (the whole window at the worst density)
    per run                 20 papers, $1.50, 900,000 tokens

Three ceilings, and the tightest one stops the run. `CAP_USD` is money and is
measured from the provider's own usage block. `TOKENS_PER_RUN` is Moonshot's
tier-0 daily token allowance, 1,500,000 for this account, shared with triage
and interpret: distill's share is what is left after them, with a margin. And
`MAX_PAPERS_PER_RUN` is the clock, because 3 requests a minute is one paper
every 20 seconds and the slot is 90 minutes wide. Whichever binds first, the
run stops cleanly and the next run resumes where it stopped.

**The honest limit.** Twenty papers a day read completely is what a tier-0
Moonshot account can do, and it is not what a drained triage queue will
produce. If triage starts routing more than 140 papers a week here, the next
move is a Moonshot tier upgrade, which is money and therefore the owner's call,
not this file's. `drain` says so out loud whenever the queue stops clearing
inside a week.

## The reading queue comes first (2026-09-27)

ADR-35 made reading a precondition of skill creation, and the skill seat's first
run under it read five papers and listed twelve more it needed and could not
reach, in docs/research/reading-queue.md. Nothing in the pipeline read that
file, so the request was addressed to nobody.

This job reads it now, before it looks at the day's intake.
`pipeline/reading_queue.py` parses the unchecked lines, resolves each arXiv id
against `papers`, ingests anything the corpus has never seen straight from
arXiv, and hands back rows for the front of the drain. Each id prints on its
own `reading-queue:` line with what happened to it, because the research seat
is the one who strikes the line and it strikes what the log shows.

One thing to know about it: the queue's CONTENT is baked into the image at
`modal deploy`, so a line appended this morning reaches the scheduled run
tomorrow. `modal run pipeline/distill.py` sends the working copy instead, which
is the escape hatch for a paper somebody needs today.

## What changed on 2026-09-26 and 2026-09-27 (kept, because it still holds)

`pipeline/topics.py` is the only place that decides what a topic is, it is
enforced at the one place claims are written, and the off-list rate is printed
every run. Every claim carries `prompt_sha`. `papers.fulltext_chars` records
how much of each paper was actually read, so the weekly issue's
`papers_read_in_full` counts rows rather than assuming them.
"""

import hashlib
import json
import pathlib
import time

import modal

# Kimi first, Groq's free tier behind it, in the order `pipeline/llm.py` walks.
# The order is the whole point of the 2026-09-30 change: rank 1 is a funded
# account with a 262,144-token context that can take a whole paper, and ranks 2
# to 4 are the free tier that could take 12,000 characters of one. They stay on
# the list because one provider is one point of failure and incident 24 is what
# that costs, and because a run that falls back still writes claims, from the
# abstract, and says so. Every id here is verified by `pipeline/budget.py`,
# which reads this list out of this file rather than keeping a copy of it.
MODELS = [
    "kimi-k2.6",
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
]
MODEL = MODELS[0]           # the default; whichever model answered is logged

EMBED_MODEL = "Qwen/Qwen3-Embedding-0.6B"

# 12,000 until 2026-09-30, and before that 24,000, which never fitted Groq at
# all. Both numbers were Groq's 8,000-tokens-a-minute ceiling wearing a
# paper-shaped hat. On kimi-k2.6 the binding limit is the 262,144-token context,
# 222,822 of it usable after the guard's 15% margin, and the question stops
# being "how little of a paper fits" and becomes "how much of one is worth
# paying for".
#
# 250,000 characters is the answer, chosen by measuring rather than dividing.
# Against the fourteen real papers in
# docs/evals/2026-09-30-fulltext-token-density.json:
#
#   window    papers arriving complete    expected $/paper    ceiling $/paper
#    12,000            0 of 14                 $0.008             $0.012
#   100,000            6 of 14                 $0.029             $0.041
#   250,000           13 of 14                 $0.042             $0.103
#   400,000           14 of 14                 $0.044             $0.159
#
# The expected cost stops moving after 250,000 because most papers are shorter
# than that, and only the ceiling keeps climbing. So 250,000 is where the money
# buys completeness and past it the money buys headroom nobody uses. The one
# paper still cut at this size is arxiv:2407.21783, Llama 3, at 367,520
# characters, and what is cut from it is appendices and references.
#
# `papers.fulltext_chars` records exactly how much was sent, per paper, and the
# run prints how many arrived complete. "Read in full" is a claim the product
# makes to readers, so it is counted from that column and never assumed.
FULLTEXT_CHARS = 250_000

# Every paper in the run gets its full text. There was a fetch budget here,
# `FULLTEXT_MAX_PER_RUN = 15`, and it existed because the provider could not
# afford more; on Kimi the spend cap and the token ceiling below are the honest
# forms of that limit and they are measured rather than counted. The owner's
# directive of 2026-09-29 is explicit: full text for every paper distilled,
# abstract only as the documented fallback. The fallback is still here, it is
# still logged, and it is now reached only when arXiv serves no HTML.

# The job sent no reservation until 2026-09-27, so the provider was free to
# spend the rest of the window on output and the budget guard had to assume a
# number. 2,000 is that assumption made explicit rather than a new, smaller
# guess: 1 to 5 claims with evidence and a numbered procedure measures around
# 1,500 tokens, and an under-sized reservation truncates the JSON mid-object,
# which surfaces as a json.JSONDecodeError and loses the whole paper. Lower it
# only against a measurement from `rehearse`, which prints the real usage block.
MAX_COMPLETION_TOKENS = 2000

# What one run may spend, measured from the provider's own usage block and
# never estimated. At kimi-k2.6's list price ($0.95 per million in, $4.00 per
# million out) and the measured payload sizes above, $1.50 buys about 35 papers
# at the expected cost and 14 at the ceiling. On a normal day MAX_PAPERS_PER_RUN
# stops the run first and this is the safety valve; on a day of unusually long
# papers this stops it, cleanly, and tomorrow resumes.
#
# Raising it is a change to what the org spends: `budget.check_cron_spend()`
# fails the deploy command if the corpus caps together pass
# `budget.MONTHLY_CAP_CEILING_USD`, and that number moves only with
# docs/finance/opex.md in the same commit.
CAP_USD = 1.50

# Moonshot's tier-0 daily token allowance for this account is 1,500,000 tokens
# (budget.MODELS["kimi-k2.6"]["tpd"]), and it is shared by every Kimi caller in
# the org. It binds before the money does and nothing checked it until today,
# because until today no job sent a request big enough for it to matter: one
# 250,000-character paper is about 40,000 tokens, so twenty-five papers is most
# of a day's allowance on their own.
#
#   1,500,000  the account's day
#    -225,000  15% margin, the same margin the request guard holds back
#    -330,000  triage, 70 calls at its cap x 4,713 tokens a call
#     -60,000  interpret, measured small
#   ---------
#     885,000  distill's share, which is 22 papers at the measured mean of
#              40,259 tokens a paper including the prompt and the reply
#
# 900,000 rounds that to a number a person can hold, and MAX_PAPERS_PER_RUN is
# set below it so the paper count is what normally stops the run. When this
# ceiling is the one that trips, the log says so by name, because "we ran out of
# the account's day" and "we ran out of money" want different fixes.
# `budget.check_kimi_tpd()` holds the arithmetic above against the table.
TOKENS_PER_RUN = 900_000

# The clock. Moonshot's tier-0 rate is 3 requests a minute, so one paper every
# 20 seconds, and a 40,000-token request with thinking disabled takes another
# 30 to 40 seconds to come back. Twenty papers is therefore about 20 minutes of
# calls inside a 90-minute slot, which leaves the embedding sweep the rest.
#
# It is also, and more importantly, the number that says what this pipeline can
# actually read in a day. Twenty papers a day is 140 a week. `drain` compares
# that against the live queue every time it is run and says plainly when the
# queue has outgrown it, because the next move at that point is a Moonshot tier
# upgrade and that is the owner's call rather than this file's.
MAX_PAPERS_PER_RUN = 20

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1", "sentence-transformers")
    .add_local_file("prompts/distill.md", "/root/prompts/distill.md")
    # The practices variant travels with it. A field report routed to a prompt
    # that is not in the image fails at the open(), one paper at a time, so
    # `rehearse` loads both and refuses to report success on one.
    .add_local_file("prompts/distill-practices.md",
                    "/root/prompts/distill-practices.md")
    .add_local_file("pipeline/evidence.py", "/root/evidence.py")
    # The provider table and the shared client travel with the job, so the
    # numbers CI checks are the numbers this run uses. Added 2026-09-30 with
    # the move to Kimi: this was the one corpus job still calling a provider
    # by hand.
    .add_local_file("pipeline/budget.py", "/root/budget.py")
    .add_local_file("pipeline/llm.py", "/root/llm.py")
    # The standing threads, shared with triage. One list, so the threads triage
    # promotes are the threads this job reads first.
    .add_local_file("pipeline/priority.py", "/root/priority.py")
    # The taxonomy travels with the job, so the list the tests check is the list
    # the insert enforces.
    .add_local_file("pipeline/topics.py", "/root/topics.py")
    # The reader and the queue parser travel too, so the job reads a paper the
    # same way the seats do (tools/read_paper.py) and drains the same file the
    # skill seat writes (ADR-35).
    .add_local_file("tools/read_paper.py", "/root/read_paper.py")
    .add_local_file("pipeline/reading_queue.py", "/root/reading_queue.py")
    # The queue's CONTENT is baked at deploy time, which is the one thing to
    # know about it: a line appended today reaches the cron on the next
    # `modal deploy`. A manual `modal run` sends the working copy instead, so
    # an urgent request is one command rather than a deploy.
    .add_local_file("docs/research/reading-queue.md", "/root/reading-queue.md")
)

app = modal.App("alexandria-distill", image=image)

hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)


def evidence():
    """pipeline/evidence.py, wherever this is running from.

    Modal drops it at /root/evidence.py; a local `python3 pipeline/distill.py`
    import finds it beside this file. Same trick weekly.py uses for the token
    budget, for the same reason: the rules the tests check are the rules the
    run applies.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import evidence as module

    return module


def topics():
    """pipeline/topics.py, wherever this is running from. The same two-path trick.

    The taxonomy has to be one object shared by the insert and the tests. A
    second copy of the list is how `prompts/distill.md` came to offer tags the
    database never accepted.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import topics as module

    return module


def llm():
    """pipeline/llm.py, wherever this is running from.

    The fallback walk, the measured spend cap and the pacing all live there, and
    they are shared with triage and interpret so there is one answer to "how
    does this org talk to a model". Same two-path trick as `evidence()`.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import llm as module

    return module


def priority():
    """pipeline/priority.py — the standing threads, shared with triage."""
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import priority as module

    return module


def _sibling(name: str):
    """Import a module Modal dropped at /root, or that sits beside this file.

    The same two-path trick `evidence()` and `topics()` use, once, for the two
    modules added since. `tools/read_paper.py` lands at /root/read_paper.py in
    the image and at ../tools/read_paper.py in a checkout.
    """
    import importlib
    import sys

    here = pathlib.Path(__file__).resolve().parent
    for path in ("/root", str(here), str(here.parent / "tools")):
        if path not in sys.path:
            sys.path.insert(0, path)
    return importlib.import_module(name)


def read_paper():
    """tools/read_paper.py — the one reader, shared by this job and the seats."""
    return _sibling("read_paper")


def reading_queue():
    """pipeline/reading_queue.py — the parser for docs/research/reading-queue.md."""
    return _sibling("reading_queue")


# Which prompt reads which source. `paper` is the original: an arXiv preprint or
# a Hugging Face daily pick, written to be checked. `practices` reads a field
# report, where the contribution is a mechanism somebody runs in production and
# the most valuable paragraph is the one about what broke. pipeline/evidence.py
# already decides which of the two a row is, for the grade, and routing off that
# same function means a row cannot be graded `field` and read as a paper.
PROMPTS = {
    "paper": "distill.md",
    "practices": "distill-practices.md",
}


def prompt_path(kind: str) -> pathlib.Path:
    """Where `kind`'s prompt is, in the image or in a checkout.

    Modal drops prompts at /root/prompts; a local run or a test reads the
    working copy. The same two-path trick `evidence()` and `topics()` use, for
    the same reason: the prompt the tests check has to be the prompt the run
    sends.
    """
    name = PROMPTS[kind]
    deployed = pathlib.Path("/root/prompts") / name
    try:
        if deployed.exists():
            return deployed
    except OSError:
        # /root is not readable by the CI user, and pathlib raises rather than
        # answering False. Caught rather than avoided, because the alternative is
        # deciding "am I on Modal" from an environment variable, and that answer
        # goes stale the first time the image changes.
        pass
    return pathlib.Path(__file__).resolve().parent.parent / "prompts" / name


def load_prompt(kind: str = "paper") -> tuple[str, str]:
    """One distill prompt and the first 12 hex of its sha256.

    Written onto every claim as `claims.prompt_sha`, the way triage writes it
    onto every decision and the press writes it onto every issue. Until this
    landed, the deploy state of `prompts/distill.md` was unverifiable except by
    inference from the shape of the output: the research seat's brief of
    2026-09-26 found the interpret prompt seven days stale that way, after the
    stale prompt's output had already reached readers.

    Two prompts as of 2026-09-30, so the sha now identifies which one as well as
    which version of it. That is the whole audit trail for the practices split:
    `select prompt_sha, count(*) from claims group by 1` says how much of the
    corpus was read as a paper and how much as a field report.
    """
    text = prompt_path(kind).read_text()
    return text, hashlib.sha256(text.encode()).hexdigest()[:12]


def _text_or_none(value) -> str | None:
    """A model's optional string field, or None.

    JSON from a model is not always typed and "null" arrives as often as null,
    so an absent field has four spellings. `claims.broke` being NULL is read as
    "the source reported no failure", which is a claim about the source, so it
    has to mean that and not "the model wrote the word null".
    """
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text or text.lower() in {"null", "none", "n/a", "na"}:
        return None
    return text


def has_column(conn, table: str, column: str) -> bool:
    """Whether db/schema.sql has been applied since `column` landed.

    The column ships in the same PR as the code that writes it, and the schema
    is applied by hand (`modal run pipeline/db_setup.py`). Asking the database
    rather than assuming means a deploy that lands before the schema run
    distills normally instead of failing every insert.
    """
    return conn.execute(
        """
        select 1 from information_schema.columns
        where table_name = %s and column_name = %s
        """,
        (table, column),
    ).fetchone() is not None


def has_evidence_grade(conn) -> bool:
    """Whether db/schema.sql has been applied since evidence_grade landed.

    The column ships in the same PR as the code that writes it, and the schema
    is applied by hand (`modal run pipeline/db_setup.py`). Asking the database
    rather than assuming means a deploy that lands before the schema run
    distills normally instead of failing every insert.
    """
    return conn.execute(
        """
        select 1 from information_schema.columns
        where table_name = 'claims' and column_name = 'evidence_grade'
        """
    ).fetchone() is not None


def fetch_fulltext(paper_id: str) -> str | None:
    """arXiv's HTML full text, cut to FULLTEXT_CHARS, or None for the abstract.

    The fetching and the cleaning live in `tools/read_paper.py` now, so that
    the job and the seats read a paper the same way and there is one place to
    fix when arXiv changes. What stays here is the only part that is distill's
    own: the cut to FULLTEXT_CHARS, which is a provider limit and not a fact
    about the paper. A seat running `python3 tools/read_paper.py <id>` gets the
    whole thing.
    """
    return read_paper().fetch_fulltext(paper_id, max_chars=FULLTEXT_CHARS)


def extract_claims(title: str, body: str, kind: str = "paper", *, env,
                   cap, available=None, models: list[str] | None = None
                   ) -> tuple[dict, str]:
    """One paper to one model, through the shared client. Returns (json, model).

    Everything that used to be here by hand — the fallback walk, the 429
    backoff, the JSON parse, the usage accounting — is `pipeline/llm.py` now,
    and it is the same code triage and interpret run. What stays distill's own
    is the message pair: the prompt for this KIND of source, and a user turn
    that is a title and a body.

    `cap` is passed in rather than made here on purpose. A drain loop needs one
    cap for the whole run, and a function that made its own would reset the
    allowance on every paper, which is a spend cap that cannot be reached.
    """
    client = llm()
    prompt, _ = load_prompt(kind)
    return client.ask_json(
        models or MODELS, prompt, f"title: {title}\n\ncontent: {body}", env,
        cap, max_completion=MAX_COMPLETION_TOKENS, temperature=0.2,
        available=available)


# The payload is a fixed sample carried in this file, the way triage's rehearsal
# batch is, so the gate needs no database. What must be real is its SIZE IN
# TOKENS, because the question this gate answers is whether a full paper fits.
#
# "Length" is not size. Until 2026-09-27 this was prose alone, which runs 4.19
# chars/token, so at FULLTEXT_CHARS the rehearsal sent 750 fewer tokens than the
# densest real paper and would have passed a request that Groq refuses. That is
# the same mistake as the budget guard's prose filler
# (INC-2026-09-27-filler-tokenizes-cheaper-than-a-paper), made independently, in
# the gate whose whole job is to catch it.
#
# The mix changed on 2026-09-30 and the reason is worth keeping. Density is not
# a property of papers, it is a property of the WINDOW: over their first 12,000
# characters these same fourteen papers run 3.35 chars/token, and over their
# whole body they run 2.53, because a paper opens with a title block and an
# abstract and only later reaches its equations. Five parts prose to one part
# table was slightly worse than the worst paper at the old window and would have
# been 6% LOOSER than the worst paper at this one, which is a gate that passes
# what production fails. Two parts prose, one part table and two parts LaTeX
# lands at 2.505 against the 2.535 of arxiv:2501.19393 over its full 198,125
# characters, the densest of the fourteen in
# docs/evals/2026-09-30-fulltext-token-density.json.
# `tests/test_distill_fulltext_budget.py` holds that, so the ratio cannot drift
# back toward prose, and it now compares against a receipt measured at the
# window the job actually sends.
REHEARSAL_PROSE = (
    "We introduce a two-stage procedure for aligning a reward model to human "
    "preference pairs. In the first stage the policy is trained with supervised "
    "fine-tuning on 12,400 demonstrations. In the second stage we distil the "
    "reward model into the policy with a KL penalty of 0.02, which we ablate in "
    "Table 4. On the held-out split the aligned policy reaches 71.3% pairwise "
    "win rate against the SFT baseline, measured by three annotators with "
    "Krippendorff alpha 0.81. Training used 64 A100-hours. "
)

REHEARSAL_TABLE = (
    "Table 4: ablation over KL penalty. beta 0.005 0.01 0.02 0.05 0.10 0.20 | "
    "MMLU 5-shot 66.1 68.4 71.3 70.9 69.2 64.8 | GSM8K 8-shot maj@1 74.2 78.0 "
    "82.4 81.7 79.3 71.5 | HumanEval pass@1 55.4 59.8 64.0 63.1 60.2 52.7 | "
    "MATH 4-shot 28.3 31.6 34.9 34.1 32.0 26.4 | ARC-C 25-shot 81.2 83.5 85.7 "
    "85.0 83.8 79.1 | HellaSwag 10-shot 82.0 83.9 85.2 84.8 83.6 80.3 | "
    "TruthfulQA mc2 44.7 47.2 49.8 49.1 47.5 43.0 | avg 61.8 64.6 67.6 66.9 "
    "65.1 59.7 | Delta vs. SFT +0.0 +2.8 +5.8 +5.1 +3.3 -2.1 | n=3 seeds, "
    "sigma<=0.4. "
)

# The part that only appears once a window is wide enough to reach it. Cleaned
# arXiv HTML keeps the LaTeX, and a subscripted expectation over a preference
# triple is 2.2 chars/token where the sentence around it is 4.2.
REHEARSAL_MATH = (
    "\\begin{equation} \\mathcal{L}_{\\mathrm{DPO}}(\\pi_\\theta;\\pi_{\\mathrm{ref}}) "
    "= -\\mathbb{E}_{(x,y_w,y_l)\\sim\\mathcal{D}}\\Big[\\log\\sigma\\big(\\beta\\log"
    "\\tfrac{\\pi_\\theta(y_w\\mid x)}{\\pi_{\\mathrm{ref}}(y_w\\mid x)}-\\beta\\log"
    "\\tfrac{\\pi_\\theta(y_l\\mid x)}{\\pi_{\\mathrm{ref}}(y_l\\mid x)}\\big)\\Big] "
    "\\end{equation} where $\\beta\\in[0.005,0.2]$, $\\sigma(z)=(1+e^{-z})^{-1}$, and "
    "$\\hat{r}_\\theta(x,y)=\\beta\\log\\pi_\\theta(y\\mid x)/\\pi_{\\mathrm{ref}}(y\\mid x)$. "
)

REHEARSAL_SAMPLE = (REHEARSAL_PROSE * 2 + REHEARSAL_TABLE
                    + REHEARSAL_MATH * 2)

REHEARSAL_TITLE = "A two-stage procedure for distilling reward models into policies"


@app.function(
    secrets=[modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq")],
    timeout=300,
)
def preflight() -> str:
    """Gate 2: do the models exist, and what does a paper cost? Before every deploy.

        modal run pipeline/distill.py::preflight

    `modal deploy` runs no entrypoint, so without this nothing asks the provider
    between one day's cron and the next. Incident 24 is the reason the press has
    this and it applies here unchanged: a model can be retired under a running
    schedule and the first thing that notices is a cron with nobody watching.

    It asks each provider's `/models` endpoint and prices one paper, and nothing
    else. Whether the request FITS is gate 1's question,
    `python3 pipeline/budget.py`, and whether the provider actually answers is
    gate 3's. Three gates that each ask one question can each fail for one
    reason.

    The cost lines are here because the owner's directive of 2026-09-29 asks for
    the cost per paper and the projected monthly cost, and a number printed
    where the deploy happens is a number somebody reads. It raises, so a failure
    stops the chair's `&&` chain before the deploy.
    """
    import os

    client = llm()
    guard = client.budget()
    available, notes = client.usable_models(MODELS, os.environ)
    for note in notes:
        print(f"  {note}")
    problems = [p for rank, model in enumerate(MODELS, start=1)
                for p in guard.model_problems(f"distill fallback {rank}", model,
                                              available)]
    for line in problems:
        print(f"  PROBLEM: {line}")
    usable = [m for m in MODELS if available is None or m in available]
    if not usable:
        raise client.NoModelAnswered(
            "preflight: no model in distill's list is listed by its provider "
            "for these keys, so distill cannot read a single paper. Fix "
            "pipeline/distill.py MODELS and pipeline/budget.py MODELS together.")

    print("distill preflight:")
    for line in cost_report(guard, usable[0]):
        print(f"  {line}")
    if usable[0] != MODELS[0]:
        print(f"  NOTE: {MODELS[0]} is not usable here, so the run would fall "
              f"back to {usable[0]}. That model's whole per-request budget is "
              f"smaller than one paper, so every paper would be read from its "
              "abstract and papers.fulltext_chars would be null for all of "
              "them. The run still writes claims. It does not read papers.")
    return f"preflight ok: {usable[0]} would read the paper"


#: What the expected request looks like, measured rather than guessed. The mean
#: payload across the fourteen papers in
#: docs/evals/2026-09-30-fulltext-token-density.json at FULLTEXT_CHARS, plus the
#: prompt, against a reply of the size the rehearsal actually produces. Used
#: only to PRICE a run; nothing sizes a request off it, because a request is
#: sized against the worst case and priced against the expectation.
EXPECTED_PROMPT_TOKENS = 39_059      # 38,069 payload + 990 prompt
EXPECTED_COMPLETION_TOKENS = 1_200


def cost_report(guard, model: str) -> list[str]:
    """Cost per paper and projected monthly spend. One place, three callers.

    `preflight` prints it at deploy, `drain` prints it against the live queue,
    and the daily run prints the realised version of it from the usage blocks.
    The owner asked for these two numbers by name; they are computed from
    `budget.MODELS` prices so they cannot drift from what CI projects.
    """
    expected = guard.cost_usd(EXPECTED_PROMPT_TOKENS, EXPECTED_COMPLETION_TOKENS,
                              model)
    ceiling = guard.cost_usd(
        int(FULLTEXT_CHARS / guard.FULLTEXT_CHARS_PER_TOKEN) + 990,
        MAX_COMPLETION_TOKENS, model)
    lines = [
        f"model: {model}   window: {FULLTEXT_CHARS} chars   "
        f"reservation: {MAX_COMPLETION_TOKENS}",
    ]
    if expected <= 0:
        lines.append(
            f"cost per paper: $0.00 on {model}. This model is free and the only "
            "ceiling on it is its provider's rate limit, which is why it cannot "
            "read a paper.")
        return lines
    lines += [
        f"cost per paper: ${expected:.4f} expected, ${ceiling:.4f} at the "
        "ceiling (the whole window at the worst measured density)",
        f"per run: {MAX_PAPERS_PER_RUN} papers, ${CAP_USD:.2f} cap, "
        f"{TOKENS_PER_RUN:,} tokens; the first of the three to bind stops the "
        "run and the next run resumes",
        f"projected monthly: ${expected * MAX_PAPERS_PER_RUN * 30:.2f} expected "
        f"at {MAX_PAPERS_PER_RUN} papers every day, ${CAP_USD * 30:.2f} at the "
        "cap. docs/finance/opex.md carries both.",
    ]
    return lines


@app.function(
    # Neon is deliberately absent. A rehearsal must not be able to write a claim,
    # and the strongest form of that promise is a missing credential rather than
    # a missing function call. This is the shape pipeline/triage.py::rehearse
    # established and the reason is the same.
    secrets=[modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq")],
    timeout=900,
)
def rehearse(allow_abstract_only: bool = False) -> str:
    """Gate 3: one real call on the real prompt, writing nothing.

        modal run pipeline/distill.py::rehearse
        modal run pipeline/distill.py::rehearse --allow-abstract-only

    The first two gates ask questions about the request. This one exercises the
    provider, and every one of the four failures of
    INC-2026-09-24-press-provider-migration was on this question. The prompt,
    the provider, the key, the reservation and the timeout are the real ones,
    because it calls `extract_claims` rather than reimplementing it. What is
    fake is the paper, and what is absent is the database.

    **It asks distill's own question, which no other gate asks: can this job
    read the paper it was handed?** Until 2026-09-27 the answer was no and
    nothing said so out loud: the request was refused every time, the run
    degraded to `abstract[:6000]`, and it succeeded. A job that succeeds while
    doing the lesser thing is the shape of the owner's finding of 2026-09-25,
    that the corpus is not being read: 164 papers read in full out of 8,956
    ingested. So a rehearsal that got claims out of an abstract and called
    itself green would be the same defect in a smaller box.

    It therefore raises when the full-text request does not survive, and it
    raises when a FALLBACK answered rather than the model about to be deployed,
    because a receipt from a model that cannot take a paper is not a receipt.
    `--allow-abstract-only` is the escape hatch for the day the chair is
    deploying an unrelated fix and knows the payload does not fit. The hatch
    prints what it is forgiving, so the receipt says which of the two things was
    proved.

    One rehearsal costs about $0.10 at kimi-k2.6's list price, because it sends
    a 250,000-character paper on purpose. That is the price of knowing, and the
    line below prints it rather than leaving it to be inferred from a bill.
    """
    import os

    client = llm()
    prompt, sha = load_prompt()
    # Gate 3 for the second prompt is weaker than for the first and this is the
    # honest form of it: the practices prompt is LOADED here, so a deploy whose
    # image is missing it fails the chain instead of failing on the first blog
    # post of the next run, and it is not CALLED, because the request that must
    # fit is the full paper below and one rehearsal call is the budget. What
    # this proves is that the file is in the image and its sha is the one about
    # to be deployed. What it does not prove is that the provider answers it
    # well, and the first field report of the next run is where that shows.
    practices, practices_sha = load_prompt("practices")
    taxonomy = topics()
    cap = client.Cap(CAP_USD, label="distill rehearsal")
    available, notes = client.usable_models(MODELS, os.environ)
    for note in notes:
        print(f"  {note}")

    # The worst case by construction: exactly what the daily run sends when
    # fetch_fulltext succeeds, which is the request that must fit. Its density
    # is slightly worse than the worst real paper measured, so a provider that
    # accepts this accepts them.
    body = (REHEARSAL_SAMPLE * (FULLTEXT_CHARS // len(REHEARSAL_SAMPLE) + 1))[:FULLTEXT_CHARS]

    print("distill rehearsal:")
    print(f"  model wanted: {MODELS[0]}   prompt_sha: {sha}   "
          f"payload: {len(body)} chars (FULLTEXT_CHARS)")
    print(f"  practices prompt loaded, not called: {practices_sha} "
          f"({len(practices)} chars)")

    read_in_full = True
    started = time.monotonic()
    try:
        out, model = extract_claims(REHEARSAL_TITLE, body, env=os.environ,
                                    cap=cap, available=available)
    except client.NoModelAnswered as exc:
        print(f"  the full-text request was refused by every model:\n{exc}")
        if not allow_abstract_only:
            raise RuntimeError(
                "the rehearsal's full-paper request was refused by every model "
                "in distill's list, so a deploy today installs a job that reads "
                "abstracts and reports papers. `python3 pipeline/budget.py` "
                "says this request fits, so either the prompt grew since the "
                "guard last ran, or the provider's limit moved, or the guard's "
                "measured density is stale. `python3 tools/fulltext_density.py "
                "--window 250000 --model kimi-k2.6` says which, against real "
                "papers. Lower FULLTEXT_CHARS until it stops printing REFUSED. "
                "Pass --allow-abstract-only to deploy anyway, knowingly. "
                "Nothing was deployed."
            ) from exc
        read_in_full = False
        print("  --allow-abstract-only: retrying at abstract size, as the run does")
        out, model = extract_claims(REHEARSAL_TITLE, body[:6000], env=os.environ,
                                    cap=cap, available=available)
    elapsed = time.monotonic() - started

    claims = [c for c in out.get("claims", []) if isinstance(c, dict)]
    with_text = [c for c in claims if (c.get("claim") or "").strip()]
    kept, dropped = 0, {}
    for c in claims:
        tags, off = taxonomy.normalize(c.get("topics"))
        kept += len(tags)
        for tag in off:
            dropped[tag] = dropped.get(tag, 0) + 1

    print(f"  answered by: {model}")
    print(f"  {len(claims)} claims back, {len(with_text)} with text, in {elapsed:.1f}s")
    print(f"  read in full: {read_in_full}")
    print(f"  topics: {kept} on the closed list, {sum(dropped.values())} dropped "
          f"{sorted(dropped) if dropped else ''}")
    for c in with_text[:3]:
        print(f"    - {(c.get('claim') or '')[:110]}")
        print(f"      evidence: {str(c.get('evidence'))[:90]}")
    print(f"  institutions: {out.get('institutions')}")
    print(f"  {cap.line()}")
    print("  wrote nothing: this container has no database credential")

    if not with_text:
        raise RuntimeError(
            "the rehearsal got no claim with text back. A distill run that "
            "answers with an empty claims list writes nothing and logs nothing "
            "unusual, so the paper is marked processed and never revisited. "
            "Nothing was deployed.")
    if dropped:
        raise RuntimeError(
            f"the model tagged claims with {sum(dropped.values())} topics off "
            f"the closed list ({sorted(dropped)}), which pipeline/topics.py "
            "drops. Dropped tags mean claims no query can match, which is "
            "incident 30 and the 18 invisible claims of 2026-09-26. Fix "
            "prompts/distill.md and pipeline/topics.py together. Nothing was "
            "deployed.")
    if read_in_full and model != MODELS[0]:
        raise RuntimeError(
            f"the rehearsal was answered by {model}, not by {MODELS[0]}, which "
            "is what the deploy installs. A receipt from a fallback is not a "
            "receipt: tomorrow's cron meets the head of the list first, and "
            "every model below it has a per-request budget smaller than one "
            "paper. Fix the head of the list before deploying. Nothing was "
            "deployed.")

    verdict = "in full" if read_in_full else "from an abstract only"
    return (f"rehearsal ok: {model} read {len(body)} chars {verdict} and wrote "
            f"{len(with_text)} claims at prompt {sha} in {elapsed:.1f}s for "
            f"${cap.spent:.5f}, wrote nothing")


def drain_forecast(remaining: int, per_run: int) -> str:
    """How many runs are left at this rate, and whether that is inside a week.

    The owner asked for progress, and progress is a remainder and a date rather
    than a count of what one run did. Its twin lives in `pipeline/triage.py`;
    this one adds the week, because the directive of 2026-09-29 sized this
    job's cap against clearing the queue inside one.
    """
    if per_run <= 0:
        return f"{remaining} papers still queued and this run read none"
    runs = -(-remaining // per_run)
    verdict = ("inside the week the directive asks for" if runs <= 7
               else "OVER A WEEK: see `modal run pipeline/distill.py::drain` "
                    "for what to do about it")
    return (f"{remaining} papers still queued; at {per_run} a run that is "
            f"{runs} more run{'s' if runs != 1 else ''}, {verdict}")


@app.function(
    # No model secret in this container, so it cannot call anything even by
    # mistake. Neon only: the question a plan answers is how deep the queue is.
    secrets=[modal.Secret.from_name("neon")],
    timeout=300,
)
def drain() -> str:
    """What the drain looks like from here, spending nothing. The dry run.

        modal run pipeline/distill.py::drain

    The owner's directive of 2026-09-29 asks for a per-run cap sized so the
    whole distill queue clears in a week. A constant cannot promise that: the
    queue is fed by triage and grows. So the promise is a CHECK instead, run
    against the live queue whenever anybody asks, and it says plainly when the
    queue has outgrown what a tier-0 Moonshot account can read.
    """
    import os

    import psycopg

    client = llm()
    guard = client.budget()
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        depth = conn.execute("select count(*) from distill_queue").fetchone()[0]
        threads = conn.execute(
            "select count(*) from distill_queue where title ilike any(%s)",
            (priority().PRIORITY_PATTERNS,),
        ).fetchone()[0]
        deep = conn.execute(
            "select count(*) from distill_queue where triage_decision = 'deep_read'"
        ).fetchone()[0]
        read_in_full = conn.execute(
            "select count(*) from papers where fulltext_chars is not null"
        ).fetchone()[0]

    queue = reading_queue()
    text = queue.read_file("/root/reading-queue.md") or queue.read_file(queue.QUEUE_PATH)
    waiting = len(queue.pending(text, limit=None)) if text else 0

    per_run = MAX_PAPERS_PER_RUN
    runs = -(-depth // per_run) if per_run else 0
    expected = guard.cost_usd(EXPECTED_PROMPT_TOKENS, EXPECTED_COMPLETION_TOKENS,
                              MODELS[0])
    lines = [
        f"distill queue: {depth} papers, of which {threads} are the standing "
        f"threads and {deep} are deep_read; {waiting} more in the reading queue",
        f"read in full to date: {read_in_full} papers",
    ]
    lines += cost_report(guard, MODELS[0])
    lines += [
        f"the queue clears in {runs} daily run{'s' if runs != 1 else ''} for "
        f"about ${depth * expected:.2f} in total",
    ]
    if runs > 7:
        lines.append(
            f"OVER A WEEK: {depth} papers at {per_run} a run is {runs} days, and "
            "the directive of 2026-09-29 asks for seven. Raising "
            "MAX_PAPERS_PER_RUN alone will not do it, because "
            f"{TOKENS_PER_RUN:,} tokens a run is already most of Moonshot's "
            "tier-0 daily allowance for this account. The next move is a tier "
            "upgrade, which is money, which is the owner's call. Bring this "
            "line and docs/finance/opex.md to her.")
    else:
        lines.append(
            f"inside the week the directive asks for: {runs} runs at "
            f"{per_run} papers.")
    print("\n".join(lines))
    return lines[-1]


@app.function(
    secrets=[modal.Secret.from_name("neon"), modal.Secret.from_name("moonshot"),
             modal.Secret.from_name("groq")],
    timeout=3600,
)
def bake_off(n_papers: int = 8, models: list[str] | None = None) -> list[dict]:
    """Same papers, every model, side by side, for a blind human read.

        modal run pipeline/distill.py::run_bake_off --n-papers 8

    The 2026-09-07 bake-off chose gpt-oss-120b over qwen3.8-27b, 4-1-3
    (docs/evals/2026-09-07-distill-bakeoff.json), and both of those are now
    fallbacks behind kimi-k2.6. This still reads abstracts rather than full
    text on purpose: the Groq entries cannot take a paper, and a comparison
    where one arm reads more than the other measures the window and not the
    model.
    """
    import os

    import psycopg

    client = llm()
    candidates = models or MODELS
    cap = client.Cap(CAP_USD, label="distill bake-off")
    available, notes = client.usable_models(candidates, os.environ)
    for note in notes:
        print(f"  {note}")

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        papers = conn.execute(
            """
            select id, title, abstract, url, triage_decision
            from distill_queue
            where abstract is not null and length(abstract) > 200
            order by case triage_decision when 'deep_read' then 0 else 1 end,
                     case tier when 'b' then 0 when 'c' then 1 else 2 end,
                     published_at desc nulls last
            limit %s
            """,
            (n_papers,),
        ).fetchall()

    results = []
    for pid, title, abstract, url, decision in papers:
        entry = {"paper_id": pid, "title": title, "url": url, "decision": decision}
        for model in candidates:
            try:
                out, _ = extract_claims(title, abstract[:6000], env=os.environ,
                                        cap=cap, available=available,
                                        models=[model])
                entry[model] = out.get("claims", [])
            except Exception as exc:                        # noqa: BLE001
                entry[model] = [{"claim": f"PROVIDER ERROR: {exc}",
                                 "evidence": "", "topics": []}]
            time.sleep(client.pace(model))
        results.append(entry)
        print(f"distilled on {len(candidates)} models: {title[:60]}")
    print(cap.line())
    return results


@app.function(
    # 15:00 UTC as of 2026-09-30, moved from 11:30, and the slot is load-bearing
    # rather than incidental now. Moonshot's organization concurrency is 1, so a
    # second Kimi call anywhere in the org takes a 429 and the run that meets it
    # loses its slot (failure 2 of INC-2026-09-24-press-provider-migration).
    # This slot has to miss the press (09:00-11:00, which includes the chair's
    # manual rehearsal), triage (12:00-13:00) and interpret (14:00-15:00), and
    # the 13:00-14:00 gap stays unclaimed because it is the margin.
    # `pipeline/llm.py` KIMI_WINDOWS is the table that says so and
    # `budget.check_kimi_windows()` fails CI if two windows overlap.
    #
    # The 90-minute timeout is what makes 15:00 a window rather than a moment.
    # 20 papers at 3 requests a minute is about 20 minutes of calls, and the
    # rest is the embedding sweep, which runs on this job's GPU-less container
    # and is slow on a backlog.
    #
    # Runtime change under docs/agents/runtime-changes.md: this job's provider,
    # model, schedule, timeout and caps all moved. Its three gates are in this
    # module's docstring, and the deploy does not happen until the rehearsal
    # passes.
    schedule=modal.Cron("0 15 * * *"),
    secrets=[modal.Secret.from_name("neon"),
             # ADR-32's funded account, primary here since 2026-09-30.
             modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq")],
    volumes={"/root/.cache/huggingface": hf_cache},
    timeout=5400,
)
def distill(max_papers: int = MAX_PAPERS_PER_RUN, queue_text: str | None = None,
            cap_usd: float = CAP_USD):
    """The day's drain: the reading queue, then the standing threads, then intake.

    `queue_text` is docs/research/reading-queue.md's content. The scheduled run
    leaves it None and reads the copy baked into the image; `modal run` passes
    the working copy, so a line appended this morning is read this morning
    rather than after the next deploy.
    """
    import os

    import psycopg
    from sentence_transformers import SentenceTransformer

    client = llm()
    cap = client.Cap(cap_usd, label="distill")
    available, notes = client.usable_models(MODELS, os.environ)
    for note in notes:
        print(f"  {note}")

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        # ADR-35: what the skill seat could not read comes before what the
        # firehose happened to deliver, because a queue line is a person
        # asking and the intake is a subscription.
        queue = reading_queue()
        text = queue_text
        if text is None:
            text = queue.read_file("/root/reading-queue.md") or queue.read_file(queue.QUEUE_PATH)
        if text:
            waiting = queue.pending(text, limit=None)
            requested = waiting[:queue.MAX_PER_RUN]
            print(f"reading queue: {len(waiting)} pending, {len(requested)} taken this run")
        else:
            requested = []
            print("reading queue: unreadable from here, so the day's intake only. "
                  "The file is baked into the image; check the deploy.")
        first = queue.resolve(conn, requested,
                              fetch_metadata=read_paper().fetch_metadata) if requested else []
        # Committed before a single claim is written: a paper ingested because
        # someone asked for it should stay in the corpus even if the provider
        # rate-limits this run to a stop two papers later.
        conn.commit()

        # The owner's order of 2026-09-29, in as many words: the reading queue
        # first (that is `first`, above), then the four standing threads, then
        # the rest. The threads outrank `deep_read` here and that is deliberate:
        # `deep_read` is triage's opinion about one paper and a thread is the
        # owner's standing instruction about a subject, so the standing
        # instruction wins and triage's ranking breaks the tie inside it.
        #
        # `pipeline/priority.py` owns the term list, shared with triage, because
        # the threads triage promotes and the threads this job reads first have
        # to be the same threads.
        intake = conn.execute(
            """
            select id, title, abstract, triage_decision, source
            from distill_queue
            order by case when title ilike any(%s) then 0 else 1 end,
                     case triage_decision when 'deep_read' then 0 else 1 end,
                     published_at desc nulls last
            limit %s
            """,
            (priority().PRIORITY_PATTERNS, max_papers),
        ).fetchall()
        papers = queue.merge(first, intake, max_papers)
        print(f"{len(papers)} papers to distill: {len(first)} from the reading "
              f"queue, {len(papers) - len(first)} from the day's intake")
        if not papers:
            return 0

        marking_fulltext = has_column(conn, "papers", "fulltext_chars")
        if not marking_fulltext:
            print("papers.fulltext_chars is missing, so the weekly issue cannot "
                  "say how much was read in full; run db/schema.sql")
        grading = has_evidence_grade(conn)
        # evidence() is loaded whether or not the column is there, because it now
        # does two jobs: it grades a claim, and it decides which prompt reads the
        # source. Routing must not switch off just because the grade column is
        # missing, or an un-migrated database would read every blog post with the
        # paper prompt and no log line would say so.
        router = evidence()
        grader = router if grading else None
        if not grading:
            print("claims.evidence_grade is missing; run db/schema.sql to start grading")
        keeping_broke = has_column(conn, "claims", "broke")
        if not keeping_broke:
            print("claims.broke is missing, so what a field report says went wrong "
                  "is read and then dropped; run db/schema.sql")
        stamping = has_column(conn, "claims", "prompt_sha")
        if not stamping:
            print("claims.prompt_sha is missing, so nothing records which distill "
                  "prompt wrote a claim; run db/schema.sql")
        taxonomy = topics()
        # Both prompts are loaded before the first paper, so a missing or
        # unreadable practices prompt fails the run at the top rather than on
        # whichever paper happens to be the first field report.
        shas = {kind: load_prompt(kind)[1] for kind in PROMPTS}
        print(f"prompt_sha paper {shas['paper']}, practices {shas['practices']} "
              f"({len(taxonomy.TOPICS)} topics accepted)")
        off_list: dict[str, int] = {}

        wrote_any = False
        finished: list[str] = []   # papers this run actually got through
        read_in_full = 0       # how many papers' claims actually came from one
        complete = 0           # of those, how many arrived whole rather than cut
        graded: dict[str, int] = {}
        by_kind: dict[str, int] = {}
        broke_reported = 0     # field claims that named a failure
        stopped = "the queue ran out"
        answered: dict[str, int] = {}
        for pid, title, abstract, decision, source in papers:
            # Three ceilings, and the tightest one ends the run. Each is checked
            # BEFORE the call, so the run stops AT its limit rather than one
            # paper past it, and each names itself: "we ran out of money", "we
            # ran out of the account's day" and "we ran out of papers" want
            # different fixes and a single "stopped" line would hide which.
            if not cap.allows():
                stopped = f"the ${cap_usd:.2f} spend cap"
                print(f"stopping: {cap.line()}")
                break
            drawn = cap.prompt_tokens + cap.completion_tokens
            if drawn >= TOKENS_PER_RUN:
                stopped = f"the {TOKENS_PER_RUN:,}-token daily share"
                print(f"stopping: {drawn:,} tokens drawn, which is this job's "
                      f"share of Moonshot's tier-0 daily allowance. Not a "
                      "failure and not a cost problem: the next run resumes.")
                break
            # A field report is read by the practices prompt. Same call, same
            # JSON contract, different questions: what they did, why, and what
            # broke. source_class is the grader's own function, so the prompt a
            # row is read with and the grade it is given can never disagree.
            kind = "practices" if router.source_class(pid, source) == "field" \
                else "paper"
            by_kind[kind] = by_kind.get(kind, 0) + 1
            # Every paper gets its full text. The fetch budget that used to sit
            # here existed because Groq could not afford more than fifteen, and
            # the owner's directive of 2026-09-29 is explicit that full text is
            # the default and the abstract is the documented fallback.
            body = fetch_fulltext(pid)
            whole = None
            if body is not None:
                # Strictly less than, so a paper that is exactly the window
                # long counts as cut. It probably was, and a number the
                # masthead rests on errs toward the smaller claim.
                whole = len(body) < FULLTEXT_CHARS
                print(f"  full text ({len(body)} chars"
                      f"{'' if whole else f', cut at {FULLTEXT_CHARS}'}): "
                      f"{title[:50]}")
            used_fulltext = body is not None
            if body is None:
                body = (abstract or "")[:6000]
            try:
                out, answered_by = extract_claims(title, body, kind,
                                                  env=os.environ, cap=cap,
                                                  available=available)
            except client.CapReached as exc:
                stopped = f"the ${cap_usd:.2f} spend cap"
                print(f"stopping: {exc}")
                break
            except client.NoModelAnswered as exc:
                if used_fulltext:
                    # No model would take the paper. The abstract is the
                    # documented fallback and the claims then came from the
                    # abstract, so this paper was NOT read in full and the
                    # marker has to say so: a stat the issue prints cannot be
                    # generous about what was read.
                    print(f"  no model took the full text; retrying with the "
                          f"abstract:\n{exc}")
                    used_fulltext, whole = False, None
                    try:
                        out, answered_by = extract_claims(
                            title, (abstract or "")[:6000], kind,
                            env=os.environ, cap=cap, available=available)
                    except client.CapReached as inner:
                        # The retry is a second call and the walk checks the
                        # cap before it sends. Caught here as well as above,
                        # because an uncaught CapReached on the retry path
                        # would end the run in a traceback instead of the
                        # clean stop the cap is for, and the papers already
                        # committed would look like a crash.
                        stopped = f"the ${cap_usd:.2f} spend cap"
                        print(f"stopping: {inner}")
                        break
                    except client.NoModelAnswered:
                        stopped = "every model refused"
                        print("stopping: no model would take the abstract "
                              "either, so this is the provider and not the "
                              "payload. The next run resumes.")
                        break
                else:
                    stopped = "every model refused"
                    print(f"stopping: no model answered:\n{exc}")
                    break
            answered[answered_by] = answered.get(answered_by, 0) + 1
            claims = out.get("claims", [])
            # The practices prompt is allowed to return nothing, and says why in
            # `skipped`. A launch post yielding zero claims is the right answer,
            # and it is also the only signal that says a feed is being routed
            # here when it should be discarded at triage, so it is printed.
            skipped_why = _text_or_none(out.get("skipped")) if not claims else None
            institutions = [i for i in (out.get("institutions") or []) if i][:3]
            if institutions:
                conn.execute(
                    "update papers set institutions = %s where id = %s",
                    (institutions, pid),
                )
            for c in claims:
                text = (c.get("claim") or "").strip()
                if not text:
                    continue
                # The taxonomy is enforced here, at the only place claims are
                # written. Tags are folded onto the closed list and anything
                # still unknown is dropped and counted, never stored: a tag that
                # no query can match is worse than no tag, because it looks like
                # coverage. pipeline/topics.py explains what the fold will and
                # will not do.
                tags, dropped = taxonomy.normalize(c.get("topics"))
                for tag in dropped:
                    off_list[tag] = off_list.get(tag, 0) + 1
                # Columns are assembled rather than branched because two optional
                # columns is four INSERTs, and the next one is eight. Every name
                # here is a literal from this file, so nothing user-supplied ever
                # reaches the statement text.
                cols = ["paper_id", "claim", "evidence", "topics", "procedure"]
                vals = [pid, text, c.get("evidence"), tags, c.get("procedure")]
                if grading:
                    row_grade = grader.grade(pid, c.get("evidence"), c.get("measured"), source)
                    graded[row_grade] = graded.get(row_grade, 0) + 1
                    cols.append("evidence_grade")
                    vals.append(row_grade)
                if keeping_broke:
                    broke = _text_or_none(c.get("broke"))
                    if broke:
                        cols.append("broke")
                        vals.append(broke)
                        broke_reported += 1
                if stamping:
                    cols.append("prompt_sha")
                    vals.append(shas[kind])
                conn.execute(
                    f"insert into claims ({', '.join(cols)}) "
                    f"values ({', '.join(['%s'] * len(cols))})",
                    tuple(vals),
                )
                wrote_any = True
            # fulltext_chars is how the weekly issue knows how much was read in
            # full. NULL means the abstract, which is the honest answer when
            # arXiv served no HTML.
            if used_fulltext:
                read_in_full += 1
                if whole:
                    complete += 1
            if marking_fulltext:
                conn.execute(
                    "update papers set distilled_at = now(), fulltext_chars = %s "
                    "where id = %s",
                    (len(body) if used_fulltext else None, pid),
                )
            else:
                conn.execute("update papers set distilled_at = now() where id = %s", (pid,))
            conn.commit()
            finished.append(pid)
            print(f"  {len(claims)} claims ({kind}) <- {title[:60]}")
            if skipped_why:
                print(f"    declined: {skipped_why}")
            # Moonshot's published rate for this account, read out of
            # budget.MODELS rather than hardcoded, so the day the account moves
            # up a tier the drain speeds up by editing the table that has to be
            # edited anyway.
            time.sleep(client.pace(answered_by))

        # The research seat strikes the queue line, and it strikes what this
        # log says was read. One line, greppable, naming the ids.
        if first:
            done = [pid for pid, *_ in first if pid in set(finished)]
            left = [pid for pid, *_ in first if pid not in set(finished)]
            if done:
                print("reading-queue: read this run, the lines for these ids can "
                      f"be struck in {queue.QUEUE_PATH}: {', '.join(done)}")
            if left:
                print("reading-queue: not reached this run, still pending: "
                      + ", ".join(left))

        # The sentence the product prints above every issue is "read in full",
        # and these are the counts behind it. `complete` is the strict reading:
        # arXiv served the whole paper and nothing was cut at FULLTEXT_CHARS.
        # `read_in_full` is the looser one the `fulltext_chars` column records.
        # Both are printed because the difference between them is exactly the
        # kind of gap the masthead has been wrong about before (ban list 60).
        print(f"read {read_in_full} of {len(finished)} papers from their full "
              f"text, {complete} of those complete with nothing cut; "
              f"{len(finished) - read_in_full} from the abstract alone")
        print(f"stopped on: {stopped}")
        print(cap.line())
        if answered:
            print("answered by: "
                  + ", ".join(f"{m} x{n}" for m, n in sorted(answered.items())))
            if MODEL not in answered:
                print(f"  NOTE: {MODEL} answered nothing this run. Every model "
                      "below it has a per-request budget smaller than one "
                      "paper, so the claims above came from abstracts.")
        if finished:
            print(f"cost per paper this run: "
                  f"${cap.spent / len(finished):.4f} measured")
        remaining = conn.execute(
            "select count(*) from distill_queue").fetchone()[0]
        print(drain_forecast(remaining, len(finished)))
        if graded:
            tally = ", ".join(f"{g} {n}" for g, n in sorted(graded.items()))
            print(f"evidence grades this run: {tally}")
        # Which prompt read what, every run. The practices split is only worth
        # having if field reports are actually reaching it, and this line is how
        # a reader of the log knows they are without querying anything.
        print("read as: " + ", ".join(f"{k} {n}" for k, n in sorted(by_kind.items())))
        if by_kind.get("practices"):
            print(f"  field reports named a failure in {broke_reported} claims. "
                  "Zero, run after run, means the practices prompt is being "
                  "answered like a paper prompt.")
        # The off-list rate, printed every run. It was 3.9% for the pipeline's
        # whole life and nobody could have known, because nothing counted it.
        if off_list:
            worst = sorted(off_list.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
            print("tags dropped as off-list: "
                  + ", ".join(f"{t!r} x{n}" for t, n in worst))
            print("  a tag dropped often is a proposal for prompts/distill.md, "
                  "which belongs to the research seat (ADR-12 whitelist)")

        # Embedding is blackboard work: sweep every unembedded claim and paper,
        # not just this run's, so any crash or missed backfill heals next run.
        pending = conn.execute(
            "select id, claim from claims where embedding is null"
        ).fetchall()
        pending_papers = conn.execute(
            """
            select id, title, coalesce(abstract, '')
            from papers where embedding is null
            order by fetched_at limit 500
            """
        ).fetchall()
        if pending or pending_papers:
            model = SentenceTransformer(EMBED_MODEL)
            hf_cache.commit()  # persist downloaded weights for future runs
        if pending:
            vectors = model.encode([t for _, t in pending], normalize_embeddings=True)
            for (claim_id, _), vec in zip(pending, vectors):
                conn.execute(
                    "update claims set embedding = %s::vector where id = %s",
                    (str(vec.tolist()), claim_id),
                )
            conn.commit()
            print(f"embedded {len(pending)} claims with {EMBED_MODEL}")
        if pending_papers:
            texts = [f"{t}\n\n{a[:2000]}" for _, t, a in pending_papers]
            vectors = model.encode(texts, normalize_embeddings=True)
            for (paper_id, _, _), vec in zip(pending_papers, vectors):
                conn.execute(
                    "update papers set embedding = %s::vector where id = %s",
                    (str(vec.tolist()), paper_id),
                )
            conn.commit()
            print(f"embedded {len(pending_papers)} papers with {EMBED_MODEL}")
        return len(pending)


@app.local_entrypoint()
def main(max_papers: int = MAX_PAPERS_PER_RUN,
         queue: str = "docs/research/reading-queue.md",
         cap_usd: float = CAP_USD):
    """A manual run sends the working copy of the reading queue, not the baked one.

        modal run pipeline/distill.py --max-papers 8
        modal run pipeline/distill.py --queue /dev/null     # the intake alone
        modal run pipeline/distill.py --max-papers 1 --cap-usd 0.15   # smoke run
    """
    text = pathlib.Path(queue).read_text() if pathlib.Path(queue).exists() else None
    if text is None:
        print(f"no reading queue at {queue}; the run will use the image's copy")
    print(f"claims embedded: "
          f"{distill.remote(max_papers, queue_text=text, cap_usd=cap_usd)}")


@app.local_entrypoint()
def run_bake_off(n_papers: int = 8):
    results = bake_off.remote(n_papers)
    with open("bakeoff_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote bakeoff_results.json with {len(results)} papers")
