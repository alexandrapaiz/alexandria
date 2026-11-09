#!/usr/bin/env python3
"""The grade distribution restated in a sentence, checked against the frontmatter.

The engineer seat's `check_status_tables` connects a table cell to a `status:`
field and finds its tables by shape rather than by path. The same facts are
also written as prose, and prose is invisible to it. `skills/README.md` says
"**No skill carries `status: active`.** Nine carry `status: provisional` and
`agent-approval-paths` carries `status: draft`", and every clause of that is a
claim about frontmatter that no gate reaches. Eight `SKILL.md` files make the
same kind of claim about themselves, in the form "`status: provisional` says
exactly that".

That page is this seat's surface and the table gate is not. So this is the
prose half, scoped to the tree this seat may write, and the engineer's entry
`docs/ideas/inbox/2026-11-09-a-prose-sentence-restates-the-grade-distribution-and-no-gate-reaches-it.md`
is the proposal it implements.

Nothing here parses English. Four things make the pattern tractable and all
four are properties of this library rather than of prose:

1. the grade vocabulary is closed, three words, and written in backticks,
2. the skill names are enumerable from `skills/`,
3. a count is a number word from a closed list or a digit,
4. the subject of an unqualified claim inside `skills/<slug>/SKILL.md` is that
   slug, so the commonest form in the library needs no subject detection.

Four claim classes fail, and they are the prose images of the three the table
gate already fails plus the self-claim the table form cannot express:

- `count`      a number and a grade: "Nine carry `status: provisional`"
- `negative`   a zero quantifier and a grade: "No skill carries `status: active`"
- `named`      a backticked skill directory and a grade
- `self`       a grade inside `skills/<slug>/SKILL.md` naming no other subject

Three classes are read, reported and never failed, and the count of each is
printed so the reach stays visible rather than implied:

- `dated`      the sentence or its filename carries an ISO date. A reading of
               the library on a day is right when it is stale, which is the
               exemption the table gate already grants a dated caption. It
               earns its keep immediately here: nine sentences in the library
               say a skill "replaced `status: active` on 2026-10-26", and
               without the exemption every one of them reads as a claim that
               the skill carries `active` today.
- `size`       "<number> skills", a claim about the library's size rather than
               its grades. Out of reach on purpose: "two skills,
               `evaluation-integrity` and ..." is the same shape as "Ten
               skills as of 2026-11-09" and means something else, and a false
               positive on reader-facing prose costs a seat a debugging
               session it cannot afford. The one such claim in the library is
               dated and exempt anyway.
- `unread`     a grade in a sentence with no subject this tool can resolve.

    python3 skills/_validation/prose_distribution.py            # the reach report
    python3 skills/_validation/prose_distribution.py --check    # exit 1 on a disagreement
    python3 skills/_validation/prose_distribution.py --self-test

`--check` exits non-zero, because a check that prints the number and passes is
documentation (standards/lessons.md L-A114). `--self-test` is the evidence it
can fail: it copies the tree, breaks it one way at a time, and asserts the
exit code moves. What this seat cannot do is add the command to a chain that
runs, because every such chain is a hand list of `tests/test_*.py` files in
`.github/workflows/checks.yml`, and both are outside this seat's write
surface. Until the engineer wires it, this gate is enforced at the reliability
of reading and L-A22 says to write that down rather than imply otherwise.
"""

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

SKILLS = pathlib.Path(__file__).resolve().parents[1]
GRADES = ("draft", "provisional", "active")
CHECKED = ("count", "negative", "named", "named-not", "self", "self-not")

NUMBER_WORDS = {
    "no": 0, "none": 0, "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}

DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
GRADE_TOKEN = re.compile(r"`(?:status:\s*)?(" + "|".join(GRADES) + r")`")
SIZE_CLAIM = re.compile(
    r"\b(" + "|".join(NUMBER_WORDS) + r"|\d+)\s+skills?\b", re.IGNORECASE)
# The split has to survive markdown emphasis touching the stop. The library
# writes "**No skill carries `status: active`.** Nine carry ...", where the
# period is followed by two asterisks and then the space, so a plain
# look-behind leaves three grades in one unit and reads none of them.
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])(?:\*{1,2})?\s+(?!\d+\.)")
LIST_MARKER = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")

