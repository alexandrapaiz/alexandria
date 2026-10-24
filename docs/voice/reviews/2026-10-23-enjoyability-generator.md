# One gate of five has ever been in force for an issue the press made

**Writer run, 2026-10-23, third run of the day. The item is the sprint's head
card, `Reading enjoyability: the prose is not nailed down, and it is urgent`
(owner, 2026-10-05). The artifact graded is `prompts/digest.md` against the
rewrite the benchmark picked.**

## The biggest weakness, stated first

The pick is sound and the machine behind it is unmeasured, and this run has
the number for how unmeasured.

`docs/voice/benchmark-2026-10-18.md` scored two texts and said forward the
rewrite. It also said the thing nobody followed up: "Nothing on this page is a
measurement of the generator. It is a measurement of two texts, one of which
the generator wrote." This seat then wrote that caveat onto the board card and
left it there for five days.

So I took it. The rewrite beats the sent version on five gates. For each of
those five, I asked whether the rule that would close it was in the generator
on the day the generator last printed anything.

**One of the five was. It failed.** Three are governed by rules written after
the newest print exists, and one of those rules was written out of that very
print. The fifth has no establishable date in this runtime.

That is not a prose finding and no wording fixes it. The pick asks the owner
to make the rewrite the floor, and the honest statement of what she is being
asked to approve is a floor whose five requirements have between them been
tested once.

## What was measured, and the scope stated before the numbers

Three prints of the generator are reachable from this runtime, and no more.
`site/content/issues/2026-W37.md`, retired from the public archive on her
order of 2026-09-19. `site/content/issues/2026-W39.md`, which is public.
And the 2026-W40 opening quoted in
`docs/voice/enjoyability-benchmark-2026-10-05.md`, sent 2026-10-05 and still
the newest thing the press has made.

The W40 figures below are the opening and first section alone, 398 words of a
1,350-word issue, because that is the scope the rewrite was written at and a
gate compared across two scopes compares nothing. Where the full issue's
figure is known it is named as the full issue's.

The two link gates are excluded rather than scored, for the reason the
benchmark excluded them: neither excerpt holds a reading list.

```
$ python3 -I docs/voice/check_voice.py measure <each path>

axis                                target   W37 gen   W39 gen   W40 gen  W40 HAND
semicolons                             <=0        1*        1*        1*         0
em dashes                              <=0        8*         0         0         0
non-ASCII, no exception                <=0      152*         0         0         0
shapes the writer added                >=3         3         2*        1*        4
paragraphs over 100 words              <=0        8*        4*        1*         0
sections over four paragraphs           <=0        0         0         0         0
headings carrying a colon              <=0        0         0         1*        0
```

Eight gates, and the hand rewrite is the only text in the table that passes
all of them. No print of this generator ever has.

## The five gates, each against the date of its own rule

The dates are the ban list's own `Added` lines. Git cannot supply them here,
because this runtime holds a one-commit clone, which is
`INC-2026-10-18-the-machinery-diff-reads-clean-on-a-shallow-clone`.

| gate | newest print | the rule that governs it | in force for that print |
|---|---|---|---|
| semicolons | 1, and 8 in the full issue | entry 95, added 2026-10-05 | no, and it was written out of this print |
| shapes at 3 or more | 1 | entry 98, added 2026-10-06 | no |
| one list block | 0 | entry 116, added 2026-10-16 | no |
| paragraphs over 100 words | 1, and 4 in the full issue | entry 58, added 2026-09-26 | **yes** |
| headings carrying a colon | 1 | the seventh count, no entry found | not established |

The one row that says yes is the finding's sharpest end. The hundred-word rule
was nine days old when W40 printed, and the issue carried four paragraphs over
the line, down from eight in W37. The rule is working and has never landed.
That gate is improving under a wording, so its wording is the binding
constraint and a patch to it is testable. It is also the only one of the five
where that sentence is true.

For the other four, a sixth rewriting is not a test of anything, because no
print has yet tested the fifth. `check_voice.py compare` exists to make
exactly this distinction and it needs two prints at one `prompt_sha`. There
has been one print in eighteen days.

## The colon in that heading is not a punctuation slip

Worth separating out, because the gate reports it as a count and it is the
most-ruled-on thing in this seat's charter.

The newest print the press has produced carries this heading.

> ## What is gaining ground: recursive self-improvement with fewer guardrails

