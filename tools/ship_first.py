#!/usr/bin/env python3
"""The ship-first rule has been in all twelve charters for five weeks and
nothing has ever measured whether a single run obeys it.

    python3 tools/ship_first.py                      # this company, every readable run
    python3 tools/ship_first.py --seat exo
    python3 tools/ship_first.py --all                # the whole portfolio
    python3 tools/ship_first.py --session <id>       # one run, with its reasoning
    python3 tools/ship_first.py --company Ursa       # the spelling is not load-bearing
    python3 tools/ship_first.py --deadline 6         # the number before §8 settled it
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

**The deadline is settled now, and it is ten.** This file read "a few turns" as
six, measured half of one percent of 1,765 runs against it, and the measurement
went up through `docs/agents/hq-relay.md`. HQ answered in `docs/standards/pm.md`
§8: the draft comes first and the preflight comes after it, because the
preflight the same charters mandate cannot finish inside six turns, and **the
deadline is turn ten**. That section names this tool as the counter for the one
deadline it states. The default here followed it on 2026-11-09 and the `six`
above is kept as a flag, because the two numbers are the before and after of a
rule that got counted and the comparison is the evidence for the amendment.

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

## Selecting runs, and why the spelling used to decide the answer

The host keys an agent in ascii-lowercase, `ursa-exo`. Every other route in the
portfolio spells a company with a capital: the work and capacity routes, the
repository name, the daily brief, and §8 itself. So until 2026-11-09 the one
spelling a reader was most likely to type was the one spelling that selected
nothing, `--company Ursa` returned zero rows against the 945 that `--company
ursa` returns, and the line it printed read as a verdict on the company rather
than on the selector. `select` folds both sides. `report` names the selector
back and prints the keys that do exist, because a reader who matched nothing
cannot otherwise tell an empty company from a mistyped one.

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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import resolve_target  # noqa: E402

AUDIT = '/srv/asc/state/.epito/audit.jsonl'
PROJECTS = '/srv/asc/home/.claude/projects'
DEADLINE = 10         # docs/standards/pm.md §8: "The deadline is turn ten"
HQ = 'alexandra-systems'  # the one company whose keys the host writes unprefixed

# Six was this file's own reading of "your first few turns" on 2026-10-26, when
# the clause was prose and no number had ever been counted against it. The
# counting is what changed it. HQ amended §8 on the measurement this tool
# produced, and the amended section names this tool as the counter for the one
# deadline it states, so a default of six left the instrument disagreeing with
# the standard it serves. The disagreement is not neutral in direction: at six
# the portfolio reads 0.5% shipped, at ten about a tenth, and the standard
# predicts a tenth. A tool whose default makes its own governing rule look
# unobeyed will be read as evidence against the rule.
#
# Found by Ursa's ExO seat, 2026-11-09, which routed the number to HQ on the
# understanding that it was HQ's to set. It was, and HQ had already set it. See
# docs/agents/cross-repo-law.md: the parent governs, and the disagreement
# itself is the finding.

PUSH = re.compile(r'git\s+(?:-C\s+\S+\s+)?push\b')
PR_CREATE = re.compile(r'gh\s+pr\s+create\b')

# the order a report prints them in, worst first
ORDER = ['lost', 'empty', 'late', 'shipped', 'refused', 'unreadable', 'unseen']

ASCII_LOWER = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                            'abcdefghijklmnopqrstuvwxyz')


def fold(name):
    """An agent key in the form the host writes it, which is ascii-lowercase.

    `str.lower()` would do for the keys that exist, and it is not what this
    does, because its job here is to normalize one alphabet rather than to case
    anything. Unicode lowercasing maps characters outside that alphabet in ways
    a selector should not inherit, and an agent key is `ursa-exo`, so an
    ascii-only table says exactly what is meant and leaves everything else
    untouched."""
    return (name or '').translate(ASCII_LOWER)


def owner(agent, roster=None):
    """The company an agent key names, which for HQ's seats is not in the key.

    **This function is the answer to a question this file used to refuse.** The
    docstring below `unprefixed` said of the eight bare keys that every one is
    also an alexandria seat name, "so they are most likely this company's own
    early runs, and `most likely` is not a thing a measurement gets to act on."
    That refusal was right. On 2026-11-09 Ursa's ExO seat measured the thing
    that resolves it, this seat reproduced the measurement, and the answer is
    that the bare keys are HQ's own, so claiming them for a product company
    would have imported 3,504 rows of alexandra-systems' work.

    The evidence is the `pr` field rather than the dates. Of the 128 PR-bearing
    rows on the bare eight, 126 name an `alexandrapaiz/alexandra-systems` pull
    request, and the two exceptions are HQ seats writing into product
    repositories, which is what an HQ seat does. The positive control is what
    makes the absence mean something: all 30 qualified keys that carry a pull
    request name their own company's repository, every row, no exceptions, from
    `alexandria-pm` at 132 of 132 to `ursa-okr` at 3 of 3. And three of the
    eight bare names, `mba`, `yc` and `distribution`, have no qualified
    counterpart under any company on this host, so they cannot be a product
    seat in any spelling. Five of eight being alexandria seat names is a
    coincidence of the roster rather than evidence.

    **So the mechanism is an identity and not an omission.** The host writes a
    seat's own name and prefixes it with the company only for a product
    company. For HQ the seat name is the agent name, so there is nothing to
    prefix.

    Which is why the test is the roster rather than the hyphen. `exo-centralizer`
    is HQ's ninth key, 859 rows, and all 24 of its PR rows name
    alexandra-systems, so it is HQ's by the same identity while looking
    qualified, because that seat's own name carries a hyphen. A hyphen rule
    files those 859 rows under a company called `exo` that does not exist, which
    is what this tool printed among its five companies until this change. Over
    the whole log the roster rule agrees with the `pr` field on 887 of 889
    PR-bearing rows, and the two it misses are the two HQ cross-writes above.

    Returns `None` for a key that names nothing, which is a key with an empty
    half. An unreadable roster falls back to the shape rule rather than
    attributing anything, for the reason
    `test_an_unreadable_roster_refuses_nothing` already gives: a claim built on
    an empty roster is worse than the narrower reading it replaces."""
    key = fold(agent)
    if not key:
        return None
    head, dash, tail = key.partition('-')
    if dash and (not head or not tail):
        # `-pm` and `pm-` each split into a pair with an empty half, and neither
        # half is a name. A key a reader cannot type back names no company.
        return None
    if not dash:
        return HQ
    if roster is None:
        roster = known_companies()
    if not roster:
        return head
    # Longest match rather than the first segment, because one name on the
    # roster has a hyphen in it. `head in roster` can never be true for
    # `alexandra-systems`, since partitioning on the first hyphen yields
    # `alexandra`. No key is written that way today, so this costs nothing now
    # and it is the same defect as `exo-centralizer`: a split on the hyphen
    # meeting a name that contains one. Fixing it here rather than filing it,
    # because this function is the one place that was just rewritten to stop
    # reading the hyphen as a namespace.
    for name in sorted(roster, key=len, reverse=True):
        if key.startswith(name + '-'):
            return name
    return HQ


def seat_key(company, seat):
    """The agent key a named seat of a named company is written under.

    One line, and it is the whole repair on the `--seat` side. HQ's seats are
    written unprefixed, so HQ is the only company whose seat key is the seat
    name, and a product company's seat key always carries its company."""
    if fold(company) == HQ:
        return fold(seat)
    return fold('%s-%s' % (company, seat))


