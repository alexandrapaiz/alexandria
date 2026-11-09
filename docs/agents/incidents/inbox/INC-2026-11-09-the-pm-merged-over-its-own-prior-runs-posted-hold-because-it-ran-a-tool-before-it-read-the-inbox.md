## INC-2026-11-09-the-pm-merged-over-its-own-prior-runs-posted-hold-because-it-ran-a-tool-before-it-read-the-inbox - the fix for a misread was trusted over the seat's own just-posted decision not to apply it, and four merges had to be reverted (2026-11-09, pm seat, message wake)

**What happened.** This run's event payload named PR #849, #851 and the
standing draft #855. Before reading its own seat's board inbox, this run ran
`/srv/asc/hq/tools/check-tier.sh` against #851 and the three pull requests
`alexandria/pm` had been holding (#841, #825, #833), got Tier B on all four,
and merged all four plus #849 on the strength of that verdict.

The board inbox, read afterward rather than first, held two messages from
`alexandria/exo` at 04:02 and 04:06, both already answered by this seat's own
immediately preceding run (PR #856, concluded 04:14:37Z, exit 0, twelve
minutes before this run started): exo's own final position, after it had
itself run `check-tier.sh` and gotten Tier B two hours earlier, was "I am not
asking you to merge it" and "the three you hold stay yours to hold." PR #856
read the same diff, agreed the charter correction was real, and held all four
anyway on a second, independent ground - the standard's Tier B condition 4
still names the Tier C path list by reference, so a merger working the
checklist's letter refuses a charter diff regardless of the tool - and posted
a section 22 ask to the owner instead of merging, with a 48-hour clock
(`2026-11-11T04:10:55Z`) and this seat named as the applier on silence.

So the question "should these four merge" had already been asked and
answered, by the same seat, minutes earlier, and this run re-asked it of a
shell script instead of the inbox and got a different answer.

**Why it happened.** `check-tier.sh` is a real instrument and its verdict was
not wrong on its own terms; the incident it was built to fix
(`INC-2026-11-09-three-charter-prs-held-for-the-owner-and-hq-s-own-tier-tool-calls-all-three-tier-b`)
argues correctly that the Tier C path list is stale. What the tool cannot
see is that the PM's own prior run had already weighed the tool's answer
against the literal standard and the owner's reserved window, and chosen the
more conservative route on purpose, for content that is itself the rule
governing who may merge it. Running the tool answered a question nobody was
still asking and skipped the one check - the seat's own inbox - that would
have shown the question already had a different, considered answer in
flight.

**What this run did about it.** Reverted all four merges with
`git revert -m 1` against each merge commit, in reverse order (#841, #833,
#825, #851), confirmed with `git diff <pre-merge-sha>..HEAD` that the tree
matches the state right after #849 exactly for every file the four PRs
touched, and pushed the correction in the same pull request rather than a
second one. PR #849 itself was untouched and stays merged: it carries no
Tier C path and was never part of the disagreement. The four GitHub pull
requests stay marked merged - GitHub does not allow reopening a merged pull
request - so their content is recoverable only from the revert commits'
parents until the owner's ask resolves or the 48-hour clock lapses, at which
point the same diff is reapplied as a fresh pull request citing the
originals by number.

**The general shape.** A run with a live event payload and a tool that
answers its question fast will reach for the tool before it reaches for its
own seat's memory, because the tool is one command and the inbox is a read
with no guaranteed payoff. For a stateless seat the inbox is not optional
context, it is the only record that a near-identical question was already
asked and answered minutes ago. The order that would have caught this is the
one the charter already states elsewhere for a different reason - check for
your own seat's last open or recently closed work before acting - and this
is a second cost for skipping that check, not a new rule.

**STATUS: CLOSED.** The revert is verified byte-for-byte against the
pre-merge tree and shipped in the same run that caused the defect. The
section 22 ask #856 posted is unaffected and still governs: the owner's word,
or the 48-hour silence default naming this seat as the applier.

**Blameless note.** `check-tier.sh`'s verdict and the incident recommending
it are both still correct about the tier question in isolation. The failure
here is sequencing - which question got asked first - not a wrong tool or a
wrong charter.
