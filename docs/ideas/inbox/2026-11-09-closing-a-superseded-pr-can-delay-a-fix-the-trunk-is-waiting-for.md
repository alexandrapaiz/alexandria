### 2026-11-09 - closing a superseded pull request delays any trunk-clearing fix it carries by the length of the superseding run (skill seat, for the PM)

- Trigger: this run followed its charter's supersede clause exactly and the PM
  overrode it, correctly. #861 was this seat's own READY pull request carrying a
  one-line `duplicate-status` repair for a red `main`. The charter says to merge
  the older branch into the new one, say so, and **then close the older one
  yourself**. This run did that at 05:35:02Z, with a comment telling the merger
  that "the one-line repair now lands via #865 instead." The PM reopened and
  merged #861 at **05:38:20Z**, three minutes later, and `f979969c` put the
  repair on `main`. That was the better call and this entry exists to say so in
  a place the charter's next reader will find.
- What: the supersede clause is right about review cost and silent about trunk
  state. Its whole argument is the 2026-09-30 count, 27 review items of which 10
  were already dead, filed as
  `INC-2026-09-30-superseded-prs-are-left-for-the-owner-to-close`. That argument
  holds for an ordinary superseded branch. It inverts when the older pull request
  is **green, READY, and the only carrier of a fix the trunk is red without**,
  because closing it moves that fix from a pull request a merger can take now
  into one that cannot be taken until the superseding run finishes, is reviewed
  and is merged. This run began at about 05:37Z and this entry was written an
  hour and a half later, so the cost of the clause being obeyed here would have
  been a red trunk for that whole window, against three minutes for the override.
  Nothing was actually lost, because `main` and this branch hold the same commit
  `e67bd731` rather than two copies of one change, so the overlap is free.
- The narrower point, which is the useful one: **"supersedes" and "carries the
  only copy of a trunk fix" are independent properties and the clause only reads
  the first.** A seat can check the second cheaply. It already knows what its
  predecessor's diff repairs, because the clause makes it read that diff before
  choosing.
- First step: one sentence in the supersede clause of every charter that carries
  it, and it is the PM's to accept before it is anyone's to write, because a
  charter edit changing what this seat may do is not this seat's. Close the
  older pull request **unless it is green and READY and carries a repair the
  trunk is currently red without**, in which case say so at the top of the new
  description, leave it open, and let the merger take both. The proof command the
  clause already requires, `git log --oneline origin/<older> ^HEAD` printing
  nothing, is unaffected: this adds a condition on closing, not on superseding.
- Cost: $0
- Status: proposed
