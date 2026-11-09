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


def test_every_end_row_is_either_used_or_counted(tmp_path):
    """The report's two numbers are its whole account of the log, so a row that
    is neither selected nor counted is a row a reader cannot reconcile.

    Three rows, one session id shared by two of them. The survivor is joined
    and classified, the sessionless row is counted as before, and the row the
    overwrite buried is counted as `superseded`. Before this, the buried row
    left both numbers untouched and the arithmetic against the log was short by
    one with nothing to explain it. On the host that was 13 rows across 9
    session ids."""
    rows = [run_row('s1', turns=16), run_row('s1', turns=2), run_row('s2', turns=10)]
    del rows[2]['session']
    write_audit(tmp_path, rows)
    write_transcript(tmp_path, 'alexandria-exo', 's1', {3: 'git push'}, 2)
    records, unjoined = sf.collect(projects=str(tmp_path / 'projects'),
                                   audit=str(tmp_path / 'audit.jsonl'))
    assert unjoined == {'sessionless': 1, 'superseded': 1}
    assert len(records) + unjoined['sessionless'] + unjoined['superseded'] == len(rows)
    assert [r['turns'] for r in records] == [2], 'the later row is the one kept'


def test_the_report_says_so_rather_than_leaving_the_reader_to_subtract(tmp_path, capsys):
    write_audit(tmp_path, [run_row('s1', turns=16), run_row('s1', turns=2)])
    write_transcript(tmp_path, 'alexandria-exo', 's1', {3: 'git push'}, 2)
    records, unjoined = sf.collect(projects=str(tmp_path / 'projects'),
                                   audit=str(tmp_path / 'audit.jsonl'))
    sf.report(records, 6, unjoined)
    assert 'share a session id with a later row' in capsys.readouterr().out


def test_the_company_selector_does_not_depend_on_how_the_company_is_spelled(tmp_path):
    """Ursa's ExO seat, 2026-11-09: `--company ursa` returned 945 rows here and
    `--company Ursa` returned none.

    The host keys an agent in ascii-lowercase and every other route in the
    portfolio spells a company with a capital, so the spelling a reader arrives
    with was the one spelling that answered nothing."""
    write_audit(tmp_path, [run_row('s1', agent='ursa-exo', turns=30)])
    write_transcript(tmp_path, 'ursa-exo', 's1', {4: 'git push'}, 30)
    records, _ = sf.collect(projects=str(tmp_path / 'projects'),
                            audit=str(tmp_path / 'audit.jsonl'))
    for spelling in ('ursa', 'Ursa', 'URSA', 'uRsA'):
        got, _note = sf.select(records, company=spelling)
        assert [r['session'] for r in got] == ['s1'], spelling


def test_the_seat_selector_folds_both_halves_of_the_key(tmp_path):
    """`--seat` built its key from both arguments, so either half being
    capitalized lost the run, and the bare-seat fallback lost it too."""
    write_audit(tmp_path, [run_row('s1', agent='ursa-exo', turns=30)])
    write_transcript(tmp_path, 'ursa-exo', 's1', {4: 'git push'}, 30)
    records, _ = sf.collect(projects=str(tmp_path / 'projects'),
                            audit=str(tmp_path / 'audit.jsonl'))
    for company, seat in (('ursa', 'exo'), ('Ursa', 'exo'),
                          ('ursa', 'ExO'), ('Ursa', 'ExO')):
        got, _note = sf.select(records, company=company, seat=seat)
        assert [r['session'] for r in got] == ['s1'], (company, seat)


def test_a_capitalized_company_cannot_turn_a_lost_run_green(tmp_path):
    """The sharp end of the same defect, and worse than a confusing line. Ursa's
    record carries ten `lost` runs, so `--company ursa` exits 1 and `--company
    Ursa` exited 0. A gate wired to the capital was green on a fleet that had
    lost work."""
    write_audit(tmp_path, [run_row('s1', agent='ursa-exo', exit_code=1, turns=30)])
    write_transcript(tmp_path, 'ursa-exo', 's1', {}, 30)
    args = ['--projects', str(tmp_path / 'projects'),
            '--audit', str(tmp_path / 'audit.jsonl')]
    assert sf.main(args + ['--company', 'ursa']) == 1
    assert sf.main(args + ['--company', 'Ursa']) == 1


