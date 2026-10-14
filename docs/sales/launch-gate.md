# The launch gate — which merge makes which sentence sendable

Written 2026-10-05, T-8 to launch. Readings taken between 03:00 and 03:30
UTC that morning and every one of them carries the command that took it.
Nothing here is sent, posted or scheduled.

## What this file is for, and why it did not exist until now

`claim-ledger.md` answers whether a sentence is true today. It does not
answer the question the owner actually faces in the eight days before
2026-10-13, which is narrower and harder: **for each sentence the launch
needs, what has to land in `main` for it to be true, and what does the
sentence become if that thing does not land.**

Those are different questions because this company's work does not reach
`main` when it is finished. It reaches `main` when the owner merges it.
On the morning of 2026-10-05 there were 64 open pull requests and `main`
had taken two commits in five days, both of them the same vendored
standards sync. Twenty of the 64 are drafts, which GitHub will not let
her merge at all.

```bash
gh pr list --state open --limit 200 --json number -q 'length'                      # 64
gh pr list --state open --limit 200 --json number,isDraft -q '[.[]|select(.isDraft)]|length'  # 20
git log --oneline --since=2026-09-30 main                                          # 2 commits
```

So the launch's binding constraint is not writing, research, design or
code. All four are producing faster than they are being absorbed. The
binding constraint is the merge, and sales is the only seat that can say
which merges the launch copy is standing on, because sales is the seat
that would have to send the sentence that the missing merge makes false.

Three rules for reading what follows.

1. **Sales owns no row here.** Every row is an ask. The owner grants it,
   refuses it, or moves the date.
2. **Every fallback sentence is already written.** A fallback invented on
   the morning of the send is a fallback written under pressure by the
   person least able to judge it. Each row below carries the sentence the
   draft becomes, so the decision on 10-12 is a choice between two
   sentences rather than a drafting session.
3. **A row's absence from an open pull request is the finding.** For
   several of the rows below, the gap is not that the work is unmerged.
   It is that no open pull request contains it. Those are the rows to
   read first.

---

## 1. The row the launch is defined by

**KR1, committed, in its own words:** "By 2026-10-13, the site is public
with a digest archive and the skill library; free digest signup (full
issues) and the $20/month paid spine are both purchasable end-to-end the
same day, no manual steps." (`docs/okrs/okrs-2026-Q4.md` O1 KR1.)

**Reading, 2026-10-05.** Not started, and nothing in flight starts it.
Three separate gaps, and each one alone is sufficient to stop a sale.

| Gap | Evidence | In any open pull request? |
|---|---|---|
| No payment integration exists. Polar is the decided processor (ADR-30, Merchant of Record, chosen because Stripe does not operate in Guatemala). The word `polar` appears in the tree four times: two legal pages, one schema comment calling the column "unused until payments open", and one comment in `account-core.js` saying how Polar "will" write status. There is no checkout route, no webhook, no client. | `git grep -li polar -- site db pipeline tools` | **No.** Zero of 64. |
| Entitlement can never return true. `site/lib/entitlement.js` gates the spine on `hasSpine()`, which gates on `currentEmail()`, which is `return null`. The file says so itself: "the whole $20 spine is shut. It fails closed, so nothing leaks, and that is the only good news in it." | `cat site/lib/entitlement.js` | **No.** |
| The pricing page offers no purchase. Both plans render a pill reading "Opens October 13", and the page's only working control is the waitlist form. ADR-31 says those pills "become the three offers" — trial, $20 monthly, $200 lifetime. Nothing has made them. | `grep -n 'Opens October 13' site/app/pricing/page.jsx` | **No.** |

**What is actually built, and it is not nothing.** Accounts landed since
the drafts were written. `@clerk/nextjs` runs in `site/middleware.js`,
`/sign-in` and `/sign-up` are routes in the tree, `/api/clerk-webhook`
verifies Clerk's signature and writes users into Neon, and ADR-34 makes
Neon the system of record. The identity half of ADR-30's architecture is
real. The money half has not been started. Whether the identity half
*serves* is a deploy reading this seat cannot take from the repository,
which is L-A16, so no draft asserts it.

**The copy consequence, which is the whole point of this file.** Six of
the seven launch drafts tell a stranger that the library is $20 a month
and that it opens today.

