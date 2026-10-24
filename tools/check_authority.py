#!/usr/bin/env python3
"""Answer one question about a diff: is this change the owner's to merge?

`docs/standards/pm.md` §21 (owner, 2026-10-05) moved every merge to the PM
seat of the company and to the chairs, and kept exactly four things for the
owner: a change to a seat's own authority, and anything that spends money,
opens an account or writes a secret. §22 adds that those four are also the
only things that never proceed on her silence.

Seven times this company has answered that question from a path instead of
from the diff. `prompts/` became shorthand for "the owner's", and the
shorthand outlived the rule by nineteen days
(`INC-2026-10-09-tier-c-carve-out-misread-for-four-days`,
`INC-2026-10-18-tier-c-carve-out-misread-a-sixth-time`,
`INC-2026-10-24-tier-c-was-repealed-on-2026-10-05-and-a-charter-was-held-under-it-anyway`).
The last of those is the one a path check cannot reach: a charter edit across
twelve charters, correctly identified as a charter, held anyway, and it moved
no seat's authority at all.

So this reads the changed lines.

    python3 tools/check_authority.py                  # HEAD against origin/main
    python3 tools/check_authority.py --pr 455
    python3 tools/check_authority.py --range main...HEAD
    git diff | python3 tools/check_authority.py --stdin
    python3 tools/check_authority.py --explain        # the four questions

Three verdicts, and the exit status is the gate (lessons L-A9):

    0  clear       Nothing here moves a seat's own authority, spends money,
                   opens an account or writes a secret. The PM's to merge.
    2  reserved    At least one changed line does one of the four. Hers, and
                   §22's forty-eight-hour ask is the route.
    3  undecided   The command cannot tell. It declines rather than guess,
                   names the lines a reader has to read, and fails closed.
    1  error       The command could not run. Not a verdict about the diff.

The direction is deliberate. A wrong `reserved` costs one merge of waiting.
A wrong `clear` costs an authority breach. So `undecided` exists, it is
non-zero, and it is the error this command is allowed to make.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CLEAR, RESERVED, UNDECIDED, ERROR = "clear", "reserved", "undecided", "error"
EXIT = {CLEAR: 0, ERROR: 1, RESERVED: 2, UNDECIDED: 3}
RANK = {CLEAR: 0, UNDECIDED: 1, RESERVED: 2}

NO_SECTION = "(no section)"
UNRESOLVED_SECTION = "(section could not be resolved)"

# §21's own words name what stays hers: "this section, section 10, section 19,
# the PM charter's grant". Those are the sections themselves, so a changed line
# inside one is reserved with no judgement and no exemption.
RESERVED_SECTIONS = {
    "docs/standards/pm.md": {"10", "19", "21"},
    "prompts/pm-agent.md": {"5"},
}

# ...and any heading that declares itself a grant, so a seat that gains an
# authority section tomorrow is covered without anyone editing the table above.
GRANT_HEADING = re.compile(r"\b(authority|the grant|terms of the grant|permissions?)\b", re.I)

LAW_FILE = re.compile(r"^(prompts/[^/]+\.md|docs/standards/[^/]+\.md|docs/decisions\.md)$")

# A sentence carries authority only when it does three things at once: it rules
# rather than reports, it rules an act the company controls, and its subject is
# the seat itself. All three, because a charter is mostly the first alone.
#
# The third of these is the one that does the work. Requiring a named act is
# what keeps "a final turn that may not arrive" and "never to write one" out,
# and those are the sentences a looser reading flagged on a charter edit that
# moved nothing.
PERMISSION = re.compile(
    r"\b(may not|may|must not|must|never|always|shall|cannot|can|could|"
    r"is allowed|are allowed|not allowed|do not|don't|is yours|are yours|"
    r"authority|right to|licence|license|on your own)\b",
    re.I,
)
CONTROLLED_ACT = re.compile(
    r"\b(merge|merges|merging|self-merge|push|pushes|pushing|force|"
    r"dispatch|dispatches|dispatching|deploy|deploys|deploying|"
    r"spend|spends|spending|pay|pays|paying|purchase|buy|"
    r"approve|approves|grant|grants|granted|"
    r"rotate|rotates|delete|deletes|deleting|"
    r"enable|enables|disable|disables|switch(?:es)?\s+(?:on|off)|"
    r"write[sn]?\s+(?:a\s+|the\s+)?(?:secret|token|credential)|"
    r"auto-merge|squash|rebase\s+main)\b",
    re.I,
)

# §21 reserves a change to a seat's OWN authority. A charter addresses its seat
# in the second person, so the subject of a rule inside one is checkable: a line
# that rules somebody else is not a change to this seat's authority.
OWN_SEAT = re.compile(r"\b(you|your|yours|yourself|this seat|own authority)\b", re.I)

# A secret write is an assignment of a value. A read is not a write, and every
# seat run reads secrets, so the reads are excluded by name.
SECRET_KEY = (r"[A-Za-z0-9_\-]*(?:TOKEN|SECRET|PASSWORD|PASSWD|API_KEY|APIKEY"
              r"|PRIVATE_KEY|CREDENTIAL)[A-Za-z0-9_\-]*")
SECRET_READ = re.compile(
    r"(os\.environ|getenv|environ\[|process\.env|\$\{\{\s*secrets\.|secrets\.|"
    r"modal\.Secret|from_name|Secret\.|\$\{[A-Z_]+\}|\$[A-Z_]{2,}|"
    r"\.\.\.|<[^>]+>|REDACTED|xxx+|placeholder|example|None|null|\{\{)",
    re.I,
)
SECRET_ASSIGN = re.compile(rf"\b{SECRET_KEY}\b\s*(?:=|:)\s*(?P<value>\S.*)$", re.I)
SECRET_LITERAL = re.compile(r"\b(sk-[A-Za-z0-9_\-]{12,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{12,})")
# A credential has no spaces and is long. A setting is a word. `id-token: write`
# in a workflow's permissions block is a setting, and so is every secret NAME a
# charter is allowed to mention.
CREDENTIAL_SHAPE = re.compile(r"[A-Za-z0-9_\-+/=.]{20,}")
SETTING_VALUE = re.compile(
    r"write|read|read-all|write-all|none|true|false|required|optional|str|string|"
    r"int|bool|yes|no|\d{1,6}|[A-Z][A-Z0-9_]{2,}", re.I)

# Money and accounts move only when a line does something. Prose that reports a
# cost spends nothing, which is why these two run on effectful files only. A
# bare `$1` is a shell positional and not a dollar, so an amount has to carry a
# decimal, a thousands comma or a unit.
SPEND = re.compile(
    r"\b(price_id|price_cents|amount_cents|unit_amount|monthly_price|plan_id|"
    r"checkout_session|billing_plan|seats_purchased|paid_tier|subscription_id|"
    r"stripe|polar_product)\b"
    r"|\$\s?\d[\d,]*\.\d{2}\b"
    r"|\$\s?\d{1,3}(?:,\d{3})+\b"
    r"|\$\s?\d[\d,]*\s*(?:/|\bper\b|\ba\b)\s*"
    r"(?:mo|month|yr|year|seat|run|issue|user|day|week|call)\b",
    re.I,
)
ACCOUNT = re.compile(
    r"\b(sign[_ -]?up|create[_ -]?account|new account|open an account|"
    r"customers\.create|accounts\.create|organizations\.create|createCustomer)\b",
    re.I,
)

PROSE = re.compile(r"\.(md|txt|rst)$")


@dataclass
class Finding:
    question: str          # which of the four
    verdict: str           # reserved | undecided
    path: str
    line: int
    section: str
    text: str
    because: str

    def as_dict(self) -> dict:
        return {
            "question": self.question,
            "verdict": self.verdict,
            "path": self.path,
            "line": self.line,
            "section": self.section,
            "text": self.text.strip()[:160],
            "because": self.because,
        }


@dataclass
class Line:
    kind: str              # "+", "-", " "
    old: int | None
    new: int | None
    text: str
    anchor_old: int        # nearest old-side line at or before this one

    @property
    def lineno(self) -> int:
        return self.new if self.kind == "+" else (self.old or 0)


@dataclass
class Hunk:
    path: str
    old_start: int
    new_start: int
    lines: list = field(default_factory=list)

    @property
    def changed(self) -> list:
        return [l for l in self.lines if l.kind in "+-"]

    @property
    def body(self) -> str:
        return "\n".join(l.text for l in self.changed)


# ---------------------------------------------------------------- diff reading

HUNK_HEAD = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
HEADING = re.compile(r"^(#{1,4})\s+(.*)$")
SECTION_ID = re.compile(r"^(\d+[a-z]?(?:\.\d+)?)\.\s")


def parse_diff(text: str) -> tuple[list[Hunk], list[str], list[str]]:
    """Unified diff to hunks.

    Also returns the paths this parser could not read and the paths the diff
    deletes outright. Neither becomes silence: an unreadable change cannot be
    cleared, and a deleted rule can remove an authority as surely as a new line
    can grant one.
    """
    hunks: list[Hunk] = []
    unreadable: list[str] = []
    deleted: list[str] = []
    path = None
    old_path = None
    hunk = None
    old_no = new_no = 0
    anchor = 0

    for raw in text.splitlines():
        if raw.startswith("diff --git"):
            path, old_path, hunk = None, None, None
            continue
        if raw.startswith("Binary files") or raw.startswith("GIT binary patch"):
            m = re.search(r"b/(\S+)", raw)
            unreadable.append(m.group(1) if m else (path or "(a binary file)"))
            continue
        if raw.startswith("--- "):
            target = raw[4:].strip()
            old_path = None if target == "/dev/null" else re.sub(r"^a/", "", target)
            continue
        if raw.startswith("+++ "):
            target = raw[4:].strip()
            if target == "/dev/null":
                path = None
                if old_path:
                    deleted.append(old_path)
            else:
                path = re.sub(r"^b/", "", target)
            continue
        m = HUNK_HEAD.match(raw)
        if m:
            if path is None:
                hunk = None
                continue
            old_no, new_no = int(m.group(1)), int(m.group(3))
            anchor = old_no - 1
            hunk = Hunk(path=path, old_start=old_no, new_start=new_no)
            hunks.append(hunk)
            continue
        if hunk is None:
            continue
        if raw.startswith("+"):
            hunk.lines.append(Line("+", None, new_no, raw[1:], anchor))
            new_no += 1
        elif raw.startswith("-"):
            hunk.lines.append(Line("-", old_no, None, raw[1:], old_no))
            anchor = old_no
            old_no += 1
        elif raw.startswith("\\"):
            continue
        else:
            hunk.lines.append(Line(" ", old_no, new_no, raw[1:] if raw else "", old_no))
            anchor = old_no
            old_no += 1
            new_no += 1

    return hunks, unreadable, deleted


# ---------------------------------------------------------------- the sections

_BASE_CACHE: dict[tuple[str, str | None], list] = {}


def base_sections(path: str, base: str | None) -> list:
    """(line number, section id, heading text) for every `##` heading in the
    file BEFORE this diff. Read from `base` when one is named, otherwise from
    the working tree. Empty when the file is new or absent."""
    key = (path, base)
    if key in _BASE_CACHE:
        return _BASE_CACHE[key]
    if base:
        r = subprocess.run(["git", "show", f"{base}:{path}"],
                           capture_output=True, text=True, cwd=REPO)
        content = r.stdout if r.returncode == 0 else None
    else:
        f = REPO / path
        content = f.read_text(errors="replace") if f.is_file() else None

    out = []
    if content is not None:
        for i, line in enumerate(content.splitlines(), start=1):
            m = HEADING.match(line)
            if m and len(m.group(1)) == 2:
                title = m.group(2).strip()
                sid = SECTION_ID.match(title)
                out.append((i, sid.group(1) if sid else "", title))
    _BASE_CACHE[key] = out
    return out


def _parse_heading(title: str) -> tuple[str, str]:
    sid = SECTION_ID.match(title)
    return (sid.group(1) if sid else "", title)


def section_of(hunk: Hunk, index: int, base: str | None) -> tuple[str, str]:
    """The section a changed line sits in, decided from the diff first.

    A hunk that adds its own heading carries the answer inside itself, so that
    heading wins. Otherwise the line's old-side anchor is looked up in the file
    as it was before the diff. Nothing here consults the new file's line
    numbers against a different revision's content, which is the mistake that
    would make a reserved section unfindable on a branch this checkout has not
    merged.
    """
    for i in range(index, -1, -1):
        line = hunk.lines[i]
        if line.kind == "-":
            continue
        m = HEADING.match(line.text)
        if m and len(m.group(1)) == 2:
            return _parse_heading(m.group(2).strip())

    sections = base_sections(hunk.path, base)
    if not sections:
        return ("", NO_SECTION if (REPO / hunk.path).suffix else UNRESOLVED_SECTION)

    anchor = hunk.lines[index].anchor_old
    enclosing = ("", NO_SECTION)
    for start, sid, title in sections:
        if start <= anchor:
            enclosing = (sid, title)
        else:
            break
    return enclosing


# -------------------------------------------------------------- the citations

CITE_SECTION = re.compile(r"(?:§|section\s+)(\d+[a-z]?)", re.I)
CITE_DOC = re.compile(r"\b(docs/[\w\-/]+\.md|prompts/[\w\-]+\.md|company\.yaml)\b")
CITE_INC = re.compile(r"\bINC-\d{4}-\d{2}-\d{2}-[a-z0-9\-]+")
CITE_ADR = re.compile(r"\bADR-(?:\d{4}-\d{2}-\d{2}-[a-z0-9\-]+|\d{1,3})\b")


def _read(path: Path) -> str:
    return path.read_text(errors="replace") if path.is_file() else ""


def _has_section(f: Path, sid: str) -> bool:
    return bool(re.search(rf"^#{{1,3}}\s+{re.escape(sid)}\.\s", _read(f), re.M))


def resolving_citations(hunk_body: str, own_path: str) -> list[str]:
    """Citations in this hunk that actually resolve in this tree.

    A charter line that restates a rule some other document already carries is
    derivative: it reports an authority rather than moving one. The whole weight
    of that exemption rests on the citation being real, so presence is not
    enough and every one of these is resolved against a file. That is the repair
    `INC-2026-10-23-a-voice-gates-first-firing-is-green-for-a-false-reason` asked
    for in general terms: bind the evidence to the subject rather than to its
    neighbourhood.
    """
    found: list[str] = []

    incidents = _read(REPO / "docs/agents/incidents.md")
    found += [i for i in CITE_INC.findall(hunk_body) if i in incidents]

    decisions = _read(REPO / "docs/decisions.md")
    found += [a for a in CITE_ADR.findall(hunk_body) if a in decisions]

    docs = [d for d in CITE_DOC.findall(hunk_body) if (REPO / d).is_file()]
    found += docs

    for sid in CITE_SECTION.findall(hunk_body):
        targets = [REPO / d for d in docs] or sorted((REPO / "docs/standards").glob("*.md"))
        targets.append(REPO / own_path)
        if any(_has_section(t, sid) for t in targets):
            found.append(f"§{sid}")

    return sorted(set(found))


# ---------------------------------------------------------------- the four

def is_effectful(path: str) -> bool:
    """A file that can do a thing rather than describe one. Prose reporting a
    cost spends nothing; `pipeline/`, a workflow and a roster can."""
    return not PROSE.search(path)


SUBSTANCE = re.compile(r"[A-Za-z0-9]")


def _sentences(lines: list[Line]) -> list[str]:
    """The changed text as sentences rather than as lines.

    Charters are hard-wrapped, so one changed line routinely carries a clause
    that changed beside a clause that did not, and one unchanged rule reflowed
    across a rewrite looks like a new one. A sentence is the unit a rule is
    written in, so it is the unit this compares.
    """
    prose, fenced = [], False
    for l in lines:
        stripped = l.text.strip()
        if stripped.startswith("```"):
            fenced = not fenced
            continue
        if fenced or l.text.startswith("    ") or stripped.startswith("$ "):
            continue  # a command is not a rule, and joining one makes a sentence of nothing
        prose.append(stripped)
    text = re.sub(r"[`*_]+", "", " ".join(prose))
    text = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _norm(sentence: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", sentence.lower()).strip()


def rules_that_moved(hunk: Hunk) -> list[str]:
    """Sentences this hunk really adds or really removes, with the ones that
    only moved on the page taken back out."""
    added = _sentences([l for l in hunk.lines if l.kind == "+"])
    removed = _sentences([l for l in hunk.lines if l.kind == "-"])
    added_set = {_norm(s) for s in added}
    removed_set = {_norm(s) for s in removed}
    return ([s for s in added if _norm(s) not in removed_set]
            + [s for s in removed if _norm(s) not in added_set])


def check_authority(hunk: Hunk, base: str | None) -> list[Finding]:
    path = hunk.path
    out: list[Finding] = []
    reserved_ids = RESERVED_SECTIONS.get(path, set())

    # 1. The sections §21 reserves by name, and any heading that calls itself a
    #    grant. No exemption reaches these.
    for i, line in enumerate(hunk.lines):
        if line.kind not in "+-" or not SUBSTANCE.search(line.text):
            continue
        sid, title = section_of(hunk, i, base)
        if reserved_ids and title in (NO_SECTION, UNRESOLVED_SECTION):
            out.append(Finding("authority", UNDECIDED, path, line.lineno, title, line.text,
                               f"{path} carries sections this command must place a changed line "
                               "inside, and this line's section could not be resolved"))
            continue
        if sid in reserved_ids and reserved_ids:
            out.append(Finding("authority", RESERVED, path, line.lineno, title, line.text,
                               f"the changed line sits in {path} §{sid}, which §21 names as the "
                               "owner's"))
            continue
        if LAW_FILE.match(path) and GRANT_HEADING.search(title):
            out.append(Finding("authority", RESERVED, path, line.lineno, title, line.text,
                               f"the changed line sits under a heading that declares itself a "
                               f"grant: {title!r}"))
    if out:
        return out[:1] if all(f.verdict == RESERVED for f in out) else out[:3]

    # 2. Past those sections, only a law file can move authority at all.
    if not LAW_FILE.match(path):
        return out

    # 3. A rule that really moved, and whose subject is the seat itself.
    #    Anything else in a charter rules somebody else, and §21 reserves a
    #    seat's OWN authority.
    suspects = [s for s in rules_that_moved(hunk)
                if PERMISSION.search(s) and CONTROLLED_ACT.search(s) and OWN_SEAT.search(s)]
    if not suspects:
        return out

    # 4. Derivative or originating. A hunk that cites a rule this tree really
    #    carries is restating it; one that cites nothing is speaking on its own
    #    authority, and this command does not get to guess which way that went.
    if resolving_citations(hunk.body, path):
        return out

    anchor = next((i for i, l in enumerate(hunk.lines) if l.kind in "+-"), 0)
    sid, title = section_of(hunk, anchor, base)
    return [Finding("authority", UNDECIDED, path, hunk.lines[anchor].lineno, title, suspects[0],
                    "this rule about the seat itself is added or removed here, and the hunk "
                    "cites no rule that resolves in this tree, so it may be granting rather "
                    "than restating")]


def check_secret(hunk: Hunk, base: str | None) -> list[Finding]:
    out = []
    for i, line in enumerate(hunk.lines):
        if line.kind != "+":
            continue
        if SECRET_LITERAL.search(line.text):
            sid, title = section_of(hunk, i, base)
            out.append(Finding("secret", RESERVED, hunk.path, line.lineno, title, line.text,
                               "an added line carries a credential-shaped literal"))
            continue
        m = SECRET_ASSIGN.search(line.text)
        if not m:
            continue
        value = m.group("value").strip().strip("'\",")
        if SECRET_READ.search(value):
            continue
        # The setting exemption runs AFTER the credential shape, never before
        # it. `SETTING_VALUE` is case-insensitive and its last alternative is
        # `[A-Z][A-Z0-9_]{2,}`, so it fullmatches any single word of letters,
        # digits and underscores at any length: a forty-character hex token
        # assigned to `*_API_KEY` read as a setting and cleared. That is a false
        # `clear`, which is the one error this command says it is not allowed to
        # make. Checked the other way, a long constant like
        # `READ_WRITE_ALL_THINGS_HERE` now reads reserved, and a false reserved
        # costs one merge of waiting. The cheap error is the one to keep.
        sid, title = section_of(hunk, i, base)
        if CREDENTIAL_SHAPE.fullmatch(value):
            out.append(Finding("secret", RESERVED, hunk.path, line.lineno, title, line.text,
                               "an added line assigns a credential-shaped value to a "
                               "secret-shaped name, and the value is not a read of one"))
        elif SETTING_VALUE.fullmatch(value):
            continue
        elif is_effectful(hunk.path):
            out.append(Finding("secret", UNDECIDED, hunk.path, line.lineno, title, line.text,
                               "a file that can act assigns something to a secret-shaped name, "
                               "and this command cannot tell a value from a setting"))
    return out


def check_spend_and_account(hunk: Hunk, base: str | None) -> list[Finding]:
    if not is_effectful(hunk.path):
        return []
    out = []
    for i, line in enumerate(hunk.lines):
        if line.kind != "+":
            continue
        for question, pattern, because in (
            ("spend", SPEND, "an added line in a file that can act carries a price, a plan or a "
                             "payment identifier, and this command cannot tell a configured "
                             "amount from a spent one"),
            ("account", ACCOUNT, "an added line in a file that can act opens or names an "
                                 "account, and this command cannot tell a new one from an "
                                 "existing one"),
        ):
            if pattern.search(line.text):
                sid, title = section_of(hunk, i, base)
                out.append(Finding(question, UNDECIDED, hunk.path, line.lineno, title,
                                   line.text, because))
    return out


# ---------------------------------------------------------------- the verdict

def examine(diff_text: str, base: str | None = None) -> dict:
    hunks, unreadable, deleted = parse_diff(diff_text)
    findings: list[Finding] = []

    for hunk in hunks:
        findings += check_authority(hunk, base)
        findings += check_secret(hunk, base)
        findings += check_spend_and_account(hunk, base)

    for path in unreadable:
        findings.append(Finding("authority", UNDECIDED, path, 0, "(unreadable)", "",
                                "this command cannot read the change, so it cannot answer any of "
                                "the four questions about it"))

    for path in deleted:
        if LAW_FILE.match(path):
            findings.append(Finding("authority", UNDECIDED, path, 0, "(deleted)", "",
                                    "a law file is deleted, and removing a rule can remove an "
                                    "authority as surely as adding one can grant it"))

    verdict = CLEAR
    for f in findings:
        if RANK[f.verdict] > RANK[verdict]:
            verdict = f.verdict

    return {
        "verdict": verdict,
        "exit": EXIT[verdict],
        "files": sorted({h.path for h in hunks} | set(unreadable) | set(deleted)),
        "hunks": len(hunks),
        "findings": [f.as_dict() for f in findings],
    }


# ---------------------------------------------------------------- the diff

def diff_from_pr(number: int) -> str:
    r = subprocess.run(["gh", "pr", "diff", str(number)], capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(f"gh pr diff {number} failed: {r.stderr.strip() or r.returncode}")
    return r.stdout


def diff_from_range(rev: str) -> str:
    r = subprocess.run(["git", "diff", "--no-color", rev], capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(f"git diff {rev} failed: {r.stderr.strip() or r.returncode}")
    return r.stdout


def default_range() -> str:
    for base in ("origin/main", "main"):
        r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", base],
                           capture_output=True, text=True, cwd=REPO)
        if r.returncode == 0:
            return f"{base}...HEAD"
    raise RuntimeError("no origin/main or main in this checkout: name a range with --range")


# ---------------------------------------------------------------- the report

EXPLANATION = """The four questions, which are `docs/standards/pm.md` §21's own words

  Only a change to a seat's own authority (that section, §10, §19, the PM
  charter's grant), and anything that spends money, opens an account or writes
  a secret, stays the owner's. Everything else is the PM seat's to merge,
  charters and standards and workflows included.

