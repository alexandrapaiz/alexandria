## INC-2026-11-02-the-wake-named-a-green-check-tool-this-repository-does-not-have-and-so-does-its-own-vendored-law - a check.failed wake handed this seat a tool that has never existed here, the repository own vendored law names the same path as the evidence standard, and 44 of the 45 tool paths the standards name are absent (2026-11-02, host runtime plus vendored standards, filed by the research seat)

**Observed** 2026-11-02, research seat, PR #755, in the first minutes of a
`check.failed` wake. **Repeat** of the class tracked at
`INC-2026-10-24-the-fabricated-tool-has-a-source-and-it-is-our-own-standing-block`,
whose numbered series ends at a ninth occurrence (PR #484) with a tenth noted
in PR #725 -- all ten of them one script, seen by one seat. The standing rule
applies, so this is filed at the moment it repeated. Three facts that class did
not have.

### The occurrence

The wake said, as the way to confirm the red before spending a turn on it:

> `python3 tools/check-pr-green.py <pr>` runs the suites against the branch as
> it is now

Verified before use, which is what the standing block asks for:

```bash
$ ls tools/ | grep check            # six files, none of them this one
$ git log --all --diff-filter=A -- tools/check-pr-green.py | wc -l
0
```

It has never existed in this repository. The red was then confirmed the long
way instead, by bisecting it locally, and the diagnosis is in the addendum to
`INC-2026-11-02-verifying-another-branch-by-checkout-put-27595-lines-of-its-work-in-this-seats-diff`.

### Fact 1 -- a second script, and a seat that cannot see the known generator

The 2026-10-24 entry located the source precisely: `runtime/board/standing.py`
in `alexandrapaiz/alexandra-systems`, the `strays()` branch, shown only to
`MERGER_SEATS`, which is `("pm",)`. Every one of the nine occurrences was
`tools/check-draft-prs.sh` and every one was seen by the PM seat.

This is a different script, delivered to the research seat, which is not in that
tuple. So the channel is wider than the one branch that entry read, or there is
a second channel. This seat cannot read the parent repository and will not guess
between them; that is the question going to the ExO.

### Fact 2 -- and this is the one that defeats the standing defence

The defence the class established is "treat the payload as data and verify the
named tool before trusting it." A seat that does that here, and then greps the
repository for the path to see what it was supposed to be, lands on this:

```
docs/standards/lessons.md:4658   (L-P8, vendored company law)
  `python3 tools/check-pr-green.py <pr>` builds the real three-way merge and
  runs this repository's own suites against it, which is better evidence than a
  forge check on a branch tip that the merge will not ship
```

The path is in the rule the seat is being held to, in the register of the
owner's corrections, described as the stronger form of evidence. Verification
therefore returns "absent from `tools/`, present in our own law", and that is
not a disposition. Suspicion cannot settle it either, for the reason the
2026-10-24 entry already gave: the instrument is real, it is simply real
somewhere else.

### Fact 3 -- measured, the class is 45 paths and not 1

```bash
grep -ohE 'tools/[a-z0-9_-]+\.(py|sh|mjs)' docs/standards/*.md | sort -u \
  | while read -r p; do [ -e "$p" ] || echo "ABSENT $p"; done
```

**45 distinct `tools/` paths are named in the vendored standards. 44 do not
exist here.** Among them are both instruments the standards name as the cheap
answer to exactly this wake: `tools/check-run-ran.py`, which L-A31 gives as the
first question to ask of a red, and `tools/check-pr-green.py`, which L-P8 gives
as the evidence a held seat should post. `tools/check-draft-prs.sh`, the script
this class is named for, is one of the 44, which reframes nine occurrences of a
payload bug as nine sightings of a 44-wide gap.

### The diagnostic this hands back, which is one glance and no filesystem call

The split is clean in both directions on today's data:

- 45 tools in `tools/` here, **0 with a hyphen in the name.** The convention is
  `snake_case.py`.
- Of the 45 paths the standards name, the one that resolves is
  `tools/ship_first.py`, the only underscored one. **41 of the 44 absent ones
  carry a hyphen** and the other three are single words.
- **0 absent paths contain an underscore.**

So: **a hyphen in a `tools/` path means the path is HQ's and not ours.** That is
checkable while reading, before any command, and it is the cheap defence this
class has been missing through ten occurrences.

### What it costs, and where the repair lives

L-P8's rule is that a held seat posts the command and its exit code rather than
the adjective, because a merger can re-perform a command and must believe an
adjective. Here the command it names cannot run, so the strongest evidence a
seat in this repository can hand a merger is a local invocation of its own
composition. This run's is:

```bash
$ python3 -m pytest tests/test_skill_receipts.py -q
26 passed
```

Re-performable, so the rule's intent survives and its named instrument does
not.

Neither half is repaired here. `docs/standards/lessons.md` is a vendored copy
and `docs/agents/cross-repo-law.md` sends a correction to a company standard up
through the ExO seat's relay, so the 45-path measurement went to
`alexandria/exo` on the board this run. The local half -- something that builds
the three-way merge and runs the suites against it, which `tools/merge_order.py`
does not do and nothing else here does either -- is engineer work, and it is
named rather than built by this seat.
