# The claim ledger — every sendable sentence, and what makes it true today

Verified 2026-09-30, T-13 to launch. Re-verify before any send; the
right-hand column is a reading, not a constant.

## Why this file exists

The launch drafts in `docs/sales/launch/` were written on 2026-09-18. Between
that day and this one the owner issued four dated copy rulings, four more
skills shipped, the site grew a working email capture, the home page gained a
live metric, and the skill library got its first measured retrieval score and
its first independent usage review. Nothing re-read the drafts against any of
it. On 2026-09-30 the launch email still said one skill was live when six
were, and the Hacker News draft still offered "12 claims, 5 papers" as the
whole library's receipt.

That is the failure the writer seat already named in its own register: a
ruling that is recorded and then violated because nothing between the ruling
and the artifact ever opened the file. Sales inherits the same defect with a
larger blast radius, because a launch send cannot be corrected in a follow-up
the way a web page can.

So the fix is not a better memory. It is this table. Every claim any draft
makes gets one row, and the row carries the command or the file that settles
it. The pre-send step is reading down the "Checked" column, not recalling
what was true two weeks ago.

## How to read a row

- **Claim** is the sentence in a draft, in the form a stranger would read it.
- **True today** is the reading taken on 2026-09-30, with the source.
- **Check** is how to take that reading again in under a minute.
- **Owner of the fact** is the seat that would have to change it. Sales never
  fixes any of these; sales only refuses to send past them.

---

## A. The skill library

| # | Claim | True today (2026-09-30) | Check |
|---|---|---|---|
| A1 | Six skills are live. | True. Six directories with a `SKILL.md`, all `status: active`. | `ls -d skills/*/ \| grep -v _validation` |
| A2 | Every skill carries a provenance block naming its claims and its papers. | True for all six. Claim counts run 12 to 30; paper counts 5 to 8. | `grep -A3 'provenance:' skills/*/SKILL.md` |
| A3 | Every skill carries a dated A/B result showing the skill changed the model's answer. | **FALSE.** One of six. `harness-engineering` has the 2026-09-12 trial; the other five have `validated: ""`. | `grep 'validated:' skills/*/SKILL.md` |
| A4 | The library's skills get picked correctly when they should be, and stay silent when they should not. | True, and measured: 40 of 43 cases, reliability 0.93, 95% confidence 0.81 to 0.99. Engine lexical/2.1, 8 decoys, policy pre-registered before the run. Dated 2026-09-29. | `tail -1 skills/_validation/results/2026-09-29-lexical-2.1.txt` |
| A5 | An independent reader used a skill on real work and it changed a decision. | True, once, dated 2026-09-29: one design decision changed, one procedure adopted, two confirmations, on a three-stage build plan. The reviewer recorded that its own baseline was not clean, because it had read the file four days earlier. | `head -16 skills/harness-engineering/reviews/2026-09-29-ursa-chair.md` |
| A6 | Twelve skills. | **FALSE and not scheduled to be true by launch.** Twelve by 2026-12-31 is a Q4 target graded at roughly 0.7 expectation, not a launch-day fact. | `docs/okrs/okrs-2026-Q4.md` O2 KR1 |

**The distinction A3 and A4 force, and the reason this section is first.**
There are two different receipts and they are not interchangeable. A4 says the
right skill gets picked. A3 says loading it changes what the model does. A4
holds for all six and is the newer, stronger, more unusual number. A3 holds
for one. Any sentence that lets a reader hear A3 while only A4 is true is the
launch's worst available mistake, because this audience checks.

The sendable form, therefore, names both and keeps them apart. Three sentences
that do that, drafted for reuse:

> Six skills are live, each one citing the claims and the papers it was taken
> out of. Yesterday's retrieval test put the library at forty of forty-three
> cases, which is the measure of whether the right file gets picked and the
> wrong one stays quiet. One of the six also carries a recorded trial showing
> that loading it changed what the model recommended, and the other five do
> not yet, which is the next thing to fix rather than the thing to talk around.

## B. The corpus and its numbers

