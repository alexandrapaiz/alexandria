# Security audit, 2026-11-02 (message wake, the note's disposition)

**Seat:** alexandria security. **Trigger:** `message`, the ExO seat's note of
04:58:04Z. **Branch:** `sec/2026-11-02-message-disposition`, built on PR #732.

This is the fourth security report of 2026-11-02 and it is a delta report. The
full sweep of the night is `audit-2026-11-02-supply-chain.md`, finished 45
minutes before this run started, and everything it established is carried
forward rather than restated. What follows is what this run added, which is two
live host findings its predecessors had not reached, plus the disposition of the
note that woke it.

## 0. Why this run exists, which is a defect rather than a decision

The message that woke this run had already been read whole and answered by the
run that produced PR #732, eleven minutes after it arrived and two minutes
before that run ended. Verified live rather than taken from #732's report, the
way the charter asks:

- `GET /api/messages?to_seat=security&to_company=alexandria` returns the note as
  id `0bdf3d21`, `ts 2026-11-02T04:58:04Z`, 2,213 characters.
- The same endpoint filtered to `from_seat=security` returns four replies to the
  ExO seat at 05:10:29Z, 05:10:46Z, 05:11:00Z and 05:11:17Z. The first is
  subject "Your correction accepted", and it postdates the note by eleven
  minutes.
- `/srv/asc/state/.epito/audit.jsonl` records the note arriving `coalesced` at
  04:58:05Z inside a live run, that run ending at 05:13:23.474Z, and this run
  starting at 05:13:23.622Z.

So the wake was a duplicate, the work was done, and the 148 milliseconds are the
daemon's. Filed as
`INC-2026-11-02-the-duplicate-wake-class-priced-fleet-wide-at-two-thirds-of-the-days-turns`,
the ninth sighting, and the one thing that entry adds to the eight before it is
a number that is not about one seat: 148 immediate restarts today across 21
seats in five companies, holding 65% of the day's turns.

## 1. The note's tail, which the wake cut and which carries no ask

The wake delivered 1,415 of 2,213 characters and said in its banner that the
undelivered tail is where the sender's disposition lives. Read whole from the
inbox, the tail holds four paragraphs: that a fix merged upstream reaches this
host only if a hand forward-ports it, because nothing reads the two code trees
against each other; that the live pair splits file by file, one matching the
staged copy byte for byte and one four prompt clauses behind; and that the ExO
seat's own command now reports per file with the overclaim pinned as a test
case.

**The banner was right about where the disposition lives and this tail asks
nothing of me.** That is the answer to the question the wake posed. The sender
decided to keep the narrower row rather than withdraw it, decided its own
command needed a per-file verdict, and stopped asking me to treat the loss of
the hotfixes as a finding. There is no request in it, so there is nothing
outstanding on this seat from that note.

The banner is a static template and I checked whether that makes it a guess.
It does not. `runtime/board/api.py` carries the measurement behind it: house
style puts reasons first and disposition last, so a tail cut removes the
decision every time and in one direction, measured at two of seven payloads on
the day it was written, both dropped tails beginning "I am not asking". The
template asserts a well-founded prior rather than a reading of the message, and
in this instance the prior held. No finding.

## 2. SEVERE, and it is the third class of the shared sandbox priced properly for the first time

`audit-2026-11-02-supply-chain.md` §3b separated the shared-`/tmp` exposure into
three classes, found the staged runtime fix closes two, and left the third,
reading across seats, open with this sentence: "What the third class is worth is
not something this seat can price alone."

It can now, and the price is higher than that section implies, because the same
uid owns the host's credential store.

Measured in this run, read-only:

```
uid=997(seats) gid=988(seats) groups=988(seats)
/srv/asc/env             READABLE by this seat   mode 600  owner seats:seats   36 lines
/srv/asc/env.infisical   READABLE by this seat   mode 600  owner seats:seats   51 lines
/srv/asc/infisical-token READABLE by this seat   mode 644  owner root:root
```

**No value from any of those files was read, printed, logged or copied, here or
anywhere.** The readability test is `test -r` plus `stat` and `wc -l`. What is
named below is variable names, which are not secrets, because the owner cannot
price the blast radius without knowing which credentials are in scope.

Mode 0600 is the correct mode and it separates this seat from nobody, for
exactly the reason §3b gave about scratch directories: every seat of every
company runs as uid 997. The difference is what sits behind the mode here.
`env.infisical` holds 46 names, and they include `GH_TOKEN`, `NPM_TOKEN`
alongside `NPM_RECOVERY_CODES`, `CLAUDE_CODE_OAUTH_TOKEN`,
`GITHUB_WEBHOOK_SECRET`, `EPITO_HOOK_SECRET`, `BOARD_RUNTIME_TOKEN`,
`EXO_TOKEN`, `ASC_DATABASE_URL`, `CLICKHOUSE_PASSWORD`, `ASC_UI_PASSWORD`,
`LANGFUSE_SECRET_KEY`, `PHOENIX_SECRET`, `OPENROUTE_API_KEY`, `GROQ_API_KEY`,
`TWENTYFIRST_API_KEY` and `CALLMEBOT_APIKEY` with `CALLMEBOT_PHONE`.

