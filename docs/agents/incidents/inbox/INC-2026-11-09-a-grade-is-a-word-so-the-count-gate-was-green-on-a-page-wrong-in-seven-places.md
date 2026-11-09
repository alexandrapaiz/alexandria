## INC-2026-11-09-a-grade-is-a-word-so-the-count-gate-was-green-on-a-page-wrong-in-seven-places - the install page's status table drifted for thirteen days with a gate two lines above it passing (2026-11-09, engineer seat)

**What happened.** `docs/product/install.md` carries a table that grades every
skill in the library, and a buyer reads it to decide which skills to lean on.
It said `active` for six of them. Every `SKILL.md` on `main` said
`provisional` for nine and `draft` for one, and `agent-approval-paths` had no
row at all. Seven places wrong on one page, six grades and a missing row.

The count census that shipped in #843 sits two lines above that table and was
green on the same file the whole time, because a count is a number and a status
is a word, and nothing connected a word in a table to a field in front matter.
The table was repaired in #843 and the gate is this run's work.

**The dates, and they are the skill seat's own.** The table was right the day
it was written, 2026-10-18, when six skills did say `active`. The skill seat's
retrofits to the library's eval bar took them down one at a time, six still
`active` on 2026-10-23 and none by 2026-10-27, and the tenth skill landed on
2026-11-02 with no row written. Thirteen days stale on the grades and seven on
the row, every commit in `skills/` and nothing else.

**Why it is in this register.** It is the restated-field class and it is at
least the third live instance.
`INC-2026-11-09-the-checkers-four-count-surfaces-were-its-own-reach-and-eight-ship`
is the same shape with a number in place of a word, eight surfaces of which
four were unread. Before that, `site/app/skills/page.jsx` told visitors the
library held two skills while nine shipped, and no test failed. Every instance
is one fact on disk and a second copy of it in prose, agreeing only on the day
somebody typed the second one.

**What the mechanism adds, and it is the part worth carrying.** The two
earlier instances were one seat's blind spot. This one is a split between two
seats and neither of them could have closed it. The skill seat writes
`status:` in front matter and its write surface is `skills/`,
`prompts/skill-extract.md` and `docs/ideas.md`, so it may not open the page
that restates the field. The engineer seat owns the page and has no reason to
reread ten front matter blocks on a quiet morning. Discipline cannot close
that, because the habit would have to live in a file one of the two seats is
not allowed to open. A gate can, because a gate runs on both surfaces at once
and belongs to neither.

**The repair.** `tools/check_status_tables` in
`tools/check_plugin_manifest.py`, with twelve tests. Tables are found by shape
rather than by path, which is the lesson the same file already carries from its
hand list of two manifests: a header with a `Status` column plus one row whose
first cell is a backticked `skills/` directory. Three disagreements fail,
because all three were live in this one page: a grade that is not the declared
one, a skill on disk with no row, and a row for a skill that is not on disk. A
table under a dated caption is a record and is exempt.

**What is still open.** `skills/README.md` restates the same distribution in
prose, "Nine carry `status: provisional` and `agent-approval-paths` carries
`status: draft`". It is correct today and it is outside a table gate's reach.
Filed in the ledger inbox rather than guessed at here, because a prose claim
about a grade distribution is a different pattern from a table and deserves its
own measurement.
