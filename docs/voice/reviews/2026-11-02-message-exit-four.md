# Writer run, 2026-11-02: the exit code I asked for was already spent, and the gate for it had the same defect

Woken by a `note` from alexandria/engineer, `a17423f5`, 05:12Z, ref PR #731.
The wake carried 1192 of 3788 characters and said so, so the tail was read on
the board before anything was written. Ninth link in this seat's chain.

## The single biggest weakness, which is mine

**I specified a number into another seat's file by carrying the convention of
the file I own, and the number was already spent there.** My ledger ask of
earlier tonight asked `tools/board.py inbox` to refuse an unknown seat name
"with exit 2 rather than reporting zero. Exit 2 and not 1, so a caller
separates `this seat is not here` from `this seat has no mail`."

That file spends 2 at `main()`'s `except BoardError: return 2`, for the board
refused or could not be asked, and spends 3 as `EXIT_AMBIGUOUS`. The engineer
seat used 4 and answered: "If your dispatcher is free to use two, use two. I
cannot." Both numbers were one grep from an ask that names the file by path in
its own first line.

`check_voice.py` returns 2 from its own dispatcher for an unknown gate, and I
shipped that and argued for it twice. So the ask did not guess. It carried,
and the carrying is invisible from inside, because the reasoning that justifies
2 in my file is sound and travels with it.

## The grade, scored only on what this run's artifacts can break

No reader-facing prose was produced this run and no new edition exists to
grade, so the laws are scored against the three artifacts this run shipped,
which are a gate, a ban-list pair and an incident entry. The laws a run with
no prose cannot score are named as unscored rather than passed, because a
flattering grade is a corrupted instrument and nine of ten rows reading
"clean" on a run that wrote no issue is the easiest flattery available.

| law | what it says | verdict on this run |
|---|---|---|
| 1 | plain sentences, no stylistic em dashes, no semicolon joins | **failed and repaired.** `selfcheck` found three semicolons in `spent_exits`'s docstring list and one em dash in this file's own first draft heading. All four struck, not excused. The one em dash left is inside a test fixture quoting a real ledger heading, and it stays because changing it would stop the case matching live data |
| 2 | no buzzwords, every line targeted | clean. `selfcheck` clean after the strike |
| 3 | sell the product, never the recipe | unscored. No reader-facing copy this run |
| 4 | the headline is a finding | holds on this file and on both commits. "the exit code I asked for was already spent" is the finding, not the subject |
| 5 | relevance is impact, not recency | unscored. No ranking produced |
| 6 | evidence grades in-line | holds. Every figure below carries the command that produced it |
| 7 | honesty serves items, never the method | **the one I had to argue with myself about.** The gate prints a paragraph about where its own defect came from. That is method narration, and law 7 bans it inside an ISSUE. A docstring is read by the next run and never by a reader, which is the distinction canon's 2026-10-27 section draws for law citations, so it stays |
| 8 | links go to the full text | unscored. No links written |
| 9 | her fine-tuned instruction is the foundation | holds by not being touched. `prompts/digest.md` is untouched this run |
| 10 | the dual-audience close | unscored. No issue written |
| 11 | length follows the news | holds. Two ban-list entries because the note handed two tells, not because the file wanted a round number |
| 12 | framework names never print | unscored. No headings written |
| 12a | the outsider test and density | **the live risk and the reason this row is not clean.** Ban list 152 explains an exit-code collision to a reader who may not hold the convention. Its second sentence defines the shape before the instance arrives, which is the on-ramp duty. The density rule is the part I would still fail on re-reading: entry 152 runs five paragraphs for one defect |
| 13 | every issue stands alone | holds on both ban-list entries. Each states its instance in full rather than pointing at the incident entry |

## What the machine caught that I did not

Three times this run, and that is the number worth reporting rather than the
fixes.

**The gate built to catch this class shipped with the class in it.**
`ledger_bullets` joined a bullet's wrapped continuation lines and recognised
only bullets carrying a `Label:`, so an off-schema bullet's wrapped lines were
appended to the last labelled bullet before it. The instance is as close to
the bone as it gets: the correction recording that my ask named the wrong
number quotes `exit 2`, the quote landed inside the `What:` bullet it was
correcting, and the gate stayed red for the sentence repairing it.
`docs/ideas.md` holds 539 off-schema bullets, so the parser's domain was the
bullets its author had in mind.

**The second draft of the gate printed a clean pass over the one real
collision.** It called a file unenumerable as soon as any exit path returned a
value rather than a literal, so all 40 tools with an entrypoint came back
CANNOT and the report ended `OK every proposed code is free`. Certainty is per
path and never per file. `board.py` computes `args.func(args)` and writes 2
down in the same function, and the written 2 is the allocation the ask hit.
That draft was ban list 150 with my name on it.

**A surviving mutation found a case I had written to pass.** The first case for
the off-schema branch labelled its own bullet `Answered:`, so it matched the
recogniser and passed whether the branch existed or not. Backing the branch
out left every case green. Rewritten with a genuinely unlabelled bullet, the
mutation is caught. Second run in a row that a surviving mutation found a hole
in my own cases rather than in the code.

## What shipped

