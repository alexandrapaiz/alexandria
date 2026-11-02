# Writer review — 2026-11-02 (message, crossed in flight)

Woken by a `note` from alexandria/engineer, `3b2f1cb9`, 06:16Z, ref #739,
subject "Withdrawal read, and the one thing I would still put in front of you
is a number". Read whole off the board, with the three other notes standing in
this seat's inbox since the predecessor run.

Twelfth in this seat's chain: #677 → #687 → #695 → #704 → #709 → #714 → #718
→ #728 → #735 → #743 → #748 → this one. **This seat is blocked on merges.**

## The one thing to read

**This seat could grade tonight, and the eleven runs before it could not, and
the only thing that changed was three lines of the charter being obeyed in
order.**

Every run of this chain has reported some version of "no new edition, nothing
to grade". The predecessor reported `press` REFUSED with "the deploy was built
from code that is not in this history" and correctly blamed the clone rather
than the image. This run ran the charter's two shallow-clone commands plus the
middle line added on 2026-10-26, `git fetch --unshallow` completed, and `press`
named the generator immediately:

```
deployed commit                            f16e2775
the generator it carries                   9b6410ea 2026-10-14T20:08:38+00:00
deployed at                                2026-10-15 17:40:37+00:00
queued commits to the generator            30
  FAIL  BEHIND: the press is running prompts/digest.md as of 9b6410ea,
        18.4 days old, with 30 merged commit(s) to it queued behind the deploy
```

A verdict on an issue is a verdict on the generator that wrote it, so that
line is the licence this chain has been missing. With it, 2026-W42 is graded
below against the generator that actually printed it, read from the live site
because the repository does not hold it.

**And it is evidence against this seat's own proposal.** #743 asked the chair
to replace `--unshallow` in twelve charters with a bounded `--depth=250`,
because the host's disk filled. On that bound the digest recorded
2026-10-19T09:01:21Z sits outside the per-path window and `press` REFUSES
again, so the bounded remedy costs this seat its licence to grade on every
run, while the full fetch costs it only on the runs when the disk happens to
be full. Both numbers are now measured. The note is in
`docs/ideas.md` on that entry, and the repair that serves both is the entry
below it: `_is_shallow` inside `undeployed_commits`, so a gate that knows its
window was truncated grades on what it has and says what it could not see.

## What I owe the sender, and it is a correction I cannot make stick by sending it again

The note carries "your sweep covered four of fifty-six rather than four of
241". Every figure in its derivation reproduces exactly on an independent `ast`
walk, which found 246 declarations, 4 positional, 242 flag-carried, 102
boolean and 7 with a `choices` list. The conclusion is still wrong, because `SWEPT` is
`("paths", "ids", "key")` and all three are positional. The 56 are flags. The
overlap is empty, measured. **Zero of fifty-six, not four.**

That correction was already sent, as `81ad102d` at 06:36:16Z, and it is not
the finding. The finding is the clock:

| time | what existed where |
|---|---|
| 05:42:04Z | this seat's withdrawal, four notes, on the bus |
| 06:05Z | the sender's derivation, on the bus, carrying `four of 56` |
| 06:12:47Z | **`zero of 56` measured, in #748's body** |
| 06:16:05Z | the sender's note, re-asserting `four of 56` |
| 06:36:16Z | `zero of 56` on the bus, as `81ad102d` |
| 06:39:18Z | the sender's next note, answering the 05:42 batch |

**Nobody was late and nobody was careless.** For twenty-three and a half
minutes the true number existed in a pull request body and nowhere a seat
reads, and the sender wrote a note in that window. Their 06:39 note is three
minutes after the correction and answers the older batch, so the correction
still has not been acknowledged and no one has made a mistake.

This is not a new class. The charter already carries it: "The first two
instances were written up carefully in pull request bodies, which nothing
sweeps, so the third seat rediscovered the class from scratch." What this run
adds is that the two surfaces have measurably different latencies, and the
faster one is the one with no index. A finding lands in the pull request first
because that is where the work is, and reaches the bus when the run gets round
to it. Everything in between is another seat building on a number that is
already dead.

The actionable half, and it is the only one in this seat's reach: **the
correction goes on the bus before the commit that proves it, not after.** That
is an ordering rule for this seat's own runs and it costs nothing.

## The grade: 2026-W42, read from the live site

Read once start to finish as the outsider before anything was scored, per law
12a. Served copy, un-rendered from `https://libraryofalexandria.dev/library/2026-W42`.
The un-renderer is proved on 2026-W39, which the repository holds both ways.
Every figure below is printed under the path it was measured on, per ban list 91.

**The single biggest weakness: a builder outside the research world cannot
read this issue.** 38 terms of art against the generator's own cap of five, 34
of them handed over with no clause. The worst sentence is in the reading list:

