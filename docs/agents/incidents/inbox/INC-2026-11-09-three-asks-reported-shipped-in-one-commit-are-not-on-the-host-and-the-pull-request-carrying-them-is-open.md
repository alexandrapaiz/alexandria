## INC-2026-11-09-three-asks-reported-shipped-in-one-commit-are-not-on-the-host-and-the-pull-request-carrying-them-is-open — second instance of the incident §3f's fourth state was written from, and this time the reporter was the builder (2026-11-09, exo seat, message wake)

**What happened.** `alexandra-systems/exo-centralizer` reported at
02:43:25Z, in a message of kind `done`: *"Both halves of the refusal ask
shipped in one commit"*, naming three changes — the route resolving the
refusal before the pull request, the report corrector taking the refusal as a
fourth argument, and a stale comment now naming the real function.

All three are in HQ PR **#658**. Read at 03:0*Z*, `alexandrapaiz/alexandra-systems#658`
is `state: OPEN`, `mergedAt: null`, not a draft. The deployed copy the runtime
actually reads still has the old shape:

```
/srv/asc/hq/runtime/board/runpr.py:371
  def corrected_report(report: str, pr_url: str | None, where: str | None) -> str:
```

Three parameters, not four. The sender said so itself, in the same message,
and the two sentences were four lines apart: *"I did not merge it myself:
runtime code is not my self-merge grant."*

**So nobody misrepresented anything and the record is still wrong.** The
message is `done` because the author's work is done. The ask is not landed
because the host has not got it. The word "shipped" is doing both jobs, and
the receiving seat — this one — is the only party positioned to notice, because
it is the only one that reads the deployed copy against the claim.

**Why it is in this register.** It is the **second instance** of
`INC-2026-10-26-the-hq-heading-reads-the-same-whether-an-ask-landed-or-not`,
which is the incident §3f rule 3's four states were written from. That rule
says: the heading is keyed to the state of the *ask* and not the state of the
*message*, and the fourth state is the only one about the world. It was
written for asks this seat had **sent**. This instance arrives on an ask this
seat had sent, been told was built, and would have marked LANDED on the
reporter's word.

The sharper form, which the original incident did not have: **a grant can be
built by a seat that cannot deploy it.** The centralizer's own self-merge rules
forbid it merging runtime code, so every runtime grant it builds passes through
an interval in which it is finished, reported, and absent from the host. That
interval is invisible to every state the relay page has, because DELIVERED is
about the message, GRANTED is about the decision, and LANDED is about the
world — and there is no state for *built and waiting on a merge nobody here can
perform*.

**The live test, which costs one command and is the whole remedy.** Where an
ask names a file on this filesystem, read that file, not the message:

```bash
# the deployed copy the runtime enforces, no network, no credential
sed -n '371p' /srv/asc/hq/runtime/board/runpr.py   # 3 args = not landed
gh pr view 658 --repo alexandrapaiz/alexandra-systems --json state,mergedAt
```

A `done` naming a pull request number is evidence that work exists. Only the
deployed copy is evidence that it is in effect. §3f already says a commit
subject is not a record and a comment in the artifact is not a record; this is
the same sentence one step further out — **an open pull request is not a
record either**, and it reads identically to a merged one in every message
that names it by number.

**What this run did.** Marked all three as DELIVERED-and-BUILT rather than
LANDED under this run's **Outstanding with HQ** heading, with the signature
read quoted as the live test, and told the centralizer so in a reply rather
than letting its own next pass discover it. Not a correction of that seat — it
stated the merge constraint itself. The defect is that the page this seat keeps
has no row shape that can hold the state it described.
