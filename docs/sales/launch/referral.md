# Referral and share mechanics

Rewritten 2026-09-30. The constraint from the charter has not changed and is
the whole design brief: the honest-billing principle extends to growth, so no
manufactured urgency, no pressure copy about what a friend already did, and no
points system pretending to be more than it is.

What has changed is that the 2026-09-18 version's two mechanics were both
about the email, and the email is not this company's most-copied artifact. The
skill file is. A skill file exists in order to be copied into somebody else's
repository, which means the library's distribution channel is the filesystem,
and nobody has looked at what happens to a copy once it leaves.

## Mechanic 1, the return address. New this run, and the one to build

**The finding.** Read the frontmatter of any skill in the library. It carries
the papers with their arXiv links, a list of claim numbers, an extraction date
and, on one file, a validation result. It does not carry a single reference to
alexandria. Somebody copies `skills/harness-engineering/SKILL.md` into their
own repository, which is the exact act the file was designed for and the best
thing that can happen to it, and the copy has no idea where it came from.

We ship our best asset with no return address on it, and we do that at the one
moment when a stranger has already decided they want it.

**The mechanic.** Two lines in the provenance block of every skill.

```
source: libraryofalexandr.ia/skills/harness-engineering
updated: 2026-09-12
```

That is the whole build. Six files today, one line each in a block that already
exists, and it is a frontend and skill-seat edit rather than anything new.

**Why it is not tracking, and why that matters here.** There is no unique
identifier, no per-download code, no pixel and no way to tell one copy from
another. It is attribution in the sense a citation is attribution. Anything
that could identify who copied the file would be the dark pattern this charter
rules out, and it would also be worse at the job, because a line a person is
happy to leave in the file survives and a tracking parameter gets deleted.

**The second-order effect, which is the actually valuable half.** A skill file
copied in October and never touched again is wrong by March, because the entire
premise of this company is that findings stop being true. Today a stale copy
fails silently in somebody's repository and takes our name down with it, except
that our name is not on it, so it takes nothing down and teaches nobody
anything. With those two lines, a stale copy tells its reader two things at
once: there is a canonical version of this, and the version you are holding has
a date on it. That converts the copy from a leak into the product's own
argument, and it does it without a single word of marketing inside an
engineer's repository.

**How it gets measured, honestly and publicly.** GitHub code search for the
string `libraryofalexandr.ia/skills` returns the number of public repositories
holding a copy. It is a real number, it is independently checkable by anyone
who doubts it, it needs no analytics of ours, and it is the first growth metric
this company could quote without asking a reader to trust us. It undercounts,
because private repositories are invisible, and undercounting in public is the
right direction to be wrong in.

**Ask.** Skill seat adds the two lines on the next maintenance pass, per the
one-skill-per-run rule already in force, or in one pass across six files if the
owner wants it before launch. Filed in the ledger in this pull request.

## Mechanic 2, forward this. Live at launch, nothing to build

The launch email and every digest end with a plain forwarding ask and no
tracked link. For a list of comped friends this is the correct mechanic, and
building attribution for a few dozen people is overhead the charter's own
cheapness instruction argues against.

```
If you know one or two people who would use a skill file rather than merely
click a link about one, forwarding this is the entire referral program at the
moment.
```

Plain ASCII, no em dash, and no scare quotes around the contrast. The
2026-09-18 version of this paragraph used two em dashes and a quoted aside, and
both are house violations that had been law for a day when it was written.

## Mechanic 3, the issue permalink. A site feature, flagged not owned

Every issue should carry a link to its own page, so that a good issue becomes
its own acquisition surface without asking the reader to do anything but read.
This depends on the archive rendering each issue at a stable path, and the
archive holds two issues today with a week missing between them. It is the
cheapest growth loop on this list and it is a frontend item, flagged here
rather than claimed.

## Mechanic 4, manual referral credit. After launch, not at it

Once paid signup exists, the honest cheap version is that a subscriber tells
the owner who they referred and the owner credits one month by hand. Manual on
purpose: unique codes, a referral table and webhook credit logic are real
engineering scope, and proposing that spend before there are enough paid
subscribers to make the build pay is the kind of premature machinery this
charter's cheapness rule exists to stop.

## What is deliberately absent

No leaderboard, no public referral count, no streak, and no framing that turns
sharing into a competition. None of it fits the house voice and none of it is
needed to make forwarding an email work. A referral mechanic that would
embarrass us if a subscriber described it out loud is not a mechanic we ship.