# A bare integer only counts when it stands alone. `ADR-38`, `L-A114` and
# `2026-09-30` all contain digits and none of them is a count, and the first
# version of this tool read 38 skills out of "ADR-38 adds the third word".
BARE_NUMBER = re.compile(r"(?<![\w-])(\d+)(?![\w-])")

# The engineer's entry names the shape: a number or a skill name, then "carr"
# in some inflection, then the backticked grade. The verb is what separates a
# claim from a coincidence, and the window is what keeps "every skill here is
# **unmeasured** in that word, and a `provisional` status is the honest
# reading" out of the checked set. That sentence quantifies "unmeasured" and
# not the grade, it was the first version's second false positive, and no
# tightening of the number list would have caught it.
LINKING_VERBS = ("carry", "carries", "carrying", "carried", "say", "says",
                 "read", "reads", "is", "are", "was", "were", "has", "have")
VERB_WINDOW = 60

# "It is not `active` and cannot be until a differential delta exists" is a
# true sentence in `agent-security-measurement`, and the first version read it
# as a claim that the skill carries `active`. A negation inside the window
# inverts the claim rather than disqualifying it, because the inverted form is
# still checkable and it is the form half this library uses.
NEGATIONS = ("not", "never", "cannot", "no longer", "nor", "neither")

# A comparison between two grades claims neither of them.
COMPARATIVES = ("than", "instead of", "versus", "rather")

# The subject of a count has to be skills. "No delta carries a differential
# number, and `status: provisional` says exactly that" put a zero quantifier,
# a linking verb and a grade in one sentence and meant none of it about the
# count, and it was this tool's third false positive. So a count needs the
# noun, or the number has to sit directly on the verb with the noun elided,
# which is what "Nine carry `status: provisional`" does.
SKILL_NOUN = re.compile(r"\bskills?\b", re.IGNORECASE)


def skill_dirs(root: pathlib.Path) -> dict:
    """slug -> declared grade, read from frontmatter, for every skill on disk."""
    grades = {}
    for skill in sorted(root.glob("*/SKILL.md")):
        if skill.parent.name.startswith("_"):
            continue
        declared = None
        for line in skill.read_text().splitlines():
            if line.strip() == "---" and declared is not None:
                break
            if line.startswith("status:"):
                declared = line.split(":", 1)[1].strip()
                break
        grades[skill.parent.name] = declared
    return grades


def units(text: str):
    """(first_line, sentence) over a markdown file, list items kept whole.

    A paragraph is joined before it is split, because this library wraps its
    prose and the claim "Nine carry `status: provisional` and / `agent-approval-paths`
    carries `status: draft`." spans two physical lines.
    """
    block, start = [], 0
    out = []

    def flush():
        if not block:
            return
        joined = LIST_MARKER.sub("", " ".join(line.strip() for line in block))
        for sentence in SENTENCE_SPLIT.split(joined):
            if sentence.strip():
                out.append((start, sentence.strip()))

    in_fence = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            flush()
            block, start = [], 0
            continue
        if in_fence:
            continue
        starts_item = bool(re.match(r"\s*([-*+]|\d+\.)\s", line))
        if not line.strip() or starts_item or line.startswith("#"):
            flush()
            block, start = [], 0
        if not line.strip() or line.startswith("#"):
            continue
        if not block:
            start = lineno
        block.append(line)
    flush()
    return out


