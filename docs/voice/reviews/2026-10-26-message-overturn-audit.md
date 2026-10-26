# The one section the product is sold on was graded sixteen ways and never against a paper

**Writer run 57, 2026-10-26, message.** The PM's handoff of 19:31Z: the live
`2026-W42`'s overturn section is wrong three for three, and pulling it or
correcting it is this seat's call. The writer lane's Backlog, This sprint and In
progress columns are all empty, so the handoff is the item.

## The biggest weakness, stated plainly

It is not in the issue. It is in this seat's instrument.

Writer run 51 graded `2026-W42` nine hours before this run, against all sixteen
canon laws and all six grading passes. That grade is thorough, its figures
re-measured clean here, and it found four real defects inside the overturn
section. Nine hours later the research seat read the same section against the
two abstracts it cites and scored it **three wrong out of three**.

Both readings are correct. The grade asked how the section was written and the
audit asked whether it was true, and the procedure has a pass whose stated job
is the second one. That pass has six questions. Two numbers against each other.
A number against its own sentence. A claim about alexandria's own counts. A
verdict against the half of the sentence it read. **Not one of them opens a
paper.** The pass that exists to ask whether the issue is true has never once
checked a statement against the source the issue cites, and the section where
that is the entire product has run unchecked for three editions.

So this run did not re-grade the issue. Run 51's verdicts stand, they are on
`main`, and a fourth reading of the same text would produce patches already
merged. What follows is the one thing that grade could not reach and the repairs
that follow from it.

## No fresh grade of a fresh edition, and the reason is a missed send

`python3 tools/delivery_health.py --surface press --no-notify` reads FAILING:
"the newest issue is 2026-W42 and 2026-W43 has ended; 1 issue(s) missing". The
live archive serves three editions, `2026-W42`, `2026-W40` and `2026-W39`, so
`2026-W41` is missing as well and the record holds three issues over five weeks.

The Monday slot of today passed with nothing printed. `press.newest_week` is
still `2026-W42` created 2026-10-19T09:02:52Z, read at 19:58Z today, and the
`weekly` row in `deploy_runtime` carries `recorded_at` equal to its own
`first_seen_at` at 2026-10-19T09:01:21Z, where every other app's `recorded_at`
has advanced. One row that never moved is a job that has run once. The cause is
the engineer's and it is recorded: the Modal workspace has been off since
2026-10-23 (`docs/agents/engineer-run-note-2026-10-25-message.md`). Nothing is
filed here.

**Two of the three generator shas are unreadable this run, and that is the
honest report rather than a skipped step.** `NEON_RO_URL` is unset in this
runtime, so the `prompt_sha` the stored body carries cannot be read, and the
`weekly` `runtime_sha` the receipt publishes is `2e313065f5c7`, a bundle hash
over five files rather than a git commit, so it resolves to no revision here.
What is readable is the third integer and the gap it implies: `prompts/digest.md`
on this branch hashes to `c302e23c3f3b`, and **eight commits have touched it
since `2026-W42` was written**, the newest of them this morning. Every verdict
about the generator below is a verdict about a file the press has not read.

## The seventh question, and what it answers that six could not

For every belief the issue says fell, name the paper that overturned it and the
paper that held it, and read both abstracts. Three answers end the item. The
audit found all three in one section.

- **The two papers are one paper.** Vosti is reported as contradicted by Vosti,
  and the two halves are that paper's own findings about two different systems:
  bitwise identity is Vosti's result and the shortfall is vLLM's and SGLang's.
- **The overturned belief is the citing paper's own proven result.** "This
  directly contradicts the earlier claim that task complexity above a model-size
  threshold forces near-linear information leakage." That is the theorem of
  `arxiv:2609.37312`, the paper the sentence cites. The issue's own prose
  carries the refutation three sentences earlier, as something this paper
  showed.
- **A figure in neither abstract.** "Omitting tenant-salt provenance enables 93%
  prompt identification from timing side-channels", attributed to "the same
  paper", which is a theory paper on chain-of-thought encryption containing
  neither the mechanism nor the number.

The third is the worst and it is worth separating from the other two. A
mislabelled edge misleads the reader who follows the link. A figure under the
wrong paper gives them nowhere to follow at all.

A fourth defect sits in the same section and run 51 found it: "New work from a
team at an unnamed institution shows that". That is the attribution rule's third
form executed as a phrase. No paper has an unnamed institution, so the sentence
describes the payload and prints it as a property of the research.

## The patches, and which law each serves

**`prompts/digest.md`, the fell-behind slot: a third test.** The slot has
carried STRENGTH and KIND, and both compare the two claims to each other, so a
pairing in which one paper stands against itself passes both of them perfectly.
SOURCE asks where each half came from. It completes a lookup the file already
orders two rules down for the link: a `deprecated` row carries the old paper's
title and url, the link rule sends the model to find the contradicting work at
the front of a `new_claims` string, and nothing told it to compare the two.
Serves canon laws 6 and 7 through the claims pass, and law 15's principle
applied outward: a claim with no checkable link is one the reader either trusts
or stops trusting the issue over.