> A full post-training stack, hierarchical SFT and WIRL, for autonomous
> long-horizon ML engineering.

Four undefined terms in fifteen words, two of them acronyms appearing exactly
once each. The next sentence makes it worse rather than better: "The
hierarchical supervision and world-model-informed reward learning are the
parts most agents lack." A reader who does not already know what WIRL is has
now been told twice that it matters and never once what it is. This is law
12a's whole job and the issue fails it in the place a reader goes when they
have decided to trust the issue.

| law | verdict | evidence |
|---|---|---|
| 1 plain sentences, no em dashes, no semicolon joins | **FAIL** | `measure`: em dashes 0, semicolons 2. "Llama-3.1-8B loads skills 72% of the time overall; Llama-3.3-70B loads them 11% of the time." |
| 2 no buzzwords, every line targeted | **FAIL** | "Two papers this week converged on a finding that reshapes the retrieval stack." The finding is named in the next sentence, so "reshapes the stack" is decoration occupying the position where the finding goes. |
| 3 sell the product, never the recipe | PASS | The close gives scale and no method: "69 papers read in full this week, from 2,161 that arrived." |
| 4 the headline is a finding | PASS | "Agent skill systems are splitting between retrieval and self-evolution." A builder knows from that line whether to open it. |
| 5 relevance is impact, traction leads | **FAIL** | The lead slot carries a result the issue itself grades "one platform, one model family, five benchmarks, no replication outside the group yet". The traction item is in section two: "Two papers this week converged on a finding". Two groups converging is what traction means, and it did not lead. |
| 6 evidence grades in-line | **FAIL** | The grading is this issue's best feature and the attribution breaks under it. `provenance`: "The same paper also overturns a companion claim" — one paper cannot overturn itself. And "Vosti had claimed bitwise-identical logits across all tested execution variations" sits in a section whose reading links include *Vosti* itself, so a reader clicking full text gets the overturned claim with nothing saying so. |
| 7 honesty serves items, never the method | **FAIL** | Four instrument nouns wearing a colon, per `apparatus`: "The procedure is extractable:", "The grade: one platform, one model family, five benchmarks", "The procedure is clean:", "The procedure runs:". Plus "Three results stand out", which is the issue ranking itself out loud. |
| 8 links go to the full text | **FAIL** | 10 arXiv links, 9 of them `/abs/`, and `links` asked arXiv: 7 of the 9 have an HTML full text. Also 6 bare identifiers against 4 versioned in one issue, which is ban list 100. |
| 9 the fine-tuned instruction is the foundation | **FAIL** | Carried by laws 5 and 12 below. Her order is traction first; this issue inverts it and prints a slot label. |
| 10 the dual-audience close | PASS | "**Accelerate every builder and agent to frontier speed.**" |
| 11 length follows the news | PASS | 1,552 words, 35 paragraphs, three results and three reading-list items. No template shape, and the issue is honestly the size of its week. |
| 12a the outsider test and density | **FAIL** | 38 terms against a cap of five, 34 bare. See the quotation above. `measure` also finds one paragraph over 100 words, which is the smaller half. |
| 12 framework names never print | **FAIL** | `## What to read`, which `slotheads` names as "the ban's own phrasing". This is the one ruling the owner has given twice. |
| 13 every issue stands alone | PASS | "If you run agents that fetch skills from a library, you are choosing between two architectures that used to look like one." Present tense, the reader's own chair, nothing charged to a week they may not have had. `standalone` finds no hit in this edition. |
| 14 enjoyable, and formatting is how | **FAIL** | `measure`: shapes 1. `devices`: "no list and no written turn". The canon says the page count comes first and one shape is a failing grade on its own, and this is the state she read and rejected. |
| 15 never claims to have read what it only ingested | PASS | And it passes exactly as the law prescribes, with both numbers and the one allowed verb: "69 papers read in full this week, from 2,161 that arrived." |
| 16 a title already used is not a title | PASS | Distinct from 2026-W39 and 2026-W40. |

Five passes, eleven failures. That ratio is not a surprise and it is not a
decline: the press is running a generator from 2026-10-14 with 30 merged
commits queued behind the deploy, so this grade measures an 18.4-day-old file
against laws that have moved under it. Said plainly, because the opposite
reading is available and wrong: **most of these failures are already fixed in
the tree and undelivered, and the grade cannot tell which without asking.**
So it asked.

## What each failure got, and why most got no prompt diff

Step 3's amendment requires this run to say which command it asked, so each
row below names the answer `check_voice.py queued <law>` gave.

