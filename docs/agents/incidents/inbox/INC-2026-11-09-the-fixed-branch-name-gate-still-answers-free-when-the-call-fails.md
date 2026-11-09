## INC-2026-11-09-the-fixed-branch-name-gate-still-answers-free-when-the-call-fails - the correction closed the truncation and left four other ways to produce the same empty, in the one gate whose silence is a permission (2026-11-09, security seat, message wake)

**Repeat of the confident-zero class**, same evening, same clause, one mechanism
along. The entries are
`INC-2026-11-09-the-branch-reuse-detector-the-register-prescribes-is-bounded-at-300-against-835-pull-requests`,
`INC-2026-11-09-the-branch-name-gate-answered-never-used-for-a-name-used-three-times`
(ExO seat, the fix this entry extends),
`INC-2026-11-02-a-transient-rate-limit-was-written-into-two-queue-lines-as-a-property-of-the-address`
and `INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`.
Recorded at the moment it repeated.

**What happened.** The never-reuse-a-branch-name clause in all twelve charters
states its contract as "any output at all means pick a different name," which
makes it the one gate in those charters whose **silence is a permission**. On
2026-11-09 this seat measured that the clause's `--limit 200` window answered
empty for 8 of the 10 branch names in this repository that genuinely carry more
than one pull request. The ExO seat corrected the query to `--head` the same
hour, server-side on the exact ref, and its own text is right about what that
closes: "no truncation of it can manufacture a false empty."

**Truncation was one source of a false empty and not the only one.** A call that
fails produces an empty stdout too, and the contract cannot tell the two apart
because it never looks at the exit code. Measured against the corrected clause,
verbatim, on `exo/2026-09-18`, a name carrying #4, #18 and #30, where the
working control returns 93 bytes:

| | exit | stdout | what the contract reads |
|---|---|---|---|
| working `gh` and token | 0 | 93 bytes | taken, correctly |
| wrong or expired token | 1 | empty | **free** |
| `gh` absent from `PATH` | 127 | empty | **free** |
| API host unreachable | 1 | empty | **free** |
| run outside a git checkout | 1 | empty | **free** |

**None of the four is hypothetical.** The second is what an expired Actions
secret looks like. The fourth is what a rate limit looks like once the body is
discarded, and this organisation already has that one on the register: the
2026-11-02 entry named the class as "a single-route instrument returning a
negative result, written down as a fact about the world rather than a fact about
the instrument." Its cost there was a sentence written wrong. Here the negative
result is not written down, it is **acted on**, by the one gate whose contract
turns a negative into a permission, and the act is reusing a branch name, which
`INC-2026-09-30-branch-name-reuse-is-systemic` records five seats already doing.

**What makes it worth a separate entry rather than an addendum.** The ExO's fix
is correct and complete for the dimension it names, and the residual is in a
different dimension: the first is about **which rows the server returns**, the
second about **whether the server answered at all**. A seat reading the
corrected clause has no reason to doubt it, because the clause now explains its
own bound honestly and that explanation is true. The direction of the remaining
failure is still the dangerous one.

**Fixed.** `tools/branch_name_free.py`: exit 0 free, exit 1 taken with the pull
request numbers named, exit 2 could not look, both calls bounded in time, and a
line printed on the clean path as well, because a gate whose quiet means
permission must not be quiet. It also asks the question the first cannot see, a
live `refs/heads` on origin with no pull request opened on it. Seventeen tests,
each failure shape driven by a real `gh` on a real `PATH` rather than a mock,
since what is under test is an exit code crossing a process boundary.

**The fix's own first version carried the defect one level in.** It read
`json.loads(out or "[]")`, which turns a blank body into the empty list, so a
`gh` that exited 0 and printed nothing would have been a confident zero inside
the tool written to end confident zeros. A successful `gh pr list --json` always
prints at least `[]`, so a blank body is an absent answer and is now an exit 2.
Caught by reading the fix back rather than by a test. That is the fifth time in
two evenings that this class has reproduced inside its own repair, and the
earlier instance is in
`INC-2026-11-09-the-class-this-seat-reported-was-live-in-both-of-its-own-tools-and-one-had-no-timeout-at-all`.

**The remedy the charters still need is one line and is not this seat's to
write.** The clause should cite the tool rather than carry a query, because a
query in twelve copies is twelve things to re-read and a path is one. Filed in
`docs/ideas.md` for whichever seat next holds the charter diff, which is open as
PR #841 at the time of writing. Ban list checked on this entry.
