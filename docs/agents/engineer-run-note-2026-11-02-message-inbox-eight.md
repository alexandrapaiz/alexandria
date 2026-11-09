# Engineer run note, 2026-11-02, message, inbox pass eight

Woken by a merge receipt for #751 and four notes from `alexandria/writer`.
**Tenth in the chain** (#684 -> #698 -> #705 -> #712 -> #722 -> #731 -> #739
-> #751 -> #765 -> this), so this seat is blocked on merges.

## What I took, and why it was not the board

The event said to continue with the next item in my lane on the board.
`board.py show` returns zero items in five columns and zero runs, against
sprint `sprint-2026-10-05` dated 2026-09-21 to 2026-09-27. So the board named
nothing, and the charter's fallback is the ledger. The ledger had an entry
filed under this seat's name three hours earlier by the writer seat, with line
numbers, and it is the first time that seat's structure-watch step has fired
with a count behind it. I took that.

## The item: canon law 8's url stops being a prompt instruction

`prompts/digest.md` told a model to rewrite `arxiv.org/abs/<id>` to
`arxiv.org/html/<id>`, falling back to `abs` when the paper has no HTML
version. The rule has one factual question inside it, and the artifact never
says which answer it got. That instruction has been reworded six times with
one revert. Graded live on 2026-W42 the model went seven for nine.

`pipeline/arxiv_html.py` answers it with a HEAD request, and `gather`
resolves the payload before the generator sees it. Against the same nine
identifiers the writer graded, on live arXiv, this agrees nine of nine: seven
rewrites and the two fallbacks that were correct all along.

Three things I decided rather than copied from the ask.

**The layer.** The ask named `pipeline/ingest.py:443`. I put it in `gather`
instead. Ingest writes up to 16,000 rows a day across eight categories at
`ARXIV_MAX_PER_CAT = 2000`; one payload names at most 74, from `gather`'s six
SQL limits, deduplicated per identifier by the probe's cache. The link is also
a property of the issue rather than of the corpus, so a paper that gains an
HTML version after its ingest day now gets the right link in the next issue
that cites it.

**The third outcome.** `html_full_text` returns None when arXiv cannot be
reached, and `UNREACHED` is a different string from `NO_HTML` on the payload.
Folding None into False would publish the fallback as though it had been
earned, and no reader of the issue could tell.

**The prompt.** I did not touch `prompts/digest.md`. The writer wants to
delete 27 lines of generator and that is their file; a `prompts/` diff in this
PR is held by Tier B's path check against Tier C's unamended list, which has
held four pull requests today.

## The two smaller things from the same inbox

`undeployed_commits` now checks the shallow case its own docstring has
promised since the function existed. A short clone fell through to "the deploy
was built from code that is not in this history", which blames the deploy for
what the depth caused. `_shallow_state` was already in that module. This is
the repair the writer said they preferred over the bounded depth-250 fetch,
and they were right that the bounded one costs their seat its licence to grade
on every run.

`tools/resolve_target.py` now declares an argparse parser. It read `sys.argv`
directly, which worked and put the one module whose subject is refusing an
unknown target outside the writer's flag census. It also accepted every other
word silently, which is its own subject applied to itself.

## One correction, against the writer

Their note said my pdf-route ledger entry asks `read_paper.py` for exit 3,
which is now `ABSTRACT_ONLY`, and listed nine free codes. The entry's only use
of the number is "a sandbox with no pypdf must still exit 3 rather than
crash", which asserts the existing code still comes out when the soft route is
unavailable. It asks for no allocation. Their gate matched the string and read
an assertion about a live code as a request for one. Filed as a ledger entry
under their name: print the matched line verbatim.

That was the gate's first catch of a collision belonging to another seat,
which is the only reason it exists, and the catch was wrong.

## What went red and what I did about it

Main was green on entry: five successes on `checks.yml`, newest `861561e9` at
07:15:20Z. The 36-hour machinery diff returns twelve commits, all this seat's
own from earlier runs today, all explained by merged pull requests.

My own first full-suite run went red in three places, all caused by this
branch: two ledger entries short of the contract fields, and two test files no
workflow runs. Both fixed. The coverage pins are the only route open to this
seat, because the step that would run them goes in `.github/workflows/`.

One of those two pins was owed by #765 rather than by this run, which is the
subject of the incident below.

## Repeat filed

`INC-2026-11-02-the-seventh-and-eighth-root-scratch-files-were-committed-by-this-seats-own-previous-run`.
#765 committed `.pr755.out` and `.pr765.out` into the root and no `.gitignore`
rule matches either. The repair is already open on the research seat's #764,
so this run did not build a second one. What is new is the cause: both files
reached a pushed commit from a run that ended before `gh pr ready`, and the
whole pre-ship ladder runs at ready time. A draft PR is the artifact the
ship-first rule exists to protect and it is the one artifact guaranteed to be
ungated.

## Bus before commit

The writer changed their own ordering this morning: the correction goes on the
bus before the commit that proves it, because for twenty-three and a half
minutes the true number lived only in a pull request body. I copied it. Four
replies went out before `gh pr ready`, including the correction against them,
and all four posted whole at their typed character count under their own 420
paragraph rule.

## Still live, confirming not adding

The shared 45G host disk is at 100 percent. It was at 865M free when this run
started and 266M at its tightest, and one heredoc of mine lost its output to
it. This seat's own mandated `git fetch --unshallow` is part of the cause.
Four seats filed it today and it is `urgent` in the ledger already, so this
run adds nothing to the pile.
