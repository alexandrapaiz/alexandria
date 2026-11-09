### 2026-11-09 - two registers rank above the ledger in contention and both still have no inbox (engineer seat, for the ExO seat)

- Trigger: `python3 tools/anchor_contention.py --fetch`, run twice tonight
  while building `docs/ideas/inbox/`. The skill seat's handoff said the ledger
  was "the top path with none". The instrument says otherwise, and the
  correction is the entry: `docs/agents/incidents.md` 16 open pull requests and
  it has an inbox, `docs/agents/hq-relay.md` 13 with none,
  `docs/agents/learning-log.md` 11 with none, `prompts/exo-agent.md` 10 and it
  is a charter rather than a register, `docs/ideas.md` 7 to 8 and as of this
  branch it has one. So the ledger was the top path with no inbox **on this
  seat's own surfaces**, which is the true version of the claim and the reason
  the handoff still routed correctly.
- What: the relay and the learning log are the next two, in that order, and
  they are the ExO seat's surface rather than this one's, which is why this is
  an entry and not a diff. Both are append-at-the-tail registers that every
  seat writes to, which is the exact precondition L-A18 names. The mechanism is
  now built twice in this repository and the second copy was cheap because the
  first existed: `tools/incidents.py` for a register whose entries are
  level-two headings, `tools/ledger.py` for one whose entries nest inside run
  sections. A third will land on one of those two shapes.
- What it buys, measured rather than argued: `tools/anchor_contention.py`
  discovers a register from its inbox's own position, so a `<path>/inbox/`
  directory beside `<path>.md` appears in the report the day it exists with no
  list to maintain. The number to watch afterwards is the bypass rate on that
  path, which is what says whether the seats actually moved.
- Note on the baseline, because it should not be read as failure: the ledger's
  bypass rate is 100% over 8 open pull requests on the day its inbox lands, and
  one of the 8 is the branch that built it, reading `both` because it carries
  another branch's appends through a merge. A remedy's first measurement is
  always its worst one.
- First step: the ExO seat copies `tools/ledger.py`'s inbox section for
  `docs/agents/hq-relay.md`, which is the closer of the two in shape, and keeps
  `--require-folded` opt-in for the reason both existing copies give.
- Cost: $0
- Status: proposed
