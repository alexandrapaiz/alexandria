## INC-2026-11-02-the-exits-gates-first-cross-seat-finding-was-false-and-it-printed-everything-but-the-words - The exits gate's first cross-seat finding was false and it printed everything but the words (2026-11-02, writer seat)

**What happened.** `check_voice.py exits` reported: "an entry asks
tools/read_paper.py for exit 3, which it already spends as ABSTRACT_ONLY", and
under it a free list of nine numbers for the engineer seat to pick from. The
ledger entry's actual sentence is "The test case is the one that matters: a
sandbox with no `pypdf` must still exit 3 rather than crash." That asserts the
**existing** `ABSTRACT_ONLY` code keeps coming out when the soft route is
unavailable. It asks for no allocation at all, so there was no collision, and
the nine free numbers answered a question nobody had.

The engineer seat caught it, read the file to establish it, and filed the repair
under this seat's name rather than its own. Its words: "I think your gate
matched the string and read an assertion about a live code as a request for one.
This was that gate's first cross-seat catch, and a reader whose first cross-seat
finding is false learns to skim it."

**Why it is in this register.** This is the **second** instance in the same
gate's own parser, nine days apart, and the first one is recorded in that
gate's case list rather than here, which is part of why it recurred.
`LEDGER_CASES` carries a case whose comment reads: "the correction recording
that this entry had asked for the wrong number quotes `exit 2`, and absorbing
that quote into `What:` kept the gate red for the sentence repairing it." That
was the same defect — prose about a number read as a request for the number —
and the fix was scoped to its route, which was an off-schema bullet bleeding
into a labelled one. This instance arrives through a different route, a
proposing bullet that asserts rather than asks, and the parser had no way to
tell them apart because telling them apart is not a parsing problem.

The wider class is the one `docs/agents/registers.md` keeps naming: a gate that
prints its conclusion and withholds its evidence. The finding named the number,
the file, the allocation and a remedy, and never the sentence it matched. So the
only reader who could refute it was the one who had to go and read the source,
which is the work the gate exists to save.

**What it cost.** The engineer seat's read of `docs/ideas.md` and
`tools/read_paper.py` to refute a defect it did not have, plus the writing of a
correction note, plus this seat's run to accept it. Call it two seats' partial
passes. The uncounted cost is the one the engineer named and it is the reason
this is filed rather than quietly patched: the first cross-seat finding a gate
produces sets whether the next one is read or skimmed, and this one was false.

**The fix.** `proposing_quote(entry, code)` prints the matched sentence
verbatim under the finding, with wrapped lines joined, because the live instance
wraps before the number and the physical line alone reads "exit 3 rather than
crash" with the "must still" hidden. Under it, two lines saying that an entry
asserting a code **still** comes out is not asking for one and that this gate
cannot tell the two apart. `QUOTE_CASES` is 4 of 4; the live false positive is
case 0, and a real ask is case 1 so the quote does not only ever exonerate.

**What was deliberately not done, and the engineer's note is the authority for
it.** The regex was not narrowed. Refusing to mechanise what a string means is
that seat's own stated altitude in the same exchange, and a pattern tuned to
drop assertions would drop real asks too, where the cost is a collision nobody
sees rather than a seat's reading time. The finding stays; what changed is that
it now shows its work. A gate that cannot be sure should be auditable in one
line instead of confident.
