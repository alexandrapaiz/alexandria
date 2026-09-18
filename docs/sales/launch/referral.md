# Referral and share mechanics

Design constraint from the charter: self-built, honest, no dark
patterns — the same billing-honesty principle (vision.md §4) extends to
growth mechanics. No fake urgency, no "your friend already joined and
is waiting" pressure copy, no gamified points system pretending to be
more than it is.

## What exists to build on today

The current send is Gmail SMTP to a `subscribers` table
(roadmap.md, sprint 1) — no referral infrastructure, no per-subscriber
codes, no attribution links. Two mechanics below, ordered cheapest
first, so the launch doesn't wait on engineering work sales can't do
itself.

### Mechanic 1 — "forward this issue" (live at launch, zero build)

The launch email (`email.md`) and every digest going forward ends with
a plain-language forwarding ask, not a tracked link:

```
If you know one or two people who'd actually use this — not "might
click a link," but would use a claim-graph-backed skill or want this
in their inbox — forward this email. That's the whole ask.
```

No tracking, no attribution, no reward. Costs nothing, asks honestly,
and is the correct mechanic for a list this small (comped friends):
manufacturing a referral-code system for a few dozen people is
overhead the charter's own "scalable cheap" instruction argues against
at this stage.

### Mechanic 2 — manual referral credit (propose once the list has
grown past comped friends, e.g. post-launch)

Once there's a real free-signup flow (blocked today — see
`calendar.md`'s dependency list), the honest, cheap version of a
referral reward:

- A subscriber emails or replies with the name/email of someone they
  referred who signed up for the paid spine.
- The owner manually credits one free month. Manual because building
  attribution tracking (unique codes, a referral table, webhook
  credit-application logic) is real engineering scope this run
  shouldn't propose spending before the paid product itself has more
  than a handful of subscribers to make it worth the build.
- Ledger this as an engineer-agent proposal once volume justifies
  automating it — a unique referral parameter on the signup link is
  the minimum viable version (attribution without a full rewards
  system), and even that should wait until the signup flow itself
  exists.

**What this deliberately avoids:** a leaderboard, a public referral
count, or any framing that turns sharing into a competition — none of
that fits the house voice, and none of it is needed to make forwarding
an email work.

## Share-this-issue mechanic (digest-level, not referral-level)

Separate from referrals: each digest issue, once the archive actually
renders (currently broken per the market report), should carry a plain
"share this issue" link to its own page — the cheapest possible growth
loop, since it turns every good issue into its own acquisition surface
without asking a subscriber to do anything but read. This is a site
feature (an issue permalink with unencumbered social meta tags), not a
sales-lane deliverable — flagging it here because it's the single
highest-leverage cheap-and-scalable mechanic on this whole list, and it
depends entirely on the archive-rendering fix already noted in
`calendar.md`.