def test_an_empty_selection_names_the_selector_and_the_keys_that_exist(tmp_path, capsys):
    """"Nothing is claimed about runs this command did not select" is honest and
    it reads as a verdict, so a reader concluded the company had no runs rather
    than that the selector missed. The keys are what tell those apart, and they
    are free to print because every record is already in hand.

    The company here is `epitome`, which the portfolio declares and this
    fixture has no runs for. That is the case the refusal above deliberately
    does not cover and the only case left where an empty answer is the true
    one: a real company, correctly spelled, with nothing on the record."""
    write_audit(tmp_path, [run_row('s1', agent='ursa-exo', turns=30)])
    write_transcript(tmp_path, 'ursa-exo', 's1', {4: 'git push'}, 30)
    args = ['--projects', str(tmp_path / 'projects'),
            '--audit', str(tmp_path / 'audit.jsonl'), '--company', 'Epitome']
    assert sf.main(args) == 0
    out = capsys.readouterr().out
    assert 'No run matched company Epitome' in out
    assert 'about the selector and not about the company' in out
    assert 'ursa' in out, 'the key that does exist has to be printed'


def test_an_empty_selection_prints_the_seats_of_the_company_that_was_asked_for(tmp_path, capsys):
    """A mistyped seat is the other half of the same confusion, so the keys
    printed are scoped to the company the selector named rather than to all of
    them."""
    write_audit(tmp_path, [run_row('s1', agent='ursa-exo', turns=30),
                           run_row('s2', agent='alexandria-pm', turns=30)])
    write_transcript(tmp_path, 'ursa-exo', 's1', {4: 'git push'}, 30)
    write_transcript(tmp_path, 'alexandria-pm', 's2', {4: 'git push'}, 30)
    args = ['--projects', str(tmp_path / 'projects'),
            '--audit', str(tmp_path / 'audit.jsonl'),
            '--company', 'Ursa', '--seat', 'nosuchseat']
    assert sf.main(args) == 0
    out = capsys.readouterr().out
    assert 'No run matched seat nosuchseat of company Ursa' in out
    assert 'ursa-exo' in out
    assert 'alexandria-pm' not in out, 'another company\'s seats answer nothing here'


def test_the_fold_is_ascii_only_and_not_a_unicode_lowercase(tmp_path):
    """The job is normalizing one alphabet rather than casing anything. A
    Unicode lowercase maps characters outside that alphabet in ways a selector
    should not inherit, and an agent key is `ursa-exo`."""
    assert sf.fold('Ursa-ExO') == 'ursa-exo'
    assert sf.fold(None) == ''
    assert sf.fold('İ') == 'İ', 'dotted capital I is left alone'
    assert 'I'.lower() == 'i' and sf.fold('I') == 'i'


def test_the_default_deadline_is_the_number_the_standard_states():
    """`docs/standards/pm.md` §8 says "The deadline is turn ten" and names this
    tool as the counter for it. A default of six left the instrument
    disagreeing with the standard it serves, in the direction that makes the
    standard look unobeyed: 0.5% of the portfolio met six and about a tenth
    meets ten."""
    assert sf.DEADLINE == 10
    standard = (ROOT / 'docs' / 'standards' / 'pm.md').read_text()
    assert 'The deadline is turn ten' in standard
    assert 'tools/ship_first.py' in standard


def test_a_session_selector_is_not_folded(tmp_path):
    """A session id is a uuid the host generated, not a name anybody types, and
    folding it would make two distinct ids collide. The fold is for agent keys
    and stops there."""
    write_audit(tmp_path, [run_row('AbC', turns=30)])
    write_transcript(tmp_path, 'alexandria-exo', 'AbC', {4: 'git push'}, 30)
    records, _ = sf.collect(projects=str(tmp_path / 'projects'),
                            audit=str(tmp_path / 'audit.jsonl'))
    assert [r['session'] for r in sf.select(records, session='AbC')[0]] == ['AbC']
    assert sf.select(records, session='abc')[0] == []


