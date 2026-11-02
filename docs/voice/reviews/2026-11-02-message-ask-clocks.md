# Writer run 64, 2026-11-02 (message). Four violations of a rule that names its own specimen, and the gate that could stop them blocks on none

**The single biggest weakness, stated plainly.** `2026-W42` prints one kind of
block, thirty-five paragraphs of it, and the rule forbidding exactly that was
present in full in the generator that wrote it. So was the rule forbidding its
printed framework heading. So was the rule forbidding the four colon labels it
spends its prose on, with one of the four quoted in that generator by name as a
specimen already struck from an earlier edition. This is not an issue whose
generator lacks rules. It is an issue whose generator holds every rule it
breaks, which means no wording I add this run is the lever, and a fifth
sentence about labels would be the tinker run 51 drafted and reverted inside
one run on this exact ground.

## The generator's age, before a line is graded

| | |
|---|---|
| artifact | `2026-W42`, read live from `https://libraryofalexandria.dev` and un-rendered, at 2026-11-02T00:56Z |
| the generator the press runs | `prompts/digest.md` as of `9b6410ea`, 2026-10-14T20:08Z, **18.2 days old** |
| deployed image commit | `f16e2775`, deployed 2026-10-15T17:40Z, carrying the generator file unchanged from `9b6410ea` (`git diff 9b6410ea f16e2775 -- prompts/digest.md` is empty) |
| the digest's own record | recorded at 2026-10-19T09:01:21Z, so this edition was written by `9b6410ea` and every rule quoted below is quoted out of the file that wrote it |
| queued commits to the generator | **30**, of which two are a cancelling revert pair |
| read from | the public deploy receipt, by `check_voice.py press`, which is the job's own report rather than git's opinion of it (L-A16) |

`NEON_RO_URL` is unset in this run, so the stored row's `prompt_sha` and the
`deploy_runtime` query the canon's grading procedure names were both
unavailable. The receipt answered the same question from a surface that does
not need the credential, and the third integer the procedure asks for is the
one above. The limit is recorded rather than worked around: this grade did not
read the stored body, so it cannot say whether the row and the page differ.

## The ten laws, one verdict each, with the line that earns it

**Law 1, plain sentences, no em dashes, no semicolon joins. FAIL.** Two
semicolon joins, both the exact construction the law names, which is two
finished sentences in a balanced contrast.

> Llama-3.1-8B loads skills 72% of the time overall; Llama-3.3-70B loads them
> 11% of the time.

> A model leading MTEB at 75.7 scores 59.0 on SkillRet; a 7B model at 54.0 on
> MTEB scores 57.0 on SkillRet, below a 270M model at 64.6.

Em dashes 0, non-ASCII 0. `measure` and `marks` both read this, on the served
page, at `2026-W42.md:21` and `:27`. The generator's fifth count says "the
target is zero and there is no budget" and describes this construction in its
own words, in the file that wrote the issue.

**Law 2, no buzzwords, every line targeted and actionable. PASS.** The
pre-send gate's `empty-intensifier` findings on this issue are both false, for
a reason given under the findings below. Reading it myself I find no empty
line. "For builders, this means your embedding choice needs task-specific
validation, not leaderboard faith" is the law's own standard met.

**Law 3, sell the product, never the recipe. PASS.** The issue sells no
recipe of ours. The closest call is the close, and law 15 settles it.

**Law 4, the headline is a finding. PASS.** "Agent skill systems are
splitting between retrieval and self-evolution" is a finding a builder can
decide on from one line, and it is not a greeting.

**Law 5, relevance is impact, and every ranking says what earned each slot.
PASS, narrowly.** "The most concrete result this week comes from RSIGym" and
"Two papers this week converged on a finding that reshapes the retrieval
stack" each say what earned the slot. "Three results stand out" does not, but
the three sentences after it do the work.

**Law 6, evidence grades in-line. PASS on substance, and it is the issue's
best law.**

> The grade: one platform, one model family, five benchmarks, no replication
> outside the group yet.

Every item carries one. The SHAPE of that sentence fails law 7 and ban list
149 below, which is a different complaint from whether the grading happened.

**Law 7, honesty serves items and never the method. FAIL.** The grade above
is the method's own instrument named out loud in the reader's way. A reader
who meets "The grade:" in a paragraph has been handed the name of an
apparatus they did not know existed, at the position a sentence was owed.
Three more of the same kind, each opening a comma-run of steps: "The procedure
is extractable:", "The procedure is clean:", "The procedure runs:". The middle
word of three of the four is a payload field name, which the generator's
vocabulary rule forbids saying out loud. Filed as ban list 149 and this run's
one new entry.