"Gaining traction" is the framework's internal name. Her ruling of 2026-09-19
is that the internal names are never printed and every heading a reader sees
is written fresh from that day's news. She gave it twice. It is canon law 12
and incident 20.

The rewrite's four headings, at three levels, are the control.

> An agent that improves itself needs nothing scoring it
>
> The same week, a cheaper way to keep the gains
>
> Training on a tenth of a percent of the data

The generator is not the thing at fault here, and I checked before writing
this. Its seventh count already says what to look for, in its own words: "a
slot name, then a colon, then the day's news, which the heading rule spends a
paragraph forbidding." There is nothing to add to it and a sixth wording would
be the move this review spends its last section refusing.

The instrument is the thing at fault. `axes` returned this as a bare number
and `measure` printed nothing at all, so the one ruling she has had to give
twice reached a grade as `headings carrying a colon: 1`. A seat reading that
line sees punctuation. The colon is the detector and the label is the defect.

So the change is to `docs/voice/check_voice.py`, which is this seat's file, and
`measure` now prints the specimen under the law.

```
shapes 1     links 0     paragraph 5
  one kind of block is a failing issue (canon law 14)
  colon heading, canon law 12 and incident 20: ## What is gaining ground: ...
    the internal names are never printed. Strike the label and the colon,
    and check whether what is left is the heading.
```

The line above it is the precedent. That file has named canon law 14 under its
shape count since 2026-10-17, and the reason is the same reason: a count a
seat has to translate back into a law is a count a seat reads past.

## The second finding, which is live and public and not about the newsletter

Canon law 15 cites exactly one string as its evidence.

> The masthead said "read in full and distilled weekly" on every issue ever
> sent, against 166 full reads out of 8,956 papers held.

`pipeline/weekly.py` was repaired. Its masthead now reads "What's new in AI
research, what's gaining acceptance, and what newer evidence has overturned."

The third line of `site/content/issues/2026-W39.md` still says it.

And `site/lib/issues-core.js` settles what that means: "the record decides
which weeks exist, the committed file decides the text of any week that has
one." 2026-W39 has one and is not hidden, so that file is the live public text
of the one week the archive publishes. Twenty-eight days, on a page anybody
can open, under a law that quotes the sentence.

Two reasons the gate built for the law could not see it, and both are now
closed in `docs/voice/check_voice.py`.

- **Its surface list held the module and not the archive.** `SURFACE_GLOBS`
  takes `pipeline/weekly.py`, which is the string that will print on the next
  issue. A masthead repaired in the module is repaired for every week the press
  has not written yet and for no week it already did. The archive globs are
  added to `reading` alone, because `claims` reads the same list and an issue
  body's sentences are claims about the research rather than about our
  artifact.
- **Its regex exempted the law's own string.** `READING` skips "read in full",
  and it has to: that is the one act the word may name, and "164 papers read in
  full" is both true and the sentence the law asks for. Attached to a count it
  is a fact. Attached to a cadence it is a claim about everything that arrives
  in a week. The exemption now holds for the count form and not the cadence
  form.

The check's own docstring wrote this hole down when it was built and left it
open: "a sentence that says read in full over a number that came from the
ingest field passes here and is a worse version of the same lie." It was not a
hypothetical. It was already in print.

The repair to the line is drafted at
`docs/voice/archive-masthead-2026-10-23.md` and is the frontend seat's to set,
because `site/` is not this seat's surface.

## The ten laws, scored

Against `site/content/issues/2026-W39.md`, the public print, with the W40
opening cited where it is the sharper specimen.

1. **Punctuation. FAIL.** One semicolon, joining two clauses that are each a
   finished sentence. Quoted here in a block, because the mark is the specimen.

   ```
   RMBench measures end-to-end agent construction on software tasks; the
   air-combat result measures win rate in a physics simulator.
   ```

   The rule's own fix is a full stop. The count that would have caught it
   postdates this print by eleven days.
2. **Plain words over club words. FAIL.** Unchanged from this morning's grade,
   which counted 24 terms of art and 22 without a clause. Not re-counted here
   and not re-filed.
3. **Context first. PASS.** "You have spent the week watching agents get
   faster by thinking less at test time. That trick has a ceiling." The
   subfield and its stuck problem, before any finding.
4. **Institution-first attribution. PASS.** "Researchers at Peking University,
   Google, and HKUST have shown" opens the section rather than a surname.
5. **Varied rhythm. FAIL.** Four paragraphs over 100 words, the longest 141.
   The rule governing this is the one rule on this list that was in force for
   a print and is measurably working. No patch.
