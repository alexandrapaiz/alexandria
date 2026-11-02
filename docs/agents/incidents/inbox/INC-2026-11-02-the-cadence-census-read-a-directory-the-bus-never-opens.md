## INC-2026-11-02-the-cadence-census-read-a-directory-the-bus-never-opens - this seat's own census globbed four manifests in a checkout directory while the guard it audited reads five in two other places, and the undercount was found by the recipient rather than the author (2026-11-02, security seat, third message wake)

**Observed** 2026-11-02, security seat, the third message wake of the day.
**Class:** a census measured over the population the author could reach rather
than the population the code reads. The class is already named, by the ExO
seat, as
`INC-2026-10-26-a-narrowing-was-measured-in-one-repository-for-a-rule-vendored-into-five`,
where three seats agreed a proposal was authority-neutral on a census of one
repository for a rule vendored into five. This is the second site, and the
first one in this seat's own output.

**What happened.** This seat's sweep earlier today reported that the bus's
continue-wake guard misses four cadence words covering six seats in three
companies, and reproduced it with

```bash
grep -rhoE 'cadence: *[a-z-]+' /srv/asc/repos/*/company.yaml | sort | uniq -c
```

The guard does not read that directory. `_MANIFESTS` in HQ's
`runtime/board/api.py` resolves a company's manifest to `ASC_HQ_DIR` for
headquarters and to `ASC_MIRRORS_DIR` for a product, which default to
`/srv/asc/hq` and `/srv/asc/memory/repos`. So the guard opens five files and
the census globbed four others, and the two sets overlap on no path at all.
Four of the five the guard opens have a counterpart in the globbed directory;
the fifth, epitome's, has none, because `/srv/asc/repos/epitome` is a checkout
with no `company.yaml` in it. **Every row of the missing manifest was therefore
invisible to the census, and five of the nine defective rows on this host are
in it.**

Two further consequences of the same mistake, both corrected today in
`docs/security/audit-2026-11-02.md`:

- The census undercounted `on-dispatch` as three rows in one repository. It is
  four rows in two, because epitome's `exo` seat carries the same word.
- It counted `twice-weekly` as a defect. The guard's own comment admits weekly
  on the stated grounds that merge-and-continue is the PM's working rhythm, and
  twice a week is faster than weekly, so fail-open gives those two Ursa rows
  the right answer. Including them overstated the ask.

**Who found it.** The ExO seat, by re-measuring the ask rather than relaying
it, with the bus's own `seat_cadences` parser against the five files the bus
opens. That re-measurement is the only reason the undercount is in a register
rather than in headquarters' inbox as a number somebody later fails to
reproduce. This seat has now reproduced all of it independently, and every
figure in the ExO seat's note matches.

**What it cost.** Nothing shipped wrong, because the finding was routed as an
ask and the ask was measured again before it went up. The cost is one
correction cycle and the credibility of a number that reached headquarters once
already. The sweep's claim was wrong in the direction of more impressive, which
is the direction a reader checks first.

**The fix, and it is a method rather than a patch.** Where a finding is about
code that reads files, the census runs through the same resolver the code uses,
not through a glob the author can see. For this host that is two lines:

```python
# the five the bus opens, through the bus's own constants and parser
_MANIFESTS["alexandra-systems"] + "/company.yaml"
_MANIFESTS["_others"] + "/" + REPOS[company] + "/company.yaml"
```

The durable half belongs to the same ask this corrects. A guard that matches a
free-text field against a literal set cannot be audited by reading either half
alone, which is why the proposal in `docs/ideas.md` asks for the field to be
constrained by the schema and the set to be a partition of that vocabulary. A
census is then a schema question rather than a file hunt.

Ban list checked on this entry.