**Law 8, links go to the full text. FAIL, and it is the most mechanical
failure on the page.** Ten arXiv links, nine of them to `abs`, and arXiv
serves `html` for seven of those nine.

```
FAIL    abs/2604.24594 and arxiv serves html/2604.24594
FAIL    abs/2606.03056 and arxiv serves html/2606.03056
FAIL    abs/2605.05726 and arxiv serves html/2605.05726
FAIL    abs/2604.01687 and arxiv serves html/2604.01687
FAIL    abs/2609.38981v1 and arxiv serves html/2609.38981v1
FAIL    abs/2610.22344 and arxiv serves html/2610.22344
FAIL    abs/2610.22322 and arxiv serves html/2610.22322
OK      abs/2609.37312v1, no html version, which is the rule's own fallback
OK      abs/2610.21055v1, no html version, which is the rule's own fallback
```

`check_voice.py links --live` reached arXiv for all nine, so the two passes are
the rule's own fallback working and not an unreached guess. The law is about
one less step between claim and evidence, and this edition charges the reader
that step seven times.

**Law 9, the fine-tuned instruction is the foundation. PASS.** Context
before finding: "If you run agents that fetch skills from a library, you are
choosing between two architectures that used to look like one" situates the
reader in the subfield and its stuck problem before any result arrives.
Attribution is institution-first throughout, with one exception graded under
the findings.

**Law 10, the dual-audience close. PASS.** "Accelerate every builder and
agent to frontier speed." present and verbatim.

**Law 11, length follows the news. PASS.** 1,552 words over ten papers, four
sections and a reading list. Nothing here reads padded and nothing reads
truncated.

**Law 12a, the outsider test and the density rule. FAIL.** The issue assumes
a vocabulary a smart builder outside the research world does not have, and it
assumes it in the places where the numbers live. Undefined at first use and
never after: `MTEB`, `rho=0.70`, `ALFWorld`, `SkillsBench`, `SWE-bench
Verified`, `GPQA Diamond`, `Terminal-Bench`, `LiteLLM`, `Harbor`, `WIRL`,
`LOAD_SKILL`, and "hierarchical SFT". The worst single line:

> MTEB Retrieval scores predict skill retrieval performance at only rho=0.70,
> with frequent ranking inversions.

That sentence carries the finding of a whole paper and a stranger cannot read
it. The generator's two hard tests per item say "no acronym or coined term
appears before the prose has unpacked it", and that rule is in `9b6410ea`.

**Law 12, framework names never print. FAIL, and the fix is already written.**

> ## What to read

The ban's own phrasing, printed as the reading list's whole heading. Canon law
12 and incident 20, the ruling she has given twice.

**Already patched and queued behind the deploy, so no prompt diff is written
for it.** `97de5c8b`, "Generator: law 12's slot ban names a sixth dress, and
one restatement pays for it", adds "what to read" to the ban's own quoted
list. The command this run asked is `python3 docs/voice/check_voice.py queued
12`, which returns:

```
OK      QUEUED: law 12 is named by 1 queued commit(s), so a fresh wording is
        the tinker the structure-watch step refuses
```

**And it is not itself reverted**, checked by diffing across the pair rather
than by trusting the count, which is the step the charter added after law 8's
named pair turned out to be net-empty. `97de5c8b`'s added lines are present at
HEAD and the only revert in the queued range is `0251df0b`, which reverts law
8's patch and not this one.

**Law 13, every issue stands alone. PASS.** `standalone --live` reports zero
sentences whose subject is "you" and whose verb is past. The opening is in the
present tense and about the reader's job: "If you run agents that fetch skills
from a library". Where a thread continues it is restated rather than pointed
at: "The field had held that sufficiently complex hidden computation
necessarily leaks an information-theoretic footprint into the CoT trace."
Nobody had to have been there.

**Law 14, the issue is enjoyable, and formatting is how it gets there. FAIL,
and this is the failing grade on its own.**

```
words 1552   paragraphs 35   longest 103  over100 1
shapes 1     links 2     paragraph 21
  one kind of block is a failing issue (canon law 14)
  no list and no written turn (canon law 14's two named devices)
```

One shape. No list, no line standing alone, no written turn, no third-level
heading, in an issue of thirty-five paragraphs with four sections. The law's
own words are that one kind is a failing issue whatever the word counts say,
and the paragraph counts here are good: the longest is 103 words and only one
clears 100. So this edition passes the measurable half of the law completely
and is the exact state she read and rejected, which is the thing law 14 says
about itself in the paragraph beginning "So the page count comes first".

