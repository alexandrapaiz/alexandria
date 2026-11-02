## INC-2026-10-27-the-citation-step-3-requires-went-into-the-review-and-never-the-commit - 2 of 28 queued generator commits name the law they serve (2026-10-27, writer seat, hook run)

**What happened.** The writer charter's step 3 says a prompt change cites the
law it serves. Twenty-eight merged commits to `prompts/digest.md` are queued
behind the weekly deploy, and two of them name a law in the commit message:
`c5a32e4c` and the revert of it, `0251df0b`, both law 8.

The citation was not skipped. It went into the review file, every time, which
is where step 3 is also read. A review is read once, by its author, on the day
it is written. So the fact a later run needs, which is whether the rule it is
about to reword is already fixed and waiting on a deploy, was not recoverable
from the queue, and four consecutive runs rebuilt it from commit subjects and
memory instead.

```
queued commits to the generator            28
of those, naming the law they serve        2
changed lines under no citation            0
```

The same shape sits inside the generator. Five of the sixteen laws, 3, 7, 8,
10 and 16, had their rule written into `prompts/digest.md` with no citation
naming the law, two of them, 3 and 8, failures in today's live grade. The rules
were all present. The name was not, so nothing could be asked whether the
generator covers a law a grade had just failed, and a positional reading
returns nothing at all for a law that owns no span.

**Why it is in this register.** The standing rule records a repeat at the moment
it repeats, and this is the third instance of one class in four days. The first
two are in the writer charter's own text:
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`
records that the duplicate-wake class was written up carefully in two pull
request bodies, which nothing sweeps, so a third seat rediscovered it from
scratch. This is that, in commit messages rather than PR bodies, and with a
count. Registered as ban list 147, "the fact written where it is read once,
rather than where it is read again", with the test stated as one question: will
the next run that needs this fact be reading the file I am putting it in?

**What it cost.** The derivation four times, and one wrong conclusion drawn
from it this morning, recorded in the sibling entry
`INC-2026-10-27-twenty-grades-share-one-artifact-and-the-charters-run-assumes-one-each`.

**The fix, or why there is not one yet.** `docs/voice/canon.md` now carries the
commit-citation line and the generator-citation line as one dated section, and
`prompts/digest.md` carries the five citations that were missing, so every law
owns a span. `docs/voice/check_voice.py queued` reads the queue twice, by
message and by position, and prints `UNCITED` as its own state rather than as
`UNPATCHED`, because the two look alike from outside and acting on the second
one means rewording a rule the generator already carries.

This entry is an instance and not a remedy for the general case. Nothing sweeps
commit messages for the citation, and the gate that would is not this seat's to
write.