def links(sentence: str, subject_end: int, grade_start: int) -> bool:
    """Is there a linking verb between the subject and the grade, close enough?

    The span is directional and bounded. Directional because "`status:
    provisional` says exactly that" puts the grade first and is the self-claim
    form, handled separately. Bounded because a verb thirty words away belongs
    to a different clause.
    """
    if grade_start < subject_end:
        return False
    span = sentence[subject_end:grade_start]
    if len(span) > VERB_WINDOW:
        return False
    return any(re.search(r"\b" + verb + r"\b", span, re.IGNORECASE)
               for verb in LINKING_VERBS)


def negated(sentence: str, grade_start: int) -> bool:
    """Does a negation sit in the grade's own clause, before it?

    The clause boundary is what makes this safe. "...is not screened, `status`
    stays `provisional`, and the skill remains..." puts a negation 32
    characters before the grade and negates "screened", and reading it as a
    denial of `provisional` was this tool's fourth false positive. A comma,
    semicolon or colon between the two ends the negation's reach.
    """
    span = sentence[max(0, grade_start - VERB_WINDOW):grade_start]
    span = re.split(r"[,;:]", span)[-1]
    return any(re.search(r"\b" + re.escape(word) + r"\b", span, re.IGNORECASE)
               for word in NEGATIONS)


def counts_skills(sentence: str, subject_end: int, grade_start: int) -> bool:
    """Is the number's subject skills, rather than something else in the clause?"""
    span = sentence[subject_end:grade_start]
    if SKILL_NOUN.search(span):
        return True
    first = span.strip().split(" ")[0].strip(",;:").lower() if span.strip() else ""
    return first in LINKING_VERBS


def resolve(path, root, sentence, slugs, match, lone_grade: bool) -> tuple:
    """(claim_class, grade, expectation) for one grade token in one sentence."""
    grade = match.group(1)
    if any(re.search(r"\b" + re.escape(word) + r"\b",
                     sentence[max(0, match.start() - VERB_WINDOW):match.start()],
                     re.IGNORECASE)
           for word in COMPARATIVES):
        # "`status: draft` ... is lower than the `provisional` the format
        # contract prescribes" compares two grades and claims neither.
        return ("unread", grade, None)

    carries = not negated(sentence, match.start())

    # a named skill, when the sentence links it to the grade
    for slug in slugs:
        at = sentence.find("`" + slug + "`")
        if at >= 0 and links(sentence, at + len(slug) + 2, match.start()):
            return ("named" if carries else "named-not", grade, [slug])

    # a number or a zero quantifier, likewise linked, and about skills
    subjects = [(m.start(), m.end(), NUMBER_WORDS[m.group(0).lower()])
                for m in re.finditer(
                    r"(?i)\b(" + "|".join(NUMBER_WORDS) + r")\b", sentence)]
    subjects += [(m.start(), m.end(), int(m.group(1)))
                 for m in BARE_NUMBER.finditer(sentence)]
    for start, end, value in sorted(subjects):
        if (links(sentence, end, match.start())
                and counts_skills(sentence, end, match.start())):
            kind = "negative" if value == 0 else "count"
            return (kind, grade, value)

    # Inside skills/<slug>/SKILL.md an unqualified grade is about that skill,
    # and only when the sentence names one grade. The subject of a self-claim
    # is implicit, and an implicit subject cannot be attached to one of two
    # grades: "`status` moved from `active` to `provisional`" is true, names
    # two grades, and reads as a claim to carry `active` under any rule that
    # would let the sentence through.
    if (lone_grade and path.name == "SKILL.md" and path.parent.parent == root
            and not any("`" + s + "`" in sentence for s in slugs)):
        return ("self" if carries else "self-not", grade, [path.parent.name])
    return ("unread", grade, None)