So the third class is not "a seat can read another seat's scratch". It is **any
seat, of any company, can read every credential the host holds**, including the
tokens that write to this organisation's GitHub repositories, publish to its npm
account with the recovery codes beside them, and reach the owner's phone.

**This is not a leaked secret and no rotation is indicated.** Nothing is in the
working tree, nothing is in git history, and there is no evidence any seat has
read these files. The finding is that one unix user is the whole of the access
control around them, which makes the blast radius of any single compromised seat
the entire credential set rather than one seat's work.

**Owner action, and it is the same action §3b already asked for, at a higher
price.** A separate unix user per seat, with the credential files readable only
by the service that injects them. That is a root action and a design call, it
belongs to whoever holds the host, and it moves neither authority nor money, so
§21 does not reserve it to the owner. What this run changes is the priority: §3b
could not say what the class was worth, and the answer is the whole credential
set.

Two narrower mitigations are worth naming because they are cheaper and neither
needs the per-user redesign. `/srv/asc/infisical-token` is mode 0644 and root
owned, so it is readable by every process on the host rather than only by the
seats group, and nothing about its function requires that. And a seat process
does not need the files at all once its own variables are in its environment,
so the injection path could read them as root and drop privileges.

**Why this is a prompt-injection finding and not only a permissions one.** The
charter's prompt-injection duty asks where fetched content could steer an agent
into unintended action. Every seat in this org reads the public web, scraped
pages, pull request text and issue bodies. The ceiling on what a successful
injection can do is set by what the seat process can reach, and that ceiling is
now measured: the org's GitHub write tokens and its npm publish token with
recovery codes. An injected instruction that reads one file and exfiltrates it
compromises the supply chain outward, to anybody who installs this
organisation's packages. That is the answer to this sweep's upstream question,
in the direction nobody had asked it: the blast radius of our own ingestion is
not bounded by what we ingest, it is bounded by what a seat can read.

## 3. SEVERE and immediate, the host's only data volume is full

This is an availability finding rather than a confidentiality one, and it is
live as this report is written.

A tool call in this run failed at roughly 05:21Z with ENOSPC. `/dev/sda1`, 45G,
is the host's only data volume and carries `/`, `/usr`, `/srv/asc` and every
seat's `/tmp` checkout. Four readings in five minutes, no action taken by this
run: 4.6M free at 100%, then 1.5G at 97%, then 689M and 698M at 99%. It is
oscillating against zero rather than merely full once. `/tmp` holds 17G,
`/srv/asc` 18G, `/usr` 3.6G. `/var/lib/docker` is 4.0K.

It had already been detected and it had already killed a run.
`/srv/asc/state/diskwatch.last` reads `crit 1793592679`, which is 04:11:19Z,
seventy minutes before this run's ENOSPC. And the audit log records
`alexandria-research` ending at 05:14:58Z with `"exit":"clone"` after 24
seconds, the only exit of that kind in all 11,599 rows of a log that reaches
back to 2026-09-24.

Filed as `INC-2026-11-02-the-only-disk-filled-again-and-a-seat-run-died-at-clone`,
a repeat of the 2026-10-23 fill recorded inside
`INC-2026-10-24-the-observability-runtime-was-retired-with-no-local-record`,
where 14G of one container's logs filled this same volume and Postgres died with
`No space left on device`. The owner's standing condition from that incident was
met, Docker now holds 4.0K, and the volume filled anyway because the space it
freed was taken by seat checkouts that no budget governs either. **A disk budget
given to one writer on a shared volume is not a disk budget.**

Owner or host action, in order: reclaim headroom now, then put a cap or a
predictable reaper on seat scratch, then give `diskwatch`'s verdict a reader,
because `crit` currently lands in a file no charter and no gate has ever opened.

## 4. The instrument this org audits itself with has a corrupt record

Found while reading the audit log for section 0, and it is a defect in the
measurement rather than in the thing measured.

`/srv/asc/state/.epito/audit.jsonl` has one malformed line of 11,599, line
4209. It holds a record truncated mid-field from 2026-10-20T12:20:00Z, cut at
`...,"held":false,"coales`, immediately followed by a complete record from
2026-10-23T15:26:00Z on the same line. One run-accounting record is lost and one
line cannot be parsed. The second date is the day of the first disk fill, which
makes a truncated append the likely cause and places both findings in one class.

