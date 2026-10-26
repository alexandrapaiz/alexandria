## INC-2026-10-26-the-gate-this-seat-points-at-itself-passed-clean-on-a-ref-that-does-not-resolve - `check_voice.py selfcheck` printed a clean pass for a base ref git could not resolve, and two writer runs reported figures from it (2026-10-26, writer seat)

**What happened.** `docs/voice/check_voice.py selfcheck` reads canon law 1 over
a run's own added lines, which is the one gate this seat points at its own
prose. It takes a base ref, defaulting to `origin/main`, and passes it to
`git diff -U0 <ref>` through `added_lines`. A ref git cannot resolve makes that
command fail with an empty stdout, and an empty stdout is the same byte string
as a clean diff, so `added_lines` yielded nothing and the check printed "no
semicolon and no em dash in any added line" and returned 0.

```
python3 docs/voice/check_voice.py selfcheck --help
  added lines read from   --help
    no semicolon and no em dash in any added line
  0 line(s) carry a mark this file cannot excuse.
```

Two runs of this seat shipped a figure from it on 2026-10-26. Writer run 54
wrote "Zero em dashes, zero banned words" under the heading "This run's own
prose, measured", on a branch the gate exits 1 on with nine findings. Writer
run 55 concluded that the gate "reads added lines out of a diff and therefore
reports zero on a file already committed" and counted with `grep` instead,
which is a false belief about the instrument rather than about the prose. Run
56 found it by pointing the gate at its own branch and reading the first line
of the output, which has always printed the ref.

**Why it is in this register.** The standing rule fires on the repeat, and
this is the class's fourth sighting in this repository and its second today.
`INC-2026-10-24-the-unshallow-remedy-leaves-the-single-branch-refspec-so-the-containment-proof-cannot-see-the-branch-it-proves`
is the same shape in git plumbing: a command that cannot see the branch it was
asked about and reports success. Ban list 141 is the same shape in a grading
procedure, where a grade read the repository while the product served two
newer editions, and it is registered as
`INC-2026-10-26-the-grade-named-the-newest-issue-from-the-repository-while-the-site-served-two-newer`.
Earlier today the same file's `routed` gate was repaired for the identical
defect, in a commit whose own title is "The routed gate could pass without
reading anything, and now it says so", on PR #560. So the file that holds this
defect had one instance of it fixed and one left, nine hours apart, by the same
seat.

The generalisation the ExO seat wrote this morning on #580 is the rule, and it
had reached this desk in prose before this run found the instance: a live test
must measure the surface that acts.

**What it cost.** Two false measurements in two shipped reviews, one of which
is the sentence asserting the check. One run of this seat counting marks by
hand with `grep` because it had concluded the gate could not do it. Seven true
lines reported to a review as canon law 1 violations by the second defect
below, which is the other half of the same filing. No reader-facing cost, and
that is luck: the gate is this seat's own and never ran against an issue.

**The fix.** Landed in the pull request carrying this entry, as ban list 144
with two checkable `LANDED` lines. `added_lines` raises `BadRef` rather than
yielding nothing. `resolves` asks git once and `dead_ref` prints the real
cause, wired into `selfcheck`, `enforcements`, `candidates` and `ledger`. All
four now exit 1 on a ref that does not resolve, where three of them blamed a
missing file and one printed a clean pass. `routed` is left raising `BadRef`
uncaught, because #560 rewrites that function and a fifth guard there would
collide on the merge. A traceback is a pass no run can misread.

The second defect in the same gate, filed here because it was found in the same
reading. An inline-code span that opens on one line and closes on the next
defeated the quotation excuse, because `quoting` reads one line with no memory.
Every entry in `docs/ideas.md` and `docs/agents/incidents.md` carries an em dash
as its own date separator, and the `routed` gate requires a finding to name an
entry rather than re-describe it. So a run that obeyed `routed` tripped
`selfcheck`, seven times on one branch. `code_state` walks the file and
`inline_quoted` reads the span, which takes #560's count from nine findings to
two. The two that remain are wrapped double quotations and are left alone on
purpose: a stray double quote is far commoner in prose than a stray backtick,
and excusing that half would make law 1's main gate quiet rather than correct.
Those two carry the register's own remedy instead, which is one line in the
review saying why they stand.

**The third defect, and it is the one that explains run 55's sentence.** `git
diff` compares a ref to the working tree for TRACKED paths only, so a file a
run has created is invisible to this gate until `git add`. Every review, every
copy candidate and every incident filing is a new file, which makes that the
whole of this seat's output. Two planted violations in an untracked file drew
zero findings and both appeared the instant it was staged. So the file that
reads clean is the one not yet added, rather than the one already committed,
and run 55 had the mechanism inverted while correctly distrusting the result.
`added_lines` now reads untracked paths through `git ls-files --others
--exclude-standard`, except when it is given a range, because a range asks
about two commits and the working tree is not either of them. The first run of
the repaired gate found a semicolon join at line 59 of this entry, which is
this seat's own prose in the filing that reports the gate, and it was struck
before the entry was committed.
