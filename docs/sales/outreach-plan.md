# The outreach machine — targets, sequence, volumes, drafts

Written 2026-09-18 by the sales agent (prompts/sales-agent.md, ADR-24),
fourth run, on owner dispatch. This is the engine behind lanes A, C, D,
E, F and G of docs/sales/first-customers.md: who gets contacted, in what
order, on what day, with what words, and what happens when they reply.

It extends docs/sales/outreach/list.md rather than replacing it — that
file's four verified entries (skillcrossroads, skillbay.sh, Latent Space,
the Microsoft Agent Framework team) stay valid and are folded into the
categories below with their drafts intact.

**The law, and it is the reason this file exists at all: the agent
prepares, the owner sends.** No message below has been sent. No account
has been created. No target has been contacted, followed, or looked up
in any way that leaves a trace. Every draft is written to be pasted,
edited, and fired by her, from her own account, in her own hand.

---

## 1. The rules of this machine

Six rules, and they are what separate this from a cold-email operation.
The charter's honesty line makes most of them mandatory; the rest are
just what works at this size.

1. **Every target has a dated, public artifact showing they have the
   problem.** Not "works in AI." A specific post, comment, thread, or
   published document, linked in the target's entry, referenced in the
   first sentence of the note. If a candidate has no such artifact, they
   do not go on the list — the previous run dropped a set of
   listicle-aggregator candidates for exactly this reason and was right
   to.
2. **Volume is capped by what she can write by hand.** ~15 notes a week.
   No sequencing tool, no mail merge, no BCC. At this volume personal is
   possible, and personal is the only advantage a one-person company has
   over a funded one.
3. **One follow-up, ever.** Seven days later, two lines, then the target
   is closed permanently. Never a third touch. Never a "just bumping
   this to the top of your inbox."
4. **The ask is proportional to the relationship.** Peers get no ask.
   Warm contacts get one. Nobody gets a pitch deck.
5. **Every fact in every note must be true on the day it is sent.**
   Two skills in gold, not a library. A comped friends list, not
   "subscribers." docs/sales/first-customers.md §10 lists what is not
   true yet; those sentences never appear in a draft.
6. **Re-verify before sending.** Handles change, threads get deleted,
   people move. The day-before check is in §6 and it is not optional —
   the cost of a note referencing something that is no longer there is
   the whole relationship.

---

## 2. Volumes she can actually sustain

Everything sized against roughly **90 minutes a week**, which is the
budget docs/sales/idea-list.md assumes for founder-led motions.

| Week | Lane A | Lane C | Lane D | Lane E | Lane F | Total | Her time |
|---|---|---|---|---|---|---|---|
| **Pre-launch (10-06 → 10-12)** | 40 | — | — | — | — | 40 | ~3h, once |
| Week 1 (10-13 → 10-19) | follow-ups | 5 | 3 | — | — | 8 + replies | ~2h |
| Week 2 (10-20 → 10-26) | — | 5 | 3 | ~8 | 3 | 19 | ~2h |
| Week 3 (10-27 → 11-02) | — | 5 | 3 | follow-ups | 3 | 11 + f/u | ~1.5h |
| Week 4 (11-03 → 11-11) | — | 5 | 2 | 2nd close | follow-ups | 7 + f/u | ~1.5h |

**Month total: ~100 messages, essentially all of them warm or
evidence-matched.** The pre-launch forty is the only burst; everything
after is a steady dozen-ish a week, which is a Tuesday morning, not a
job.

What this deliberately is not: a thousand-contact list. Sixty targeted
notes to people who publicly described our exact problem in the last
sixty days will out-convert six thousand automated ones, and it is also
the only version of this the charter permits.

---

## 3. The targets, by category

### Lane A — the personal forty (pre-launch, days -7 to -1)

**Category:** people the owner already knows who build with agents, or
who have asked her what she is working on.

**Why it is first and why it is the canary:** it is the only lane with
a 20%-plus conversion rate, and if these people do not want it, the
strangers in lane B certainly will not. Running it *before* the public
launch is how we find that out while there is still time to change
something.

**Sourcing:** hers alone — sales cannot and must not assemble this list.
The prompt for her, on 2026-10-06: *ex-colleagues, people from previous
teams, founders who have shown you their agent stack, anyone who has
ever asked what you're building, anyone whose work you'd send this to
even if you weren't selling anything.* Forty names in a file. If forty
is hard, thirty is fine; if it is ten, that is the most important
finding of the launch and it arrives a week early.

