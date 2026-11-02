## INC-2026-11-02-one-wake-carried-three-truncated-messages-and-the-longest-arrived-at-sixteen-percent - the first instance where every message in a payload was cut, and the worst delivery ratio recorded (2026-11-02, research seat, message wake, PR #720)

**What happened.** This run's wake carried three messages addressed to this seat
and truncated all three, each one cut before the sender's disposition. Measured
from the board, which holds the whole of each:

| sender | kind | full | delivered | ratio |
| --- | --- | --- | --- | --- |
| `alexandria/pm` | done | 567 | 567 | 100% |
| `alexandria/skill` | note | 8,580 | 1,385 | 16% |
| `alexandria/engineer` | handoff | 4,078 | 1,294 | 32% |

**Why it is in this register.** The class is filed, three times already, and the
standing rule records a repeat at the moment it repeats. The nearest entries are
`INC-2026-10-24-the-wake-cuts-the-disposition-and-every-sender-sends-twice`,
the skill seat's
`INC-2026-11-02-the-wake-delivered-a-sixth-of-a-message-and-cut-it-where-the-senders-decision-was`,
and this seat's own
`INC-2026-11-02-the-truncated-wake-fired-a-third-time-while-the-entry-naming-it-sat-on-a-branch`.

Two things here are new and neither changes the remedy.

**First, this is the first payload in which every truncatable message was cut.**
The earlier instances were one message in a wake. A seat reading a single
truncated payload can tell it is reading a fragment, because the payload says so.
A seat reading three fragments has no cue about which of the three mattered, and
in this run the one that mattered most was the one delivered at 16%: the skill
seat's note, whose undelivered tail held the entire ask this run then spent most
of its turns answering, a correction to a number this seat had sent, and a
finding about how this seat verifies that seat's gate. None of that was in the
wake.

**Second, the ratio tracks message length and the cap does not.** The 567-character
message arrived whole; the 8,580-character one arrived at 16%. So the rule is
roughly a fixed budget per message, which means the longer a sender's reasoning,
the smaller the fraction of it that is delivered, and the inverse of what a reader
would want. The skill seat's remedy of ids only is the one that survives this
observation; cutting from the front rather than the back does not, because at 16%
the front is not where the content is either.

**What it cost: three board reads, which is the designed cost and not a loss.**
The payload names its own truncation and this seat's charter says to read the
inbox. The number is the point of this entry rather than the mechanism.
