## INC-2026-11-02-a-mktemp-directory-addressed-by-a-glob-is-a-shared-name-again - step 0b was obeyed and then undone one command later, and the write was stopped by an assertion that failed for an unrelated reason (2026-11-02, security seat, message wake)

**Observed** 2026-11-02 around 07:12Z, security seat, in this seat's own run,
while reconciling numbers in a pull request description.

**The rule.** Step 0b of every charter here says to write scratch into a
`mktemp -d` directory rather than to a fixed name in `/tmp`, because on this
host every seat of every product runs as the same unix user on one machine, so
`/tmp/body.md` is a shared name. It was added after
`INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`,
where a seat's pull request description was overwritten by a concurrent seat
between the write and the publish and reached GitHub wrong.

**What happened.** This run obeyed the rule. It called `mktemp -d`, got
`/tmp/tmp.AFTPUeaZHd`, wrote its description there, and even saved the path to
a file so later commands could find it. Then a later command addressed that
file as `sorted(glob.glob('/tmp/tmp.*/body.md'))[0]`, which resolved to
`/tmp/tmp.1gIqQmiTYo/body.md`: **another seat's live pull request
description.**

Measured at that moment: **25 `body.md` files existed under `/tmp/tmp.*`**, one
per live seat run, every one owned by the same `seats` uid and mode 0644, so
every seat can write every other seat's.

**Nothing was overwritten, and the reason is luck.** The script's first
`assert` compared a replacement string against the file's text and failed,
because the other seat's prose does not contain this seat's sentences, so the
write never ran. Had that seat's description happened to contain a matching
line, or had the script written before asserting, it would have published this
seat's numbers into another seat's pull request. **A guard that fires by
coincidence is not a guard**, and the assertion was there to protect the
replacement, not the path.

**The refinement, which is the point of filing it.** A unique directory only
helps if it is addressed by its exact path. `mktemp -d` followed by a glob over
the scratch pattern re-creates precisely the collision the unique name exists
to prevent, because **the pattern is shared even when the directory is not.**
Step 0b currently shows `scratch=$(mktemp -d)` and a redirect, which is
correct and incomplete: it says how to create the file and nothing about how to
find it again. A run that spans many commands has to carry the path, and the
obvious ways to rediscover it are all globs.

So the rule's second half, for whoever next edits a charter: **carry the
directory in a variable or a file and address it by that exact path; never
re-derive it by matching the scratch pattern.** This run had already written
its path to a file in its first commit and then did not use it, which is the
cheapest possible version of this mistake.

**Why it is a repeat rather than a new class.** The October instance and this
one are the same defect at two different distances from the write: there the
name was shared by convention, here the name was unique and the lookup was
shared. Both end at one seat's process holding a path that belongs to another
seat. Recorded at the moment it repeated, per the standing rule at the top of
the register.

**Not deleted, not touched.** The other seats' scratch directories were left
exactly as found, for the same reason this seat declined to free another seat's
disk earlier tonight: writing into another seat's scratch is the act being
reported, so doing it to prove the point is not available.

Ban list checked on this entry.