The law also names the one honest fix, which is to find the material that is
genuinely parallel and set it as a list. **That material is on the page three
times and is already marked.** The three procedures are three comma-runs of
parallel steps, each announced by the word "procedure" and a colon. The issue
had its list, wrote it as prose, and then failed the shape count that the list
would have cleared.

**Law 15, the library never claims to have read what it only ingested.
PASS, and this is the law the issue gets exactly right.**

> 69 papers read in full this week, from 2,161 that arrived.

Both numbers together, "read in full" attached to the full-read count and
"arrived" to the ingestion count, which is the scale sentence this law
explicitly permits and the pair it asks for. The verb is the one the law
assigns. Nothing here softens anything.

The law's other half is red elsewhere and not on this page. `check_voice.py
reading` fails on four live site lines, `site/app/page.jsx:44`,
`site/app/terms/page.jsx:19` and `site/app/llms.txt/route.js` twice, and the
taste gate reports her verdict 6 as unheld because of them. Those are the four
rows already open in `docs/voice/awaiting-her-word.md` and they are a frontend
diff, not a generator patch.

**Law 16, a title the library has already used is not a title. PASS.** "Agent
skill systems are splitting between retrieval and self-evolution" is the same
finding as no earlier title in the archive, and a subscriber who saw
`2026-W40` would not think this is that issue again.

## The ban list, where this issue adds one and breaks two more

**Ban list 149, new this run, and it is four violations of a rule that names
its own specimen.** The four colon labels above, and the reason the entry exists
rather than a note under law 7: the heading gate collects "the text in front of
any colon, bolded or plain", puts the deciding question to it, and quotes "The
procedure is extractable:" BY NAME as a specimen struck from `2026-W39`. All
of that was in `9b6410ea`. The string printed again anyway, three times over
in new dress.

What the position buys is the finding. Every unit that gate defines is
anchored to a line, which is what "every line beginning with `#`" and "sitting
alone on its own line" and "BEGINS a line" each say. All four specimens sit
mid-paragraph after a full stop. A gate that runs over lines cannot be the gate
for a defect that lives inside them, and this one has now failed on the same
word twice, an edition apart.

`check_voice.py apparatus` is the enforcement and it is on this seat's own
surface. It fires four times on `2026-W42`, in the repository and live, and
zero times on `2026-W37`, `2026-W39` and `2026-W40`. Its nine asserted cases
include the four honest colons of the same edition, "This week the field drew a
hard line:" among them, because a detector that reddens those is a detector the
next run deletes.

**Ban list 103, the inbox preview sells a fragment. FAIL.**

```
inbox preview 122 chars
truncates at  'If you run agents that fetch skills from a library, you are choosing
               between two architect'
```

The first sentence of the opening is 122 characters, so what reaches an inbox
is the clause and not the thought. The rule is that the first sentence has to
survive the cut, and `2026-W40` fails identically at 128 characters, so this is
the second consecutive edition on it.

**Ban list 100, the artifact disagrees with itself about the version suffix.
FAIL.** Four of the ten identifiers carry `v1` and six do not, which means at
least one was composed rather than copied out of the payload.

**Ban list 145, the phrase reporting the absence. FAIL, and already patched.**

> New work from a team at an unnamed institution shows that under plausible
> cryptographic assumptions, even a one-layer Transformer can encrypt its
> reasoning online.

"a team at an unnamed institution" is one of the four phrasings entry 145
quotes. **No prompt diff**, because the rule naming that exact phrase is
`6bb1c8a9`, "Generator: the fell-behind section gets a third test, and it is
where the claim came from", which is queued and not in `9b6410ea`. Verified
present at HEAD and absent from the deployed file by grepping both. The
command asked was `check_voice.py queued`, whose law table lists `6bb1c8a9`
under law 6's span, which is why this one is reported under the ban list rather
than under a law verdict.

## The patch, and why it is empty

Step 3 asks for the smallest prompt change that would have prevented each
failed grade. This run writes **no prompt diff at all**, and the four failures
divide cleanly into the two reasons the charter already states.

**Already merged and queued behind the deploy, reported with the commit and no
diff.** Law 12 (`97de5c8b`), ban list 145 (`6bb1c8a9`), and law 14's list half
(`2c6ce635`, which adds the block naming all three procedure specimens
verbatim and is absent from `9b6410ea`). Three of the three are present at
HEAD and none is reverted.

**Stated in the generator that wrote the issue, in its most explicit available
form, so a new wording is the structure-watch refusal.** Law 1's semicolon
count, law 8's bolded and worked link rule, law 12a's acronym test, law 14's
shape count with "one kind is a failing issue" at line 1621 of the deployed
file, and the heading gate's fragment collection with its own quoted specimen.
Every one of those was in `9b6410ea` and every one printed through.

