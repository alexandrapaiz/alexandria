# Hacker News — Show HN (launch day, 2026-10-13)

Venue read: HN distrusts hype, rewards receipts, and will test every
claim by clicking through. It just gave a hand-curated skill
marketplace (skillbay.sh, Show HN 2026-09-17) a skeptical reception —
top comment: "Why would I buy a markdown file that someone most likely
got an LLM to generate while I can just simply get my own LLM to
generate a similar one for me for free?" (news.ycombinator.com/item?id=49743459).
The founder conceded AI-generated skills "are usually pretty bad." That
thread is this post's best pre-mortem: lead with verification, not
volume, or expect the same comment.

**Post as Show HN**, not Ask HN or a plain link — the product has a
working repo and a shipped artifact, which is what Show HN is for.

**Timing:** weekday, mid-morning ET, per general HN front-page
convention. Avoid Friday/weekend.

---

**Title:**

```
Show HN: Alexandria – an AI research org that publishes its own decisions
```

(Alternate, more literal: `Show HN: A research pipeline that turns AI
papers into Claude skills, with citations`. Owner's call on which title
undersells less — the first leads with the unusual-org hook, the second
leads with the mechanism. Test with the first; it's the harder claim to
ignore.)

**Body:**

```
Alexandria is a small AI research pipeline I've been running:
it reads arXiv and lab blogs daily, distills claims, tracks which
ones get contradicted or supported over time (a claim graph, not
a link list), and turns the ones that hold up into Claude Agent
Skills — procedure files an agent can load, each one citing the
papers and claims behind it.

Two things about it that I think are actually unusual, and that I'd
rather show than claim:

1. Every decision the project has made is a public, timestamped ADR
   in the repo (docs/decisions.md) — including the ones that didn't
   work. Nothing is retconned after the fact.

2. The org running it is mostly autonomous agents, each with a
   written charter, each opening its own pull request. I merge them
   or I don't. This post you're reading was drafted by the sales
   agent (prompts/sales-agent.md) under a charter that says, in its
   own words, "you prepare, I send" — I'm sending it now, unedited
   except for whatever I choose to cut before I hit submit.

The skill that's actually live today —
skills/harness-engineering/SKILL.md — carries the format I want every
skill to have before I call this a library: 12 claims, 5 papers, and
a dated A/B result (loading the skill changed what the model
recommended, logged in the frontmatter, not asserted in a landing
page).

I bring this up because I think it's the actual answer to the
skillbay.sh thread from last week ["Why buy a markdown file an LLM
could write"] — you're right not to pay for the file. The file isn't
the product. The evidence trail behind it, and the graph that keeps
checking whether it still holds, is what a prompt can't generate for
you on the spot.

The digest (the same claim graph, written up weekly) is free, full
issues, no paywall on the writing itself — that part's genuinely
commoditized and I'm not pretending otherwise. What's paid, $20/mo,
starting today, is the operational layer: the skills, the queryable
claim graph, and the automations built from digest findings. One
skill live so far, more shipping weekly — I'd rather undersell that
number than round it up.

Repo: github.com/alexandrapaiz/alexandria
Site: [SITE_URL]
Happy to answer anything, including "why should I trust a claim
graph I can't audit" — the repo's public specifically so you don't
have to take my word for it.
```

**Anticipated pushback and how to answer in comments (owner's call on
tone, drafted for reference):**

- *"This is just a skill marketplace with extra steps."* → No
  marketplace: one seller, one evidence standard, applied to every
  entry. Point at the provenance block in SKILL.md directly.
- *"Why would agents/companies trust an evidence trail an LLM
  wrote?"* → Honest answer: the same way you'd trust any citation —
  check it. The claims cite real arXiv IDs; the contradicts/supports
  edges are checkable against the papers. Don't oversell this one.
- *"One skill isn't a library."* → Agree plainly. "Correct, it's one
  skill and a pipeline that's supposed to produce more — judge us on
  whether it does, not on the pitch."

**What not to say:** no subscriber counts (there aren't real ones
yet), no "growing fast," no comparison claiming to beat Elicit/Consensus
outright — the honest claim is a different job (orchestration/systems,
not paper search), not a better one at their job.
