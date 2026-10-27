#!/usr/bin/env python3
"""The ship-first rule has been in all twelve charters for five weeks and
nothing has ever measured whether a single run obeys it.

    python3 tools/ship_first.py                      # this company, every readable run
    python3 tools/ship_first.py --seat exo
    python3 tools/ship_first.py --all                # the whole portfolio
    python3 tools/ship_first.py --session <id>       # one run, with its reasoning
    python3 tools/ship_first.py --deadline 6         # what counts as "a few turns"
    python3 tools/ship_first.py --self-check         # the four properties, printed
    python3 tools/ship_first.py --json

Exit 1 only when a run is `lost`: it worked past turn one, the provider or the
host ended it non-zero, and it had pushed nothing. That is the single outcome
the rule exists to prevent. Every other state is printed and exits 0, because a
gate that fires on the common case says nothing.

## Why this exists

`prompts/*-agent.md`, the ship-first rule, 2026-09-18, all twelve seats:

> Open the pull request before you do the work, not after. In your first few
> turns, before any substantial thinking: create your branch, make one small
> commit, push it, and open the PR with `gh pr create --draft`.
>
> ... A run that dies at turn 90 with a draft PR open has delivered most of its
> value. The same run with nothing pushed has delivered none of it.

Two claims, and they are separable. The second is a claim about mechanism: that
pushing early retains value when a run is cut. The first is a deadline: "your
first few turns". **Only the second had ever been argued for, by four incidents.
The first had never been checked against a single run**, and this file was
written on 2026-10-26 by a run of the ExO seat whose own predecessor had been
cut at turn 20 with nothing pushed, one turn before it would have created its
branch.

## Where the measurement comes from

The host keeps every run's session transcript at
`/srv/asc/home/.claude/projects/-tmp-epito-<agent>-<rand>/<session>.jsonl`, and
the audit log at `/srv/asc/state/.epito/audit.jsonl` carries one `run.end` row
per run with `session`, `agent`, `trigger`, `exit` and `turns`. The transcript
holds every tool call in order; the audit row holds the verdict. Joined on the
session id they answer a question neither can answer alone: **at which turn did
this run first push, and had it pushed by the time it died?**

A turn is one `user` entry in the transcript. That is not an assumption: over
the 1,106 runs where both surfaces exist, the count of `user` entries equals
the audit row's `turns` exactly on 1,049 of them, and the 57 disagreements are
reported as `unreadable` rather than folded in, because a session id that
carries two runs is what a disagreement looks like and no reading of it is
honest.

## The states, and seven is not padding

Each of these is a different fact about a run, and the three the org cares about
are separated from the four that only look like them.

`shipped`
    Pushed at or before the deadline. The rule, obeyed.

`late`
    Pushed, after the deadline. The run kept its work and missed the clause.
    This is the overwhelming majority and it is **not** an error, which is the
    whole reason this tool does not exit 1 on it. A rule that 99% of runs miss
    is a finding about the rule.

`lost`
    Ended non-zero after turn one with nothing pushed. The run did work and
    none of it reached a reader. This is the only state that exits 1.

`empty`
    Ended zero with nothing pushed. The rule calls ending silently "the one
    outcome that is never acceptable", but a run that only merged somebody
    else's pull request also lands here, and this file cannot tell the two
    apart. Reported as a question with its trigger and turn count attached,
    never as a defect.

`refused`
    Ended non-zero at turn one or before, nothing pushed. **Not a ship-first
    defect**: no rule about the first few turns can be obeyed by a run that
    never completed one. Separating this from `lost` is the point of the state
    list, because the audit log shows both as `exit 1, pr null` and 181 of the
    215 non-pushing failures in the record are this.

`unreadable`
    The transcript's own turn count disagrees with the audit row's. A resumed
    or reused session id looks exactly like this, and a turn index computed
    over two concatenated runs is a number rather than a measurement.

`unseen`
    An audit row with no transcript, or a transcript with no audit row. Not
    having looked and having found nothing are different facts.
"""

