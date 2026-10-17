# Engineer run note, 2026-10-17 (scheduled)

The day's OODA cycle, with the numbers behind the pull request so they are
in the repository rather than only in a description.

## Observe

**Guard colour first** (charter's gate 0, before the machinery log).
`checks.yml` on `main`: success, newest run 2026-10-16T18:27:09Z on
`c4f2ccd`. Main is green, so there was no red to clear ahead of the sprint.

**Machinery diff, 36 hours, `.github/` and `pipeline/`.** One commit,
`a941a71`, the sources availability check. It merged as #317 with a pull
request behind it and it is this seat's own work from yesterday. No
unexplained runtime change, no missing smoke run, nothing to file.

**Credentials.** None. No Neon, no Groq, no Moonshot, no Modal, no Resend.
Network is available: `example.com`, `huggingface.co` and `arxiv.org` all
answer 200. So anything that needs the database or a provider was out of
reach today, and anything that needs only HTTP was not.

**Pipeline health.** Skipped. The Modal CLI has no token in this run, so
`modal app logs` cannot be read. Recorded rather than guessed.

## Orient: the sprint survey, L-E10

`docs/sprints/sprint-2026-10-12.md` is the newest sprint. Four of its five
items are the engineer's. None of the four was today's work and the table is
why.

| # | Item | State found today |
|---|---|---|
| 1 | Press-send gap | In flight on **#312**, this seat's own message dispatch, still draft |
| 2 | Polar, three products end to end | Shipped: **#285** merged, **#301** merged |
| 3 | Institution backfill, then resend | `pipeline/backfill_institutions.py` exists, **#303** merged the distill fix; the run itself needs Neon, Groq and Modal and this runner has none |
| 4 | Left-Behind Index | Frontend seat, **#306** merged, deliberately unlinked |
| 5 | Same-day quiet-send guardrail | Shipped in `tools/press_watch.py`, and #312 is editing it again |

Closed-PR searches run for the survey: `Polar`, `institutions backfill`,
`press send`, `delivery guardrail quiet send`, `left-behind`. Open list:
#322 (PM), #321 (writer), #315 and #312 (this seat), #272 (ExO).

So the sprint had room, which is the condition the charter's standing
assignment is written against. The fallback order then asks for `accepted`
ledger entries no sprint has picked up, and reading that list is what started
the day's work, because the list was wrong.

## The two things that were wrong

**A status filter over `docs/ideas.md` returns fiction and misses fact.**
The first observation step of this run was a grep for accepted entries. It
returned eleven. Nine entries are accepted. Two of the eleven are prose: one
inside the 2026-09-24 entry about this exact defect, quoting the command, and
one in a chair's note. In the other direction, 62 entries carry no status a
filter can read, 51 of them with no status line at all, and
`tools/check_registers.py` could see 6 of the 62 because it walked status
lines rather than entries.

**A gate measured its own client and called a live feed dead.**
`owasp-genai` was pinned as `MEASURED DEAD` yesterday on an HTTP 403 and put
in front of the owner as one of five sources to retire. It answers 200 with
10 items, newest 8.6 days old, through the transport `pipeline/ingest.py`
actually uses. Full account in
`INC-2026-10-17-a-403-was-recorded-as-a-measured-death-and-the-gate-never-
asked-the-production-client`.

## Measurements taken today

Ledger, `python3 tools/ledger.py --census`, before the day's appends:

| | count |
|---|---|
| dated entries | 551 |
| with a status a filter can read | 489 |
| no status line at all | 51 (30 of them scan notes) |
| empty status line | 5 |
| status outside the vocabulary | 6 |
| headings with no date where an entry belongs | 4 |
| lines of prose a grep mistakes for a verdict | 5 |
| readable entries missing a contract field | 206 |

Feeds, `python3 tools/feed_health.py`, full census in
`docs/evals/2026-10-17-feed-health.json`:

| | 2026-10-16 | 2026-10-17 |
|---|---|---|
| delivering | 48 of 53 | **49 of 53** |
| failing, unrecorded | 0 | 0 |
| failing, pinned for a ruling | 5 | **4** |
| gate exit code | 0 | 0 |

The transport probe behind the fix, all from this process within one minute:

| host | httpx | urllib |
|---|---|---|
| `genai.owasp.org/feed/` | 403, five user agents tried | **200, 208 KB, 10 items** |
| `thesequence.substack.com/feed` | 403 | 403 |
| `www.latent.space/feed` | 200 | 200 |
| `newsletter.pragmaticengineer.com/feed` | 200 | 200 |
| `jack-clark.net/feed/` | 200 | 200 |

## What was not done, and why

- **`docs/ideas.md`'s 62 bad entries were not corrected.** Statuses are the
  owner's and most of these need a judgement about what their author meant.
  The ratchet is the enforceable half: the count may fall and may not rise.
- **The four undated headings were not dated.** Three belong to the skill
  seat. The fourth is this seat's own craft scan from 2026-09-24 and it
  carries no status, so dating it would move one entry from the undated
  count into the statusless count and improve nothing.
- **`docs/market/landscape.md` was not edited** for either of the two
  corrections this run found in it. It is the market seat's surface. Both are
  in the ledger as notes to that seat.
- **`tests/test_ledger.py` runs in no workflow** and is pinned with a reason,
  which is the documented last resort. That pin is filed as an incident
  because it is the eighth in ten days and the first whose test guards a
  blocking gate.
