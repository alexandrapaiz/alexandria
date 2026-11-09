## INC-2026-11-09-a-pin-list-comment-cites-an-incident-id-that-exists-in-no-register-and-no-gate-reads-a-citation - the register's two gates both pass a citation that points at nothing (2026-11-09, security seat)

**What happened.** This run read `tests/test_ci_coverage.py` while resolving a
merge conflict in it, and the comment that pins
`tests/test_kill_vocabulary.py` and `tests/test_burn_shares.py` ends by filing
its own cost:

```
    # is filed as
    # `INC-2026-11-09-the-coverage-ratchet-is-invisible-on-the-pull-request-that-breaks-it-so-three-of-this-seats-own-merges-passed-it`.
```

That id exists in neither `docs/agents/incidents.md` nor
`docs/agents/incidents/inbox/`. `grep -rn` over the whole tree returns three
hits and all three are citations: that comment, and two files this run wrote
after believing it. The incident the comment describes is real and is filed, as
`INC-2026-11-09-the-coverage-ratchet-was-repaired-by-two-pins-and-the-same-seats-next-commit-reopened-it-in-seventy-minutes`,
which carries the same facts under a different slug. So this is a wrong
pointer rather than an unfiled incident, which is the harder of the two to
notice: the entry exists, the reader who follows the citation finds nothing, and
there is no way to tell that case from an entry that was never written.

**What it cost, measured rather than imagined.** One run, which is this one.
The citation was believed and copied into
`docs/security/audit-2026-11-09-accepted-set.md` and into a ledger entry before
anything checked it, and it was checked only because `python3
tools/incidents.py prior` was run for an unrelated reason and the slug did not
come back. Both copies are corrected in this pull request. A seat that cites a
citation is the mechanism by which one wrong pointer becomes three, and two of
the three were a minute old.

**Why it is in this register.** Not a repeat. `tools/incidents.py prior` over
669 entries returns nothing above 0.611, and the closest match is incident 29,
which is about how ids are allocated rather than whether a cited id resolves.
This is the first filing of the class.

**The gap, and it is the registers rule's own shape.** The register has both
gates the rule asks for. `tools/incidents.py check` decides something is well
formed, and it passed this tree: "375 entries in the register, 282 waiting in
the inbox, nothing malformed." `tools/check_registers.py` decides the registers
are shaped the way their contract says. **Neither one reads a citation.** Both
gates look at the register from the inside, and a dangling citation is a defect
of the text pointing in. The population is large: every charter, run note,
report, ledger entry, docstring and test comment in this repository that names
an `INC-` id, and nothing has ever asked whether the id is there.

**The fix, and it is one predicate.** Collect every `INC-[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+`
and every bare `incident <n>` in the tree, resolve each against the register
and its inbox, and fail on the ones that resolve to nothing. It belongs beside
`tools/incidents.py check` because that is the command every seat's ship step
already runs, so the gate costs a seat nothing new. It is not written here
because this seat's charter sends work this size to the engineer through the
ledger rather than shipping it inside an audit run, and because the predicate
has one judgement call worth a reader: an id cited inside a code fence or a
quoted failure message may be quoting somebody else's wrong citation on
purpose, which this entry itself does twice. Filed at
`docs/ideas/inbox/2026-11-09-no-gate-asks-whether-a-cited-incident-id-resolves.md`.

**The generalization worth carrying.** A register with an inbox, a well-formedness
gate and a ship-step check still cannot tell you that the thing pointing at it is
pointing at nothing. Every gate this register has is a gate on the register.
The citations are the other half of the graph and they are ungated, which means
the register's own reliability is bounded by prose nobody checks.