def select(records, company=None, seat=None, session=None, every=False):
    """The runs a selector names, and the selector written back in words.

    **Both sides are folded, and that is the whole of this.** The host keys an
    agent in ascii-lowercase. Every other route in the portfolio spells a
    company with a capital: the work and capacity routes, the repository name,
    the daily brief, and the standard that names this tool as the counter for
    its deadline. So the spelling a reader arrives with was the one spelling
    that selected nothing, and `--company Ursa` returned zero against the 945
    runs `--company ursa` returns.

    The exit code is not folded in, and it is worth knowing why the stakes were
    higher than a confusing line. Ursa's record carries ten `lost` runs, so
    `--company ursa` exits 1 and `--company Ursa` exited 0. A gate wired to the
    capital was green on a fleet that had lost work.

    **The second repair here is the `--seat` branch, and it ran the other
    way.** That branch used to match the bare key as a fallback, and the
    docstring under `unprefixed` called that compensation: one of the two
    selectors reached the historical rows and the other did not. It was not
    compensation. `owner` now says whose those rows are, and they are HQ's, so
    the fallback was importing alexandra-systems' work into every product
    seat's reading of itself. Measured on this host before the change:
    `--company alexandria --seat engineer` returned 1,389 rows of which 1,015,
    or 73.1 per cent, were HQ's engineer seat. Across the five alexandria seats
    whose names HQ also uses, 3,127 of 6,247 selected rows belonged to another
    company, so the seat selector was more than half wrong and in the direction
    that matters least to notice.

    **The report was already contradicting itself about it in print.** Its
    `BY SEAT` block groups on the raw key, so one run of `--seat engineer` put
    `engineer` at median 23 and `alexandria-engineer` at median 15, two rows, as
    two seats, inside a report whose summary had just called them one seat and
    published their merged median of 17. A seat that reads its own first-push
    median off this tool was reading a number four turns worse than its own,
    and the evidence that it was two populations was eleven lines further down
    the same page."""
    if session:
        return ([r for r in records if r['session'] == session],
                'session %s' % session)
    if seat:
        want = seat_key(company, seat)
        return ([r for r in records if fold(r['agent']) == want],
                'seat %s of company %s' % (seat, company))
    if every:
        return list(records), 'every seat of every company'
    roster = known_companies()
    return ([r for r in records if owner(r['agent'], roster) == fold(company)],
            'company %s' % company)