import argparse
import collections
import glob
import json
import os
import re
import statistics
import sys

AUDIT = '/srv/asc/state/.epito/audit.jsonl'
PROJECTS = '/srv/asc/home/.claude/projects'
DEADLINE = 6          # "your first few turns", read generously

PUSH = re.compile(r'git\s+(?:-C\s+\S+\s+)?push\b')
PR_CREATE = re.compile(r'gh\s+pr\s+create\b')

# the order a report prints them in, worst first
ORDER = ['lost', 'empty', 'late', 'shipped', 'refused', 'unreadable', 'unseen']


def audit_rows(path=AUDIT):
    """Every `run.end` row that names a session, keyed by session id. A row
    with no session cannot be joined to a transcript and is counted, not used."""
    rows, sessionless = {}, 0
    with open(path) as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get('action') != 'run.end':
                continue
            if d.get('session'):
                rows[d['session']] = d
            else:
                sessionless += 1
    return rows, sessionless


def read_transcript(path):
    """The turn at which this run first pushed and first opened a pull request,
    and its own turn count.

    A turn is one `user` entry. The assistant blocks that follow user entry k
    belong to turn k+1, so a tool call seen before any user entry is turn 1.
    Sidechain entries are a subagent's conversation and are skipped: they do not
    advance the parent's turn counter and the host's `turns` does not count
    them."""
    turn, push, pr = 0, None, None
    try:
        fh = open(path)
    except OSError as why:
        return None, None, None, 'the transcript cannot be read (%s)' % why
    with fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get('isSidechain'):
                continue
            kind = d.get('type')
            if kind == 'user':
                turn += 1
            elif kind == 'assistant':
                for part in (d.get('message') or {}).get('content') or []:
                    if part.get('type') != 'tool_use':
                        continue
                    cmd = (part.get('input') or {}).get('command') or ''
                    if push is None and PUSH.search(cmd):
                        push = turn + 1
                    if pr is None and PR_CREATE.search(cmd):
                        pr = turn + 1
    return turn, push, pr, None


def classify(row, turns_seen, push, deadline):
    """The state, and the sentence that justifies it."""
    exit_code, turns = row.get('exit'), row.get('turns') or 0
    if turns_seen is not None and turns_seen != turns:
        return 'unreadable', ('the transcript counts %d turns and the audit row says %d,'
                              ' which is what one session id carrying two runs looks like'
                              % (turns_seen, turns))
    if push is not None:
        if push <= deadline:
            return 'shipped', 'pushed at turn %d, inside the %d-turn deadline' % (push, deadline)
        return 'late', ('pushed at turn %d, past the %d-turn deadline; the work was kept'
                        ' and the clause was missed' % (push, deadline))
    if exit_code == 0:
        return 'empty', ('ended clean at turn %d having pushed nothing: either a silent'
                         ' ending or a run that only merged somebody else\'s work'
                         % turns)
    if turns <= 1:
        return 'refused', ('ended non-zero without completing a turn, so no rule about'
                           ' the first few turns could have been obeyed')
    return 'lost', ('worked to turn %d, ended exit %s, and pushed nothing: every line of'
                    ' it stayed in the sandbox' % (turns, exit_code))


