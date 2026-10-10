#!/usr/bin/env python3
"""How many tokens is a paper, really? Measured against real arXiv HTML.

    python3 tools/fulltext_density.py
    python3 tools/fulltext_density.py --papers 2501.12948,2412.19437
    python3 tools/fulltext_density.py --write docs/evals/YYYY-MM-DD-fulltext-token-density.json

`pipeline/budget.py` sizes every request before it is sent, and for the corpus
crons it does that against a filler string rather than against the real payload,
because the real payload lives in a database this guard cannot reach. That is
the right design and it has one failure mode: a filler that tokenizes more
cheaply than the real thing makes every estimate look better than it is.

That failure mode happened. `budget._FILLER` is clean English prose and runs
**6.17 chars/token**. A cleaned arXiv full text runs **3.65 to 4.28**, so the
guard understated distill's payload by 44% to 69% and reported the full-text
request as missing Groq's free tier by 109 tokens when it misses by roughly
1,900 (INC-2026-09-27-filler-tokenizes-cheaper-than-a-paper).

This tool is the check that closes that loop. It fetches real papers through
the same cleaning `pipeline/distill.py:fetch_fulltext` applies, counts the
result with the same tokenizer `budget.count_tokens` uses, and prints the worst
density it found. `budget.FULLTEXT_CHARS_PER_TOKEN` must stay at or below that
number, and `tests/test_fulltext_density.py` holds it against the receipt this
tool writes.

It reaches the network, so it is not a CI check. It is a thing a person runs
when `FULLTEXT_CHARS`, the cleaner, or the model's tokenizer changes, and the
receipt it writes into docs/evals/ is what CI reads instead.
"""

import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request
from datetime import date

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "pipeline"))

import budget  # noqa: E402
import read_paper  # noqa: E402

# Fourteen papers of the kind the library's corpus is made of. Chosen to span
# the formatting that changes the answer — pages of tables, pages of math,
# pages of plain prose — rather than to be representative of arXiv, because the
# number this tool exists to produce is a worst case and not an average.
#
# arxiv:2407.21783 (Llama 3) is the one that binds, at 3.35 chars/token: it
# opens with tables. The loosest is arxiv:2408.03314 at 4.93, and the spread
# between them is the reason a single hand-picked sample would not have done.
DEFAULT_PAPERS = [
    "2501.12948",   # DeepSeek-R1
    "2412.19437",   # DeepSeek-V3
    "2407.21783",   # Llama 3 — the densest of these, and the one that binds
    "2310.06825",   # Mistral 7B
    "2402.03300",   # DeepSeekMath, GRPO
    "2305.18290",   # DPO
    "2201.11903",   # chain-of-thought prompting
    "2203.02155",   # InstructGPT
    "2302.13971",   # LLaMA
    "2404.19737",   # multi-token prediction
    "2408.03314",   # test-time compute scaling
    "2312.11805",   # Gemini
    "2501.19393",   # s1, simple test-time scaling
    "2410.05229",   # GSM-Symbolic
]


def clean(raw: str) -> str | None:
    """Exactly the cleaning the pipeline applies, because it is the same function.

    This was a copy until 2026-09-27, with a docstring claiming a test held the
    two identical. That test did not exist, so the copy was free to drift from
    the thing it was measuring, which would have made the receipt describe a
    cleaner nobody runs. The cleaning now lives in `read_paper.clean_html`,
    beside this file and importable without `modal`, and both this tool and
    `pipeline/distill.py:fetch_fulltext` call it.
    """
    if len(raw) < read_paper.MIN_HTML_BYTES:
        return None
    text = read_paper.clean_html(raw)
    return text if len(text) > read_paper.MIN_TEXT_CHARS else None