def test_every_selector_says_in_words_what_it_selected(tmp_path):
    """The note is what the empty report prints back, so it has to exist for
    every branch rather than only the one that found the defect."""
    records = []
    assert sf.select(records, session='x')[1] == 'session x'
    assert sf.select(records, company='Ursa', seat='exo')[1] == 'seat exo of company Ursa'
    assert sf.select(records, every=True)[1] == 'every seat of every company'
    assert sf.select(records, company='Ursa')[1] == 'company Ursa'


def test_a_company_the_portfolio_does_not_declare_refuses_instead_of_reporting_zero(tmp_path, capsys):
    """The sixth instance of the confident-zero class
    (`INC-2026-11-02-the-confident-zero-class-was-measured-in-three-more-tools-and-two-sweeps-had-covered-four-of-fifty-six`),
    and the repair that incident shipped is the one used here: exit 4, the
    value named, the roster printed."""
    write_audit(tmp_path, [run_row('s1', agent='ursa-exo', turns=30)])
    write_transcript(tmp_path, 'ursa-exo', 's1', {4: 'git push'}, 30)
    args = ['--projects', str(tmp_path / 'projects'),
            '--audit', str(tmp_path / 'audit.jsonl')]
    assert sf.main(args + ['--company', 'ursa']) == 0
    assert sf.main(args + ['--company', 'Ursa']) == 0
    code = sf.main(args + ['--company', 'ursaa'])
    assert code == sf.resolve_target.EXIT_UNKNOWN_TARGET
    err = capsys.readouterr().err
    assert "'ursaa' is not a company this repository carries" in err
    assert 'ursa' in err, 'the refusal prints the roster'


def test_the_roster_the_refusal_uses_is_the_one_the_board_already_declares():
    """Written down once. §14 makes a company a repository name and
    `tools/board.py` already carries that list, so a second list here would be
    a second thing to keep in step. The list is also the evidence for the fold:
    it spells `Ursa` with a capital and five others lowercase."""
    from tools import board
    assert 'Ursa' in board.KNOWN_COMPANIES
    assert 'alexandria' in board.KNOWN_COMPANIES
    assert sf.known_companies() == {sf.fold(c) for c in board.KNOWN_COMPANIES}
    assert 'ursa' in sf.known_companies()


def test_a_bare_agent_key_is_disclosed_and_never_claimed_for_a_company(tmp_path, capsys):
    """The host writes HQ's seat name with no company in front of it, so a
    product company's selector must not claim one. This was already the
    behaviour of the `--company` branch when the owner of those rows was an
    open question, and it is still the behaviour now that the answer is known,
    which is the half of this change that did not move."""
    write_audit(tmp_path, [run_row('s1', agent='alexandria-pm', turns=30),
                           run_row('s2', agent='pm', turns=30)])
    write_transcript(tmp_path, 'alexandria-pm', 's1', {4: 'git push'}, 30)
    write_transcript(tmp_path, 'pm', 's2', {4: 'git push'}, 30)
    args = ['--projects', str(tmp_path / 'projects'),
            '--audit', str(tmp_path / 'audit.jsonl'), '--company', 'alexandria']
    assert sf.main(args) == 0
    out = capsys.readouterr().out
    assert '1 runs selected' in out
    assert 'agent key with no company in it (pm 1)' in out
    assert "HQ's own seats rather than this company's" in out
    assert '--company alexandra-systems' in out, 'and the reader is told where they are'


