# Reddit — subreddit drafts (launch day, 2026-10-13)

Venue read: subreddit self-promotion tolerance is sub-specific and
changes without notice — sales can't verify current moderator rules or
flair requirements same-day. **Check each sub's current self-promo
rule and required flair immediately before posting**, not from this
file's assumptions. Post a day apart rather than all at once so one
takedown doesn't cost the whole run.

Three subs chosen for genuine audience fit, not reach:

## r/ClaudeAI

Fit: audience already uses Claude Agent Skills directly — the exact
buyer for "skills with receipts."

```
Title: Built a skill-authoring pipeline that attaches evidence to
every Claude skill (claims, papers, a dated A/B test)

Every Claude skill I've seen ships as instructions with no way to
check if they're any good — a recent audit of 216 public skills found
69% "won't reliably trigger." I got tired of guessing, so I built a
pipeline that reads AI research daily and only promotes a skill to
"done" once it has a provenance block: the specific claims it rests
on, the papers behind them, and a recorded before/after test (did
loading the skill actually change what the model recommended).

One skill live so far — skills/harness-engineering in the repo below,
frontmatter has all of it. More coming out of the pipeline weekly.
Repo's public, pipeline's public, feedback welcome, especially "this
provenance format is still not enough because ___."

github.com/alexandrapaiz/alexandria
```

## r/AI_Agents

Fit: agent builders who evaluate orchestration technique claims
directly — the exact audience the claim graph and harness-engineering
skill serve.

```
Title: A claim graph for agent-orchestration research (supports/
contradicts edges, not just a link dump)

If you build multi-agent systems you've probably run into the same
problem I did: research on harness design, orchestration patterns,
context engineering moves fast, contradicts itself constantly, and
there's no maintained record of what's actually held up versus what
got walked back.

I built a pipeline that ingests arXiv + lab blogs daily, distills
claims, and tracks supports/contradicts edges between them over time,
plus a weekly digest of what's trailblazing, what's matured, and
what's been left behind. The claims that hold up long enough turn into
Claude skills with the evidence attached — the harness-engineering one
in the repo is the first example (12 claims, 5 papers, a dated A/B
result in the frontmatter).

Digest is free. The skills/claim-graph/automation layer is $20/mo,
launched today. Repo's open if you just want to see the pipeline:

github.com/alexandrapaiz/alexandria
```

## r/SideProject

Fit: this sub explicitly welcomes launch posts and rewards an
authentic build story over a polished pitch — the "an agent org chart
runs this" angle is exactly the kind of unusual build story that does
well here.

```
Title: Launched today: a research pipeline where most of the "team" is
autonomous agents, each one's decisions logged in public

Wanted to share something a little unusual. alexandria reads AI
research daily and turns findings that hold up into free digests and
paid Claude skills (each one citing its sources). Nothing novel about
that shape on its own.

What's a little different: most of the day-to-day running of the
project — research, drafting, proposing changes — is done by
autonomous agents, each with a written charter, each opening pull
requests against a public repo. I (the actual human) review and merge,
or don't. Every decision the project's made, including the ones that
didn't work, is logged in the open as a dated ADR, not cleaned up
after the fact.

This launch post itself was drafted by the "sales agent," under a
charter that says, verbatim, "you prepare, I send." I'm sending it.

Free digest, $20/mo for the operational layer (skills + claim graph +
automations), one skill live so far with more shipping weekly. Happy
to answer anything about how the agent org actually works day to day.

github.com/alexandrapaiz/alexandria · [SITE_URL]
```

**Common instruction across all three:** no crossposting the identical
text to all subs same-hour — reddit's spam detection and several
communities' cultures both penalize that. Space by at least a day and
let the copy above be the message, not a mechanical duplicate.