**`prompts/digest.md`, the attribution gate: the dress that looks like
compliance.** The third form has one correct execution and it is a sentence with
no attributive clause at all. Serves canon law 9.

**`docs/voice/canon.md`: the claims pass's seventh question**, with the
measurement that produced it and the one honest failure mode, which is that the
abstracts may be unreachable and then the section is ungraded on provenance
rather than scored on its prose.

**`docs/voice/check_voice.py provenance`: the half a command can hold.** Two of
the three dresses leave their evidence inside the sentence and those two are
gated. On the served editions:

```
python3 -I docs/voice/check_voice.py provenance --live
  the detector's own cases   5 pass
  2026-W39  0 finding(s)
  2026-W40  0 finding(s)
  2026-W42  2 finding(s)
    FAIL  line 47: points back at the work it overturns
    FAIL  line 49: the work that held it is a work this section links (vosti)
  exit 1
```

Clean on two editions and failing on the one the audit named, which is the
evidence that it reads the defect rather than ordinary prose. Its own output
says a clean exit is not a verdict on the section, because the figure under the
wrong paper needs the abstract and no command in this repository will hold it.

**Ban list 145**, three enforcement anchors, all verified by
`check_voice.py enforcements`. Swept per entry 90: the generator writes the
backreference phrase nowhere outside the bullet that bans it, and the gate is
clean on both committed editions and on `2026-W40` served, so the count is two
and both are the section the audit named.

## The generator's weight, and this run could not pay

```
python3 pipeline/budget.py
  before  prompts/digest.md 33,947 tokens   $0.1475 an issue
  after   prompts/digest.md 34,720 tokens   $0.1482 an issue
  tests/test_press_resilience.py   26 passed
```

**+773 tokens, and nothing was removed to pay for them.** The canon's rule is
that a run adding tokens removes at least as many, and where it genuinely
cannot it says so with the measured number instead of spending the margin
silently. This is that case and here is the search that justifies it. An
eight-word shingle scan across the whole file found exactly one removable
repetition, which is the sentence "The slot's internal name is not repeated here
and is not a candidate" standing at three of the four heading slots. It is the
taste gate's enforcement anchor for her ruling of 2026-09-19 given twice, the
anchor needs one copy and two are therefore free, and they are **not** taken,
because each copy sits at the writing position of a different heading and
incident 20 is the owner giving that same ruling a second time. Sixty tokens is
not worth reopening the one defect she has had to rule on twice. Everything else
the scan surfaced is an operative clause or a disambiguation, which the canon
says never go.

The addition was compressed twice before this number was accepted, from 1,062
tokens to 773, by striking the argument for the rule and keeping the rule.

## Pass 2, the taste gate, and its one red row is not this run's

`check_voice.py taste` reports one FAIL on this branch and it is inherited:
`reading` is red, so her ruling of 2026-09-29 that "read" never stands for
ingested is not held. The four live hits are on the site, at
`site/app/page.jsx:44`, `site/app/terms/page.jsx:19` and two in
`site/app/llms.txt/route.js`. That is the frontend seat's surface, the repair
has been drafted since 2026-09-26 in `docs/voice/home-metric-line-2026-09-26.md`,
and it is the quality claims register's "N papers read this week" row. Confirmed
in place, not restated, and not touched here. Every other ruling the gate can
hold is held.

## Pass 6, the standing defects, confirmed in place and not restated

- **`MASTHEAD` in `pipeline/weekly.py` still recites the framework slots** in
  plain-English synonyms, on line 3 of every issue the press sends, including
  the one under review. Twenty-three days open, the engineer's,
  `INC-2026-10-03-law-12-graded-by-grep`. Confirmed with today's evidence: the
  un-rendered live `2026-W42` carries it at line 3 verbatim.
- **`site/content/issues/2026-W39.md` still opens on canon law 13's own
  rejected specimen**, "You have spent the week watching agents get faster by
  thinking less at test time", and it is live at
  `https://libraryofalexandria.dev/library/2026-W39` today, fetched this run.
  `check_voice.py standalone` fails on it and the open question in that gate's
  own docstring is already filed. Not re-filed. It earns one new sentence
  below, because its mechanism is the mechanism this run's correction depends
  on.

## The W42 ruling: pulled, not corrected

The decision and the exact words are `docs/voice/w42-correction-2026-10-26.md`,
with the corrected body at `docs/voice/corrections/2026-W42-corrected.md`. The
reasoning in one paragraph, because the middle option is the trap.

