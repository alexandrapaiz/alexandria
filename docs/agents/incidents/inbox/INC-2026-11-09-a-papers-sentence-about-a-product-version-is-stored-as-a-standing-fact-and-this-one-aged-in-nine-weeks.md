## INC-2026-11-09-a-papers-sentence-about-a-product-version-is-stored-as-a-standing-fact-and-this-one-aged-in-nine-weeks - L-R1's class in a new shape: the live check was run on the feeds and never on the claim (2026-11-09, research seat, message run on skill's v7 done)

**Repeat of the class L-R1 in `docs/standards/lessons.md` names, which is
alexandria incident 19: a fact about the live world that no seat checked
against the live world.** The prior instances were events the corpus never
ingested. This one is different in shape and that is why it is written down:
the corpus did ingest the paper, read it in full, quoted it accurately, and
carried a sentence about a vendor's release history as though it were a
property of the mechanism.

**What happened.** `arxiv:2609.21081` reports OpenClaw 2026.2.23 as affected
and 2026.2.24 as fixed, 3/3 each way, and its section 3.3 dismisses a later
May-boundary advisory as "substantively the same shell-wrapper mismatch,"
saying so carefully and labelling the dismissal "our evidence-led
reconciliation, not a formal vendor or GitHub merge decision."
`agent-approval-paths` v7 then carries the sentence that 2026.2.24 "is the only
released fix for any positive in any of the three namings."

Five minutes of advisory reading this run found three distinct advisories in
that family with three distinct patched versions:
GHSA-q399-23r3-hfx4 (PATH-token executable identity, affected <= 2026.2.26,
patched 2026.3.1), GHSA-rw39-5899-8mxp (approval displays the extracted
payload and not the executed argv, patched 2026.3.11) and
GHSA-2j8v-hwgc-x698 (approve one resolved argv shape and rebuild another,
affected <= 2026.5.16, patched 2026.5.18), with four more listed in the
product's index. **2026.2.24, the release the corpus holds as the fixed one,
is inside the first of those affected ranges.**

**Why it happened.** L-R1 is implemented as a check on feeds and events: what
happened in the world that the corpus should hold. Nothing checks the other
direction, which is whether a claim the corpus already holds is still true of
the world. A paper's statement about product versions is time-stamped on the
day it was written and the corpus stores it with no expiry, and this one aged
in nine weeks. The pipeline cannot notice: a vendor advisory enters no arXiv
category, which is the same gap incident 19 named.

**What this costs.** A skill whose whole subject is approval binding told a
reader that one fix exists for one of three failure classes. The accurate
statement is that the vendor has shipped at least four fixes in six months,
each closing one shape, which changes the advice from "there is no fix" to
"check your version against four advisories." Those are different
instructions.

**Not fixed in this run.** The repair is a watch, not an edit: the advisory
streams for the products this literature names belong in `sources.yaml` as
artifacts with method, since a patch note that says it pins path-token
commands "to canonical executable identity (`realpath`)" is a technique and
not an announcement. That is a `sources.yaml` diff, which is image-baked, and
this seat cannot read the deployed sha to show a proposal there would reach
production. Routed in PR #926 instead, with the three advisory URLs, so the
seat that can deploy can see the whole proposal in one place.
