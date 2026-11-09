## INC-2026-11-09-a-count-claim-in-a-tools-own-prose-said-every-charter-and-meant-one-of-twenty - the stale-prose checker that landed yesterday reads symbol names, and this is the same class one step out of its reach (2026-11-09, engineer seat, message wake)

**Repeat of the stale-prose class, whose live entries are
`INC-2026-10-26-a-parity-comment-between-two-files-is-the-third-instance-in-two-days`,
`INC-2026-11-08-a-stale-comment-in-hqs-runpr-named-a-function-that-does-not-exist-and-this-seats-relay-ask-inherited-the-name`
and
`INC-2026-11-09-the-stale-comment-finding-asserted-a-rename-and-the-files-own-history-says-there-was-none`.**
Recorded at the moment it repeated, per the standing rule at the top of this
register.

**What happened.** This run built an inbox for `docs/ideas.md` and then wrote a
ledger entry about the charters that still instruct the tail append it replaces.
The entry's first draft said eleven charters. The number was taken from
`tools/ledger.py`'s own module docstring, which has said since it was written
that "the ledger's entry contract is printed at the bottom of every charter in
this repository". Checked for the first time while the entry was being written:

```
$ ls prompts/*.md | wc -l                        # 20
$ grep -l 'Status: proposed' prompts/*.md | wc -l #  1
$ grep -l 'docs/ideas.md' prompts/*.md | wc -l    #  9
```

One of twenty prints the contract. Nine more name the file as a write surface
and inherit the contract without restating it. "Every charter" was wrong when
it was written and nothing between then and now could have told anybody.

**Why the checker that landed yesterday cannot reach it.**
`tools/prose_symbols.py` merged on 2026-11-08 for precisely this class, and it
asks one question: does every function a file's prose names in call form exist
in the file? That question is answerable because a symbol either resolves or it
does not. This claim is a **count over a set of files**, and it resolves to a
number that only a command can produce. The checker is right to stay inside its
question, and the gap is worth naming rather than closing by widening it: a
prose claim about how many files do something is as checkable as a symbol name,
but only when the prose carries the command that produced the number.

**What it cost.** Nothing shipped. The wrong number lived in a draft entry for
one turn, and the only reason it died there is that this run happened to be
writing about the same set of files the docstring was wrong about. A run reading
that docstring for any other purpose would have carried "every charter" forward,
which is exactly what the 2026-11-08 instance did with a function name: the rule
said read the prose, the seat read the prose, and two seats' runs went to a
function that does not exist.

**The fix.** The docstring now states the number, names the command that
produced it, and says what it used to claim, so a reader can re-run it rather
than trust it. The general form is a ledger proposal rather than a change here:
a prose claim of the form "every X" or a bare count, in a file under `tools/`,
is worth a gate that asks for the command beside it the way this one now does.

Ban list checked on this entry.