def test_a_product_seat_selector_does_not_import_hqs_seat_of_the_same_name(tmp_path):
    """The bug this replaces, and it ran the opposite way to the one the file
    was guarding against. `--seat` matched the bare key as a fallback, so every
    product company's reading of a seat whose name HQ also uses carried HQ's
    rows. On this host `--company alexandria --seat engineer` returned 1,389
    rows of which 1,015 were HQ's, and five alexandria seats were over half
    another company's work.

    Both halves are asserted, because the repair is not simply narrower: the
    rows are real and they belong to somebody, so HQ's own selector has to
    reach them."""
    write_audit(tmp_path, [run_row('s1', agent='alexandria-engineer', turns=30),
                           run_row('s2', agent='engineer', turns=30)])
    write_transcript(tmp_path, 'alexandria-engineer', 's1', {4: 'git push'}, 30)
    write_transcript(tmp_path, 'engineer', 's2', {4: 'git push'}, 30)
    records, _ = sf.collect(projects=str(tmp_path / 'projects'),
                            audit=str(tmp_path / 'audit.jsonl'))
    got, _n = sf.select(records, company='alexandria', seat='engineer')
    assert [r['session'] for r in got] == ['s1'], "HQ's engineer is not ours"
    got, _n = sf.select(records, company='alexandra-systems', seat='engineer')
    assert [r['session'] for r in got] == ['s2'], 'and it is not nobody\'s either'


def test_hqs_company_selector_reaches_every_one_of_its_keys(tmp_path):
    """`--company alexandra-systems` returned zero rows and printed
    `alexandra-systems seats (none)` three lines above a row counting 653
    unowned ones. The two lines were the question and its answer, printed
    adjacent and rendered as unrelated.

    `exo-centralizer` is in here because the hyphen is not the test. It is
    HQ's ninth key and all 24 of its PR-bearing rows name alexandra-systems,
    so a rule that reads the head as the company files 859 rows under a
    company called `exo`."""
    write_audit(tmp_path, [run_row('s1', agent='pm', turns=30),
                           run_row('s2', agent='exo-centralizer', turns=30),
                           run_row('s3', agent='alexandria-pm', turns=30)])
    for agent, session in (('pm', 's1'), ('exo-centralizer', 's2'),
                           ('alexandria-pm', 's3')):
        write_transcript(tmp_path, agent, session, {4: 'git push'}, 30)
    records, _ = sf.collect(projects=str(tmp_path / 'projects'),
                            audit=str(tmp_path / 'audit.jsonl'))
    got, _n = sf.select(records, company='alexandra-systems')
    assert sorted(r['session'] for r in got) == ['s1', 's2']
    got, _n = sf.select(records, company='alexandria')
    assert [r['session'] for r in got] == ['s3']


def test_the_owner_of_a_key_is_decided_by_the_roster_and_not_by_the_hyphen():
    """The rule, stated once. A key whose head is a declared company belongs to
    that company, and every other key that names anything at all is HQ's,
    because HQ is the one company the host writes unprefixed. Over this host's
    log the rule agrees with the `pr` field on 887 of 889 PR-bearing rows, and
    the two exceptions are HQ seats writing into product repositories."""
    roster = {'alexandria', 'ursa', 'alexandra-systems'}
    assert sf.owner('alexandria-pm', roster) == 'alexandria'
    assert sf.owner('URSA-ExO', roster) == 'ursa', 'and the fold still applies'
    assert sf.owner('pm', roster) == 'alexandra-systems'
    assert sf.owner('exo-centralizer', roster) == 'alexandra-systems'
    assert sf.owner('-pm', roster) is None, 'a key with an empty half names nothing'
    assert sf.owner('pm-', roster) is None
    assert sf.owner('', roster) is None
    assert sf.owner(None, roster) is None


