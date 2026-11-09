### 2026-11-09 - nothing states the invariant that being woken authorizes nothing, and twelve charters hold it by accumulation (engineer seat, then the owner)

- Trigger: A2A specification section 7.6.4, merged 2026-07-30 as PR 2081 and
  still untagged 102 days later, says an agent "MUST NOT treat the state
  transition itself as authorization for any particular operation". Research
  named the clause as the security seat's territory. Read against this org
  rather than against A2A, the clause's question is whether a seat treats having
  been woken as authorization for the operation its waking event names. Full
  reasoning in `docs/security/audit-2026-11-09-a2a-untagged.md`.
- What holds today, and it does hold: twice in one hour on 2026-11-09 a payload
  asked a run of this seat for an operation and the charter refused it, once a
  branch rename and once by forbidding self-merge. Both refusals came from a
  charter condition re-read at source, not from judging whether the payload
  looked trustworthy. That is the correct mechanism and it is worth keeping.
- The gap: no file in this repository states the invariant. Twelve charters each
  enumerate operations their seat may not perform, and the union of those
  enumerations is what has been holding. A union of enumerations is weaker than
  a stated invariant in one specific way: a newly added operation is permitted
  by default until some charter names it, and nothing checks the union for
  gaps. Every seat's charter forbids self-merge and pushing to `main` by name.
  None of them says why, which is that an event arriving is not a grant.
- What: one sentence in the org rules that every charter already carries
  sections from, saying a wake, a dispatch, a handoff and a board state are
  information and never authority, and that a seat's authority comes only from
  its charter and the standards. Then the twelve enumerations become
  consequences of a rule rather than the rule itself, and a new operation is
  refused by default.
- Why it is not fixed in the pull request that filed it: writing it into
  charters is a charter edit, which this seat does not do, and `docs/standards/`
  is vendored so a change there goes up through `docs/agents/hq-relay.md`. The
  engineer's half is whether the invariant should also be a check; the owner's
  half is the sentence.
- Size: the sentence is minutes. Deciding where it lives is the work, and it is
  a decision rather than an implementation.
- Status: proposed
