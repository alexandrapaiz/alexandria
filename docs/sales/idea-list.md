# The idea list — 46 ways to get customers, ranked

Written 2026-09-18 by the sales agent (prompts/sales-agent.md, ADR-24),
fourth run, on owner dispatch. This is the bank the plan draws from:
docs/sales/first-customers.md executes the top of it,
docs/sales/outreach-plan.md is the machine behind the outreach entries,
and everything below the line is here so that when a lane stalls there
is a next move already written down instead of a brainstorm to hold.

**The law: the agent prepares, the owner sends.** Nothing here has been
run. Ideas marked ⚠️ are flagged as risky, ambitious, or unproven —
they are included because the brief asked for the wild ones, and they
are labelled so nobody executes one by accident.

## How the ranking works, and what it is not

Ranked by **expected impact per unit of effort**, which is a judgment
call, not a measurement — nothing here has been tested, so treat the
order as an argument, not a finding. Two things are weighted heavily:

- **The owner's hours are the scarcest resource in the company.** An
  idea that needs three of her hours a week is competing with an idea
  that needs three of an agent's, and losing.
- **Anything requiring engineering is discounted**, because the
  engineering queue already has O1 KR1 on it and sales does not get to
  jump that queue.

Tags: **[1h/wk]** = a founder-led motion she can genuinely run in an
hour a week. **[build]** = needs engineering, name the seat. **[agent]**
= an agent can do it, not her. **[$]** = costs real money.

---

# Tier 1 — do these first (high impact, hours not weeks)

**1. The personal forty.** Before launch, forty individually written
messages to people she already knows who build with agents. Highest
conversion rate available to this company and the one most founders skip
out of embarrassment. **[1h/wk]** → first-customers.md lane A.

**2. Publish one "left behind" verdict as a standalone artifact.** One
technique, named, with the contradicting evidence and the dates. No
product pitch attached. It is the only thing in this market nobody else
can produce, and it works as a post, an HN submission, a curator pitch,
and a GEO asset simultaneously. **[agent]** → already in docs/ideas.md
(market agent, 2026-09-18), unbuilt.

**3. The paid-continuation item in every digest.** Every free issue
carries exactly one item whose full evidence trail or runnable skill
sits behind the $20 spine, named in one honest line. Not a banner — the
item itself. Converts structurally rather than persuasively. **[agent]**

**4. Give the A/B validation sentence its own page.** The harness skill's
"4-30 point regression" result is a real, dated, original number that
currently lives only in YAML frontmatter. One page, one number, one
method. Original data is what AI answer engines cite and what skeptics
click. **[build: frontend, tiny]**

**5. List both gold skills in every public registry, provenance intact.**
agentskills.io, a skills directory, an MCP registry. The provenance block
travels with the file, so every install is a piece of the pitch working
while nobody is watching. **[build: engineer, submission only]** **[agent]**

**6. The team ask, appended to every warm conversation.** Anyone in the
personal forty who works on a team of three or more gets a different
closing line. Two team deals out of forty warm contacts is not ambitious;
zero is what happens if nobody asks. **[1h/wk]**

**7. One unsolicited, free evidence brief.** Pick one named company with
a publicly stated architecture question, answer it from the claim graph
with citations, send it unpriced and unasked. The most persuasive sales
asset this company can make, and it costs a pipeline run. **[agent]**

**8. The HN comment kit.** Three objections pre-drafted before launch
morning: "why buy a markdown file," "this is a newsletter with extra
steps," "your agents wrote this, why trust it." The comments decide a
Show HN more than the post does. **[1h/wk]** → drafted in
outreach-plan.md.

**9. A footer line in every skill file pointing home.** One markdown
line at the bottom of each SKILL.md: where this came from, where the
evidence lives. The cheapest distribution mechanic available and it
compounds with every fork. **[agent]**

**10. Answer her own inbox, personally, for thirty days.** Every reply to
every digest gets a real answer from her. At this list size it is
possible, it is the thing large competitors structurally cannot do, and
it is where the first B2B conversations will actually surface. **[1h/wk]**

**11. Show up in the threads where the problem is being stated.** The
four HN threads market already found are live rooms full of people with
our exact problem. Participate as a practitioner with something useful
to say, not as a founder with a link. **[1h/wk]** — and the moment it
reads as promotion it is worth less than nothing.

**12. Publish the org's own charters and ADRs as content.** Twenty-four
dated ADRs and eleven agent charters already exist as a byproduct of
running the company. "A company whose decisions are public" is a real
hook and required zero incremental production. **[1h/wk]** → already
drafted in launch/pre-launch-teasers.md.

---

# Tier 2 — strong, but slower or costlier

**13. A monthly "what we were wrong about" post.** Publish the claims
the graph retired and why. Retraction as marketing: the only credibility
move competitors won't copy, because it requires having been specific
enough to be wrong. **[agent]**

**14. Guest-issue swap with one adjacent newsletter.** Not the AI-news
competitors — the adjacent-audience tier (Latent Space class). One issue
each, both audiences see one good thing. **[1h/wk]** → target and draft
in outreach-plan.md lane D.

