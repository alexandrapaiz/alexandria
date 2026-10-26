# 2026-W42's overturn section: the ruling, and the words to set

Writer run 57, 2026-10-26. The research seat's audit
(`docs/research/notes/2026-10-26-w42-left-behind-audit.md`, merged this pass)
read the live issue's overturn section against the two abstracts it cites and
scored it three wrong out of three. The PM handed the disposition to this seat
at 19:31Z with the reason that research found it and has no path to the site.

This file is the decision and the exact words. It is not set by this seat.
`site/` is the frontend seat's surface and that has not changed.

## The ruling: the section is pulled, not corrected

Three options were available and the middle one is the trap.

**Leave it.** No. The issue's own subtitle promises "what newer evidence has
overturned" and the generator's own instruction at that slot says what this
costs in the plainest terms available: an empty fell-behind section costs
nothing and a false one costs the reason to subscribe. Three of three is not a
section with an error in it.

**Correct it in place.** This is the one that looks right and is not. There is
no overturn to correct it into. The audit's finding is not that three relations
were mislabelled, it is that one paper's own theorem was printed as the thing
it refutes, one figure belongs to a paper the issue never names, and one
paper's two stated halves were set against each other. The honest version of
that material is two good new results, and both of them belong in the new-work
section of an issue that has already been sent. Writing them in would make the
archive a different issue under the same title, which is canon law 16's defect
in reverse: a reader who kept the email and opens the page would find
paragraphs they never received.

**Pull it.** This is the ruling. A subscriber received the issue with the
section in it on 2026-10-19 and the email cannot be recalled, so the archive is
the only correctable surface, and the correct archive is a subset of what was
sent rather than a rewrite of it. Removing a false section leaves every
sentence a subscriber read standing and true. Adding corrected prose does not.

## What goes, and it is four edits rather than one block

The artifact is the live page, un-rendered to the markdown the press stored:

```
python3 -I docs/voice/check_voice.py provenance --live
  2026-W42  2 finding(s)
    FAIL  line 47: points back at the work it overturns
    FAIL  line 49: the work that held it is a work this section links (vosti)
```

Line numbers are that markdown's, printed in full in this run's review.

1. **Lines 43 to 53, the whole section.** The heading "Hidden reasoning can be
   encrypted, not merely hidden", its three paragraphs, and both citation
   lines. The two papers go with it, because a citation under no item is a
   named work with nothing said about it.
2. **The third sentence of the lead paragraph at line 7.** "And a long-held
   belief about hidden reasoning in chain-of-thought traces was overturned
   twice in one week, leaving the monitoring picture murkier than the field had
   admitted." It is the same false claim in the position where the reader meets
   it first.
3. **"Three results stand out" becomes "Two results stand out"**, same line.
   The lead names three and one of them is leaving, and the generator's own
   count gate exists because a reader who counts two where three were promised
   goes back to look for what they missed and there is nothing to find.
4. **The masthead's third clause, on this one page.** Line 3 reads "*What's new
   in AI research, what's gaining acceptance, and what newer evidence has
   overturned.*" and becomes "*What's new in AI research and what's gaining
   acceptance.*" A promise standing above a section that is no longer there is
   the same defect as the section, one line higher.

What the fourth edit is NOT, said here because it would be easy to read it as a
repair and stop. `MASTHEAD` in `pipeline/weekly.py` is unchanged and still
recites the framework slots in plain-English synonyms on every issue the press
sends, which is a canon law 12 violation that has been filed for 23 days and is
the engineer's. This removes the one clause that promises the removed section
from the one page it was removed on. The register entry stays open.

## The close is untouched, and that was checked rather than assumed

The close says "These three papers suggest the answer depends on whether your
skills are static documents or living code, and that the tooling to test either
is now available with a budget cap attached." The three it counts are the
retrieval group, the self-evolution group and the budget platform. None of them
is the hidden-reasoning paper, so the count is still right after the excision.

## The two semicolons stay, and that is a decision rather than an oversight

`check_voice.py marks` reports two semicolon joins on the corrected artifact,
at lines 21 and 27, both in the retrieval section. They are canon law 1
failures and they are not repaired here.

The reason is the line this whole ruling turns on. This edit exists to remove
something false. The semicolons are a style defect in prose that is true, and a
subscriber received them. Editing them makes the archive diverge from the send
for no honesty reason. Law 1 is held by the generator and by the pre-send gate,
which is where a run this morning correctly refused to add a fourth wording of
it, and holding it retroactively on one page buys nothing and costs the record.

## The corrected artifact measures no worse on any axis

```
python3 -I docs/voice/check_voice.py measure <before> <after>
  before   words 1552  paragraphs 35  longest 103  over100 1  shapes 1
  after    words 1299  paragraphs 30  longest 103  over100 1  shapes 2
  provenance:  2 finding(s) before, 0 after
```

Shapes went from one to two because the removed section was four paragraphs of
one kind. Law 14's "one kind is a failing issue" is still failing at two, and
that is a property of the issue as sent rather than of this edit.

## The one line that needs her word, with this seat's recommendation

Everything above is this seat's call and is made. This is not, because no
ruling covers it and the two honest answers differ for the reader.

**Recommended, to sit directly under the masthead on this page only:**

> One section of this issue was removed on October 26, 2026, because its three
> statements about findings that newer work had overturned did not hold against
> the papers it cited.

The case for it. An archive that quietly loses a section is a record that edits
itself without saying so, and the only thing the removed section ever cost was
a reader's reason to believe the next one. A publisher that says what it
withdrew is the cheapest trust available here.

The case against it, and it is real. Her ruling of 2026-09-19 is that the issue
never narrates its own methodology, ranking logic or virtues, and a correction
notice is a shape no issue of this product has ever carried.

Why the recommendation is to carry it anyway. The ban is on an issue
advertising how it works. This sentence says what happened to this page, in the
past tense, and claims nothing about how the library operates, which is the
line `docs/agents/quality-claims.md` asks every claim to stand on: it is
checkable against one artifact and it promises no mechanism. A sentence saying
we check our claims against the papers would be the violation, and it is not
this sentence.

Under the company standard's §22 this proceeds as recommended after
forty-eight hours of her silence. It moves no authority and no money.

## Who sets it

The frontend seat, and the route needs no database credential, which is the
part worth carrying.

`site/lib/issues-core.js` `pickIssue` returns the committed file ahead of the
`digests` row, and `mergeIssues` lets files override rows in the listing too.
So a corrected `site/content/issues/2026-W42.md` is served to every reader in
place of the stored body, with the Modal workspace still off and `NEON_RO_URL`
unset. The stored row keeps the sent text, which is correct: it is the record of
what went out.

The full corrected markdown is the artifact to commit and this seat holds it.
It is not pasted here, because a 62-line issue body copied into a candidate
file is a second copy that can drift from the first.

One warning the same mechanism has already earned. `site/content/issues/2026-W39.md`
is why `check_voice.py standalone` fails on the archive today: her correction to
that issue's opening was applied downstream of the record, the file was later
replaced with what the press sent, and the correction was lost. A correction
written into the file is the durable half here, and the file is what this ruling
asks for.
