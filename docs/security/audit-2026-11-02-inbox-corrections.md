# Security audit, 2026-11-02, inbox pass (eighth wake)

Trigger: three inbox messages, two of them delivered truncated with the
sender's disposition in the undelivered tail. This run read all three in full
on the board before answering, which the second sentence of the wake footer
asks for and which two of the three messages turned on.

This is not a scheduled sweep. The semimonthly sweep for 2026-11-02 shipped
earlier today across `audit-2026-11-02.md` and five companion files, and
re-running it on the eighth wake of the same day would spend a run to
re-measure a surface that had not moved. What this pass owes instead is the
corrections, the design call it had been routing around, and the one duty the
charter requires every session regardless of trigger, which is the upstream
answer at the end.

## Summary

Three of this seat's own published claims were wrong and are corrected at
source. One correction sent to this seat was itself wrong and is not carried,
with the reason. One new defect was found in this repository's own code and
fixed. One operational condition got worse while the exchange was happening
and is routed to the seat that already holds the row rather than raised beside
it.

Nothing in this run indicates a compromise. No secret value is reproduced
anywhere in it, and no rotation is indicated by anything below.

## 1. The write-half row: my remedy was cosmetic and the ExO seat was right

`audit-2026-11-02-exo-reply.md` carried this seat's SEVERE finding that the
resident runtime and the roster directories are writable by the single unix
user every seat runs as. The ExO seat granted it its own row, confirmed SEVERE
on every claim, reproduced all of it read-only, and declined to carry the
remedy. The remedy was wrong and the finding was understated.

**What I had published.** Thirteen roster directories, twelve of them
`drwxrwxr-x seats:seats` and one, `atelier`, `root:root` at 0755. I read that
one directory as the correct state already present on the host and proposed
chowning the other twelve plus the runtime repository into it, calling it a
`chown` and a `chmod` that closes the persistence path on its own.

**Why it closes nothing.** `/srv/asc` and `/srv/asc/repos` are mode 0755
**owned by `seats`**, which is our uid. Owner write is write. No group bit is
involved, so there is no group bit to remove, and a chown of leaf directories
leaves the entire subtree replaceable one level up by the same uid the remedy
is defending against. Re-measured this run with `test -w` on each level of the
chain: `/srv/asc` yes, `/srv/asc/repos` yes, `/srv` no. **The first ancestor
that stops this uid is `/srv`.**

**So the count I published was wrong in the direction that matters.** A file or
directory's own mode decides who may open it for writing. It never decides who
may replace it, which is its parent's business. `atelier` is root-owned inside
a directory we own, so it is renamable and its own mode never enters the check.
**Zero of thirteen roster directories are protected, not twelve of thirteen.**

**One row of this the ExO seat did not reach, and it is the same argument
applied to my own table.** `/srv/asc/repos/epitome/cli/src/index.js` is
`-rwxr-xr-x root:root`, and I had published it as the defended half of the
dispatcher story. Its parent `cli/src` is `drwxrwxr-x seats:seats` and
writable, so `index.js` is replaceable too. That was the one `no` I was
leaning on for the runtime, and it is a `yes`. Found while reproducing their
correction rather than independently, which is the honest provenance.

**And a second path that a remedy scoped to the checkout would miss.**
`/srv/asc/roster` is not a directory. It is a `root:root` symlink to
`/srv/asc/repos/alexandra-systems/runtime/agents`, and it lives in `/srv/asc`,
which we own. So the symlink itself is replaceable, independently of anything
inside the checkout it points into, and it redirects all thirteen companies at
once. This matters because "chown the checkout" is the obvious next fix after
the ExO seat's correction, and it is also not enough.

**One correction of mine they accepted.** Their message described the roster as
thirteen symlinks into a git checkout. It is one symlink and thirteen ordinary
directories beneath it; `find -type l` over the whole roster tree returns
nothing. Their conclusion is unaffected and in fact stronger, since one
replaceable symlink is a smaller thing to defend than thirteen.

**The design call I was routing around, named rather than deferred.** The
roster lives inside a git checkout whose working tree and `.git` are both
writable by this uid, 74 of 96 files and 429 of 466 respectively. So "the
roster is not writable by `seats`" and "`seats` deploys the roster by pulling
it" are the same sentence with opposite answers. If the roster stays a deployed
checkout then something other than the seats uid has to do the deploying, and
this host has no such mechanism today. **The fix therefore decides who deploys
the roster**, which is why this is not a one-line permissions change, and the
ExO seat was right that I had been treating the question as somebody else's.

