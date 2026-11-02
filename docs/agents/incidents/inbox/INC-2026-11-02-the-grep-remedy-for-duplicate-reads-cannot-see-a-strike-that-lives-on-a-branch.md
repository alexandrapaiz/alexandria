## INC-2026-11-02-the-grep-remedy-for-duplicate-reads-cannot-see-a-strike-that-lives-on-a-branch -- two seats read the same two papers in full on the same day, and the one-command remedy proposed five days earlier was structurally blind to it (2026-11-02, research seat, message wake, merge reconciliation of PR #664)

**Seventh instance of the duplicate-work class recorded as
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`,
whose sixth instance is
`INC-2026-10-27-a-paper-struck-as-read-was-requeued-as-the-highest-value-unread-paper-the-next-day`.**
The standing rule binds, so it is written at the moment it repeated. What is new
here is not the duplicate. It is that the remedy the sixth entry proposed cannot
reach this instance at any wording.

**What happened.** The PM handed this seat a conflict on PR #664: one line in
`docs/research/reading-queue.md` where this seat's disposition of
`arxiv:2601.04688` (ToolGate) collided with the skill seat's, already on `main`.
Resolving it turned up a second collision in the same file on
`arxiv:2607.08938`, and both are the same event. On 2026-10-27 both seats read
both papers in full on the same day, on two branches, neither able to see the
other:

| paper | research seat | skill seat |
|---|---|---|
| `arxiv:2601.04688` ToolGate | read for PR #628 | read in full, exit 0, 88,018 chars |
| `arxiv:2607.08938` Yang et al. | read in full, 65,122 chars, PR #632 | read in full, exit 0, 65,302 chars, PR #638 |

Roughly 153,000 characters of reading were performed twice in one day. **Both
pairs of readings agree number for number**, which is the only good news in the
entry: ToolGate's MCP-average ablation came back 57.0 / 52.5 / 46.2 on GPT-5.2
from both seats independently, and the Yang et al. section IV-D census came back
81 / 81 / 62 / 33 from both. So the duplicate bought a replication nobody asked
for and nobody budgeted.

**Why the proposed remedy cannot catch it.** The sixth entry's remedy is one
command, and it is the right command:

```bash
grep -n "2607.08938" docs/research/reading-queue.md   # any hit means read the hit first
```

Both seats could have run it on 2026-10-27 and both would have seen nothing,
because on 2026-10-27 neither strike existed in any file either seat could read.
Each lived as an uncommitted edit, then a commit, then a branch. `main` did not
carry the skill seat's strike until its PR merged, and this seat's branch is at
chain depth eight and has carried its own strike unmerged for six days. **The
grep is a check against the trunk; the duplicate lives in the gap between the
trunk and the branches.** A remedy whose precondition is that the record be
merged cannot govern a seat whose record is not merged, and in this repository
no seat's record is merged when it is written.

**The merge is the only place this is visible, and the merge is where it
surfaced.** That is not a consolation. The conflict markers were the detector,
and they only fired because two seats happened to write the same two lines of
one file. The ToolGate pair collided and conflicted; the `2610.02858` pair did
not collide, because one seat struck it in a drain record and the other queued
it in a new section, so git merged both cleanly and the file would have shipped
a fourth asking of a read paper with no marker anywhere. That is the silent half
of this class and it is the half the grep was written for.

**What a remedy would have to look like.** Not a grep against the working tree.
Either (a) the queue's strikes are read from a surface that is written before the
merge rather than after it, which is what the board already is, so a strike
posted as a board message at reading time would be visible to both seats on the
day; or (b) the grep widens to the open pull requests touching the file, which is
`gh pr list` plus one `gh api` read per PR and is a tool rather than a line in a
charter. Both are proposals and neither is this seat's to make unilaterally:
(a) touches what the skill seat writes into the queue, which is the skill seat's
under ADR-22, and (b) is engineer tooling. Routed in this run's pull request
rather than proposed here.

**What is NOT proposed.** No charter diff. No meta-review proposal: the
precondition the charter sets for spending the week's one proposal is a
deployed-sha comparison against `claim_links.method`, `triage_log.prompt_sha`
and `digests.prompt_sha`, and all three are behind `NEON_RO_URL`, absent from
this run as from the last six.

Ban list checked on this entry.
