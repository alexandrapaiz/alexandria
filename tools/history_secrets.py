#!/usr/bin/env python3
"""Is anything credential-shaped in this repository's history, and could this clone tell?

    python3 tools/history_secrets.py                   # every blob on every ref
    python3 tools/history_secrets.py --worktree         # the working tree only, fast
    python3 tools/history_secrets.py --json
    python3 tools/history_secrets.py --baseline docs/security/history-secrets.json
    python3 tools/history_secrets.py --self-check       # the properties, printed

Exit 0 when nothing credential-shaped is found and this clone could see the
history. Exit 1 on a finding. **Exit 2 when the clone cannot answer**, which is
the reason this file exists.

## Why

The security charter's first audit duty is "scan the working tree and the full
git history for anything credential-shaped." Ten audits have answered it and
none of them answered it with a tool. The 2026-11-08 audit did the work
properly, over 8,536 blobs across 4,686 commits, and said so in its own report:
"the history scan is reproducible from this description and the script is not."

So the duty that would catch a leaked credential was carried out by a fresh
ad-hoc script every sweep, and a duty whose instrument is a description and
whose clean answer is silence gives a reader no way to tell a scan of 8,536
blobs from a scan of one. Of the two errors that shape can make, the one it
makes is a false clean.

**And the clone it runs on is blind by default.** The host clones this
repository at `--depth 1`, which implies `--single-branch`, so `--all` reaches
one grafted commit on one branch. Its sibling duty was measured on exactly that
clone on 2026-11-09 and published as clean: `tools/history_boundary.py`'s
docstring carries the reproduction. The same blindness applies here and the
preflight below is the same one, which is why it is imported rather than
retyped.

## What this reads, and why blobs rather than diffs

Every blob reachable from every ref, once each. Blobs are content-addressed, so
a file that never changed across four thousand commits is one read rather than
four thousand, and a secret that was committed and then deleted is still a
blob. A scan of `git log -p` would read the same content repeatedly and still
miss a file added on a ref whose tip was later rewritten.

The reads are chunked and every chunk is bounded in time. That is not
decoration: an unbounded `git cat-file` here would hang a gate in front of a
seat's ready command, which is the class
`docs/security/unbounded-calls-2026-11-09.json` exists to count. This file adds
no row to it.

## What it never prints

A matched value, ever, including one already leaked. The charter's words are
"NEVER print, quote, or copy the value anywhere, including your PR and logs",
so a finding is reported as the path, the object, the commit that carries it
and the kind of credential it looks like. The pattern that matched is named.
The bytes that matched are not, and there is no flag that turns that off.

## The pattern set, and the two things it gets wrong on purpose

The set lives in `PATTERNS` below rather than in a seat's head, which is the
whole point of the file. It is shape-matching and nothing more, so it has both
errors available to it.

A false positive costs one baseline row with a reason. A false negative is a
live credential in a public repository, so where the two trade off, this file
takes the noise. The generic assignment pattern is the one that earns its keep
and the one that will need baseline rows.

**The needles are built from pieces, and that is load-bearing rather than
coy.** A scanner whose source holds a PEM private-key header as a literal
matches itself forever, and the obvious repair, skipping its own file, is a
carve-out that would hide a real secret pasted into this file.

The first version of this paragraph quoted that header in full in order to
explain why it must not be quoted in full, and the history scan this file was
written for is what found it: one finding, in `tools/history_secrets.py`,
reported by itself. The sentence is now a description. The same
applies to the suite: `tests/test_history_secrets.py` assembles every fixture at
run time from fragments, so no blob in this repository's history ever contains a
string this tool matches. That property is tested.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent

CLEAN = 0
FOUND = 1
CANNOT_LOOK = 2

#: How many objects go to one `git cat-file --batch`. Chunked so that both the
#: clock and the memory are bounded per call rather than per run.
CHUNK = 400

#: Seconds for one chunk. Generous, because a cold pack on a loaded shared host
#: is slow, and still finite, because the alternative is the sixty-minute wall.
CHUNK_TIMEOUT = 120

_spec = importlib.util.spec_from_file_location(
    "check_pr_green", TOOLS / "check_pr_green.py"
)
_green = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("check_pr_green", _green)
_spec.loader.exec_module(_green)

# Assembled from fragments so this file is not itself a finding. See the
# docstring: skipping our own path would be a carve-out a real secret could
# hide behind.
_BEGIN = "-" * 5 + "BEGIN"
_PRIVATE_KEY = "PRIVATE KEY" + "-" * 5

#: The two case-insensitive patterns are built through this rather than with an
#: inline `(?i)`, because an inline global flag cannot appear part-way into a
#: concatenated expression and `COMBINED` below concatenates every source.
#: `(?i:...)` scopes the flag to its own group, which is the spelling that
#: survives the join.
def ci(source: str) -> re.Pattern:
    return re.compile(f"(?i:{source})")


#: `(kind, compiled pattern, what a hit would be)`. Kind is what gets printed.
PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36}"),
     "a GitHub personal, OAuth, user, server or refresh token"),
    ("github-fine-grained-pat", re.compile(r"github_pat_[A-Za-z0-9_]{22,}"),
     "a GitHub fine-grained personal access token"),
    ("anthropic-key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
     "an Anthropic API key"),
    ("openrouter-key", re.compile(r"sk-or-v1-[A-Za-z0-9]{32,}"),
     "an OpenRouter key, which is the OPENROUTE_BASE_URL endpoint's credential"),
    ("openai-style-key", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"),
     "an OpenAI-shaped API key"),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
     "an AWS access key id, which names the account even without its secret"),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
     "a Google API key"),
    ("slack-token", re.compile(r"xox[baprse]-[0-9A-Za-z-]{10,}"),
     "a Slack bot, user, app or refresh token"),
    ("stripe-live-key", re.compile(r"\b[sr]k_live_[0-9A-Za-z]{16,}\b"),
     "a live Stripe secret or restricted key"),
    ("modal-token", re.compile(r"\ba[ks]-[A-Za-z0-9]{22,}\b"),
     "a Modal token id or secret, and requirements.txt pins modal"),
    ("private-key-block", re.compile(re.escape(_BEGIN) + r"[A-Z ]*" + re.escape(_PRIVATE_KEY)),
     "a PEM or OpenSSH private key block"),
    ("signed-jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
     "a signed JWT, which the MCP server issues and which carries its signing key's authority"),
    ("db-url-with-password",
     re.compile(r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://"
                r"[^\s:/@\"']+:[^\s:/@\"']{6,}@"),
     "a connection string carrying an inline password"),
    ("labelled-app-password",
     ci(r"(?:app[_ -]?password|smtp[_ -]?pass\w*)[^A-Za-z0-9]{0,24}"
                r"\b[a-z]{4} ?[a-z]{4} ?[a-z]{4} ?[a-z]{4}\b"),
     "a mail app password in its four-group spelling, next to its own label"),
    ("assigned-secret",
     re.compile(r"[\"'][A-Za-z0-9_+/=-]{24,}[\"']"),
     "a long opaque value assigned to a credential-shaped name"),
]


#: What may sit between a credential word and the value it vouches for.
#:
#: Without this, the window alone was far too generous, and the history scan
#: measured the cost: 95 of 107 unaccepted findings over 9,103 blobs were a
#: long quoted *identifier* vouched for by a credential word in a neighbouring
#: key. `"token_endpoint_auth_methods_supported": "none",` followed by
#: `"code_challenge_methods_supported"` is the clearest specimen. The word
#: `token` is real, the 32-character quoted string a few bytes later is real,
#: and nothing whatsoever is assigned to anything.
#:
#: So the value has to be the word's own value: quotes, whitespace, a colon or
#: an equals, and the brackets of an `os.environ["X_API_KEY"] = "..."`
#: subscript. A letter or a digit in between means the match belongs to some
#: other name, which is the whole class above.
BETWEEN = re.compile(r"""[-"'\s:=\]\)]*""")