`check_voice.py exits`. Reads every exit code `tools/` writes down and fails
on a ledger entry proposing one the named file already holds.

It reads the tree with `ast` and not a regex, and that is the engineer seat's
lesson rather than my caution. Their note reported two bugs in their own
roster shortcut, a regex matching the company key where the board's company
name is the product key, and one reading only the block form where the
manifest writes inline mappings. Both "returned an empty set for every real
call, which is a roster that is never consulted and reads exactly like a roster
that agrees." A gate comparing the shortcut to the real parser caught both
before they shipped.

Three answers and never two, which is the whole design.

| answer | when | why it is not the others |
|---|---|---|
| a collision | the code is in the file's written set | definite, and the only state that fails the gate |
| `FREE`, provisional | not written, and some path of that file computes a status | the enumeration is incomplete and the report says so |
| `CANNOT` | the file has no exit surface, or is not in the tree | `tools/noship.py` is named in a 2026-09-26 entry and does not exist. Failing on it would hold the ledger red over another seat's unwritten work |

| table | cases | what it pins |
|---|---|---|
| `CERTAINTY_CASES` | 10 | a library, a computed status, two literal arms of a conditional, a return through a declared `EXIT` name, `sys.exit(__doc__)`, an unparseable file, a bare `return`, the `SystemExit(main())` delegation, and `return smoke()` |
| `EXIT_CASES` | 14 | the live `board.py` shape, the dict form five tools use, string keys with a `None` value, `True` not being a code, a helper's `return 2` not being one, `()` for a file that exits and writes nothing down against `None` for a library |
| `LEDGER_CASES` | 8 | the live wrapped ask, an observed code in `Trigger:` not being a proposal, zero not being allocable, two tools for one code, and the off-schema bullet both ways |
| `COLLISION_CASES` | 5 | the live collision, the engineer's 4 against the same file, a named code reporting its name, `()` against `None` |

37 asserted cases. **Eleven mutations, every one backed out in the working
tree, all eleven caught, and the file verified byte-identical after each by
sha256.** The eleventh is the one described above, which survived its first
case.

Over the live tree: 42 files, 16 with every exit path written down, 24 with
some path computing a status, 2 libraries. Codes written down are 0 in 32
files, 1 in 26, 2 in 17, 3 in 3, 4 in 1 and 130 in 1. Five files name their
codes, and those five are the only ones where a collision is legible to the
seat proposing one.

## Ban list

Two entries, both readings rather than phrases, both handed to me by the note.

**151, the restated register entry, which reads as a check and is a
repetition.** The engineer seat named it against itself in the clearest
sentence anybody here has written on it: "a sentence restated from another
seat's register entry looks like a check, a citation and a claim at once, and
is none of them." It belongs in this file rather than the incident register
because my step 1b test asks whether a sentence is about the research or about
our artifact, and a restated register entry is about our artifact AND carries a
citation, so it passes the only test I run on claims.

**152, the number proposed into another seat's file without reading what that
file already spends it on.** My own, with `exits` as its second ending.

## No prompt diff, and no eighth grade of one edition

`prompts/digest.md` is untouched. The newest served edition is still
**2026-W42**, `recorded_at` 2026-10-19T09:01:21.333Z, read off the live
receipt this run and unmoved. The press runs the generator as of `9b6410ea`,
**18.4 days old**, with **30 merged commits to `prompts/digest.md` queued
behind the deploy**. A rule reworded tonight is the thirty-first thing waiting
on that same deploy, which is the condition the charter's granted step-3
amendment was written for.

The command the charter asks for, with its answer:

```
python3 docs/voice/check_voice.py queued 1 3 8 12a 14
```

28 queued commits after two cancelled each other as a revert pair, **1 naming
the law it serves**, 0 changed lines under no citation. Five laws come back
`UNNAMED`, which is an instruction to read those commits and not a verdict:
law 1 with 14 commits in a 197-line span, law 3 with 1 in 107, law 8 with 2 in
143, law 12a with 19 in 346, law 14 with 3 in 103. No law reports `QUEUED`, so
no failed law this run is waiting on a merged fix, and none reports `UNPATCHED`
either, because nothing this run found is a prose defect in a generated
edition.

**Structure watch is empty.** No structural fix was attempted through prompt
changes, so nothing has failed twice.

## Taste, run first and ruling by ruling

31 rulings, 27 enforced in a file and quoted, 3 filed with the reason no file
can carry them, 1 replaced by a later ruling.

One FAIL, and it is not this run's and not mine to close: verdict 6 of the
2026-09-29 ruling, never "read" for ingested. Four live instances, all in
`site/`, at `site/app/page.jsx:44`, `site/app/terms/page.jsx:19` and
`site/app/llms.txt/route.js` lines 31 and 36. The replacement copy has been
drafted in `docs/voice/claim-repairs-2026-10-18.md` since run 40 and is open
on her word. `site/` is the frontend seat's surface. Reported unchanged rather
than re-litigated.

## Step 1b does not fire

No reader-facing copy was produced, so no row of `docs/agents/quality-claims.md`
is engaged and no frontend handoff is owed. The one claim this run makes about
a machine is that `exits` exists and catches one collision, and the machine is
in the diff.
