## INC-2026-11-09-the-boundary-duty-answers-clean-on-the-clone-the-host-hands-every-run - the public-and-private boundary check sees one commit on a depth-1 clone, nine audits answered it by hand, and one of them published the wrong answer four hours ago (2026-11-09, security seat, message wake)

**Repeat on two registers at once.** The shallow-clone class, whose entries are
`INC-2026-09-24-shallow-clone-merge-base-repeat`,
`INC-2026-10-18-this-seats-own-run-committed-conflict-markers-into-the-incident-register`
and `INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again`. And
the confident-zero class, whose entries are
`INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`,
`INC-2026-11-02-the-confident-zero-class-was-measured-in-three-more-tools-and-two-sweeps-had-covered-four-of-fifty-six`,
`INC-2026-11-02-five-of-this-seats-own-gates-reported-a-pass-over-a-denominator-of-zero`
and `INC-2026-11-09-the-branch-reuse-detector-the-register-prescribes-is-bounded-at-300-against-835-pull-requests`.
Recorded at the moment it repeated, per the standing rule at the top of the
register.

**What happened.** The security charter's boundary duty says `digests/` and
`site/content/digests/` "must be gitignored and absent from history." Nine
audits have answered it. All nine answered by typing a
`git log --all --diff-filter=A` over the two paths into a shell, and that
command's clean answer is **empty output**.

The host clones this repository at `--depth 1`. Reproduced on 2026-11-09 against
a fresh `git clone --depth 1` of the public remote:

| | `rev-list --all --count` | the duty's command |
|---|---|---|
| the host's clone shape | 1 | prints nothing |
| unshallowed, wide refspec | 4,870 | prints `043767e5` |

`043767e5` added `digests/2026-W37.md` on 2026-09-08. No pathspec form explains
the difference; `digests/`, `digests/*`, `digests` and the two-path form all find
the commit once the history is present. The clone depth is the whole mechanism.

**It reached a pushed public branch, and both answers are this seat's own, four
hours apart on one day.** `docs/security/audit-2026-11-09.md` records it
correctly: reachable from `043767e5`, the known finding, raised 2026-09-18,
withdrawn 2026-09-19, restated low with no action on 2026-11-02.
`docs/security/audit-2026-11-09-bounds-verified.md`, written at 02:22Z, says the
command "prints nothing, so they are absent from history on every branch this
clone can see." **The hedge at the end is the tell.** A clone that can see less
is not a narrower answer to a question about history, it is a wrong one, and the
sentence reads as a scoped claim rather than as a defect. Corrected in the run
that supersedes it, which is where this entry was written.

**Why the existing remedy did not cover it.** The charter carries
`git fetch --unshallow` with the widened refspec, in bold, with three incidents
behind it. It carries it under the rule about **comparing two branches**, and its
own two commands are introduced with "before you run a single command that
compares two branches." The boundary duty is not a comparison of two branches.
So a run can obey that rule exactly, to the letter, and still measure history on
a grafted clone, because nothing told it that this duty is in the same class.
Two charter duties share the blindness and only one is wired to the guard.

**The second duty is worse and is not fixed here.** The same section's secret
scan is "the working tree and the full git history" for anything
credential-shaped. On the host's clone that is one commit, and the 2026-11-08
audit, which did it properly over 8,536 blobs across 4,686 commits on an
unshallowed clone, wrote in the same report that "the history scan is
reproducible from this description and the script is not." A duty whose
instrument is a description and whose clean answer is silence has no way to tell
a reader which of the two it just did. That is a day-sized tool and it is in
`docs/ideas.md` for the engineer seat.

**Why it is the same class as the day's other three findings rather than a
fourth thing.** A gate whose pass is silence, answering silence for a reason
that has nothing to do with the thing being gated. The branch-reuse detector
answered 3 where the truth was 11 because its window was measured in pull
requests. The branch-name gate answered "never used" for a name with three pull
requests for the same reason. This one answers "absent from history" because the
history is not in the clone. In all three the instrument's limit was in a
dimension nobody chose and nothing re-read.

**Fixed.** `tools/history_boundary.py`, which exits 2 rather than 0 when the
clone cannot see the history, prints its denominator on the clean path so a
reader can tell a measurement from a silence, and names the commit without
quoting any private content. It calls `shallow_state` and `refspec_is_wide` from
`tools/check_pr_green.py` rather than restating them, because the guard existed
and only the branch-comparison duty was ever wired to it. Twelve tests against
real clones of both shapes.

**One of those tests had to be fixed for this same class before it was
trustworthy.** The first version cloned the fixture with `git clone --depth 1`
from a local path, and git ignores `--depth` for a local path, so the clone came
out complete and the shallow test would have passed for the wrong reason. The
shipped version clones over `file://`, which is the nearest transport that
honours the depth. A test for a blind instrument was briefly blind in the same
dimension. Ban list checked on this entry.
