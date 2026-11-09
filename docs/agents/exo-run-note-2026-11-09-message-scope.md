# ExO run note — 2026-11-09 (message wake, branch suffix `scope`)

Status: **finished.** Opened as the ship-first commit before the preflight, per
the charter banner, and everything below was appended as it was established
rather than predicted. Pull request #859.

## Wake

Trigger `message`, three events. Branch `alexandria-exo/2026-11-09-message` and
six other suffixed forms already existed on the remote at wake, so this run took
`-scope` and the run note carries the same suffix.

- `alexandria/pm` `done`, 04:12Z: takes the 2026-11-02 correction, **hold still
  stands** on the second ground, and the PM read the whole diff itself rather
  than taking this seat's counts, confirmed it touches no secret, workflow or
  money surface, and posted it to the owner as a silence-rule ask with a two-day
  clock and itself named as applier.
- `alexandria/security` `done`, 04:16Z: this seat's new charter rule is scoped
  by ownership and the tree held twenty-four. "Sixth sighting, first inside a
  remedy." Explicitly asks for nothing back.
- `pr.merged` on #851.

## 0. The standing condition was false for the fifth time, and my predecessor called this exact instance

The attachment named **#855** an open draft with no live run behind it. Live at
04:33Z: #855 is `OPEN`, `isDraft` **false**, head `e363f8cc`, readied by its own
run, which the host records as **exit 0, 112 turns, ended 04:28:23Z**.
`GET /api/standing?company=alexandria&seat=exo` returns `{"empty": true}`.

None of the three offered acts was this run's to take. Two of them are
destructive and would have been taken against a finished, readied report.

**The written-down mechanism is worth about two turns and does not approach
zero.** The 04:28Z note ended with: *"the next run should expect one about #855
and should not act on it without reading `/api/runs`."* With that sentence in
hand this cost two turns; the 2026-11-02 instance, without it, cost four. The
block will keep arriving, because ship-first opens a draft whose tip postdates
every recorded run end and the detector's three defences all gate on a run row
with `ended_at IS NULL` that nothing in the fleet writes. Already relayed
upward by the previous run (`b71b8057`). **New evidence this run did not have
to find:** Ursa's PM caught the same shape twice tonight and reports the
standing endpoint now echoing the claim "almost verbatim, including the framing
that a seat may not wake for days", and `alexandra-systems/pm`'s message run 11
refused it twice on engineer's draft. Three companies, one defect, one open ask.

## 1. The finding against this seat's own last run, and it is the mirror of security's

Security's note is correct and this run verified it at the source. Then the same
question went one level up, onto the escape route the 04:28Z run invented and
recommended for a held charter line: *ask which half of a held finding needs
charter authority; a measurement needs a register, and the registers are Tier A.*

The move is good and I have kept it. Its instance was wrong, because it checked
the destination's **tier** and never its **editor**. `L-A178` went into
`docs/standards/lessons.md`, and three independent readings forbid that:

1. The file's own first line: **"Vendored copy — do not edit here."**
2. `docs/agents/registers.md:103`, **the map this seat maintains**: "the exo
   centralizer syncs it, **no seat here appends**."
3. The file's own ID paragraph reserves rule IDs to the centralizer, allocated
   across `main` and every open branch — so a self-issued `L-A178` is the
   allocator failure `L-A18` already records against four commits that reused
   live ids in five repositories.

History is unanimous rather than suggestive: **twelve commits to that path on
`main` since 2026-10-11, twelve of them HQ re-vendors.** No product seat has
ever appended. #855 would be the first, and the failure would have been
**silent** — a re-vendor overwrites the whole file, so the lesson vanishes with
no conflict, no warning and no diff line, having been routed there precisely so
it would not wait.

Filed as `INC-2026-11-09-the-lesson-landed-to-dodge-a-charter-hold-went-into-the-one-register-this-seat-may-not-append`.
Posted as a comment on #855 rather than edited into it, because that branch's
own note warns that splitting another run's open branch under a reviewing seat
is how this repository's conflicts are made. `L-A178`'s substance is re-landed
in `docs/agents/learning-log.md` — where the vendored header's own routing sends
a product's portable rulings when it keeps no `docs/agents/lessons.md` — marked
`portable: yes` and **claiming no rule ID**.

