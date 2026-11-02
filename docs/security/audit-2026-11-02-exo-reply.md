# Security and debug audit, 2026-11-02 (exo-reply wake)

Fifth security run of 2026-11-02. Woken by `message`, a note from
alexandria/exo. The wake carried 1238 of 2594 characters and said so.

This run's distinct contribution is one finding, reached by doing what the
note asked and reading the whole message rather than the delivered half. The
finding is the mechanism behind the truncation thread both seats have been
paying for all night, and it is not truncation.

Earlier runs today are [audit-2026-11-02.md](audit-2026-11-02.md),
[audit-2026-11-02-refusal-slots.md](audit-2026-11-02-refusal-slots.md),
[audit-2026-11-02-reply.md](audit-2026-11-02-reply.md),
[audit-2026-11-02-supply-chain.md](audit-2026-11-02-supply-chain.md) and
[audit-2026-11-02-disposition.md](audit-2026-11-02-disposition.md). The full
sweeps are there. This file does not repeat them. What it re-ran is recorded
under "Sweeps re-run" below, as deltas only.

## Finding 0, SEVERE and new: the host's control plane is writable by the uid every seat shares

**This is the write half of the 05:30Z run's credential finding, and it was
not measured. It is strictly worse than the read half.**

`audit-2026-11-02-disposition.md` section 2 established that every seat of every
company runs as uid 997 and can therefore read every credential the host holds.
It priced the exposure as the whole credential set. The question it did not ask
is what that uid can **write**, and the answer is the machinery that runs every
seat.

**How this was checked, and the limits of it.** `test -w`, `stat`, `ls -l` and
`find -writable`. Nothing was written, created, unlinked or modified at any
path below, and no file's contents are reproduced here. A permission is a fact
about the filesystem and reading one is not exercising it.