#: Kinds whose pattern is only a driver: a match counts when one of these words
#: appears within `CONTEXT_WINDOW` characters before it.
#:
#: Written for `assigned-secret`, which started life as one regex reading
#: "credential word, then a colon or equals, then a long quoted value". That
#: spelling had both problems available to it.
#:
#: It was the slowest thing in the file by a distance. A six-way word
#: alternation with six different first characters gives the engine no literal
#: to search for, so it attempted a match at every one of two million
#: positions in `docs/ideas.md` for 1.3s a pass, and history holds 1,641 MiB of
#: blob content.
#:
#: And it was wrong in the commonest spelling of all. `"api_key": "<value>"` is
#: JSON, and in JSON the credential word is followed by a quote before the
#: colon, which the old pattern required to be whitespace. So the single most
#: likely way for a key to be committed to this repository was the one shape it
#: could not see.
#:
#: Driving on the quoted value fixes both. A quote followed by 24 or more
#: characters of an opaque class is rare in prose, so the engine has something
#: to find, and the window behind it is read in Python where a quote between
#: the word and the colon costs nothing.
CONTEXT: dict[str, tuple[str, ...]] = {
    "assigned-secret": ("api_key", "apikey", "api-key", "secret", "token",
                        "password", "passwd", "credential"),
}

