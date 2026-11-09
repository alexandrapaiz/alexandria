"""Is this branch's name the one its seat's charter mandates.

Run with `python3 -m pytest tests/test_branch_prefix.py -q`.

This file exists because of the sixth instance of
`INC-2026-11-02-the-dispatch-prompt-now-instructs-the-branch-prefix-its-own-charter-holds-back`.
The security seat's charter holds its branch prefix at `sec/` on purpose: this
company declares that seat `cadence: semimonthly` in `company.yaml`, and
`semimonthly` is absent from `NO_SELF_CONTINUE` in headquarters'
`runtime/board/api.py`, so moving the prefix to `alexandria-security/` would
connect the seat's own merges to its own continue-wake. The charter fixes the
order: the cadence word lands first, then the prefix moves.

Five runs were handed the forbidden name by the resident runtime's dispatch
prompt and declined it. The sixth created the branch, pushed it and opened a
pull request on it, then caught it during the register check. The hold had
been written down at length and nothing checked it, which is the exact failure
the org rule quoted in every charter calls out: a register needs a gate that
decides something gets written down and a gate that decides something gets
checked before it ships. The hold had the first and not the second.

**What this can and cannot check.** It cannot read
`NO_SELF_CONTINUE`, because HQ's file is absent from a pull request checkout
and a test that needs another repository's disk is a test nobody runs on a
pull request. So it checks the two things that are local and that the breach
actually turned on: the branch a run is standing on against the prefix its
charter mandates, and the charter's prefix line against the charter's own hold
paragraph. Either one alone would have failed this run's branch.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# The charter sentence that mandates the prefix, e.g. "on a branch named
# sec/YYYY-MM-DD". The date placeholder is what distinguishes the mandate from
# the paragraphs that merely discuss other prefixes.
MANDATE = re.compile(r'on a branch named\s+(?P<prefix>[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*)/YYYY-MM-DD')

# The paragraph that says the prefix is deliberately wrong for now. While this
# is present the mandate must still read the held prefix.
HOLD = 'Keep `sec/` for now, and the reason is not style'

# Charters whose branch prefix this file governs, seat name to charter path.
# Only the security seat holds a prefix against its own dispatch today, so it
# is the only row; the shape takes a second seat without changing the tests.
CHARTERS = {'security': 'prompts/security-agent.md'}


def charter_prefix(seat):
    """The branch prefix the seat's charter mandates, read out of the charter
    rather than transcribed, because a transcription is the thing that went
    stale in the five instances before this file existed."""
    text = (ROOT / CHARTERS[seat]).read_text()
    found = MANDATE.search(text)
    assert found, 'no "on a branch named <prefix>/YYYY-MM-DD" sentence in %s' % CHARTERS[seat]
    return found.group('prefix')


def current_branch():
    """The branch this test is running on. `GITHUB_HEAD_REF` is set on a
    pull_request event and names the head branch; `git rev-parse` is the answer
    everywhere else. Returns None when neither is available, which is a
    detached checkout and not a failure."""
    ref = os.environ.get('GITHUB_HEAD_REF')
    if ref:
        return ref
    try:
        out = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                             cwd=ROOT, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):  # pragma: no cover
        return None
    name = out.stdout.strip()
    return None if out.returncode or name in ('', 'HEAD') else name


@pytest.mark.parametrize('seat', sorted(CHARTERS))
def test_the_charters_mandate_is_consistent_with_its_own_hold(seat):
    """A hold paragraph that survives while the mandate moves is the defect the
    hold was written to prevent, arriving through the charter instead of
    through a branch name."""
    text = (ROOT / CHARTERS[seat]).read_text()
    prefix = charter_prefix(seat)
    if HOLD in text:
        assert prefix == 'sec', (
            'the charter still holds `sec/` on purpose but now mandates `%s/`.'
            ' The hold paragraph and the mandate have to move in one commit,'
            ' and the cadence word goes first.' % prefix)
    else:
        assert prefix == 'alexandria-%s' % seat, (
            'the hold paragraph is gone, so the prefix should have moved to'
            ' `alexandria-%s/` and it reads `%s/`' % (seat, prefix))


@pytest.mark.parametrize('seat', sorted(CHARTERS))
def test_a_seat_branch_carries_the_prefix_its_charter_mandates(seat):
    """The check the sixth instance needed. A branch that belongs to this seat
    under any of its historical prefixes must carry the one in force now.

    Branches that belong to another seat, to a human, or to no seat are not
    this test's business: it claims nothing about names it did not select, for
    the same reason `ship_first.py`'s seat filter does not."""
    branch = current_branch()
    if branch is None:
        pytest.skip('detached checkout, so no branch name to judge')
    prefix = charter_prefix(seat)
    known = ('sec', 'alexandria-%s' % seat, seat)
    head = branch.split('/')[0]
    if head not in known:
        pytest.skip('%r is not a %s-seat branch' % (branch, seat))
    assert head == prefix, (
        'this branch is %r and %s mandates `%s/`. If the dispatch prompt handed'
        ' you the other name, the charter is the authority and the prompt does'
        ' not read it.' % (branch, CHARTERS[seat], prefix))


def test_the_mandate_pattern_reads_a_charter_and_not_a_hopeful_substring():
    """Pinned because the first draft of this file matched the first `sec/` in
    the charter, which sits in a paragraph about why the prefix is wrong rather
    than in the sentence that mandates it, so the test passed on a charter
    whose mandate had already moved."""
    assert MANDATE.search('One PR per run on a branch named sec/YYYY-MM-DD: the'
                          ' fixes').group('prefix') == 'sec'
    assert MANDATE.search('this line becomes `alexandria-security/YYYY-MM-DD`'
                          ' and this paragraph goes') is None
    assert MANDATE.search('then on a branch named alexandria-security/YYYY-MM-DD'
                          ' always').group('prefix') == 'alexandria-security'


if __name__ == '__main__':  # pragma: no cover
    sys.exit(pytest.main([__file__, '-q']))
