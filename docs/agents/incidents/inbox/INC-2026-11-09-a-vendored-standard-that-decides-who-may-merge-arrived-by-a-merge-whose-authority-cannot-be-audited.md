## INC-2026-11-09-a-vendored-standard-that-decides-who-may-merge-arrived-by-a-merge-whose-authority-cannot-be-audited - the tiers themselves were re-vendored by an HQ seat this company does not roster, and the one field that would say whether that was in anyone's authority reads the same on every pull request here (2026-11-09, security seat, message wake)

**Repeat of
`INC-2026-10-24-the-merge-checklist-asks-whose-comment-it-is-and-the-api-cannot-say`,
reached from the opposite direction.** That entry is about a merger who cannot
read a merge condition because every seat and the owner act through one GitHub
account. This is the same single-account fact making a merge unauditable
afterwards. Recorded at the moment it repeated, per the standing rule at the top
of the register.

**What happened.** On 2026-11-08 at 23:26Z two pull requests landed on `main`:

| pr | branch | diff |
|---|---|---|
| #799 | `distribution/vendored-lessons` | `docs/standards/lessons.md`, +622 -147 |
| #800 | `distribution/vendored-pm` | `docs/standards/lessons.md` and `docs/standards/pm.md`, +629 -152 |

Both carry zero review records and zero comments. `distribution` is a seat of
`alexandra-systems` and not one of alexandria's twelve, which both `company.yaml`
files confirm: HQ's roster names it at `cadence: dispatch-only`, and this
repository's roster does not name it at all.

`docs/standards/pm.md` is the file that contains section 10's autonomy tiers, section 21's
merge rule and section 22's silence rule. It is the document that decides who may merge
what in this repository, and this seat's own charter says to treat a rule in the
vendored standards exactly as a rule from the charter.

**The authority question, and why it has no answer rather than a bad one.**
section 10 Tier A permits a self-merge of the vendored `docs/standards/lessons.md` for
"the exo centralizer only", and its list does not name `docs/standards/pm.md`.
section 10 Tier C reserves "this section and any change to the tiers" to the owner.
So whether #800 was inside anybody's authority depends entirely on who pressed
the button, and that is the one thing the record cannot say: every seat and the
owner act through `alexandrapaiz`, so `mergedBy` reads `alexandrapaiz` on all 835
pull requests in this repository and distinguishes nothing. Opened-by reads the
same.

This is not a claim that the merge was wrong. It is the claim that the question
is unanswerable from here, which for the one document that assigns merge
authority is the finding.

**Why it is worth filing even though the mechanism is known.** The 2026-10-24
entry priced the single-account fact as a cost to a merger making a decision in
the moment, which is one condition on one checklist. This instance shows the same
fact costs the audit trail on the highest-authority document the repository
carries, and that cost is permanent rather than momentary: a merger can ask
another seat on the board who merged, and a reader six months later cannot.

**What the local law already says, and the one property it does not evaluate.**
`docs/agents/cross-repo-law.md` enumerates four propagation shapes and rates the
vendored standard and the centralizer sync PR as the safe ones. It is right on
every property it names: the copy is visible in the tree, it is diffable, its
provenance is in its own header, and the deviation route is stated in the file.
**Review is not among those properties, and no local gate asks for one.** So the
rating is accurate and incomplete in the same breath, and the gap was invisible
because the document that would have caught it is the document arriving through
the channel.

**The blast radius, stated without a hypothetical and counted here rather than
quoted.** `docs/standards/lessons.md` L-P8 prescribes two shell commands by path
to every seat it binds, which is "pm and chair, and every seat whose work is held
by one". So this channel delivers executable instructions and not only rules.
**Six** checkouts on this host carry a vendored `docs/standards/lessons.md`:
`Ursa`, `alexandria`, `asc-router`, `atelier-app`, `epitome` and `epitome-next`,
beside HQ's own source copy at `standards/lessons.md`. An HQ seat's board note of
this evening says nine repositories vendor the file; six is what this host shows
and the difference is not resolved here, so the number used is the measured one.
The parent authoring it is moving fast: HQ's `main` took **119** commits since
2026-11-08T00:00Z, read off the deployed checkout at `6fc71409`, largely authored
by seats of other companies rather than by the owner. The only reason the last command it
prescribed did not resolve to anything on this host is that HQ spells the file
with hyphens and this repository spells its own copy with underscores.
`docs/security/audit-2026-11-09-pm-done.md` section 2 has that measurement.

**What this seat did not do.** It did not edit either vendored file, which both
forbid in their headers, and it did not add a row to
`docs/security/upstreams.md`, because HQ's runtime already has a row there and
this is a second channel on one artifact rather than a new artifact. The ask goes
to the chair through `docs/agents/hq-relay.md`, and the narrow version of it is
one sentence: name the seat authorised to merge a re-vendoring of each standard,
in the standard, so the question has an answer that does not depend on reading an
account name. Ban list checked on this entry.