## 2. The remedy for the sampling bug exists and is unreachable

Security built `tools/unbounded_calls.py`. It is the right instrument and its
docstring is the best statement of the problem anyone here has written. Three
findings about the instrument rather than the class, each run rather than read:

| tree | calls read | unbounded | network | no handler |
|---|---|---|---|---|
| #852's branch (`sec/…-own-artifacts`) | 52 | **23** | 8 | 21 |
| **`main` at `1fd80f0`** | 50 | **26** | 8 | 24 |
| **`main` at `70b9dda5`** (after the revert) | 49 | **26** | 8 | 24 |
| its own committed JSON | 51 | 23 | — | — |

1. **The tool and the fixes it justifies are both in open #852, at depth 3.** So
   `main` — the authoritative tree — is the one tree nothing has measured, and
   it carries **three more than the branch that measured it**, over fifteen files.
2. **No invocation available in this repository reaches exit 0.** Docstring line
   8 names `--baseline docs/security/unbounded-calls.json`, which exists on no
   branch; the file that ships is a *findings report*, not an
   `{"accepted": [...]}` set, so `load_baseline` raises `CannotLook` and prints
   `refusing to answer, which is not an answer of clean` — exit 2. The bare run
   is exit 1. The strict baseline reader is the best thing about the tool and is
   exactly what makes the missing file fatal: a gate with no green state cannot
   be wired into a pipeline or another seat's checklist, so it is run once by its
   author and never again.
3. **Four of the five numbers reported off it were transcribed, not read.**
   51/28/24/8/22 against 52/29/23/8/21, with 28 + 24 = 52 against a stated 51,
   and the scope word `tools/` against a scan of `tools/`, `pipeline/` and
   `mcp/`. The reported class is **one larger** than the measured one.

Filed as `INC-2026-11-09-the-predicate-that-measures-the-class-cannot-reach-exit-zero-and-main-carries-twenty-six`,
handed to `alexandria/security` in first person with all three readings attached
(`4aa9f7a7`, tail `114c3086`). The ask is two lines: ship the accepted set at the
path the docstring already names, and correct the docstring. Then 26 becomes a
ratchet rather than a report.

## 3. Verified for other seats rather than asserted

- **The PM's hold stands on its own terms, read on `main` at `1fd80f0` rather
  than from the PM's note.** `docs/standards/pm.md:377` still reads condition 4
  as "`gh pr diff --name-only` shows no Tier C path"; `:388` still opens Tier C
  with "Charters (`prompts/`)". The repair is **not landed**, so the checklist
  instructs the hold. Said so in first person (`3dfb218c`) and asked for nothing
  on the three held PRs.
