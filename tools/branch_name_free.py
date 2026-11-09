#!/usr/bin/env python3
"""Has this branch name ever been used, and did the answer come from GitHub?

    python3 tools/branch_name_free.py <name>              # 0 free, 1 taken, 2 could not look
    python3 tools/branch_name_free.py <name> --json
    python3 tools/branch_name_free.py <name> --timeout 60
    python3 tools/branch_name_free.py --self-check        # the properties, printed

Exit 0 when GitHub answered and the name is free. Exit 1 when the name carries a
pull request or a remote ref. **Exit 2 when the question could not be asked**,
which is the whole reason this file exists, because the rule this gate serves
reads an unanswered question as a yes.

## Why a tool, when the clause is one line of `gh`

The never-reuse-a-branch-name rule in all twelve charters states its contract in
one sentence: "any output at all means pick a different name." So this is the
one gate in those charters whose **silence is a permission**. Every other gate
here fails toward refusal; a quiet `root_scratch.py` means clean, a quiet
`ban_list.py` means clean, and a broken one of either prints a traceback nobody
can mistake for a pass. This one is inverted, so any empty stdout for any reason
is read as "the name has never been used."

The clause carried `--limit 200` with a client-side `select` for six weeks. The
ExO seat corrected that to `--head` on 2026-11-09, server-side on the exact ref,
after this seat measured the window: at 846 pull requests the gate answered
empty for **8 of the 10 names in this repository that genuinely carry more than
one pull request**, including `exo/2026-09-18`, which carries #4, #18 and #30.
`INC-2026-11-09-the-branch-name-gate-answered-never-used-for-a-name-used-three-times`
is that correction, and it is right: `--head` has no recency window, and the
largest row count for a single ref here is eleven against a page of thirty, so
no truncation of it can manufacture a false empty.

**Truncation was one source of a false empty and not the only one.** A call that
fails produces an empty stdout too, and the contract cannot tell the two apart
because it never looks at the exit code. Measured on 2026-11-09 against the
corrected clause, verbatim, on `exo/2026-09-18`, a name with three pull
requests. The control returns 93 bytes:

| | exit | stdout | the contract reads |
|---|---|---|---|
| working `gh` and token | 0 | 93 bytes | taken, correctly |
| expired or wrong token | 1 | empty | **free** |
| `gh` absent from `PATH` | 127 | empty | **free** |
| API host unreachable | 1 | empty | **free** |
| run outside a git checkout | 1 | empty | **free** |

None of those four is hypothetical. The second is what an expired Actions secret
looks like, the fourth is what a rate limit looks like once the body is
discarded, and this organisation has the class in its register already:
`INC-2026-11-02-a-transient-rate-limit-was-written-into-two-queue-lines-as-a-property-of-the-address`
named it "a single-route instrument returning a negative result, written down as
a fact about the world rather than a fact about the instrument." That entry's
cost was a sentence written wrong. Here the negative result is not written down,
it is **acted on**, by the one gate whose contract turns a negative into a
permission, and the act is reusing a branch name, which
`INC-2026-09-30-branch-name-reuse-is-systemic` records five seats already doing
and which makes one reader unable to tell a run's new commits from an old run's.

So the exit code is the finding and the fix is not a better query. A gate whose
silence is a permission has to be unable to be silent by accident.

## What it asks, and why two questions

**Pull requests, every state, exact ref.** `gh pr list --state all --head NAME`,
server-side, no recency window. This is the ExO's corrected clause, executed
rather than quoted, so the twelve charters can cite one path instead of carrying
a query each.

**A remote ref with no pull request.** `git ls-remote --heads origin NAME`. The
charters' absolute is about a name whose pull request already merged, and the
reuse that actually collides is one step wider: a live `refs/heads` the host
would push onto. A branch pushed and never opened answers nothing to the first
question. Five of this repository's ten reused names were found through pull
requests, so the first question is the load-bearing one, and the second costs
one call and closes the case the first cannot see.

Both calls are bounded in time, because a gate that hangs stops a run without
saying so, and a single git helper with no timeout at all is the defect this
seat shipped in `tools/root_scratch.py` and fixed on 2026-11-09. A timeout here
is an exit 2, never an exit 0.

## It prints on success, deliberately

`root_scratch.py` prints nothing when it passes, so it can sit in front of an
`&&` without being noticed. This one says what it asked and what answered, on
every path including the clean one, because the lesson of the clause it replaces
is that a gate whose quiet means permission must not be quiet. The line names
the denominator the way the register's detector now prints `refs N of M`: a
reader who sees "asked GitHub" knows the answer came from the server, and a
reader who sees nothing knows the gate never ran.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

DEFAULT_TIMEOUT = 30

# gh pages --head at 30 rows and the contract needs only the first, but ask for
# more than the largest count this repository has ever carried for one ref so
# the printed number is the true one rather than a page.
PR_PAGE = 100

FREE = 0
TAKEN = 1
CANNOT_LOOK = 2


class CannotLook(Exception):
    """The question could not be asked. Never an answer of "free"."""


def _run(argv: list[str], timeout: int) -> str:
    """Run a command and return stdout, or raise CannotLook with the reason.

    Every failure shape lands here rather than in a caller's empty string: a
    missing binary, a non-zero exit, a timeout. That is the whole mechanism.
    """
    if shutil.which(argv[0]) is None:
        raise CannotLook(f"{argv[0]} is not on PATH")
    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        raise CannotLook(
            f"{argv[0]} did not answer within {timeout}s: {' '.join(argv)}"
        ) from None
    except OSError as exc:  # pragma: no cover - defensive
        raise CannotLook(f"{argv[0]} could not be run: {exc}") from None
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        first = detail[0] if detail else f"exit {proc.returncode}"
        raise CannotLook(f"{argv[0]} exited {proc.returncode}: {first}")
    return proc.stdout


def pull_requests(name: str, timeout: int, repo: str | None = None) -> list[dict]:
    """Every pull request ever opened on this exact head ref."""
    argv = [
        "gh", "pr", "list",
        "--state", "all",
        "--head", name,
        "--limit", str(PR_PAGE),
        "--json", "number,state,url",
    ]
    if repo:
        argv += ["--repo", repo]
    out = _run(argv, timeout)
    if not out.strip():
        # A successful `gh pr list --json` always prints at least `[]`. Reading a
        # blank body as the empty list would put this file's own defect inside
        # its fix: an absent answer standing in for an answer of none.
        raise CannotLook("gh exited 0 and printed nothing where json was asked for")
    try:
        rows = json.loads(out)
    except json.JSONDecodeError as exc:
        raise CannotLook(f"gh returned output that is not json: {exc}") from None
    if not isinstance(rows, list):
        raise CannotLook("gh returned json that is not a list")
    return rows


def remote_ref(name: str, timeout: int) -> bool:
    """Is there a live refs/heads on origin under this name?"""
    out = _run(["git", "ls-remote", "--heads", "origin", name], timeout)
    return bool(out.strip())


def check(name: str, timeout: int = DEFAULT_TIMEOUT, repo: str | None = None) -> dict:
    """Ask both questions. Raises CannotLook rather than guessing."""
    rows = pull_requests(name, timeout, repo)
    ref = remote_ref(name, timeout)
    return {
        "name": name,
        "asked": "gh pr list --state all --head, server-side on the exact ref",
        "pull_requests": [
            {"number": r.get("number"), "state": r.get("state"), "url": r.get("url")}
            for r in rows
        ],
        "pull_request_count": len(rows),
        "remote_ref": ref,
        "free": not rows and not ref,
    }


def describe(result: dict) -> str:
    n = result["pull_request_count"]
    name = result["name"]
    if result["free"]:
        return (
            f"free: asked GitHub for every pull request whose head ref is exactly "
            f"{name!r} and it returned 0, and origin has no ref by that name."
        )
    parts = []
    if n:
        shown = ", ".join(
            f"#{p['number']} ({str(p['state']).lower()})" for p in result["pull_requests"]
        )
        parts.append(f"{n} pull request{'s' if n != 1 else ''}: {shown}")
    if result["remote_ref"]:
        parts.append("a live ref on origin")
    return f"TAKEN: {name!r} carries " + " and ".join(parts) + ". Pick a different name."


SELF_CHECK = """\
branch_name_free.py, the four properties it is written to hold