There is no overturn to correct this into. The honest version of that material
is two good new results, and both belong in the new-work section of an issue
already sent. A subscriber received the section on 2026-10-19 and the email
cannot be recalled, so the archive is the only correctable surface, and the
correct archive is a **subset of what was sent rather than a rewrite of it**.
Removing a false section leaves every sentence a subscriber read standing and
true. Writing corrected prose in would put paragraphs on the page that no
subscriber ever received, under the same title, which is law 16's defect
reversed.

Four edits, not one block: the section at lines 43 to 53, the lead's third
sentence which carries the same false claim where the reader meets it first, the
lead's count from three to two, and the masthead's third clause on this page
only. The close's "These three papers" was checked rather than assumed and
survives: its three are the retrieval group, the self-evolution group and the
budget platform, none of them the hidden-reasoning paper.

**Why this route works with the workspace off, which is the part worth
carrying.** `site/lib/issues-core.js` `pickIssue` returns the committed file
ahead of the `digests` row, and `mergeIssues` lets files override rows in the
listing too. So a corrected `site/content/issues/2026-W42.md` serves to every
reader with no database credential and no Modal. And the inverse of that
mechanism is exactly why `2026-W39` still carries her struck sentence: that
correction was applied downstream of the record and lost when the file was
replaced with what the press sent. A correction written into the file is the
durable half.

**The two semicolons in the corrected body stand, and this is the line that
says why.** `check_voice.py selfcheck` reports them at lines 21 and 27 of
`docs/voice/corrections/2026-W42-corrected.md`. They are canon law 1 failures,
they are in the retrieval section which the audit did not touch, and a
subscriber received them. This edit removes something false; it does not
retroactively restyle true prose, because that makes the archive diverge from
the send for no honesty reason. Law 1 is held by the generator and the pre-send
gate, which is where run 54 correctly refused a fourth wording of it this
morning.

## One line needs her word, and it carries a recommendation

A correction notice under the masthead on that page only, recommended and quoted
in full in the candidate file. No ruling covers it: her 2026-09-19 ban is on an
issue narrating its own methodology, and this sentence says what happened to one
page in the past tense and claims no mechanism, which is the line the quality
claims register asks every claim to stand on. Under the company standard's §22
it proceeds as recommended after forty-eight hours of her silence. It moves no
authority and no money.

## Three findings for the quality claims register, named and not resolved

The register is the ExO seat's and this seat is its artifact-side gate, so these
are reported by name per the charter's step 1b.

1. **The masthead's "what newer evidence has overturned" has no row at all.** It
   is a claim about our artifact on every issue ever sent, a reader can ask how
   we know it, and it is now measured at three wrong out of three on the newest
   edition. A claim with no row is the finding.
2. **The row "replaced when newer work overturns it" needs a worse state than it
   has.** It reads "reports, does not replace", and the mechanism it names is
   `pipeline/weekly.py` computing `deprecated` from `contradicts` edges. What it
   reported on the newest issue was wrong three for three, so the row currently
   credits the claim with a reporting function that the artifact does not
   support.
3. **The row "Each week the library becomes an issue" moved today.** Its own
   last reading says the 2026-10-26 slot is the thing to read first. Read at
   19:58Z: the slot passed, `press.newest_week` is still `2026-W42` at 7.45
   days, and the clock has now missed.

## Routed to the engineer, with the entries named

Filed rather than worded a third time, under the charter's structure-watch step.
The new entry is `docs/ideas.md`, **2026-10-26 - Every same-paper contradiction
written before 2026-10-25 is outside the only repair the pipeline has**. It
stands on the research seat's four-step finding: the rejudge queue keys on
`prompt_sha`, the same-paper exclusion is shortlist SQL and moves no sha, both
paths pass the judged claim's own `paper_id`, and `latest_links` repairs an edge
only through a later row for the same pair. Its first step is a count rather
than a migration, because the count decides whether the fix is a one-off
withdrawal pass or a `retracted_at` column.

The prevention half is already filed and already shipped and is not re-filed:
**2026-09-19 — The interpret neighbour query has no paper boundary**, whose
proposed one-line fix the engineer shipped on 2026-10-25 as `5af27966`,
undeployed.

## This run's own prose, measured over the branch

```
python3 -I docs/voice/check_voice.py selfcheck origin/main
  added lines read from   origin/main
  docs/voice/check_voice.py                     semicolon 4   (code, excused)
  docs/voice/corrections/2026-W42-corrected.md  semicolon 2   (stands, see above)
  2 line(s) carry a mark this file cannot excuse
```

Taken over the whole branch against `origin/main`, with every file staged first,
because an unstaged file this run created is invisible to `git diff` and that is
ban list 144's third finding. The two findings are the published sentences this
run deliberately did not restyle, and the paragraph above is the one line the
gate asks for. Zero in anything this run wrote itself.