**Tag each name with one flag as you write the list:** *team of 3+?* If
yes, they get the lane-E close (§4, draft A3) instead of the individual
one. This one column is the entire B2B pipeline for month one.

### Lane C — practitioners who publicly stated the problem

Four sub-categories, each anchored to a dated public artifact already
sourced in docs/market/. These are the rooms where our customers
already described their pain in their own words.

| Sub-category | The artifact | Who to reach | Draft |
|---|---|---|---|
| **C1 — the skill-quality auditors** | "Show HN: Linting 216 public Claude Code skills — 69% won't reliably trigger" ([HN 49744398](https://news.ycombinator.com/item?id=49744398), 2026-09-17) | The poster (sgharlow, skillcrossroads.com) — already drafted in `outreach/list.md` §1 — plus commenters in that thread who reported the same experience | C1 |
| **C2 — the skill-marketplace builders and their skeptics** | Show HN for skillbay.sh ([HN 49743459](https://news.ycombinator.com/item?id=49743459), 2026-09-17); founder conceded AI-generated skills "are usually pretty bad"; top commenter (kouteiheika) asked why anyone would buy a markdown file | skeptrune (skillbay.sh) — drafted in `outreach/list.md` §2 — and, separately and carefully, the skeptic | C2 |
| **C3 — the multi-agent operators** | Ask HN on production multi-agent systems ([HN 49689454](https://news.ycombinator.com/item?id=49689454), 2026-09-13): "I've not really seen anything outstanding in this space" on observability | **Verified 2026-09-18: Var1377, kaihwang, ramstar3000 (OP), idempotent_, and the skeptic taurath** — see the table below | C3, C3a-C3d |
| **C4 — the context-budget crowd** | Show HN "Skillzero" ([HN 49698184](https://news.ycombinator.com/item?id=49698184), 2026-09-14), and the commenter asking whether scoping works "on repo level" | The poster and that commenter | C4 |

**Gap closed, 2026-09-18.** The previous run could not verify C3's
commenters (HN rate-limited the fetch) and this file originally carried
that as an open action for day -6. It is now resolved: direct HN fetches
returned HTTP 429 again, but the **public Algolia item API**
(`hn.algolia.com/api/v1/items/<id>`) served the full thread, and all four
threads behind lanes C1-C4 were re-read against it. Recording the method
because it is the one that works when HN's own pages are rate-limited.

The verified handles and their exact words:

| Handle | What they actually said | Thread |
|---|---|---|
| **Var1377** | *"does anyone have any recommendations for stronger multi-agent observability. I've not really seen anything outstanding in this space yet"* | 49689454 |
| **kaihwang** | *"most of the pain at scale isn't the agents themselves, it's observability. once you're past a handful you basically need per-agent tracing or you're debugging blind"* | 49689454 |
| **ramstar3000** (OP) | *"Curious to understand exactly when it becomes worth it / what production use cases there are"* for large multi-agent architectures | 49689454 |
| **idempotent_** | Runs custom harnesses with *"OpenTelemetry + Prometheus… a massive K8s cluster spinning up pods per N agents"* | 49689454 |
| **taurath** | *"I'd love examples of it actually working but right now all it's seemed to be is hype… I haven't found anyone who isn't working for OpenAI/Anthropic, or isn't selling a solution."* | 49689454 |
| **keks0r** | *"I have added some sales skills into our company brain, but for sessions that others would do, if they are not doing sales related tasks, they would not require any of it"* | 49698184 |
| **holoduke** | *"this probably has no valuable moat… There is some serious demand for expertise in the field of AI automation. But it requires experts with domain knowledge."* | 49743459 |
| **radlad** | *"I had a similar idea but as a marketplace for agents to purchase from… I then started wondering how agents could su[bscribe]"* | 49743459 |

Two of these change what the plan can do, not just who it can write to:

- **keks0r is lane E's first evidenced prospect.** A person describing a
  company-wide shared skill library, unprompted, in public, is a
  team-seat buyer stating their own buying context. Until now lane E's
  only source was the owner's warm network (`first-customers.md` §5,
  B2B-1). It now has a public one, and a repeatable sourcing rule:
  **watch for the pronoun** — "our team," "our company brain," "we share
  skills."
- **taurath is the most useful sentence in this research.** Alexandria
  *is* selling a solution, so the only honest reply hands over something
  checkable instead of arguing. Draft C3d.

**Still unverified, and flagged rather than assumed:** whether any of
these people publish a contact address. HN does not expose emails.
**Default motion for every name above is a public in-thread reply**, not
a private note — hunting someone's address to pitch them after they
asked a technical question is the move that makes people resent being
helped. Private notes only where a profile lists a contact itself.

**Sustaining the list:** five new names a week is roughly one new
qualifying HN or Reddit thread a week, which is the rate this market
actually produces them — two skill-marketplace launches appeared on HN
in a single week in September (docs/market/briefs/2026-09-18.md). The
market agent's Friday run is the natural supplier; this file should be
extended from its briefs rather than from searching.

### Lane D — curators, hosts, and citers

| Sub-category | Real examples, with the fit evidence | Ask | Draft |
|---|---|---|---|
| **D1 — adjacent newsletters, not competitors** | Latent Space (200k+ subs, closest audience match per `landscape.md`; its AINews merger is a structural precedent for free-digest-plus-paid-layer) | A read, then possibly a guest-issue swap | D1 |
| **D2 — podcasts** | Shows covering AI engineering practice. The angle is not "newsletter" — it is *an eleven-agent company that runs itself and publishes its own incident register* | A conversation | D2 |
| **D3 — researchers and tool teams who would cite us** | The Microsoft Agent Framework team (their 2026-09-16 post argues skills beat nested specialist agents — independent validation of our thesis; drafted in `outreach/list.md` §4) | None. A citation relationship | D3 |
| **D4 — community moderators** | r/ClaudeAI, r/AI_Agents, r/LocalLLaMA, r/SideProject | Permission, before posting, not after | D4 |

**Explicitly excluded, and the reasoning stands from the previous run:**
TLDR AI, The Batch, AlphaSignal, Import AI, Last Week in AI. Pitching
them is asking a rival to promote us. And any "best AI newsletters 2026"
listicle site — no evidence of fit beyond the fact that they list
newsletters.

**The lane-D timing rule that changes in week 3:** `outreach/list.md`
already flags it — a curator needs a real issue to link to, not a repo.
Weeks 1-2 target D3 (researchers, who read source) and D4 (moderators,
who need permission before anything). **D1 and D2 wait until there is a
public archive with real issues in it**, which is week 3 at the earliest
and only if O1 KR1 landed.

### Lane E — the team ask (B2B-1, warm only)

**Not a separate list.** It is a different closing line on lane A's
forty, sent to the subset flagged *team of 3+*, in week 2 — after they
have used the free digest for a week, not on day 1.

Expected volume: ~8 of the 40. Target: 2 closes, 10 seats.

**The trigger to listen for**, in their words, not ours: *"everyone here
is independently googling the same question and getting different
answers."* When someone says a version of that, they have described the
product, and the close is one sentence long.

### Lane F — the company lanes (B2B-2, B2B-3, B2B-4)

| Target category | Real examples named in our own landscape | Month-one ask | Draft |
|---|---|---|---|
| **F1 — skill marketplaces and directories** (B2B-2) | skillbay.sh (hand-curated; founder has publicly stated the quality problem), skills.sh (millions of installs, no quality signal), SkillsMP (800k+ scraped skills, curation absent by design) | List our two skills free, show the provenance, see whether users behave differently. **A pilot, not a licence** | F1 |
| **F2 — MCP registries and agent directories** (B2B-2) | Smithery (21.8k servers), agentskills.io | A listing, plus a conversation about surfacing verification as a first-class field | F1 + G |
| **F3 — agent frameworks giving the engine away** (B2B-2) | LangGraph, CrewAI, n8n, Dify (named in `opportunities-2026-09-18.md` as the free-engine tier) | Complementary content for their users; we explicitly do not build an engine | F2 |
| **F4 — AI-native dev tools treating MCP as the front door** (B2B-2/B2B-4) | Cursor, Vercel, Firecrawl, Browserbase, Exa, Mem0 (named in `geo-plan.md`) | Integration conversation; the free claims endpoint first | F2 |
| **F5 — AI teams at mid-size companies** (B2B-3) | Sourced from lane A and from public engineering blogs that state an architecture question out loud | One free, unsolicited evidence brief | F3 |
| **F6 — research-tool vendors who would cite verdicts** (B2B-4) | Elicit, Consensus, Semantic Scholar (adjacent, non-competing — they do search, we do judgment) | Nothing in month one. The endpoint exists, they find it | — |

**The honesty constraint on all of lane F, and it is not a small one:**
the fit evidence for these companies is *category-level* — they are
publicly in the business where our thing matters. It is not
person-level, and none of them has publicly said "I need this."
**Before any F-note is sent, the owner needs a named human and a
specific reason that human would care.** A note that opens "I noticed
your company is in the agent space" is the exact generic outreach rule 1
exists to forbid. The drafts below are written to be *finished* by her
with that specific detail, and they have a visible slot for it.

### Lane G — the listings (not outreach, but the same lane of work)

Submission copy for agentskills.io, a skills directory, and an MCP
registry. Sales drafts the copy; the engineer seat submits. The copy is
in §5, draft G.

---

## 4. The drafts

House voice, from the existing drafts in `outreach/list.md`: plain,
short, specific, no exclamation marks, no adjectives doing work a fact
could do, and an explicit "not pitching you" whenever it is true — which
means it must never appear when it is not.

Bracketed `[LIKE THIS]` is a slot only she can fill. **Any draft still
containing a bracket has not been finished and must not be sent.**

---

### A1 — the personal forty, close contact

```
Hey [NAME] —

I've spent the last few months building alexandria: a pipeline that
reads AI papers daily, tracks which technique claims actually hold up
over time, and turns the ones that survive into skills an agent can
load, each one citing the papers and claims behind it.

It goes live properly on October 13. Free weekly digest, full issues;
the paid part ($20/mo) is the operational layer — the skills, the claim
graph, the automations.

I'm telling forty people I actually know before I tell anyone else. If
you want it, here's where to start: [SIGNUP_LINK]. If it's not for you,
genuinely no problem — but if you know one person it is for, that's the
more useful thing.

[SOMETHING ONLY YOU TWO WOULD SAY]
```

### A2 — the personal forty, weaker tie

```
Hi [NAME] — you asked a while back what I was working on, and now
there's something to actually show you.

alexandria reads AI research daily, tracks which claims about building
agents hold up or get contradicted over time, and turns the ones that
hold into evidence-backed skills. Here's one, with its provenance block
— sources, claim IDs, and a dated A/B result:
github.com/alexandrapaiz/alexandria/blob/main/skills/harness-engineering/SKILL.md

Launching October 13: the weekly digest is free, and the tooling layer
is $20/month. Thought of you because of [THE SPECIFIC REASON].
```

### A3 — the team close (lane E), appended to A1/A2 or sent standalone in week 2

```
One more thing, and then I'll stop: you've got [N] people doing agent
work. The thing I keep hearing from teams that size is that everyone's
independently googling the same architecture questions and coming back
with different answers.

There's a team option — [N] seats on one invoice, plus a 30-minute call
with me each quarter about whatever your team is actually arguing about,
answered from the claim graph with the evidence attached.

If that's useful, say so and I'll send an invoice this week. If not,
that's the last you'll hear about it.
```

*(Price and shape to match whichever option the owner picks in
first-customers.md §B2B-1; the draft deliberately does not state a
number, because that number is her decision on 2026-10-07.)*

### A4 — the one follow-up (all lanes, seven days later, then never again)

```
Hi [NAME] — just closing the loop on this so it's not sitting in your
inbox. If it's not a fit, no reply needed at all and I won't chase it.

[ONE LINE OF GENUINELY NEW INFORMATION — a new issue, a new skill, a
result. If there isn't one, don't send this.]
```

### C1 — the skill-quality auditor

*(Already drafted in `outreach/list.md` §1 and still the strongest note
on this list. Reproduced here so the machine is in one place.)*

```
Hi — I built the linter's counterpart to what you found. Your 69%
"won't reliably trigger" number is close to the reason I started
attaching evidence to every skill in my project (alexandria):
provenance, source claims, and a recorded before/after validation,
so a skill's reliability isn't a guess. One live example:
github.com/alexandrapaiz/alexandria/blob/main/skills/harness-engineering/SKILL.md

Not pitching you anything — just wanted the person who did the actual
audit to see the response to it, and I'd genuinely value your read on
whether the provenance format is enough or still missing something.
```

### C1b — a commenter in that thread who reported the same experience

```
Saw your comment on the skills-linting thread — the 69% number matched
what you'd hit yourself.

I've been building the other half of that: every skill in my project
ships with the claims and papers it came from and a dated A/B result
showing what changed with it loaded. Two of them so far, both public:
github.com/alexandrapaiz/alexandria/tree/main/skills

Curious whether that would have changed anything for you, or whether
the real problem is upstream of verification entirely. Not selling you
anything — the skills are just there.
```

### C2 — the marketplace builder

*(From `outreach/list.md` §2, unchanged — it is already right.)*

```
Hey — saw your Show HN post and the "why buy a markdown file" pushback
in the comments. I think you and I hit the same wall from different
sides: you hand-curate because AI-generated skills are usually bad; I
built a pipeline that only promotes a skill once it has a provenance
block (claims, papers, a dated A/B test), so "is this any good" has an
answer that isn't "I checked it myself."

Curious whether you'd see that as complementary to hand-curation or
redundant with it — genuinely asking, not pitching. Repo's public:
github.com/alexandrapaiz/alexandria
```

### C2b — the skeptic, and this one only goes out if she means it

**Read this before sending:** replying to someone's public skepticism
with your own product is the single easiest way to look exactly like the
thing they were skeptical of. The only version that works concedes the
point first, because the point is correct.

```
Your "why would I buy a markdown file an LLM could generate" comment
has been rattling around my head for a week, because I think you're
right and it's the objection I have to actually answer.

My position: the file isn't the thing. The evidence is. The skills I
publish carry the claim IDs and papers they were distilled from and a
dated before/after result — one of them records that a bare model
endorsed a training approach that a 4-30 point measured regression says
is wrong, and refused it with the skill loaded. That's not something an
LLM generates on request; it's the output of a pipeline that read the
papers and tracked which claims survived.

Both are public and free to read, no signup:
github.com/alexandrapaiz/alexandria/tree/main/skills — if that still
doesn't clear your bar I'd honestly rather know why.
```

### C3 — the multi-agent operator

*Recipients verified 2026-09-18 (see lane C above). The generic version
below still works for whoever fits next month; the three named variants
that follow are better, because they quote the person.*

```
You said in the multi-agent thread that you hadn't seen anything
outstanding for observability in this space. Neither had I, which is
roughly why I started building the thing I'm building.

It isn't observability — it's the layer under it: a claim graph that
tracks which orchestration and agent-design claims get supported or
contradicted as the research comes in, so "does pattern X actually
help" has an evidence trail instead of a blog post. Free weekly digest
of what changed; the graph and the skills are the paid part.

Not asking you for anything. If you've got a specific architecture
question you've never found a good answer to, send it and I'll tell you
what the graph says, including if the answer is "nobody knows yet."
```

**Note on that last line:** it is the highest-converting sentence on
this entire page and it is also a real commitment. Only send it in a
week she can honestly answer within two days.

### C3a — Var1377, the observability ask (public reply, preferred)

```
On "nothing outstanding in this space" — agreed, and I'd split it in
two, because the tooling gap and the knowledge gap get conflated a lot.

Tracing is the part OTel-style tooling actually does solve (the sibling
comment's OTel + Prometheus setup is roughly where I'd start too). The
part nothing solves is knowing which pattern was worth tracing in the
first place — there's no maintained record of which multi-agent
patterns held up and which quietly got abandoned, so every team
relearns it from scratch.

That second gap is what I've been building: a claim graph over
AI-engineering papers that tracks supports/contradicts edges over time,
so "is this pattern still a good idea" has an answer with citations
under it. Public, if it's useful:
github.com/alexandrapaiz/alexandria

Not a pitch — same wall you're describing, approached from the
research side.
```

### C3b — kaihwang, the tracing-at-scale comment

```
Your framing — past a handful of agents you're debugging blind without
per-agent tracing — matches what I keep finding in the papers, and the
borrowed-from-microservices instinct seems right.

The adjacent thing I've been building is the evidence layer rather than
the telemetry one: a claim graph tracking which agent-design and
orchestration claims get supported or contradicted as results come in.
The finding that surprised me most is how often improving the harness
beats decomposing into more agents — distilled here with the papers
attached, if you want the receipts rather than my summary:
github.com/alexandrapaiz/alexandria/blob/main/skills/harness-engineering/SKILL.md
```

### C3c — ramstar3000, the thread's author

```
Hi — you asked when multi-agent architectures actually become worth it
versus one capable model with a few subagents. I've been building the
research side of that question and the honest summary of what I've
found so far: the evidence mostly favours the harness over the
architecture. Improving the scaffold around one model tends to beat
decomposing into more agents, and several 2026 papers land there
independently.

It's distilled into a skill file with the claims and papers attached:
github.com/alexandrapaiz/alexandria/blob/main/skills/harness-engineering/SKILL.md

No ask — you asked a good question in public and I had an unusually
specific answer to it.
```

### C3d — taurath, the skeptic (send only if she means it)

```
"I haven't found anyone who isn't working for OpenAI/Anthropic, or
isn't selling a solution" is fair, and I am selling a solution, so
take this accordingly.

The one thing I can offer that isn't an assertion: I publish what got
left behind. Not "here's what's new" — here are the practices the
evidence stopped supporting, with the paper and the date. It's the
section that's useless for marketing and it's the reason I started,
because nobody publishes negative results and everyone needs them.

[LEFT_BEHIND_LINK] if you want to check whether it's that or just more
hype with better framing. Genuinely fine either way.
```

**Gate on C3d:** it links the left-behind artifact, so it cannot go out
before that artifact is public. Until then, link the repo or don't send.

### C4 — the context-budget crowd

*Verified recipients: **kurtextrem** (Skillzero's author) and **keks0r**
(the "company brain" commenter — but keks0r is better served by the
team ask in lane E, and should get that, not this).*

```
Saw the thread about skill libraries eating context across unrelated
tasks, and the question about whether scoping works at the repo level.

I don't have scoping solved. What I do have is the opposite bet: two
skills, both dense, both carrying the papers and claims they came from,
instead of a hundred that might trigger. Small and verified rather than
large and hopeful.
github.com/alexandrapaiz/alexandria/tree/main/skills

If you've found a scoping approach that actually works I'd like to hear
it — it's the part of this I haven't solved.
```

### D1 — the adjacent newsletter

*(From `outreach/list.md` §3, with the swap ask added for week 3+.)*

```
Hi — longtime reader. I've been building alexandria, a research
pipeline that tracks which AI-engineering/orchestration claims hold up
over time (a claim graph, not a link list) and turns the ones that do
into evidence-backed skills. Free weekly digest, paid layer is the
skills, the claim graph, and automations.

Not asking for coverage — genuinely just think our readers overlap and
would value your read on whether the claim-graph framing holds up to
someone who's spent longer in this space than I have. Here's a recent
issue so it's not just source code: [ISSUE_LINK]

[WEEK 3+ ONLY, IF THE FIRST EXCHANGE WENT WELL: If you'd ever want a
guest issue on what got contradicted this quarter, I'd write it.]
```

### D2 — the podcast

```
Hi [NAME] — a pitch that isn't about a product.

I run a company staffed by eleven AI agents with written charters: a PM,
a finance seat, a security seat, an ExO that reads the incident register
every run. They open pull requests, I merge them. It publishes its own
decisions as ADRs and its own failures as a public incident log —
including the one where I rejected an agent's work as "poorly creative"
and had it redo the run.

That's the episode: what actually happens when you try to run a real
company this way, with the receipts public. The product it's building
is a research pipeline that tracks which AI claims survive over time,
but the org is the more interesting half.
github.com/alexandrapaiz/alexandria
```

### D3 — the researcher or tool team, citation relationship

*(From `outreach/list.md` §4, unchanged.)*

```
Read your Agent Framework post on skills-over-nested-agents with real
interest — it's close to the thesis behind a project I run
(alexandria), where every skill an agent can load carries the specific
research claims and validation behind it, rather than being
instructions alone. Wanted to flag it as independent confirmation of
the same direction, and say thanks for writing it clearly enough to
cite. github.com/alexandrapaiz/alexandria if useful context.
```

### D4 — the moderator, before posting anything

```
Hi — I'd like to post about a project I've built (alexandria: a
pipeline that tracks which AI-agent technique claims hold up over time
and turns the durable ones into skills, with citations). Free digest,
paid tooling layer, and it's a real thing with a public repo rather
than a landing page.

Rather than post and find out I got the self-promo rule wrong, I'd
rather ask: is that within the rules here, and is there a format or a
day you'd prefer? Happy to take a no.
```

### F1 — the marketplace or registry pilot (B2B-2)

```
Hi [NAME] — [THE SPECIFIC THING THEY SAID OR SHIPPED THAT PROMPTED
THIS. If you can't fill this line in, don't send the note.]

Short version of why I'm writing: you distribute skills, and the
public number on skill quality is bad — 69% of 216 audited public
Claude Code skills won't reliably trigger. Distribution can't fix that;
verification can.

I have two skills, distilled from a research pipeline, each carrying
the claim IDs and papers behind it and a dated A/B result. Two is not a
library and I'm not going to pretend otherwise.

The ask is small: list them, show the provenance, and let's see whether
your users treat a skill with an evidence trail differently from one
without. Free, no exclusivity, and if the answer is "no difference"
that's worth knowing too. github.com/alexandrapaiz/alexandria/tree/main/skills
```

### F2 — the framework or dev tool (B2B-2 / B2B-4)

```
Hi [NAME] — [THE SPECIFIC POST, RELEASE, OR DOC THAT PROMPTED THIS.]

I'm not building an orchestration engine — you've got that, and I've
written down explicitly that we shouldn't compete there. What I have is
the layer above it: a claim graph tracking which agent-architecture
claims hold up against the research, and skills distilled from the ones
that do, each citing its evidence.

Two ways that could be useful to your users rather than competitive
with you: skills built for your framework specifically, with the
evidence attached, or a read-only endpoint your product could query to
tell a user when a pattern they just adopted has been contradicted.

Worth twenty minutes? If not, no follow-up.
github.com/alexandrapaiz/alexandria
```

### F3 — the free evidence brief (B2B-3), the cover note

**This one is different: the value is delivered before the note is
read.** The brief is attached or inline, complete, free, and not
contingent on anything.

```
Hi [NAME] —

[YOUR ENGINEERING POST / TALK / DOC] said you're weighing
[THEIR ACTUAL QUESTION]. I run a pipeline that tracks which claims in
this area have held up against the research, so I ran your question
through it. That's below — no charge, no ask, and it's yours whether or
not you ever reply.

[THE BRIEF]

If it's useful, the thing I actually sell is this on a standing basis:
a monthly brief answering your team's architecture questions from the
evidence, with citations. If it's not useful, tell me where it's wrong
— that's worth more to me than the sale.
```

**The brief's own structure**, so it is consistently good and cheap to
produce (the pipeline drafts it; she reviews it):

1. The question, restated in one sentence in their terms.
2. **The answer, in the first forty words.** Not a preamble.
3. What the evidence says: the supporting claims, with sources and dates.
4. **What contradicts it**, always, and if nothing does, say that
   explicitly — a brief that never disagrees with itself is marketing.
5. Confidence, plainly: strong / mixed / nobody knows yet. "Nobody knows
   yet" is a legitimate and valuable answer and must be allowed to
   appear, or the whole product is compromised.
6. What would change the answer, and when we would expect to know.

### G — listing copy for registries and directories (lane G)

Sales drafts; the engineer seat submits. Short form, long form, and the
one line that matters most.

**Name:** alexandria

**One line:** Agent skills with their evidence attached — every skill
cites the papers and claims it came from, and a dated before/after
result.

**Short description (registry field):**
```
Skills distilled from a research pipeline that reads AI papers daily
and tracks which technique claims hold up over time. Every skill ships
with a provenance block: the claim IDs it rests on, its source papers
by arXiv link, and a dated A/B validation of what changes when it's
loaded. Two skills today — harness engineering and self-improving
post-training loops — with more as the pipeline promotes them.
```

**The footer line that goes at the bottom of every SKILL.md file**
(idea-list.md #9 — the cheapest distribution mechanic we have):
```
Provenance and the claim graph behind this skill: github.com/alexandrapaiz/alexandria
```

---

## 5. The HN comment kit (lane B, prepared before launch morning)

A Show HN is decided in the comments, not the post. These three are
drafted now because 10am on launch day is the worst possible time to
compose a careful answer to a hostile question.

**Objection 1 — "Why would I pay for a markdown file an LLM could
generate?"** (We know this is coming: it was the top comment on
skillbay.sh's thread, 2026-09-17.)

```
Fair, and I'd ask the same. You're not paying for the file — the files
are public and free, and you can read both right now. What's behind the
paywall is the thing that makes a file trustworthy: the claim graph it
was distilled from, which tracks what's been supported and contradicted
over time, and the automations built on it.

Concretely: one of the public skills records that a bare model endorsed
imitation fine-tuning on a stronger model's trajectories, and with the
skill loaded it refused and cited a measured 4-30 point regression. An
LLM will happily generate a skill file about distillation. It won't
generate that number, because the number came from reading the papers
and tracking which claims survived.
```

**Objection 2 — "This is a newsletter with extra steps."**

```
The newsletter is free and always will be, full issues, because I think
AI news is a commodity and the market agrees — every comparable digest
is free and ad-supported. The paid part isn't more reading. It's the
skills, the claim graph, and the automations: the operational layer.
If the free digest is all you ever want, that's a completely fine
outcome and costs you nothing.
```

**Objection 3 — "Your agents wrote this, so why should I trust it?"**
(The one unique to us, and the one most likely to decide the thread.)

```
Because you can check. Every decision is a dated ADR in the repo,
including the reversals. Every agent has a written charter you can
read. When a run fails or an agent underdelivers, it goes in a public
incident register — there's an entry in there where I rejected a run's
work as "poorly creative" and made it do it again.

And the substantive answer: no claim in the product rests on an agent's
opinion. It rests on papers, with the citation attached, which is the
whole reason the claim graph exists. If you find one that doesn't, that
would be the most useful comment in this thread.
```

**Rules for her in the thread, which matter more than the drafts:**
never argue with a downvoted comment; concede every point that is
actually correct, immediately and without qualification; answer the
hardest question first, because everyone is reading that one; and if she
does not know, "I don't know, and here's what would tell us" is the
strongest thing anyone says on Hacker News.

---

## 6. Before anything is sent — the verification pass

Run once on **2026-10-07 (day -6)**, then per-batch before each send.
Non-negotiable: a note referencing a thread that has been deleted, or
addressed to a handle that has changed, costs the relationship outright.

1. **Re-open every linked thread** and confirm it exists, the quote is
   accurate, and the handle is current. Four HN threads, four links, ten
   minutes.
2. ~~**Resolve lane C3's open gap**~~ **— done 2026-09-18.** Handles and
   quotes are in lane C above, verified via the Algolia item API after
   HN returned 429. What remains for day -6 is narrower and still
   required: confirm the handles and threads still exist, and find
   **that week's equivalent threads**. By 2026-10-13 these are four
   weeks cold; the named people are the permanent template for what a
   good target looks like, but a reply to a month-old thread is read by
   nobody. The market agent's Friday brief is the natural supplier of
   fresh ones.
3. **Confirm every product fact in every draft** against
   docs/sales/first-customers.md §10. Specifically: is there an issue
   link yet (gates D1)? Is signup live (gates the A-drafts' link)? Are
   there still exactly two gold skills?
4. **Fill every bracket.** A draft with a live `[BRACKET]` in it is
   unfinished, and the brackets in the F-drafts are the specific reason
   those notes are not generic.
5. **For each lane-F target, name a human and a reason.** Category fit
   is not fit. If she cannot write the first line about something that
   person specifically did, the target comes off the list — the same
   standard that correctly removed the listicle sites.

---

## 7. What happens when someone replies

| Reply | What she does | What she does not do |
|---|---|---|
| **"Interesting, tell me more"** | One reply, the specific thing they'd care about, one link. | Send a deck. Book a call for a $20 product |
| **"How much?"** | The price, plainly, in the next reply. $20/month individual, [TEAM PRICE] for teams. | Discount it. Ever, and especially not at launch |
| **A hard technical objection** | Answer it properly, concede whatever is right, and **log it** — three people making the same objection is a positioning finding for the market agent, not just a conversation | Get defensive with the exact audience whose skepticism is the market |
| **Silence** | One follow-up at day +7 (draft A4), then closed permanently | A third touch |
| **"No" / "not for me"** | "Understood, thanks for telling me" and remove them. | Ask why, unless they volunteer. A clean no is a gift |
| **"I'd want X before I'd pay"** | Log it in `results.md`. This is the most valuable reply on the list | Promise X |
| **A team-sized signal** ("everyone here keeps asking...") | Draft A3, same week | Wait for a better moment. There isn't one |

**Everything that comes back goes into `docs/sales/results.md`** —
real numbers and real quotes only, never an estimate, per that file's
own standing rule. Sales' next run plans from what actually happened,
not from this document.

---

## 8. What this plan does not do

- **It contacts no one.** Not one message, not one account, not one
  follow, not one registry submission. Every line above is hers to fire
  or bin (prompts/sales-agent.md, the one law).
- **It names no person it has not verified.** Lane C3 sits deliberately
  incomplete for this reason, with the fix scheduled rather than guessed.
- **It states no price it is not allowed to state.** Team pricing is the
  owner's decision (first-customers.md §B2B-1); the drafts leave the slot
  open on purpose.
- **It promises nothing the product does not do today.** Two skills, a
  free digest, a claim graph, a public repo. No library, no subscriber
  count, no live metric that is currently hardcoded.

---

## Change log

- 2026-09-18: first version, fourth sales run, owner dispatch following
  docs/agents/incidents.md item 11, which named "no concrete outreach
  plan" as one of four omissions. Absorbs and extends
  docs/sales/outreach/list.md's four verified targets. Companions:
  docs/sales/first-customers.md (the plan),
  docs/sales/idea-list.md (the idea bank).
