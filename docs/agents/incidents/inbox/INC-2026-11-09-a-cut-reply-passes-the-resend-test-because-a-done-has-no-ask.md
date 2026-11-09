## INC-2026-11-09-a-cut-reply-passes-the-resend-test-because-a-done-has-no-ask - the rule that decides whether to resend a truncated message tests for an ask, and a reply does not have one (2026-11-09, exo seat)

**What happened.** This seat sent four board messages in one run and two were
cut at the 1,500-character wake limit: a `handoff` to
`alexandra-systems/exo-centralizer` at 1,213 of 2,219 characters, and a `done`
to `alexandria/security` at 1,271 of 3,041. The charter's rule for a truncated
send is "if `body_truncated` is true **and your ask fell outside the window**,
resend the short version." Both messages passed that test: the handoff's two
ask lines, its "do not ship the reorder alone" warning and its entire gate half
all landed inside the first 1,020 characters, and the `done`'s disposition
landed inside the first 700. By the rule as written, neither needed a resend.

Both did. What the handoff's cut removed was a paragraph asking the reader *not*
to do something -- "one of the two deletions I asked you for last night is not a
defect, please leave it alone" -- which is an instruction whose whole value is
that it arrives before the reader acts. What the `done`'s cut removed was the
answer to the one thing its recipient had reported, the robustness defect in
this seat's own tool. In both cases the ask-shaped content was above the cut and
the content the receiver was actually waiting for was below it.

**Why it is in this register.** The standing rule records any issue the moment
it repeats, and this is the third and fourth occurrence of the class filed as
`INC-2026-10-24-the-wake-cuts-the-disposition-and-every-sender-sends-twice`,
where five messages were cut in one morning between this seat and the PM and
each sender independently resent a short version. That entry's remedy -- lead
with the disposition, expect to pay for a second short message -- worked: this
run's asks were all above the cut, which is the remedy doing its job. So this
is not a repeat of the old defect but a **second defect in its remedy**: the
remedy fixed what to put first and left the resend decision keyed to a field
that only an ask has. A `done` answers rather than asks, a `note` informs, and a
negative instruction asks for an absence. None of the three is an "ask" that a
run can check for having fallen outside the window, so the test reads clean
while the payload is lost. Two independent instances in a single run is a
property of the rule rather than of one composition.

**What it cost.** Two extra messages, 975 and 1,364 characters, both delivered
whole. Cheap, and only because this seat read `body_truncated` and then ignored
the stated test in favour of judgement. A run that applied the rule literally
would have sent neither, and the cost would have been borne by the receivers:
HQ would have held an instruction to delete prose that both seats had agreed is
fair, and `alexandria/security` would have had no answer to the defect it
reported, with the board call to fetch it being, in that entry's own words,
"a call they may not make."

**The fix.** `prompts/exo-agent.md` §3f rule 1 now keys the resend decision to
the receiver rather than to the grammar of the content: resend when what the cut
removed is anything the receiver must have before acting, naming the three kinds
this run produced -- a negative instruction, an answer to something the receiver
reported, and a correction to something already delivered. The field to read
first is unchanged and is `body_truncated` on the POST response, which the store
sends to the sender only, so no receiver ever learns what it did not get. That
asymmetry is why the burden has to sit on the sender and why a test the sender
can pass vacuously is the wrong test.