#: Characters before a driver match that count as its context. Wide enough for
#: `"api_key" : "` with indentation, narrow enough that a credential word one
#: paragraph up does not vouch for an unrelated hash.
CONTEXT_WINDOW = 64


#: A literal every match of a pattern must contain, lowercased, keyed by kind.
#:
#: This is what makes the history scan finishable, and the first thing tried in
#: its place did not work. `docs/agents/incidents.md` and `docs/ideas.md` are
#: megabytes of prose and history holds many versions of each, so fifteen
#: regex passes over all of them ran past this run's own command bound. Joining
#: the fifteen into one alternation changed nothing, measured: a backtracking
#: engine tries every branch at every position, so one fifteen-way alternation
#: costs what fifteen passes cost. `docs/ideas.md` went from 4.5s to 2.3s and
#: the remainder was the join itself.
#:
#: A literal substring test is a different kind of operation. `"sk-ant-" in
#: text` is a C-level search with no backtracking, so fourteen of the fifteen
#: patterns never compile a match attempt against a blob of prose.
#:
#: **Every entry here is a necessary condition of its pattern, and a wrong one
#: would be a false clean.** That is the dangerous direction for this file, so
#: it is not argued from the regex source: `tests/test_history_secrets.py`
#: drives a positive fixture through `scan_text` for every kind, which is the
#: path that applies the hint, and a hint that excluded a real match would fail
#: there.
HINTS: dict[str, tuple[str, ...]] = {
    "github-token": ("ghp_", "gho_", "ghu_", "ghs_", "ghr_"),
    "github-fine-grained-pat": ("github_pat_",),
    "anthropic-key": ("sk-ant-",),
    "openrouter-key": ("sk-or-v1-",),
    "openai-style-key": ("sk-",),
    "aws-access-key-id": ("akia", "asia"),
    "google-api-key": ("aiza",),
    "slack-token": ("xox",),
    "stripe-live-key": ("k_live_",),
    "modal-token": ("ak-", "as-"),
    "private-key-block": ("private key",),
    "signed-jwt": ("eyj",),
    "db-url-with-password": ("postgres://", "postgresql://", "mysql://",
                             "mongodb://", "mongodb+srv://", "redis://",
                             "amqp://"),
    "labelled-app-password": ("app password", "app_password", "app-password",
                              "apppassword", "smtp pass", "smtp_pass",
                              "smtp-pass", "smtppass"),
    "assigned-secret": ("api_key", "apikey", "api-key", "secret", "token",
                        "password", "passwd", "credential"),
}


class CannotLook(Exception):
    """This clone cannot answer. Never an answer of "clean"."""


