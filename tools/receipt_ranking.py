#!/usr/bin/env python3
"""Which trigger-test bundle counts as the library's result. One rule, one
implementation, every Python reader calling it.

    python3 tools/receipt_ranking.py                 # the ranking, and any tie in it
    python3 tools/receipt_ranking.py --check         # fail if a tie decides a receipt

## Why this file exists rather than a third copy of the rule

`docs/agents/incidents/inbox/INC-2026-10-27-three-same-day-receipt-bundles-lost-one-tie-and-the-two-readers-break-it-opposite-ways.md`
records this defect on six consecutive days, says in its own words that the
repair is "one tie-break function that the gate, the panel and the page all
call, on a timestamp rather than a date", and registers that duty to the
engineer seat. It was owed for thirteen days. This is it.

Three readers had three rules, and none of them was recency.

- `skills/_validation/trigger_test.py` ranked on `generated` descending with a
  pre-registration tie-break, over `sorted(glob())`, with a stable sort. On a
  tie it kept the alphabetically **first** name.
- `tools/panel_validator.py` took `sorted(glob(), reverse=True)` and never read
  `generated` at all, so it kept the alphabetically **last** name, and it
  decided which engines to ignore by looking for `experiment` or `retired` in
  the filename rather than by reading `policy.pre_registered`.
- `site/lib/skill-provenance.js` ranked like the gate but over `readdirSync`,
  which Node does not promise is sorted, so its tie-break was the filesystem's.

So a filename chosen to make the gate pass was a filename chosen to make the
panel quote the other bundle. The incident puts it exactly: "there is no
filename that satisfies both." That is why the mitigation for six days was
moving the losing bundles into `results/superseded/` rather than naming them
better, and why the page could publish one result while the panel published
another.

## The rule

Newest first, by `generated` compared as a plain string. Then the
pre-registered policy, because an experimental engine's run measures the engine
rather than judging the skill. Then the file's basename, ascending.

`generated` as a string and not a parsed date is deliberate, and it is what
makes a re-run able to win: a full ISO-8601 stamp sorts above a bare date of
the same day, because the bare date is a prefix of it. A seat that re-runs the
trigger test on a day that already has a bundle writes a stamp, and the tie it
used to lose is gone.

The third key is arbitrary and it is declared anyway. Nothing inside a
bare-dated bundle says which of two ran later, so there is no fact here to get
right, and ascending is chosen only because it preserves the answer the gate's
incidental order already gave. What declaring it buys is that three readers
give one answer. `tied_with()` is how a caller finds out that the answer it got
was the arbitrary one, so an unknowable ordering can be reported instead of
published as a measurement.

The JavaScript mirror is `rankBundles()` in `site/lib/skill-provenance.js`, and
the two are executed against one fixture from opposite input orders by
`tests/test_skill_receipts.py`. That test exists because a comment claiming two
files implement one rule is the thing that stops anyone checking: both of these
carried that comment while disagreeing.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

#: An engine whose policy was not pre-registered is a measurement of the
#: engine. The gate and the page both read this field; the panel used to infer
#: it from the filename.
def pre_registered(bundle: dict) -> bool:
    return bool((bundle.get("policy") or {}).get("pre_registered"))


def source_name(bundle: dict) -> str:
    """The bundle's own filename, which is the third ranking key.

    Read from `source_file` or from `_path`, because the three readers each
    attach it under their own name and the basename is the only spelling all of
    them can compare. The page holds a filename from `readdirSync` and this
    side holds a path from `glob`, so comparing paths would be one more
    coincidence that holds only while every bundle sits in one directory.
    """
    for key in ("source_file", "_path"):
        value = bundle.get(key)
        if isinstance(value, str) and value:
            return os.path.basename(value)
    return ""


class _Descending:
    """Descending order on a string key without reversing the whole sort, so
    the keys beneath it still read ascending."""

    __slots__ = ("s",)

    def __init__(self, s: str) -> None:
        self.s = s

    def __lt__(self, other: "_Descending") -> bool:
        return self.s > other.s

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _Descending) and self.s == other.s


def rank(bundles: list[dict]) -> list[dict]:
    """The ranking. Bundles with no string `generated` are dropped, because a
    bundle that cannot say when it was produced cannot be the newest."""
    usable = [b for b in bundles if isinstance(b.get("generated"), str)]
    return sorted(
        usable,
        key=lambda b: (
            _Descending(b["generated"]),
            0 if pre_registered(b) else 1,
            source_name(b),
        ),
    )


def tied_with(bundle: dict, bundles: list[dict]) -> list[dict]:
    """The other bundles that rank exactly equal to this one: same `generated`
    string, same pre-registration.

    A non-empty answer means `rank()` put this bundle first on the basename
    alone, so a caller about to publish it as the newest result is publishing
    one of several that are equally new. A tie that decides nothing is
    harmless. A tie that decides a published receipt is a coin flip shown to a
    reader as a measurement, which is the half worth failing on.
    """
    key = (bundle.get("generated"), pre_registered(bundle))
    return [
        b for b in bundles
        if b is not bundle
        and isinstance(b.get("generated"), str)
        and (b.get("generated"), pre_registered(b)) == key
    ]


def load(results_dir: str | os.PathLike) -> list[dict]:
    """Every readable bundle in a results directory, each carrying its own
    path. A bundle that will not parse is skipped rather than raised: one
    corrupt receipt must not take a gate or a page down with it."""
    out = []
    for path in sorted(glob.glob(os.path.join(str(results_dir), "*.json"))):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            data["_path"] = os.path.relpath(path)
            out.append(data)
    return out


def suite_for(bundle: dict, slug: str) -> dict | None:
    """The row in this bundle that scores one skill, or None. A suite with no
    cases in it scores nothing, so it does not count as a receipt."""
    for suite in bundle.get("suites") or []:
        if not isinstance(suite, dict):
            continue
        if suite.get("skill") == slug and suite.get("total"):
            return suite
    return None


def newest_for(bundles: list[dict], slug: str,
               pre_registered_only: bool = False) -> tuple[dict, dict, list[dict]] | None:
    """The bundle that is one skill's receipt, its suite row, and whatever
    ranked equal to it and also scores that skill.

    `pre_registered_only` is the panel's policy, which is stricter than the
    gate's: the gate ranks an experimental run below a pre-registered one and
    will still show it when it is all there is, while the panel refuses to
    treat it as evidence about the library at all. That difference is a
    judgment the panel is entitled to, so it stays a parameter here rather than
    being flattened into one answer. What is no longer a difference is how the
    two of them order the bundles they do accept.
    """
    ranked = rank(bundles)
    for bundle in ranked:
        if pre_registered_only and not pre_registered(bundle):
            continue
        suite = suite_for(bundle, slug)
        if suite is None:
            continue
        equals = [
            b for b in tied_with(bundle, ranked)
            if suite_for(b, slug) is not None
            and (not pre_registered_only or pre_registered(b))
        ]
        return bundle, suite, equals
    return None


# ------------------------------------------------------------------- the report

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--results", default="skills/_validation/results")
    ap.add_argument("--skills", default="skills")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if a tie decides any skill's receipt")
    args = ap.parse_args(argv)

    bundles = load(args.results)
    ranked = rank(bundles)
    print(f"{len(ranked)} rankable bundles of {len(bundles)} files in "
          f"{args.results}\n")
    for bundle in ranked:
        equals = tied_with(bundle, ranked)
        mark = f"  tied with {len(equals)}" if equals else ""
        print(f"  {bundle['generated']:26} "
              f"{'pre-registered' if pre_registered(bundle) else 'experiment  '} "
              f"{source_name(bundle)}{mark}")

    slugs = sorted(
        d for d in os.listdir(args.skills)
        if os.path.isdir(os.path.join(args.skills, d)) and not d.startswith("_")
    )
    coinflips = []
    print()
    for slug in slugs:
        found = newest_for(bundles, slug)
        if found is None:
            print(f"  {slug}: no bundle scores this skill")
            continue
        bundle, _suite, equals = found
        if equals:
            coinflips.append(slug)
            print(f"  TIED  {slug}: {source_name(bundle)} won on its filename "
                  f"over {', '.join(source_name(b) for b in equals)}")
        else:
            print(f"  ok    {slug}: {source_name(bundle)}")

    # The verdict, and the exit status is computed from it rather than from
    # whatever ran last. Ursa/exo's note of 2026-11-09 names that as a class
    # with four instances across two companies in one night.
    if coinflips:
        print(f"\n{len(coinflips)} of {len(slugs)} receipts were chosen by "
              f"filename rather than by recency: {', '.join(coinflips)}.")
        print("Nothing in a bare-dated bundle says which of them ran later. "
              "Give the newer one a full ISO-8601 `generated` stamp.")
        return 1 if args.check else 0
    print(f"\nno tie decides any of the {len(slugs)} published receipts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
