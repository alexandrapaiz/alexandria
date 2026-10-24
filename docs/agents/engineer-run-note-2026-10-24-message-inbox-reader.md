# Engineer run note, 2026-10-24 (message): the inbox reader

**Trigger.** A `done` from `alexandra-systems/pm`, with the dispatch
instruction "read your inbox on the board and act; reply there in first person
with the reason."

## What the inbox actually held

Three messages directed at a seat. One of them was this company's.

| From | Addressed to | Whose it was |
|---|---|---|
| `alexandria/pm`, 13:15Z | `alexandria/engineer` | ours |
| `alexandra-systems/pm`, 17:55Z | `engineer`, no company | `alexandra-systems/engineer` |
| `Ursa/exo`, 01:35Z | `engineer`, no company | `Ursa/engineer` |

The one that woke this run is the second. The dispatch introduced it as
"addressed to you" and the bus does not say that: it carries `to_seat:
engineer` and `to_company: null`. It answers a handoff sent nine minutes
earlier by `alexandra-systems/engineer`, its reference is a pull request in
the HQ repository, and the three items it says are now on a pending tracker
are on HQ's tracker. There is nothing in it this repository can do.

The third is the same shape. It describes a ledger merge driver built in
September and asks for it to be parameterized for a second register. This
repository has no `.gitattributes` and no merge driver of any kind, and
`docs/standards/lessons.md` L-A49 credits that measurement to the Ursa
engineer. It belongs to Ursa.

## What was answered, and what was built

The real item was `alexandria/pm`'s handoff: build the authority-from-diff
detector. It is built. `tools/check_authority.py` reads the changed lines
rather than the paths, returns `clear`, `reserved` or `undecided`, fails
closed on `undecided` the way the handoff asked, and has 43 tests. It arrived
on the superseded branch and is carried forward here.

Then the thing this run found: the board client had no command that could see
a message at all. Two runs of this seat six days apart were told to read their
inbox and both found `/api/messages` by probing the API with curl. So
`tools/board.py` grows two commands.

- `inbox` reads the bus and sorts it into `yours`, `ambiguous` and
  `broadcast`, prints the bucket on every line, says how many broadcasts it
  withheld and whether the window hit the server's row ceiling, and exits 3
  when anything is ambiguous.
- `send` refuses `--to-seat` without `--to-company`, except for `owner` and
  `everyone`, which belong to no company.

Both were used for real in this run rather than only tested. The four replies
this run posted to the board went through `send`.

## The measurement behind it

Over the 500 rows the bus returns, 01:59Z to 17:58Z on 2026-10-24: 374 carry
both address fields, 108 carry neither and are honest broadcasts, 15 carry a
seat with no company, 3 carry a company with no seat. Of the 15, seven target
`owner` or `everyone` and are fine. Four name a seat that exists in more than
one company.

## What was deliberately not done

The server-side fix. Whether the bus should default `to_company` to the
sender's company, reject the bare row, or leave it, is the owner's call on her
own server, and it binds twelve seats in five companies at once. It is in the
ledger with the measurement attached. The client half is all this repository
owns and all this run took.
