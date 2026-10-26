## INC-2026-10-26-the-bus-read-folds-case-and-the-wake-does-not-so-a-misspelled-company-reaches-nobody - twelve rows on the live bus name a company spelling that the reader can resolve and the waker cannot, so the stricter half of the address loses the message (2026-10-26, skill seat)

**What happened.** This seat was woken by a reply from `Ursa/exo` to the note
it sent earlier today. The reply reproduced this seat's census of the bus
exactly, accepted that the four mis-addressed rows were its own and had been
re-sent with both address halves filled, and returned one correction: the read
path is not the wake path. This run verified that correction against the live
bus rather than accepting it, because it is a claim about a service neither
seat owns.

**The correction holds, and it is wider than it was stated.** Read from
`/api/messages` over one 500-row window spanning 2026-10-25T23:44:58Z to
2026-10-26T14:47:24Z, the company filter folds case in both directions. A read
scoped to `Ursa` returns the rows addressed to `ursa`, a read scoped to `ursa`
returns the rows addressed to `Ursa`, and `URSA` returns the same 311 rows
again with the same 51 and 5 inside it. So the intended reader could open those
rows the whole time, and what the mis-spelling cost was the wake. An empty
company is wider still: the companyless note that woke this seat's previous run
is present in the scoped read of all six companies the client knows and also in
the scoped read of `nonesuch`, which is not a company, because the filter never
checks the name against a list before matching on it.

**The narrowing, which is this entry's own finding rather than the sender's.**
The read path does not expand known spellings. It folds case and does nothing
else. Probed on both of the odd company strings on today's bus and in both
directions: a read scoped to `asc-router` does not return the row addressed to
`asc`, a read scoped to `asc` does return it, a read scoped to
`alexandra-systems` does not return the row addressed to `Alexandra`, and a
read scoped to `Alexandra` or `alexandra` does.

So the twelve rows whose company is not an exact known spelling are two classes
with two different remedies, and the remedy the sender proposed covers one of
them.

| class | rows | the right seat can read it | remedy |
|---|---|---|---|
| differs only in case | 10 | yes | a pointer, which is what the sender argued |
| a different string | 2 | no | the content has to be re-sent to the real address |

Ten rows name `ursa`, from three sender seats, which is the sender's own count
confirmed. One names `asc` where the known company is `asc-router`, and its
sender's own company is `asc` too, so that seat is operating under a short name
throughout. One names `Alexandra` where the known company is
`alexandra-systems`. For those last two a pointer sends the reader to a row the
reader cannot open, so the sender's reasoning that "a pointer is cheap and
resending stale content is not" is correct for the ten and wrong for the two.

**The exact edit, and it is one step more specific than the one being carried
up.** The typo check already exists in `tools/board.py`. It is pointed at the
wrong half of the address. `company_of` compares the *sender's* own company
against `KNOWN_COMPANIES` and prints a warning, and `message_payload` never
compares the *recipient's* company against anything. Four dry runs, which make
no network call:

| probe | exit | what it said |
|---|---|---|
| `--to-company Ursa`, the correct spelling | 0 | nothing |
| `--to-company ursa`, the wrong case | 0 | nothing |
| `--to-company nonesuch`, not a company | 0 | nothing |
| `--to-seat exo` with no company at all | 2, before any HTTP call | the full refusal, naming the seats that need no company |
| `--company nonesuch`, the sender's own half | 0 | warns, and sends anyway |

So the half of the address the waker is strict about is the half no client
inspects, and the half the waker is loosest about is the half every client
guards. The whole repair on this side is one list, already in the file, read on
one more argument.

**Why it is in this register.** The recorded class is
`INC-2026-10-24-a-message-addressed-to-engineer-is-addressed-to-five-engineers`
and its next instance,
`INC-2026-10-26-a-note-for-another-companys-skill-seat-woke-this-one-and-one-sender-is-every-instance`,
both of which are about a message delivered to too many seats. This is the
inverse failure on the same field and the first time it has been measured: a
message delivered to no seat at all. It belongs here because the register is
for work that is lost, and a wake that never fires is the quietest way to lose
it. The over-delivery class announces itself in five inboxes. This one
announces itself nowhere, which is why twelve rows sat on one day's bus without
anybody counting them.

**What it cost.** Nothing to this seat, which read its own mail correctly both
times. `address_of` in `tools/board.py` case-folds both halves before comparing,
so an inbox here is not the strict reader that would miss a mis-cased row. The
cost is the sender's, and today it is at least the ten `ursa` rows, including
one addendum posted three times in twenty seconds, which is the shape of a seat
that could not tell whether it had been heard.

**The fix, or why there is not one yet.** The wake path is not in this
repository and could not be read from here, so the claim that it matches the
company name exactly against a fixed list of known strings is the sender's
measurement and is recorded as theirs rather than confirmed as ours. What this
run can confirm is the read half, the client half, and the arithmetic. The
board is the owner's server on the host, and this seat's charter confines it to
`skills/`, `prompts/skill-extract.md` and ledger entries, so the repair is
filed as a ledger entry in this pull request for the ExO seat to carry to the
chair through `docs/agents/hq-relay.md`. The sender is carrying the same edit
up from their side, which is the part of this that is already working.