def _git(*args: str, repo: Path = ROOT, timeout: int = 60) -> str:
    """One bounded git call, where a refusal and an empty answer stay apart."""
    try:
        proc = subprocess.run(
            ["git", *args], cwd=str(repo), capture_output=True, text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise CannotLook(
            f"git did not answer within {timeout}s: git {' '.join(args)}"
        ) from None
    except OSError as exc:
        raise CannotLook(f"git could not be run: {exc}") from None
    if proc.returncode != 0:
        first = (proc.stderr or "").strip().splitlines()
        raise CannotLook(
            f"git exited {proc.returncode}: {first[0] if first else 'no message'}"
        )
    return proc.stdout


REMEDY = (
    "Run: git config --add remote.origin.fetch "
    "'+refs/heads/*:refs/remotes/origin/*' && git fetch --unshallow"
)


def preflight(repo: Path = ROOT) -> str | None:
    """The reason this clone cannot answer, or None.

    The two primitives are `tools/check_pr_green.py`'s and
    `tools/history_boundary.py` calls the same pair for the sibling duty. The
    sentence differs because the question does: there, a private path on an
    unreachable ref is invisible; here, every blob on that ref is.
    """
    state = _green.shallow_state(repo)
    if state is not False:
        was = "is shallow" if state else "could not say whether it is shallow"
        return (f"this clone {was}, so the history this duty asks about is not "
                f"here to be scanned. {REMEDY}")
    if not _green.refspec_is_wide(repo):
        return ("this clone's fetch refspec names only the trunk, so `--all` "
                f"reaches the trunk alone and every other ref is unread. {REMEDY}")
    return None


def blob_index(repo: Path = ROOT) -> list[tuple[str, str]]:
    """Every distinct blob on every ref, as `(object, the path it was listed at)`.

    One row per object rather than per commit, which is the whole reason this
    reads blobs. The path is whatever name the object was listed under, which is
    a locator for a reader and not a claim that the file is still there.
    """
    out = _git("rev-list", "--objects", "--all", repo=repo, timeout=300)
    seen: dict[str, str] = {}
    for line in out.splitlines():
        oid, _, path = line.partition(" ")
        if path and oid not in seen:
            seen[oid] = path
    if not seen:
        raise CannotLook("`git rev-list --objects --all` named no paths at all")
    return _batch_check(seen, repo)


def _batch_check(seen: dict[str, str], repo: Path) -> list[tuple[str, str]]:
    """Keep the blobs, drop the trees and tags, in bounded chunks."""
    oids = list(seen)
    blobs: list[tuple[str, str]] = []
    for start in range(0, len(oids), CHUNK):
        chunk = oids[start:start + CHUNK]
        try:
            proc = subprocess.run(
                ["git", "cat-file", "--batch-check=%(objectname) %(objecttype)"],
                cwd=str(repo), input="\n".join(chunk) + "\n",
                capture_output=True, text=True, timeout=CHUNK_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            raise CannotLook(
                f"`git cat-file --batch-check` did not answer within "
                f"{CHUNK_TIMEOUT}s on a chunk of {len(chunk)}"
            ) from None
        except OSError as exc:
            raise CannotLook(f"git could not be run: {exc}") from None
        if proc.returncode != 0:
            raise CannotLook(
                f"`git cat-file --batch-check` exited {proc.returncode}"
            )
        for line in proc.stdout.splitlines():
            oid, _, kind = line.partition(" ")
            if kind.strip() == "blob":
                blobs.append((oid, seen[oid]))
    return blobs


def scan_text(text: str) -> list[tuple[str, str]]:
    """`(kind, note)` for every pattern that matched, with no value carried out.

    Returns the kinds rather than the matches on purpose. A caller that cannot
    get the bytes cannot leak them into a log by accident, which is the charter
    rule this function enforces structurally rather than by discipline.
    """
    low = text.lower()
    return [(kind, note) for kind, pattern, note in PATTERNS
            if _matches(text, low, kind, pattern)]


#: How far either side of a hint the pattern is given to match. `BEFORE` covers
#: the most deeply buried hint in `HINTS`, which sits about twenty characters
#: into its match; `AFTER` covers the longest minimum match, which is about
#: forty. Both are an order of magnitude past what any pattern needs, because
#: the cost of generosity here is microseconds and the cost of meanness is a
#: credential this file reports as absent.
WINDOW_BEFORE = 128
WINDOW_AFTER = 512


def _matches(text: str, low: str, kind: str, pattern: re.Pattern) -> bool:
    """Does this pattern match, searched from its hints rather than from byte zero.

    A hint is a necessary literal, so every match contains one, so searching a
    window around each occurrence of one finds every match the whole-text
    search would. What it skips is the attempts, and the attempts were the
    whole bill: with the hint used only as a gate, `openai-style-key` and
    `labelled-app-password` still cost 0.78s and 0.72s a pass over
    `docs/ideas.md`, because `task-`, `risk-` and `desk-` all contain `sk-` and
    the gate opens on any of them. Anchored, the regex runs on a few hundred
    characters per occurrence instead of two million.
    """
    words = CONTEXT.get(kind)
    if words is not None:
        return _confirmed_near(text, low, pattern, words)
    hints = HINTS.get(kind)
    if not hints:
        return bool(pattern.search(text))
    for hint in hints:
        at = low.find(hint)
        while at != -1:
            region = text[max(0, at - WINDOW_BEFORE):
                          at + len(hint) + WINDOW_AFTER]
            if pattern.search(region):
                return True
            at = low.find(hint, at + 1)
    return False


def _confirmed_near(text: str, low: str, driver: re.Pattern,
                    words: tuple[str, ...]) -> bool:
    """Does `driver` match within `CONTEXT_WINDOW` after one of `words`.

    Searched forward from each word rather than by matching the driver across
    the whole text and looking back, and the difference is the cost. Looking
    back means running the driver over every byte: `docs/ideas.md` is two
    megabytes of prose carrying thousands of quoted kebab-case slugs long
    enough to drive on, so that spelling cost 2.5s a blob against 1,641 MiB of
    history.

    Forward from the word, the driver only ever runs on a few hundred
    characters per occurrence of a credential word, and the answer is the same
    one: a finding needs a word behind it and a value in front of it, so
    starting from either end reaches the same pairs.
    """
    reach = CONTEXT_WINDOW + 256
    for word in words:
        at = low.find(word)
        while at != -1:
            region = text[at:at + len(word) + reach]
            for hit in driver.finditer(region):
                if hit.start() > len(word) + CONTEXT_WINDOW:
                    break
                if BETWEEN.fullmatch(region[len(word):hit.start()]):
                    return True
            at = low.find(word, at + 1)
    return False


def _read_blobs(blobs: list[tuple[str, str]], repo: Path) -> tuple[list[dict], int]:
    """Findings and bytes read, in bounded chunks of `git cat-file --batch`."""
    findings: list[dict] = []
    bytes_read = 0
    oids = [oid for oid, _ in blobs]
    paths = dict(blobs)
    for start in range(0, len(oids), CHUNK):
        chunk = oids[start:start + CHUNK]
        try:
            proc = subprocess.run(
                ["git", "cat-file", "--batch"], cwd=str(repo),
                # Bytes in, because stdout is read as bytes: a blob is not
                # necessarily text and decoding it here would be a guess. The
                # first version passed a str against a bytes pipe and raised
                # TypeError out of main, which is the hole closed below.
                input=("\n".join(chunk) + "\n").encode("utf-8"),
                capture_output=True, timeout=CHUNK_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            raise CannotLook(
                f"`git cat-file --batch` did not answer within {CHUNK_TIMEOUT}s "
                f"on a chunk of {len(chunk)}"
            ) from None
        except OSError as exc:
            raise CannotLook(f"git could not be run: {exc}") from None
        if proc.returncode != 0:
            raise CannotLook(f"`git cat-file --batch` exited {proc.returncode}")
        bytes_read += len(proc.stdout)
        for oid, body in _split_batch(proc.stdout):
            hits = scan_text(body.decode("utf-8", "replace"))
            for kind, note in hits:
                findings.append({"object": oid[:12], "path": paths.get(oid, "?"),
                                 "kind": kind, "note": note})
    return findings, bytes_read


def _split_batch(raw: bytes):
    """`git cat-file --batch`'s stream, as `(object, body)`.

    Parsed on the declared length rather than on a newline, because a blob's
    own content holds newlines and a header-shaped line inside a file would
    otherwise desynchronise the whole chunk and silently drop the rest of it.
    """
    pos = 0
    while pos < len(raw):
        end = raw.find(b"\n", pos)
        if end == -1:
            return
        header = raw[pos:end].decode("utf-8", "replace").split()
        pos = end + 1
        if len(header) < 3 or header[1] in ("missing", "ambiguous"):
            continue
        try:
            size = int(header[2])
        except ValueError:
            return
        yield header[0], raw[pos:pos + size]
        pos += size + 1


def load_baseline(path: Path | None) -> set[tuple[str, str]]:
    """Accepted `(identity, kind)` pairs, where identity is an object or a path.

    Read strictly, like `tools/unbounded_calls.py`'s: an unreadable baseline is
    a `CannotLook` and never an empty set, because an empty set reads as
    "nothing is accepted" and would turn an unreadable file into a wall of
    findings nobody asked for.

    **Two identities, and the difference is how much a row forgives.** An
    `object` row is one blob, and a blob is its content, so such a row accepts
    exactly the bytes somebody read. A `path` row accepts that kind anywhere in
    that file, for every version of it in history, which is far broader and is
    what makes it usable at all: a placeholder living in `docs/ideas.md` is a
    different blob in every revision of that file, so an object row per blob
    would be hundreds of rows that go stale on the next commit.

    The first draft of this keyed worktree findings on the literal string
    `"worktree"`, so one accepted row would have silenced that kind across
    every file in the tree. A baseline that broad is a false clean wearing a
    reason, which is the error this whole file is shaped to avoid.
    """
    if path is None:
        return set()
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CannotLook(f"{path}: could not read the baseline ({exc})") from exc
    if not isinstance(data, dict) or not isinstance(data.get("accepted"), list):
        raise CannotLook(f"{path}: a baseline is an object with an 'accepted' list")
    out = set()
    for row in data["accepted"]:
        if not isinstance(row, dict) or "kind" not in row:
            raise CannotLook(f"{path}: every accepted row needs a kind")
        identity = row.get("object") or row.get("path")
        if not identity:
            raise CannotLook(
                f"{path}: every accepted row needs an object or a path")
        out.add((str(identity), str(row["kind"])))
    return out


def is_accepted(finding: dict, accepted: set[tuple[str, str]]) -> bool:
    """Either identity may carry the acceptance, and neither is implied."""
    return ((finding.get("object"), finding["kind"]) in accepted
            or (finding.get("path"), finding["kind"]) in accepted)


def worktree_files(repo: Path = ROOT) -> list[Path]:
    """Tracked files in the working tree, which is the fast half of the duty."""
    out = _git("ls-files", "-z", repo=repo, timeout=120)
    return [repo / name for name in out.split("\0") if name]


def check_worktree(repo: Path = ROOT,
                   accepted: set[tuple[str, str]] | None = None) -> dict:
    accepted = accepted or set()
    findings, read, bytes_read = [], 0, 0
    hidden = [0]
    for path in worktree_files(repo):
        try:
            body = path.read_bytes()
        except OSError:
            continue
        read += 1
        bytes_read += len(body)
        rel = str(path.relative_to(repo))
        for kind, note in scan_text(body.decode("utf-8", "replace")):
            row = {"object": None, "path": rel, "kind": kind, "note": note}
            if is_accepted(row, accepted):
                hidden[0] += 1
                continue
            findings.append(row)
    return {"scope": {"where": "working tree", "files_read": read,
                      "bytes_read": bytes_read},
            "findings": findings, "accepted": hidden[0]}


def check_history(repo: Path = ROOT,
                  accepted: set[tuple[str, str]] | None = None) -> dict:
    accepted = accepted or set()
    reason = preflight(repo)
    if reason:
        raise CannotLook(reason)
    commits = int(_git("rev-list", "--all", "--count", repo=repo).strip() or 0)
    if commits <= 1:
        # The guard above reads git's own shallow flag. This reads the result,
        # because a clone can be grafted in ways that flag does not admit and a
        # history of one commit cannot answer a question about history.
        raise CannotLook(
            f"this clone holds {commits} commit(s), which cannot answer a "
            "question about history even though git does not call it shallow"
        )
    refs = len(_git("for-each-ref", "--format=%(refname)", repo=repo).splitlines())
    started = time.monotonic()
    blobs = blob_index(repo)
    findings, bytes_read = _read_blobs(blobs, repo)
    kept = [f for f in findings if not is_accepted(f, accepted)]
    return {"scope": {"where": "every blob on every ref", "commits": commits,
                      "refs": refs, "blobs_read": len(blobs),
                      "bytes_read": bytes_read,
                      "seconds": round(time.monotonic() - started, 1)},
            "findings": kept, "accepted": len(findings) - len(kept)}


def describe(result: dict) -> str:
    scope = result["scope"]
    if result["findings"]:
        lines = ["CREDENTIAL-SHAPED CONTENT FOUND. The value is deliberately not "
                 "printed. Rotation is the owner's immediate action."]
        for row in result["findings"]:
            where = (f"blob {row['object']}" if row.get("object")
                     else "working tree")
            lines.append(f"  {row['path']}  ({where})  "
                         f"{row['kind']}: {row['note']}")
        lines.append("")
        lines.append("Record the file, the object and the kind. Never the value, "
                     "including in a pull request or a log.")
    else:
        where = scope["where"]
        if "blobs_read" in scope:
            read = (f"{scope['blobs_read']} distinct blobs over "
                    f"{scope['commits']} commits and {scope['refs']} refs, "
                    f"{scope['bytes_read'] // 1024} KiB in {scope['seconds']}s")
        else:
            read = (f"{scope['files_read']} tracked files, "
                    f"{scope['bytes_read'] // 1024} KiB")
        lines = [f"clean: {len(PATTERNS)} patterns over {where}, {read}. "
                 "The denominator is printed because this duty's clean answer "
                 "used to be silence, and silence cannot be told from not "
                 "having looked."]
        if result["accepted"]:
            lines.append(f"{result['accepted']} finding(s) accepted by the "
                         "baseline and not shown.")
    return "\n".join(lines)


SELF_CHECK = """tools/history_secrets.py, the properties it holds:

  1. A clone that cannot see the history exits 2, never 0. The preflight is
     tools/check_pr_green.py's, shared with tools/history_boundary.py.
  2. A clean answer prints its denominator: patterns, blobs, commits, refs and
     bytes. The duty's old clean answer was silence.
  3. A matched value is never printed, and no flag turns that off. scan_text
     returns kinds, so a caller cannot leak bytes by accident.
  4. Every external call is bounded in time, in chunks of %d objects with a
     %ds clock, so this gate cannot hang in front of an && .
  5. Its own needles are assembled from fragments, so no blob in this
     repository matches this tool because this tool exists.
""" % (CHUNK, CHUNK_TIMEOUT)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Is anything credential-shaped in this repository, and could "
                    "this clone tell?")
    ap.add_argument("--worktree", action="store_true",
                    help="the working tree only, which needs no history")
    ap.add_argument("--repo", type=Path, default=ROOT)
    ap.add_argument("--baseline", type=Path, default=None)
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--self-check", action="store_true", dest="self_check")
    args = ap.parse_args(argv)

    if args.self_check:
        sys.stdout.write(SELF_CHECK)
        return CLEAN

    try:
        accepted = load_baseline(args.baseline)
        result = (check_worktree(args.repo, accepted) if args.worktree
                  else check_history(args.repo, accepted))
    except Exception as exc:  # noqa: BLE001 - see below
        # Deliberately broad, and this is the lesson of the run that wrote this
        # file rather than a precaution. The first version of `_read_blobs`
        # passed a str to a bytes pipe, and the TypeError left `main` as **exit
        # 1**, which in this tool's own contract is "credential-shaped content
        # found". A crash that arrives as a finding is the same conflation as a
        # refusal that arrives as an answer, pointing the other way: three
        # exits mean clean, found and could-not-look, and a bug is the third of
        # those every time. Nothing below this line may turn an unexpected
        # exception into either of the first two.
        if not isinstance(exc, CannotLook):
            exc = CannotLook(f"{type(exc).__name__}: {exc}")
        if args.as_json:
            print(json.dumps({"clean": None, "cannot_look": str(exc)}, indent=1))
        else:
            sys.stderr.write(
                f"COULD NOT LOOK: {exc}\n"
                "This is not an answer of 'no credentials found'. Do not record "
                "a clean secret scan on it.\n")
        return CANNOT_LOOK

    if args.as_json:
        print(json.dumps(result, indent=1))
    else:
        print(describe(result))
    return FOUND if result["findings"] else CLEAN


if __name__ == "__main__":
    sys.exit(main())
