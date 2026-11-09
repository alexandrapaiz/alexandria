### 2026-11-09 - the charter that prints the ledger contract still names the tail append the inbox replaces (engineer seat)

- Trigger: this run built `docs/ideas/inbox/` and then read the ledger contract
  printed at the bottom of its own charter. It says "Append today's new ideas
  and the competitive-scan note to `docs/ideas.md` on the same branch", and
  then spends a paragraph on what to do when another open pull request appends
  to the same file. That paragraph is the defect the inbox removes, and it is
  still the instruction the seat reads.
- What: measured rather than assumed, because the first draft of this entry
  guessed eleven and the number is one. `grep -l 'Status: proposed' prompts/*.md`
  returns exactly `prompts/engineer-agent.md`: one charter of twenty prints the
  entry contract, and it is the one that also spells out the tail append and the
  two-PRs-at-one-anchor workaround. Nine charters name `docs/ideas.md` as a
  write surface without printing the contract, so they inherit whatever the
  contract says. None of the nine mentions the inbox, because it did not exist
  when they were written. A seat following its charter exactly now bypasses the
  remedy, which is the shape
  `INC-2026-10-27-the-register-anchor-conflicted-seven-times-in-two-days-and-its-inbox-has-no-gate`
  already recorded for the incident register: that inbox landed, the charters
  kept saying append, and the anchor needed a keep-both resolve seven times in
  the thirty-nine hours after. The same thirty-nine hours are ahead of this one
  unless the instruction moves.
- Why it is not in this pull request: `prompts/` is charter surface and this
  seat's charter forbids including a charter edit in its daily pull request.
- First step: replace the append sentence in `prompts/engineer-agent.md`'s
  ledger-contract section with `python3 tools/ledger.py --inbox-new <slug>`, and
  leave the collision paragraph in place, because it still governs every
  register that has no inbox. The other nine need nothing if the contract they
  inherit is the one that moved. Whoever merges it can prove it took by running
  `python3 tools/anchor_contention.py --fetch` a day later and reading the
  ledger's bypass rate, which is the number this entry is about.
- Whose call: the owner's merge, since charters are hers. Under section 22 of
  `docs/standards/pm.md` the PM may post it as an `ask` carrying a
  recommendation and proceed after forty-eight hours of her silence.
- Cost: $0
- Status: proposed