```
docs/sales/launch/email.md:20       The library opens today
docs/sales/launch/linkedin.md:20    Alexandria opens today.
docs/sales/launch/linkedin.md:38    The library is $20 a month
docs/sales/launch/reddit.md:114     subscriptions opening today
docs/sales/launch/hn.md:97          costs money is the library, at $20 a month
docs/sales/launch/x.md:79           The library costs $20 a month.
docs/sales/launch/pre-launch-teasers.md:83  the skill library is $20 a month
```

Every one of those is unsendable on 2026-10-13 if the three gaps above
are still open, and "unsendable" is not a style judgment. A post that
says a thing opens today, read by an audience that clicks, against a page
that offers no way to buy, is the one failure mode the honest-marketing
rule in this seat's charter exists to prevent. It also costs more than
silence would, because the reader who clicks and finds nothing does not
come back on the day it works.

**The fallback sentence, drafted now so it is not drafted then.** It is
one sentence and it is true today, because the waitlist is real and
writes to Postgres (`site/app/api/waitlist/route.js`).

> The weekly digest is free and arrives in full. The library it is drawn
> from costs $20 a month and is not open yet. Leave an email and you will
> hear once, on the day it opens, and nothing before that.

That sentence is weaker than the one it replaces and it is stronger than
it looks. It states a price without taking money, which is the posture
the pricing page already holds, and it keeps the only ask the site can
honour today. See `campaigns/merge-day/` for the launch shape built
around it rather than apologising for it.

---

## 2. The archive, and a correction to this seat's own ledger

**`claim-ledger.md` row C1 said two issues. One renders.** `site/lib/content.js`
line 23 holds `HIDDEN_WEEKS = new Set(["2026-W37"])`, retiring the pilot
on the owner's order of 2026-09-19 so that the next issue would be the
first one a stranger reads. The order was carried out. The ledger was
written as though the file still listed what `ls` lists.

```bash
ls site/content/issues/                        # 2026-W37.md  2026-W39.md
grep -n 'HIDDEN_WEEKS' site/lib/content.js     # W37 is not served
```

So a stranger who clicks "Read an issue" on launch morning sees **one**
issue, 2026-W39, covering the week of 2026-09-21. On 2026-10-13 it will
be three weeks old, and the two weeks since it — W40 and W41 — have no
file. No open pull request writes one: zero of 64 touch
`site/content/issues/`.

**Two drafts carry the overstatement and both must change.**

```
docs/sales/launch/hn.md:97   The archive holds two issues today,
docs/sales/launch/x.md:79    The archive holds two issues today,
```

Fixed in this pull request to the true form, which is also the better
sentence, because a reader who counts finds exactly what the post said:

> The archive holds one issue today. The pilot before it was pulled
> because it was not good enough to be the first thing you read.

That is a sentence no competitor's launch post can say, and it is only
available to us because it happens to be true.

**The ask.** One issue in the archive dated the week of launch. It is the
cheapest high-value merge on this list and it belongs to the writer seat,
whose five open pull requests contain voice registers, reviews and the
digest prompt, and no issue.

---

## 3. The home page metric

| | |
|---|---|
| **Sentence at risk** | Any draft pointing a stranger at the home page as the receipt for scale. |
| **Reading 2026-10-05** | `site/app/page.jsx:44` still prints `<b>{papersThisWeek}</b> papers read this week` over a count whose own definition, in `site/lib/metrics.js`, is `count(*) from papers where fetched_at > now() - interval '7 days'` — what arrived, not what was read. |
| **The law it breaks** | Canon law 15, her ruling of 2026-09-25: only the full-read count may take the verb *read*. The repair was drafted as `docs/voice/home-metric-line-2026-09-26.md` on 2026-09-26. |
| **In any open pull request?** | **No.** Zero of 64 touch `site/app/page.jsx`. Nine days. |
| **Sales' position** | Unchanged from 2026-09-30 and now dated: no draft quotes that line, and no draft links the home page as a scale receipt. Drafts link `/library`, the repo, and the skills. |
| **Note that softens it** | The metric renders only when `INGEST_COUNT_URL` is set, and returns nothing otherwise. If it is unset in production the false verb is invisible, which is luck rather than a fix, and L-A16 says a reading taken from the repo cannot tell us which. |

---

## 4. The skill library's two receipts

| # | Sentence | Reading 2026-10-05 | Moved since 09-30? |
|---|---|---|---|
| A1 | Six skills are live. | True. Six directories with `SKILL.md`. | No |
| A3 | One of the six carries a recorded trial showing that loading it changed what the model recommended. | True, and still one. Five still `validated: ""`. | No |
| A4 | The newest retrieval run put the library at 40 of 43. | True, dated 2026-09-29. The newest file in `skills/_validation/results/` is still that day's. | No |
| A6 | Twelve skills. | Still false, still a 2026-12-31 aspirational target at ~0.7. | No |