def test_a_company_whose_own_name_has_a_hyphen_is_matched_whole():
    """The defect this change just removed, waiting one level down inside the
    fix for it. `alexandra-systems` is on the roster and contains a hyphen, so
    partitioning a key on its first hyphen yields `alexandra`, which is on no
    roster, and a membership test on that can never be true. The host writes no
    key in this shape today, which is the only reason it was free to fix: the
    cost of finding it later is the cost of `exo-centralizer`, which is the
    same split meeting the same kind of name."""
    roster = {'alexandria', 'alexandra-systems'}
    assert sf.owner('alexandra-systems-pm', roster) == 'alexandra-systems'
    assert sf.owner('alexandria-pm', roster) == 'alexandria', 'and the short name still wins its own key'
    # `alexandra-pm` matches no roster name, so it lands on HQ by the ordinary
    # rule. Asserted through `sf.HQ` rather than by its value, because HQ's name
    # is `alexandra-systems` and writing that string here would read as a match
    # on the roster when it is the opposite.
    assert sf.owner('alexandra-pm', roster) == sf.HQ
    assert 'alexandra' not in roster, 'which is what makes the line above a fallthrough'


def test_an_unreadable_roster_attributes_nothing_to_hq():
    """The attribution rests on the roster being readable, so an empty roster
    falls back to the shape rule rather than sweeping every hyphenated key it
    cannot check into HQ. Same reason
    `test_an_unreadable_roster_refuses_nothing` exists: a claim built on an
    empty roster is worse than the narrower reading it replaces.

    A bare key is the exception and stays HQ's, because that attribution comes
    from the `pr` field rather than from the roster."""
    assert sf.owner('nosuchco-pm', set()) == 'nosuchco'
    assert sf.owner('pm', set()) == 'alexandra-systems'


def test_unprefixed_counts_the_keys_the_host_writes_with_no_company_in_them():
    """Renamed with the behaviour. This used to be called "the keys no company
    selector can reach", which stopped being true the moment
    `--company alexandra-systems` reached them."""
    assert sf.unprefixed([{'agent': 'alexandria-pm'}, {'agent': 'pm'},
                          {'agent': 'PM'}, {'agent': None},
                          {'agent': 'engineer'}]) == {'pm': 2, 'engineer': 1}


def test_all_and_session_are_not_subject_to_the_company_roster(tmp_path):
    """`--all` names no company and `--session` names a run directly, so
    neither can be refused for a company it never asked about. The default
    value of `--company` is still `alexandria` on both paths and must not
    become a gate on them."""
    write_audit(tmp_path, [run_row('s1', agent='nosuchco-pm', turns=30)])
    write_transcript(tmp_path, 'nosuchco-pm', 's1', {4: 'git push'}, 30)
    args = ['--projects', str(tmp_path / 'projects'),
            '--audit', str(tmp_path / 'audit.jsonl')]
    assert sf.main(args + ['--all']) == 0
    assert sf.main(args + ['--session', 's1']) == 0


def test_an_unreadable_roster_refuses_nothing(tmp_path, monkeypatch):
    """A refusal built on an empty roster refuses every name, which is strictly
    worse than the confident zero it replaces. So the gate is skipped when the
    roster cannot be read rather than defaulting closed."""
    monkeypatch.setattr(sf, 'known_companies', lambda: set())
    write_audit(tmp_path, [run_row('s1', agent='ursa-exo', turns=30)])
    write_transcript(tmp_path, 'ursa-exo', 's1', {4: 'git push'}, 30)
    args = ['--projects', str(tmp_path / 'projects'),
            '--audit', str(tmp_path / 'audit.jsonl'), '--company', 'anything']
    assert sf.main(args) == 0