1. A name that carries pull requests exits 1 and names them, because the
   charters' contract is that any output means pick a different name and a
   number a reader can follow is better than output.
2. A name that carries nothing exits 0 and still prints a line, because this
   is the one gate in those charters whose silence is a permission.
3. A question that could not be asked exits 2 and never 0. Four shapes were
   measured producing an empty stdout from the corrected clause: a wrong token,
   no gh on PATH, an unreachable host, and running outside a checkout. All four
   read as "free" to a contract that looks only at output.
4. Both calls are bounded in time and a timeout is an exit 2. A gate that hangs
   stops a run without saying so.

The query is server-side on the exact ref, so no recency window exists. That
half is the ExO seat's correction of 2026-11-09 and this file executes it
rather than restating it. A second question goes to origin for a live
refs/heads under the name, which no pull request query can see, and a git that
cannot answer it is an exit 2 the same way.
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Has this branch name ever been used on this repository?"
    )
    ap.add_argument("name", nargs="?", help="the branch name you are about to create")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--repo", help="owner/name, when not run inside the checkout")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    ap.add_argument("--self-check", action="store_true", dest="self_check")
    args = ap.parse_args(argv)

    if args.self_check:
        sys.stdout.write(SELF_CHECK)
        return FREE
    if not args.name:
        ap.error("a branch name is required")
    if args.timeout <= 0:
        ap.error("--timeout must be positive, since zero is a gate that never answers")

    try:
        result = check(args.name, args.timeout, args.repo)
    except CannotLook as exc:
        if args.as_json:
            print(json.dumps({"name": args.name, "free": None, "cannot_look": str(exc)}, indent=1))
        else:
            sys.stderr.write(
                f"COULD NOT LOOK: {exc}\n"
                "This is not an answer of 'free'. The name may well be taken. "
                "Fix the call or ask a seat that can reach GitHub, and do not "
                "read this as permission.\n"
            )
        return CANNOT_LOOK

    if args.as_json:
        print(json.dumps(result, indent=1))
    else:
        print(describe(result))
    return FREE if result["free"] else TAKEN


if __name__ == "__main__":
    sys.exit(main())