6. **Evidence grades. PASS on the half the payload can serve.** The tie the
   benchmark found is a missing field, filed as ban list 124 and in the ledger
   for the engineer. Not re-filed.
7. **The contents draw the conclusion. PASS.** No line tells the reader what
   to think that the results do not.
8. **Depth follows significance. PASS.** The lead finding takes the longest
   section.
9. **Shape. FAIL.** Two kinds of block on the page, and law 14 calls one kind
   categorical. The rule that counts this postdates the print by twelve days.
10. **The closing line prints verbatim and last. PASS.** Present and last.
    The unterminated slot that threatened it was the subject of this morning's
    second run and is fixed on main.

Nine laws scored, four failing, and three of the four failures are governed by
rules the press has never run. That ratio is the review.

## What is owed, and by whom

- **The owner.** The card's done condition is her pick and the next issue held
  to it. The benchmark recommends the rewrite. What this run adds, and she
  should have it before she rules, is that adopting it makes every print to
  date a failing issue, and the first real test of the pick is the next send
  rather than anything in this pull request.
- **The engineer.** Two blockers, both on the board already. `Press: no issue
  for 2026-W41`, and `Deploy: weekly is not running main, still on
  0cbc51a0e248`. The second is the one that matters to this card. A print made
  from a pinned old commit does not test the generator on main, so it would
  not close a single row of the table above. I could not verify that commit
  from here, because a one-commit clone cannot reach it, so this cites the
  board's own card rather than a reading.
- **The frontend seat.** The archive masthead line, drafted and waiting.
- **The ExO seat.** Whether `docs/agents/quality-claims.md` should cover the
  archive is that seat's call on its own file. This run points the `reading`
  law at it and deliberately does not point the claims register at it.

## This run changed the generator not at all

`prompts/digest.md` is untouched by this pull request. Stated plainly rather
than padded, because the charter says a quiet day with no diff is a fine
outcome and the reason here is better than quiet.

Four of the five gates the pick depends on have rules younger than the newest
print. Writing a sixth wording of any of them would be this seat patching
toward a number that does not exist yet, which is the move the ledger entry of
2026-10-15 named and `compare` was built to stop. The generator is ahead of its
own evidence. The next print is what this seat is waiting on, and the waiting
is the correct state rather than a stall.

Every diff this run does carry is an instrument rather than prose, and each
exists because a rule was already right and unreadable at the point of use.
The `reading` law was right and pointed at the wrong files. The colon rule was
right and arrived at a grade as punctuation. That is the shape of this seat's
work when the prompt is no longer the weak link.

## The sweep that found a second one in the same file

Ban list 131 says the generalisable half of the archive finding is the surface
list rather than the string, so I ran L-A21's test over the rest of this
seat's gates. It takes one question per gate. Name a change that would break
what this gate governs, then ask whether the gate would have seen it.

`candidates` is the gate that stops a run redrafting a surface another run has
already drafted. Its `SURFACE` regex matched `site/**.{jsx,js,txt}`. The
archive is `.md`.

So the gate built to stop a surface being redrafted could not see an archive
candidate at all, and what it would have printed is the sentence a later run
would have trusted.

```
no candidate here redrafts a surface already awaiting her word
```

Two gates in one file, the same error, and the second was found by applying a
test to the first rather than by anything noticing. `claims` is the third and
stays pointed where it is, with the reason filed for the seat whose register
it is.

Widening it then surfaced the opposite failure, which is worth recording
because it is evidence about widening rather than about this file. With `.md`
matching, `candidates` accused this run of redrafting its own candidate and
named the file in the accusation. A surface held only by the file being
checked is not a clash. It is the normal shape of a first draft, where the
register row and the candidate land in one diff, and the bug was latent since
the gate was written because it only fires when both arrive together. Fixed,
and a probe confirmed a real clash still fires.

## Sources

- The gate figures: `python3 -I docs/voice/check_voice.py measure <path>`,
  run 2026-10-23 on the three prints and on the rewrite.
- The two W40 bodies, cut from the quoted blocks of
  `docs/voice/enjoyability-benchmark-2026-10-05.md` and not committed, for the
  reason that page gives.
- The rule dates: the `Added` lines of `docs/voice/ban-list.md` entries 58, 95,
  98 and 116.
- The pick and its caveat: `docs/voice/benchmark-2026-10-18.md`.
- Which weeks are public: `site/lib/issues-core.js` and `site/lib/content.js`.
