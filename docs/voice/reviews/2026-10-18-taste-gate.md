# The register this seat reads first had no check, and the first honest run of its check is red

**Writer run, 2026-10-18, ninth run of the day. Graded against the registers
rather than against a new issue, for the reason in the first section.**

## The biggest weakness, stated first

It is this seat's own loop and not the artifact. The charter makes
`docs/voice/taste.md` the register read FIRST, before the canon laws are scored
at all, and the canon's pass 2 has said "ruling by ruling, against the issue
and against the generator" since it was written, citing incident 20 in the same
sentence. Nothing in the loop ever re-ran it. So the seat has a register it
reads, a law saying reading is not enforcing, and a procedure whose second
pass is the only one with no machine under it.

The cost is measured rather than argued. Her title ruling of 2026-10-04 names
this seat and `prompts/digest.md` in its own last sentence. Fourteen days and
five writer runs later the prompt did not carry it. Her site-copy ruling of
2026-09-29 carries six numbered verdicts, and the sixth of them, never "read"
for ingested, is being broken on four reader-facing lines today, three of them
since before the ruling was given.

## Why this run did not grade a new issue

The press has printed nothing since 2026-10-05, which is thirteen days.
`NEON_RO_URL` is unset in this runtime, so the newest issue available is
`site/content/issues/2026-W39.md`, and that file has been graded in roughly
twenty reviews in this directory. Both of its standing defects are already in
the registers with their own entries: the presumptive opening is ban list 894's
specimen, and the archived masthead carrying "read in full and distilled
weekly" is filed as the owner's call, because the line was spliced into the
body before storage and no later edit reaches it.

A twenty-first grade of the same file would produce the same verdicts and would
read like work. The artifact this run could actually improve is the generator
and the instrument, so that is what it graded, and the whole instrument was run
over the issue for the record rather than re-read by hand.

| command | verdict |
|---|---|
| `enforcements` | 74 endings, 45 quoted and resolving, 29 prose only |
| `sweep` | 50 of 50 anchored, every anchor still in the generator |
| `taste` | **red**, and the red is true. One ruling of 31 is not held |
| `stale` | 2 hits, both read by hand, both claims about past output |
| `measure` | clean |
| `links` | clean |
| `delivery` | clean |
| `claims` | **red on main**, 17 claims unhedged and live, the ExO's register |
| `reading` | **red on main**, 4 lines, one of them found only today |
| `candidates` | clean, after this run withdrew its own draft |

## What the new gate is, and the constraint that shaped it

`docs/voice/check_voice.py taste`. All 31 of her rulings mapped to the text
that enforces each one: 27 landed and quoted, 3 filed with the reason no file
can carry them, 1 marked as replaced by a later ruling.

The design is forced by a boundary. This seat may not edit `taste.md`, so the
anchor convention the ban list uses, a `LANDED` line written inside the entry,
is not available. The quote has to live on the checker's side and reach across
into her register. That inverts `sweep`, where the register holds the numbers
and the map answers for them. Here the register holds prose nobody else may
touch, the map quotes it, and the check asks whether the quote still resolves.
A ruling she rewords breaks its own row, which is the behaviour I want: a
reworded ruling is a ruling to re-read.

Five failure modes, each proven by breaking it rather than asserted:

| failure | how it was proven |
|---|---|
| a ruling no row claims | appended a dated ruling, exit 1, named by date |
| a row whose quote of her words stops resolving | reworded a ruling in place, exit 1, both halves reported |
| a row matching two rulings | added a row anchored on "site copy", exit 1 |
| an enforcement that has left the file it named | struck the title rule from the generator, exit 1 |
| a supersession pointing at nothing | repointed the close's supersession, exit 1 |

## The first green run was false, and that is the finding worth keeping

The check passed on its first firing. 31 rulings, every quote resolving. I
nearly shipped it.

Her 2026-09-29 ruling was green because two of its six verdicts are anchored to
bare-noun headings on the site that she approved herself, and both quotes
resolve. The sixth verdict of the same ruling was being broken on three
reader-facing surfaces at that moment, and `reading`, the command that knows
it, was red on main and read by nobody.

So a quote proves a rule is present and says nothing about the artifact. Rows
can now inherit a command's verdict instead of a quote, and the gate is red on
that ruling. A red first run of a gate is worth more than a green one, and this
one is red for a true reason that no eye in this seat's loop had seen.

What it still cannot see is the width, and that is named in the code rather
than discovered later. Her outsider ruling covers every term of art in an issue
and the quote anchoring it covers the first use of one. Checking the width is a
reading and belongs to the grade.

## Three defects found by building the instrument

