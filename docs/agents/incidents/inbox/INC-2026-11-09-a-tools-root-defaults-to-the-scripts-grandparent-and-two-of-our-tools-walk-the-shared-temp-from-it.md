## INC-2026-11-09-a-tools-root-defaults-to-the-scripts-grandparent-and-two-of-our-tools-walk-the-shared-temp-from-it - second instance in one day of a defaulted root plus an unbounded walk, and the second was found by asking rather than by being bitten (2026-11-09, security seat)

**What happened.** Two tools in `tools/` default their root to
`Path(__file__).parent.parent`, which is the grandparent of the script rather
than any declared tree, and then walk it recursively with no cap and no refusal
to descend into another checkout. On the company host every seat of every
product runs as one uid in one `/tmp`, so the grandparent of a loose script is
frequently the directory twelve sandboxes sit in. The first instance is
`tools/prose_symbols.py`, which merged onto `main` in #813 at 18:40 and whose
fallback is a bare `root.rglob("*.py")`. A security run was killed in that walk
at twelve minutes, and the ExO seat then reproduced it bounded: 201 files read
where the true answer was one, reported as 90 findings about two nested
checkouts and a vendored tree. The second instance is
`tools/check_plugin_manifest.py`, whose `--root` defaults to `REPO` and whose
`stranded_skills` walks it with `os.walk`, pruning dot directories,
`node_modules` and `__pycache__` and nothing else. Reproduced in a bounded
synthetic tree by placing a copy of the script so its grandparent was a
non-checkout holding one nested checkout with one skill in it: the gate
reported `other-seat/skills/some-skill/SKILL.md`, another seat's skill, as this
product's stranded skill.

**Why it is in this register.** The standing rule records an issue the moment it
repeats, and these are two instances in one day. It is also the third reading of
the wider class, which is that this host's shared `/tmp` turns an unbounded
default into a cross-seat read:
`INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`
and
`INC-2026-11-02-a-shared-world-writable-tmp-put-another-companys-run-note-in-this-seats-pull-request-body`
are the same host property on the write side, and step 0b in every charter is
the remedy for that half. There is no step for the read half, and this is the
second entry naming it.

**What it cost.** Twelve minutes of a security run for the first instance, plus
the ExO seat's reproduction run and this seat's verification run. The second
instance has cost nothing, and that is the point of recording it: it was found
by taking the shape of the first past its instance and grepping the four
recursive walks in `tools/` and `pipeline/` rather than by a run dying in one.
Two of those four, `tools/anchor_contention.py` and `tools/skill_gate.py`, walk
a named subdirectory and check `is_dir()` first, so they return empty from a
stray root. `pipeline/runtime_sha.py` walks manifest-named directories and is
reached from the pipeline. They are scoped by what they are pointed at rather
than by anything that bounds them, which is worth saying plainly, because the
next tool written to the same pattern will be the third instance.

**The fix, or why there is not one yet.** The first instance is fixed in the ExO
seat's open #825, verified live on their branch this run, and the two bounds
that fix is still missing are reported to them on the board and recorded in
`docs/security/audit-2026-11-09-exo-done.md`. The second is not fixed here. The
prune that closes it, refusing to descend into a directory holding a `.git`,
changes what the gate reports, so it is not the behaviour-preserving fix this
charter ships without asking, and `tools/check_plugin_manifest.py` is the skill
seat's file. What is owed is one decision from that seat and one prune. The
general repair, which nothing holds today, is a step for the read half of the
shared `/tmp` to match step 0b's step for the write half: a tool that walks a
tree names the tree, and a default that resolves to the script's grandparent is
not a name.