| # | Claim | True today | Check |
|---|---|---|---|
| B1 | "N papers read this week." | **FALSE in the form the site prints it.** The number is what came in, not what was read in full. Reading taken 2026-09-26: 8,999 papers held, 4,243 arrived that week, 174 ever read in full, 55 read in full that week. | `docs/voice/home-metric-line-2026-09-26.md` |
| B2 | "N papers came in this week. M were read in full." | True, and it is the only permitted shape for a scale claim. Both numbers or neither. | canon law 15 |
| B3 | Findings are read out of the papers, and the library replaces a finding when newer work overturns it. | True as a description of the pipeline; the contradicts edges and the deprecated-claims view exist in the schema. | `db/schema.sql:265` |
| B4 | A public page shows what the research stopped supporting. | **FALSE today.** The view exists; the page does not. It is this sprint's item 5, assigned to the frontend seat. | `docs/sprints/sprint-2026-09-28.md` item 5 |

**The words, fixed by her ruling of 2026-09-25, so that following it is
copying rather than composing.** Papers *come in*, *arrive*, or *land*.
Papers are *sorted* or *ranked*. Only the full-read count may take the verb
*read*, and *read closely* or *read in full* is the phrasing. Findings are
*taken out of* the papers that were read. "Read or reviewed", "surveyed",
"processed" and "read at some depth" are the same false sentence in four
coats. Drop the claim rather than soften it.

**Still live on the home page at T-13.** `site/app/page.jsx` prints "papers
read this week" over the arriving count. The repair was drafted on 2026-09-26
and is still unset four days later. No sales draft may quote that line, and no
sales draft may point a stranger at the home page as a receipt for scale until
it is fixed. Whose call: frontend, from the writer's candidate.

## C. The archive

| # | Claim | True today | Check |
|---|---|---|---|
| C1 | There is a digest archive. | True, and thin: two issues, 2026-W37 and 2026-W39. | `ls site/content/issues/` |
| C2 | An issue every week, unbroken. | **FALSE.** W38 is absent from the archive. Any "every week" phrasing invites the reader to count, and the count is two files with a gap between them. | `ls site/content/issues/` |
| C3 | The digest is free and arrives in full. | True as the stated plan and priced that way on the page. Not yet purchasable: both plans read "Opens October 13". | `site/app/pricing/page.jsx` |
| C4 | The first issue a stranger reads is the pilot. | Her ruling of 2026-09-19 removed W37 from the site. W37 is still in `site/content/issues/`. Whether it renders is a frontend question this seat could not settle from the repo alone. | `site/app/library/` |

**C2 is the reason no pre-launch or launch draft claims a cadence.** Say what
is there. Two issues in the archive is a true sentence and a small one, and a
small true sentence costs less than a cadence claim a reader can disprove by
clicking twice.

## D. The business

| # | Claim | True today | Check |
|---|---|---|---|
| D1 | The digest is free, in full, with no paywall on the writing. | True, and decided at the first all-hands. | `docs/vision.md` §0 |
| D2 | Full access is $20 a month. | True. Sales never restates, discounts, or reframes this; pricing is the owner's and is argued for in market's positioning doc. | `docs/vision.md` §0 |
| D3 | Both are purchasable end to end on launch day with no manual steps. | **Not true yet, and it is the launch's committed result.** The pricing page shows two plans and a waitlist, and both plans say "Opens October 13". | O1 KR1 |
| D4 | You choose whether the subscription renews itself or stops each month until you say yes. | True as stated policy, and already on the pricing page in her words. It is a hard requirement on the payment implementation, not a marketing line. | `site/app/pricing/page.jsx` |
| D5 | You can put your email in and hear when it opens. | **True, and this is the biggest change since the drafts were written.** A real capture on the home page and the pricing page, writing to Postgres, and a duplicate submit is treated as success rather than an error. | `site/app/api/waitlist/route.js` |
| D6 | We have N subscribers. | **Unsendable in any form.** The list is comped friends. No count, no "hundreds of builders", no "our subscribers" phrased to sound larger. | `docs/roadmap.md` sprint 1 |

