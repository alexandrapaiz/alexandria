# The B2B lane, extended — three more constructions

**This file extends [first-customers.md](first-customers.md) §5, it does
not replace it.** That section argues the B2B case and defends four
products: B2B-1 team seats, B2B-2 library licensing, B2B-3 evidence
retainers, B2B-4 the claim graph as a data feed. Read it first; the
sequencing rule at its end governs this file too.

Three further constructions are defended here, plus one correction and
one warning. They are separated out because each is a *different shape*
of business from the four — one is a monitoring product, one is a
services wedge that exists to sell something else, and one is not a sale
at all but a standards play.

Sales agent (prompts/sales-agent.md, ADR-24), 2026-09-18. **The agent
prepares, the owner sends** — no company has been contacted, quoted, or
offered anything. Every price below is a **proposal for the owner's
decision**, never a decision.

---

## Correction first: the claim graph is bigger than the site says

`first-customers.md` §5 B2B-4 sizes the graph at "254 claims and 88
edges," citing `site/lib/graph-data.js`. That file is a **snapshot dated
2026-09-13** and says so in its own header comment. The live count on
2026-09-18 was **441 claims**, verified that day against the production
cluster by the skill agent (`psql "$NEON_RO_URL" -c 'select count(*)
from claims;'` → 441, recorded in docs/ideas.md).

Both numbers are honest; one is five days stale. The B2B-4 argument gets
slightly stronger — the graph is growing at a visible rate, which is
the actual sales point for a data feed, more than any absolute size. Any
draft quoting a graph size should quote the **live** number and the date
it was checked, never the site snapshot.

---

## B2B-5 — Claim Watch: contradiction alerts as a product

**What it is:** a team pins the practices their stack depends on — "we
do on-policy distillation from a teacher model," "our orchestrator uses
nested specialist agents" — and alexandria **alerts them when new
evidence contradicts one.** A `contradicts` edge landing on a pinned
claim fires a notification with the paper, the date, and the strength of
the contradiction.

`idea-list.md` carries the raw version of this as wild idea 34
("deprecation watch") with the correct warning attached: sent
unsolicited, it reads as surveillance and as *"your architecture is
wrong, pay me."* That warning is why this belongs as a **subscription a
team opts into for its own stack**, not as an outbound motion. The
pinned set is theirs, the alert is theirs, and nobody gets told their
architecture is wrong by a stranger.

**Why it is the best-*shaped* product in the whole B2B lane:** it turns
a one-time research purchase into infrastructure with a retention
mechanic that is honest. The customer does not stay because cancelling
is hard; they stay because an alert only has value while it is running,
and the pinned set they have built is their own accumulated context.
Margin is near-total — the `contradicts` edges are computed anyway — and
unlike B2B-3 it consumes **no owner hours at all.** It is also the
natural product shape of the one thing alexandria does that nobody else
does: tracking what got abandoned. Every competitor tells you what is
new; this tells you what you are still doing that stopped being true.

**What must be built:** a pinning surface, an alert job, a notification
path. A real engineering item, flagged to the engineer seat as a
proposal, not scheduled here.

**The honest gate:** it needs enough `contradicts` density in the graph
to fire non-trivially. At 441 claims that is not yet obviously true, and
**nobody should sell this before someone has checked how often it would
actually have fired over the last quarter.** That check is cheap — one
query — and it should gate the build, not follow it. Q1-2027 at the
earliest.

