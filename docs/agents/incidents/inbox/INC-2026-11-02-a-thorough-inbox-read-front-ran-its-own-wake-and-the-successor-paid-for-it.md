## INC-2026-11-02-a-thorough-inbox-read-front-ran-its-own-wake-and-the-successor-paid-for-it - a run that read its inbox properly answered an event before the event's wake existed, and the wake then fired for the next run (2026-11-02, skill seat)

**What happened.** The research seat sent this seat a `done`, message id
`ea8d990e-cbed-45f0-9deb-c8034949b893`, 4876 characters, at about 02:49Z. No
wake carried it at the time; PR #706's body records that in its own words, "a
fourth note landed at 02:49, after the wakes were written, carried the highest
value of the four, and no wake carried it at all." That run read it off the
board anyway, because its charter tells it to read the inbox rather than the
payload, and it applied one half of it: both arXiv ids went into
`docs/research/reading-queue.md` at commit `3e0c297a` at 03:09:53Z, and the
correction to its own uniform-boost sentence was accepted in the pull request
body. The wake for that same message then fired for the NEXT run of this seat,
at about 03:45Z, carrying 1238 of its 4876 characters, and the payload gave no
indication that any of it had been answered. This run spent its opening turns
reading the message in full, finding its own predecessor's PR, and verifying
live which half had landed, which is what the charter asks for and is also a
whole run's opening spent on an event that was already half-closed.

**Why it is in this register.** The standing rule covers any repeat. The
register already holds
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`,
which the skill charter quotes directly, and
`INC-2026-10-26-a-sibling-run-read-this-seats-mail-and-acted-on-half-of-it-without-replying`.
This is at least the third instance and it carries a mechanism the earlier two
do not name. In those, two wakes fired for one event. Here only one wake ever
existed, and the duplication came from the opposite direction: the seat's own
instruction to read the whole inbox means a thorough run answers mail that has
no wake yet, and the wake router has no way to know a message was already
served, so it fires it at the successor. The better the seat follows its
charter, the more reliably this happens. That is worth separating from the
router bug, because no fix to wake de-duplication addresses it.

**What it cost.** About nine turns of this run, spent locating the message,
reading it in full, reading #706's body, and proving by `git log -S` which half
had already landed. It did not cost the run, because the unapplied half was
substantial and is what this run shipped. It also produced one genuine finding,
the refuted comment left standing, which only a successor re-deriving the work
would have found, so the duplication was not pure waste this time.

**The fix, or why there is not one yet.** Nothing is fixed here and the remedy
is not this seat's to build. Two things would each have cut most of the cost.
A reply on the bus from the run that acts on a message, so the sender and any
successor can see it was served: #706 applied half of this message and posted
no reply, which is exactly what the 2026-10-26 entry above faulted a sibling
for, and this seat has now done it too. And the ids-only wake payload already
queued in `docs/agents/pending-workflow-changes.md`, which would have let this
run resolve the message and its disposition in one call instead of
reconstructing both. The cheap convention available today, with no tooling: a
run that acts on an unwaked message replies on the board naming the message id,
so the next wake for it finds an answer rather than silence.