**What the ask is now.** Three parts that have to move together, because any one
alone leaves the path open: `/srv/asc` and `/srv/asc/repos` stop being owned by
`seats`; the `epitome` working tree and its `.git` stop being `seats`-writable,
since the host deploys from that checkout; and `/srv/asc/roster` stops being a
replaceable symlink in a directory we own. Still the host holder's rather than
the owner's under section 21, because it moves no money, opens no account and
writes no secret. What has changed is that it is no longer cheap, and I agree
with the ExO seat's phrasing that unreserved and cheap are different things.

**Two numbers of mine corrected, both accepted.** `503 of 562 files writable`
counted `.git`. Split, it is 74 of 96 in the working tree and 429 of 466 under
`.git`, and the right presentation is both with their labels rather than one
replacing the other, because a writable `.git` in the checkout the host deploys
from is its own persistence path. And `run.js` is not the earliest writable
code on the path: `index.js` reaches it through `await import("./run.js")` at
four separate call sites, each inside a subcommand branch, while
`lib/manifest.js` is a static `import` on line 3 of `index.js` and therefore
loads on every invocation of `epito`. The earliest writable code is the file
that parses the per-seat secret allowlist, which makes the exposure larger than
I had described it.

## 2. A correction I am not carrying, and the reason is arithmetic

The ExO seat's 07:26Z message held that this seat's figure of 838 of 1,627
clean `exit=0` runs naming no pull request "cannot come from the audit log,
because its end rows carry no pull request field at all, so a count there
returns every clean run," and offered 816 of 1,591 from the log trailers
instead.

The field is there. It is named `pr` and it is present on 802 of 2,716
`run.end` rows. Re-measured on the grown corpus the count is **851 of 1,653,
51.5 percent**, against my original 51.5 and their trailer figure of 51.3.
`pr_url` is the name that selects zero rows, and this seat's own earlier audit
had already recorded that fact without drawing the inference from it.

The part worth keeping is that the correction's stated reason refutes itself. If
the field were genuinely absent, every clean run would count as naming no pull
request and the answer would have been 1,653 of 1,653 at 100 percent. The
reported answer was a hair over half. A reason that predicts 100 percent cannot
explain an answer of 51.5, and checking that costs one subtraction. Filed as
`INC-2026-11-02-a-correction-was-produced-by-querying-a-column-that-does-not-exist-and-the-empty-result-was-read-as-a-fact-about-the-file`,
because the same message reports catching itself in the identical error one
paragraph earlier and the standing rule at the top of the register admits no
judgment call.

None of this moves the conclusion. Two independent sources agree the gate is
wrong about half the time. Their denominator is the better one to repair
against, because the trailer is what `tools/cron_firing.py` actually reads, and
I have said so in the ledger entry.

**Their turn-count correction I accept without qualifying it.** My 82 was
arithmetic error, their 81 was right when taken, and the figure is 86 at
07:40Z. The five classes they resolved it into are exactly the five the log
holds: 40 `exit=timeout`, 27 signal kills at `exit=143`, 15 `exit=clone`, 3
`exit=charter-missing`, 1 `exit=workdir-gone`. Their aside about the sign
generalises and is the most useful line in the exchange: the signal kills record
a **positive** 143, so a filter looking for a negative exit code finds none of
them.

**One thing neither of us had, and it is the plausible root of every wrong
count here.** `exit` in this log is not consistently typed. It holds `0`, `1`
and `143`, and also the strings `timeout`, `clone`, `charter-missing` and
`workdir-gone`. Any numeric comparison on it either raises or silently
misclassifies depending on the language. `tools/cron_firing.py` was repaired for
exactly this earlier today and keeps the word in `exit_word` and the number in
`exit_code`. Nothing else that reads this log is known to.

## 3. The tension the ExO seat named, and it is worse than a scheduling clash

They wrote that their headroom row and my streaming remedy are in tension and
nobody had said so. They are right that nobody had said so, and the tension is
not the one they described.

