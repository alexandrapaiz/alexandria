# The register that answers "has this surface been written for" could not see a candidate standing alone

**Writer run 58, 2026-10-26, message.** The wake said this seat's pull request
had merged and asked for the next item in the lane. The lane's Backlog, This
sprint and In progress columns are all empty, and the newest sprint plan,
`sprint-2026-10-26` on the PM's open pass, carries five items and all five are
the engineer's. So the item was not read off a column. It was the defect this
seat's own last run walked into nine hours before this one started, and the
command that was supposed to stop it printed green while it happened.

## The biggest weakness, stated plainly

`docs/voice/awaiting-her-word.md` is the register whose own second paragraph
calls it the first file a writer run opens, because it answers the one question
the other registers cannot: has this surface already been written for?
`check_voice.py candidates` is the command that makes that duty a check rather
than a paragraph, and it asked only half the question. It compared a run's new
candidates against the open rows and failed where a surface was already held by
a different candidate. **A candidate for a surface this register had never held
matched nothing, registered nothing, and passed**, and the pass line read "no
candidate here redrafts a surface already awaiting her word", which is what it
prints for a run that did the bookkeeping right.

Run 57 is the instance. It ruled on the live `2026-W42` page, wrote the exact
words in `docs/voice/w42-correction-2026-10-26.md`, raised one line that needs
her word, and merged with no row in the register and no question row either. For
nine hours the newest copy candidate this seat holds existed in no index, while
the page it corrects went on serving three statements the research seat measured
wrong three for three.

## The measurement, because a paragraph about a gate is worth less than its recall

Every file under `docs/voice/` that is a candidate rather than a review or a
record, against whether any row in the register names it.

| Candidate | Live `site/` surfaces it names | Named by a row |
|---|---|---|
| `archive-masthead-2026-10-23.md` | 2 | yes, closed |
| `claim-repairs-2026-10-18.md` | 2 | yes |
| `desk-verdict-queue-2026-10-24.md` | 1 | yes |
| `home-metric-line-2026-09-26.md` | 2 | yes |
| `llms-txt-2026-10-18.md` | 3 | yes |
| `pricing-claims-2026-10-18.md` | 3 | yes |
| `shelf-names-2026-10-26.md` | 2 | yes |
| `site-copy-2026-09-19.md` | 2 | yes, closed |
| `skills-copy-2026-10-18.md` | 5 | yes |
| `w42-correction-2026-10-26.md` | 3 | **no** |
| `corrections/2026-W42-corrected.md` | 0 | no, and the floor below cannot see it either |

Ten of eleven, and the one that is missing is the newest. Four more files sit in
that directory and are not in this table, because `benchmark-2026-10-18.md`,
`enjoyability-benchmark-2026-10-05.md`, `market-bar-2026-10-16.md` and
`prose-benchmark-2026-09-19.md` are studies rather than candidates and name no
surface at all. Their absence from the register is correct and it is worth
stating, because a recall number that counted them would read 10 of 15 and the
gap would be four files nobody should be looking for.

## Re-run against the branch that merged, the widened command fails it

```
python3 -I docs/voice/check_voice.py candidates 9c8c5973^1
  FAIL    docs/voice/reviews/2026-10-26-message-overturn-audit.md
            drafts for site/app/llms.txt/route.js, which is already open in llms-txt-2026-10-18.md
  FAIL    docs/voice/reviews/2026-10-26-message-overturn-audit.md
            drafts for site/app/terms/page.jsx, which is already open in claim-repairs-2026-10-18.md
  FAIL    docs/voice/w42-correction-2026-10-26.md
            no row in awaiting-her-word.md names it, and it names 3 live surface(s):
              site/content/issues/2026-W39.md
              site/content/issues/2026-W42.md
              site/lib/issues-core.js
```

The third line is the new one. The first two are the old gate working, on the
same branch, unrecorded: run 57's review reports `selfcheck` and never ran
`candidates`, so a gate of this seat's own was red on a branch that merged. Both
failures were right to fire. That review cites the terms page and the
`llms.txt` route as live reading defects and two candidates have been awaiting
her word on those surfaces since 2026-10-18, which is exactly the bookkeeping
the gate asks a run to do before it writes about a surface somebody already
drafted.

## The repair, and the two scope decisions that are the whole of it

A floor under the clash test. A candidate file that names a live `site/` surface
and that no row in the register names back now fails, and one row clears it.

**It applies to candidate files only.** `FLOOR_CASES` pins that scope with six
real paths and runs before any diff is read, in the shape `SELFCHECK_CASES` and
`HEADLESS_CASES` already use. The false cases carry the weight: a review and a
preference record both live under `docs/voice/` and both quote live surfaces by
path as evidence, so a floor that caught them would fail every grade this seat
writes, and a gate that fails the work it governs gets switched off.

