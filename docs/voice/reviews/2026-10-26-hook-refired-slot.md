# Every gate this seat points at itself reads the artifact, and none of them read the sentence that reaches her

**Writer run 56, 2026-10-26, hook, the 16:00Z scheduled slot refired.** The
provider refused the slot before this seat took a turn and it refired after the
limit reset at 19:00Z. A cron slot fires once per period, so the alternative
was a skipped day rather than a late one.

## The single biggest weakness, plainly

The instruments are the artifact this run graded, because the editions had not
changed and the instruments turned out to be lying.

`docs/voice/check_voice.py selfcheck` is the one gate this seat points at its
own prose. It could not see a file the run had just created, it excused nothing
when handed a base ref git does not know, and it reported a register key quoted
the way another gate demands as a violation of canon law 1. Two runs of this
seat shipped a figure from it today. Writer run 54 wrote "Zero em dashes, zero
banned words" on a branch the gate exits 1 on, and writer run 55 wrote that the
gate "reads added lines out of a diff and therefore reports zero on a file
already committed", which has the mechanism exactly inverted: the file that
reads clean is the one not yet added.

And the wider version of it, which is the finding this run did not go looking
for. Every gate in this seat's shipping step runs against files in
`docs/voice/` and `prompts/`. The owner's ruling of 2026-09-27 says a decision
is named by what it decides and never by its number, and the recorded ruling
names the surfaces: "in everything she reads, Slack bullets, PR opening bullets,
the board". A pull request description is written after the last gate, in a
different tool, and nothing reads it. Three of this seat's last five
descriptions carry a code in prose. Four of them are on #560 and this run wrote
them, ninety minutes before finding them.

## No fourth grade of the same three editions, and the command that says so

The charter's run grades the newest issue. Run 55 declined a fourth reading of
the same editions and this run verified that live rather than taking it on
report:

```
python3 docs/voice/check_voice.py editions
  served by the product     3: 2026-W39, 2026-W40, 2026-W42
  held in the repository    2: 2026-W37, 2026-W39
```

`2026-W42` is the newest edition a reader can open and it is unchanged since
run 51 graded it link by link. `2026-W40` was graded cold by run 54 today,
twenty-one days after it was sent. A fourth reading of the same three texts
would produce a generator patch already sitting in #560's diff, so this run's
editorial work is in the instruments and in the lane, and this section exists
so the next run does not have to guess why.

## The grade, of this seat's own owner-facing prose

Nobody has ever graded this artifact class, which is why it is here.

**The ruling of 2026-09-27, that a decision is named by what it decides. FAIL,
nine times across three descriptions, four of them written by this run.** The
specimen, from #560's description as this run first wrote it: "so per
`docs/standards/pm.md` §21 this does not wait on the owner". A merger reads
that sentence to decide whether three runs of editorial work ship, and it asks
them to hold a section number. The repaired form, now on the PR: "so under the
company's merge standard this is merged by a PM seat or a chair and does not
wait on the owner." The same sentence, and the reader no longer needs the
repository open. Measured:

```
ADR-, L-A, "incident N", "ban list N", section marks, INC- ids
  #560   4   #550   3   #544   2     of 5 writer descriptions
```

All four on #560 are struck and this review's own PR description carries none.
The ruling permits codes inside repository files, where a seat cites one to
prove a judgment already exists, so this review keeps them and the description
does not.

**Plain sentences and no semicolon joins. FAIL once, caught by the repair
itself.** The first run of the repaired gate found a semicolon join at line 59
of the incident entry reporting the gate, which is this seat's own prose inside
the filing about this seat's own prose. Struck before it was committed. That is
the cheapest possible proof that the scope was the defect rather than the
reading.

**Longer undecorated sentences, no colon-led devices. PASS, with one line of
doubt.** Her ruling of 2026-09-29 governs site copy and the register it names
is the house one. This review runs two to four plain sentences a paragraph and
no fragment openings. The doubt is the headings, which are statements rather
than bare nouns, and her bare-noun ruling is about the site's own headings
rather than a review's.

**Codes inside the repository, translated on the way out. PASS here by
construction** and worth stating because it is the rule this run leaned on
hardest. This file names entries and incidents by id freely. Nothing a reader
or the owner opens does.

## The patch, and it is a gate rather than a wording

Three defects in `selfcheck`, all found by pointing it at its own branch.

- **A base ref git cannot resolve** made `git diff` fail with an empty stdout,
  which is the same byte string as a clean diff, so the check printed a clean
  pass and returned 0. `added_lines` now raises and the check reports the real
  cause and exits 1.
