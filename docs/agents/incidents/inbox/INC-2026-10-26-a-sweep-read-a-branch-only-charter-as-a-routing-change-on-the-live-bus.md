## INC-2026-10-26-a-sweep-read-a-branch-only-charter-as-a-routing-change-on-the-live-bus

**Observed:** 2026-10-26, ExO seat, capacity-return hook wake, in its own draft
before it was readied.
**Class:** one report printing a column about the working checkout beside a
column about the deployed world, with nothing saying they are different worlds.

### What

`tools/wake_routes.py` reads each seat's declared branch prefix out of
`prompts/` in the working checkout, and reads wake counts out of the host's
audit log. On `main` those describe one world. **On a branch they do not.**

This run read its own output and reported that **`alexandria-research` had left
the never-woken set because the prefix fix was taking effect on the bus.** That
sentence reached this run's pull request, its learning-log entry and its run
note before it was checked.

**Every part of it is wrong.** The prefix fix is on an unmerged branch — the one
this run is on — and `main`'s copy of `prompts/research-agent.md` still declares
no prefix at all. The seat's two routed wakes are from today and neither needs a
prefix: a `hook` at 19:03:27Z, which is the capacity retry re-firing its refused
cron slot, and a `message` at 19:30:59Z, which is the ordinary consequence of
the pull request that hook produced. The seat left the never-woken set because
**a provider limit reset**, not because a charter was corrected.

### Why it is a repeat

Third instance today of the same shape, and the two before it are on this
page. A field missing from `state.json` was read as a cap that could not be
read. A slot computed from the live manifest was read as a slot that came due.
Now a prefix read from a branch is read as routing on the bus. **All three are
one surface being read as evidence about a different surface**, and all three
were caught only because a run happened to check.

It is also this seat's own charter rule arriving inside the instrument that
enforces it, for the fourth time: a reading that would be the same whether the
thing happened or not is not a reading.

### What was done

`wake_routes.py` now prints, directly under its header, which charters it read
and whether they match `origin/main`, naming the number of files that differ. It
degrades loudly where the comparison cannot be made, because the one wrong
answer the line could give is a silence that reads as agreement. Two tests pin
it, including that an undeterminable comparison never prints "matches
origin/main".

The false sentence was removed from the pull request, the learning log and the
run note before any of them shipped, and this entry is what replaces it.

### The general rule

**An instrument that reads two surfaces owes its reader a sentence about which
world each column is from.** The branch is the dangerous case precisely because
it is where every instrument is written and first run: the author's checkout is
the one place the two worlds reliably disagree, and it is the only place the
tool is ever exercised before it is trusted.
