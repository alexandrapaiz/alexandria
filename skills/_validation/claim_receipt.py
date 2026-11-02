#!/usr/bin/env python3
"""The claim-to-section receipt, which is the provenance half a stranger reads.

ADR-13's provenance reviewer returns `unknown` on every skill in this library,
and the reason is the same sentence nine times: "Nothing in the file says which
claim supports which section, so whether a cited claim supports the sentence
citing it is not decidable from this document." That is true of `SKILL.md` alone
and it is not true of the skill's directory. `evals/evals.json` already carries,
per task, a `sections` list naming the exact `##` headings a task exercises and a
`source.claims` list naming the claim ids behind it. Join the two and most of the
mapping is already written down, by this seat, with no database involved.

So this is a reader rather than a new claim. It joins what the files hold, reports
what they do not, and never infers a placement: a claim id that no task places and
no body sentence names is reported as orphaned, because guessing which section
owns it would be the launder the provenance reviewer exists to catch.

    python3 skills/_validation/claim_receipt.py            # the table
    python3 skills/_validation/claim_receipt.py --json
    python3 skills/_validation/claim_receipt.py --check     # exit 1 on a stale section ref

`--check` fails on the one thing a join can be wrong about: a task naming a
section heading the skill no longer carries, which is what a length retrofit
produces if it moves a heading and leaves the suite behind.
"""
import argparse
import contextlib
import glob
import json
import pathlib
import re
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from earned_pass import verdict                              # noqa: E402

# "claim 200", "claims 1652, 1653", "C476". The body of two skills already cites
# this way inline, which is the finest-grained receipt in the library, so an
# inline mention counts as a placement even when no eval task carries the id.
INLINE = re.compile(r"(?:claims?|C)\s*#?(\d{2,5})")


def read_skill(slug: str) -> dict:
    raw = pathlib.Path(f"skills/{slug}/SKILL.md").read_text()
    _, front, body = raw.split("---", 2)
    meta = yaml.safe_load(front)
    prov = meta.get("provenance") or {}
    sections = re.findall(r"^## (.+)$", body, re.M)
    spec = json.loads(pathlib.Path(f"skills/{slug}/evals/evals.json").read_text())

    by_claim: dict[int, set[str]] = {}
    stale: dict[str, list[str]] = {}
    # A length retrofit cuts a section and keeps its task under `retired_tasks`
    # so the seat picking the finding up can lift it rather than rewrite it. The
    # ids on that task are therefore placed, to a heading this file deliberately
    # no longer carries, which is a different answer from orphaned and the one
    # `recursive-harness-self-improvement`'s own provenance entry said was not
    # derivable from the file. It is derivable, from the suite beside it.
    retired: dict[int, set[str]] = {}
    # The denominator this file's `--check` is a verdict over: every (task,
    # heading) pair it compared against the skill's own headings. Zero of them
    # is what `earned_pass.py` refuses, because a suite with no tasks cannot
    # name a heading wrongly and that is not the same as naming them all right.
    section_refs = 0
    for task in spec.get("retired_tasks") or []:
        label = ", ".join(task.get("sections") or []) or f"cut with {task['id']}"
        for cid in (task.get("source") or {}).get("claims") or []:
            retired.setdefault(cid, set()).add(label)
    for task in spec.get("tasks") or []:
        named = task.get("sections") or []
        section_refs += len(named)
        for section in named:
            if section not in sections:
                stale.setdefault(task["id"], []).append(section)
        for cid in (task.get("source") or {}).get("claims") or []:
            for section in named:
                by_claim.setdefault(cid, set()).add(section)

    inline = {int(n) for n in INLINE.findall(body)}
    cited = list(dict.fromkeys(prov.get("claims") or []))
    return {
        "skill": slug,
        "status": meta.get("status"),
        "version": meta.get("version"),
        "sections": sections,
        "papers": len(prov.get("papers") or []),
        "cited": cited,
        "by_eval": {c: sorted(by_claim[c]) for c in cited if c in by_claim},
        "by_body": sorted(c for c in cited if c in inline),
        "by_retired": {c: sorted(retired[c]) for c in cited
                       if c in retired and c not in by_claim
                       and c not in inline},
        "orphaned": [c for c in cited if c not in by_claim
                     and c not in inline and c not in retired],
        "stale_section_refs": stale,
        "section_refs": section_refs,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any eval task names a heading the skill "
                         "no longer carries")
    args = ap.parse_args()

    rows = [read_skill(p.split("/")[1])
            for p in sorted(glob.glob("skills/*/SKILL.md"))]
    refs = sum(r["section_refs"] for r in rows)
    stale = {r["skill"]: r["stale_section_refs"]
             for r in rows if r["stale_section_refs"]}

    # `--json` used to return here, so `--check --json` printed the bundle and
    # exited 0 on a defect that `--check` alone exits 1 on. That is the
    # engineer's own 2026-11-02 defect in this file: a verdict discarded by how
    # the tool was invoked. The bundle keeps stdout to itself and the verdict
    # goes to stderr, so both readers get what they came for.
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        if not args.check:
            return 0
        with contextlib.redirect_stdout(sys.stderr):
            return verdict(
                "claim-to-section receipt", checked=refs,
                unit="eval-task section references", failures=len(stale),
                pass_line="No eval task names a heading its skill no longer "
                          f"carries, over {refs} section references.",
                fail_line=f"{len(stale)} skills name a heading they no longer "
                          "carry: " + ", ".join(sorted(stale)) + ".")

    cited = placed = 0
    width = max(len(r["skill"]) for r in rows)
    print("claim-to-section receipt, joined from SKILL.md and evals/evals.json\n")
    for r in rows:
        n = len(r["cited"])
        p = n - len(r["orphaned"])
        cited += n
        placed += p
        bits = []
        if r["by_retired"]:
            bits.append(f"{len(r['by_retired'])} to a cut section")
        if r["orphaned"]:
            bits.append(f"orphaned {r['orphaned']}")
        note = ("  " + ", ".join(bits)) if bits else ""
        print(f"  {r['skill']:<{width}}  {p:>3} of {n:<3} placed   "
              f"{len(r['sections'])} sections, {r['papers']} papers{note}")
    retired_n = sum(len(r["by_retired"]) for r in rows)
    print(f"\n{placed} of {cited} cited claim ids are placeable to a named "
          f"section from the files alone, with no database.")
    if retired_n:
        print(f"{retired_n} of those place to a section the skill no longer "
              "carries, read off the task kept under `retired_tasks`.")
    orphans = sum(len(r["orphaned"]) for r in rows)
    if orphans:
        print(f"{orphans} are listed in frontmatter and placed nowhere. Placing "
              "one needs the claim row, so it is reported rather than guessed.")

    if stale:
        print("\nstale section references, which a heading rename produces:")
        for slug, tasks in stale.items():
            for task, sections in tasks.items():
                print(f"  {slug}/{task} names {sections!r}, "
                      "which the skill no longer carries")
    code = verdict(
        "claim-to-section receipt", checked=refs,
        unit="eval-task section references", failures=len(stale),
        pass_line="No eval task names a heading its skill no longer carries, "
                  f"over {refs} section references.",
        fail_line=f"{len(stale)} skills name a heading they no longer carry.")
    # Without `--check` this file is a reader, so a stale ref is printed above
    # and the exit stays 0. A denominator of zero is refused either way: it
    # means this reader read nothing, which no caller asked for.
    if not args.check and code == 1:
        return 0
    return code


if __name__ == "__main__":
    sys.exit(main())
