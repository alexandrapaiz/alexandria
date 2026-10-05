# The claim ledger — every sendable sentence, and what makes it true today

First verified 2026-09-30 (T-13). **Re-verified 2026-10-05 (T-8), and the
re-verification is the next section.** Re-verify before any send; the
right-hand column is a reading, not a constant, and two of its 2026-09-30
readings turned out to be wrong in the direction that costs us.

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

## The re-verification, 2026-10-05 (T-8)

Every command in the pre-send gate at the bottom of this file was run between
03:00 and 03:30 UTC on 2026-10-05. **Not one reading moved.** That is the
finding, and it is a larger one than any individual row.

| Row | 2026-09-30 | 2026-10-05 | Moved |
|---|---|---|---|
| A1 six skills | six | six | no |
| A3 one skill has a trial | one of six | one of six | no |
| A4 newest retrieval score | 2026-09-29, 40 of 43 | still 2026-09-29, no newer file | no |
| A6 twelve skills | false | false | no |
| B1 the false reading verb on the home page | live, 4 days old | live, 9 days old | no |
| C1 issues in the archive | stated as two | **one serves. The ledger was wrong** | corrected below |
| C2 a gap in the weekly run | W38 missing | W38 and W40 missing | worse |
| D3 purchasable end to end | "not true yet" | **not started, and nothing in flight starts it** | corrected below |
| D5 the waitlist works | true | true | no |

The reason nothing moved has nothing to do with the seats. `main` took two
commits in those five days, both of them the same vendored standards sync, while
the open pull request count went from 16 on 2026-09-30 to 64 on 2026-10-05. The
work exists and it is not in `main`, and a sales draft cites what a stranger can
open. `launch-gate.md` is the file that works out what that costs, sentence by
sentence, and it is the document to read beside this one from now on.

```bash
git log --oneline --since=2026-09-30 main | wc -l                     # 2
gh pr list --state open --limit 200 --json number -q 'length'         # 64
```

**Two corrections this seat owes, both of them overstatements, which is the
direction that matters.**

**C1 was wrong. The archive serves one issue, not two.** `site/lib/content.js`
line 23 holds `HIDDEN_WEEKS = new Set(["2026-W37"])`, retiring the pilot on her
order of 2026-09-19 so the next issue would be the first a stranger reads. The
order was carried out in code. The ledger counted files with `ls` and never
read the module that decides what is served, so C4's open question — whether
W37 renders — was answerable in one grep on 2026-09-30 and was left open
instead. Five drafts said two issues. All five are fixed in this pull request.

The general form of the mistake, worth more than the fix: **a claim about what
a reader sees is never settled by listing files.** It is settled by reading the
code that chooses which files are served. `ls` answers a question about the
repository and every sendable sentence is a question about the site.

**D3 was understated.** "Not true yet" reads as late. The reading at T-8 is
that it has not been started and that no open pull request starts it: no
payment integration in the tree, `currentEmail()` returning null by
construction so `hasSpine()` can never be true, and both pricing pills still
reading "Opens October 13". Full evidence in `launch-gate.md` §1. This is the
difference between a date slipping and a committed KR having no work behind it,
and the copy consequence is six drafts rather than one.

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
| A7 | You can follow any recommendation in a skill back to the work it came from. | **Half true, and the half that is false is the half the drafts leaned on.** The papers are listed with arXiv links, which open. The claim numbers are integers that appear nowhere else in the file and resolve only on `/graph`, which is a paid page with no preview by her ruling of 2026-09-19. A non-subscriber cannot open a single claim. | `grep -A2 'claims:' skills/harness-engineering/SKILL.md`; `site/app/graph/page.jsx` |
| A8 | 69 percent of 216 public Claude Code skills will not reliably trigger. | True as a sourced third-party finding, not ours: a Show HN report of 2026-09-17, item 49744398, recorded by the market seat on 2026-09-18. | `docs/market/opportunities-2026-09-18.md` |

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

**A7 is the correction this run had to make to its own new copy.** Three
rewritten drafts said a reader could follow a recommendation back to the work it
came from, which is the sentence the whole evidence pitch rests on, and it was
written before anyone checked what a claim number resolves to. It resolves to
nothing a stranger can reach. The drafts now lean on the paper links, which do
open, and the Hacker News draft says outright that the claim numbers are
internal and only resolve on a paid page, because on that venue naming the
limit is worth more than the claim it costs.

