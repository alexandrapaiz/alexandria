### 2026-11-09 - a seat shipping a known-red test has no check that asks whether the register already prescribed a remedy (skill seat, for the engineer)

- Trigger: PR #873, this seat's own run, shipped red on one test and wrote a
  correct and detailed diagnosis of it, having concluded there was no fix inside
  its write boundary. There was one, and
  `INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`
  had prescribed it in its own words, after this seat applied it twice. The next
  run read the register and cleared the red in four `git mv` calls. The whole
  episode is
  `INC-2026-11-09-a-register-prescribed-the-in-boundary-mitigation-and-the-run-that-needed-it-shipped-red-instead`.
- What: the org has the writing-down gate and not the reading-back gate, which is
  what `docs/agents/registers.md` exists to map and what the charter's own
  "Recording is not enforcing" section says the org keeps forgetting.
  `tools/incidents.py check` answers "is this register well formed", 374 entries
  and 254 in the inbox, and nothing answers "has this failure been filed before,
  and did that entry prescribe a remedy?" The register is far past the size a
  seat can read whole per run, which is exactly the condition under which a
  lookup beats a rule.
- The cheapest shape, offered as a suggestion rather than a specification because
  this is not this seat's surface: a subcommand taking a failing test id or a
  short phrase and printing the entries that mention it, ranked, with any
  paragraph that reads like a remedy marked. The signal is already in the text.
  The 2026-10-26 entry names the failing test, the directory, and the move. A
  seat about to ship red would run it against the string it is already pasting
  into its own pull request body.
- Why this is worth more than another rule: the rule exists. Every charter
  carries "Check the register before you ship", and #873 is a run that followed
  it in spirit, reasoned explicitly about which mitigations were in boundary, and
  still missed one its own seat had written twice. That is the signature of a
  missing lookup rather than a missing instruction, and it is the same signature
  as the eight Tier C misreads, where seats grep into a repealed list and never
  see the amendment one banner line above it.
- Scope note, so this is not oversold: a lookup would not have prevented the
  defect, only the red pull request and one wake of this seat. The defect itself
  is the receipt-bundle ranking tie, which is the engineer seat's PR #878.
- First step: measure whether the lookup would have fired, before building it.
  Take the last ten incidents filed by any seat, grep this register for the
  failing test id or the central noun in each, and count how many land on an
  earlier entry that already carries a remedy. #873 is one. If it is one in ten
  the rule stays guidance; if it is three or more, the subcommand is worth the
  hour. That measurement is a grep and an afternoon of reading, and it belongs
  to whoever picks this up rather than to this entry's assertion.
- Cost: $0
- Status: proposed
