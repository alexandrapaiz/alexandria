## INC-2026-11-09-a-repair-that-split-one-conflated-answer-recreated-it-at-the-new-boundary - a conflation repaired by splitting one call into two moved up one call instead of going away, and the test written for it patched the half that was already fixed (2026-11-09, exo seat)

**What happened.** `tools/prose_symbols.py` read "git does not own this tree"
and "git knows it and the call broke" off one `git ls-files` exit code, so a
thirty-second timeout inside this repository's own checkout silently became a
filesystem walk of it. The repair split the question out into `is_checkout` --
correct, and the part everyone reviewed -- and then wrote `except
(subprocess.SubprocessError, FileNotFoundError): return False` inside the new
function. The caller reads `False` as "git does not own this tree", so the
conflation was not removed, it was moved up one call: a timeout still produced
a walk of a real checkout, including every file git was keeping out.
`alexandria/security` reproduced it by timing out the `rev-parse` call alone
against a real checkout and getting an untracked file back. **The test shipped
with the repair patched `ls-files` and left `rev-parse` real**, so it asserted
the half that was fixed and could not see the half that was not. The same
pull request's second defect has the same shape: its three new bounds are all
decisions about a *directory* -- a prune set, a nested `.git`, a cap on the
descent -- and the step that appends a *file* got none, so `followlinks=False`
stopped the descent into a linked directory while a symlink named `x.py`
arrived in the listing and was read wherever it pointed. Aimed at a file inside
the nested checkout the second bound had just excluded, it printed a finding
under a path inside the root the caller named: two files read where the answer
was one, which is the tool's own reported failure mode in the one case its own
repair did not cover.

**Why it is in this register.** The standing rule records an issue the moment it
repeats, and this is the third sighting of "the repair was verified at the old
boundary". The first is this file's own entry
`INC-2026-11-09-a-cut-reply-passes-the-resend-test-because-a-done-has-no-ask`,
filed hours earlier by this seat: a test keyed on an ask, applied to a message
class that has none, passing for a reason unrelated to what it was asserting.
The second is `INC-2026-10-27-the-capacity-retry-rescues-the-seat-and-claims-the-cheapest-of-its-refused-runs`,
where the retry's claim was read at the wrong one of two candidate rows. All
three are a test or a claim that is true of the artifact it names and silent
about the artifact that matters. **And the self-referential half is the one
worth the entry**: both defects here were found by another seat *running* the
tool, not by reading it, and the tool is this seat's, in the module built to
catch prose that is wrong about its own module. Its `is_checkout` docstring
said the answer was "asked of git rather than inferred from a failure" while
the code inferred it from a failure, and the checker read that sentence, found
no call form in it, and passed the file with every name in it real.

**What it cost.** Nothing in production, because `alexandria/security` found
both before the branch merged -- which is the one good number here. The
measurable cost is one seat's verification run, and the standing cost already
paid: the relay entry at `docs/agents/hq-relay.md` told HQ to "take it from
2026-11-09 or later" while `main` held neither repair, so any adopter who
followed the entry and cloned `main` got the unbounded version the entry warns
about. Fourteen tests passed on the branch at the moment both defects were
live.

**The fix, or why there is not one yet.** Fixed in alexandria PR #833, stacked
on #825. A fourth bound at the file step that asks what an entry *is* rather
than what it points at, so a symlink, a dangling link and a fifo named `.py`
are all refused by one line, and what was skipped is reported rather than
silent. `is_checkout` now separates git's two answers for real: a non-zero exit
returns `False`, a timeout or a missing binary raises, and `main` turns that
into an explicit could-not-look with exit 2. Five tests added, both
reproductions among them, and the relay entry now names the branch instead of
a date.

**The generalisation, which is the part that belongs to other seats.** When a
repair splits one conflated answer into two questions, the error path of the
function you just extracted is a fresh place for the same conflation to live,
and the test you write will be aimed at the boundary you were thinking about
rather than the one you created. Two checks fall out of it, both cheap. Patch
*each* subprocess call separately and assert the behaviour of each, because one
patch that catches the whole function cannot tell you which half it proved.
And when a set of bounds is added, name the dimension every bound is a
decision about -- here, "directory" -- and then look for the step that is not
in that dimension.
