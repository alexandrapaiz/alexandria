# Engineer run note — 2026-10-26, the re-fired scheduled slot

PR #624. Branch `alexandria-engineer/2026-10-27-hook`. Supersedes #617,
depth 1.

## The event, and the two things the payload knew that no predecessor could

The scheduled slot of 2026-10-26T23:06:03Z was refused by the provider before
this seat took a turn, and the host re-fired it after the limit reset at
2026-10-27T00:00:00Z. A cron slot fires once per period, so nothing else would
have run it: the choice was a late daily run or a skipped one. This run is
therefore the periodic daily run for 2026-10-26 rather than a reply to the
wake, and the board carries the refusal as a one-turn run at 23:06:08 with no
pull request behind it.

The second thing is the one that changed the plan. The run at
2026-10-26T21:07:05Z was cut off at turn 60 and nothing has completed for this
seat since. That run is #617, and its branch holds exactly one commit, the
placeholder run note the ship-first rule asks for. Sixty turns of work did not
survive. So this run did not continue that work, because there was none to
continue: it started the same two queued items again, from the inbox and the
ledger rather than from the branch.

Worth saying plainly for the Monday retrospective, because the ship-first rule
is what made this cheap. A run that dies at turn 60 with a draft open costs the
next run one command to find out. The same run with nothing pushed costs it a
rediscovery.

## What was built, and what the measurement changed about it

Item 1 of two, the PM's withdrawal of 20:35Z, queued ahead of the sprint: the
frontmatter parser refuses an unquoted colon instead of accepting it.

The first thing this run did was run the function, and the function does not do
what four separate documents say it does. All four, the skill seat's report,
the PM's withdrawal, the ledger entry that carries the item and the title of
#617, say the parser *truncates*. It does not. `str.partition(":")` keeps
everything after the first colon, so the two broken skills return 983 and 746
characters of description with nothing missing. The conclusion all four drew is
right and the fix all four asked for is the right fix. The mechanism is a guess
rather than a truncation, and that decides the shape of the refusal: a
truncating parser is repaired by reading more of the line, and a guessing
parser is repaired by refusing to answer. Filed as
`INC-2026-10-26-the-defect-mechanism-was-read-out-of-the-code-and-four-documents-carried-it`,
a repeat of the class the previous run of this seat wrote up hours earlier in
its own note.

So the refusal is `frontmatter_problems`, which implements YAML's actual rule
for an unquoted scalar: a colon followed by whitespace, or ending the line,
opens a mapping. The validation that matters is that it needs no dependency and
agrees with the dependency anyway. Over all nine shipped skills it returns
exactly what `yaml.safe_load` returns, nine for nine, and it is asserted in CI
against written cases rather than against an import, because the previous run's
own finding was that the loader-based gate has a skip path which returns the
pass code. A gate that can skip reads as a pass, and PyYAML is declared in
neither requirements file.

## The thing that stopped this being a one-line change

The two skills that carry the defect are on `main`, and the fix for them is a
write into `skills/`, which this seat does not make and the skill seat already
has in flight. A refusal that raises by default is therefore not landable
today, and that is measured rather than argued: with the raise as the default,
23 tests across four files fail over the real library.

So the refusal is the default for every new reader and the seven call sites
that have to keep working pass `strict=False` and each say why, which
`grep -rn 'strict=False' tools/` lists. The two broken skills are held open by
`FRONTMATTER_QUARANTINE`, which is an excuse with a reason, an owning seat and
a date on it, reported by every mode of the gate and blocking none of them.

The quarantine cannot rot in either direction, which is the part worth
reviewing. Past `FRONTMATTER_QUARANTINE_EXPIRES` a still-broken skill blocks
like any other, so forgetting the constant costs a red gate with the slug in
it. And a quarantined skill that has been fixed raises nothing at all, so the
skill seat's merge never turns anything red; the entry is then spent, and the
gate prints the sentence asking for its deletion. Both directions are tests.

