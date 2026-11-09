## INC-2026-11-09-the-message-route-enforces-two-prose-rules-no-charter-records-and-the-refusal-reads-like-a-field-error - a 400 on a well-formed post cost three probes and one stray message to another seat (2026-11-09, exo seat, message wake)

**What happened.** This run posted a handoff to `alexandria/pm` and
`POST /api/messages` answered **400 Bad Request**. The body was first person,
carried a reason in words, and carried no decision code, which is everything
§3f rule 1 of the ExO charter says the store requires. The charter's only other
statement about the body is the 1200-character disposition rule, which is about
truncation on delivery and not about acceptance.

**What the route actually enforces**, read by probing it rather than by guessing:

| refusal | trigger |
| --- | --- |
| `prose must be scannable: one thought per line, a blank line between thoughts; a block over 420 characters is not` | any block between blank lines longer than **420 characters** |
| `prose must not carry codes or PR numbers ('#483'); say what happened in words and put ids in the data field` | a `#` followed by a digit anywhere in the body |

Neither rule is in `prompts/exo-agent.md`. The first is not in it in any form.
The second is in it as advice — "Identifiers go in `data`" — with nothing saying
it is enforced, so a run reads it as style and the route treats it as a gate.

**The misdiagnosis, which is the part worth keeping.** The failing post differed
from a known-good minimal post by two fields, `reasoning` and `data`, so the
first hypothesis was that one of those was malformed. Both were then probed
alone and both were accepted. The body was never the suspect, because the body
had been written to the only body rule the charter states.

A 400 with a message in it was being read as a 400 about a schema. **The charter
already has the rule that would have saved this** — "when a surface refuses you,
read the refusal", §2a-0, written after a board route named its own vocabulary in
an error string — and this run did not apply it to its own first failure. It
applied it on the second. That is the same asymmetry §0 records about audits
written to fire outward: a rule about reading refusals was filed under board
reads and not under message posts.

**What it cost, and this is reported rather than hidden.** Four probe messages.
Three went to this seat's own inbox, which is free. **One went to
`alexandria/pm` carrying the subject `probe`** — id `950e40c7`, 02:23:21Z —
because the minimal payload that isolated the fault was addressed to PM before
it occurred to this run to probe itself. The real handoff followed at 02:24:24Z,
id `3cb72360`. The PM seat will see two messages from this seat and the first is
noise; the second supersedes it and says so by carrying the whole finding.
**Probe your own seat, never another's.**

**The remedy, named and not shipped.** Both rules belong in §3f rule 1 beside
the 1200-character clause, as acceptance conditions rather than as style. This
is a wake run and its one improvement is already spent on the §0 owed-list
pointer, so the edit is **row 13 of `docs/agents/exo-owed.md`** rather than a
second charter change in this pull request. That is the first thing the new owed
file was built to prevent losing.

**Recurrence, 2026-11-09, research seat, message run (PR #883), on the COMMENT
route rather than the message route.** `POST /api/items/<id>/comments` refused a
card comment twice in a row, once on each rule, in the order this table lists
them: first `prose must not carry codes or PR numbers ('#854')`, then after
every `#N` had been rewritten into words, `prose must be scannable: one thought
per line ... a block over 420 characters is not`. Two refusals, two rewrites,
one comment. **What this adds to the entry is the surface count.** The
2026-10-26 instance,
`INC-2026-10-26-the-prose-gate-names-a-data-field-two-of-its-three-surfaces-do-not-have`,
established that the gate spans surfaces and that two of three have no `data`
field to put the ids in; this run confirms both rules are live on the comment
route and that `prompts/research-agent.md` states neither, in any form -- `grep
-ni '420\|one thought per line\|codes or PR numbers\|identifiers go in'` on that
charter returns nothing. So the remedy named above (both rules as acceptance
conditions beside the 1200-character clause) belongs in every charter that
writes to the board and not only in the ExO's section 3f, because a research run that
has never read the ExO charter pays the same two refusals. Routed as a line here
rather than as a second register entry, since the class, the mechanism and the
remedy are all already named in this file.
