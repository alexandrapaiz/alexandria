"""The full-history scan for credential-shaped content.

Every test here carries a control, because the whole point of the tool is that
a negative result must be a fact about the repository and not a fact about the
instrument. A test that only asserts "nothing found" passes equally well
against a scanner that never looked, and this duty's clean answer was silence
for ten audits.

**Every fixture is assembled from fragments at run time.** A suite for a secret
scanner that writes matching literals into its own source puts them in this
repository's history forever, where its own subject then reports them. The tool
builds its needles from pieces for the same reason, and the second-to-last test
below checks that the property holds for the whole tree rather than trusting
either of us to remember.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import history_secrets as hs  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

#: Prose with word boundaries at both ends, so a fixture dropped in the middle
#: of it is still bounded on both sides. The first version of this filler was
#: concatenated without separators and three patterns reported a miss that was
#: the filler's fault rather than the tool's.
FILLER = "the quick brown fox jumps over the lazy dog. " * 300

#: One matching fixture per kind, assembled rather than written. The value of
#: this table is that it is exhaustive: a kind added to PATTERNS without a row
#: here fails `test_every_kind_has_a_fixture`.
FIXTURES = {
    "github-token": "ghp_" + "a" * 36,
    "github-fine-grained-pat": "github" + "_pat_" + "b" * 30,
    "anthropic-key": "sk-" + "ant-" + "c" * 30,
    "openrouter-key": "sk-" + "or-v1-" + "d" * 40,
    "openai-style-key": "sk-" + "e" * 40,
    "aws-access-key-id": "AK" + "IA" + "F" * 16,
    "google-api-key": "AI" + "za" + "g" * 35,
    "slack-token": "xo" + "xb-" + "1234567890h",
    "stripe-live-key": "sk" + "_live_" + "i" * 20,
    "modal-token": "ak" + "-" + "j" * 24,
    "private-key-block": "-" * 5 + "BEGIN" + " RSA " + "PRIVATE KEY" + "-" * 5,
    "signed-jwt": "ey" + "J" + "k" * 12 + ".ey" + "J" + "l" * 12 + "." + "m" * 12,
    "db-url-with-password": "postgres" + "://u:" + "n" * 10 + "@h/d",
    "labelled-app-password": "app " + "password: abcd efgh ijkl mnop",
    "assigned-secret": "secret = " + '"' + "o" * 30 + '"',
}


def kinds(text):
    return [kind for kind, _ in hs.scan_text(text)]


# --- the pattern set --------------------------------------------------------

def test_every_kind_has_a_fixture():
    """A pattern with no fixture is a pattern nothing proves fires."""
    assert set(FIXTURES) == {kind for kind, _, _ in hs.PATTERNS}


def test_every_kind_has_a_hint_and_the_hint_is_lowercase():
    """A missing hint is only slow. A hint in the wrong case is a false clean."""
    assert set(hs.HINTS) == {kind for kind, _, _ in hs.PATTERNS}
    for kind, hints in hs.HINTS.items():
        for hint in hints:
            assert hint == hint.lower(), (kind, hint)


@pytest.mark.parametrize("kind", sorted(FIXTURES))
def test_each_fixture_is_found_alone_and_buried_in_prose(kind):
    """The hint-anchored search must find what a whole-text search would.

    Buried as well as alone, because the search runs in a window around each
    hint rather than over the blob, so a fixture surrounded by megabytes of
    prose is the case that would expose a window too narrow to hold a match.
    """
    fixture = FIXTURES[kind]
    assert kind in kinds(fixture), "alone"
    assert kind in kinds(FILLER + " " + fixture + " " + FILLER), "buried"


@pytest.mark.parametrize("kind", sorted(FIXTURES))
def test_the_window_agrees_with_a_whole_text_search(kind):
    """The control for the optimisation: same answer, less work.

    `_matches` searches from the hints. This asserts it against the thing it
    replaced, a plain search over the whole text, on the same bytes.
    """
    pattern = {k: p for k, p, _ in hs.PATTERNS}[kind]
    blob = FILLER + " " + FIXTURES[kind] + " " + FILLER
    assert bool(pattern.search(blob)) is (kind in kinds(blob))


def test_prose_with_no_credential_in_it_is_quiet():
    """The denominator control: the filler alone must find nothing."""
    assert kinds(FILLER) == []


# --- assigned-secret, which is the one that earns its keep ------------------

@pytest.mark.parametrize("spelling", [
    'SECRET = "{v}"',
    '{{ "api_key": "{v}" }}',
    'os.environ["MOONSHOT_API_KEY"] = "{v}"',
    'token: "{v}"',
])
def test_a_value_assigned_to_a_credential_name_is_found(spelling):
    """Four real spellings, including the JSON one the first pattern missed.

    That pattern read "credential word, then a colon or equals, then a quoted
    value", and in JSON the word is followed by a quote before the colon. So
    the commonest way a key reaches a repository was the one shape it could
    not see.
    """
    assert "assigned-secret" in kinds(spelling.format(v="o" * 30))


@pytest.mark.parametrize("quiet", [
    # A credential word inside one key, vouching for a long identifier that is
    # the name of the next key. 95 of 107 unaccepted findings over this
    # repository's whole history were this one shape.
    '"token_endpoint_auth_methods_supported": "none",\n'
    '  "code_challenge_methods_supported": ["S256"],',
    'resp.headers.get("x-ratelimit-remaining-requests")',
    '"budget_fill_ratio_median": 6.1728,',
    'monkeypatch.setenv("GITHUB_REPOSITORY", "alexandrapaiz/alexandria")',
    "sha256 " + "b" * 40,
    'secret' + ' ' * 400 + '"' + "c" * 40 + '"',
])
def test_a_long_identifier_nobody_assigned_anything_to_is_quiet(quiet):
    assert kinds(quiet) == []


# --- the three exits --------------------------------------------------------

def test_a_malformed_baseline_is_a_refusal_and_never_an_empty_set(tmp_path):
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"accepted": [{"object": "abc", "kind": "k"}]}))
    assert hs.load_baseline(good) == {("abc", "k")}          # the control

    for bad in ([], {"accepted": {}}, {"rows": []},
                {"accepted": [{"kind": "k"}]},
                {"accepted": [{"object": "abc"}]}):
        rough = tmp_path / "rough.json"
        rough.write_text(json.dumps(bad))
        with pytest.raises(hs.CannotLook):
            hs.load_baseline(rough)
    assert hs.load_baseline(None) == set()


def test_an_object_row_does_not_forgive_the_path_or_the_other_way():
    """The breadth of a row is the thing a reader has to be able to see."""
    by_object = {("abc123", "anthropic-key")}
    by_path = {("tests/x.py", "anthropic-key")}
    finding = {"object": "abc123", "path": "tests/x.py",
               "kind": "anthropic-key"}
    assert hs.is_accepted(finding, by_object)
    assert hs.is_accepted(finding, by_path)
    # Neither forgives a different kind, and neither forgives a different file.
    assert not hs.is_accepted({**finding, "kind": "github-token"}, by_object)
    assert not hs.is_accepted({**finding, "object": "def456",
                               "path": "tests/y.py"}, by_path)


def test_an_unexpected_exception_exits_two_and_never_one(tmp_path, capsys,
                                                         monkeypatch):
    """A crash is "could not look", never "found".

    This is the hole this file shipped with for one commit. `_read_blobs`
    passed a str to a bytes pipe, the TypeError left `main`, and the process
    exited 1, which in this tool's contract means credential-shaped content
    was found. Three exits mean clean, found and could-not-look, and a bug is
    the third of those every time.
    """
    def boom(*a, **k):
        raise RuntimeError("the kind of thing nobody predicted")

    monkeypatch.setattr(hs, "check_worktree", boom)
    assert hs.main(["--worktree", "--repo", str(tmp_path)]) == hs.CANNOT_LOOK
    err = capsys.readouterr().err
    assert "RuntimeError" in err
    assert "not an answer of 'no credentials found'" in err


def test_a_clone_that_cannot_see_the_history_refuses(monkeypatch, tmp_path,
                                                     capsys):
    """Exit 2, not 0. This is the blindness the sibling duty was published on."""
    monkeypatch.setattr(hs._green, "shallow_state", lambda repo=None: True)
    assert hs.main(["--repo", str(tmp_path)]) == hs.CANNOT_LOOK
    assert "shallow" in capsys.readouterr().err

    # The control: not shallow, but the refspec names only the trunk.
    monkeypatch.setattr(hs._green, "shallow_state", lambda repo=None: False)
    monkeypatch.setattr(hs._green, "refspec_is_wide", lambda repo=None: False)
    assert hs.main(["--repo", str(tmp_path)]) == hs.CANNOT_LOOK
    assert "refspec" in capsys.readouterr().err

    # And a git that could not answer at all is also a refusal, never a pass.
    monkeypatch.setattr(hs._green, "shallow_state", lambda repo=None: None)
    assert hs.main(["--repo", str(tmp_path)]) == hs.CANNOT_LOOK


def test_the_clean_path_prints_its_denominator(tmp_path, capsys):
    """Silence cannot be told from not having looked, which is the whole file."""
    (tmp_path / "ok.py").write_text("x = 1\n")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, timeout=60)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, timeout=60)
    assert hs.main(["--worktree", "--repo", str(tmp_path)]) == hs.CLEAN
    out = capsys.readouterr().out
    assert "15 patterns" in out
    assert "tracked files" in out
    assert "KiB" in out


# --- history, against a real repository -------------------------------------

def _repo(tmp_path, body):
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path,
                   check=True, timeout=60)
    for key, value in (("user.email", "t@example.com"), ("user.name", "t"),
                       ("remote.origin.fetch",
                        "+refs/heads/*:refs/remotes/origin/*")):
        subprocess.run(["git", "config", key, value], cwd=tmp_path,
                       check=True, timeout=60)
    (tmp_path / "f.py").write_text(body)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, timeout=60)
    subprocess.run(["git", "commit", "-qm", "one"], cwd=tmp_path, check=True,
                   timeout=60)
    (tmp_path / "f.py").write_text("x = 2\n")
    subprocess.run(["git", "commit", "-aqm", "two"], cwd=tmp_path, check=True,
                   timeout=60)
    return tmp_path


def test_a_secret_deleted_from_the_tree_is_still_found_in_history(tmp_path):
    """The reason this reads blobs rather than the working tree.

    The fixture is committed and then overwritten, so the working tree is
    clean and the blob is not. A scan that only read the checkout would pass.
    """
    repo = _repo(tmp_path, "KEY = " + '"' + FIXTURES["anthropic-key"] + '"\n')
    assert hs.check_worktree(repo)["findings"] == []          # the control
    found = hs.check_history(repo)["findings"]
    assert [f["kind"] for f in found] == ["anthropic-key"]
    assert found[0]["path"] == "f.py"
    assert found[0]["object"] and found[0]["object"] != "worktree"


def test_a_finding_never_carries_the_matched_value(tmp_path):
    """Structural, not a matter of discipline: the charter forbids the value.

    `scan_text` returns kinds, so there is no code path on which a caller
    holds the bytes, and `describe` can only print what a finding holds.
    """
    repo = _repo(tmp_path, "KEY = " + '"' + FIXTURES["anthropic-key"] + '"\n')
    result = hs.check_history(repo)
    rendered = hs.describe(result) + json.dumps(result)
    needle = FIXTURES["anthropic-key"]
    assert needle not in rendered
    assert needle[8:] not in rendered
    assert set(result["findings"][0]) == {"object", "path", "kind", "note"}


def test_a_baseline_row_silences_the_history_finding(tmp_path, capsys):
    repo = _repo(tmp_path, "KEY = " + '"' + FIXTURES["anthropic-key"] + '"\n')
    baseline = tmp_path / "base.json"
    baseline.write_text(json.dumps({"accepted": [
        {"path": "f.py", "kind": "anthropic-key", "why": "a fixture"}]}))
    assert hs.main(["--repo", str(repo), "--baseline", str(baseline)]) == hs.CLEAN
    out = capsys.readouterr().out
    assert "1 finding(s) accepted by the baseline" in out
    assert "distinct blobs" in out


# --- the two properties about this repository itself ------------------------

def test_this_repository_has_no_blob_that_matches_because_a_scanner_exists():
    """The scanner and its suite must not be their own findings.

    Both assemble their needles from fragments so that no blob in this
    repository holds a string this tool matches. The first revision of each
    broke it in the same way, by quoting a needle in full while explaining that
    needles must not be quoted in full, and the tool's own first full-history
    pass is what found them. They are accepted by object, which is exactly
    those bytes and no forgiveness for either path.
    """
    for path in (ROOT / "tools/history_secrets.py",
                 ROOT / "tests/test_history_secrets.py"):
        assert kinds(path.read_text(encoding="utf-8")) == [], path.name


def test_the_shipped_baseline_reads_and_the_working_tree_is_clean_under_it():
    """The documented green invocation, over this repository.

    `tools/unbounded_calls.py` shipped with no green state anywhere in this
    repository and 38 tests passed over it, because every exit-0 assertion was
    against a tree the test built. This is the test that class does not have.
    """
    baseline = ROOT / "docs/security/history-secrets.json"
    rows = hs.load_baseline(baseline)
    data = json.loads(baseline.read_text(encoding="utf-8"))
    assert len(rows) == len(data["accepted"])
    assert all(row["why"] for row in data["accepted"])

    done = subprocess.run(
        [sys.executable, "tools/history_secrets.py", "--worktree",
         "--baseline", "docs/security/history-secrets.json"],
        cwd=str(ROOT), capture_output=True, text=True, timeout=300)
    assert done.returncode == hs.CLEAN, (done.stdout, done.stderr)
    assert "accepted by the baseline" in done.stdout