The fix that would make A7 true is not a copy fix. Either a claim gets a public
permalink, or the skill file states its claims in words beside their numbers.
Both are outside this seat. Filed in the ledger in this pull request.

**A8 is the strongest comparative sentence the company owns, and it is one bad
sentence away from being its worst.** Their audit says 69 percent of public
skills will not reliably trigger. Our test says 40 of 43. Those measure the same
axis and they do not share an instrument, we do not know their method, and a
post that puts the two numbers side by side without saying so has claimed a head
to head that nobody ran. Every draft that uses both now states that they are
different instruments in the same breath, which is also, on this audience, the
most persuasive thing in the post.

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
| C1 | There is a digest archive. | **Corrected 2026-10-05: one issue serves, 2026-W39.** Two files are on disk and `site/lib/content.js:23` hides 2026-W37 on her order of 2026-09-19. The 2026-09-30 reading said two and was taken with `ls`. | `ls site/content/issues/`; `grep -n HIDDEN_WEEKS site/lib/content.js` |
| C2 | An issue every week, unbroken. | **FALSE.** W38 is absent from the archive. Any "every week" phrasing invites the reader to count, and the count is two files with a gap between them. | `ls site/content/issues/` |
| C3 | The digest is free and arrives in full. | True as the stated plan and priced that way on the page. Not yet purchasable: both plans read "Opens October 13". | `site/app/pricing/page.jsx` |
| C4 | The first issue a stranger reads is the pilot. | **Settled 2026-10-05: it does not render.** `site/lib/content.js:23` excludes 2026-W37 from the index and from every path the library serves. The question was answerable from the repo on 2026-09-30 and this seat recorded it as unanswerable instead. | `grep -n HIDDEN_WEEKS site/lib/content.js` |

**C2 is the reason no pre-launch or launch draft claims a cadence.** Say what
is there. Two issues in the archive is a true sentence and a small one, and a
small true sentence costs less than a cadence claim a reader can disprove by
clicking twice.

## D. The business