Run 51 reached this conclusion five hours before it reverted its own law 8
patch, and wrote the sentence this run has nothing to add to: "A run that
argues wording is not the lever and then adds a fourth wording has graded
itself more kindly than it graded the generator."

## Structure watch, which is where the work actually goes

The same structural fix has now failed more than twice through prompt changes
alone, so step 4 applies and the proposal is in `docs/ideas.md` under this
run's date rather than in the prompt. Two parts.

**The pre-send gate blocks on none of the three laws this edition breaks.**
`tools/check_digest_quality.py` is the one machine that can stop a send. Run
against this issue it returns `0 blocking, 4 warnings`. Its own docstring
reserves `block` for "defects that are unambiguous from the text alone, that
the owner has already had to report, or that make the issue wrong rather than
weak". The printed framework heading is a defect the owner has reported twice.
The one-shape page is a count of kinds of block. The `abs` link where arXiv
serves `html` is one HTTP request. All three meet that bar in its own words,
and all three are already computed on this seat's surface by `slotheads`,
`measure` and `links`. `tools/` is pipeline code and not this seat's to write,
which is why this is a ledger proposal and not a diff.

**And all four warnings it did return on this issue are false.** Two are
`bare-number` on figures that have a comparison in the same sentence. The other
two are `empty-intensifier`, and they are the clearer defect: `INTENSIFIERS`
holds `"very "` with a trailing space and no leading one, and the test at line
224 is `if word in low` where its neighbour at 218 is `\bword\b`. So the string
"every " matches, and one of the two hits is the standing close that canon law
10 requires in every issue the product will ever send. The gate's only two
warning classes on this edition are a false positive guaranteed by a law, and
noise in the instrument that reads an issue last is how a real finding gets
read past.

## One finding about this seat's own instrument, found by being failed by it

`check_voice.py candidates` failed this review three times, for drafting copy
for `site/app/page.jsx`, `site/app/terms/page.jsx` and
`site/app/llms.txt/route.js`. This review drafts nothing. It quotes those three
lines because law 15's verdict is that the issue gets the law right and the
four red lines are elsewhere, and a grade cannot say that without naming them.

The gate already holds the argument against its own behaviour. `is_candidate`
exists, it correctly answers no for anything under `docs/voice/reviews/`, and
the docstring's reason is that "a review cites surfaces as evidence and failing
a grade for quoting the line it grades would make the gate unusable by the work
it governs". That guard was applied to the floor half of the pass and not to
the clash half, so the half with the written reasoning was protected and the
half without it was not.

Fixed in this run by giving the clash test the floor's scope, and the scope it
read is now printed, because zero candidates and zero added files mean
different things. Proved both ways rather than asserted: a probe candidate
drafting for `site/app/pricing/page.jsx` and naming no open candidate still
fails on both halves, and the two reviews in this diff no longer fail at all.

This is the register-width class a fourth time and the first instance where the
width is too great rather than too small. The three before it were gates that
could not see a surface. This one saw a surface it had no business reading, and
the cost is the same in the end: a gate that reddens a grade is a gate the next
run learns to read past.

## Checks

| | |
|---|---|
| `check_voice.py press` | `BEHIND`: the press runs the generator as of `9b6410ea`, 18.2 days old, 30 commits queued |
| `check_voice.py queued 12` | `OK QUEUED`, law 12 named by `97de5c8b`, and the pair diffed for a revert |
| `check_voice.py apparatus --live` | 9 detector cases pass, 4 FAIL on `2026-W42`, 0 on `2026-W39` and `2026-W40` |
| `check_voice.py deadlines` | 2 rows, 2 readable clocks, 2 named asks, none expired, against 2 `unasked` an hour earlier |
| `check_voice.py enforcements` | entry 149's three anchors all resolve |
| `check_voice.py all --live` | run, and every figure in this review is quoted under the path it was measured on |
| `tools/check_digest_quality.py` | `0 blocking, 4 warnings`, all four false, which is the finding above |
| conflict markers | none in `docs/`, `prompts/`, `README.md` |

## What this run did not do

It did not grade the stored `digests` row, because `NEON_RO_URL` is unset, so
it cannot say whether the row and the served page differ.

It did not touch `prompts/digest.md`. That is the charter's step 3 executed
rather than skipped, and the argument is above.

It did not answer either question now carrying a clock in
`docs/voice/awaiting-her-word.md`. Both run to 2026-11-04T00:32Z and resolving
a reservation on silence is the PM's to apply under the company standard. What
this seat owes that morning is the reading.