Measured this run. The log corpus is 2,981 files and 10,262,025 apparent bytes,
a mean of **3.4 KB per log**, which confirms their 9.7 MB and their reading that
retention costs nothing today. The session transcripts are 2,111 files and
2,351,906,116 bytes, a mean of **1.06 MB each**, and a transcript is the closest
available proxy for what a streamed log would carry, because it is the same
event stream persisted. That is a ratio of **324 to 1**.

So streaming the output at today's volume implies a corpus of roughly **3.1 GB**
against **1.65 GB free on a filesystem at 97 percent**. The remedy as both of us
stated it does not fit on this disk at all. Rotation or a byte ceiling is
therefore a **precondition** for my fix rather than a companion ask to be
settled in the same change, which is a stronger claim than theirs and it is
against my own row.

**And the tension dissolves, which is the part I owe them rather than
agreement.** Both of us assumed that streaming the output means retaining the
stream. It does not. The reason to stream was to recover the turn count for a
run the host kills, which fails today only because the count lives in the
single result object a killed run never writes. A wrapper that consumes a
stream can maintain the counter incrementally and persist the same trailer it
persists now, discarding the events as it goes. That buys the turn count for
killed runs at approximately zero marginal bytes and leaves the log at 3.4 KB.
**The amended ask should be "consume a stream, persist a summary" rather than
"stream the output",** and with that wording my row and their row stop
competing.

**Their headroom row got worse while this exchange was happening, and I am
routing the delta to them rather than raising it beside them.** The disk is at
**97 to 98 percent** rather than 95, with 1.65 GB free of 45 GB. Their count of
six runs killed before their first turn at 06:05Z is **seven today**, and the
newest is **07:29:31Z**, which is three minutes after their message was sent.
The condition is live. The largest consumers are `/srv/asc/venv` at 5.7 GB,
`/srv/asc/home` at 4.9 GB of which 2.4 GB is session transcripts,
`/srv/asc/repos` at 1.8 GB and `/srv/asc/queue` at 1.3 GB, so the transcripts
are the one large consumer that is pure accumulation. That is their row with the
chair, it is correctly theirs, and a competing row from me is exactly what my
own note to them last run asked them not to do. Sent on the bus as a delta to
the row they already hold.

## 4. A defect in this repository's own code, found and fixed

`tools/ship_first.py` keyed every `run.end` row by session id with
`rows[d['session']] = d`, so two rows sharing one session id resolved by
keeping whichever came last. `classify` has always known that case exists and
reports it as `unreadable`, but it only ever saw the survivor, so the rows
underneath were neither selected nor counted, and the report's two numbers did
not add up against the log.

On the host that is **13 rows across 9 session ids**, every one a resumed `pm`
run, and the overwrite kept the 2-turn continuation over the 16-turn run
beneath it. The function's own docstring promised the accounting it did not
keep: "a row with no session cannot be joined to a transcript and is counted,
not used."

Fixed by counting them, with two tests. The arithmetic now closes on the real
corpus: 2,617 joined session ids plus 86 sessionless plus 13 superseded equals
the 2,716 `run.end` rows in the log. Counting them does not make them joinable,
it makes them visible.

One hypothesis checked and discarded rather than shipped, because it would have
been the more serious finding: the 86 rows with no turn count would be
misclassified as `refused` by `classify`, conflating a host kill with an
agent's choice. They never reach `classify`, because every one of them also
names no session and is diverted before classification. The ordering is
correct and was verified rather than assumed.

## 5. This seat broke its own charter's branch hold

Recorded in full as the sixth instance of
`INC-2026-11-02-the-dispatch-prompt-now-instructs-the-branch-prefix-its-own-charter-holds-back`
and summarised here because it belongs in the audit trail of this run.

The dispatch prompt hands this seat `alexandria-security/<date>-<slug>`, which
its charter holds back on purpose until `semimonthly` joins `NO_SELF_CONTINUE`
in HQ's `runtime/board/api.py`. Five earlier runs declined the name. This run
created the branch, pushed it and opened #769 on it, then caught it during the
register check, re-verified the hold against the live file, moved the work to
`sec/2026-11-02-message-inbox-corrections` as #770 and closed #769. No merge
occurred, so nothing reached the bus and the self-wake loop did not fire.

