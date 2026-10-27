# Twenty grades have one artifact, and the fact that decides what to do about a failed law was going into the review instead of the commit

**Writer run 61, 2026-10-27, hook, capacity return.** The provider limit cut
run 60's successor off at turn 42, after it had opened pull request #643,
merged #622 and merged `main`, and written nothing of its own. This branch
carries both merges forward and does the run they never reached.

## The generator the press is running, before the first verdict

Per the canon's forwards check, said with the command:

```
python3 -I docs/voice/check_voice.py press
  the generator it carries   9b6410ea 2026-10-14T20:08:38+00:00
  deployed at               2026-10-15 17:40:37+00:00
  queued commits            28
  FAIL  BEHIND: 12.4 days old
```

Unchanged from run 60's reading two hours earlier. The press is writing from a
generator twelve days old with twenty-eight merged patches queued behind a
deploy, and the engineer's queue is blocked on a disabled Modal workspace.

## The artifact did not move, and that is verified rather than assumed

The charter's duplicate-wake rule says a run that finds its predecessor's work
already covering this event verifies live rather than trusting the report. So:

```
served_weeks()  ->  ['2026-W39', '2026-W40', '2026-W42']
measure 2026-W42 (served, un-rendered)
  words 1552   paragraphs 35   longest 103  over100 1
  em dashes 0  semicolons 2    shapes 1     links 2
marks     2 semicolons, lines 21 and 27
devices   FAIL  no list and no written turn
standalone  0 over 17 passing cases
```

Every figure is run 60's figure. `2026-W42` is still the newest served edition
and not one character of it has changed, so the sixteen verdicts in
`docs/voice/reviews/2026-10-27-hook.md` stand as this run's grade and are not
rewritten here. Nine held, law 1 failed twice on semicolons, law 8 nine times
on `/abs/` links, law 12a on eleven unglossed terms of art, and law 14 on a
page with one shape and no list. Re-prosing sixteen verdicts about a file that
did not move is the thing this run filed an incident about, and doing it anyway
would be the fifth instance.

**One of those verdicts is corrected, and the correction is the finding.** Run
60 wrote that law 12a was "the one failure with no patch in the queue". That
was reached by hand, from twenty-eight commit subjects, and it is not what the
queue says. Twenty-one queued commits land inside law 12a's span. None of them
names a law, so the honest answer is that the queue could not be asked, and
the state is `UNNAMED` rather than either `QUEUED` or `UNPATCHED`.

## The single biggest weakness, and it is in this seat's own filing habits

**Step 3 of this charter says a prompt change cites the law it serves.
Twenty-eight generator patches are queued and two of them do.**

```
queued commits to the generator            28
of those, naming the law they serve        2
```

The citation was never skipped. It went into the review, every time, and a
review is read once, by its author, on the day it is written. So the one fact
that decides what a grade does about a failed law, which is whether the rule is
already fixed and waiting on a deploy, was not recoverable from the queue. Four
consecutive runs rebuilt it from commit subjects and memory. Run 51 escalated
law 8's form to the ledger rather than word it a fourth time, run 54 refused a
fourth wording of law 1, run 60 refused a fifth wording of law 12a and shipped
no prompt diff at all, and each of those three judgments was correct and cost a
run the derivation.

The same shape sits inside the generator. Five of the sixteen laws, **3, 7, 8,
10 and 16**, carried their rule in `prompts/digest.md` with no citation naming
the law. Law 3's rule is there, at "Sell what alexandria found, never how the
digest gets written". Law 8's is there, at "Links reach the full text, never
the landing page". Law 10's is the standing close and law 16's is her
2026-10-04 ruling on repeated titles, both present in full. Only the names were
missing, and laws 3 and 8 are two of the four failures in the live grade. So
nothing could be asked whether the generator covers a law a grade had just
failed, because a positional reading returns nothing for a law that owns no
span.

## Why twenty grades share one artifact, which is the structural half

`docs/voice/reviews/` holds twenty-one files dated 2026-10-19 or later. The
product has served one newest edition across that whole span. The charter's run
reads as one grade per issue and nothing in it says what the second grade of
the same issue does differently.

That is the reason the structure-watch step keeps firing. Where twenty grades
share one page, the failure a grade finds has usually been patched by a
previous grade, so the correct action on a failed law is most often to name the
commit that fixes it and write nothing. Step 3 says the opposite in its own
words, and step 4 only reaches the case at the third repetition of one fix, so
the first two repetitions are each a judgment a run makes against its own
charter. Four runs made it correctly. The fifth would not have to.

## The patch, and why it is citations rather than rules

Step 3 asks for the smallest prompt change that would have prevented a failed
grade. Five of the sixteen laws are now cited at the rule that serves them, in
the file's own idiom, which it already uses twenty-six times.

```
law 3   (canon law 3) at the recipe rule
law 7   (owner's ruling, 2026-09-19, canon law 7) at honesty without narration
law 8   (canon law 8) at the full-text link rule
law 10  (canon law 10) at the standing close
law 16  (owner's ruling, 2026-10-04, canon law 16) at the prior-titles rule
```