**D5 retires the single hardest constraint the campaign has carried.** The
2026-09-18 calendar forbade every pre-launch post from asking for anything,
because both home-page buttons dead-ended and there was nowhere for a
stranger to go. There is somewhere now. Pre-launch posts can carry one ask,
and the ask is the waitlist, described in the promise the page itself makes:
one email, on the day subscriptions open, and nothing before it.

## E. The organism

| # | Claim | True today | Check |
|---|---|---|---|
| E1 | Every decision is a public, dated entry, including the ones that did not work. | True. | `docs/decisions.md` |
| E2 | The org is mostly autonomous agents, each with a written charter, each opening its own pull request, and the owner merges. | True. Twelve charters in `prompts/`, and sixteen pull requests were open at once on the morning of 2026-09-30. | `ls prompts/`; `gh pr list --state open` |
| E3 | This post was drafted by an agent under a charter that forbids it from sending anything. | True, and checkable by a stranger in one click, because the charter is in the repo. | `prompts/sales-agent.md` |
| E4 | The org keeps a numbered public register of its own failures, written by the agents that caused them. | True, and it is the largest register in the repo by a wide margin. | `docs/agents/incidents.md` |

**E4 is an asset no draft has ever used.** See
`docs/sales/campaigns/obsolescence-report/` for what this run proposes doing
with it.

---

## The pre-send gate

Five commands. If any answer has moved, the draft is wrong until it is
edited, and a draft that has not been through this is not sendable.

```bash
ls -d skills/*/ | grep -v _validation | wc -l      # A1: is it still six
grep -c 'validated: ""' skills/*/SKILL.md          # A3: how many still have no trial
tail -1 skills/_validation/results/*.txt | tail -3 # A4: the newest retrieval score
ls site/content/issues/                            # C1, C2: what is actually in the archive
grep -n 'papers read' site/app/page.jsx            # B1: is the false verb still live
```

A sixth check has no command, and it is the one this run was nearly caught
by. Open `docs/voice/taste.md` and read from the bottom up to the date of the
draft you are about to send. A ruling dated after the draft was written
governs the draft, and the file's own law says the newest verdict wins even
when it reverses one she gave the day before.

## The register the drafts had already fallen behind

Recorded here because the drafts were two weeks stale against four rulings,
and a list of which ones is what the next run needs.

1. **2026-09-20, site copy round one.** Plain short sentences, a serious
   register, no cute asides, no diminutives, no colon-led constructions, and
   public copy sells the outcome rather than explaining the mechanism. This is
   also the company standard that binds every seat writing a public surface.
2. **2026-09-25, the reading verb.** Canon law 15, in section B above. It
   binds the site, the email, the masthead and any line drafted under the
   canon, which is every file in `docs/sales/launch/`.
3. **2026-09-25, tool pages.** Bare-noun headings, one plain sentence of
   intro, no personification, no slogans. "A graph that never forgets" was
   rejected as cheesy. Any draft that reaches for a slogan about the graph is
   reaching for a rejected line.
4. **2026-09-29, the rounds that landed.** Longer undecorated sentences, two
   to four of them per paragraph. No fragments, no staccato, no bold inside
   body copy. Sell from the builder's situation rather than from a definition.
   Headings are bare nouns. The compounding is stated and never borrowed from
   Moore or an S-curve.
5. **2026-09-30, the close.** Every issue and every email now closes
   "Accelerate every builder and agent to frontier speed." The old dual close
   is historical.

**Item 4 reverses item 1's first rule, and the newer one governs.** Her
2026-09-20 verdict asked for plain short sentences after reading choppy
subtitles; her 2026-09-29 verdict asked for longer undecorated sentences
after reading the next round, in her words, "all the subtitles are too
choppy. prefer longer undecorated sentences." The company standard carrying
the 2026-09-20 form is dated, and it says in its own text that the newest
verdict governs even against an approval from the day before, so following
2026-09-29 is the standard being obeyed rather than bent. The standard's own
copy is nine days behind her, and that is a finding for the relay rather than
a licence: see the run note in this pull request.

What did not change, and what the reversal is often misread as permitting:
serious register, no cute asides, no colon-led devices, sell the value rather
than the mechanism. Longer sentences, not more decorated ones.
