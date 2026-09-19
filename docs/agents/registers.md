# The register map — where every rule is actually enforced

Written by the ExO agent on 2026-09-19, on the owner's order after
incident 20. It answers one question for every register the org keeps:
when a rule in that file is about to be broken, what stops it?

**Enforced at:** prompts/exo-agent.md §3d, every run.

## The pattern this file exists to kill

Incident 20 in [incidents.md](incidents.md) is the whole argument. The
owner ruled that section headings must be written fresh from the day's
news. The ruling was recorded in `docs/voice/taste.md` inside the hour,
correctly and permanently. The next artifact to reach her printed
"Gaining traction" and "Trailblazing" anyway, so she had to give the
same ruling a second time, in capitals.

Nothing failed at the archive. The ruling was written down, in the right
file, by the right seat, immediately. What was missing is that no step
between the ruling and the artifact ever opened that file. **Recording
is not enforcing.** A rule written down but not checked at the point of
production is documentation, and documentation does not stop anything.

So every register has two gates, and they are different gates.

- The **archive-side gate** decides that something gets written down.
  Who appends, when, and under what standing rule.
- The **artifact-side gate** decides that something gets checked before
  it ships. Which seat, at which step of which run, opens the file and
  compares its output against it.

An org can have a perfect archive-side gate on every register and still
break every rule it keeps. That is the state incident 20 found us in.

## The map

State after this run's charter edits. "was GAP" means no charter told
any seat to check an artifact against the file before 2026-09-19.

| Register | Owner | Archive-side gate | Artifact-side gate | State |
| --- | --- | --- | --- | --- |
| `docs/agents/incidents.md` | ExO | standing rule, any seat appends the moment an issue repeats | every charter's ship check, plus PM §1f and ExO §2 | was GAP, closed |
| `docs/voice/taste.md` | chair and PM record | chair or PM records the ruling | writer's first grading gate, line by line | was GAP, closed, this is incident 20 |
| `docs/voice/ban-list.md` | writer | writer appends new tells | writer §2, plus sales for launch copy | closed for copy outside the digest |
| `docs/voice/canon.md` | writer | writer proposes, owner rules | writer §2, plus market and sales | enforced |
| the House voice rules | writer | live in `ban-list.md` | nine charters held a frozen four-rule copy | was GAP, now the file wins |
| `docs/design/taste.md` | chair and PM record | chair or PM records the ruling | frontend, compare step added | was GAP, closed |
| `docs/design/ban-list.md` | frontend | frontend appends new tells | frontend, check every change before shipping | enforced, and the model for the rest |
| `docs/design/canon.md` | frontend | owner's rulings and the references | frontend, off-system values need a ledger entry | enforced |
| `docs/design/motion.md` | frontend | distilled from the sources | named by no charter until this run | was GAP, closed |
| `docs/agents/runtime-changes.md` | ExO | ExO writes the law | engineer, frontend, security, ExO | was GAP at the seats that make runtime changes |
| `docs/agents/turn-caps.md` | ExO | ExO re-derives monthly | ExO | enforced, same seat writes and reads |
| `docs/agents/unowned-duties.md` | ExO | ExO files, owner assigns | ExO §3b | enforced |
| `docs/agents/model-routing.md` | ExO | nobody since 2026-09-17 | named by no charter, including the ExO's | was GAP, now in the ExO read list |
| `docs/agents/pending-workflow-changes.md` | ExO | ExO queues, owner applies | ExO §5, verified every run | enforced |
| `docs/agents/registers.md` | ExO | this file | ExO §3d, the register-gate sweep | enforced |
| `docs/agents/org-chart.md` | PM | PM maintains | PM §1b | enforced |
| `docs/agents/frameworks.md` | PM | PM §1e | PM §1e | enforced |
| `docs/decisions.md` (ADRs) | chair | chair records | engineer, PM and ExO read, nine seats do not | partial, and mostly fine |
| `docs/ideas.md` (the ledger) | all seats | append-only, owner decides status | the ledger contract in most charters | enforced |
| `docs/agents/learning-log.md` | ExO | ExO appends every run | ExO §2, read first | enforced |

## What this run changed

Every charter, all twelve, now ends with a section called "Check the
register before you ship". It does two things. It names, per seat, the
registers that seat's output is bound by, and it puts the incident
register's standing rule inside every charter instead of only inside the
register it governs.

The specific gaps that closes.

1. **The voice taste register**, incident 20 itself. The writer's first
   gate is now a taste-compliance pass, line by line against the
   artifact, before the canon laws are scored at all.
2. **The writer charter's own contradiction**, which is the sharper half
   of incident 20. The charter told the seat to protect "her section
   names (Trailblazing, Gaining traction, Left behind, Read these
   yourself)" while canon law 12 said those names never print. An agent
   reading its charter was being told to preserve the violation. The
   framework and the printed heading are now stated apart.
3. **The design taste register**, the same shape and not yet fired. It
   now carries the compare step the design ban list always had.
4. **`docs/design/motion.md`**, named by no charter at all until now.
5. **The runtime-changes law**, which binds every seat and the chair and
   was named in one charter. Engineer, frontend and security now carry
   it at the point where they would break it.
6. **Reader-facing copy outside the newsletter.** The sales seat writes
   launch posts, outreach emails and landing lines, and no voice
   register governed any of it.
7. **The incident register's standing rule.** "Any issue that occurs
   more than once is always recorded at the moment it repeats, no
   exceptions" binds every seat. Before this run, eleven of twelve
   charters mentioned the file only inside the ship-first boilerplate,
   citing incident 3 as evidence for a different rule, and no seat was
   told to open it or append to it. The most-cited register in the org
   was enforced at one seat, once a week, after the fact.
8. **The House voice snapshots.** Nine charters restate four ban-list
   entries inline. When the writer appends a new tell, those nine keep
   enforcing the 2026-09-18 copy. Each now says the file wins.
9. **`docs/agents/model-routing.md`**, which names this seat as its
   owner and which no run had opened since it was written. It is in the
   ExO read list now, so the next run either uses it or retires it.

## Still open, and honestly

- **`docs/agents/org-chart.md` and `docs/agents/frameworks.md`** are the
  PM's and are enforced at the PM's own steps, which is fine, but
  neither carries an `Enforced at:` line yet because neither file is
  this seat's to edit. Filed in the ledger.
- **`docs/voice/*` and `docs/design/*`** are the writer's and the
  frontend's surfaces for the same reason. The enforcement now exists in
  the charters, which is where enforcement belongs. The marker line in
  the register files themselves is a ledger request to those two seats.
- **Nothing verifies that a seat actually ran its check.** A charter
  line is still an instruction to a model, not a gate a runner enforces.
  The honest position is that this run moved the rules from a file
  nobody opens to a file every seat opens, which is a real improvement
  and is not the same as enforcement. A mechanical gate would be a CI
  job, and a CI job is a runtime change, so it goes through
  docs/agents/runtime-changes.md and the owner.

## The rule this file establishes

Every register the org keeps carries an **Enforced at:** line near its
top, naming the charter and the step that checks artifacts against it.
A register that cannot name one is documentation, and it says so.

One reading note for whoever runs the grep. Not every file under
docs/agents/ is a register. `app-identity-handover.md` is a plan,
`pending-workflow-changes.md` is a queue, and plans and queues are
finished rather than enforced. The grep will list the plan and that is
correct output, not a gap.

This is a cheap invariant on purpose. It is one grep, it needs no
tooling, and it makes the failure visible in the file itself rather than
in a postmortem written after the owner repeats herself.
