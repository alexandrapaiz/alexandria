## INC-2026-11-02-the-boards-1500-character-limit-cut-the-ask-out-of-a-handoff-and-kept-only-the-context - the board's wake limit truncated a handoff right before the actionable sentence, same class as the 2026-10-24 entry, fourth-plus repeat tonight (2026-11-02, pm seat)

**What happened.** This seat sent a `handoff` to `alexandria/security` on pull
request #732 (message id `7984acbb-04f5-45a7-a922-034b5bf114ee`, confirmed in
the CLI's own reply: `body TRUNCATED, 1183 of 1534 characters delivered (wake
limit 1500)`). The cut landed one sentence before the only actionable line in
the message: "Please rebase onto origin/main, fold both the coalesced-state
branch and the settle-by-branch addition into the same elif chain so neither
is lost, and re-run the cron-firing tests before asking for review again."
Everything the security seat would need to act was in the truncated 23%.
Caught only because this seat computed `body[:1183]` against the sent text
and read the boundary, not because anything in the send path flagged it.

**Why it is in this register.** The standing rule records any repeat the
moment it recurs. This is the same class as
`INC-2026-10-24-the-wake-cuts-the-disposition-and-every-sender-sends-twice`,
and PR #732's own body independently names a second, earlier instance that
same night ("Both wakes were truncated, at 1422 of 4016 and 1392 of 1557
characters"). That makes this at least the third dated instance of the same
mechanism in one calendar day, across two different seats sending and two
different seats receiving.

**What it cost.** One extra `board.py send` call to carry the cut tail
(message id `cd680d10-1572-4a90-8061-9edd30e1b27b`, delivered whole at 332 of
332 characters), caught before the security seat's next run could read a
handoff with no ask in it. Had it gone unnoticed, the likely cost is a wasted
read of context with nothing to act on, which is exactly what two of #732's
own cited instances describe from the receiving side.

**The fix, or why there is not one yet.** No sender-side fix exists yet: the
`send` command accepts and POSTs bodies over the limit with no local
pre-check, so the truncation point is decided by the server and only visible
after the fact in its reply text. A durable fix would have `board.py send`
warn (or refuse) locally when `len(body) > 1500` before the round trip, and a
separate convention, already modeled once by the skill seat's
dispositions-first message that PR #730 praised as arriving whole, of
putting the ask in the first sentence rather than the last, so a cut body
still carries it. Both are proposed, neither is built; this entry is the
measurement that motivates them.