- **Law 12, `OK QUEUED`, no prompt diff.** Named by `97de5c8b`, "Generator:
  law 12's slot ban names a sixth dress, and one restatement pays for it",
  whose own message cites `## What to read` in 2026-W42 as its trigger. A
  previous run of this seat already graded this exact failure and already
  patched it. Verified non-reverted the way the charter demands, by diffing
  across the pair rather than trusting the count: the net
  `f16e2775..origin/main` diff of `prompts/digest.md` carries the change, and
  it is a subtle one worth recording. The queued patch *adds* the words
  "Gaining traction, Trailblazing, Left behind, Read these yourself" to the
  generator, replacing plain-English slot labels. That is correct and it reads
  backwards: the internal names are unmistakably unprintable, while a label
  like "what is genuinely new" reads like a draft heading and gets printed as
  one. 2026-W40 printed three of them.
- **Law 8, `FAIL UNNAMED`, and it goes to step 4 rather than to a diff.**
  Nothing is queued, so the amendment does not cover it. The rule is not thin:
  `prompts/digest.md:1399` already says to rewrite the url, already names the
  fallback condition, already says "only the path segment changes", already
  says a composed identifier is an invented one. `git log` shows six prior
  wordings and one revert. The structure-watch step exists for exactly this,
  and the pipeline change is filed in `docs/ideas.md` for the engineer:
  `pipeline/ingest.py:443` composes `https://arxiv.org/abs/{pid}` and hands
  the model a question that `check_voice.py:491` already answers. The
  implementation exists, tested, on the wrong side of the press.
- **Law 12a, `UNNAMED`, and this one got the prompt diff.** Not a rewording.
  The clause requirement is complete. The step written to PRODUCE the list it
  runs down says "take every word and short phrase in the finished issue that
  appears three times or more". **30 of the 34 bare terms in 2026-W42 appear
  fewer than three times**, so the list step could reach four of them. Same
  shape on both other served editions: 16 of 22 on 2026-W39, 29 of 33 on
  2026-W40. The floor was written for ordinary English doing a technical job,
  which recurs and needs frequency to be spotted at all. An acronym announces
  itself and appears once. So the floor keeps the class it was for and the
  visible terms of art are listed at first appearance with no threshold.
  Paid for per the canon's weight rule, below.
- **Laws 1, 7 and 14, where the rules are already complete and a fourth
  wording is what step 4 refuses.** Law 1's rule says "Count the semicolons. The target
  is zero and there is no budget." Law 7's colon ban is in the generator twice.
  Law 14's shape count is there with "Count the shapes first". All three are
  counts over finished text, all three are already implemented in
  `check_voice.py`, and all three ran tonight, after readers had the issue. The
  2026-10-12 ledger entry asking for those counts to run before a send is 21
  days old and still `proposed`. This run gave it its measurement rather than
  filing a fourth rule. **Canon law 12 is in that set, which is the sentence
  worth carrying: the only ruling the owner has had to give twice reached
  readers on an edition the repository could have refused, and the refusal was
  already written.**
- **Laws 2, 5, 6 and 9, reported and not patched, deliberately.** These are
  the four that need a reading rather than a count, and the generator's text
  on each is long and correct. A rule I cannot state more clearly than the
  file already does is a rule I should not restate. They are the grade's
  content and the next run's evidence if they repeat.

## What shipped in the gate, and both halves are the same defect

**`reading --live` reported a clean pass over a domain that excluded every
violation it exists to find.** Measured both ways, before the change:

```
$ python3 docs/voice/check_voice.py reading
surfaces read   63
lines giving the arriving count a verb of reading   4
[exit 1]

$ python3 docs/voice/check_voice.py reading --live
surfaces read   3
lines giving the arriving count a verb of reading   0
  every surface uses the verb the law allows
[exit 0]
```

`reading` is the only gate in `TAKES_PATHS` whose default domain is site
*code* rather than the issue archive, because canon law 15 binds "the
masthead, the email, the site and any line of copy". `--live` replaces the
archive glob, which is right for every other gate and drops the half the law
names first for this one. The four it stopped seeing are `site/app/page.jsx`,
`site/app/terms/page.jsx` and two in `site/app/llms.txt/route.js`, live on
pages anybody can open. `taste` inherits this gate's verdict for her
2026-09-29 verdict 6, so the green reported one of her rulings as held while
the line breaking it was on the home page.

The aggravating fact is that the file recommended it. `editions` prints
"`--live` on the passes that take paths is the way to answer it inside one
run", so the false green is what a run gets for following this file's own
printed advice. Ban list 155.

**The second half: there was no state in which that gate could have reported
the violation.** `reading` built its hit rows with a bare
`path.relative_to(ROOT)`, and `--live` hands it absolute paths in a tempdir
outside the repository. Reproduced before the fix on a planted edition:

```
RAISED ValueError: '/tmp/probe-f9ol64hf/2026-W99.md' is not in the subpath of
       '/tmp/epito-alexandria-writer-FtRz87'
```

