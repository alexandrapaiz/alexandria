### 2026-11-09 - The register append tool stamps one seat's name by default, and it has not fired yet (security seat, message wake, for the engineer seat)

- Trigger: sweeping `tools/` for hardcoded seat defaults after finding one in
  the mail auditor, this run found that `tools/incidents.py` defaults `--seat`
  to `engineer`, and that the value is written straight into the heading of the
  entry the tool creates. So any seat filing an incident without the flag
  stamps the entry as the engineer's, in an append-only register whose entries
  are cited by id across charters and run notes.
- The measurement, because the risk is not the finding: of 287 entries in the
  register's inbox, 145 carry a parseable seat in their heading. Six of those
  name a seat different from the commit that added the file, and all six of
  those commits are authored by the owner's merge identity rather than by a
  seat, so all six headings are correct. No misattribution has actually
  happened. The default happens to match the seat that files most often, which
  is why eleven months of filings have not surfaced it.
- So this is latent and low, and it is written down because the next thing that
  changes is which seat files most often. The register's own gates do not catch
  it either: `tools/incidents.py check` reports nothing malformed on this tree,
  because a heading naming the wrong seat is well formed.
- What: resolve the seat from `ASC_SEAT`, and refuse rather than substitute
  when nothing says who is filing, which is already `tools/board.py inbox`'s
  behaviour for the same question. A register append is a write, so the
  argument for refusing is stronger here than in the read-only case filed
  beside this one.
- One observation that is not part of the ask: the other 142 inbox entries
  carry no seat in the shape the tool's own skeleton writes. Anything keying on
  that heading format therefore reads about half the register, which is worth
  knowing before a gate is built on it.
- Cost: $0, and under an hour including the test.
- Status: proposed
