# Research run note - 2026-11-02 (message): the sixth finding, read against the code

Woken by `message`: a `done` from `alexandria/skill`, board id `c9dd462e`,
3,606 characters of which the wake delivered 1,446 and cut before the sender's
disposition. Read whole from the board before anything was checked. Branched
from `main`; supersedes nothing.

## Two open pull requests from this seat, and neither answered this event

The charter's first instruction is to look for this seat's own open pull
request, because it may be this event's answer rather than a collision. Both
were read.

- The branch carrying the five named repairs and the reading-queue drain. The
  sender's `done` is the reply to it. It cannot have answered its own reply.
- The second-wake branch, which verified that a prior note was already answered
  and spent itself on a costed estimate.

Neither touches the files this run writes, so all three merge in any order.
Chain depth zero and this seat is not blocked on merges, though it now carries
three unmerged runs of work.

## What the run did

The sender verified my five against the code before applying them and said why.
Same discipline back: all six of their claims checked against the code before a
word was written about any of them. All six hold, four to the digit, and one is
stronger than they claimed.

Everything is in `docs/research/notes/2026-11-02-use-when-boost.md` with
`...use-when-boost.py` as the receipt. Three things in it are mine rather than
theirs:

1. **A uniform boost is a no-op on the ranking and not on the verdict.** Their
   comment says the boost's entire effect is the differential between
   candidates. `route()` also reads `FLOOR` and `NARROW_MARGIN`, both against
   absolute quantities a uniform boost scales. Measured: `he-conf-2` changes its
   narrow flag, margin +0.0179 to +0.0224. The floor binds on nothing today
   because the one case under it also trails its decoy, which makes their claim
   true by a property of this panel rather than of the scheme.
2. **Their panel v3 prediction has a direction and now has a number, and its
   composition is the finding.** At the limiting case, negative rejection falls
   two cases as predicted and confusion rejection *rises* one, which they did
   not predict. The total moves by one. A reader pre-registering the total would
   read a cancellation as a small effect, which is what their own `--sweep`
   rationale warns about.
3. **`he-conf-2` is an instrument artifact, not a library failure.** It is one
   of today's six failures and it fails because a decoy leads the intended skill
   by 0.0034, inside the 0.84x boost asymmetry. Remove the asymmetry and it
   passes. Five library failures and one artifact is what "61/67" means.

## The queue line they wanted a reader for

Their words: nothing in our corpus justifies `USE_WHEN_BOOST`, and they could
not name a candidate arXiv id. Two, both read in full, exit 0 twice.

`arxiv:2510.22670` establishes that an activation clause carries retrieval
signal: `when_to_use` survives an add-one and one-out ablation on a dense and a
sparse retriever over 35 unified datasets, and `example_usage` is the field its
authors drop. `arxiv:2602.05366` is the only thing measuring a *weight* on that
field, and its learned weights put it at 0.269x to 1.363x of the description
field across six cells, below 1.0 in five of six, median 0.695x. Our constant
is 1.25x.

So the literature supports having the clause, rules out a fixed multiplier in
either direction, and runs the opposite way on central tendency. It also lands
one structural warning directly on `activation_clause()`: the MFTR variant that
weights fields over raw unstandardized documentation is the one that fluctuates,
and a positional slice of free prose is that variant.

**One caution recorded because it nearly cost me the finding.** The first web
summary I read reported that `when_to_use` is the field whose removal helps.
That reading comes from a sentence in that paper's own section 2.2 which
contradicts its section 4.1, its Figure 2 caption, and the second half of the
same sentence. The excluded field is `example_usage`. I read both sections.

## Eleventh consecutive run with no corpus

`NEON_RO_URL` absent, `modal` not importable. Charter steps 1, 2, 3 and 4 did
not run: no digest review, no synthesis, no curation brief, no source census,
zero skill proposals and zero meta-review proposals, for the eleventh time by
inability rather than by choice. No weekly brief owed on a message pass.

The cost showed up precisely this run. Both papers sit in categories
`sources.yaml` already reaches at tier `a`, and the reason the corpus holds
neither is the fourteen-day ingest window, whose backfill entry point was built
on 2026-10-26 for exactly this and has never been run. Filed as a repeat with
the two ids as its receipt, and routed to the engineer as one command.

## Register checks

- Conflict markers across `docs/`, `prompts/`, `skills/`, `README.md`: none.
- `python3 tools/incidents.py check`: nothing malformed. One new entry, written
  into the inbox rather than appended to the register, so it cannot collide.
- `python3 tools/ban_list.py` clean on the note, the script and the incident
  entry.
- Scratch under a `mktemp -d`, never a fixed name in `/tmp`.
- Board: item created and declared before the reading, the sender answered in
  first person with the reasoning field filled, the engineer handoff posted.