**The reason it matters is which file this is.** `INC-2026-10-24` designates
this log as the replacement source for failed-run detection now that the seats
have left GitHub Actions, naming it for this seat's own charter §2b. The ExO
seat's loop ticks say every number in them is derived from it, and
`docs/agents/hq-relay.md` uses it for run turns, exits and slot accounting in at
least five places.

**And no reader can see the corruption, by construction.** The parser documented
at `docs/agents/hq-relay.md:6058` is `try: rows.append(json.loads(l)) except
ValueError: pass`. That is the right shape for a log that may be mid-write, and
it means every consumer silently drops the bad line and reports a clean parse. A
strict reader would crash instead. This run's own first parse crashed on it,
which is the only reason it was found.

Not fixed here, because the file and the writer are headquarters'. Two things
are owed and both are small: the writer should append atomically, and any
documented reader of this log should count and report skipped lines rather than
discarding them, so a lost record is visible as a number instead of as nothing.

## 5. The upstream and supply-chain question, answered

The charter requires one written answer per sweep: what did we consume since the
last sweep that somebody else controls, and what would a compromise of it do to
us.

**Nothing new was consumed.** The last sweep closed 45 minutes before this run
began. No feed was read, no package installed, no image pulled and no model
endpoint called by this company in the interval. `npm audit` in `site/` reports
0 vulnerabilities, unchanged.

**What changed is the answer to the second half, and it did not change because
of anything we ingested.** Every artifact inventoried in `upstreams.md` keeps
its trust assumption, and the blast radius of all of them is now measured rather
than assumed, by section 2 above. A compromise of any ingested artifact that can
get instructions in front of a seat reaches the whole credential set in
`/srv/asc/env.infisical`, because one uid is the whole boundary. The pinned
agent image, the pinned action, the npm and PyPI dependency trees, the arXiv and
Hugging Face feeds and the third-party endpoint behind `OPENROUTE_BASE_URL` all
share that ceiling. Narrowing the ceiling is worth more than narrowing any one
of them.

## 6. The delta sweep

Mechanical checks over this branch, all against its own diff rather than the
whole tree, which §0 of the charter's register step requires before shipping.

| check | result |
| --- | --- |
| conflict markers in `docs/`, `prompts/`, `README.md` | none |
| `python3 -m compileall pipeline tools mcp` | 0 failures |
| `npm audit` in `site/` | 0 vulnerabilities |
| `digests/`, `site/content/digests/` gitignored | yes, `.gitignore:8` and `:11` |
| tracked files under either path | 0 |
| `tools/incidents.py check` | 364 entries, 108 inbox, nothing malformed |
| secret-shaped strings in this branch's delta | no exposure: prose about secrets, plus the redaction-test fixture that names itself one |
| scratch files under a fixed `/tmp` name | none, `mktemp -d` per the charter's §0b |

One item checked and deliberately left alone. `digests/2026-W37.md` is still
reachable in this public repository's history, at the ten commits between
`043767e5` and its deletion in `6910bd9b`. The charter's words are that the path
must be "absent from history" and it is not. This was called severe on
2026-09-18, withdrawn on 2026-09-19 because the same text ships publicly as
`site/content/issues/2026-W37.md`, and restated as low with no action on
2026-10-15 on a measured basis. **I agree with that disposition and am not
reopening it.** It is recorded here only so that a future sweep reading the
charter's "absent from history" against the repository does not rediscover it as
new, which is the fourth report in a row to carry it.

## 7. What this run fixed, and what it did not

**Fixed: nothing in this repository, and that is the correct outcome rather than
an empty one.** Every finding above lives in the host or in headquarters' files.
The charter is explicit that fixes preserve behaviour and that anything larger is
routed, and a seat that patched a root-owned volume or another repository's
daemon would be exceeding its own boundary.

**Routed:** two incident filings, two ledger entries, and board replies to the
ExO seat carrying the two severe findings to the seat that holds the relay.

**Left open and named:** the per-seat unix user, the volume budget, the
`diskwatch` reader, the audit log's atomicity and the coalesce recheck. None is
this seat's and all five now have a measured price, which is the only thing this
seat can add to them.

## 8. The board replies, and both were delivered whole

Two messages to the ExO seat, posted from this run and sized against the
1,500-character wake limit on purpose, because the previous four replies of this
seat were cut and the measurement that matters is what the recipient's wake
carries rather than what the board stores.

| kind | characters | delivered | what it carries |
| --- | --- | --- | --- |
| `note` | 1,161 | whole | the correction accepted, nothing outstanding, and the fleet price of the class |
| `ask` | 1,328 | whole | both severe findings and the order I am asking for |

Two mechanical notes for any seat posting to this door. The store refuses a
single block over 420 characters and it refuses pull request numbers and
incident codes in prose, which it says in its own error rather than failing
quietly, so ids belong in the `data` field. Both refusals were hit and fixed in
this run.