Thirty-one citations now, every law named, no rule reworded and no rule added.
This is deliberately not a patch for law 1, 12a or 14. Those three are already
worked by commits sitting in the queue or escalated in the ledger, and a fifth
wording of a rule whose fourth wording has not reached the press is what the
structure-watch step exists to refuse. `generator` is green on both prompt
files, fourteen headless cases passing, which is how I know the five insertions
cut nothing.

## The instrument, and the wrong answer it gave first

`check_voice.py queued` reads the queue and answers, per law, whether a patch
for it is merged and waiting. It attributes a commit to a law twice, by the
message and by position, and it reports those separately.

**It reported the wrong thing first, and the wrong thing was flattering.** The
first version returned the union of both readings under one name and said law
12a was worked by twenty-one of twenty-eight commits, which contradicted a
grade written two hours earlier. The grade was closer to right than the
instrument. Law 12a's citations own a 325-line span of a 2,191-line file and
law 1's own 305, so between them they own 29% of the generator and any commit
landing in that 29% attributed to one of them. The number measured citation
sparsity and not anybody's intent. Counts print with their spans now, because a
count without its span reads like evidence.

Four states, and the fourth is the one worth carrying:

- `QUEUED`, the fix is merged and undelivered, so the grade fails the law and
  writes nothing. Law 8 today, by its own two commits.
- `UNNAMED`, commits landed in the law's span and none said so. Laws 1, 12a and
  14 today. An instruction to read those commits, never an answer.
- `UNPATCHED`, the law is cited, owns a span, and nothing in the queue touches
  it. A prompt patch is the run's work.
- `UNCITED`, the generator never names the law, so it owns no span and the
  queue cannot be asked at all. Laws 3, 7, 10 and 16 read this on `origin/main`
  this morning. The verdict that resembles it from outside is `UNPATCHED`, and
  acting on that means rewording a rule the generator already carries. An
  instrument confidently flattering about the one law with no patch is the
  worst available case, which is ban list 146 pointed at this file.

Sixteen pinned cases over four pure functions, no network and no git in any of
them, including the two that would have caught the first version: named and
nearby disagreeing, and a span of zero answering `UNCITED` rather than
`UNPATCHED`.

## What landed

- `prompts/digest.md`, five law citations, no rule touched.
- `docs/voice/check_voice.py queued`, and `press_deploy` factored out of
  `press` so the receipt read has one copy rather than two.
- `docs/voice/canon.md`, the commit-citation line and the generator-citation
  line as one dated section, with the structure-watch step's command under it.
- Ban list 147, the fact written where it is read once.
- Two incidents, the twenty-grades-one-artifact shape and the citation that
  went into the review.
- One ledger entry for the ExO: the sentence step 3 is missing.

## No new copy candidate

`docs/voice/value.md` still carries no recorded approval, which is this
charter's precondition for a copy round. Nothing in this diff is
reader-facing, so step 1b's claims check has no sentence to run on, and step 5b
has no approved copy to hand off.

## Gates

`press` 4 of 4 cases, red on the live row, which is the standing finding.
`queued` 16 of 16 cases over `CHANGED_CASES`, `LAWS_CASES`, `SPAN_CASES` and
`VERDICT_CASES`, red on the live row because four laws read `UNCITED` on
`origin/main` and three read `UNNAMED`.
`generator` clean on both prompt files, 14 headless cases, run after the five
insertions and timed at 115 seconds.
`deadlines` 4 of 4 cases, clean. The one row carrying a clock expires
2026-10-28T20:44Z and has not run out.
`candidates` clean.
`taste` 31 rulings, 27 enforced, 3 filed with their reason, 1 superseded. The
one failure is verdict 6 standing red because `reading` is red on live site
lines that two other seats owe, which is the same pre-existing red run 60 read.
`enforcements` 92 entries, both of ban list 147's quoted anchors resolving.
`selfcheck` 0 unexcused against `origin/main`. It found two semicolons in this
run's own added lines, one in the ledger entry and one in a comment in
`check_voice.py`, and both were struck rather than excused. An editor who
excuses her own mark has stopped being the instrument.
`tools/incidents.py check` 353 entries and 47 inbox files, nothing malformed.
`tools/check_registers.py` and `tools/ledger.py --check` both 0 blocking and at
the recorded baseline.
The conflict-marker grep over `docs/`, `prompts/` and `README.md` prints
nothing.

## The wake, answered

#643's wake was the ExO seat's class C ask: one sentence in this seat's ship
check so merged copy hands off to the frontend seat. The ExO wrote that
sentence itself, as step 5b of `prompts/writer-agent.md`, and it is on `main`.
Nothing was owed here but to follow it, and this run carries no approved copy,
so 5b has nothing to hand off. Answered on the board as a `done`, with the step
3 ask carried back in the same message, because the ExO owns the charter this
seat cannot edit.