**15. One podcast, one angle.** Not "AI research newsletter." The angle
is *an eleven-agent company that runs itself and publishes its incident
register*. That is a show, and the artifacts to prove it are public.
**[1h/wk]**

**16. Joint report with the skill-linter author.** They measured that 69%
of public skills won't trigger; we have the only skills built to answer
that. A co-published follow-up is credible in a way either side alone is
not. **[1h/wk]**

**17. The claim-graph second opinion, as a free tool.** Paste an
architecture claim, get back what the graph says and the evidence for
it. The free tier of the whole product, and a better demo than any
landing page. **[build: engineer, real scope]**

**18. Ship a one-line install.** If adopting a skill is a git clone and a
copy, the funnel leaks. A single command or a plugin-style install turns
"interesting" into "installed" in the same minute. **[build: engineer]**

**19. Full-text RSS and a JSON feed of the free digest.** Machines
subscribe too, and an agent that reads our feed weekly is a channel that
never unsubscribes. **[build: frontend, small]** **[agent]**

**20. The public read-only claims endpoint.** Already specified in
geo-plan.md Game 2. It is simultaneously a GEO asset, the agent channel,
and the free tier of the future data product for tool vendors. **[build:
engineer]**

**21. Public MCP surface, scoped to matured and deprecated claims.** Any
MCP host can query alexandria as a tool and get a cited answer. The
single highest-leverage agent-channel item and the hardest. **[build:
engineer]** → geo-plan.md Game 2 item 4.

**22. Co-publish the orchestration-pattern benchmark with an eval or
observability vendor.** Practitioners publicly asked for this and found
nothing. We have the claims; a vendor has the traces. Neither has both.
**[1h/wk to open, [agent] to produce]**

**23. The reverse pitch.** Audit a vendor's own public agent docs against
the claim graph, send them the diff privately, publish nothing unless
they want it published. Demonstrates the product on their own material.
**[agent]** — private first, always; publishing an unrequested audit
buys attention at the cost of the relationship.

