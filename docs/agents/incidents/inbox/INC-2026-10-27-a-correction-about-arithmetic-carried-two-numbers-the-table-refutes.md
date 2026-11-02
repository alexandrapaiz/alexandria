## INC-2026-10-27-a-correction-about-arithmetic-carried-two-numbers-the-table-refutes - a message sent to correct an arithmetic error carried its own, and a second line asserted a comparison a table plainly contains (2026-10-27, research seat, hook run)

**What happened.** At 01:40Z the skill seat sent this seat a `note` (board id
`e2c34faf`, PR #638) whose purpose was to return a routed correction on the
grounds that its arithmetic did not survive the table. It was right, and this
run verified it live before accepting it: Table 2 of `arxiv:2609.09134` gives
six evolved-harness edits, base Qwen at 98.7 / 93.5 / 96.4 / 100.0 / 98.2 /
30.8 and SFT-imitation Qwen at 91.2 / 89.6 / 91.7 / 99.0 / 97.5 / 76.1, so the
means are 86.27 and 90.85 exactly as sent, adoption rises 4.58 points, and this
seat's replacement sentence — that a team watching aggregate adoption would see
it fall — is wrong.

Two numbers in the same message are not.

1. **"The five that fall lose 21.1 between them."** They lose 17.8:
   −7.5, −3.9, −4.7, −1.0, −0.7. The message's own three figures are mutually
   inconsistent — 45.3 − 21.1 = 24.2, over six is 4.03, not the 4.58 it also
   states, while 45.3 − 17.8 = 27.5 over six is 4.58 — so the error is visible
   without the paper. `21.1` is a cell in Table **1** of the same paper, row 6,
   the Anom column of qwen3-coder-30b-a3b (SFT-imit.) under `h0`.
2. **"The zero-shot tau-bench arm reports no outcome-reward comparison at
   all"** (the same seat's queue line of the same run, against
   `arxiv:2609.04094`). Table 2 of that paper has an `Outcome reward` row with
   τ_B SR at p¹/p²/p³ of 17.6 / 11.0 / 9.3 against DRACO's 20.4 / 12.0 / 8.6.
   The comparison is there, it is the third split the question asks for, and it
   inverts the finding the question was asked to defend.

**Why it is in this register.** The standing rule records an issue the moment it
repeats, and this is the same class as two entries already filed today:
`INC-2026-10-27-a-queue-line-named-a-capability-benchmark-as-the-source-of-a-security-table`
and
`INC-2026-10-27-a-cost-figure-with-its-unit-and-its-backbone-still-inverted-the-cost-ordering`.
The class is a quantity asserted *about* a table by a seat that did not open the
table on that pass, in both directions between these two seats, in both a
message and a queue line. Neither instance here changes the conclusion it was
carrying — adoption does rise, and the paper's prose does restrict its widening
claim to AppWorld — which is exactly why both survived: a wrong supporting
number attached to a right conclusion has nothing to fail against.

**Blameless note.** Nothing cheap catches either one. The relayed-claim label
the engineer shipped would not fire, because both numbers came from the correct
paper. What caught them is the rule both charters already carry, which is that
the receiving seat re-reads the table rather than the message, and in this case
it cost one fetch of a paper already in `.cache/papers`.

**The repair, and it is narrow.** The grep rule the skill seat put in the
reading queue's header covers an id. It does not cover a quantity. The
convention line already proposed in `docs/ideas.md` — a figure carries its unit
and its backbone or it is not written — should carry one more clause: **an
arithmetic claim carries the operands, not the result**, because the operands
are checkable against the table in one pass and the result is not. Both
instances above would have been caught by their own authors under that rule:
45.3 and 17.8 do not sum to the stated mean change, and a row named in full
cannot be said not to exist.
