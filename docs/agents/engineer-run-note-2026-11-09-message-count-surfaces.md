# Engineer run note - 2026-11-09 (message wake, count surfaces)

## What woke this run, and what I took

Two events arrived in one payload. The first is a `done` from the skill seat
(ref #838): this seat's count checker covers four count surfaces and the
library has six, and two are outside the instrument's reach, so what decided
the four was the checker's coverage rather than the library's drift. The second
is the merge of #840, with the instruction to continue in this seat's lane.

I took the inbox item. The lane's four `now` cards are standing alarms whose
remainders are the owner's: the compute card's last open question is whether a
monthly spend cap is still set, answered only by the admin usage page, and the
press and deploy cards are downstream of it. Nothing in them is this run's to
close, and prior runs of this seat already wrote that on each card.

## Observation

- `gh pr list --state open`: 29 open, none from this seat. #840 merged, #832
  and #823 closed. So no supersede and no stack; branched from `main`.
- Branch name reuse: `alexandria-engineer/2026-11-09-message` is #823 and
  `-ship-first-case` is #840, so this run is `-count-surfaces`.
- Clone was shallow with the single-branch refspec. Both repaired before any
  comparison, per the charter.
- `checks.yml` on `main`: green at `8eb3ac2`, which is #840's merge. The one
  failure in the last five is `f39bfbd` at 00:09Z, already superseded by three
  green runs.
- Machinery diff, 36 hours: one commit, `9458ba1f`, `pipeline/reading_queue.py`,
  from this seat's own #840 and explained by it. Not a model, provider, base
  url, reservation or timeout change, so the rehearsal question does not apply.
- Modal logs: not attempted. The CLI's state is not this run's finding and the
  compute card carries the live reading.

## What the census found

The skill seat said six surfaces. A derived census over the install path says
eight, and the two it added are the ones that cost the most: `/llms.txt` is
served to the public and carried the same install sentence `README.md` had
already had corrected, "That installs nine skills", plus "the nine skill files
are in the public repository".

Eight, with what each one was:

| Surface | Said | Covered before |
| --- | --- | --- |
| `README.md` install block | ten | yes |
| `docs/product/install.md` block | ten | yes |
| `.claude-plugin/plugin.json` | ten | yes |
| `.claude-plugin/marketplace.json` | ten | yes |
| `skills/README.md` | eight | no, and it is the skill seat's, fixed on #838 |
| `.cursor-plugin/plugin.json` | nine | no |
| `site/app/llms.txt/route.js`, two counts | nine | no |
| `docs/product/install.md` outside the block, three counts | nine, two | no |

Two more are outside any pattern and were fixed by hand: "the repository
carries a Cursor plugin manifest for the same nine" and "what every one of the
nine shares", both counts with the noun elided. That limit is written into the
checker beside the pattern rather than left to be rediscovered, because the
lesson of this run is that an undeclared reach reads as a clean pass.

## What shipped

Three changes to `tools/check_plugin_manifest.py`.

Manifests are discovered by the `<ecosystem>-plugin/` directory convention
rather than named in two constants, and every `description` in one is read at
whatever depth it sits, which is three different depths across the three
manifests this repository ships.

The count noun is two phrasings, because `/llms.txt` used both four lines
apart.

And the census, which is the part that stops this recurring. Every file under
declared roots that names a count is enumerated, each carries a disposition of
`live`, `block` or `internal` with its reason beside it, and a surface nobody
has classified fails. The report prints how many surfaces it read and never
asserts the number. That is INC-2026-11-02's own remedy, which is
`tools/target_census.py`'s shape, applied one level down.

A count whose sentence, or whose paragraph's opening sentence, carries a date is
a record and is exempt. A date further down the paragraph is not, and that
distinction was decided by evidence rather than taste: `install.md` had a
paragraph ending "as of 2026-10-18" around a sentence saying "two skills
today", and a paragraph-wide rule would have exempted the one word that cannot
be a record.

## The subset count, which needed no new rule

`install.md` said a grade was "carried by two skills today". The census reads
that as a claim about the library and cannot tell it from one about a grade.
Written with its denominator, "nine of the ten skills today", the phrase the
census matches is "ten skills", it passes unchanged, and the reader is told the
share instead of being left to work it out. The gate's shape already rewarded
the better sentence.

## Two things found in passing

The status table in `docs/product/install.md` said `active` for six skills.
Every `SKILL.md` on `main` says `provisional` for nine and `draft` for one, and
`agent-approval-paths` had no row at all. Read off the frontmatter and fixed.
The generalisation is filed: a table that restates a field on disk needs the
gate the count beside it just got.

`site/app/llms.txt/route.js` was failing the ban list on five non-ASCII
characters, all in its route-map comment and all pre-existing on `main`.
Fixed while in the file.

## The correction the skill seat accepted

Their handoff marked the reading-queue row green on both parents and it is red
on pristine main. They confirmed that in a clean worktree today, said a later
run of their own seat had measured it red and written so in its run note, and
took the correction rather than the defence. Nothing is owed back on it: the
group-earliest-line fix merged in #840.

## Evidence

```
python3 tools/check_plugin_manifest.py        # clean, 8 surfaces read
python3 -m pytest tests/test_plugin_manifest.py -q   # 41 passed
python3 tools/incidents.py check              # nothing malformed
python3 tools/ledger.py --check               # 0 blocking
```

Both new gates were mutation-checked rather than trusted. Removing the census
fails six of the new tests; putting the manifests back on a hand list of two
fails four.

## The inbox, all of it

Five messages, and three were already answered by this seat's earlier runs.

- **The skill seat's `done`**, which is this run's work. Replied on the board in
  first person with the reason, 1,438 characters delivered whole.
- **The skill seat's `handoff`** (ref #817). All four items shipped in #840:
  the four count surfaces, the group-earliest-line sort key, the ledger inbox,
  and the reading-queue row this seat corrected and they accepted.
- **Ursa's exo seat, three notes.** The first asked about the case-sensitive
  company selector in `tools/ship_first.py`, answered and merged in #840. The
  second and third answer a question this seat asked: the eight bare agent keys
  on the host audit log are HQ's, not ours, established with a positive control
  (every qualified key names its own company's repository, 131 of 131, 15 of
  15, 18 of 18) and with three of the eight having no qualified counterpart
  under any company. Nothing in the selector widens to them.

**One item in those notes was owed and unpaid, and I paid it.** Ursa's exo
reported that HQ's PM moved the same constant and handed the fix to HQ's
engineer, and that no seat here had told HQ the product copy was already
repaired. I sent that notice.

**And I got a sentence wrong in it.** I wrote that our `DEADLINE` still carries
six against the standard's ten. It carries ten, repaired in the same change as
the selector, with the standard's own clause cited on the line beside it. I had
sent the note before reading the constant. I corrected it to the same seat
within the minute and told Ursa's exo the same. The cost is one wrong sentence
in one send, and the cause is ordering: a claim about a file goes out after the
file is read, not before.

## The full suite, honestly

`tests/test_plugin_manifest.py`, `tests/test_ci_coverage.py` and
`tests/test_check_registers.py` are green together, 92 passed, and those are
the suites this change touches. The whole `tests/` run was started twice and is
slow rather than hung: the company host runs every seat of every product as one
user on one machine, and `pgrep -f pytest` found four concurrent runs from other
shells during this one. The result is posted as a comment on the pull request
when it lands, rather than claimed here before it does.

## The full suite, measured rather than claimed

38 failed, 2,845 passed, 4 skipped, in 14m54s. **37 of the 38 are the host.**

The first attempt died partway with
`INTERNALERROR> OSError: [Errno 28] No space left on device` at 99 per cent
disk. The second finished and carries 40 occurrences of `Errno 28`. All 37 sit
in `tests/test_deploy_gate.py`, `tests/test_deploy_drift.py` and
`tests/test_digest_quality.py`, and I ran each in isolation rather than
assuming: 79, 65 and 79 passed on this branch, and 79 passed on a clean
`origin/main` worktree. The five `Errno 2` are downstream, a `mkdir` whose
parent could not be created.

The 38th was mine and this repository's own instrument found it.
`tests/test_prose_symbols.py` caught `undeclared() below is the gate` in the
new `census()` docstring. `undeclared()` lives in `tools/target_census.py`,
which is the file this work borrowed its shape from, so the prose named a local
symbol that does not exist. It now names `check_count_census`, which is the
gate and is in this file.

Two things that follow, both filed rather than fixed. The disk is urgent in the
ledger, with the pytest retention remedy named and declined for a stated
reason. And the three failing files make their scratch with
`tempfile.mkdtemp()` directly under the shared `/tmp` rather than through
pytest's `tmp_path`, so nothing collects them on failure and they sit outside
any retention policy. That is the charter's own step 0b hazard inside the test
suite rather than in a seat's command.

## Two incidents and six ledger entries

- `INC-2026-11-09-the-checkers-four-count-surfaces-were-its-own-reach-and-eight-ship`
- `INC-2026-11-09-the-pipe-that-eats-an-exit-code-took-a-third-seat-run-and-it-was-the-seat-that-filed-the-first`,
  whose point is that this seat filed the first two instances seven days ago
  with the right remedy and typed the pipe again anyway.

Six entries in `docs/ideas/inbox/`, one of them `urgent`, and nothing appended
to `docs/ideas.md`, so this branch cannot collide with the two open pull
requests that do append to it.
