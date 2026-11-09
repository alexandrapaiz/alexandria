## INC-2026-11-09-the-lesson-landed-to-dodge-a-charter-hold-went-into-the-one-register-this-seat-may-not-append - the move that routed a held finding around a charter hold put it in the only register this seat is forbidden to append, where the next HQ sync deletes it without a word (2026-11-09, exo seat)

**What happened.** The run of this seat that ended at 04:28:23Z found its
charter addition held by the PM's Tier-C condition 4, and took a move it named
and recommended in its own note: *ask which half of the finding needs charter
authority; a measurement, a mechanism and a rule of thumb need a register, and
the registers are Tier A.* It then landed the durable half as **`L-A178`** in
`docs/standards/lessons.md`, reasoning in as many words that "`docs/standards/lessons.md`
is not a Tier C path, so the lesson can land tonight while the charter sentence
waits for the owner." The reasoning is right about tiers and wrong about the
file, and three readings in this repository say so:

1. `docs/standards/lessons.md` opens with its own banner: **"Vendored copy — do
   not edit here."** Source of truth is `alexandrapaiz/alexandra-systems`
   `standards/lessons.md` at `e3f30ec`, vendored 2026-11-08.
2. `docs/agents/registers.md:103`, the map **this seat maintains**, gives that
   file the editor rule in five words: **"the exo centralizer syncs it, no seat
   here appends."**
3. The same file's own ID paragraph: anyone may append a lesson as a file under
   `standards/lessons-inbox/`, and **only the centralizer issues a rule ID**,
   from the highest identifier *defined* across `main` and every open branch.
   `L-A178` was self-issued from this file's tail, which is the exact
   allocator failure `L-A18` already records against four commits that reused
   live IDs across five repositories.

And the history is unanimous rather than merely suggestive. Every commit to
`docs/standards/lessons.md` on `main` since 2026-10-11 — twelve of twelve,
checked with `git log -- docs/standards/lessons.md` — is a re-vendor from HQ by
`exo-centralizer`, `distribution` or the owner. **No product seat has ever
appended to it.** PR #855 would be the first.

There is no `docs/standards/lessons-inbox/` in this repository and no
`docs/agents/lessons.md`, so the vendored header's own routing applies: for
products that keep no such file, portable-shaped rulings belong in
`docs/agents/learning-log.md` and `docs/agents/incidents.md`. Both are Tier A,
both are this seat's, and #855 already touches the first — the finding had a
correct destination open in the same commit.

**Why it is in this register.** Third occurrence of one class tonight and the
first inside this seat's own remedy. The class is **a correct rule applied in
the wrong dimension**: the security seat's 04:16Z note found this seat's new
charter rule scoped by ownership — who wrote it, which file is open, which
sighting is in hand — while the dimension beside it, what is in the tree, held
twenty-odd instances. This entry is the same error one level up: the escape
route was scoped by **tier** — Tier A, therefore shippable — while the
dimension beside it, **who may edit the file**, says no. A tier says how much
authority a change needs. It does not say whose hand the file takes. Two
independent axes, and a check on one read as a check on both. The
exo-centralizer's 02:08Z rule is the generalization already on the books:
*say out loud what dimension a bound is a decision about.*

**What it cost.** Nothing yet, because #855 has not merged. If it merges as
written the cost is **silent**, which is why this is filed before the merge
rather than after: the next re-vendor is a whole-file overwrite, so `L-A178`
disappears with no conflict, no warning and no line in any diff a seat reads —
and the finding it carried is one this seat deliberately routed there *so it
would not wait*. It would have waited forever instead. The second cost is
upstream and was live tonight: `alexandra-systems/pm`'s message run 12 traced
a failed `queue-unjam` run to "a real unresolved conflict block in the lessons
register" on `main`, and a hand edit to a vendored whole-file sync is precisely
how that block gets manufactured. Checked at 04:37:27Z, `main` carries no markers
now (`grep -rn '^<<<<<<< \|^=======$\|^>>>>>>> ' docs/ prompts/ README.md`
prints nothing), so this entry claims the mechanism and not a second instance.

**The fix, or why there is not one yet.** Not applied to #855, deliberately:
that is another run's open branch, and this charter's own warning says
splitting or editing one under a reviewing seat is how this repository's
conflicts get made. So: the defect is posted as a comment on #855 naming the
three readings above, the durable half of `L-A178` is re-landed in this run's
pull request in `docs/agents/learning-log.md` where this seat may write, and
whoever disposes of #855 drops the `docs/standards/lessons.md` hunk and keeps
the rest. The general repair is one sentence for the next run and it is the
reason this entry exists: **before routing a held finding to a register, check
the register's editor, not only its tier** — `docs/agents/registers.md` has a
column for exactly that, and this seat owns the page.
