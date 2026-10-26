## INC-2026-10-26-the-seats-own-pull-request-descriptions-are-owner-facing-prose-and-no-gate-reads-them - the ruling that codes never reach the owner names pull request descriptions by name, and three of this seat's last five break it (2026-10-26, writer seat)

**What happened.** The owner's ruling of 2026-09-27 is in
`docs/voice/taste.md` in her words, "i dont want to see adrs, for me its just
random codes. id rather have good descriptions", and the recorded ruling names
the surfaces it binds: "in everything she reads, Slack bullets, PR opening
bullets, the board, a decision is named by what it decides, never by its
number". It permits codes inside the repository, where a seat cites one to
prove a judgment already exists, and requires the sentence that reaches her to
translate the code into the decision it recorded.

Measured over this seat's pull requests in the last sixty opened on the
repository, three of five descriptions carry a code in prose: #560 carries
four, #550 three, #544 two. The four on #560 were written by writer run 56
about ninety minutes before this entry, by the same run that then found them,
and #560's description is the one a merger reads to decide whether three runs
of editorial work ship.

```
ADR-, L-A, "incident N", "ban list N", section marks, INC- ids
  #560   4   #550   3   #544   2     of 5 writer descriptions
```

**Why it is in this register.** The standing rule fires on the repeat, and the
class is already here.
`INC-2026-09-30-finance-ledger-never-checked-against-ban-list` records three
finance runs writing owner-facing prose the house voice register already
banned, with none of them opening the file, and its own text calls finance "a
fifth seat now shipping owner-facing prose". This is a sixth surface, and the
distinguishing fact is that the writer seat is the one that owns the register
being broken.

The ruling predicted it. Its own recorded text says NOT YET GATED, in those
words, and names a live contradiction inside another seat's charter on the day
it was written. That was twenty-nine days ago. Both halves of this repository's
two-gate rule are visible in one place: the ruling was written down by the
right seat into the right register within the hour, and nothing between the
ruling and the artifact has ever opened the file.

**What it cost.** Nothing a reader paid for, because these are descriptions
rather than issues. What it cost her is the thing the ruling was given about:
three of five descriptions from the seat that owns the voice register asked her
to carry a number instead of a decision. The narrower cost is credibility of
the gate list. This seat's shipping step names seven registers and runs them
against the artifact in `docs/voice/` and `prompts/`, and the description is
written after the last of those checks, in a different tool, with nothing
reading it.

**The fix, or why there is not one yet.** Run 56 translated all four codes out
of #560's description by hand and its own description carries none, which is
one artifact rather than a gate. The gate is the part that is owed, and it has
a shape: the voice checks in `docs/voice/check_voice.py` already read
reader-facing surfaces from a glob list, and a description is not a file in the
repository, so the check would have to take a body file as an argument and run
before `gh pr create` or `gh pr edit`. That is this seat's own surface and it
is the natural next run's work, filed here rather than started, because run 56
reached this finding after its diff was already coherent and a gate added in
the last turns of a run is the thing this register is full of.

One scope note for whoever builds it. The ruling permits codes in repository
files, so the gate reads the description and never the register, and a check
that swept `docs/agents/incidents.md` for code strings would flag the correct
use of every entry in it.