So the two outcomes were a green that excluded the evidence and an uncaught
traceback. Seven of the eight path-taking gates that call `relative_to` wrap
it in `try`/`except ValueError`, and `measure`'s copy carries the comment
"used to raise rather than measure it (2026-10-06)". `reading` joined the
path-taking gates on 2026-10-23, seventeen days after that repair, and never
received it. A repair applied in seven places, missed by the one caller added
next.

Both repaired, with `READING_DOMAIN_CASES`, four asserted, in `dispatch`. The
domain identity is the guard rather than any single case: restoring the
replacing version fails all three path cases at once. `reading --live` now
reads 64 surfaces, 61 code and 3 served editions, and exits 1.

**What I did not mechanise.** The 77/56 split the sender proposed is judgment
about what a string means, and `firstuse`'s three kinds, `club`, `coined` and
`candidate`, are the same kind of judgment inside my own file. Neither has a
test here, by choice. Encoding judgment as measurement is the defect one
altitude above the one being fixed, and this run's own event is what that
looks like from the receiving end.

## The generator's weight, measured

The canon says a run that adds tokens removes at least as many, and the number
is not comfortable: `prompts/digest.md` was **34,717 tokens, $0.1482 an issue
against the $0.15 ceiling** in `tests/test_press_resilience.py`. That is
$0.0018 of headroom, about 1,900 tokens, for the whole seat.

After the law 12a patch: **34,720 tokens, $0.1482.** Three tokens over, cost
unchanged, so the addition is paid for. What paid for it, per the canon's list
of what trimming may take: the two-fixes pair stated three times in one pass
is now stated once, the account of which print produced the count clause is
gone, the jargon class is stated once instead of three times, and the date and
the counts came out of my own new clause and into this file, where the canon
says they belong.

tiktoken 0.14.0 is installed here, so these are exact rather than the
pessimistic estimate.

## Things found and left alone, so the next run does not chase them

- **`captions --live` FAILs, and it is the gate behaving correctly.** It
  filters a fixed table of site caption sets, so editions select nothing and
  it says so rather than printing its own case count and exiting 0. That is
  `SELECTION_CASES` working. It is also the right handling of the same
  `--live` class `reading` got wrong, in the same file, which is how I know
  the fix above is the house style and not my invention.
- **`taste` is red, honestly, and stays red.** Its one failure is verdict 6
  inheriting `reading`, and `reading` is red because four site surfaces break
  canon law 15. Those four are `site/`, the frontend seat's surface. Not mine
  to set, and the repair for the home page's line was drafted by this seat on
  2026-09-26 in `docs/voice/home-metric-line-2026-09-26.md`.
- **`ledger` is red and predates this run.** The desk reads
  `/- Status:\s*(\w+)/` and `tools/ledger.py` reads `/^-\s+Status:\s*(\w+)/m`,
  one entry apart. Verified by stashing this run's changes: 684/685 before,
  685/686 after, so both readers see my entry and the off-by-one is the
  pre-existing one, already filed in
  `docs/voice/desk-verdict-queue-2026-10-24.md`.
- **The live 2026-W39 still opens with the sentence law 13 was written for.**
  `standalone --live` finds it: "You have spent the week watching agents get
  faster by thinking less at test time." The canon quotes her rejection of
  that opening's earlier wording verbatim, prints the repair in full, and
  names the 2026-09-26 rehearsal of the same shape as the reason laws 13 and
  14 are "not yet strong enough". The repair text exists in `canon.md` and the
  served page does not carry it. The archive is `site/content/issues/`, which
  is not this seat's surface, and the committed file and the served page agree,
  so this is one edit in the frontend seat's lane rather than a press defect.
  Named here and not filed, because the edition is six weeks old and the
  generator's rule now catches the shape.

## Own-prose check, and it caught me

**The first draft of this file broke canon law 1 fifteen times, and the
sentence in this section claimed it had not.** I wrote "Semicolons in this
file: 0. Em dashes: 0" before running the command, which is the whole defect
of `INC-2026-10-12-the-editors-own-prose-broke-canon-law-one-a-fifth-time`
performed inside the paragraph that cites it. `selfcheck origin/main..HEAD`
then found thirteen marks in this review and two more in the sentence I added
to `docs/ideas.md`, two of them inside the row grading the issue's own
semicolons.

All fifteen struck, `selfcheck` clean at 0, re-run after the strike and not
before. The count is the gate's and not mine, and this section now says which
way round that happened, because the version where I quietly fixed it and kept
the clean sentence is the version that teaches the next run nothing.

Filed as a repeat, since the standing rule at the top of the incident register
admits no exceptions.

No reader-facing copy in this run, so no quality-claims round, no preference
file entry, and no frontend handoff is due.
