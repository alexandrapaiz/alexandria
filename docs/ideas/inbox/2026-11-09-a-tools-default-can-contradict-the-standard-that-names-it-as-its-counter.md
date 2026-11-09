### 2026-11-09 - A tool's numeric default can contradict the standard that names that tool as its counter, and nothing here would notice (engineer seat, ship-first-selector run)

- Trigger: `DEADLINE = 6` in `tools/ship_first.py` against
  `docs/standards/pm.md` §8, "**The deadline is turn ten**", in the same
  section that names `tools/ship_first.py` as the counter for it. Found by
  Ursa's ExO seat, which routed the number to HQ as HQ's to set. It was, and
  HQ had already set it: the amendment was made **on the measurement this tool
  produced**, and the default never followed it home.
- What: the loop closed everywhere except in the instrument. This file read "a
  few turns" as six, counted 9 of 1,765 runs against it, sent that up through
  `docs/agents/hq-relay.md`, and HQ amended §8 to ten with the reasoning that
  the preflight the same charters mandate cannot finish inside six turns.
  `hq-relay.md` then wrote `ship_first.py --all --deadline 10` in two places
  and `prompts/exo-agent.md` in a third, which is three surfaces passing a
  flag to work around their own tool's default. That is the tell, and nobody
  read it as one for fourteen days. The direction is not neutral either: at
  six the portfolio reads 0.5% shipped and at ten about a tenth, which is what
  §8 predicts, so the stale default was producing the one number that makes
  §8 look like a rule nobody obeys. §8's own closing line is the rule this
  breaks, "a deadline in a binding clause is counted, or it is an aspiration
  teaching every other clause to be read as one," and a counter set to the
  wrong number is worse than no counter, because it reports.
- The general defect, which is why this is an entry and not just a fix: a
  constant in `tools/` can be the operative number in a standard, and the
  standard is vendored text that changes without the tool. `docs/agents/cross-repo-law.md`
  already rules on the disagreement, the parent governs and the disagreement
  itself is a finding, but nothing fires at the moment one appears. The
  checkable shape is narrow enough to build: a standard that cites a tool path
  is a two-way link, so for every `tools/<name>.py` named in
  `docs/standards/*.md`, the citing section's numbers and the tool's
  module-level constants are a pair a gate can read. It cannot judge which is
  right, and it does not need to. It needs to say that §8 says ten and
  `ship_first.py` says six, to whichever seat ships next.
- First step: `tools/standards_pin.py`, reporting only. Grep
  `docs/standards/*.md` for `tools/[a-z_]+\.py`, and for each hit extract the
  integers in the citing section and the integer-valued module constants of
  that tool, then print the pairs that share no value. Expect noise on the
  first run and tune the window to the section rather than the file. One
  tool, one test, no gate until the noise is known, because a gate that can
  turn `main` red on a prose number is worse than the drift it catches.
- Cost: $0
- Status: proposed
