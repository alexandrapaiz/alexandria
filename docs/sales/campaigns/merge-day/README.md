# Merge Day — the launch when the cart is not open

Proposed 2026-10-05 by the sales seat, T-8. For the owner's yes or no.
Nothing here has been published, shown, posted or sent. Every asset in
this folder is complete enough to go out the hour she says go, and the
campaign depends on **no merge, no code, and no seat but hers.** That
last property is the reason it exists.

## The situation it answers, in four lines

The launch date is 2026-10-13 and O1 KR1 says both plans are purchasable
end-to-end that day with no manual steps. On the morning of 2026-10-05
there is no payment integration in the tree, no open pull request
containing one, and `site/lib/entitlement.js` returns null for everyone
by construction. Six of the seven drafts in `../../launch/` say the
library opens today. The evidence is in `../../launch-gate.md` §1.

So there are three honest doors and only three. Move the date. Launch an
announcement with no cart and hope nobody clicks. Or change what the
launch is *about*.

## The bet

**Launch the company, not the store.** Those have been the same event by
assumption, and nothing requires it. The cart opening is a feature ship.
A company becoming public is a one-time event, it is the one this date was
actually bought for, and it can happen on 2026-10-13 with no engineering
whatsoever, because the thing being launched is already written.

What goes public on Merge Day is the record. Twelve chartered agents, each
with its charter in `prompts/`, each opening its own pull requests, none of
them permitted to send anything. Forty-three dated decisions in
`docs/decisions.md`, including the reversed ones. An eighty-entry register
of the company's own failures, written by the agents that caused them. A
weekly digest, free in full, with the evidence under each finding. And a
library those findings become, which costs $20 a month and is not open yet.

The ask is the waitlist, and the waitlist is real today
(`site/app/api/waitlist/route.js`, a duplicate submit treated as success).

**The reason this is better than it sounds, and it is the whole thesis.**
Every company in this class can buy a writer and ship a digest next month.
Not one of them can produce three weeks of dated self-correction, because
that artifact is made of time. It is the only asset here that a funded
competitor cannot acquire, and until today it has never been the subject of
a single post. Launch posts in this genre are all the same post: a founder
explaining that their agents are real. Ours hands over the failure log and
lets the reader check.

## The move nobody expects, and it is the one to fight for

**The headline artifact is the incident register, and the headline number
is a defect in it.**

```bash
grep -cE '^## INC-' docs/agents/incidents.md             # 54
grep -cE '^## Incident [0-9]+' docs/agents/incidents.md  # 26
grep -oE '^## Incident [0-9]+' docs/agents/incidents.md | sort -u | wc -l  # 14
```

Eighty entries. Twenty-six of them are numbered, and those twenty-six
numbers collapse to fourteen: incidents 24, 25 and 26 each exist three
times, and 27 through 31 twice each. The company's own failure register
cannot count its own failures, because a sequential counter in a file is
not an allocator when every agent writes on a separate branch and none of
them can see each other. That collision is itself an entry in the
register, written by the seat that caused it, and the fix it prescribes is
the date-slug identifier the newer fifty-four use.

That paragraph is the launch. It is unfakeable, it is checkable in three
commands, it is funny in the specific way this audience finds credible,
and no marketing department on earth would let it out of the building. A
company that publishes the bug in its own bug tracker has said something
about itself that no adjective can say.

**The second move, in the same spirit.** The post does not claim the
register is complete. It states the opposite, with the evidence: a
generated company-wide view reports fifty-seven entries carrying no status
marker, so the register cannot say which of its own incidents are open.
That is a standing company lesson, L-A28, in the vendored standards file
anyone can read. Naming the limit is what makes the rest of it believable.

## What it does not do, stated before she asks

- **It takes no money, so it cannot satisfy O1 KR1 or fund O1 KR2.** KR1
  is committed and this campaign does not meet it. It converts a missed
  committed KR into a dated public event and a waitlist, which is the best
  available outcome and is not the outcome that was promised. The October
  check-in should grade KR1 on the cart, not on this.