**Proposed price (owner's call):** $99-199/month per team, above seats
and below a retainer. A pure construction — no comp exists.

---

## B2B-6 — The deprecation audit: a paid service that exists to sell something else

**What it is:** point the claim graph at a team's shared skills, agent
prompts, or stated architecture, and report which of their practices sit
in the left-behind pile, each with its citation.

**Why it earns its place next to four bigger ideas:** it is the only B2B
product deliverable **this quarter with today's assets.** No build, no
endpoint, no twelve-skill library — just the graph as it exists and a
written document. And its output *is* the pitch: a team reading *"four
of your eleven shared skills reference a practice the evidence has since
contradicted, here are the papers"* does not then need convincing that
$20 a seat is worth it. It is B2B-3's free sample brief made concrete and
pointed at something the team already owns.

**The motion:** offer the first three **free**, in exchange for
permission to publish the anonymised findings. A published audit of a
real library is a better launch asset than any post in
`docs/sales/launch/`, because it is the product doing its job in public
rather than describing itself.

**Proposed price after the free three (owner's call):** $500-1,500
one-off, credited against the first year of team seats. Land and expand,
with the land priced to be said yes to.

**Boundary, absolute, and it is the same line `idea-list.md` draws
against wild idea 35:** an audit runs **only** on material a team hands
over voluntarily or has already published, **on request.** No scraping
private repos. No unsolicited audit of a named company published as a
growth stunt. Auditing someone without asking is a growth hack that
spends trust, and it is a spectacular way to make an enemy of the exact
buyer B2B-1 wants.

---

## B2B-7 — The Receipt Standard: give the format away, keep the substance

**The boldest construction in this folder, and the one I would spend a
weekend on before any other build here.**

**What it is, in two halves.** First: publish the `provenance:`
frontmatter already shipping in `skills/harness-engineering/SKILL.md` —
`extracted`, `validated`, `claims`, `papers` — as an **open spec that
anyone may implement**, with a free conformance linter. Second: offer
every registry in the ecosystem (skills.sh, skillbay.sh,
Smithery-hosted registries, agentskills.io, localskills.sh, ClawHub) a
**free** verification integration: they call a read-only endpoint, they
display whatever it returns — including "unverified" — and they keep
their distribution entirely.

**Why give away a thing we could sell.** Because the format is not the
asset and never was. Anyone can write four YAML keys. What cannot be
copied is a year of claim-graph edges that make those keys non-empty.
Every competitor who adopts the spec ships `claims: []` and
`validated: ""` — and **every empty field is an argument for alexandria,
published by a competitor, inside their own product, at their own
expense.** A registry that adopts the badge has made evidence a visible
column in its catalogue, which means it has made *our* axis the axis the
category competes on. That is the schema.org / OpenTelemetry / robots.txt
move: whoever defines the format that describes trust in a skill becomes
the reference implementation, and the reference implementation is the
default answer to "who checks this?"

The symmetry is worth noticing: **sgharlow's linter *found* the quality
crisis** (69% of 216 audited skills won't reliably trigger,
[HN 49744398](https://news.ycombinator.com/item?id=49744398)). This is
the linter that *answers* it — and he is already the first entry on
`outreach/list.md`.

**Who signs:** nobody. That is the point — it is an integration, not a
sale. Revenue arrives two doors later through B2B-2 and B2B-4, and
through being the noun people use.

**Relation to the neighbouring wild ideas:** this is the disciplined
version of `idea-list.md` 46 (a public scoreboard scoring the whole
market) and 42 (embeddable verdicts). It keeps their upside and drops
their main risk, because we are not scoring competitors — we are
publishing a format and a checker and letting anyone score anyone,
including themselves, including us.

**The first move, concretely, so this is executable rather than
admired.** One weekend of the engineer seat's time produces two files:
`docs/standards/provenance-v0.md` (the four fields, their types, and
what `validated:` must contain to count) and a linter that reads a
SKILL.md and reports pass/fail per field. The day those exist, three
notes go out, all to people already on `outreach/list.md` or named in
`outreach-plan.md` lane C — **sgharlow** (built the linter that found
the 69% number; the spec is the format his tool could check against),
**skeptrune** (hand-curates skillbay.sh precisely because he can't tell
good from bad at scale), and **kurtextrem** (Skillzero already reads
skill frontmatter to decide what loads). The drafted note is
`outreach-plan.md`'s C-series pattern: quote their work in line one,
offer the spec, ask nothing else. No registry integration is asked for in that first round —
the ask is "does this format describe what you'd need to know," which
is a question three people who have publicly wrestled with exactly this
can answer in a paragraph.

**The two honest risks:**

- **A standard nobody adopts is a file in our repo.** The downside is a
  wasted weekend and a spec page, which is survivable — but the owner
  should not hear "standard" and picture inevitability. Adoption by one
  real registry is the milestone that makes it real; before that it is
  a proposal with good typography.
- **Someone adopts the spec and fills it with weak evidence**, diluting
  the signal. Mitigation is the linter plus public claim IDs: a
  provenance block whose claim IDs do not resolve against a real graph
  is checkable by anyone in one request. **Ship the checker in the same
  change as the spec, never after** — a format without a checker invites
  exactly the empty-field dilution it exists to prevent.

---

## The warning I want on the record: cap the retainer

`first-customers.md` §5 B2B-3 already draws the right line — the moment
a retainer needs the owner's hours rather than the organism's, decline
it. I want to put a number on it, because "decline when it feels wrong"
is not a limit anyone has ever enforced at 2am with an invoice due.

**Proposed hard cap: three concurrent retainer clients, permanently.**

The reasoning: a retainer client's brief is not reusable inventory. It
is the one product in this whole folder that **consumes hours and does
not compound.** At three clients it is meaningful early revenue that
buys case studies and unfiltered market feedback. At ten it is a
consultancy — and a consultancy is not the standalone knowledge business
docs/vision.md §0 commits to, and it loses the autonomy tiebreak
outright. The failure mode is not a bad decision; it is twelve
reasonable decisions in a row, each one worth saying yes to on its own.

Sales would rather flag the ceiling now, while the number is zero and it
costs nothing to agree to, than argue about it later when it costs
revenue.

---

## Sequencing, folded into §5's rule

`first-customers.md` §5's sequencing rule stands: month one is B2B-1
closing, B2B-2 piloting, B2B-3 sending one free sample brief, B2B-4
building its endpoint. These three slot in as:

| Window | Item | Why then |
|---|---|---|
| Month one, days 15-21 | **B2B-6 audits**, three, free | Deliverable today with today's assets; it *is* B2B-3's sample brief with a target |
| Q4 2026, alongside B2B-2 | **B2B-7 spec + linter** | A weekend of work; it makes the B2B-2 pilot conversation much easier to open |
| Q1 2027 at the earliest | **B2B-5 Claim Watch** | Gated on a real check of `contradicts` density, then a build |

## What this file is careful not to claim

- Nobody has been contacted, quoted, or offered anything.
- B2B-5 and B2B-6 have **no observed comp at any price**; both ranges are
  constructions, flagged as such.
- B2B-5 and B2B-7 both depend on the **public read-only surface** that
  does not exist yet. The MCP server (`mcp/server.py`, ADR-11) is real
  and deployed but sits behind the owner's own OAuth passphrase, built
  for her agent — the public read-only surface is logged as `proposed`
  in docs/ideas.md and `geo-plan.md` Game 2, and is never to be
  described as live.
- The library is two skills, one carrying a recorded A/B validation
  (`harness-engineering`, validated 2026-09-12;
  `self-improving-post-training-loops` has an empty `validated:` field).
  Licensing *conversations* are honest now; licensing *delivery* is
  honest at roughly twelve skills (O2 KR1).

## Change log

- 2026-09-18: written to extend `first-customers.md` §5 with three
  constructions it does not defend, one correction to the graph size it
  quotes, and a proposed hard cap on the retainer product.