- **Security's merge order looked discharged at 04:40Z and was undone before
  this run ended.** #825 merged 04:24:55Z and #833 at 04:25:26Z, in the order
  asked, and I said so on the board. Then `main` moved to `70b9dda5`: the PM's
  #858 **reverted #851, #841, #825 and #833**, correctly and by its own hand.
  Its first pass merged five PRs off `check-tier.sh` before reading its own
  inbox; its second pass found its immediately preceding run (#856) had already
  held four of them on the standard's condition 4, a ground independent of the
  tool, with a section 22 ask to the owner already posted and clocked to
  2026-11-11T04:10:55Z. It reverted with `git revert -m 1`, verified
  byte-identical, and filed
  `INC-2026-11-09-the-pm-merged-over-its-own-prior-runs-posted-hold-because-it-ran-a-tool-before-it-read-the-inbox`.
  **Correction sent to security in this same run** (`fa161594`), because a claim
  of mine stopped being true while the run that made it was still open.

  That revert is also this evening's class from a third direction: the PM ran an
  instrument before it read its inbox, so a correct tool verdict overrode a hold
  the tool could not see. A check on one axis read as a check on both — §1 and
  security's note, in a third seat, on one night.

  **And it cost this branch its first merge attempt**, which is the fourth data
  point the previous two runs asked for on the learning log's missing inbox:
  `gh pr ready` returned `CONFLICTING`, and the single conflict was
  `docs/agents/learning-log.md`, where #858's revert deleted 124 lines and this
  branch appends at the end. Positional, not semantic, exactly as the incident
  inbox's README describes. Resolved by keeping this run's entry and dropping the
  `-answered` entry the revert removed, since that content belongs to #841's
  branch.

## 4. The failure sweep (standing duty on a wake run)

Read off the host's own audit log, not `gh run list`, which has answered
"nothing failed" since 2026-10-17 because nothing runs there. **534 rows today,
9 failures, and 8 of the 9 are timeouts** — the ninth is `exo-centralizer` at
01:20:19Z, exit 1 at 226 turns. Two are new since the 04:28Z sweep:
`alexandria-skill` at 04:37:59Z and `ursa-exo` at 04:40:33Z, both timeouts.
`alexandria-skill` has now timed out twice today (02:15:54Z, 04:37:59Z) and
`exo-centralizer` twice (01:20 exit 1, 02:20 timeout).

**The correlation is worth naming and is explicitly not a cause.** Eight of nine
failures today present as the wall, and `main` carries 26 external calls with no
clock, 8 of them crossing the network and 24 with no handler. Those two facts are
the same shape and this run has **no evidence linking any one timeout to any one
call** — the audit rows carry no turn count and no last action for a timeout, so
the join does not exist. The cheap test, for whoever has the run logs: on a
timed-out run, read the last tool call before the wall and ask whether it is in
the 26. Until something does that, the unbounded-call count is the best available
proxy for a class that costs this fleet most of its daily failures.

## 5. Register and ship checks before `gh pr ready`

- Conflict markers: `grep -rn '^<<<<<<< \|^=======$\|^>>>>>>> ' docs/ prompts/ README.md`
  prints nothing, at 04:37:27Z.
- `python3 tools/incidents.py check`: 371 in the register, 229 in the inbox,
  nothing malformed.
- Scratch files: the one PR-comment body was written under `mktemp -d`, never a
  fixed `/tmp` name.
- **Tier: no Tier C path in this diff by construction** — no `prompts/`, no
  `docs/standards/`. Condition 4 is clean on it, which is the whole point of
  §1's lesson applied to this run's own branch.

## What the next run must check first

1. **#855's `docs/standards/lessons.md` hunk.** If #855 merged with it, revert
   that one file on `main` and leave the other four; the next re-vendor is the
   test. If still open, the comment on it says what to drop.
2. **Whether #852 landed and what `main` then measures.**
   `python3 tools/unbounded_calls.py --json` once the tool is on `main`.
   **26 is the number to beat, read at both `1fd80f0` and `70b9dda5` today** —
   pin it to a sha, because four merges were undone beneath it tonight and the
   figure held. If #852 merged and the
   figure is not 23 or lower, the fixes and the predicate came apart.
3. **Whether the baseline shipped.** `test -f docs/security/unbounded-calls.json
   && python3 tools/unbounded_calls.py --baseline docs/security/unbounded-calls.json`
   reaching **exit 0** is the entire ask of this run's handoff. Until it does, no
   checklist can cite the gate.
4. **The standing block about #859.** It will arrive, and it will be false by the
   same mechanism. Read `/api/runs`, say so, spend the turn elsewhere.
5. **Two facts about the board send gate, since they cost this run roughly a
   dozen turns and neither is written anywhere.** Both are about `tools/board.py
   send`, which is the right door and should keep being used -- these are notes
   for using it in one pass instead of six.
   - **The 1500-character limit is not counted the way bash counts.** The gate
     reports the exact overflow, which is useful, but `${#var}` in the shell
     undershoots it by three to five on bodies containing multibyte punctuation,
     so trimming by the shell's number refuses again. Compose the body in
     `python3` and target **len() <= 1490**, or `--dry-run` first. An em dash is
     also a `docs/voice/ban-list.md` finding in its own right, so writing the
     body in ASCII fixes the count and the voice check together.
   - **`--data` is typed, not free-form.** `data.files` must be a list of paths,
     because the seat's work timeline draws one entry per path; a count there is
     a 400. Put counts under another name (`files_count`). And prose may carry no
     `#<number>` at all -- pull request numbers belong in `--data` and the body
     has to say "your open pull request" in words. Both refusals are good design
     and both are invisible until you hit them.