def fetch(arxiv_id: str, timeout: float = 30.0) -> str | None:
    req = urllib.request.Request(
        f"https://arxiv.org/html/{arxiv_id}",
        headers={"User-Agent": "alexandria-fulltext-density/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            return None
        return clean(resp.read().decode("utf-8", "ignore"))


def measure(papers: list[str], window: int, model: str) -> dict:
    """Density of the first `window` characters of each paper, and whether the
    real request built from it fits.

    `window` is the slice distill actually sends, and measuring anything else
    answers a question nobody asks. Density is not uniform through a paper: the
    same 14 papers run 3.65 chars/token over their first 24,000 characters and
    3.35 over their first 12,000, because a paper opens with a title block,
    an author list, an abstract and a table of contents before it settles into
    prose. Measuring the generous window and sending the tight one is how a
    corrected constant was still wrong on its first attempt.

    The fit verdict is the point. A density is a summary; whether Groq accepts
    the request is the fact, and `check_request` is the same arithmetic the
    guard and CI use rather than a second copy of it.
    """
    spec = budget.CRON_REQUESTS["distill (pipeline/distill.py)"]
    # Through budget rather than off the path: the prompt carries a marker where
    # the topic vocabulary goes, and an unrendered read measures a request the
    # job never sends.
    prompt = budget.prompt_text(spec)
    reservation, _ = budget.request_reservation(spec)
    rows, failures = [], []
    for pid in papers:
        try:
            text = fetch(pid)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            failures.append({"paper": pid, "why": f"fetch failed: {exc}"})
            continue
        if not text:
            failures.append({"paper": pid, "why": "no HTML full text served"})
            continue
        body = text[:window]
        tokens = budget.count_tokens(body)
        report = budget.check_request(prompt, body, reservation, model)
        rows.append({
            "paper": f"arxiv:{pid}",
            "cleaned_chars": len(text),
            "measured_chars": len(body),
            "tokens": tokens,
            "chars_per_token": round(len(body) / tokens, 4),
            "request_tokens": report.total,
            "headroom": report.headroom,
            "fits": report.fits,
        })
    return {"papers": rows, "failures": failures}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--papers", help="comma-separated arXiv ids")
    ap.add_argument("--window", type=int, default=None,
                    help="characters to measure (default: distill's FULLTEXT_CHARS)")
    ap.add_argument("--model", default=None,
                    help="the model whose per-request limit binds "
                         "(default: the head of distill's own list)")
    ap.add_argument("--write", help="path to write the JSON receipt to")
    args = ap.parse_args()

    papers = args.papers.split(",") if args.papers else DEFAULT_PAPERS
    window = args.window or budget.request_payload_chars(
        budget.CRON_REQUESTS["distill (pipeline/distill.py)"])

    if not budget.exact():
        print("REFUSING TO MEASURE: tiktoken is not installed here, so every "
              "count below would come from the 3.0 chars/token ratio rather "
              "than from the tokenizer. A density measured with a ratio is the "
              "ratio. Run `pip install tiktoken==0.8.0` first.", file=sys.stderr)
        return 2

    # The head of distill's list, read out of the job, because the model whose
    # limit binds is the model the job actually calls first. It was hardcoded
    # to openai/gpt-oss-120b until 2026-09-30 and distill moved to kimi-k2.6
    # that day; a default that names a fallback measures the wrong ceiling.
    model = args.model or budget.distill_models()[0]
    print(f"measuring the first {window} characters of {len(papers)} papers "
          f"with o200k_base, against {model}\n")
    result = measure(papers, window, model)
    for row in result["papers"]:
        print(f"  {row['paper']:<18} {row['measured_chars']:>6} chars -> "
              f"{row['tokens']:>5} tokens  {row['chars_per_token']:.3f} c/t  "
              f"request {row['request_tokens']:>5}  headroom {row['headroom']:>6}  "
              f"{'fits' if row['fits'] else 'DOES NOT FIT'}")
    for bad in result["failures"]:
        print(f"  {bad['paper']:<18} {bad['why']}")

    if not result["papers"]:
        print("\nnothing measured, so nothing to report", file=sys.stderr)
        return 1

    worst = min(r["chars_per_token"] for r in result["papers"])
    worst_headroom = min(r["headroom"] for r in result["papers"])
    refused = [r["paper"] for r in result["papers"] if not r["fits"]]
    prose = round(window / budget.count_tokens(budget._filler(window)), 4)
    print(f"\n  worst real paper        {worst:.3f} chars/token  <- the number that binds")
    print(f"  budget._FILLER prose    {prose:.3f} chars/token")
    print(f"  the no-tokenizer ratio  {budget.FALLBACK_CHARS_PER_TOKEN:.3f} chars/token")
    print(f"  the guard assumes       {budget.FULLTEXT_CHARS_PER_TOKEN} chars/token")
    print(f"  worst real headroom     {worst_headroom}")

    stale = budget.FULLTEXT_CHARS_PER_TOKEN > worst
    if stale:
        print(f"\nSTALE: the guard assumes {budget.FULLTEXT_CHARS_PER_TOKEN} "
              f"chars/token and a real paper measured {worst}. Every distill "
              "request is being sized smaller than it is. Lower the constant "
              "in pipeline/budget.py to at most the worst number above.",
              file=sys.stderr)
    if refused:
        print(f"\nREFUSED: {len(refused)} of {len(result['papers'])} real papers "
              f"do not fit at FULLTEXT_CHARS={window}: {', '.join(refused)}. The "
              "job will send them, be refused, and fall back to the abstract "
              "while reporting success. Lower FULLTEXT_CHARS in "
              "pipeline/distill.py until this line stops printing.",
              file=sys.stderr)

    if args.write:
        # How many papers arrived WHOLE, with nothing cut at the window. This is
        # the number behind the product's "read in full", and it is the reason
        # to widen the window at all: fitting is the provider's question and
        # completeness is the reader's. Added 2026-09-30, when the window went
        # from 12,000 characters, where the answer was zero of fourteen.
        complete = sum(1 for r in result["papers"]
                       if r["cleaned_chars"] <= window)
        print(f"  arrived complete         {complete} of "
              f"{len(result['papers'])} papers, nothing cut at {window}")
        receipt = {
            "measured_on": date.today().isoformat(),
            "tokenizer": "o200k_base (tiktoken)",
            "model": model,
            "window_chars": window,
            "worst_chars_per_token": worst,
            "worst_headroom_tokens": worst_headroom,
            "papers_complete": complete,
            "papers_measured": len(result["papers"]),
            "all_fit": not refused,
            "budget_filler_chars_per_token": prose,
            "guard_constant": budget.FULLTEXT_CHARS_PER_TOKEN,
            **result,
        }
        pathlib.Path(args.write).write_text(json.dumps(receipt, indent=2) + "\n")
        print(f"\nreceipt written to {args.write}")

    return 1 if (stale or refused) else 0


if __name__ == "__main__":
    raise SystemExit(main())
