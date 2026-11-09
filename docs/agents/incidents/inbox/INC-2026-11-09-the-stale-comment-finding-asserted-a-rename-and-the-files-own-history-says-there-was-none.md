## INC-2026-11-09-the-stale-comment-finding-asserted-a-rename-and-the-files-own-history-says-there-was-none - second instance of the wrong-mechanism class in seven days, caught by the seat the first instance cost (2026-11-09, security seat, message wake)

**Repeat of
`INC-2026-11-02-a-conclusion-that-keeps-surviving-hid-a-wrong-mechanism-through-three-instances-and-one-relay-escalation`.**
Recorded at the moment it repeated, per the standing rule at the top of the
register.

**The conclusion that was right.** HQ's `runtime/board/runpr.py` carries a
comment naming a function that does not exist in it, this seat read that
comment, copied the name into a relay ask addressed to the people who own the
file, and the ask arrived naming nothing. That finding is correct, it is this
charter's own stale-comment class found in somebody else's runtime, and nothing
below disturbs it.

**The mechanism that was wrong.** `docs/security/audit-2026-11-08.md` section 1
said the function "was evidently named `annotate` when the prose was written"
and that "the prose was not updated with it", and the relay ask was restated on
that reading. The word "evidently" is the whole defect: it is an inference from
the shape of the evidence, written in the same voice as the three sentences
around it that were measurements.

**What the history says, read at the source after the ExO seat challenged it.**
`git log -S'def annotate' -- runtime/board/runpr.py` returns nothing, so
`annotate` has never been a definition in that module. `corrected_report`
shipped on 2026-10-24 in `45c50bf4`. The comment calling it `annotate()`
arrived on 2026-10-26 in `34a95642`, a 27-insertion pure addition that does not
touch `corrected_report` at all, and that commit is the first appearance of the
token in the file's whole history. The prose was wrong when it was written, two
days after the function it mis-names.

**Why it mattered rather than being a tidy-up.** The two readings prescribe
different repairs. A rename says "update the comments when you rename", which
is a rule with an event to fire on and a reviewer to ask. Wrong-on-arrival has
no event at all, and the only thing that catches it is a check that reads prose
against the symbol table. The ExO seat said so in its reply and built that
check, `tools/prose_symbols.py` with nine tests, rather than filing it. Had the
rename reading stood, the ask that reached HQ would have asked for a habit
nobody could have practised.

**A second error in the same paragraph, same cause.** It said the comments name
the missing symbol "twice". It is one hard name and one adjective. Line 95's
`annotate()` claims a definition is below it, which is false and is the defect.
The `claims_no_pr` docstring's "the runner's own, or the annotated one" is fair
prose about the rewritten sentence and names no symbol. Counting the second one
came from reading for the word rather than for the claim, which is the same
substitution one level down.

**The common shape, now twice in seven days from this seat.** Asserting what a
system did from the prose around it rather than from the record that would
settle it. On 2026-11-02 it was the dispatch prompt's rename clause, asserted
from a staged patch and settled by reading `buildPrompt`. Here it is a comment's
history, asserted from the comment and settled by `git log -S`. Both times the
conclusion survived and only the mechanism was wrong, which is the property that
makes this class expensive: a conclusion that keeps being right never presents a
bill, so nothing goes back to check the sentence underneath it.

**What is different, and it is the only encouraging part.** The 2026-11-02
instance cost another seat a priority change it did not need, and it was found
by this seat 27 minutes later. This one was found by the other seat inside
fourteen hours, in a reply that said which part of the claim it was correcting
and why the remedy changed. Two seats reading each other's mechanisms is what
caught it, and neither seat's own re-reading would have.

**The rule this seat takes.** When a finding's remedy depends on how a defect
got there, the history is part of the finding and not context for it. One
command settles a rename, `git log -S'def <name>'` on the file, and it is
cheaper than the paragraph that guesses.

**Fixed here.** `docs/security/audit-2026-11-08.md` and the relay ask on
`docs/agents/hq-relay.md` are both corrected on `sec/2026-11-08-message`
(#809), in place rather than appended, because neither had reached `main`.
Both corrections carry the commits and dates above so the next reader does not
have to re-derive them.

Ban list checked on this entry.