def classify(path: pathlib.Path, root: pathlib.Path, sentence: str, slugs) -> list:
    """Every claim one sentence makes, which is one per grade token.

    The sentence this gate exists for makes two at once: "Nine carry `status:
    provisional` and `agent-approval-paths` carries `status: draft`". A
    sentence-level classifier reads one of them or neither.
    """
    if DATE.search(sentence) or DATE.search(path.name):
        return [("dated", None, None)]
    tokens = list(GRADE_TOKEN.finditer(sentence))
    if not tokens:
        return [("size", None, None)] if SIZE_CLAIM.search(sentence) else []
    lone = len({t.group(1) for t in tokens}) == 1
    out, seen = [], set()
    for match in tokens:
        claim = resolve(path, root, sentence, slugs, match, lone)
        key = (claim[0], claim[1], tuple(claim[2]) if isinstance(claim[2], list)
               else claim[2])
        if key in seen:
            continue
        seen.add(key)
        out.append(claim)
    return out


def read(root: pathlib.Path):
    """Every grade claim in the tree, with its verdict. Returns (rows, grades)."""
    grades = skill_dirs(root)
    slugs = sorted(grades)
    counts = {g: sum(1 for v in grades.values() if v == g) for g in GRADES}
    rows = []
    for path in sorted(root.rglob("*.md")):
        for lineno, sentence in units(path.read_text()):
            for kind, grade, expect in classify(path, root, sentence, slugs):
                verdict, detail = "read", ""
                if kind in ("count", "negative"):
                    actual = counts.get(grade, 0)
                    verdict = "agrees" if actual == expect else "DISAGREES"
                    detail = f"says {expect}, disk has {actual} `{grade}`"
                elif kind in ("named", "self"):
                    wrong = [s for s in expect if grades.get(s) != grade]
                    verdict = "agrees" if not wrong else "DISAGREES"
                    detail = ", ".join(
                        f"{s} says `{grade}`, disk says `{grades.get(s)}`"
                        for s in wrong
                    ) or ", ".join(f"{s} is `{grade}`" for s in expect)
                elif kind in ("named-not", "self-not"):
                    wrong = [s for s in expect if grades.get(s) == grade]
                    verdict = "agrees" if not wrong else "DISAGREES"
                    detail = ", ".join(
                        f"{s} denies `{grade}`, disk says `{grades.get(s)}`"
                        for s in wrong
                    ) or ", ".join(f"{s} is not `{grade}`" for s in expect)
                rows.append({
                    "path": str(path.relative_to(root.parent)),
                    "line": lineno, "kind": kind, "grade": grade,
                    "verdict": verdict, "detail": detail,
                    "sentence": re.sub(r"\s+", " ", sentence)[:150],
                })
    return rows, grades


def report(root: pathlib.Path) -> int:
    rows, grades = read(root)
    checked = [r for r in rows if r["verdict"] != "read"]
    print(f"frontmatter on disk: {len(grades)} skills, " + ", ".join(
        f"{sum(1 for v in grades.values() if v == g)} `{g}`" for g in GRADES))

    print("\n--- claims this gate checks, and the ones it read and did not ---\n")
    for row in rows:
        if row["kind"] == "dated":
            continue
        mark = {"agrees": "ok", "DISAGREES": "FAIL", "read": "--"}[row["verdict"]]
        print(f"{mark:>4}  {row['kind']:<9} {row['path']}:{row['line']}")
        print(f"        {row['sentence']}")
        if row["detail"]:
            print(f"        {row['detail']}")

    # The dated class is the loudest and the least interesting one sentence at
    # a time, so it is counted per file. Reach stays visible without burying
    # the four checked classes under a results tree of dated records.
    dated = {}
    for row in rows:
        if row["kind"] == "dated":
            dated[row["path"]] = dated.get(row["path"], 0) + 1
    print("\n--- dated and therefore exempt, by file ---\n")
    for path, n in sorted(dated.items()):
        print(f"{n:>4}  {path}")
    print()
    for kind in CHECKED + ("dated", "size", "unread"):
        n = sum(1 for r in rows if r["kind"] == kind)
        gate = "checked" if kind in CHECKED else "reported"
        print(f"{n:>3}  {kind:<9} {gate}")
    bad = [r for r in rows if r["verdict"] == "DISAGREES"]
    print(f"\n{len(checked) - len(bad)} of {len(checked)} checked claims agree "
          f"with the frontmatter")
    return 1 if bad else 0