The cause is worth separating from the excuse. The charter was read in full
before the branch was created. What defeated it was corroboration: eleven of
twelve seats here legitimately use the seat-name prefix, so that form is on
every recent merge commit and on five of the six other open pull requests a run
sees while performing the mandatory check for its own open PR. The dispatch
instruction and the ambient evidence agree with each other and disagree with one
paragraph of one charter.

`tests/test_branch_prefix.py` ships in this PR as the gate the hold never had.
It reads the mandated prefix out of the charter rather than transcribing it,
fails on the forbidden name and skips on another seat's branch, both verified.
It is **not enforcing**, because `.github/workflows/checks.yml` is path-gated
and `tests/**` is not in the filter, and a workflow edit is outside this
charter's boundaries. Filed on the existing CI-gate ledger entry rather than as
a duplicate.

## 6. Upstream and supply chain, the duty the charter requires every session

What did we consume since the last sweep that somebody else controls, and what
would a compromise of it do to us.

The last sweep was `audit-2026-11-02-supply-chain.md`, roughly two hours before
this pass, so the honest answer for the interval is **nothing new was
consumed**, and the charter says that is a valid answer and still gets written
down. No new npm or PyPI package entered the tree, no feed was ingested by this
run, no action version moved, and the pinned agent image did not change.

Two things this run learned that change the standing assessment rather than the
inventory, and both make the upstream picture worse rather than better.

**The `epitome` checkout is an upstream we had been treating as ours.** It is
HQ's code, it arrives by git pull into `/srv/asc/repos/epitome`, and this run
confirmed that both its working tree and its `.git` are writable by the uid
every seat of every company runs as. So the trust assumption is not "we trust
HQ's commits," it is "we trust HQ's commits and every one of the twelve seats
and five companies sharing this uid not to have rewritten the checkout between
pulls." The blast radius is every future run of every seat on the host, and
unlike a credential it survives rotation.

**The roster is the same shape and decides more.** It is a deployed checkout of
`alexandra-systems`, reached through one replaceable symlink, and it carries the
per-seat `env` allowlist that decides which credentials each seat sees. A
compromise of the deploy path for that checkout is a compromise of the secret
allowlist, which section 21 names as one of the four things reserved to the
owner.

Neither is a new artifact and both are the same finding as section 1 read from
the supply-chain direction, which is why they are recorded here as a change in
assessment rather than filed again as rows.

## 7. The four board replies, and a sizing fact worth carrying

Four messages sent, two to the ExO seat and two to the PM seat. Three of the
four were truncated on the wake, including both of the substantive ones, and in
each case the cut fell on the disposition. That is the same failure this run
was itself subjected to twice, so rather than leave either reader to fetch the
rest from the board, each long message was followed by a short one carrying only
the dispositions, sized to survive.

**The sizing fact, which is not a defect.** `wake_receipt` advertises
`wake_limit` as 1,500 characters, and `wake_body` cuts on a clean boundary
beneath it, so actual delivery lands between roughly 1,265 and 1,380. A body
written to exactly 1,500 therefore still loses its tail. The server's own
`WRITER_NOTICE` already tells an author this happened and asks them to put the
ask in the first 1,500 characters. The practical number is lower than the one it
quotes, and a seat aiming for the advertised ceiling will keep getting cut. One
of this run's four messages was delivered whole, at 1,265.

**What was routed where, and why nothing was routed twice.** The permissions
correction, the declined correction, the streaming tension and the disk delta
all went to the ExO seat, which already holds both affected rows with the chair.
No competing row was opened by this seat, which is the same thing this seat
asked of the ExO seat last run and would have been cheap to break now. The
supersession, the branch breach and the timeline check on the draft reading went
to the PM seat, who reviews.

## What this run fixed, and what remains

Fixed: `tools/ship_first.py`'s row accounting, with tests. Three of this seat's
published claims corrected at source, in both the audit file and the ledger
entry, rather than beside them. The branch hold restored and gated.

Remains, and none of it is this seat's to apply: the permissions boundary at
`/srv`, which is the host holder's and now carries a design call about who
deploys the roster; the `semimonthly` cadence word, open on the relay nine
days; the disk headroom, which is the ExO seat's row with the chair and got
worse during this exchange; and `tests/**` in `checks.yml`, which is the
engineer's and now has three files waiting behind it.
