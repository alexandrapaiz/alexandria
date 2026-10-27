"""Does the ship-first measurement tell a run that lost its work from one that
never had any.

Run with `python3 -m pytest tests/test_ship_first.py -q`.

`tools/ship_first.py` joins the host's audit log to the host's session
transcripts, both of which live under `/srv/asc` and are absent from a pull
request checkout, so every test here builds both in a temporary directory in
the host's exact shapes. Nothing reads `/srv/asc`, for the reason
`test_cron_firing.py` gives: a test that needs the host's disk is a test nobody
runs on a pull request.

Seven states, and the polarity between four of them is the whole point.
`lost` is a defect and the only thing that exits 1. `refused` is the identical
audit row — `exit 1`, no pull request — arrived at without the run completing a
turn, so no rule about the first few turns could have been obeyed. `empty` is a
clean ending with nothing pushed, which is either the thing the rule calls
never acceptable or an ordinary run that merged somebody else's branch, and
this tool cannot tell those apart so it reports a question. `unreadable` is the
two surfaces disagreeing on the turn count, which is what one session id
carrying two runs looks like.

Two regressions from this file's own first draft are pinned below. The turn
index was off by one, because the assistant block that follows user entry k is
turn k+1 and the block before any user entry is turn 1, not turn 0. And
`git -C <dir> push` was not matched at all, so a run that pushed from an
explicit worktree read as a run that never pushed, which is the exact direction
that manufactures a `lost`.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import ship_first as sf  # noqa: E402


def write_audit(tmp, rows):
    path = tmp / 'audit.jsonl'
    with path.open('w') as fh:
        for row in rows:
            fh.write(json.dumps(row) + '\n')
    return path


def run_row(session, agent='alexandria-exo', trigger='message', exit_code=0, turns=10):
    return dict(action='run.end', ts='2026-10-26T12:00:00.000Z', agent=agent,
                session=session, trigger=trigger, exit=exit_code, turns=turns)


def write_transcript(tmp, agent, session, commands, turns, sidechain=()):
    """A transcript in the host's shape: `user` entries advance the turn, and an
    assistant block carries the tool calls made during the turn that follows the
    user entry before it.

    `commands` maps a 1-based turn number to the shell command issued in it."""
    d = tmp / 'projects' / ('-tmp-epito-%s-AbC123' % agent)
    d.mkdir(parents=True, exist_ok=True)
    lines = []
    for turn in range(1, turns + 1):
        cmd = commands.get(turn)
        if cmd is not None:
            lines.append(dict(type='assistant', message=dict(content=[
                dict(type='tool_use', name='Bash', input=dict(command=cmd))])))
        lines.append(dict(type='user', message=dict(content=[
            dict(type='tool_result', content='ok')])))
    for cmd in sidechain:
        lines.append(dict(type='assistant', isSidechain=True, message=dict(content=[
            dict(type='tool_use', name='Bash', input=dict(command=cmd))])))
        lines.append(dict(type='user', isSidechain=True, message=dict(content=[])))
    path = d / ('%s.jsonl' % session)
    with path.open('w') as fh:
        for line in lines:
            fh.write(json.dumps(line) + '\n')
    return path


def collect(tmp, **kw):
    records, _ = sf.collect(projects=str(tmp / 'projects'),
                            audit=str(tmp / 'audit.jsonl'), **kw)
    return {r['session']: r for r in records}


def test_a_push_inside_the_deadline_is_shipped(tmp_path):
    write_audit(tmp_path, [run_row('s1', turns=8)])
    write_transcript(tmp_path, 'alexandria-exo', 's1', {3: 'git push -u origin HEAD'}, 8)
    rec = collect(tmp_path)['s1']
    assert rec['state'] == 'shipped'
    assert rec['push'] == 3


def test_a_push_past_the_deadline_is_late_and_never_an_error(tmp_path):
    write_audit(tmp_path, [run_row('s1', turns=30)])
    write_transcript(tmp_path, 'alexandria-exo', 's1', {22: 'git push'}, 30)
    rec = collect(tmp_path)['s1']
    assert rec['state'] == 'late'
    assert rec['push'] == 22
    assert sf.main(['--all', '--projects', str(tmp_path / 'projects'),
                    '--audit', str(tmp_path / 'audit.jsonl')]) == 0


def test_the_turn_index_is_one_based(tmp_path):
    """The off-by-one this file's first draft had: a tool call made before any
    user entry is turn 1. A measurement that calls it turn 0 flatters every run
    by one turn and would have reported a `shipped` that never happened."""
    write_audit(tmp_path, [run_row('s1', turns=4)])
    write_transcript(tmp_path, 'alexandria-exo', 's1', {1: 'git push'}, 4)
    assert collect(tmp_path)['s1']['push'] == 1


def test_worked_then_died_with_nothing_pushed_is_lost_and_exits_one(tmp_path):
    """The state the rule exists to prevent, and the one this file was written
    for: 2026-10-26, this seat cut at turn 20 one turn before its branch."""
    write_audit(tmp_path, [run_row('s1', exit_code=1, turns=20)])
    write_transcript(tmp_path, 'alexandria-exo', 's1', {13: 'git fetch --unshallow'}, 20)
    rec = collect(tmp_path)['s1']
    assert rec['state'] == 'lost'
    assert 'stayed in the sandbox' in rec['why']
    assert sf.main(['--all', '--projects', str(tmp_path / 'projects'),
                    '--audit', str(tmp_path / 'audit.jsonl')]) == 1


def test_refused_before_a_turn_completed_is_not_a_ship_first_defect(tmp_path):
    """The identical audit row as `lost` — exit 1, nothing pushed — and the
    opposite verdict, because the run never completed a turn. 181 of the 215
    non-pushing failures in the host's record are this, so folding them into
    `lost` would have made the defect look six times larger than it is."""
    write_audit(tmp_path, [run_row('s1', exit_code=1, turns=1)])
    write_transcript(tmp_path, 'alexandria-exo', 's1', {}, 1)
    rec = collect(tmp_path)['s1']
    assert rec['state'] == 'refused'
    assert sf.main(['--all', '--projects', str(tmp_path / 'projects'),
                    '--audit', str(tmp_path / 'audit.jsonl')]) == 0


def test_a_clean_ending_with_nothing_pushed_is_a_question_not_a_verdict(tmp_path):
    write_audit(tmp_path, [run_row('s1', exit_code=0, turns=40)])
    write_transcript(tmp_path, 'alexandria-exo', 's1', {5: 'gh pr merge 12'}, 40)
    rec = collect(tmp_path)['s1']
    assert rec['state'] == 'empty'
    assert 'merged somebody else' in rec['why']
    assert sf.main(['--all', '--projects', str(tmp_path / 'projects'),
                    '--audit', str(tmp_path / 'audit.jsonl')]) == 0


def test_the_two_surfaces_disagreeing_claims_no_reading(tmp_path):
    """A session id carrying two runs is what this looks like, and a turn index
    computed over two concatenated runs is a number rather than a measurement."""
    write_audit(tmp_path, [run_row('s1', turns=20)])
    write_transcript(tmp_path, 'alexandria-exo', 's1', {3: 'git push'}, 55)
    rec = collect(tmp_path)['s1']
    assert rec['state'] == 'unreadable'
    assert rec['push'] is None


def test_an_audit_row_with_no_transcript_is_unseen(tmp_path):
    (tmp_path / 'projects').mkdir()
    write_audit(tmp_path, [run_row('s1', turns=30)])
    rec = collect(tmp_path)['s1']
    assert rec['state'] == 'unseen'
    assert 'not on this filesystem' in rec['why']


def test_a_transcript_with_no_audit_row_is_unseen_and_names_its_seat(tmp_path):
    write_audit(tmp_path, [])
    write_transcript(tmp_path, 'ursa-research', 's9', {2: 'git push'}, 6)
    rec = collect(tmp_path)['s9']
    assert rec['state'] == 'unseen'
    assert rec['agent'] == 'ursa-research'


def test_git_dash_c_push_is_a_push(tmp_path):
    """The second regression from the first draft. `git -C <dir> push` went
    unmatched, so a run that pushed from an explicit worktree read as a run
    that never pushed — the one direction that manufactures a false `lost`."""
    write_audit(tmp_path, [run_row('s1', exit_code=1, turns=12)])
    write_transcript(tmp_path, 'alexandria-exo', 's1',
                     {4: 'git -C /tmp/wt push -u origin HEAD'}, 12)
    rec = collect(tmp_path)['s1']
    assert rec['state'] == 'shipped'
    assert rec['push'] == 4


def test_a_subagents_push_is_not_the_parents_push(tmp_path):
    """Sidechain entries are a subagent's own conversation. They do not advance
    the parent's turn counter and the host's `turns` does not count them, so a
    tool call inside one must not be read as the parent run shipping."""
    write_audit(tmp_path, [run_row('s1', exit_code=1, turns=9)])
    write_transcript(tmp_path, 'alexandria-exo', 's1', {}, 9,
                     sidechain=['git push origin HEAD'])
    rec = collect(tmp_path)['s1']
    assert rec['state'] == 'lost'
    assert rec['push'] is None


def test_pr_create_is_recorded_separately_from_the_push(tmp_path):
    write_audit(tmp_path, [run_row('s1', turns=30)])
    write_transcript(tmp_path, 'alexandria-exo', 's1',
                     {9: 'git push -u origin HEAD', 11: 'gh pr create --draft'}, 30)
    rec = collect(tmp_path)['s1']
    assert (rec['push'], rec['pr']) == (9, 11)


def test_the_deadline_is_a_parameter_and_not_a_fact(tmp_path):
    """"Your first few turns" is prose. The number this tool reads it as is an
    argument, so a charter that changes the deadline does not need the tool
    changed, and a reader can ask what compliance would be at any deadline."""
    write_audit(tmp_path, [run_row('s1', turns=30)])
    write_transcript(tmp_path, 'alexandria-exo', 's1', {15: 'git push'}, 30)
    assert collect(tmp_path, deadline=6)['s1']['state'] == 'late'
    assert collect(tmp_path, deadline=20)['s1']['state'] == 'shipped'


def test_the_self_check_properties_hold_on_a_built_fleet(tmp_path):
    write_audit(tmp_path, [run_row('s%d' % i, turns=30) for i in range(5)])
    for i in range(5):
        write_transcript(tmp_path, 'alexandria-exo', 's%d' % i,
                         {8: 'git push', 10: 'gh pr create --draft'}, 30)
    records, _ = sf.collect(projects=str(tmp_path / 'projects'),
                            audit=str(tmp_path / 'audit.jsonl'))
    assert sf.self_check(records) is True


def test_a_seat_filter_claims_nothing_about_runs_it_did_not_select(tmp_path):
    """The company filter is a prefix match on the agent name, so a run of
    another company's seat with a `lost` in it must not make this company's
    report exit 1."""
    write_audit(tmp_path, [run_row('s1', agent='ursa-pm', exit_code=1, turns=30)])
    write_transcript(tmp_path, 'ursa-pm', 's1', {}, 30)
    args = ['--projects', str(tmp_path / 'projects'), '--audit', str(tmp_path / 'audit.jsonl')]
    assert sf.main(args + ['--company', 'alexandria']) == 0
    assert sf.main(args + ['--all']) == 1