def check(root: pathlib.Path) -> int:
    rows, _ = read(root)
    bad = [r for r in rows if r["verdict"] == "DISAGREES"]
    for row in bad:
        print(f"{row['path']}:{row['line']}: {row['kind']} claim disagrees with "
              f"frontmatter: {row['detail']}")
        print(f"  {row['sentence']}")
    checked = sum(1 for r in rows if r["verdict"] != "read")
    if bad:
        print(f"\n{len(bad)} of {checked} prose claims about the grade "
              f"distribution are wrong. Fix the sentence or fix the frontmatter.")
        return 1
    print(f"{checked} prose claims about the grade distribution agree with the "
          f"frontmatter on disk")
    return 0


def self_test(root: pathlib.Path) -> int:
    """Break the tree one way at a time and assert the exit code moves."""
    def run(tree: pathlib.Path) -> int:
        return subprocess.run(
            [sys.executable, str(pathlib.Path(__file__).resolve()),
             "--check", "--root", str(tree)],
            capture_output=True, text=True).returncode

    def set_status(tree: pathlib.Path, slug: str, grade: str):
        path = tree / slug / "SKILL.md"
        text = re.sub(r"(?m)^status:.*$", f"status: {grade}", path.read_text(), count=1)
        path.write_text(text)

    def sub(tree: pathlib.Path, rel: str, old: str, new: str):
        path = tree / rel
        text = path.read_text()
        assert old in text, f"fixture missing: {old!r} in {rel}"
        path.write_text(text.replace(old, new, 1))

    mutations = [
        ("the real tree", lambda t: None, 0),
        ("a skill's grade moved out from under the README count",
         lambda t: set_status(t, "agent-containment", "active"), 1),
        ("the README's count word changed",
         lambda t: sub(t, "README.md", "Nine carry", "Eight carry"), 1),
        ("a skill carries the grade the README says none carries",
         lambda t: set_status(t, "harness-engineering", "active"), 1),
        ("the README's named claim changed",
         lambda t: sub(t, "README.md", "`agent-approval-paths` carries `status: draft`",
                       "`agent-approval-paths` carries `status: active`"), 1),
        ("a SKILL.md self-claim contradicts its own frontmatter",
         lambda t: set_status(t, "agent-containment", "draft"), 1),
        ("a new skill lands and no sentence is updated",
         lambda t: shutil.copytree(t / "agent-containment", t / "zz-new-skill"), 1),
        ("a wrong claim under a date stays exempt",
         lambda t: sub(t, "README.md", "Ten skills as of 2026-11-09",
                       "Four skills as of 2026-11-09"), 0),
        ("a wrong grade claim in a dated sentence stays exempt",
         lambda t: sub(t, "README.md", "`agent-approval-paths` carries `status: draft`",
                       "On 2026-11-09 `agent-approval-paths` carried `status: active`"), 0),
    ]

    failures = 0
    for name, mutate, want in mutations:
        with tempfile.TemporaryDirectory(prefix="prose-distribution-") as tmp:
            tree = pathlib.Path(tmp) / "skills"
            shutil.copytree(root, tree)
            mutate(tree)
            got = run(tree)
            ok = got == want
            failures += 0 if ok else 1
            print(f"{'ok  ' if ok else 'FAIL'}  exit {got}, wanted {want}: {name}")
    print(f"\n{len(mutations) - failures} of {len(mutations)} mutations behaved")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 on any prose claim that disagrees with frontmatter")
    ap.add_argument("--self-test", action="store_true",
                    help="break a copy of the tree one way at a time")
    ap.add_argument("--root", default=str(SKILLS), type=pathlib.Path,
                    help="the skills tree to read, for the self-test's copies")
    args = ap.parse_args()
    root = pathlib.Path(args.root).resolve()
    if args.self_test:
        return self_test(root)
    if args.check:
        return check(root)
    return report(root)


if __name__ == "__main__":
    sys.exit(main())