def collect(deadline=DEADLINE, projects=PROJECTS, audit=AUDIT):
    """One record per run the two surfaces agree exists, plus the ones only one
    of them knows about."""
    rows, sessionless = audit_rows(audit)
    seen, out = set(), []
    for path in sorted(glob.glob(os.path.join(projects, '*', '*.jsonl'))):
        session = os.path.basename(path)[:-len('.jsonl')]
        row = rows.get(session)
        if row is None:
            out.append(dict(session=session, agent=_agent_of_dir(path), trigger=None,
                            exit=None, turns=None, push=None, pr=None,
                            state='unseen', why='a transcript with no `run.end` row:'
                            ' the run has not ended, or its row names no session'))
            continue
        seen.add(session)
        turns_seen, push, pr, unreadable = read_transcript(path)
        if unreadable:
            out.append(dict(session=session, agent=row.get('agent'), trigger=row.get('trigger'),
                            exit=row.get('exit'), turns=row.get('turns'), push=None, pr=None,
                            state='unseen', why=unreadable))
            continue
        state, why = classify(row, turns_seen, push, deadline)
        if state == 'unreadable':
            # A turn index this command has just declared unreadable must not
            # survive on the record, or every statistic below quietly consumes
            # it. The first draft of this file kept it, and `report`'s median
            # first-push turn was computed over 54 runs the same file had
            # already refused to read. A refusal that leaves its number behind
            # is not a refusal.
            push = pr = None
        out.append(dict(session=session, agent=row.get('agent'), trigger=row.get('trigger'),
                        exit=row.get('exit'), turns=row.get('turns'), turns_seen=turns_seen,
                        push=push, pr=pr, state=state, why=why))
    for session, row in rows.items():
        if session in seen:
            continue
        out.append(dict(session=session, agent=row.get('agent'), trigger=row.get('trigger'),
                        exit=row.get('exit'), turns=row.get('turns'), push=None, pr=None,
                        state='unseen', why='an audit row whose transcript is not on this'
                        ' filesystem, so no turn can be read for it'))
    return out, sessionless


def _agent_of_dir(path):
    """`-tmp-epito-alexandria-exo-94mgPy` names a seat, and the suffix the host
    appends is six characters of its own. Used only where no audit row exists to
    say the name authoritatively."""
    name = os.path.basename(os.path.dirname(path))
    m = re.match(r'^-tmp-epito-(.+)-[A-Za-z0-9]{6}$', name)
    return m.group(1) if m else name


def self_check(records):
    """Four properties that must hold if the turn index means what this file
    says it means. Printed rather than asserted, because a number nobody looks
    at is the defect this whole file is about."""
    readable = [r for r in records if r.get('push')]
    lines = []
    bad = [r for r in readable if r['push'] > (r['turns'] or 0)]
    lines.append(('a push cannot happen after the run ended', len(bad), len(readable)))
    both = [r for r in readable if r.get('pr')]
    after = [r for r in both if r['pr'] < r['push']]
    lines.append(('`gh pr create` comes at or after the first push', len(after), len(both)))
    neg = [r for r in readable if r['push'] < 1]
    lines.append(('the first turn is turn 1 and never turn 0', len(neg), len(readable)))
    agreed = [r for r in records if r.get('turns_seen') is not None
              and r['turns_seen'] == r.get('turns')]
    disagreed = [r for r in records if r.get('state') == 'unreadable']
    lines.append(('the two surfaces agree on the turn count',
                  len(disagreed), len(agreed) + len(disagreed)))
    print('SELF-CHECK — violations out of the runs the property applies to')
    for claim, n, total in lines:
        verdict = 'ok' if n == 0 else 'VIOLATED'
        print('  %-8s %4d / %-5d  %s' % (verdict, n, total, claim))
    return all(n == 0 for _, n, _ in lines[:3])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--company', default='alexandria')
    ap.add_argument('--seat')
    ap.add_argument('--all', action='store_true', help='every seat of every company')
    ap.add_argument('--session')
    ap.add_argument('--deadline', type=int, default=DEADLINE)
    ap.add_argument('--projects', default=PROJECTS)
    ap.add_argument('--audit', default=AUDIT)
    ap.add_argument('--self-check', action='store_true')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args(argv)

    records, sessionless = collect(args.deadline, args.projects, args.audit)

    if args.session:
        records = [r for r in records if r['session'] == args.session]
    elif args.seat:
        want = '%s-%s' % (args.company, args.seat)
        records = [r for r in records if r['agent'] in (want, args.seat)]
    elif not args.all:
        records = [r for r in records
                   if (r['agent'] or '').startswith(args.company + '-')]

    if args.json:
        json.dump(dict(deadline=args.deadline, sessionless=sessionless,
                       records=records), sys.stdout, indent=2, sort_keys=True)
        print()
    else:
        report(records, args.deadline, sessionless)
        if args.self_check:
            print()
            self_check(records)

    return 1 if any(r['state'] == 'lost' for r in records) else 0