**1. The generator was stuttering, and the stutter was mine.** Two lines of the
fell-behind slot printed twice, from a botched edit in the eighth run's commit,
whose message says it touched the canon. The model reads the same instruction
twice and the press pays 32 tokens an issue for it. 34,396 prompt tokens to
34,364. No gate saw it: `enforcements` reads anchors, `budget.py` reads a total,
the grade reads the issue, and none of the three can see a block repeated
inside the prompt.

**2. Law 15's command missed a violation because the subject was a pronoun.**
`site/app/llms.txt/route.js:13` has said "alexandria is an autonomous research
pipeline. It reads the week's AI research" since the file was written. The
pattern needs the library named inside the sentence carrying the verb, and a
paragraph that names it once and then pronominalises it keeps the claim and
moves the subject out of reach. Her ruling of 2026-09-20 rejects that same word
as the subject of a mechanism sentence, so the line is wrong twice over and was
caught by neither gate for twenty-three days. The pattern is widened, the
fourth instance is reported, and the class is ban list 128.

**3. The law's own specimen passes the law's own command, and this one is
reported rather than fixed.** Law 15's text cites the masthead, "read in full
and distilled weekly", as its evidence. The command excludes "read in full" by
a negative lookahead, correctly for the clause and falsely for the claim,
because the masthead applies "read in full" to all of AI research. The live
masthead was repaired on 2026-09-26. The archived issue still carries the old
one, which is filed as the owner's call. So the blind spot has no live victim
today and it will have one the next time a surface writes "read in full" about
the corpus rather than about the 166.

## And this run repeated a failure recorded four runs earlier

It drafted four candidates for four law-15 lines. Every one of the four
surfaces already had an open candidate, one of them twenty-two days old, and
all three earlier candidates are better. The home metric line's candidate
prints both numbers, what arrived and what was read in full, which is the form
law 15 asks a scale sentence to take, and this run's version dropped the second
number.

The draft is withdrawn. The register that would have stopped it,
`docs/voice/awaiting-her-word.md`, was created four runs earlier for exactly
this, and says in its own second paragraph that it is the first file a writer
run opens. The charter's shipping step names seven registers and not that one,
so a seat following its charter exactly reads seven and not the eighth, and the
step is at shipping time, which is after the drafting by construction.

That ordering is right for a check and wrong for a precondition. So the duty is
`docs/voice/check_voice.py candidates`, over the run's own diff, with the
register's own escape: a run may draft for a listed surface as long as it names
the candidate already open on it. Proven both ways on the withdrawn draft. It
fired on all three surfaces, and passed once the draft named the three files.

The charter line is asked for in the ledger rather than written here, because a
charter is not this seat's surface. Both gates are needed for the same reason
the org needs a draft gate and a merge gate: the command saves the owner a
review, and the charter line saves the run its work. This run wrote four
candidates and threw all four away.

## The ten laws, scored against this run's own artifacts

The artifact is the instrument and the registers, so the laws are scored
against this run's own prose, by command rather than by reading, which is the
rule added to the canon on 2026-10-13.

`python3 -I docs/voice/check_voice.py selfcheck origin/main`: 0 lines carry a
mark this file cannot excuse. One em dash in an added line is the regex that
has to match her register's own date separator, written as `—` so that
law 1 needs no exception for it. Two semicolons, both inside code.

Law 3, sell the product and never the recipe, does not engage: no copy shipped.
Laws 4 to 11 are issue laws and no issue was written. Law 12a, the outsider
test, binds this review, and the test I applied is whether a reader who has
never opened this repository can follow why a quote on one side of a boundary
is the only shape available. Law 13, stands alone: every register named here is
named with what it is, not with a pointer back to a previous run.

Law 15 is the one this run is about and it is the one broken in public. Four
lines. Three have candidates awaiting her word and the fourth is inside one of
them.

## The weighing gate, which the last run added

A run that adds tokens removes at least as many. This run removed 32 and added
none. `prompts/digest.md` is 34,364 tokens and $0.1479 an issue against the
$0.15 ceiling, which is 2,258 tokens of headroom, and the floor the eighth run
measured has not moved: two thirds of the per-issue cost is the output
reservation and no amount of editing reaches it.

## What is not fixed

The wiring. Four of this file's commands now read a register against a file and
none of them is called by anything. The ask is filed for the third time and the
scoping note matters more now, because `taste` and `claims` and `reading` are
all honestly red and will stay red until she rules on three candidates and the
frontend seat sets them. Switching the whole file on in CI before that puts red
on work the engineer cannot do. The four register-against-file checks,
`enforcements`, `sweep`, `taste` and `candidates`, are green today and stay
green without anyone ruling on anything, so they can be wired now.

And the question that has been open for eighteen days and is hers alone: is
`docs/voice/value.md` still the target owed an approval, or is it stale against
the five pages she approved on 2026-09-29? Its own status line says no site
copy is drafted until she rules, on a day when five approved pages are live and
nine candidates are waiting. No copy round converges while that sentence is
unresolved.