**It asks for one row per candidate and not one per surface.** The first version
asked per surface and reported three failures for the single W42 candidate,
because that file also cites the `2026-W39` page whose correction was lost
downstream and the module the override serves through. Neither is a line it
proposes to replace. Clearing those two would have put rows in the register for
surfaces nobody drafted, which is a worse register than the silence it replaced.
The unit of this register is the candidate, so the question is whether the draft
is indexed at all.

**And one limit stays.** The floor reads a candidate's surface out of the
candidate's own prose, so a candidate that names no surface is invisible to it.
`corrections/2026-W42-corrected.md` is that case, being the corrected body
itself. It is indexed only because the row for its parent names it by filename,
and no command would have asked for that.

## Two rows written, and one of them is the first here with a deadline

The surface row is `site/content/issues/2026-W42.md`, and the answer to "is the
defective line still live" was read rather than assumed. At 20:49Z today, after
the ruling merged, the page still serves the heading "Hidden reasoning can be
encrypted, not merely hidden". The ruling is to pull that section rather than
reword it, setting it is the frontend seat's diff, and the PM's pass records why
it was not dispatched: that seat has an open pull request on another topic and
the hard stop against dispatching a seat with one applies regardless of subject.

The question row is the correction notice, which needs her word and no wording
can settle. The PM posted it as a formal ask carrying this seat's
recommendation, so under the company standard's silence rule it proceeds as
recommended at about 20:44 UTC on 2026-10-28. **That date is in the row**, which
is the half that was missing: a reservation for the owner with a clock on it and
no row anywhere is a clock nobody can read.

## The repeat, filed rather than described a fourth time

`INC-2026-10-26-the-gate-that-asks-whether-a-surface-was-drafted-for-passes-a-candidate-with-no-row`,
and the shape has now run three consecutive runs of this seat. Run 56 found
`routed` could only read SCREAMING_CASE identifiers, so it had never caught a
re-filed finding. Run 57 found the claims pass had six questions and not one of
them opened a paper. This run found `candidates` could read two candidates
colliding and not one standing alone.

The narrow claim those three share is sharper than incident 20's general one,
and it is the one worth carrying. Each gate's scope was drawn from the defect
that produced it, so each was blind to the first instance of its own class and
printed a reassuring line about it. The widening of this gate's surface pattern
on an earlier run is the proof that the blindness is not laziness: that run
reasoned carefully about what the gate could SEE, wrote eleven lines of comment
about the cost of missing an issue page, and never asked what the gate would say
once it saw one.

## No grade this run, and the reason is still a missed send

```
python3 tools/delivery_health.py --surface press --no-notify
  FAILING  press  the newest issue is 2026-W42 and 2026-W43 has ended; 1 issue(s) missing
```

`2026-W42` has now been graded by runs 51 and 57 and audited by the research
seat, and its overturn section is ruled pulled. A fourth reading of one edition
produces a second opinion rather than a patch. The Monday slot passed with
nothing printed and the cause is the engineer's and recorded, which is the Modal
workspace being off since 2026-10-23.

- **No patch to `prompts/digest.md`.** No failed grade in this run to translate,
  because there was no grade. Run 57's third test at the fell-behind slot is the
  live one and it is undeployed, so the generator's next measurable change is a
  deploy rather than a diff.
- **No ban-list addition.** An entry records a prose tell seen in an artifact
  and this run read no new artifact prose. The reassuring pass line this run
  deleted is a tell, and it is in Python rather than in anything a reader sees.
- **No copy drafted.** `docs/voice/value.md` still carries no recorded approval,
  which is the charter's precondition. The PM's ask on that precondition was
  posted on 2026-10-26 at 06:20Z and its own silence window has not run.

## This run's own prose, measured over the branch

```
python3 -I docs/voice/check_voice.py selfcheck origin/main
  added lines read from   origin/main
  no semicolon and no em dash in any added line
  0 line(s) carry a mark this file cannot excuse
```

Taken with every file staged first, because an unstaged file this run created is
invisible to `git diff` and that is ban list 144's third finding. It found one
semicolon on the first pass, in a comment inside the new code, and it was struck
rather than excused.

`candidates` on this branch is clean, and the reason is the gate rather than the
absence of a clash: this review cites `site/content/issues/2026-W42.md`, which
now holds an open row, and it names `w42-correction-2026-10-26.md` as the
candidate open on it. `python3 tools/incidents.py check` reads 344 entries and
nothing malformed. The conflict-marker grep over `docs/`, `prompts/` and
`README.md` prints nothing.

The gates that are red on this branch were red on `main` before it and none of
them is this run's: `reading` on four lines, `claims` on 24 unhedged claims,
`taste` on verdict 6 which `reading` holds down, `ledger` on the desk count by
one, and `editions`, `marks`, `devices` and `standalone` on the two issues that
reached readers and are not files here. Every one of them has a row in the table
this run just added to, or belongs to another seat's register.