- **It spends the launch card.** There is one first day. Spending it on the
  company and not the product means the cart opens later to a warm list
  instead of a cold one, which is a real cost and arguably a benefit, and
  this seat will not pretend to know which.
- **It invites a hostile read.** "Sixty-four open pull requests" can be
  read as a company that cannot ship. The framing answers it by being the
  merge rather than the backlog, and by never claiming a queue number the
  post does not also explain.
- **It cannot be run twice.** If she takes this and the cart opens on
  10-27, that second day gets the drafts in `../../launch/` as written,
  and they are already written.

## The four assets, all in this folder

| File | Venue | State |
|---|---|---|
| `hn.md` | Hacker News, Show HN | Drafted in this pull request |
| `x.md` | X, thread | Drafted in this pull request |
| `email.md` | The comped free list | Drafted in this pull request |
| `linkedin.md` | LinkedIn | Drafted in this pull request |

Each one is written for its venue under the canon and the ban list, each
one states the $20 price without charging it, and each one carries the
waitlist as its only ask. The reading list every asset points at is the
same three paths, and it is deliberately not the home page:

1. `prompts/` — the twelve charters, including the one that forbids this
   seat from sending anything, which is the fastest way for a stranger to
   verify the claim that a human sends every message.
2. `docs/agents/incidents.md` — the failures.
3. `docs/decisions.md` — forty-three dated decisions, with the reversals
   left in.

## The mechanic: the open incident register

A growth mechanic that spends no trust, because the thing being given away
is a line in our failure log.

**The offer.** Find something on the site or in the repo that is wrong — a
stale number, two documents that contradict each other, a claim with no
evidence behind it, a link that does not reach the paper it says it does —
and it gets registered. A dated entry in `docs/agents/incidents.md`, the
defect in plain words, the fix or the reason there is none, and the
finder's handle in the entry. Public, permanent, and in the same register
the company uses on itself.

**Why it works on this audience and would work on no other.** The people
being invited are the ones who already audit things for free and post the
results, which is how `../../outreach-plan.md` lane C found its names.
Attribution in a public engineering register is the currency they actually
use. It is also the one referral mechanic that cannot become a dark
pattern, because the reward is a record of our error.

**What it costs us.** Someone will find something real in the first hour.
That is the mechanic working. The rule that makes it survivable is the one
the register already runs on: the entry gets written whether or not it is
flattering, and the fix or the refusal is named beside it.

**One decision inside this that is hers and not this seat's.** A finder
who reports a material defect could be given the library free for a year.
That is a pricing decision and this seat does not make pricing decisions
(charter boundary, and `../../first-customers.md` §B2B-1 leaves the team
price blank for the same reason). The mechanic above works with
attribution alone. The comp version is stronger and it needs her word.

## The ask she can refuse per line

| When | Who | What | Blocks |
|---|---|---|---|
| 10-06 | owner | Yes or no on Merge Day as the Shape B fallback in `../../launch-gate.md` §6. A no here costs nothing: the `../../launch/` drafts remain the plan and this folder goes unused. | the rest |
| 10-06 | owner | Yes or no on leading with the register's own numbering defect. A no on this is a no on the campaign's best paragraph, and the fallback is to lead with the charters instead, which is true and ordinary. | the copy |
| 10-07 | owner | Yes or no on the open incident register, and separately on whether a finder gets comped. | the mechanic |
| 10-08 | engineer | One question answered, not a build: how far from a working Polar checkout is the tree. This is what decides Shape A against Shape B and nobody has asked it. | the shape |
| 10-12 18:00 UTC | owner | The go/no-go in `../../launch-gate.md` §6, with this folder as the Shape B answer. | send |
| 10-13 | owner | Send, in her own hands, in whatever order she likes. | — |

## Where this came from

Lane D2 of `../../outreach-plan.md` already named the angle, for podcasts:
"an eleven-agent company that runs itself and publishes its own incident
register." That was written as a pitch for a conversation with a host. This
campaign is the same observation promoted to the launch's subject, and the
count has since moved from eleven to twelve.

The honesty rules in `../obsolescence-report/` govern this folder too, all
six of them, and the fourth one especially: the embarrassing section leads,
and the morning of the send is when someone will want to move it down.
