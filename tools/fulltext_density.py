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
import html as htmllib
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pipeline"))

import budget  # noqa: E402

# Five papers the library's own corpus is made of: two reasoning-model releases,
# two frontier model cards, one small dense model. Chosen to span the formatting
# that changes the answer — heavy tables, heavy math, plain prose — rather than
# to be representative of arXiv, because the number this tool exists to produce
# is a worst case and not an average.
DEFAULT_PAPERS = [
    "2501.12948",   # DeepSeek-R1
    "2412.19437",   # DeepSeek-V3
    "2407.21783",   # Llama 3
    "2310.06825",   # Mistral 7B
    "2402.03300",   # DeepSeekMath / GRPO
]


def clean(raw: str) -> str | None:
    """Exactly `pipeline/distill.py:fetch_fulltext`'s cleaning, and nothing else.

    Copied rather than imported on purpose: importing distill.py pulls in
    `modal`, which this tool has no reason to need. `tests/test_fulltext_density.py`
    holds the two implementations identical, so the copy cannot drift.
    """
    if len(raw) < 5000:
        return None
    text = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", raw)
    text = re.sub(r"<[^>]+>", " ", text)
    text = htmllib.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) > 2000 else None


def fetch(arxiv_id: str, timeout: float = 30.0) -> str | None:
    req = urllib.request.Request(
        f"https://arxiv.org/html/{arxiv_id}",
        headers={"User-Agent": "alexandria-fulltext-density/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            return None
        return clean(resp.read().decode("utf-8", "ignore"))


def measure(papers: list[str], window: int) -> dict:
    """Density of the first `window` characters of each paper, which is the slice
    distill actually sends. Density is not uniform through a paper — the
    references section is far denser than the introduction — so measuring the
    whole file would answer a question nobody asks."""
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
        rows.append({
            "paper": f"arxiv:{pid}",
            "cleaned_chars": len(text),
            "measured_chars": len(body),
            "tokens": tokens,
            "chars_per_token": round(len(body) / tokens, 4),
        })
    return {"papers": rows, "failures": failures}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--papers", help="comma-separated arXiv ids")
    ap.add_argument("--window", type=int, default=None,
                    help="characters to measure (default: distill's FULLTEXT_CHARS)")
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

    print(f"measuring the first {window} characters of {len(papers)} papers "
          f"with o200k_base\n")
    result = measure(papers, window)
    for row in result["papers"]:
        print(f"  {row['paper']:<20} {row['measured_chars']:>6} chars -> "
              f"{row['tokens']:>5} tokens   {row['chars_per_token']:.3f} chars/token")
    for bad in result["failures"]:
        print(f"  {bad['paper']:<20} {bad['why']}")

    if not result["papers"]:
        print("\nnothing measured, so nothing to report", file=sys.stderr)
        return 1

    worst = min(r["chars_per_token"] for r in result["papers"])
    filler = budget.FALLBACK_CHARS_PER_TOKEN
    prose = round(window / budget.count_tokens(budget._filler(window)), 4)
    print(f"\n  worst real paper        {worst:.3f} chars/token  <- the number that binds")
    print(f"  budget._FILLER prose    {prose:.3f} chars/token")
    print(f"  the no-tokenizer ratio  {filler:.3f} chars/token")
    print(f"  budget.FULLTEXT_CHARS_PER_TOKEN is {budget.FULLTEXT_CHARS_PER_TOKEN}")

    if budget.FULLTEXT_CHARS_PER_TOKEN > worst:
        print(f"\nSTALE: the guard assumes {budget.FULLTEXT_CHARS_PER_TOKEN} "
              f"chars/token and a real paper measured {worst}. Every distill "
              "request is being sized smaller than it is. Lower the constant "
              "in pipeline/budget.py to at most the worst number above.",
              file=sys.stderr)

    if args.write:
        receipt = {
            "measured_on": date.today().isoformat(),
            "tokenizer": "o200k_base (tiktoken)",
            "window_chars": window,
            "worst_chars_per_token": worst,
            "budget_filler_chars_per_token": prose,
            "guard_constant": budget.FULLTEXT_CHARS_PER_TOKEN,
            **result,
        }
        pathlib.Path(args.write).write_text(json.dumps(receipt, indent=2) + "\n")
        print(f"\nreceipt written to {args.write}")

    return 0 if budget.FULLTEXT_CHARS_PER_TOKEN <= worst else 1


if __name__ == "__main__":
    raise SystemExit(main())