- **A file the run had just created** was invisible, because `git diff` reads
  tracked paths only. Every review, every copy candidate and every incident
  filing is a new file, which is the whole of this seat's output. Two planted
  violations in an untracked file drew zero findings and both appeared the
  instant the file was staged. `added_lines` now reads untracked paths, and
  skips them when given a range, because a range asks about two commits and the
  working tree is not either of them.
- **An inline-code span that opens on one line and closes on the next** beat
  the quotation excuse, because `quoting` reads one line with no memory. Every
  entry in `docs/ideas.md` and `docs/agents/incidents.md` carries an em dash as
  its own date separator, and the gate that checks routing requires a finding to
  name an entry rather than re-describe it. So obeying one gate tripped the
  other, seven times on #560. `code_state` walks the file and `inline_quoted`
  reads the span.

Eight cases in `SELFCHECK_CASES` run before any diff is read, in the shape the
file's other detectors already use. Three are real lines off this seat's
branches. Five are the shapes that look like them and have to stay findings: an
em dash in plain prose, an em dash outside a span that opened or closed on the
same line, and a semicolon in plain prose. A reading that excused those would
make this gate quiet rather than correct.

The sweep its own ban-list entry requires. Four checks take a base ref and read
it through `at_ref` or `added_lines`, and both returned the same value for a
path that is absent and a ref that does not exist. `resolves` asks git once and
`dead_ref` prints the cause, wired into `selfcheck`, `enforcements`,
`candidates` and `ledger`. All four exit 1 on a dead ref where three blamed a
missing file and one printed a clean pass.

**The one left alone, named rather than quietly skipped.** `routed` raises
uncaught instead of printing a line. #560 rewrites that function and a fifth
guard there would collide on the merge, and a traceback is a pass no run can
misread. Two of #560's nine findings also stand: both are wrapped double
quotations, and excusing that half would be the wrong trade, because a stray
double quote is far commoner in prose than a stray backtick and law 1's main
gate would go quiet rather than correct. Those two carry the register's own
remedy, which is one line in the review saying why they stand, and that line is
now on #560.

## What this run did that only this seat could do

**#560 was readied.** Three runs of editorial work, runs 52, 53 and 54, sat in
a draft pull request GitHub will merge nowhere. The PM seat found it at 14:30Z,
read the rule correctly and declined, because readying another seat's draft is
that seat's act. Run 55 named doing it as its whole value, wrote the sentence
into a review, and was cut off at turn 73 before performing it. Verified live
before readying rather than read off its report: 2210 pytest pass and 1
skipped, 248 node tests pass, no conflict markers, the branch contains current
`main`, and the red ledger ratchet was staleness that the engineer seat had
already repaired at 10:25Z.

**#584 was closed**, superseded by this run's own pull request, with the
containment proof run before the close.

## Structure watch

Nothing new goes to the engineer from this run. The five rules the generator
states absolutely with no gate before a reader are the semicolon, the em dash,
law 8 twice and law 14's two devices, and all five are already filed from
#560's diff. The charter says a structural fix that failed twice through prompt
changes is proposed rather than worded a third time, and that is where those
sit. `prompts/digest.md` is untouched by this run, deliberately: its live
defects were patched four hours before this run woke and a fourth wording is
the thing this run spent its whole diff arguing against.

One repair is owed and is not this seat's to make. Four writer runs in a row
ended with an unreadied draft. The turn cap explains three of them and run 55
was cut at turn 73, half the cap, by a provider refusal. So the class that
survives a cap raise is that the readying step has to come before the work
rather than after it, and the org rule's own words place it at the end, where a
cut run never arrives. That is a charter edit, charters are not this seat's
writable surface, and it is filed for the seat that reads the incident register
every run.

## Checks

| check | result |
| --- | --- |
| `selfcheck` | clean on this branch, and it can now see the files it is clean about |
| `selfcheck` with a dead ref | exits 1, where it printed a clean pass before |
| `SELFCHECK_CASES` | 8 cases pass, run before any diff is read |
| `enforcements` | entry 144 resolves on three `LANDED` lines, prose-only count 31 to 30 |
| `candidates` | clean, no candidate drafted for a surface awaiting her word |
| `ledger` | exits 1, desk 642 against the contract's 643, unchanged on `main` and already filed |
| `editions` | 3 served, 2 held, no edition newer than `2026-W42` |
| `incidents.py check` | 341 in the register, 14 in the inbox, nothing malformed |
| conflict markers | none in `docs/`, `prompts/`, `README.md` |
| pytest | 2210 pass, 1 skipped |
| node | 248 pass |
| codes in this PR's description | zero |
| `prompts/digest.md` | untouched, and the section above says why |
