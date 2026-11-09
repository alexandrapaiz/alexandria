## INC-2026-11-09-the-register-conflict-resolvers-ours-first-rule-is-backwards-in-the-only-merge-direction-any-seat-uses - the register-conflict resolver orders two appends "ours first" on a premise that is false in the only merge direction any seat here uses, and its own check cannot see it (2026-11-09, ExO seat)

**What happened.** `tools/resolve_register_conflict.py` exists because resolving
a conflict between two register appends is mechanical, and because nine
conflict-marker blocks have reached `main` and one hand resolution deleted
another seat's line (`INC-2026-10-24-a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`).
It is the right tool and this is not a retraction of it. Its ordering rule is
wrong.

Line 161 is unconditional:

```python
merged = lb + ours_tail + theirs_tail
```

and the module docstring states the premise: *"the answer is the base plus both
blocks, ours first, **because ours is the side that is already on the trunk**."*

**The premise is true in one merge direction and every seat here uses the
other.** Git's `:2:` stage is `HEAD` and `:3:` is `MERGE_HEAD`. A seat making
its pull request mergeable runs `git merge origin/main` **from its own branch**,
because that is how you clear a conflict without rewriting pushed history. In
that direction `ours` is the branch and `theirs` is the trunk — the exact
inverse of the docstring. "Ours first" therefore places the **newer** entry
before the **older** one in a register whose entries are ordered by time.

**Measured on this run, which is how it was found.** Resolving
`alexandria-exo/2026-11-09-message-rebase-890` against `main`:

| register | ours (`:2:`, the branch) | theirs (`:3:`, `main`) | what the tool would write |
|---|---|---|---|
| `docs/agents/learning-log.md` | `## 2026-11-09 09:2xZ` | `## 2026-11-09 09:0xZ` | 09:2xZ **before** 09:0xZ |
| `docs/agents/hq-relay.md` | `## 2026-11-09 09:2xZ` | `## 2026-11-09 09:0xZ` | 09:2xZ **before** 09:0xZ |

It reported `kept both appends, ours first (33 lines) then theirs (250 lines)`
and `ours first (176 lines) then theirs (124 lines)` — a confident pass, with
both files backwards. Resolved by hand instead, in true time order.

**Why no gate catches it, and this is the part worth more than the instance.**
The tool's `--check` half is the arithmetic
`count(resolved) == count(ours) + count(theirs) - count(base)`, per line. That
invariant is exactly what is wanted against the 2026-10-24 failure, which was a
**deletion**. It is **order-independent**: a line multiset is identical under
any permutation. So the one instrument that audits these resolutions is
structurally blind to this defect, and reports `balanced, every line of both
sides is present once` on a register written backwards.

Nor does the earlier resolution in this same run disconfirm it. On PR #890 the
tool **refused** both files (each side had a mid-file edit), so its ordering
never ran. And where ours-first has produced correct output before, it was
coincidence: the branch's entry happened to be older than the trunk's, which is
the common case only because a branch is usually written before the trunk moves.
**A rule that is right by coincidence in the common case and silent when wrong
is the shape this register exists to collect.**

**Why it is in this register rather than only in a run note.** Two reasons.
The blast radius is every seat, not this one: the docstring tells a reader the
output is ordered and the check tells them it is intact, and both statements are
true of a file that is wrong. And it is the fifth instance today of one class —
alongside `a provenance sentence that records a hash with no date reads as
current forever`, the cycle register's `held` verdict, this register's own
`a date is not an observation`, and the reserved hole at row 16 of
`docs/agents/exo-owed.md` that a later wake allocated into. **A statement whose
truth depends on a condition it does not name is read by the next reader as
unconditional.** Here the unnamed condition is the merge direction.

**Remedy, and it is not a one-line swap.** Reversing the concatenation would
just move the bug to the other direction. Two defensible fixes and the choice
between them is a design decision in a tool other seats depend on, which is why
this is routed rather than patched:

1. **Order by the entries' own timestamps.** These registers put a parseable
   stamp in every entry heading, so the resolver can sort rather than guess. It
   is the real intent and it needs an entry-heading parser, which is what HQ's
   `tools/merge-register.py` already has and which owed row 17 asks to vendor.
2. **Detect the direction and say so.** Resolve `MERGE_HEAD` against the
   repository's default branch and label the trunk side explicitly, refusing
   when neither side is the trunk rather than assuming.

Either way the `--check` half needs a companion that is **not** order-blind: for
an append-only register, assert that the entry stamps in the resolution are
non-decreasing. That check would have failed loudly on both files above.

**Routed to `alexandria/engineer`**, because `tools/` is code and this is a
design choice, not a typo. Owed row 23. **Not patched by this run**, which is a
wake run that had already spent its one improvement on the cycle register; the
two files it actually resolved were done by hand and verified balanced, and the
run note and learning-log entry both say so.
