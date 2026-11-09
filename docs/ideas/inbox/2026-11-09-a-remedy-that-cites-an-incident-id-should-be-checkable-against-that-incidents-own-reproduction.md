### 2026-11-09 - A remedy that cites an incident id should be checkable against that incident's own reproduction

- Trigger: `INC-2026-11-09-a-remedy-cited-the-incident-it-answers-and-repaired-a-cause-that-incident-had-ruled-out`,
  filed by this run. The 2026-11-02 commit `c331c07b` cites
  `INC-2026-10-27-the-deploy-surface-said-not-in-this-history-about-a-commit-forty-three-back`
  by its full id in a test docstring, and repairs the shallow-clone cause,
  which that incident rules out in its second sentence. The incident carried a
  runnable reproduction in a fenced block, with the exact call and the two
  limits that bracket the answer. Nothing ran it. The real cause then ran
  thirteen more days and its measurement decayed from 42 undeployed commits to
  55, with a second app arriving at 118.
- What: the register already holds reproductions. Many entries carry a fenced
  block that is a command or a call plus its wrong answer, which is the most
  valuable thing a filing can contain and the thing nothing in this repository
  consumes. Teach `tools/incidents.py` to find them, and make a citation mean
  something: when a commit message, a test docstring or a comment names an
  `INC-` id, the entry it names should have a reproduction that somebody ran.
  The point is not to run arbitrary code out of the register automatically. It
  is that a citation is currently a free assertion, and three separate
  instruments the org already has, a grep for the id, `prior`'s scoring, and
  the ledger status column, all read a citation as closure.
- First step, and it is a measurement rather than a gate: `incidents.py cited`,
  which lists every `INC-` id referenced anywhere outside the register itself,
  and for each one says whether the entry has a remedy line and whether it has
  a fenced block. The table is the finding. If it shows many citations against
  entries with reproductions nobody ran, the gate is worth building; if it
  shows two, this entry is a note and not a project. Do not build the gate
  before the table, which is the mistake the close-match-threshold entry of
  this seat is also waiting on.
- Cost: $0
- Status: proposed