def test_no_key_is_ever_offered_to_a_reader_as_a_company_that_does_not_exist(tmp_path, capsys):
    """Two defects in this function's output, in opposite directions, both
    caught by running it rather than by reading it.

    The first: the key list split on `-` unconditionally, so the live run
    printed the nine bare seat keys among the companies, which are the keys the
    same change had just finished disclosing as not companies. The second
    arrived with the repair for the first, which dropped every bare key and
    then printed `exo` as the fifth of five companies. `exo` is the head of
    `exo-centralizer`, one of HQ's seats, and 859 rows sat under it. So a reader
    was offered a company the portfolio does not have, twice, by two different
    readings of the same hyphen.

    Both keys now resolve to the company that actually ran them, and the
    assertion is on the absences as well as the presences, because the thing
    that went wrong both times is a name appearing in a list of companies."""
    write_audit(tmp_path, [run_row('s1', agent='ursa-exo', turns=30),
                           run_row('s2', agent='pm', turns=30),
                           run_row('s3', agent='exo-centralizer', turns=30)])
    for agent, session in (('ursa-exo', 's1'), ('pm', 's2'),
                           ('exo-centralizer', 's3')):
        write_transcript(tmp_path, agent, session, {4: 'git push'}, 30)
    records, _ = sf.collect(projects=str(tmp_path / 'projects'),
                            audit=str(tmp_path / 'audit.jsonl'))
    companies, _seats = sf.keys_present(records, roster={'ursa', 'alexandra-systems'})
    assert companies == ['alexandra-systems', 'ursa']
    assert 'pm' not in companies, 'pm names a seat, not a company'
    assert 'exo' not in companies, 'and neither does the head of exo-centralizer'
    assert '' not in companies, 'and an empty name is not a key at all'
    args = ['--projects', str(tmp_path / 'projects'),
            '--audit', str(tmp_path / 'audit.jsonl'), '--company', 'Epitome']
    assert sf.main(args) == 0
    out = capsys.readouterr().out
    assert 'companies      alexandra-systems, ursa' in out
    assert 'unprefixed     pm 1' in out
    assert '`--company alexandra-systems` selects them' in out


def test_a_malformed_agent_key_is_not_read_as_a_company(tmp_path):
    """`-pm` and `pm-` both split into a pair with an empty half, and neither
    half is a name. Dropped rather than printed, because a key list a reader
    cannot type back is worse than a shorter one."""
    got, _ = sf.keys_present([{'agent': '-pm'}, {'agent': 'pm-'},
                              {'agent': 'ursa-exo'}, {'agent': ''},
                              {'agent': None}])
    assert got == ['ursa']


def test_the_company_flag_is_declared_probeable_and_refuses_before_reading_the_disk():
    """`tools/target_census.py` exempted this flag from its probe on the ground
    that it "reaches the board API", which was never true of this file. The
    exemption is gone because the refusal now happens before `collect()` reads
    a byte, so the probe costs 0.36s rather than the whole corpus.

    Pinned here as well as in the census because the ordering is the property:
    a roster check placed after `collect()` would pass every test in this file
    and still be unprobeable."""
    from tools import target_census
    j = target_census.DECLARED[('ship_first.py', '--company')]
    assert j.kind == 'roster'
    assert j.offline == '', 'the board exemption was built on a false cause'
    assert ('ship_first.py', '--company') in target_census.roster_flags(probeable=True)
    # Asserted on the source rather than on a timing, because a wall-clock
    # bound on a shared host is a flake. Both anchors are checked for presence
    # first, so a rename fails this test with its own sentence instead of
    # raising ValueError out of `index`.
    src = (ROOT / 'tools' / 'ship_first.py').read_text()
    guard, read = 'resolve_target.check', 'unjoined = collect('
    assert guard in src and read in src, 'both anchors moved; re-pin this test'
    assert src.index(guard) < src.index(read), \
        'the roster check has to run before the corpus is read, or the probe hangs'


def test_the_json_output_names_the_selector_it_used(tmp_path, capsys):
    """`--json` is a published surface and the selector is now part of what a
    reader needs to interpret it: the same record set means something different
    depending on what was asked for, and before this the json said only the
    deadline."""
    write_audit(tmp_path, [run_row('s1', agent='ursa-exo', turns=30)])
    write_transcript(tmp_path, 'ursa-exo', 's1', {4: 'git push'}, 30)
    args = ['--projects', str(tmp_path / 'projects'),
            '--audit', str(tmp_path / 'audit.jsonl'),
            '--company', 'Ursa', '--json']
    assert sf.main(args) == 0
    got = json.loads(capsys.readouterr().out)
    assert got['selector'] == 'company Ursa', 'the spelling as given, not folded'
    assert got['deadline'] == 10
    assert [r['session'] for r in got['records']] == ['s1']
