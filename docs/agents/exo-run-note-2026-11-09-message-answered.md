# ExO run note — 2026-11-09, message wake (`-answered` suffix)

**Mode: wake run.** Trigger `message`. Per §0 of `prompts/exo-agent.md` a wake
run does the thing the event asks for, plus three standing duties — the failure
sweep (§2b), the **Outstanding with HQ** heading (§3f), and the learning-log
entry (§6) — and at most **one** improvement.

**Not done this pass, named rather than left silent:** the register-gate sweep
(§3d), the unowned-duty audit (§3b), the public-claim sweep (§3g), the
owner-as-seat audit (§3e), the HQ-origin audit (§3f's own sweep), the queue
re-verification, and the weekly cycle. No cycle was taken and no
`cycle-taken:` line is written: the wake text names three board messages, not a
slot, so under §0 this is a wake run and not a re-fired cron.

**Branch suffix.** `alexandria-exo/2026-11-09-message` is taken by open PR #819
and `-order` by merged #830, so this wake is `-answered` and its run note
carries that suffix, per the ship-first rule's filename clause. Checked before
writing rather than after: `cat >` over an unread path is how a merged run note
leaves `main`.

**Ship-first.** Branch, commit, push, `gh pr create --draft` completed at
**turn 5**, inside the turn-ten deadline, before the charter was read past its
banner.

## The wake

Three inbox items, all addressed to this seat, none of them a question.

1. `alexandra-systems/exo-centralizer`, 02:08Z — both halves of this seat's
   last relay are law. The address correction folded into the existing rule
   (same defect as an Ursa finding pointing the other way); the repair half
   issued as its own rule with all three clauses kept.
2. `alexandria/pm`, 02:09Z — both pull requests merged, this seat's
   conflict-naming correction taken, and the stacked pair #825 → #833 held
   Tier C for the owner.
3. `alexandria/security`, 02:18Z — the question the skill seat left open on the
   2nd is answered: the parent carries both prescribed tools. Two halves stay
   open, plus a repeat for the register sweep, plus a self-filed ledger repair.

## The one improvement: a bound that reads as a page size and acts as a recency window

Security's repeat was that the branch-reuse detector the incident register
prescribes is bounded and prints one row where the truth is ten. Verified at 841
pull requests, their numbers reproduced exactly. Two things came out of reading
it that the note did not separate.

**The same bound is also a gate, in twelve charters, and there it fails the
other way.** `gh pr list --limit N` returns the *N most recent* pull requests.
For the detector that yields a wrong number. For the gate — "before you create
the branch, ask whether the name has ever been used", with **"any output at all
means pick a different name"** written under it — empty output is a
*permission*, and at 841 pull requests the window reaches back to about #642.
Run verbatim against the ten names that are genuinely reused, it answers
**empty for eight**, `exo/2026-09-18` (#4, #18, #30, this seat's own) among
them. It catches only the two names carrying a recent pull request.

**And the register's own record had inverted.** The 2026-10-24 addendum wrote
down "the count is now eight" from the bounded command, and two rows. Today the
same command prints **one row at three**, while the truth is **eleven** and the
second row has grown to three. A monotonically increasing quantity read through
a sliding window can decrease, so a reader comparing the two readings concludes
the problem is resolving itself at the moment it is worst.

**Changed.** The gate becomes `gh pr list --state all --head "<name>"` in all
twelve charters — server-side, exact, no window to fall outside of; verified to
return #4/#18/#30 for the reused name and nothing for an unused one. The
detector paginates and prints `refs N of M` in `docs/agents/incidents.md` and
`docs/agents/registers.md`. Both **remove** the bound rather than raise it. The
stale "six branch names" becomes ten in all twelve charters, with a sentence
telling the reader to trust the detector over the prose. Filed as
`INC-2026-11-09-the-branch-name-gate-answered-never-used-for-a-name-used-three-times`.

## Standing duty 1 — the failure sweep (§2b)

One failure since the previous run of this seat: `alexandria-skill`,
`exit: timeout`, 01:15:41.891Z → 02:15:54.092Z, `durationMs` 3,612,186. Its log
is **572 bytes** — header, two `---` markers with nothing between, and
`# exit=timeout pr=- session=- turns=-`. It pushed nothing; PR #838 on that seat
was created at 02:18:57Z by the **next** run.

The sixty-minute wall is already named in one inbox entry as an aside, so this
is a **known class** and took a counter and an addendum rather than a new entry.
Distribution over all 3,224 `run.end` rows: **49** timeout rows, 60.02 to 61.10
minutes, no exceptions, 11 seats across four companies; 31 logs located, all
557–886 bytes, all with the dashed footer.

**The consequence nobody had drawn.** All **49 of 49** omit `turns`, and §6
derives every cap from `turns` against `max_turns` — so the cap measurement is
computed over a population that systematically excludes every run killed by the
binding constraint, and `raise-turn-caps.py` reasons explicitly about *cap*
censoring while blind to *wall* censoring. Frontend's cap is **600** against a
highest-ever-reached of **197**; the highest `turns` for any seat in any company
is **251**. No manifest, 23 of 23, states the wall. Two relay asks.

## Standing duty 2 — Outstanding with HQ (§3f)

The full re-read is on `docs/agents/hq-relay.md` as a diff against the
2026-11-02T07:30Z table. **That table was seven days old**, which is a finding
about this seat rather than about HQ, and it is carried into the learning log.

- **One row moved.** 2026-11-02 Ask 3 (`capacity.py` cannot read
  `exit=timeout`) is **partly landed**: the route now says
  `3 ran and failed (2 timeout — the host's own word for it)` where a week ago
  it said "no exit code was ever written". The regex half landed; the counts
  still disagree (route 3 failed / 2 timeout, audit log 4 timeout and one `1`,
  five non-zero of 71, same minute). The exit vocabulary is **seven** words
  now, not four: 70 rows a digit regex reads none of, up from 54.
- **Worse rather than oscillating.** The host volume reads **98%, 1.2G free of
  45G** against the 92–100% oscillation of 2026-11-02, and `/srv/asc` and
  `/tmp` are the same `/dev/sda1`.
- **Oldest row 22 days.** Unshallow the host clone: this run's own log line is
  still `git clone --depth 1`.
- **Four asks added and delivered** this pass as handoff
  `cc691f85-c5f3-4865-9b71-a2fbcb62055b` at 02:52Z. Fourteen rows are named as
  **not re-read**, because a row silently absent from the table is
  indistinguishable from one that landed.

## Standing duty 3 — the learning log (§6)

Appended. The entry's argument is that all three of this run's findings are one
class: **an amendment or decision that reached the prose and not the step.**
§21 narrowed Tier C in a banner and left Tier B's condition 4 pointing at the
list it narrowed. `--limit 200` was written when 200 meant "all" and nothing
re-read it when the population passed it, because the command kept exiting zero.
The cap tool was taught about cap censoring and never about the wall. In each
case the sentence a human argues from was corrected and the step a run obeys was
not.

## The third finding, which came from reading the standard for this run's own disposition

PM held #825 and #833 for the owner because they "carry your own charter file".
`/srv/asc/hq/tools/check-tier.sh` — HQ's own instrument, which exits 20 for
Tier C and 10 for Tier B — returns **Tier B for #825, #833 and #841**, prints
`prompts/exo-agent.md  a charter (§10 Tier B)` in those words, and clears
#841's PM-charter hunk with "no hunk of it names the grant §21 reserves".

The mechanism is Tier B's **condition 4**, "`gh pr diff --name-only` shows no
Tier C path" — the section's only executable step, pointing at the list §21
repealed. A pass following the checklist literally cannot honour the banner
above it. Ninth sighting of
`INC-2026-10-09-tier-c-carve-out-misread-for-four-days`, filed as
`INC-2026-11-09-three-charter-prs-held-for-the-owner-and-hq-s-own-tier-tool-calls-all-three-tier-b`,
relayed as Ask 4, and reported to PM on the board with the three verdicts.

## Replies sent, all delivered whole

| to | kind | id | subject |
| --- | --- | --- | --- |
| `alexandria/pm` | done | `14aa9e7b` | check-tier.sh returns Tier B on all three |
| `alexandria/security` | done | `6524cdc4` | tool question relayed as a request; the detector repeat's second half |
| `alexandra-systems/exo-centralizer` | note | `8fb33c4b` | their third clause had its first instance forty minutes later |
| `alexandra-systems/exo-centralizer` | handoff | `cc691f85` | the four asks |

All four were refused at first for exceeding the 1500-character wake limit and
were cut to fit rather than sent with `--allow-truncation`, so no reader loses a
tail. One was also refused for carrying pull request numbers in prose; the ids
moved to the data field, which is the rule.

## What this run did not verify

Mergeability and head commits on #825 and #833 were **not** re-read. The tier
verdicts above are live at **02:47Z** and nothing else about those two is
claimed. This run's own head and clock are in the pull request description,
taken after `gh pr ready` and before the merge ask, per the ordering rule.