def unprefixed(records):
    """The agent keys the host writes unprefixed, counted. They are HQ's seats.

    **This used to be the open question of this file and it is now a disclosure
    with an answer attached.** The previous text said the eight bare keys were
    "most likely this company's own early runs" and refused to act on a most
    likely, which was the right call: acting on it would have claimed them for
    `--company alexandria`, this tool's default invocation. `owner` carries the
    measurement that closed it on 2026-11-09, and the answer went the other
    way. The bare keys are alexandra-systems' own, so the widening this
    function was holding the door against would have imported 3,504 rows of
    HQ's work and reported them as this company's.

    That direction is the part worth keeping in mind for the next version of
    this question. The error would not have recovered rows the report was
    missing, it would have manufactured them, and a counter that grades
    shipping errs expensively when it errs toward a healthier-looking fleet.

    What this function now means is narrower than what it used to mean. It
    counts the keys with no company in them, which is 8 of HQ's 9 keys and
    exactly the population whose ownership the key itself does not state. HQ's
    ninth, `exo-centralizer`, is unprefixed in the same way and does not look
    it, so it is `owner` and not this count that decides attribution. Nothing
    here is unreachable any more: `--company alexandra-systems` selects all
    nine."""
    counts = collections.Counter()
    for r in records:
        agent = fold(r.get('agent'))
        if agent and '-' not in agent:
            counts[agent] += 1
    return counts


def keys_present(records, company=None, roster=None):
    """The company keys and seat keys the record actually carries.

    Printed when a selector matches nothing, because that is the one moment a
    reader cannot tell a company with no runs from a company spelled another
    way, and the keys are the only thing that answers it.

    Attribution is `owner`'s, which is the fix for two opposite errors this
    function made while splitting on the hyphen. It offered the bare seat keys
    to a reader as nine companies, which the comment it replaces describes. And
    after that was repaired by dropping every bare key, it offered `exo` as the
    fifth of five companies on this host, which is not a company either: it is
    the head of `exo-centralizer`, one of HQ's own seats, and 859 rows were
    filed under it. A reader who typed `--company exo` back got a refusal from
    the roster, which is the good case. A reader who believed the list learned
    the portfolio has a company it does not have."""
    if roster is None:
        roster = known_companies()
    companies, seats = set(), set()
    for r in records:
        who = owner(r.get('agent'), roster)
        if not who:
            continue
        companies.add(who)
        if company is None or who == fold(company):
            seats.add(fold(r.get('agent')))
    return sorted(companies), sorted(seats)


def audit_rows(path=AUDIT):
    """Every `run.end` row that names a session, keyed by session id. A row that
    cannot be joined to a transcript is counted, not used, and the returned
    `unjoined` dict is the whole account of those.

    Two ways a row goes unjoined, and only the first was ever counted. A row
    with no session has nothing to key on: the host writes one when it kills a
    run before a session exists, so `exit=timeout`, `exit=clone` and the
    signal kills all land here with no `turns` either.

    The second is a session id that two rows share, which `rows[...] = d` used
    to resolve by keeping whichever came last. `classify` has always known this
    case exists and calls it `unreadable`, but it only ever saw the survivor,
    so the rows underneath it were neither used nor counted and the report's
    arithmetic did not close against the log. On 2026-11-02 that was 13 rows
    across 9 session ids, every one of them a resumed `pm` run, and the
    overwrite kept the 2-turn continuation over the 16-turn run beneath it.
    Counting them does not make them joinable, it makes them visible."""
    rows, unjoined = {}, {'sessionless': 0, 'superseded': 0}
    with open(path) as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get('action') != 'run.end':
                continue
            if d.get('session'):
                if d['session'] in rows:
                    unjoined['superseded'] += 1
                rows[d['session']] = d
            else:
                unjoined['sessionless'] += 1
    return rows, unjoined


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
    rows, unjoined = audit_rows(audit)
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
    return out, unjoined


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