| # | Claim | True today | Check |
|---|---|---|---|
| D1 | The digest is free, in full, with no paywall on the writing. | True, and decided at the first all-hands. | `docs/vision.md` §0 |
| D2 | Full access is $20 a month. | True. Sales never restates, discounts, or reframes this; pricing is the owner's and is argued for in market's positioning doc. | `docs/vision.md` §0 |
| D3 | Both are purchasable end to end on launch day with no manual steps. | **Reading hardened 2026-10-05: not started, and no open pull request starts it.** No payment integration exists (`polar` appears four times in the tree, all comments and legal pages). `site/lib/entitlement.js` has `currentEmail()` returning null by construction, so `hasSpine()` can never be true for anyone. Both pricing pills still read "Opens October 13". Zero of 64 open pull requests touch pricing, checkout, Polar or entitlement. | `launch-gate.md` §1; O1 KR1 |
| D4 | You choose whether the subscription renews itself or stops each month until you say yes. | True as stated policy, and already on the pricing page in her words. It is a hard requirement on the payment implementation, not a marketing line. | `site/app/pricing/page.jsx` |
| D5 | You can put your email in and hear when it opens. | **True, and this is the biggest change since the drafts were written.** A real capture on the home page and the pricing page, writing to Postgres, and a duplicate submit is treated as success rather than an error. | `site/app/api/waitlist/route.js` |
| D6 | We have N subscribers. | **Unsendable in any form.** The list is comped friends. No count, no "hundreds of builders", no "our subscribers" phrased to sound larger. | `docs/roadmap.md` sprint 1 |
| D7 | You can make an account. | **New since 2026-09-30, and sendable with one qualifier.** `@clerk/nextjs` runs in `site/middleware.js`, `/sign-in` and `/sign-up` are routes in the tree, `/api/clerk-webhook` verifies Clerk's signature and writes users into Neon, and ADR-34 makes Neon the system of record. What this seat cannot confirm from the repository is that it serves in production, which is L-A16, so no draft says "sign up today" until someone has signed up. | `ls site/app/sign-up`; `cat site/app/api/clerk-webhook/route.js` |
| D8 | An account gets you anything. | **False, and it is the gap people will find.** An account can be created and entitlement is hard-wired shut, so a signed-in user and a stranger see exactly the same site. No draft invites a reader to create an account, because an account that does nothing is worse than no account. | `cat site/lib/entitlement.js` |

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
| E2 | The org is mostly autonomous agents, each with a written charter, each opening its own pull request, and the owner merges. | True, and the number moved hard. Twelve seat charters in `prompts/` (`*-agent.md`; the other six files are pipeline prompts, so "eighteen charters" is the wrong count). Sixteen pull requests were open on 2026-09-30 and **64 on the morning of 2026-10-05, twenty of them drafts she cannot merge**. Any draft quoting the queue number states what it means in the same breath, per `launch-gate.md` §5. | `ls prompts/*-agent.md \| wc -l`; `gh pr list --state open --limit 200 --json number -q 'length'` |
| E3 | This post was drafted by an agent under a charter that forbids it from sending anything. | True, and checkable by a stranger in one click, because the charter is in the repo. | `prompts/sales-agent.md` |
| E4 | The org keeps a numbered public register of its own failures, written by the agents that caused them. | True, and the precise form is better than the summary. Eighty entries over 6,211 lines. Fifty-four use a date-and-subject identifier. Twenty-six are numbered and those twenty-six numbers resolve to fourteen distinct ones, because incidents 24, 25 and 26 each exist three times and 27 through 31 twice each. The collision has its own entry, written by the seat that caused it. | `grep -cE '^## INC-' docs/agents/incidents.md`; `grep -oE '^## Incident [0-9]+' docs/agents/incidents.md \| sort -u \| wc -l` |
| E5 | The register is complete, or can say which of its incidents are open. | **False, and saying so is the strongest line available.** The generated company-wide view reports 57 entries carrying no status marker, so the register cannot report its own open count. Recorded as company lesson L-A28 rather than fixed. | `docs/standards/lessons.md` L-A28 |

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
ls -t skills/_validation/results/*.txt | head -1   # A4: the newest retrieval score's date
ls site/content/issues/                            # C1, C2: what files exist
grep -n HIDDEN_WEEKS site/lib/content.js           # C1, C4: which of them actually serve
grep -n 'papers read' site/app/page.jsx            # B1: is the false verb still live
git grep -li polar -- site db pipeline tools       # D3: is there a payment path yet
grep -n 'return null' site/lib/entitlement.js      # D3: can hasSpine() ever be true
```

**Three of those eight were added on 2026-10-05 and two of them exist because
the gate passed while the claim was false.** The `HIDDEN_WEEKS` line is there
because `ls site/content/issues/` answered a question about the repository when
the claim was about the site, and the gate reported a pass on a row that was
wrong by one issue. The two D3 lines are there because the old gate had no
command for the claim the entire launch rests on. A gate that cannot see the
most expensive sentence in the directory is L-A21's first half, and this one
could not.

A sixth check is the one this run was nearly caught by, and it does have a
command. Every file in `docs/sales/launch/` declares the date it was written
under on its second line. Compare that against the newest dated ruling in the
taste register, and anything older is stale until a run says otherwise.

```bash
newest=$(grep -oE '^- 20[0-9]{2}-[0-9]{2}-[0-9]{2}' docs/voice/taste.md \
  | grep -oE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' | sort | tail -1)
for f in docs/sales/launch/*.md; do
  d=$(grep -m1 -oE '(Rewritten|Verified) 20[0-9]{2}-[0-9]{2}-[0-9]{2}' "$f" \
    | grep -oE '20[0-9]{2}-[0-9]{2}-[0-9]{2}')
  if [ -z "$d" ] || [ "$d" \< "$newest" ]; then echo "STALE: $f"; fi
done
```

Run both ways on 2026-09-30. All seven current drafts pass. The 2026-09-18
version of `email.md`, taken from main, is reported stale, which is the file
whose staleness this gate exists because of. A gate that has only been shown to
pass has not been shown to work.

Then read the register anyway. The command compares dates and cannot tell you
whether a draft obeys a ruling, only whether anyone has looked since it landed.
The file's own law is that the newest verdict governs even when it reverses one
she gave the day before, and no timestamp settles that.

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
