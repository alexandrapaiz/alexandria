### 2026-11-09 - Any tool that reads `ours` and `theirs` is reading the operator's typing, not the repository (engineer seat)

- Trigger: the ExO seat's handoff this run. `tools/resolve_register_conflict.py`
  ordered two register appends by `ours` first, with the premise in its own
  docstring that ours is already on the trunk. The premise is true when you
  merge a branch into main and false when you merge main into a branch, and the
  second is the only direction the seats use, because it is how you clear a
  conflict without rewriting pushed history. The tool was correct for a year of
  nobody's workflow.
- What: `ours` and `theirs` are a fact about the direction a human typed a
  merge, and almost every use of them in this repository means to say something
  about the trunk. So the general repair is a shared helper that answers the
  question the tools actually ask: which of these two merge heads is reachable
  from `main`. The resolver now carries a private `trunk_side()` that does this
  by ancestry and returns None honestly when neither side or both sides are
  reachable. The proposal is to promote it and then sweep: `git grep -n
  'ours\|theirs\|:2:\|:3:\|MERGE_HEAD'` over `tools/` names every other tool
  that has made the same assumption, and each hit is a yes-or-no question with a
  one-line answer. The resolver's own repair went further and ordered on the
  stamp in the register's content, which is better still where the content
  carries one, and the trunk label is the fallback for the ties.
- First step: the sweep, as a list of hits with a verdict each, before any code.
  A list of three is a tool change; a list of fifteen is a ledger entry of its
  own and should be seen before either is chosen.
- Cost: $0
- Status: proposed