def known_companies():
    """The companies this portfolio declares, folded.

    Taken from `tools/board.py`'s `KNOWN_COMPANIES` rather than from a second
    list, because `docs/standards/pm.md` §14 makes a company a repository name
    and that is already written down once. **And that list is itself the
    evidence for the fold**: it spells five companies lowercase and `Ursa` with
    a capital, which is the same split between the host's keys and every other
    route that made this defect.

    Imported lazily and never fatally. `board.py` is standard library only, so
    the import is safe, and a tool that measures the host's own disk must not
    stop working because a sibling moved."""
    try:
        from tools import board
    except Exception:
        try:
            import board
        except Exception:
            return set()
    return {fold(c) for c in getattr(board, 'KNOWN_COMPANIES', ())}


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

    # A mistyped company refuses rather than reporting a zero, which is the
    # repair `tools/resolve_target.py` exists for and the sixth instance of the
    # class it was built from. Scoped to the company deliberately: the
    # companies are a closed declared list, and no closed roster of another
    # company's seats exists in this checkout, so `--seat` discloses instead of
    # refusing. Skipped when the roster cannot be read, because a refusal built
    # on an empty roster refuses everything.
    if not args.all and not args.session:
        roster = known_companies()
        if roster:
            code = resolve_target.check(
                'company', fold(args.company), roster,
                hint='The host keys an agent in ascii-lowercase, so the spelling'
                     ' is not what selects; the name is.')
            if code is not None:
                return code

    every, unjoined = collect(args.deadline, args.projects, args.audit)
    records, selector = select(every, company=args.company, seat=args.seat,
                               session=args.session, every=args.all)

    if args.json:
        json.dump(dict(deadline=args.deadline, selector=selector,
                       sessionless=unjoined['sessionless'],
                       superseded=unjoined['superseded'],
                       records=records), sys.stdout, indent=2, sort_keys=True)
        print()
    else:
        report(records, args.deadline, unjoined, selector=selector,
               universe=every, company=None if args.all else args.company)
        if args.self_check:
            print()
            self_check(records)

    return 1 if any(r['state'] == 'lost' for r in records) else 0


def report(records, deadline, unjoined, selector=None, universe=None, company=None):
    if not records:
        print('No run matched %s.' % (selector or 'the selector given'))
        if not universe:
            print('Nothing is claimed about runs this command did not select.')
            return
        # The old line stopped at the sentence above, and the sentence is
        # honest. The trouble is that it reads as a verdict, so a reader
        # concluded the company had no runs rather than that the selector
        # missed. Naming the keys is what tells those two apart, and it is free
        # here because every record is already in hand.
        print('Nothing is claimed about runs this command did not select. That'
              ' is a statement about the selector and not about the company:'
              ' %d runs are on the record, under the keys below, and none of'
              ' them answers to what was asked for.' % len(universe))
        companies, seats = keys_present(universe, company)
        print('\n  companies      %s' % (', '.join(companies) or '(none)'))
        if company is None:
            print('  seats          %d keys, which `--all` selects' % len(seats))
        else:
            print('  %s seats%s%s' % (fold(company), ' ' * max(1, 9 - len(fold(company))),
                                      ', '.join(seats) or '(none)'))
        bare = unprefixed(universe)
        if bare:
            print('  unprefixed     %s' % ', '.join('%s %d' % kv for kv in bare.most_common()))
            print('\n  The last row names seats with no company in the key. Those are'
                  ' HQ\'s own, and `--company %s` selects them.' % HQ)
        return
    counts = collections.Counter(r['state'] for r in records)
    print('%d runs selected. A turn is one `user` entry in the transcript; the deadline'
          ' read from the rule is %d turns.' % (len(records), deadline))
    print()
    for state in ORDER:
        if counts[state]:
            print('  %-11s %4d  %5.1f%%' % (state, counts[state],
                                            100.0 * counts[state] / len(records)))
    if unjoined['sessionless']:
        print('\n  %d `run.end` rows name no session and cannot be joined to a transcript.'
              % unjoined['sessionless'])
    if unjoined['superseded']:
        print('  %d more share a session id with a later row, which is the only one'
              ' above.' % unjoined['superseded'])

    # Two disclosures about the selector itself, because a count is only an
    # answer if the reader knows what it could not reach.
    if company is not None and universe and fold(company) != HQ:
        bare = unprefixed(universe)
        if bare:
            named = ', '.join('%s %d' % kv for kv in bare.most_common())
            print('\n  %d further rows carry an agent key with no company in it (%s).'
                  ' Those are HQ\'s own seats rather than this company\'s, so this'
                  ' selector did not claim them, and `--company %s` is what reads them.'
                  % (sum(bare.values()), named, HQ))
    claimed = unprefixed(records)
    if claimed and company is not None and fold(company) == HQ:
        print('\n  %d of the rows above were selected on an unprefixed key (%s). HQ'
              ' writes its seat name with no company in front of it, so for this one'
              ' company the seat name is the whole key.'
              % (sum(claimed.values()), ', '.join(sorted(claimed))))

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