```bash
ls -d skills/*/ | grep -v _validation | wc -l         # 6
grep -c 'validated: ""' skills/*/SKILL.md             # 5 of 6 empty
ls -t skills/_validation/results/*.txt | head -1      # 2026-09-29
```

**Where the merge queue bites here.** Six of the 64 open pull requests
touch `skills/_validation/results/` — #140, #146, #151, #152, #159, #200,
from the skill seat across six days. Whatever those add to the library's
evidence, no launch draft may use it, because a draft cites what a
stranger can open and a stranger cannot open a branch. That is L-A18's
third clause applied to copy: a citation into an unmerged branch reads as
evidence and is not one.

**So the drafts stand as written.** They cite A1, A3 and A4 at their
2026-09-29 values and name the difference between the two receipts out
loud. No row in this section blocks a send. This section exists to record
that it was checked, which is the thing that did not happen for twelve
days before 2026-09-30.

---

## 5. Merge order, if she merges nothing else

Five merges, ranked by sendable sentence unlocked per unit of her time.
Nothing below is a technical opinion about the code; it is the order in
which merges convert into things the launch may honestly say.

| # | Merge | Unlocks | Cost if skipped |
|---|---|---|---|
| 1 | Anything that makes the $20 spine purchasable, from any seat, in any shape, including a Polar-hosted checkout link that does not touch our code | Six drafts' central sentence, KR1, and KR2's revenue | The launch is an announcement with no cart. `campaigns/merge-day/` is the honest shape for that day and it is a different launch |
| 2 | One issue in the archive dated the week of launch | "An issue a week" becomes approachable, and the archive stops being one three-week-old file | The strongest click-through on launch day lands on a single stale page |
| 3 | `site/app/page.jsx`'s reading verb | The home page becomes linkable as a receipt, and canon law 15 stops being broken on the company's most-read surface | No draft may point at the home page's number. Survivable, and it is nine days old |
| 4 | The deprecated-claims page (sprint 2026-09-28 item 5) | The one claim no competitor can make gets a public surface, and `campaigns/obsolescence-report/` gets its link target | The obsolescence report ships as prose with no permanent page to cite, which is most of its distribution value |
| 5 | Any further A/B trial on a second skill | A3 goes from one of six to two of six, which is the difference between an anecdote and a practice | A3 stays an anecdote. The drafts already say so plainly, so nothing breaks |

**The twenty drafts are a separate ask and a cheap one.** Twenty of the
64 open pull requests are drafts, and GitHub will not merge a draft, so
every standup that reports 64 as the queue depth is reporting a number
twenty higher than the number of things she can act on. That is L-A27's
second cost, measured here. This seat's own #156 was one of them for five
days, which is in the incident register in this pull request.

---

## 6. The go/no-go, with a time on it

**Monday 2026-10-12, 18:00 UTC.** One reading of this file's commands,
then one of three shapes. The date is a suggestion and the structure is
the point: the decision gets made the night before by someone with a
document in front of her, not at 09:00 on launch morning.

**Shape A — the full launch.** Gaps 1 and 2 closed: a stranger can buy
the spine and the archive has a fresh issue. Send `launch/` as written.

**Shape B — Merge Day.** Gap 1 still open. The launch happens on the date
and the ask is the waitlist. The subject is the company and its record
rather than the cart. Drafts in `campaigns/merge-day/`, and the price is
stated in every one of them without being charged.

**Shape C — move the date.** Available, and the only argument for it is
that a dated launch is worth more than the thing launched. This seat's
reading is that Shape B is strictly better than Shape C, because the date
is a promise made publicly at the first all-hands and the waitlist makes
the date honest without the cart. But the call is hers, and if she takes
C the pre-launch teasers simply continue and nothing in this directory is
wasted.

**What would make this seat wrong about B over C.** If the spine is four
or five days from done on 10-12, Shape C spends a week to get Shape A,
and Shape A is worth more than B. The question that settles it is one the
engineer seat can answer and this seat cannot: how far from a working
Polar checkout is the tree. That question is the single most useful thing
she can ask on 10-12, and it is why this file names an hour.

## Change log

- 2026-10-05: first version, this run. Supersedes the "Blocking
  dependencies" section of `calendar.md`, which was written 2026-09-18 and
  whose four items are now two fixed, one unchanged and one superseded.
