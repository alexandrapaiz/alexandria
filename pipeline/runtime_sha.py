"""What each scheduled job is actually running, recorded by the job itself.

`modal deploy` bakes this repository's files into an image, and after that the
image is the thing that runs. A merge to main and a deploy are two separate
events, nothing in this repository has ever asked a running job what it
contains, and the org has now paid for that gap twice. Incident 24 is the first
time. PR #110 is the second: merged 2026-09-26, inert for days, with three
documents describing its behaviour as live while the deployed image knew
nothing about it.

The fix is one sentence long. Every scheduled job hashes the files it is
actually running from and writes that digest to a row, on every run. Then a
check with the repository in front of it can compare the recorded digest with
the repository's own and say plainly whether the deploy is current. That check
is the `deploy` surface in `tools/delivery_health.py`, and this module is the
half that runs inside the container.

Three things make the digest worth trusting.

**The file list is derived, never declared.** It comes from parsing the
`add_local_file` and `add_local_dir` calls in the job's own module, which is
the trick `pipeline/budget.py` already plays on `triage.MODELS`: a hand-kept
copy of a list is a list that disagrees with reality on the day it matters.
A file added to an image is in the digest the moment it is added, with nothing
to remember.

**It is keyed by repository path and read from wherever the file lives.** In
the container `pipeline/budget.py` is `/root/budget.py`. Both sides hash the
same bytes under the same key, so a digest computed on Modal is comparable
with one computed from a git checkout, which is the whole point.

**It cannot break the job it guards.** Every entry point here returns a string
instead of raising, and the database write runs inside its own savepoint. A
drift guard that can fail a production run is worse than no drift guard.

Stdlib only, and no `modal` import, because this module travels into three
images and is also imported by `tools/delivery_health.py` in a seat's sandbox,
where the Modal SDK has no reason to be installed.
"""

from __future__ import annotations

import hashlib
import pathlib
import re

# The three jobs this guards, and the module `modal deploy` is pointed at for
# each. The deploy command goes in the alarm, so the owner reads what to run
# rather than what is wrong.
APPS = {
    "triage": "pipeline/triage.py",
    "interpret": "pipeline/interpret.py",
    "weekly": "pipeline/weekly.py",
}

# Modal mounts the deployed module itself at the root of the image alongside
# whatever the image adds, which is why every one of these files imports its
# neighbours off `/root`. Parsed rather than assumed for the added files; for
# the module itself the caller passes `__file__`, so no assumption is needed
# there either.
_ADD_FILE = re.compile(
    r"""\.add_local_file\(\s*["']([^"']+)["']\s*,\s*["']([^"']+)["']""")
_ADD_DIR = re.compile(
    r"""\.add_local_dir\(\s*["']([^"']+)["']\s*,\s*["']([^"']+)["']""")

DIGEST_CHARS = 12


def manifest(source: str) -> list[tuple[str, str, bool]]:
    """The (repository path, container path, is_dir) triples an image adds.

    Read out of the module's own source. A regex over source is a blunt
    instrument and it is the right one here: the alternative is importing the
    module to inspect the built image, and importing `pipeline/weekly.py`
    from a seat's sandbox needs the Modal SDK, a stub for it, or both.
    """
    found = [(repo, box, False) for repo, box in _ADD_FILE.findall(source)]
    found += [(repo, box, True) for repo, box in _ADD_DIR.findall(source)]
    return found


def _walk(root: pathlib.Path) -> list[pathlib.Path]:
    """Every file under a directory, sorted, ignoring caches."""
    out = [p for p in sorted(root.rglob("*"))
           if p.is_file() and "__pycache__" not in p.parts]
    return out