## The second item, and why it is on the ledger instead of in the diff

Item 2 was the bare `according to` pattern in the evidence guard, handed off by
the PM at 20:57Z and measured by research at 2% precision on the text it will
see. It is not in this diff and the reason is structural rather than a
judgment about priority. `RELAY_MARKERS` and `relay_markers` do not exist on
`main`. They exist only on #607, this seat's own open pull request from the run
before last, which reads mergeable and clean with the owner's full-suite number
already posted against its tip.

Three options, and the third is the one taken. Merging #607 into this branch
makes a depth-five chain carrying 2,900 lines for one review and throws away
the review already done on it. Pushing a commit onto #607 risks the merge
landing between the push and the read, which puts the commit on a merged branch
where it never reaches `main`. So the run asked the PM on the board to merge
#607 and wrote the fix out in the ledger with the pattern, the three cases
research supplied and the two sibling patterns the same note found, so the next
run applies it in minutes instead of re-deriving it.

## Craft scan

Target was suppression expiry, chosen because today's build needed an excuse
and writing it exposed that the repository's older excuse cannot tell when it
is spent. Two products ship the answer in the language rather than in a lint
config: TypeScript's `@ts-expect-error`, which reports `Unused
'@ts-expect-error' directive.` when the line it covers is clean, and ESLint's
`reportUnusedDisableDirectives`, which defaults to `"warn"` and flags a
suppression no longer needed because the code changed. Both verified against
the vendors' own current documentation rather than from memory.

The stealable thing is not the warning, it is why the warning is safe:
`@ts-expect-error` sits on the line it excuses, so the edit that fixes the
defect and the edit that drops the suppression are the same edit by the same
hand. Ported here, that is keying an excuse to the sha256 of the file it
excuses, which the registrar already computes. What this repository does better
is that an excused problem is still printed, labelled `quarantined` or
`waiting`, where an `eslint-disable-next-line` makes the problem invisible. In
the ledger in full.

## Pipeline and machinery health

- `gh run list --workflow=checks.yml --branch=main`: the five most recent runs
  are all success, newest at 2026-10-26T20:44:24Z on `9c8c5973`. Main is green,
  so no break-fix outranked the day's work.
- Machinery diff, 36 hours, `.github/` and `pipeline/`: five commits, all of
  them this seat's own merged work arriving through reviewed pull requests. The
  two that are runtime changes under `docs/agents/runtime-changes.md`,
  `85866beb` and `f4da8c89`, change the call sizes the daily Kimi draw requests
  and the first is itself the rehearsal guard pinning those numbers to the
  jobs' own constants. Both are explained by #536's description. Nothing owed
  to the owner.
- Modal was checked once and cheaply, as the sprint's note for the engineer
  asks: the CLI is not on this host's PATH, so workspace state could not be
  measured from here and nothing in this run needed it. The sprint's own
  statement, off since 2026-10-23, stands unrefuted rather than reconfirmed.
- Conflict markers: `grep -rn` over `docs/`, `prompts/` and `README.md` prints
  nothing.

## Registers

- `docs/agents/incidents/inbox/`: one entry, above. Written into
  `docs/agents/incidents.md` first and moved before the commit, which is the
  positional collision the inbox exists to prevent and is recorded inside the
  entry.
- `docs/decisions.md`: nothing here implements or contradicts an ADR. ADR-36's
  gate is the surface the change lands on and the change strengthens it in the
  direction the ADR already points.
- `docs/agents/press-rehearsal.md`: declined again, and the reason is the same
  one the sprint gives for the backfill item. It is one Modal function and one
  more `&&` in a deploy command, and the workspace has been off since
  2026-10-23, so built today it would be a specification implemented against
  nothing and verified by reading. Named here so the next run does not
  rediscover the decision.
- `docs/voice/ban-list.md`: the ledger entries and this note were written
  against it.
