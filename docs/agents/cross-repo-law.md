# Cross-repo law — how an HQ decision takes effect in a company that has its own

**Enforced at:** prompts/exo-agent.md §3e, every run, and every seat's
"Check the register before you ship" step for the seats whose surface an
HQ standard touches.

Written by the ExO agent on 2026-09-24, on the owner's order after
incident 23. It answers one question that nothing in this org had an
answer for: when Alexandra Systems decides something and alexandria has
a law about the same subject, which one governs, and who is supposed to
notice.

## The event this comes from

On 2026-09-19 HQ accepted ADR-015 and routed four alexandria seats to
`kimi-k2.7-code`. The change arrived here as commit 609d7cc, a normal
merge into a normal repository. Alexandria's own routing law, in
docs/agents/model-routing.md, says a seat migrates only after a
golden-set comparison passes. No comparison was run, and the reason is
not that anyone overruled the law. The reason is that the decision was
not made in a place where the law was visible, and this repository holds
no seat whose job is to read parent decisions against local ones.

The PM seat then failed both of its runs. The seat did not know its
model had changed. The seat that owns the routing register found out
three days later by reading its own file on schedule. Neither of those
is a performance failure. Both are what a missing rule looks like.

## The four propagation shapes, and which one is dangerous

HQ reaches this repository in four ways, and they are not equally safe.

**1. A vendored standard.** `docs/standards/pm.md` and
`docs/standards/lessons.md` arrive as copies with a header naming the
source commit, marked do-not-edit-here. This shape is good. It is
visible in the tree, it is diffable, its provenance is in the file, and
the standard itself states the deviation route: a deviation belongs in
this product's own decisions file.

**2. An ADR recorded at HQ and referenced here.** ADR-033 is cited in
prompts/pm-agent.md §5 and in a commit message. Alexandria's
docs/decisions.md stops at ADR-32 and says nothing about it. This shape
is survivable and lossy. A reader of this repo's decision log cannot
learn why the PM seat has dispatch authority.

**3. A direct commit to this repo's machinery.** ADR-015 is this shape.
Workflow files changed, four seats changed model, and the only record in
this repository is a commit subject. This is the dangerous shape, and it
is dangerous exactly in proportion to how well the change is made,
because a clean commit that works looks like ordinary maintenance.

**4. A sync PR from the centralizer.** The lessons register arrives this
way. Same properties as shape 1.

The rule below is aimed at shape 3, and it pulls shapes 2 and 3 toward
shape 1.

## The rule

**Parent decisions govern, and they do not take effect silently.**

Alexandria does not get to ignore an HQ decision. The company is one
company and HQ carries the view across products that no single product
has. Precedence is not the problem and inventing a veto here would be
the wrong fix.

What the subsidiary is owed is notice, and notice has a definition:

1. **An HQ decision that changes anything inside this repository lands
   with a record in this repository.** For a standard, that is the
   vendored copy, which already works. For anything else, it is one
   entry in `docs/decisions.md` naming the HQ ADR, the local files it
   changes, and the local law it touches or overrides. A commit subject
   is not a record, because nothing reads commit subjects.

2. **Where a parent decision overrides a local law, the local law says
   so, in the local law's own file.** Not in a changelog, not in the
   commit. If ADR-015 had added one line to model-routing.md reading
   "four seats are exempted from the golden-set gate by HQ ADR-015," the
   ExO seat would have seen the exemption the first time it opened the
   register, which is the thing it is scheduled to do.

3. **A local law's preconditions survive the override unless the
   override names them.** Alexandria's routing law has a safety clause,
   the golden-set comparison, which exists because of incident 9. HQ
   decided the direction, which is open routing, and the direction is
   the owner's stated one from 2026-09-17. HQ did not decide that the
   gate should be skipped, and nothing suggests it meant to. So the
   default is that the gate still applies to the parent's change.
   Overriding a safety clause is allowed and it has to be explicit,
   because a clause that can be dropped by not mentioning it is not a
   clause.

4. **The seats whose behaviour changes are told, in their charter or in
   a file their charter reads.** The four routed seats had no way to
   know. A seat that cannot see its own configuration cannot report on
   it, which is why the failure took a weekly audit to find.

5. **The relay runs both ways.** When a subsidiary's incident is
   evidence about a parent decision, it goes back up. The chair is the
   relay while no automated channel exists, and the outbox is
   `docs/agents/hq-relay.md`. HQ's own seats failed the same way in the
   same week, so the evidence was available twice over and travelled
   neither direction until this run.

## What this seat does about it, every run

Added to prompts/exo-agent.md as §3e. In one pass:

```bash
# HQ-origin changes since the last run, by their own markers
git log --since=<last run> --pretty='%h %s' | grep -iE 'ADR-0[0-9]{2}|HQ|company standard|vendored|centralizer'
# and the vendored copies, against the commit they claim
head -8 docs/standards/*.md
```

For each hit, three questions. Is it recorded in `docs/decisions.md`.
Does it touch a local law, and if so does that law's own file say so.
Do the seats it changes know. Any "no" is a finding for the register and
a line in the relay note, and a "no" on the second question is an
incident rather than a finding, because it means a local safety clause
was dropped by silence.

## What this rule is not

It is not a veto and it is not an approval step. Nothing here lets a
seat in this repository refuse an HQ decision or delay one. Every
obligation above is an obligation to write something down where the
seats already look. The cost is a few lines per decision. The thing it
buys is that alexandria's laws stop being invisible to the only body
with the authority to override them.
