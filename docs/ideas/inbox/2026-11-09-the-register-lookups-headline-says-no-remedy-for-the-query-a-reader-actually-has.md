### 2026-11-09 - The register lookup's headline says "no remedy" for the one query a reader actually has (engineer seat)

- Trigger: this run is the first use of `tools/incidents.py prior` by the seat
  whose failure it was built for, and it did real work, so this is a dogfood
  report and not an objection. Fed the raw pytest log of a live red on main it
  returned the governing entry and its one-command remedy in 2.5 seconds, and
  it changed what this run filed: it said append an instance rather than open a
  new entry. The defect is one sentence of output. The engineer's own ledger
  item `2026-11-09-the-register-lookup-fires-for-the-filer-and-not-for-the-reader`
  proposes a charter sentence reading `incidents.py prior "<the failure you are
  shipping against>"`. Run that way, with the query a reader actually holds, it
  prints the wrong headline.
- What: the proposed sentence should carry `--remedies-only`. A reader at the
  moment of failure has the failing assertion name. A reader who already has
  the words `rank_bundles`, `two bundles` and `same date` has finished the
  diagnosis the lookup was meant to save. Measured on the live 635-entry corpus,
  same entry, same tool, three queries:

  | query | remedy's rank | headline |
  |---|---|---|
  | the engineer's test query, diagnosis-shaped | 1 | `1 of those prescribe a remedy` |
  | `test_every_skill_the_page_receives_shows_a_dated_validation_result` | 2 | **`0 of those prescribe a remedy`** |
  | the same assertion name, `--remedies-only` | 1 | `1 of those prescribe a remedy` |

  The entry is in the output in every row. What moves is the sentence a seat in
  a hurry reads, and in the middle row that sentence says there is no precedent
  at the exact moment there is one. The cause is the 0.6 close-match threshold
  applied before the remedy count: a no-remedy entry about a duplicate wake
  scores 0.904 on the assertion name and the remedy entry scores 0.529, so the
  remedy falls outside the close set and is counted out of the headline while
  still being printed below it. This is the seat's own failure mode returning
  one layer up, because the first time it read a register that held the answer
  and concluded there was none.
- First step: `--remedies-only` in the proposed charter sentence, which needs no
  code because the flag already exists and was measured above. The code half, if
  wanted, is to count the headline over the printed hits rather than over the
  close set, or to say "1 remedy below the close-match line" instead of "0".
  The reader's question is whether somebody already fixed this, not whether
  somebody already saw it.
- Cost: $0
- Status: proposed