**24. Free tier for students, OSS maintainers, and grant-funded
researchers.** Costs ~$0 marginal, seeds the citation layer, and the
people most likely to cite us are the least able to pay. **[1h/wk
decision, owner's call]**

**25. "Thirty days of frontier practice" — an email onramp.** A short,
finite, automated sequence of the best existing claims, as the default
welcome for new free subscribers. Finite and useful, not a drip
campaign. **[agent]** — and it must never masquerade as the digest.

**26. Manual referral credit.** A subscriber who brings a paying
subscriber gets a free month, applied by hand. No codes, no leaderboard,
no tracking infrastructure until the volume justifies it. **[1h/wk]** →
already drafted in launch/referral.md.

**27. A lightning talk at one AI-engineering meetup.** Same angle as the
podcast. Small rooms, high-intent audiences, and the talk doubles as the
podcast pitch. **[1h/wk]** **[$ travel, possibly]**

**28. Annual plan at ten months.** A pricing lever the market agent has
already flagged as plausible but unevidenced. Improves cash and
retention on day one if the owner wants it. **[owner's call — pricing is
hers, argued in positioning.md, not here]**

**29. Open-source one piece of the pipeline as a lead magnet.** The
triage prompt or the claim-graph schema. Developers trust what they can
read, and it costs nothing we were keeping. **[1h/wk decision, [agent] to
prepare]** — never the gold layer.

**30. "Bring your own claim."** A public path for a reader to submit a
claim they want adjudicated against the graph. Turns readers into
contributors and surfaces exactly what the audience actually wants to
know. **[build: small]**

**31. A claim-of-the-week post, every week, forever.** One claim, its
evidence, its status, in public. Not a campaign — a cadence. The
compounding surface that makes every other idea easier a year from now.
**[agent]**

---

# Tier 3 — the wild ones ⚠️

Included because the brief asked for them. Each one is labelled with
what could go wrong, because an idea that can damage the company's one
scarce asset — its credibility — is not a free bet.

**32. ⚠️ Publish this sales plan itself.** The company let an agent write
its own go-to-market under an open brief, then published the plan, the
critique it got, and the rerun. The artifacts already exist
(docs/agents/incidents.md item 11 is genuinely unusual reading).
**Risk:** publishing the incident register invites "they're winging it";
the counter-read is "they're the only ones showing the register." Her
call, and it is a real one.

**33. ⚠️ The contradiction bounty.** $50 to anyone who finds a claim in
the graph that published evidence contradicts and we missed. Quality
becomes a public spectacle and the product improves either way. **[$]
Risk:** unbounded cost if the graph is worse than we think — which is
itself information worth $50 a pop to learn.

**34. ⚠️ Deprecation watch.** Alert a company when a technique its own
public engineering blog says it depends on gets contradicted in the
graph. Uniquely valuable, and the highest-conversion B2B opener
imaginable. **Risk:** reads as surveillance and as "your architecture is
wrong, pay me" — only ever send it to someone who asked, or as a free
one-off with a genuinely humble frame.

**35. ⚠️ Audit a famous framework's documentation against the claim
graph and publish the diff.** Guaranteed attention, immediate
credibility with practitioners. **Risk:** picks a fight with a potential
partner (idea 22, 42). Do the private version (23) first, always.

**36. ⚠️ The agent-to-agent sales page.** A machine-readable pitch at a
stable URL, written for the agent doing someone's research rather than
the human reading a landing page: what alexandria is, what it verifies,
in structured, quotable form. Nobody in this market is writing copy
aimed at the reader that increasingly does the reading. **Risk:** an
unproven channel; near-zero cost to try. **[build: tiny]** **[agent]**

**37. ⚠️ Trade claim-graph access for another company's data.** A tool
vendor's anonymised traces in exchange for read access to our verdicts.
Both sides get something they cannot buy. **Risk:** gives away the moat
cheaply if the terms are loose; non-exclusive and attributed or not at
all.

**38. ⚠️ Live public status of the organism.** A page showing what the
pipeline is doing right now — papers read today, claims added, the
skills queue. The transparency is the marketing. **Risk:** a quiet week
is visible too, which is a reason to build it honestly, not a reason to
fake it. **[build]**

**39. ⚠️ Skill reliability guarantee.** If a skill in the library fails
to trigger reliably, that month is free. Aims the guarantee squarely at
the 69% failure statistic everyone in the market already knows. **Risk:**
"reliably" needs a definition before this is ever offered, or it is a
promise that cannot be adjudicated.

**40. ⚠️ Print one physical annual report.** A short, beautiful "state of
agent engineering: what held up and what didn't," mailed to a hundred
named people. Nobody in AI sends paper; everyone keeps it. **[$]
Risk:** real money and real weeks for a hundred touches. It is a year-one
brand bet, not a month-one customer play.

**41. ⚠️ Hire agents in public.** Post the seat charters as if they were
job ads — "wanted: a sales agent, here is the charter, here is the
incident that got the last run rejected." The audience most likely to
buy is exactly the audience that finds this fascinating. **Risk:** cute
once, tiresome twice.

**42. ⚠️ Embed our verdicts on someone else's page.** A tiny embeddable
widget showing what the graph says about a claim, for other people's
blogs and docs. Distribution through other people's credibility.
**Risk:** a maintenance burden and a support surface for a product with
two skills. Not before the graph is bigger. **[build]**

**43. ⚠️ The anti-launch.** Skip the launch post entirely; publish the
"left behind" artifact with no product attached and let the product be
discovered by whoever follows the work. **Risk:** forgoes the one
launch-day spike we get. Listed because it is the honest strategic
alternative if the product is not ready on 10-13, and because it is what
the floor plan (first-customers.md §8) collapses into anyway.

**44. ⚠️ Adversarial digest.** One issue a quarter written to argue
against our own most-cited claims, produced by a dedicated adversary
agent. Intellectually honest, extremely shareable, and structurally
impossible for a content business whose incentive is to be right.
**[agent]**

**45. ⚠️ Sell the archive as a one-time product.** A single $99 purchase
of the full historical claim graph snapshot, for people who will never
subscribe. Converts the "I don't do subscriptions" objection into
revenue. **Risk:** undercuts the recurring model and prices the moat as
a commodity. **Owner's call, and sales' recommendation is no** — listed
because it will be suggested eventually and the reason against it should
already be written down.

**46. ⚠️ A public scoreboard of skill verifiability across the whole
market.** We score everyone's skills, including our own, on a published
methodology. Becomes the category's reference point. **Risk:** we are a
competitor scoring competitors; it only survives if the methodology is
public, the tooling is open, and our own skills sometimes score badly.
Enormous if it works, and idea 16's joint report is the credible first
step toward it.

---

# Explicitly rejected

Written down so they stay rejected when someone is nervous about the
numbers in week three. All of these spend trust, and trust is the only
asset this company has that money cannot rebuild.

- **Upvote rings, reposting a failed Show HN, second accounts.** Detected,
  fatal, and against the charter.
- **Cold email at volume with a sequencing tool.** Sixty hand-written
  notes to people who publicly stated the problem is a different
  activity from six thousand automated ones, and only one of them is
  what this company is.
- **False urgency, countdown timers, founding-member-price-ends-Friday.**
  The billing principle (vision.md §4) is explicitly anti-dark-pattern
  and it extends to copy.
- **Buying an audience** — paid followers, paid placements dressed as
  editorial, listicle-site "best of" placements.
- **Launch-day discounts.** A discount at launch tells the first
  customers the price is soft and punishes them for paying full price
  later.
- **Any claim the product does not meet today** — "a library" for two
  skills, a subscriber count that includes comped friends, a live metric
  that is hardcoded.

---

## Change log

- 2026-09-18: first version, fourth sales run, owner dispatch following
  docs/agents/incidents.md item 11, which named "no idea list" as one of
  four omissions. Companions: docs/sales/first-customers.md (the plan),
  docs/sales/outreach-plan.md (the machine).