def report(records, deadline, sessionless):
    if not records:
        print('No run matched. Nothing is claimed about runs this command did not select.')
        return
    counts = collections.Counter(r['state'] for r in records)
    print('%d runs selected. A turn is one `user` entry in the transcript; the deadline'
          ' read from the rule is %d turns.' % (len(records), deadline))
    print()
    for state in ORDER:
        if counts[state]:
            print('  %-11s %4d  %5.1f%%' % (state, counts[state],
                                            100.0 * counts[state] / len(records)))
    if sessionless:
        print('\n  %d `run.end` rows name no session and cannot be joined to a transcript.'
              % sessionless)

    pushed = sorted(r['push'] for r in records if r.get('push'))
    if pushed:
        print('\nFIRST `git push`, over the %d runs that pushed at all' % len(pushed))
        buckets = [('1-3', 1, 3), ('4-6', 4, 6), ('7-10', 7, 10), ('11-20', 11, 20),
                   ('21-40', 21, 40), ('41+', 41, 10 ** 9)]
        for label, lo, hi in buckets:
            n = sum(1 for p in pushed if lo <= p <= hi)
            if n:
                print('  turn %-6s %4d  %5.1f%%' % (label, n, 100.0 * n / len(pushed)))
        print('  median %d   p90 %d   worst %d'
              % (statistics.median(pushed), pushed[int(0.9 * len(pushed))], pushed[-1]))

    cut = [r for r in records if r['state'] in ('lost',)
           or (r.get('push') and r['exit'] not in (0, None) and (r['turns'] or 0) > 1)]
    if cut:
        kept = sum(1 for r in cut if r.get('push'))
        print('\nTHE RULE\'S OWN CLAIM, tested on the %d runs cut non-zero after turn one'
              % len(cut))
        print('  had pushed before dying: %d  (%.0f%%)' % (kept, 100.0 * kept / len(cut)))
        print('  pushed nothing at all:   %d' % (len(cut) - kept))

    by_seat = collections.defaultdict(list)
    for r in records:
        if r.get('push'):
            by_seat[r['agent']].append(r['push'])
    ranked = sorted(((a, v) for a, v in by_seat.items() if len(v) >= 5),
                    key=lambda kv: -statistics.median(kv[1]))
    if ranked:
        print('\nBY SEAT, median first-push turn (five or more pushing runs)')
        for agent, v in ranked:
            print('  %-22s n=%3d  median %3d  worst %3d'
                  % (agent, len(v), statistics.median(v), max(v)))

    lost = [r for r in records if r['state'] == 'lost']
    if lost:
        print('\nLOST — worked, ended non-zero, pushed nothing. This is what exits 1.')
        for r in sorted(lost, key=lambda r: -(r['turns'] or 0)):
            print('  %-22s %-8s turns %-4s  %s'
                  % (r['agent'], r['trigger'], r['turns'], r['session'][:8]))

    empty = [r for r in records if r['state'] == 'empty']
    if empty:
        print('\nEMPTY — ended clean having pushed nothing. A question, not a verdict:'
              '\n  a silent ending and a merge-only run are indistinguishable here.')
        agents = collections.Counter(r['agent'] for r in empty)
        for agent, n in agents.most_common():
            print('  %-22s %3d' % (agent, n))


if __name__ == '__main__':
    raise SystemExit(main())