def _expand(pairs: list[tuple[str, str, bool]],
            resolve) -> list[tuple[str, pathlib.Path]]:
    """Turn the manifest into (key, location) entries, expanding directories.

    `resolve` says which side we are on: it maps a manifest path to a real one,
    which is identity in the container and "under the repository root" locally.
    """
    entries: list[tuple[str, pathlib.Path]] = []
    for repo, box, is_dir in pairs:
        if not is_dir:
            entries.append((repo, resolve(repo, box)))
            continue
        base = resolve(repo, box)
        if not base.is_dir():
            # A directory named in the manifest that is not there is a finding,
            # not something to skip quietly. The empty location hashes as
            # missing below and the two sides disagree, which is correct.
            entries.append((repo + "/", base))
            continue
        for path in _walk(base):
            entries.append((f"{repo}/{path.relative_to(base).as_posix()}", path))
    return entries


def local_entries(app: str, repo_root) -> list[tuple[str, pathlib.Path]]:
    """What the repository says this app should be running, keyed by repo path."""
    root = pathlib.Path(repo_root)
    module = APPS[app]
    source = (root / module).read_text(encoding="utf-8")
    pairs = manifest(source)
    return ([(module, root / module)]
            + _expand(pairs, lambda repo, box: root / repo))


def runtime_entries(app: str, module_file: str,
                    source: str) -> list[tuple[str, pathlib.Path]]:
    """What this container is running, keyed by the same repository paths."""
    pairs = manifest(source)
    return ([(APPS[app], pathlib.Path(module_file))]
            + _expand(pairs, lambda repo, box: pathlib.Path(box)))


def digest(entries: list[tuple[str, pathlib.Path]]) -> str:
    """A content digest over (key, bytes), order-independent and path-independent.

    A file that is not there hashes as the literal word `missing` rather than
    being dropped, because a deploy that lost a file and a deploy that never
    had it are different facts and an omitted entry makes them the same one.
    """
    h = hashlib.sha256()
    for key, path in sorted(entries, key=lambda e: e[0]):
        try:
            body = pathlib.Path(path).read_bytes()
            inner = hashlib.sha256(body).hexdigest()
        except OSError:
            inner = "missing"
        h.update(f"{key}\0{inner}\n".encode())
    return h.hexdigest()[:DIGEST_CHARS]


# The row is one per app and it carries three different times on purpose.
# `first_seen_at` is when this exact deploy started running, which is the
# question "when did the fix actually go live". `recorded_at` is when the job
# last ran at all. `notified_at` is the alarm's own cooldown, so a drift that
# lasts a week costs the owner one mail a day rather than one per check.
UPSERT = """
insert into deploy_runtime (app, runtime_sha, entrypoint, file_count)
values (%s, %s, %s, %s)
on conflict (app) do update set
    runtime_sha   = excluded.runtime_sha,
    entrypoint    = excluded.entrypoint,
    file_count    = excluded.file_count,
    recorded_at   = now(),
    first_seen_at = case when deploy_runtime.runtime_sha = excluded.runtime_sha
                         then deploy_runtime.first_seen_at else now() end,
    notified_at   = case when deploy_runtime.runtime_sha = excluded.runtime_sha
                         then deploy_runtime.notified_at else null end
"""


def record_runtime(conn, app: str, module_file: str) -> tuple[str, str]:
    """Hash this deploy and write it down. Returns (sha, the line to print).

    Never raises, on any path. The write runs inside `conn.transaction()`,
    which is a savepoint when the caller is already in a transaction: without
    it, a missing table would abort the job's whole transaction and the guard
    would take down the run it exists to protect. That is not hypothetical
    here, because the table lands in `db/schema.sql` in the same change as
    this function and `apply_schema` is a separate hand-run step.
    """
    try:
        source = pathlib.Path(module_file).read_text(encoding="utf-8")
        entries = runtime_entries(app, module_file, source)
        sha = digest(entries)
    except Exception as exc:
        return "", f"runtime: this deploy could not be hashed ({exc})"
    try:
        with conn.transaction():
            conn.execute(UPSERT, (app, sha, APPS[app], len(entries)))
    except Exception as exc:
        return sha, (f"runtime: {sha} over {len(entries)} files, "
                     f"NOT recorded ({exc}), so the drift guard is blind to "
                     f"this run")
    return sha, f"runtime: {sha} over {len(entries)} files, recorded for {app}"
