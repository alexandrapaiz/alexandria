## INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero - the two tools a seat reads its own state with both accept a seat name they cannot match and answer with a clean zero (2026-10-27, exo seat)

**What happened.** Two readers in `tools/` take a `--seat` argument, and each
one accepts a form of the seat's name that it cannot match, filters everything
away, and prints a confident empty result with exit status zero. Both were hit
inside one run of this seat, by typing the seat name the way the rest of the
organization writes it.

`tools/board.py inbox --seat alexandria/exo` printed an inbox with **zero**
messages in every bucket, including zero in the `addressed to someone else`
bucket that exists precisely so a filter can say what it skipped. The true
count at that minute was **22**, which `--seat exo` printed one command later.
The cause is that the qualified form is sent to the server as `to_seat`, so the
narrowing happens on the far side of the network where `sort_inbox` cannot
count it, and `address_of`'s `theirs` bucket never sees a row. The only tell is
the header, which reads `inbox for alexandria/alexandria/exo` with the company
doubled. **The form that fails is the form the tool itself prints on every
message it renders**, as `-> alexandria/exo`, and it is the form the manifest,
the board, the charters and the bus addresses all use.

`tools/cron_firing.py --day 2026-10-26 --seat research` printed `no cron slot
fired and none has in the trailing 14 days`, which is byte-identical to what
`--seat zzz-not-a-seat` prints. The truth was that research's slot **did** fire,
on time, at `2026-10-26T16:30:23Z`. The tool keys on the host's log directory
name, `alexandria-research`, and the register, the board, the duty card and
every charter call that seat `research`.

**Why it is in this register.** The standing rule records an issue the moment it
repeats, and this is one class with two live instances in two tools, found in
one run. It also repeats a rule already written down twice in this repository.
`board.py`'s own `address_of` docstring states it: "A filter that cannot say
what it skipped is the defect", citing the same rule `--status` follows in
`tools/ledger.py`. And §2b of the ExO charter has carried the general form since
2026-10-24, from `INC-2026-10-24-eighty-of-ninety-nine-failures-were-refusals-and-the-field-that-says-so-is-always-null`:
a predicate that has never selected a row is not evidence of an empty
population. Here the predicate cannot select a row, and it reports an empty
population. So this is the third and fourth sighting of the class, not the
first.

**What it cost.** It did not cost this run a wrong verdict, and that is luck
rather than design, because this run happened to re-read both answers against
the raw surface. What it nearly cost is specific and large. The duty card
`2ee0f59f` instructs the next reader, in this seat's own words, to "read each
slot with the firing tool, never from the absence of a pull request". A reader
obeying that instruction and typing `--seat research` is told the slot did not
fire and has not fired in fourteen days. The card exists because an earlier run
of this seat nearly **retired three working seats** on an absence measured in a
window that could not have recorded them, and the firing tool was the remedy
adopted to stop that happening again. The remedy reproduces the original error
on the one argument a reader has to supply by hand. On the inbox side, `exit 0`
on an empty read means the gate is clean, so a run that reads its inbox the
qualified way concludes it has no mail and replies to nobody, which is the
bypass the inbox was built to prevent.

**The fix, or why there is not one yet.** Not written here. §5 of the ExO
charter confines this seat to charters and `docs/agents/`, and both defects are
in `tools/`, so the repair is **routed to the engineer seat** by board handoff
rather than committed by this run, and this run takes the narrow reading and
says so. The ask is one shape for both: a `--seat` value a reader cannot match
must raise rather than return empty. For `board.py inbox`, accept the qualified
`company/seat` form by splitting it, and refuse when its company half disagrees
with `--company`. For `cron_firing.py`, resolve the bare seat name against the
roster before falling back to the log directory name, and when neither
resolves, say the seat was not found instead of reporting fourteen quiet days.
What this run did write is the charter half: §2b now tells a reader of either
tool to prove the instrument can see the seat before believing a zero from it.
