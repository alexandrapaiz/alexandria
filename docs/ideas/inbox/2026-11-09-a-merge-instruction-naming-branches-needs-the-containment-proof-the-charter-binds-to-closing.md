### 2026-11-09 - A merge instruction that names branches needs the containment proof that is bound only to closing (skill seat)

- Trigger: this seat told a merger, in a pull request body, to take the
  engineer's open pull request "or mine alone", on the belief that its own
  branch carried the engineer's work because its own merge commit named the
  engineer's branch. The engineer checked and corrected it: the branch this seat
  merged was superseded by the engineer's own later one, so "mine alone" would
  have dropped thirty two commits of theirs, including the register lookup this
  seat had asked them to build. Re-proved here after the correction, with the
  refspec widened first: their tiebreak branch is absent from neither branch,
  their current branch has **38** commits absent from this one and this one has
  **81** absent from theirs. Neither contains the other, so there was no "or"
  available and the instruction was wrong in whichever direction a merger took
  it.
- What: every charter in this repository carries
  `git log --oneline origin/<the-older-branch> ^HEAD   # must print nothing`
  and binds it to one act, closing a superseded pull request. It is not bound to
  the act that caused this, which is telling a merger which branches carry which
  work. The two acts rest on the same fact and only one of them is gated, which
  is the shape `docs/agents/registers.md` already names: a register with a write
  gate and no read gate. The failure mode is also worse than the gated one,
  because closing a pull request is reversible with `gh pr reopen` and a merger
  acting on a wrong instruction has already landed a tree that drops work. The
  engineer filed their own instance of this from the other side, as the proof
  command being bound to closing rather than to informing a merger, so this is
  the second seat to hit it in one day and the two reports agree on the gap.
- First step: one sentence in this seat's own charter, in the section that
  already requires naming the merge order when a branch is not superseded: a
  merge order that names another seat's branch is printed with the containment
  proof run in both directions, and a branch that is not contained is never
  described as optional. That is a charter diff rather than code, so it is held
  by the unamended path list in the parent standard's Tier B checklist and goes
  up as an ask rather than being written here. Named here so the next run of
  this seat does not re-derive it. The cheaper half, available today and taken
  by this run, is simply to run the proof in both directions before writing a
  merge order, which cost three commands.
- Cost: $0
- Status: proposed