How this command answers them, from the diff and not from the path

  authority  A changed line inside a section §21 reserves by name, or under a
             heading that declares itself a grant, is reserved outright. Past
             those, only a law file can carry authority, only a normative line
             can, and only one whose subject is the seat itself: §21 reserves a
             seat's OWN authority, so a charter line ruling the owner or the PM
             is not one. Such a line is derivative when its hunk cites a rule
             that resolves in this tree, and undecided when it cites none.
  secret     An added line that assigns a value to a secret-shaped name, where
             the value is not a read of one. Reads are what every seat does.
  spend      A price, a plan or a payment identifier in an added line, in a file
             that can act rather than describe.
  account    An account opened or named in the same position.

What the exit status means

  0  clear       the PM's to merge
  2  reserved    the owner's, and §22's forty-eight-hour ask is the route
  3  undecided   this command declines; a reader reads the named lines
  1  error       the command could not run

Why undecided exists at all

  A wrong `reserved` costs one merge of waiting. A wrong `clear` costs an
  authority breach. Both non-zero verdicts fail closed, and the cheap error is
  the only one this command is allowed to make.
"""


def render(result: dict) -> str:
    v = result["verdict"]
    lines = [{
        CLEAR: "CLEAR      nothing here moves authority, money, an account or a secret",
        RESERVED: "RESERVED   the owner's, under docs/standards/pm.md §21",
        UNDECIDED: "UNDECIDED  this command declines to answer, and that is not a clear",
    }[v], ""]

    if not result["files"]:
        lines.append("  no readable change in this diff")
        return "\n".join(lines)

    lines.append(f"  {len(result['files'])} file(s), {result['hunks']} hunk(s) read")
    if not result["findings"]:
        lines.append("  no changed line answered yes to any of the four questions")
    for f in result["findings"]:
        where = f"{f['path']}:{f['line']}" if f["line"] else f["path"]
        lines += ["", f"  [{f['verdict']}/{f['question']}] {where}",
                  f"      section: {f['section']}"]
        if f["text"]:
            lines.append(f"      line:    {f['text']}")
        lines.append(f"      because: {f['because']}")

    lines.append("")
    if v == RESERVED:
        lines += ["  Route: §22's ask on the board, with the PM's recommendation. It proceeds",
                  "  on silence only if it is not money, an account or a secret."]
    elif v == UNDECIDED:
        lines += ["  Route: a reader reads the lines above and says which way they go.",
                  "  Undecided is non-zero on purpose. Treat it as hers until somebody reads it."]
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Is this diff the owner's to merge? (docs/standards/pm.md §21)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = p.add_mutually_exclusive_group()
    src.add_argument("--pr", type=int, help="read a pull request's diff through gh")
    src.add_argument("--range", dest="rev", help="a git range, e.g. origin/main...HEAD")
    src.add_argument("--stdin", action="store_true", help="read a unified diff on stdin")
    p.add_argument("--base", help="the revision the diff is against, for section lookup "
                                  "(default: this working tree)")
    p.add_argument("--json", action="store_true", help="the verdict as json")
    p.add_argument("--explain", action="store_true", help="print the four questions and exit 0")
    args = p.parse_args(argv)

    if args.explain:
        print(EXPLANATION)
        return 0

    try:
        if args.stdin:
            text = sys.stdin.read()
        elif args.pr:
            text = diff_from_pr(args.pr)
        else:
            text = diff_from_range(args.rev or default_range())
    except RuntimeError as exc:
        print(f"ERROR      {exc}", file=sys.stderr)
        print("           this is not a verdict about the diff", file=sys.stderr)
        return EXIT[ERROR]

    result = examine(text, base=args.base)
    print(json.dumps(result, indent=2) if args.json else render(result))
    return result["exit"]


if __name__ == "__main__":
    sys.exit(main())