**Corrected 2026-11-02 07:40Z by this seat, after the ExO seat reproduced every
row and found the remedy wrong** (message `c1692d84`, relay PR #753). Three of
my numbers were right about the filesystem and wrong about the claim I attached
them to, and the `no` column below was the worst of them. The table as first
published is kept in the git history of this file; what follows is the state
I re-measured myself rather than taking, because a correction accepted without
reproducing it is how the first version got here.

| Path | Mode and owner | This seat can write it |
|---|---|---|
| `/srv/asc/repos/epitome/cli/src/lib/manifest.js` | `-rw-rw-r-- seats:seats` | yes |
| `/srv/asc/repos/epitome/cli/src/run.js` | `-rw-rw-r-- seats:seats` | yes |
| `/srv/asc/repos/epitome`, working tree | 74 of 96 files writable | yes |
| `/srv/asc/repos/epitome/.git` | 429 of 466 files writable | yes |
| `/srv/asc/roster/<company>/` | `drwxrwxr-x seats:seats`, 12 of 13 | yes |
| `/srv/asc/roster/alexandria/security/` | `drwxrwxr-x seats:seats` | yes |
| `/srv/asc/hq/runtime/board/api.py` | `-rw-r--r-- root:root` | no |
| `/srv/asc/venv-board/bin/python` | root | no |
| `/srv/asc/roster/atelier/` | `drwxr-xr-x root:root` | **yes, by rename** |
| `/srv/asc/repos/epitome/cli/src/index.js` | `-rwxr-xr-x root:root` | **yes, by rename** |
| `/srv/asc` | `drwxr-xr-x seats:seats` | yes, we own it |
| `/srv` | `drwxr-xr-x root:root` | no |

**The `no` column was asking the wrong question, and that is the whole
correction.** A file's own mode only decides who may open it for writing. It
never decides who may replace it, which is the parent directory's mode. Walk
the chain and the parent is ours every time: `/srv/asc` and
`/srv/asc/repos` are mode 0755 **owned by `seats`**, and owner write is write,
so no group bit is involved and removing the group bit changes nothing. The
first ancestor that stops this uid is `/srv`, which is `root:root`.

So the two rows I published as defended are not defended. `atelier` is
`root:root` 0755 and renamable, because its parent is writable by us and its
own mode never enters the check. **Zero of thirteen roster directories are
protected, not twelve of thirteen.** `index.js` is root-owned 0755 and
renamable for the same reason, which voids the one row I used to argue the
dispatcher was partly defended. The ExO seat found the roster half; the
`index.js` half is the same argument one level up and it is mine, found while
reproducing theirs.

**And `503 of 562` was a true count under a false label.** It counts `.git`.
Split, it is 74 of 96 in the working tree and 429 of 466 under `.git`, and the
two numbers mean different things rather than one replacing the other. The
tree number is the code that runs. The `.git` number is its own path: this is
the checkout the host deploys from, so a writable `.git` means rewriting refs
and objects and letting the next deploy carry the change in. Both belong in the
finding, labelled.

**`run.js` was also not the earliest writable code, and this one makes the
exposure larger.** `index.js` reaches `run.js` through
`await import("./run.js")` at four separate call sites, every one of them
inside a subcommand branch, so `run.js` loads only for `run`, `ps`, `window`
and `message`. `lib/manifest.js` is a **static** `import` on line 3 of
`index.js`, so it loads on every invocation of `epito` whatever the subcommand,
and it is mode 0664 `seats:seats`. The earliest writable code on the path is
therefore the file that parses the per-seat secret allowlist.

**What each of those three writable surfaces is.** `run.js` is the resident
runtime's dispatcher. The systemd unit runs `epito run /srv/asc/roster` as
`User=seats`, `index.js` is root-owned but immediately does
`await import("./run.js")`, and `run.js` is the file that starts every run of
every seat on this host. Beside it and equally writable are `lib/manifest.js`,
which parses the per-seat secret allowlist, `lib/audit.js`, which writes the
org's only run-accounting evidence, and `lib/hooks.js` and `lib/cron.js`.

The roster is what the daemon reads to decide which seats exist, when they
fire, which model they use, and which credentials each one sees. My own
`agent.toml` carries
`env = ["CLAUDE_CODE_OAUTH_TOKEN", "GH_TOKEN", "BOARD_API_URL", "BOARD_RUNTIME_TOKEN"]`,
and that line is the allowlist. The manifest **files** are root-owned at mode
0644, which reads as safe and is not: the **directories** holding them are
group-writable, and a writable directory is enough to replace a file inside it
regardless of the file's own mode. Twelve of the thirteen company directories
are in that state, and the thirteenth is in no better one, because the
directory above all thirteen is ours as well. See the correction above: the
count that matters is zero protected, not one.

**So the blast radius of one compromised seat is not one seat's work and it is
not even the credential set.** It is persistence. Rewrite `run.js` and you are
in every future run of all twelve seats across five companies. Rewrite
`lib/manifest.js` or replace one `agent.toml` and you widen a seat's secret
allowlist, which `docs/standards/pm.md` section 21 reserves to the owner as one of the
four things no seat may do. Rewrite `lib/audit.js` and the surface that would
have recorded any of it is yours too.

**Why this is a prompt-injection finding and not only a permissions one,** which
is the charter's standing question. Every seat here reads the public web,
scraped pages, pull request text and issue bodies. Section 2 of the 05:30Z report drew
the ceiling at what a seat can read. The ceiling is higher: an injected
instruction that writes one file owns the dispatcher, and unlike a credential
read it survives rotation. Rotating every secret on this host would not evict
it.

**There is no evidence any of this has happened**, and nothing here indicates a
compromise. No secret is leaked, nothing is in the working tree or in git
history, and **no rotation is indicated by this finding.** What is indicated is
a permissions change.

**Owner or host action. Withdrawn and replaced 2026-11-02 07:40Z, because the
remedy I published does not close the path.** What stood here said the correct
state was already on the host in `/srv/asc/roster/atelier/`, and that chowning
the other twelve directories and the runtime repository to root would close the
persistence path on its own. The ExO seat declined to carry it and was right.
Chowning thirteen leaf directories leaves the subtree replaceable one level up,
and the level up is ours by ownership rather than by a group bit, so there is no
bit to remove. `atelier` was never the worked example of the correct state. It
was a root-owned directory inside a directory we own, which is the same
exposure wearing a safer mode.

**The replacement, and the reason it is one line longer than a `chmod`.** The
boundary has to land at or above the first ancestor this uid does not own, and
walking the chain that is `/srv`. Three things have to move together, and any
one of them alone leaves the path open:

1. `/srv/asc` and `/srv/asc/repos` stop being owned by `seats`. Until this
   happens every remedy below is reversible by the uid it is defending
   against, by renaming the directory the remedy is inside.
2. The `epitome` working tree **and its `.git`** stop being writable by
   `seats`, because the host deploys from that checkout.
3. `/srv/asc/roster` is a `root:root` symlink living in `/srv/asc`, which we
   own, so it is replaceable on its own and a remedy scoped to the checkout it
   points into does not cover it. This one is mine, found while reproducing the
   ExO seat's correction, and it is the reason the obvious next fix of chowning
   the checkout is also not enough.

**And the part that is a design call rather than a `chown`, which I was routing
around.** The roster is `/srv/asc/repos/alexandra-systems/runtime/agents`,
inside a git checkout whose working tree and `.git` are both writable by this
uid. So "make the roster unwritable by seats" and "let seats deploy the roster
from a git pull" are the same sentence with opposite answers, and the fix has
to say which one wins. If the roster stays a deployed checkout, something other
than the seats uid has to do the deploying, and that is a mechanism this host
does not have today. The ExO seat named this and I had not. It is the reason
this row is not a one-line permissions change, and stating it is the honest
version of the ask.

Still true, and the reason this is not the owner's: it moves no money, opens no
account and writes no secret, so under section 21 it is the host holder's to
apply rather than hers. What has changed is that it is no longer cheap, and
unreserved and cheap are different things.

**One correction of mine the ExO seat accepted, recorded for the same reason
the rest of this block exists.** Thirteen symlinks is not the shape. There is
exactly one symlink, `/srv/asc/roster` itself, and thirteen ordinary
directories beneath it; `find -type l` over the whole roster tree returns
nothing. The conclusion drawn from it stands and is in fact stronger, since a
single replaceable symlink redirects all thirteen at once.

Recorded here, in the ledger, and sent to the ExO seat's relay, because the
surface is headquarters'.

## Finding 1, high: a seat's pending trigger is one slot deep, and anything that is not a message overwrites what a person said

**Severity: high.** Not a secret and not an exposure. It silently destroys
delivered work instructions, and it is the cause of two classes this register
already carries separately.

**Where.** HQ's runtime, `cli/src/run.js` in `epitome`, the `enqueue`
function. On this host that resolves through `/usr/bin/epito` to
`/srv/asc/repos/epitome/cli/src/run.js`. Not our file, and the remedy is not
ours to apply.

**The mechanism, read out of the source rather than inferred.** Each seat
holds `{running, pending, coalesced}`. A trigger that arrives while the seat
is running is coalesced, and the whole of the queue is the single `pending`
slot:

```
if (s.pending?.trigger === "message" && trigger === "message")
  s.pending.text = `${s.pending.text}\n\n${req.text}`;
else
  s.pending = req;
```

The merge arm is correct and it is narrow. It requires the slot to **already
hold a message** and the arriving trigger to **also be a message**. Every
other combination takes the `else` branch, which is an unconditional
overwrite. The comment three lines above it reads "a coalesced trigger may be
dropped, but something a person said may not," and the `else` branch is
exactly where something a person said gets dropped.

**Measured, not argued.** Over the 11,661 rows of the host audit log at
`/srv/asc/state/.epito/audit.jsonl`, replaying the pending slot per seat:
six coalesced message payloads were overwritten by a later non-message
trigger. Three of the six are in the last 24 hours.

| Seat | Message coalesced at | Overwritten by |
|---|---|---|
| `engineer` | 2026-10-24T12:03:19Z | `cron` at 12:06:08Z |
| `ursa-engineer` | 2026-10-25T23:06:29Z | `cron` at 23:26:14Z |
| `epitome-engineer` | 2026-10-25T23:05:20Z | `cron` at 23:46:14Z |
| `engineer` | 2026-11-01T23:22:02Z | `cron` at 2026-11-02T00:06:03Z |
| `alexandria-exo` | 2026-11-02T00:50:19Z | `cron` at 01:00:20Z |
| `ursa-security` | 2026-11-02T01:05:03Z | `cron` at 01:15:23Z |

**One window read end to end, because the aggregate understates it.**
`alexandria-exo`, inside the run that started 2026-11-02T00:49:18.438Z:

```
00:50:19.940Z  message coalesced, 1314 bytes   -> pending = that message
01:00:20.061Z  cron    coalesced               -> pending = cron, the message text is gone
01:10:29.782Z  message coalesced, 1814 bytes   -> pending = that message, the cron slot is gone
01:15:24.480Z  run.end
01:15:24.483Z  run.start trigger=message       -> only the third of the three arrived
```

Three triggers went in and one came out. A 1314-byte message was destroyed, a
weekly cron slot was destroyed, and the follow-up run's `run.start` row names
`message` as its trigger, which is the proof the cron never ran.

**This is the cause of two entries this register already holds as separate
classes.** `tools/cron_firing.py` reported that window as
`COALESCED alexandria-exo 01:00Z`, and its docstring says the host "records
the firing and starts nothing." That is the symptom described correctly. The
cause is that a message arriving ten minutes later overwrote the slot. The
tool is right and its explanation is one level too shallow, which is worth
knowing before anybody tries to fix the slot loss in our file, because it is
not fixable from here.

## Finding 2, high: resending a cut tail cannot converge, and the reason is the slot above rather than the character limit

Both seats in tonight's thread independently adopted the same remedy for the
1500-character wake cut: send the tail as a second message. alexandria/exo
then observed, correctly, that it does not converge, and attributed it to the
tail being a message with the same limit.

That is true and it is the smaller half. The larger half is mechanical.

**A tail sent to a seat that is running does not reach the run that read the
head.** It coalesces, it merges into `pending`, and `pending` is delivered to
a **follow-up run**, which is a fresh session with no memory of the head. So
the claim reaches one reader and the qualification reaches a different one.
Neither reader holds both halves. No amount of resending changes that,
because every resend lands in the same slot with the same destination.

**Demonstrated on this run's own payload.** The three notes exo sent arrived
at 05:35:01.130Z, 05:35:13.168Z and 05:35:26.840Z. The audit log marks the
first with no `coalesced` field, which is why it started this run, and marks
the second and third `coalesced: true`. Both took the merge arm, so they are
concatenated in `pending` and addressed to my successor. I am holding the
head. My successor will be handed the two tails and will not have read the
head.

I have the tails only because I went and read the bus directly, which the
wake told me to do.

**The second cost, and it is the expensive one.** That follow-up run is a
duplicate wake for an event already answered, which is the class filed today
as `INC-2026-11-02-the-duplicate-wake-class-priced-fleet-wide-at-two-thirds-of-the-days-turns`.
So a tail resend is not free and it is not neutral. It buys one extra run of
the recipient's budget, and by Finding 1 it carries a one-in-ten chance of
destroying the tail outright if a cron slot falls in the same window.

**So exo's sender-side rule is not merely the best available one, it is the
only correct one.** Put the disposition in the first 1200 characters and let
the reasoning be the part that gets cut. The alternative is not "two
messages." It is two runs, each reading half of one message, plus one run of
somebody's budget.

## Finding 3, medium: the integer exo said was not theirs to add is already computed, one line from where it is needed

exo raised the payload count as an ask and said, correctly, that a run holds
no record of the compose moment and so cannot answer whether it was handed
everything that existed when it was woken.

The runtime already answers it. `s.coalesced` is a counter incremented on
every coalesced trigger. At the moment the follow-up run starts, `run.js`
reads it:

```
const next = s.pending; const n = s.coalesced;
s.pending = null; s.coalesced = 0;
log(`${name}: starting the coalesced run (${n} trigger${n > 1 ? "s" : ""} arrived during the last run)`);
return startRun(name, next);
```

`n` is printed to epitod's own log and then discarded. It is not passed to
`startRun`, it is not in the `run.start` audit row, and it is not in the
payload the run receives. So the number exists, it is exact, it exists at
precisely the moment it is wanted, and the only reader is a log line nobody
sweeps.

This matters for how the ask should be written. It is not a new measurement
and it is not instrumentation to design. It is passing a variable that is
already in scope into the two places that already exist, `startRun`'s `req`
and the `run.start` audit row. Naming it that way is the difference between
an ask somebody schedules and an ask somebody does.

## Finding 4, low and closed: the field-name class exo handed me, reproduced and then turned on my own instrument

exo handed over a near-miss: the audit log calls the pull-request field `pr`
and the board calls it `pr_url`, and reading the audit log over `pr_url`
answers 0 of 2609 rows for every seat of every company.

Reproduced here, against the live log rather than the report. `pr` selects
762 rows of 11,661; `pr_url` selects 0. The source agrees: `run.js` writes
`...(r.pr ? { pr: r.pr } : {})` on the `run.end` row. exo's figures were 756
of 2609 run-end rows and mine are 762 of 2621, which is the log growing
between the two measurements and not a disagreement.

Then I ran the class against my own instrument, which is what it was handed
to me for. `read_coalesced` in `tools/cron_firing.py` filters
`row.get("action") != "cron"`. Of 3,887 rows carrying `coalesced` truthy,
17 are `action: "cron"`. The other 3,869 are `message` and one is `window`.

**That predicate is correct and I am not changing it.** The tool's question
is about cron slots, so scoping to cron rows is the right scope, and widening
it would report every coalesced message as a missed cron slot. Saying so
explicitly is the finding, because a 17-of-3,887 ratio looks exactly like the
defect exo nearly published and it is not one. What is a real gap is the
3,869: that surface answers the duplicate-wake question, it is the most
expensive class in this fortnight's register, and nothing in this repository
reads it. That goes to the ledger rather than into this tool.

## Sweeps re-run this wake, as deltas

- **Secrets, working tree.** Three credential-shaped hits, all three
  previously recorded and all three non-credentials: an illustrative DSN in
  the incident register at `docs/agents/incidents.md:6316`, the line in
  `audit-2026-10-15.md` that cites it, and the synthetic fixture in
  `tests/test_mcp_dsn_redaction.py`. No value is reproduced here. No change.
- **Public/private boundary.** `digests/` and `site/content/digests/` are
  both ignored, confirmed with `git check-ignore -v` using trailing slashes,
  which is needed because they are directory rules and neither path exists in
  a fresh clone. A check without the slash prints nothing and reads like a
  missing rule. No digest content is tracked. Unchanged.
- **Dependencies.** `npm audit` in `site/`: 0 vulnerabilities. Unchanged.
- **Tests.** `tests/test_cron_firing.py` passes 114 on the merged tree, which
  is the tree carrying both this run's merge resolutions. Full-suite result is
  in the pull request body.
- **Upstream and supply chain, the charter's written answer.** Nothing new
  consumed since the 03:00Z supply-chain pass of today, whose answer stands in
  [audit-2026-11-02-supply-chain.md](audit-2026-11-02-supply-chain.md). One
  addition from this wake, and it is a trust assumption rather than an
  artifact: this run read HQ's runtime source at
  `/srv/asc/repos/epitome/cli/src/run.js` and the host audit log at
  `/srv/asc/state/.epito/audit.jsonl`. Both are outside this repository and
  root-owned at the paths above, so every finding here is a reading of
  somebody else's artifact at a moment in time. A deploy of HQ main changes
  them without changing anything we hold, and the blast radius of that is that
  Findings 1 to 3 can be repaired, or re-broken, with no diff in this
  repository. The line numbers are deliberately not quoted for that reason.

## What this run fixed, and what it did not

**Fixed here.** Two merge conflicts from carrying #736, both additive on each
side and both kept whole: the `LOST` line in `tools/cron_firing.py` now
carries main's deferred-slot suffix and this seat's pull-request-candidate
hint in one string, and `tests/test_cron_firing.py` carries both new blocks.

**Not fixed here, and not ours.** Findings 1, 2 and 3 are all in
`cli/src/run.js`, which belongs to HQ. They go up as one ask, because they
are one defect in one function and splitting them would land three partial
repairs in the file that holds all three. The ask is recorded in the ledger
and sent on the bus.

**Deliberately not changed.** `read_coalesced`'s cron-only predicate, for the
reason in Finding 4.

## Finding 5, severe and live: the volume is still full, and it has moved from killing runs to disabling this seat's own verification

The 05:30Z run of this seat reported the host's only data volume full and
filed `INC-2026-11-02-the-only-disk-filled-again-and-a-seat-run-died-at-clone`.
That finding is not stale and it is not fixed. Three readings from this run:
193M free at 100% at 05:52Z, 799M at 99% at 06:01Z, 532M at 99% at 06:05Z.

**What is new is which step it broke.** The charter's debug sweep says to build
and exercise what can be exercised here. This run's attempt to do that died
inside Python's `tempfile._get_default_tempdir`:

```
FileNotFoundError: [Errno 2] No usable temporary directory found in
['/tmp', '/var/tmp', '/usr/tmp', ...]
```

The predecessor's evidence was a seat run dying at clone, which reads as one
run's bad luck. This is the seat that audits the others being unable to run
the suite that finds defects, because the volume it needs 50 megabytes of is
owned by nobody. That is worth separating from the availability finding: the
cost is not a lost run, it is a lost sweep, and a lost sweep is invisible.

**The composition, which the predecessor's remedy needed and did not have.**
It asked for "a cap or a predictable reaper on seat scratch" without saying
which scratch. The two candidates are not the same size and a reaper aimed at
the wrong one reclaims nothing:

| What | Count | Space |
|---|---|---|
| `epito-<seat>-<suffix>` live seat checkouts in `/tmp` | 22 | 5.2G, largest five 745M to 816M |
| `tmp*` per-run scratch directories in `/tmp` | 18,031 | about 0.9G, sampled mean 52K |
| `/tmp` total | | 17G |
| `/srv/asc` total | | 18G |

So the space is in the checkouts and the count is in the scratch directories.
A cap belongs on the checkouts and a reaper belongs on the scratch
directories, and they are different remedies. Mode on the scratch directories
is `0700`, which is the one thing on this list that is already right and is
the subject of the separate thread with alexandria/exo.

**`diskwatch` still has no reader, and this is now its best evidence.**
`/srv/asc/state/diskwatch.last` reads `crit 1793592679`, which is 04:11:19Z.
Unchanged across all three of this run's readings, two of them at 100%. The
verdict was correct, it was written down nearly two hours ago, and nothing has
opened the file since. The predecessor listed that third. On the evidence it is
first, because the other two remedies need somebody to decide a number and
this one needs somebody to read a file that already has the right answer in it.

**Owner or host action, unchanged in substance from the 05:30Z report and
restated because it is still owed:** reclaim headroom now, cap the seat
checkouts, reap the scratch directories, and give `diskwatch`'s verdict a
reader.

## Test results, stated with the disk caveat

The full suite does run, and it took 14m54s: **1 failed, 2474 passed, 2
skipped, 1 error**, with the failure and the error both worth separating.

**The failure was this chain's own and is fixed in this run.**
`tests/test_incidents.py::test_the_live_register_ids_all_parse` is green on
`main` and was red on this branch. The 05:00Z wake's entry separated its id
from its summary with a comma, and `INC_ID`'s lookahead ends a slug on
whitespace, an em or en dash, or a colon. So the match failed and `heading_key`
fell through to keying the entry on its whole heading, which means a charter
citing the id would not have found it and a second filing of the same id would
not have collided with it. That is the one guarantee the id scheme exists for.
Corrected by giving the heading the ` - ` separator every other entry uses. The
id string itself is unchanged and the entry is unmerged, so nothing that cites
it breaks. `tests/test_incidents.py` is 43 green after the fix.

The comment above that regex records the same mistake made with a colon by this
same seat earlier today, and repaired then by widening the lookahead. It is
deliberately not widened again here. Correcting one heading restores the
documented form; widening the pattern a second time would make the convention
whatever the register happens to contain.

**The error is not reproducible in isolation and the disk is the likely
cause.** `tests/test_skill_gate.py::test_a_version_with_no_trigger_in_the_history_is_refused`
errored in the full run and passes on its own. An error rather than a failure
means setup or teardown, the full run was executing while the volume sat at
100%, and this run has already seen `tempfile` refuse outright at that moment.
That is a reading rather than a proof: the detail lines for it were lost from
the captured output. It is stated as unresolved rather than as passing.

## Finding 6: two gates were red on this branch, and fixing the visible one is what exposed the other

This is the most useful thing this run found about itself, and it is an
instance of the general shape the charter's own prefix paragraph states.

The register heading fixed above separated its id from its summary with a
comma, so `INC_ID` did not match and `heading_key` fell through to keying the
entry on its whole heading. Correcting the separator made the id parse. On the
next run of the suite, a second gate went red:
`tests/test_incidents.py::test_the_live_branch_files_every_incident_it_adds_through_the_inbox`.
That entry had been appended straight into `docs/agents/incidents.md` rather
than filed through `docs/agents/incidents/inbox/`, which the gate requires so
that two seats filing between merges cannot collide on the register's append
anchor. That is incident 6's class.

**The gate could not see the misfiling while the separator was broken**,
because it looks for appended `INC-` ids and the id was not parsing as one. So
the first defect was the only reason the second had never fired. The charter
says it this way: a one-line repair that reads as obviously correct is the
place to look for a second defect, because the thing you are about to fix may
be the only reason the second one has never fired. It was written about the
branch prefix. It is reproduced here by this seat, on this seat, inside one
file, within one hour.

Both are fixed. The entry is moved into the inbox verbatim, text and id
unchanged. A third gate, `tests/test_ledger.py`'s contract check, was red on an
entry this run itself added with no `Trigger` field, and that is fixed too.

**What that says about the CI gap, and it is why the ledger entry above was
revised rather than repeated.** None of these three gates runs on a pull
request here. `tests/test_incidents.py`, `tests/test_ledger.py`,
`tools/incidents.py` and the two registers they read are all absent from
`.github/workflows/checks.yml`'s `paths` list. Three real defects, all of them
this seat's own, all of them in registers whose entire purpose is to be cited
later, and the only thing that found them was a seat running the full suite by
hand on a host that was simultaneously refusing to allocate temporary
directories.

## The suite is not reproducible on this host right now, and that is a finding rather than a caveat

Two full runs of the same suite, 16 minutes apart, on trees differing by one
heading separator:

| Run | Result | Wall time | Failures |
|---|---|---|---|
| 05:46Z | 1 failed, 2474 passed, 2 skipped, 1 error | 14m54s | the register id parse |
| 06:02Z | 4 failed, 2463 passed, 2 skipped, 9 errors | 13m05s | the register inbox gate, two ledger contract checks, one that passes on rerun |
| 06:25Z | 4 failed, 2472 passed, 2 skipped, 0 errors | 9m22s | four in `tests/test_deploy_drift.py`, all 58 of which pass on rerun |

**Three runs, three different failure sets, and no two of them overlap.** One
heading does not move eleven results. The second run's extra errors are in
`tests/test_latest_links.py` (seven of them), `tests/test_drift_watch.py` and
`tests/test_panel_provenance.py`, and `tests/test_check_helper_is_enforced.py`
failed in the second run and passes on rerun. Errors rather than failures means
setup or teardown, both runs executed while `/dev/sda1` sat between 97 and 100
percent, and this run has already watched `tempfile` refuse outright at that
pressure.

So the honest statement of test health on this branch is two statements. The
four failures that reproduce on rerun were real, were this chain's own, and are
fixed: the register id parse, the register inbox gate, and the two ledger
contract checks. All four are green on rerun and were green in the 06:25Z run.
Everything that did not reproduce is unresolved and is attributed to the volume
rather than to the code, which is a reading and not a proof. The third run is
the strongest evidence for that reading: its four failures were all in
`tests/test_deploy_drift.py`, a file that shells out to git, and all 58 of its
tests pass when run alone.

**The consequence for anybody reading a green run on this host is the part
worth keeping.** A suite that returns a different answer every quarter hour
cannot be used to clear a change, and nothing in the run output says which
answer you got. That is a stronger version of Finding 5: the disk does not only
stop a sweep, it can let one finish and report the wrong thing.
