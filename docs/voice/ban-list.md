# The prose ban list — tells of AI-generated writing

**Enforced at:** prompts/writer-agent.md, grading pass 4, every run, plus the
"check the register before you ship" step. Entries 1 to 50 are checked by
`docs/voice/check_voice.py sweep` and the quoted endings from 51 on by
`docs/voice/check_voice.py enforcements`. Neither command is called by
anything yet (filed in docs/ideas.md, 2026-10-04).

Companion to docs/design/ban-list.md, for words. The writer seat
checks every issue against this list, APPENDS new tells as the
generated-prose aesthetic drifts, and never deletes an entry without
the owner's word. Since her ruling of 2026-09-19 it governs site copy
as well as issues, so a page of the site is read against these tells
exactly as an issue is.

**An entry is not finished when it is written (writer seat, 2026-09-25).**
A tell recorded here has changed nothing by itself. That is L-A9 in
docs/standards/lessons.md, "recording a rule is not enforcing it", and
incident 20 in this repo's own register. So a new entry carries one of two
endings in its own text: the change to prompts/digest.md that now enforces
it, or the ledger entry saying why no prompt change can reach it. Entries 51
and 54 are why this rule exists. Both were appended on 2026-09-24 by the
grade that found them, in the same pull request that patched four other
findings from that grade into the generator, and neither of them reached it.
A tell that only gets written down is a tell the next issue is free to
commit.

**The second ending is quoted, not described (writer seat, 2026-10-04).** Of
the thirty-five entries carrying that ending, one quotes the text that landed
and thirty-four describe it, so checking them is a close reading of the
generator rather than a command, and nothing re-runs a close reading. All
thirty-four are intact today and that is luck, not a gate. So where the change
is a sentence, the ending QUOTES it on its own line, in this exact form:

```
LANDED prompts/digest.md: "the exact text that is now in that file"
```

`docs/voice/check_voice.py enforcements` verifies every such line against the
named file, matching on normalised whitespace because every file in this
register wraps its prose, and exits non-zero when one is gone. Nine entries
carry one as of 2026-10-04 and twenty-nine do not, so the ratio is printed
every run and is meant to climb. Seed the convention on the entries a run
touches rather than backfilling all of them at once, because a LANDED line
asserted without checking the generator is worse than the prose it replaced.
The quote goes on its own line and not loose in the sentence, because the
obvious heuristic does not work: a string quoted near the word "Enforced" is as
often the BANNED specimen as the landed repair, and entry 46 quotes two banned
labels in exactly that position. A check that cannot tell a ban from a fix
reports the ban as a pass. Where the change is a gate rather than a sentence, the ending
names the gate and the step inside it, which is entry 51's own correction of
2026-09-27 promoted from a remark inside one entry to a rule over all of them:
"An enforcement ending has to name the gate the defect would pass through, not
merely a place in the file where the rule is now written down." Entry 92 is why
this paragraph exists.

**An entry that names a class carries a sweep (writer seat, 2026-10-04).** The
endings above are about whether a fix landed. This is about whether it landed
everywhere. An entry is written from the one specimen the artifact happened to
show, and the generator usually holds more. So where an entry's text
generalises, run its own tell over the whole file, print the count in the
review, and fix every hit in the same pull request or say why one stays. Where
the tell is a command, the command goes in the entry. Entry 90 is why, and
entry 89 is the evidence: it named the class, struck its two specimens, and
left three more live where its own one-line grep would have found them.

**Entries 1 to 50 now have their endings in a command, not in their text
(writer seat, 2026-10-09).** Every rule above binds the entry that is being
written. None of them reached backwards, so the fifty entries that predate the
first of them were never asked whether they had landed anywhere, which was
filed in docs/ideas.md on 2026-09-27 as this seat's own work with no dependency
on anyone and went eleven days.
The pass ran on 2026-10-09 and the full per-entry table is in
docs/voice/reviews/2026-10-09.md. The answer: 46 of the 50 were already
enforced in `prompts/digest.md`, three were not and are patched in the same
pull request as this paragraph, and entry 44 is about generators other than
this one and cannot be reached from here at any wording.
Entry 1 is the finding. It is the oldest entry on this register, canon law 2 is
written from it, and it had never reached the generator in any form: not one of
its fifteen words was in that file and neither was the word "buzzword". Entry 2
had no rule either. Entry 11 had one at the heading gate and none at the slot
where a title is written, which is the position L-A23 says decides.
No live specimen of entry 1 exists. The census over the newest stored row and
both published pages came back clean on all fifteen words, so the three issues
this product has sent obeyed a law the machine that wrote them had never been
told, and that is the reason the patch is worth its lines rather than a reason
it is not: the compliance was the model's habit and not a gate.
What the ending IS, for all fifty, is `docs/voice/check_voice.py sweep`. It
maps each entry to the shortest distinctive phrase in the generator that
enforces it and fails when one of them leaves the file. Forty-six of those
endings would have been the same sentence pointing at four places in one file,
and the rule above says why that was the wrong shape: a LANDED line asserted
without checking the generator is worse than the prose it replaced, and the
check is what does the checking. An entry in that range that gains a prose
ending gains a row there too, or the command fails on it.
Three entries carry an ending in their own text as well, below, because theirs
changed today.

**A third ending, for the entry a prompt cannot reach (writer seat,
2026-09-30).** Both endings above are written once and neither of them
runs again. That is enough for an entry the generator can be taught,
because the next issue either commits the tell or does not. It is not
enough for an entry whose fix belongs to another seat, because a ledger
filing is a request and a request has no failing state: it sits at
"proposed", the artifact stays broken, and nothing anywhere turns red.
Entry 64 is the proof. It carries the second ending correctly and
completely, with the incident id beside it, and the false line it
describes was still the second line of the only published issue four
days later.
So an entry of that kind carries the filing and a check. The check is
pass 6 of the canon's grading procedure: the entry is re-verified against
the live artifact by every grade until the artifact is clean, and the
grade prints the check, its output, and how many days the entry has been
open. A standing defect that is still true is a FAIL line in every
review, not a note in one. Where the check can be a command rather than a
reading, the command is filed too, scoped to the published surfaces,
because a grep for a defect's own words over the whole repository fires
on every register that records it (L-A22, and the scoping is the reason
nobody wrote the command earlier).

Entries 30 and 31 were numbered 26 and 27 until 2026-09-20, when two
parallel writer runs were found to have appended at the same numbers.
The text of both is untouched, and only the numerals moved, into the
gap that the same collision had left empty (incident 25).

1. The slop lexicon: delve, landscape, tapestry, realm, pivotal,
   crucial, seamless, robust, leverage (as a verb), unlock, empower,
   supercharge, game-changer, revolutionize, "in the ever-evolving
   world of".
   Enforced 2026-10-09, twenty days after it was written, by the sweep above.
   The generator held nothing against this entry, so the rule is new rather
   than relocated, and it is a question about the word plus a count, because
   the one mark that went to zero in that file was the one that was counted.
   LANDED prompts/digest.md: "catches the word that fills the slot where a fact belongs"
   LANDED prompts/digest.md: "count the words that state nothing, per the law 2 bullet above"
2. Three-adjective lists. One precise adjective, or a number.
   Enforced 2026-10-09, as the last two sentences of entry 1's rule, because
   the stack of adjectives is the same failure spread over three words and a
   rule of its own would have been a second place to forget it.
   LANDED prompts/digest.md: "One precise adjective, or the number the three were standing in for"
3. Symmetric paragraph rhythm: every item the same length, every
   sentence the same shape. Vary or die.
4. The hedge stack: "could potentially", "may possibly", "it's
   important to note". State it or grade it.
5. Empty intensifiers: very, truly, incredibly, remarkably.
6. The fake question opener ("What if agents could...?") and the
   fake dialogue transition ("But here's the thing:").
7. Summaries that restate the headline instead of adding the next
   fact.
8. "Exciting" claimed rather than demonstrated. If the number is
   exciting, the number carries it.
9. Anthropomorphizing papers ("this paper believes").
10. Closing paragraphs that summarize what the reader just read.
    End on the last finding or the standing close, never a recap.
11. Titles with colons where the second half explains the first.
    One finding, one line.
    Enforced 2026-10-09 at the title slot. The ban was already in the file
    twice, over section headings and over item headlines, and the heading gate
    collects the text in front of any colon on any line beginning with `#`,
    which includes the title. What it was missing is the position: the gate
    reads finished output and the slot is where a title gets chosen, and
    L-A23 says the instruction has to be where the writing happens.
    LANDED prompts/digest.md: "And no colon. The shape the mark makes here is a short label"
12. Uniform enthusiasm. If every item is important, none is; the
    ranking must be visible in the prose's energy, not just the
    order.
13. Typesetter punctuation. Non-breaking hyphens (U+2011) inside
    "long-horizon" or "sparse-reward", narrow no-break spaces before a
    percent sign ("28.5 %"), the multiplication sign in "3×". Ordinary
    hyphens and ordinary spaces, always. The reader's search box and
    the agent loading the issue both match on plain ASCII, and neither
    matches on these. Added 2026-09-19 from 2026-W37, which carried 87
    non-breaking hyphens and 19 narrow spaces.
    Amended 2026-09-21, incident 27: the three characters named above are
    examples and the entry is the class, which is every character outside
    plain ASCII. The same issue also carries 12 en dashes, 5 curly
    apostrophes, 3 multiplication signs, 2 bullet separators and a Greek
    capital inside a system name, and none of those are a hyphen or a
    space, so a check written from the words above passes all five. The
    exception is a person's or an institution's name as the source spells
    it. Punctuation, spacing, separators and symbols have none.
14. Internal vocabulary printed at the reader. "(3 supports)" is a
    count of edges in alexandria's claim graph, not a fact about the
    research, and no subscriber can decode it. Say what the number
    means in plain words. The same goes for triage scores, tiers,
    claim ids, and the ISO week code.
    Amended 2026-09-22: those five are evidence and the entry is the
    question, which is whether a subscriber who has never seen the
    codebase could say what the word refers to. 2026-W37 closes on
    "3558 papers ingested", and "ingested" is the pipeline's word for
    read. It is not a score, a tier, an id or a week code, so a check
    written from the list above passes it, and the reader still meets a
    word from a codebase they have no access to.
15. The complete dump in place of a judged selection. A section that
    prints every row the query returned has outsourced the editing to
    the database. Nine "read these yourself" entries is a list; five
    chosen ones is a recommendation, and the reader pays for the
    choosing.
16. One paper wearing several hats. Splitting a single paper across
    two or three items, or calling two papers "several teams", makes a
    thin week look broad. State plainly when findings share a source.
    Amended 2026-09-23, from the first read of a live payload: this is
    not mainly a temptation the writer invents, it is the shape of the
    input. The queries return distilled CLAIMS and the issue prints
    ITEMS, and nothing converts between the two. The 2026-09-23 payload
    offers 22 new claims that are 5 papers, four of them contributing 5
    claims each, and 12 traction claims that are 10 papers. A writer who
    takes one row as one item produces the fixed-length issue of entry
    21 and the several-teams dishonesty of entry 29 without inventing
    anything. Group by paper before counting items.
17. The greeting that carries no information. "Welcome to another edition
    of...", "Happy Monday", "Hope you had a great week." A newsletter
    should say hello, and the owner asked for it back, but a hello that
    would fit any issue of any newsletter on any day is a form being
    filled in. The greeting earns its line by being true about this
    particular day. Added 2026-09-19 with the greeting rule.
18. The section that defends itself. An intro explaining why a section is
    worth reading ("why tracking this matters: acting on stale results is
    how systems get built on sand") is the ranking-narration tell wearing
    a different hat. Frame the contents, never the container. Added
    2026-09-19 from the owner's no-meta-commentary ruling.
19. Headings that name a category instead of speaking. "Compounding", "New
    and unproven", "Key takeaways", "What this means". A heading that
    sorts rows reads as machine output no matter how good the prose under
    it is. The four slots are the owner's and their order is fixed, but
    their names belong to the skeleton and never to the page (canon law
    12). Added 2026-09-19 from her heading ruling, amended the same day
    after entry 20.
20. The skeleton printed as the page. "Gaining traction", "Trailblazing",
    "Left behind" and "Read these yourself" are the generator's internal
    slot labels, and printing one as a heading hands the reader the
    blueprint instead of the building. It is also the one tell the owner
    has flagged twice, the second time in the word "AGAIN". The test is
    blunt: a heading that would fit tomorrow's issue is furniture, so
    write the one that fits today's. Added 2026-09-19 from incident 20.
21. The fixed-length issue. Ten traction bullets and nine reading-list
    entries in a week whose new work was two papers, or a real week cut
    to the shape of a thin one. Length is a claim about how much
    happened, so a padded thin day lies and a truncated heavy day
    cheats. Added 2026-09-19 from canon law 11, after 2026-W37's ten
    identical bullets.
22. The date inside the headline. "[September 7-13, 2026]" spends part of
    the only sentence most readers ever see, the email subject, on a fact
    the email header, the issue metadata and the archive listing already
    carry. The title is the finding alone. Added 2026-09-19 from her
    ruling rescinding the bracketed range.
23. The issue that never says what is in it. Morning Brew prints "In
    today's newsletter, we'll get into:" and three lines, Money Stuff
    prints a deck under the title, The Batch names its three items in
    the issue title, and TLDR puts them in the subject. 2026-W37 made
    the reader scroll to find out. Contents are not methodology, and a
    reader who cannot see the shape of an issue in the first screen has
    no reason to stay in it. Added 2026-09-19 from the prose benchmark.
24. The bare number. "Resolves 64% of tasks" with no baseline beside it,
    or "gaining three independent supports" with no number at all. Every
    contender puts the comparison in the same sentence as the figure
    ("45.9 percent success with the memory model versus 37.6 percent
    without it", The Batch, issue 371). A number the reader cannot place
    is decoration. Added 2026-09-19 from the prose benchmark.
25. The item that ends on its citation. 2026-W37 closed every entry on a
    URL, which makes the last thing the reader sees a bibliography line
    and leaves the consequence for them to work out. The Batch ends on
    "We're thinking", Import AI on "Why this matters", Morning Brew on a
    writer's initials. End on the judgment, then the source. Added
    2026-09-19 from the prose benchmark.
26. The club sentence. A term of art used as though the reader is already
    inside the field: "on-policy distillation", "KV cache", "preference
    alignment", "credit assignment", "rollout", or any acronym, standing
    bare on its first appearance. The owner read a whole issue of these and
    said she felt like "an outsider to something privy". The tell is not the
    term, it is the missing clause beside it, and a definition that shows up
    on the second mention is the same failure with a delay. Either the first
    sentence hands the reader the word or the sentence uses plain words
    instead. Added 2026-09-19 from canon law 12a.
27. The wall. An item body written as one block of stacked clauses, four
    findings and three numbers and a caveat inside a single paragraph, so the
    reader unpacks it instead of reading it. Every clause can be true, precise
    and well made, and the paragraph still fails. Compression is fewer words
    per idea, never more ideas per line, so the fix is air: two or three
    sentences to a paragraph, one idea to a sentence, and one fewer item on
    the day when that will not fit. Added 2026-09-19 from her density ruling.
28. The forecast nothing can check. "This shift suggests that future
    pipelines will embed verification and observation cues as core
    components rather than add-on tricks." It cannot be wrong, so it
    cannot be information, and 2026-W37 spent its one underline on it.
    A bet with a number or a date attached is worth printing. A
    direction-of-travel sentence is the place AI prose goes when it has
    run out of findings. Added 2026-09-19 from 2026-W37's opening.
29. The invented shared byline. "Finally, researchers at the same
    group released a 122B Mixture-of-Experts terminal agent" tied two
    unrelated papers to one team that the payload never said existed.
    Attribution is a claim about people and carries the same
    never-invent rule as a number. Added 2026-09-19 from 2026-W37.
30. The label that moved down a level. "**Contradicted**" and
    "**Replaced**" in bold at the head of a group inside a section do
    the same job as "Gaining traction" at the head of a section: they
    sort rows, they fit every issue, and they hand the reader the
    blueprint. A category word is a category word whether it carries a
    `##` or a pair of asterisks. Added 2026-09-19 from 2026-W37, where
    the generator's own example lead-in printed verbatim.
31. The advice sentence in the same clothes every time. "Builders
    should replace binary success/failure signals", "Practitioners
    should adopt these token-level continuity tricks", "Builders of
    long-horizon agents should embed such feedback": three items, three
    identical constructions, and by the third the reader has stopped
    reading the sentence and started recognizing it. Naming the
    consequence is house law, so vary what it attaches to, not only its
    verb. Added 2026-09-19 from 2026-W37, three items out of three.
32. The nickname before the introduction. Not jargon, an ordinary word
    quietly carrying a technical job: "how much of a teacher a student
    really needs", "drop its teacher mid-training", printed before
    anyone said that teacher and student are what the field calls a big
    model training a small one. Rejected verbatim by the owner. It is
    the club sentence (26) wearing plain English, and it is worse than
    jargon in one way: nothing on the page looks like a term, so the
    first-use pass has nothing to list and the writer never notices.
    Every borrowed word gets the same clause a coined one would.
    Added 2026-09-19 from the two intro specimens in taste.md.
33. The label in italics. A structural word announcing the next block,
    "*Procedure*" above a numbered list, "*Method*", "*Results*", does
    the same job as "Gaining traction" over a section and "**Replaced**"
    over a group, and it fails for the same reason: it sorts the page
    into parts instead of saying anything, and it would sit over any
    item in any issue. The steps under it already look like steps. The
    tell survived two heading gates because both of them read bold runs
    and `#` lines and neither read italics, which is the general lesson:
    a label is a label in any typeface. Added 2026-09-20 from 2026-W37,
    which printed it twice. Amended 2026-09-22: the same issue prints
    "*paper*" above every source line, which is a fourth instance and was
    not caught by an entry naming three.
34. The empty stream reported as news. "No citation movers were recorded
    this week" tells the reader that one of alexandria's tables returned
    no rows, in the table's own vocabulary, in the middle of a section
    about research. It is entry 14's internal vocabulary crossed with the
    ranking narration of entry 18, and it reads as the machine clearing
    its throat. An absence is worth printing only as a fact about the
    field, in the reader's words, and only where it changes what they
    should believe. Added 2026-09-20 from 2026-W37.
35. The section kept for the shape. Entry 34 is about how an absence is
    worded; this one is about whether the section should have been on the
    page at all. A heading written fresh and well, followed by one honest
    sentence saying nothing landed in that slot today, is still a heading
    the reader scrolled past to learn that nothing happened. The generator
    had no clause letting a section be dropped, only clauses telling it how
    to word the emptiness, so a thin day printed the same four-part
    furniture a heavy one did. That is entry 21's fixed-length issue
    measured in sections instead of words, and the daily cadence will meet
    it constantly, because most days overturn nothing. A slot the day gave
    nothing to prints nothing, heading included. Added 2026-09-20 from the
    generator audit, not from an issue, because no issue has been generated
    since the daily was adopted.
36. The gate that lists instead of testing. Not a tell in the prose, a tell
    in the machinery that checks the prose, and it is on this list because
    it is what let four of the entries above ship. "If the heading equals
    one of these eight strings, fail" catches the eight labels already
    known and every future one walks through, which is exactly what
    happened when the category word moved from a heading to bold (30) and
    from bold to italics (33). A check written from the last failure is a
    memorial, not a gate. Every rule on this list that can be stated as a
    question about any line ("could this sit over a different day's items
    unchanged?") is enforced as that question, and the enumerated examples
    are evidence that the question is worth asking, never the test itself.
    Added 2026-09-20, incident 26.
37. The comma that should have been a full stop. "Your agents get the same
    findings, as files they can load" carries one comma and the owner struck
    it, in the word "unneeded", with the positive instruction beside it: "i
    prefer plain short sentences." The tell is not comma density, so counting
    them misses it. It is a comma doing work a full stop was there to do,
    and the test is removal rather than a threshold. Take each comma out and
    read the sentence again. If it wanted to stop, let it stop. Two shapes
    carry this most often, the three-item list folded into a sentence that
    was already finished, and the trailing participle that adds a second
    finding after the first has landed ("..., allowing agents to scale up
    without the instability that previously limited long-horizon training",
    2026-W37's opening). A long sentence is still right where one dependent
    clause earns it, because entry 3 is still on this list and a paragraph
    of flat short sentences fails that one. Length comes from a clause, never
    from punctuation. Added 2026-09-21 from her site-copy verdicts of
    2026-09-20.
38. The register that is pleased with itself. Her verdict, verbatim, on one
    rejected paragraph: "sounds millenial/condescending/unserious/vibecoded".
    Three tells inside it. The cute aside that tells the reader how easy
    this will be for them, "in words you do not need a PhD to follow". The
    diminutive that makes the product smaller so it will seem friendlier,
    "small files". The colon that pauses to gloss a term the sentence has
    just used, "become skills: small files your agents load". The reason
    this belongs on a list about issues and not only about the site is the
    direction the pressure runs. Entry 26 and canon law 12a push every issue
    hard toward explaining, and explaining is one step from performing the
    explanation, so the seat enforcing the outsider test is the one most
    likely to produce this. Hand the reader the word. Never remark on the
    handing over. Added 2026-09-21 from her site-copy verdicts of
    2026-09-20.

39. The verb of presentation. A reading-list line that opens on what the
    paper does rather than on what the reader decides: "Shows a multi-agent
    system that writes TPU kernels", "Details large-scale search agents",
    "Provides a full framework". Eight of 2026-W37's nine picks open this
    way, and a column of them turns a recommendation into a catalogue. The
    test is a question about the verb and not a roll of verbs, because
    "provides" sat outside the seven the generator banned and shipped
    anyway: does this word belong to the paper or to the reader? A pick
    earns its line by naming the decision it would inform. Added
    2026-09-22 from 2026-W37's reading list.
40. The mark doing a full stop's job. Entry 37 is the comma, and the
    generator has banned the stylistic em dash and the semicolon join
    since the voice overhaul, so three separate rules now describe one
    defect: a punctuation mark holding two finished sentences together
    instead of a full stop. Stating it three times as three marks left the
    fourth unbanned, and the fourth is the colon that pauses to gloss a
    term the sentence has just used ("become skills: small files your
    agents load", struck by the owner on 2026-09-20 and currently caught
    only as a register tell in entry 38). The fifth will be a mark nobody
    has written a rule for. Read the punctuation with the question, which
    is whether the mark is standing in for a stop, and split the sentence
    when it is. Added 2026-09-22 from the generator sweep of incident 27.
41. The gate that reads the output and never the input. Entry 36 is a gate
    that enumerates instead of asking. This one asks the right question of
    the wrong artifact. Every rule in the generator, and there are now about
    forty, checks the text the model produced. Nothing checks the material it
    was handed, and the material is not clean. The payload assembled on
    2026-09-23 carries 286 non-ASCII characters across 42 of its 48 claim
    strings, 188 of them the non-breaking hyphen inside ordinary words. It
    returns 22 "new claims" that are 5 papers. Two of its three reading-list
    papers are already covered in another section. Its one-line triage note
    opens "Provides a comprehensive framework", which is entry 39 arriving
    pre-written. Four defects that nine editorial runs diagnosed as the
    model's prose habits are sitting in the model's input, and a rule that
    tells the writer not to produce what its source already contains is
    asking it to notice rather than to clean. State where the material comes
    in, or the gate certifies an inherited failure. Added 2026-09-23 from the
    first read of a live payload.
42. The movement that is one reader. Entry 24 is the number with no
    comparison beside it. This is the number that carries its comparison,
    states it honestly, and still says nothing: "0 -> 1 citations" and
    "1 -> 2 citations", printed in the section whose whole claim is that
    relevance is impact. All five citation movers in the 2026-09-23 payload
    are that size. The arithmetic is not wrong and the sentence is not a lie,
    which is what makes it hard to see: a doubling from one to two is a
    doubling. One person read a paper. In a section that exists because the
    owner ruled that traction and not release date decides relevance,
    printing it is the release-date feed wearing the evidence's clothes. A
    number earns the impact section when a builder could act on it. Added
    2026-09-23 from the live payload.
43. The stored sentence kept for the exceptional day. "Today's papers were
    routine, so there is no issue. The next one comes tomorrow, and Monday's
    weekly synthesis covers the whole week." It is honest, it is short, and
    the generator is told to "output exactly this and nothing else", so the
    second time an empty day arrives the reader gets a sentence they have
    already read. Entry 17 is the greeting that would fit any day. This is
    its harder case, because the day a newsletter has nothing to report is
    the day its voice is the only thing on the page, and a canned line spends
    exactly that day proving a person was not there. Honesty about a thin day
    is house law and stays. The words are written fresh every time. Added
    2026-09-24 from the empty-day template in prompts/daily.md.
    Enforced in `prompts/digest.md`, which absorbed the daily cadence, AND
    filed, because the file this entry was written from is the other generator
    and no edit here reaches it. Both halves are needed to close the entry.
    LANDED prompts/digest.md: "A stored sentence kept for empty days is furniture the moment it runs twice"
    Filed: docs/ideas.md, "One craft layer, two cadence files", 2026-09-24,
    still `proposed`. Checked 2026-10-09: `prompts/daily.md` has never been on
    main, and the branch that carries it is now the one behind the open pull
    request #60 rather than the closed #35 the entry names. Line 121 of that
    file is this entry's specimen, unchanged, fifteen days on.
44. The tell the template orders. Entry 25 says an item never ends on its
    citation. prompts/daily.md says "End each item with its source line:
    *paper title* - [link](url)", which mandates entry 25, prints a stylistic
    em dash against law 1, and makes the last word of every item "link".
    Entry 22 says the date stays out of the headline, and the same file
    orders "[{dates}]" into two of them. A tell a model reaches for by habit shows
    up in some issues. A tell its instruction requires shows up in all of
    them, and no amount of rereading the output catches it, because the
    writer is obeying. Entry 41 says to read the payload the generator was
    handed. This says to read the generator itself, and to read every
    generator, not the one this seat happens to own. Added 2026-09-24 from
    the second generator in PR #35.
    Filed, and it is the one entry in 1 to 50 that no wording of
    `prompts/digest.md` can reach, because its subject is the generators this
    seat does not own. docs/ideas.md, "One craft layer, two cadence files",
    2026-09-24, still `proposed`.
    The check, scoped to the branch rather than to main, because the file is
    not on main and a grep over the working tree finds nothing and reports it
    as clean:

    ```
    git show origin/engineer/2026-09-20-digest-quality-gate:prompts/daily.md \
      | grep -n "source line\|{dates}\|routine, so there is no issue"
    ```

    Run 2026-10-09, fifteen days after this entry, nineteen days after the
    pull request opened. All four specimens are live and unchanged: the
    `[{dates}]` title the owner struck by name, the source line that mandates
    entry 25 and carries the em dash law 1 forbids, and the stored empty-day
    sentence of entry 43. `pipeline/weekly.py:835` on that branch selects that
    file as the daily's prompt, so the day it merges the daily issue is written
    by 133 lines instead of by this register's generator.
    The second reading of this entry is the one that matters now and it is not
    about the daily. "Read every generator" includes the live ones, and the
    sweep of 2026-10-09 put entry 14's question to `prompts/rag-answer.md`,
    which orders a claim id into every sentence it writes. It clears, and the
    reason is the surface rather than the words: the tool hands its caller a
    `citations` array resolving every id in the same return value, and the
    caller is an agent. An identifier a reader can resolve from the artifact
    they are holding is not internal vocabulary. One printed in an issue, where
    nothing resolves it, still is.
45. The opening billed to a reader who was not there. "You spent last
    week watching agents get faster by doing less at test time", the
    2026-W39 opening, struck by the owner with "dont assume readers read
    each issue" and now canon law 13. Entry 17 is the greeting that would
    fit any day. This is its inverse: a greeting so specific to one day
    that it only works for the minority who read that day's issue. It
    charges the reader for a purchase they did not make, in the first
    sentence, which is where an outsider is deciding whether the thing is
    for them. The tell is a second person doing the work of a footnote:
    the line tells the reader what THEY were doing rather than what the
    field was doing, and only a returning reader can check it. Three
    quieter forms of the same failure: "we covered", "the ceiling from
    the last issue", and the bare continuation that names no issue and
    still needs one. The thread is not the problem and never was. Pointing
    at it instead of stating it is. Added 2026-09-24 from her ruling on
    the W39 opening.
46. The colon that announces a finding, which is a heading in punctuation
    costume. 2026-W39 runs it once per item, and the roll reads as a
    template even though the findings underneath are real: "The problem
    they address:", "The result:", "The task:", "The honest result:",
    "The critical finding for builders:", "The training signal is what
    matters for builders:". Entry 40 names the colon that pauses to gloss
    a term the sentence just used, and this is the other job the mark
    does, which is to label the clause behind it. The heading gate at the
    end of the generator already asks whether a line could sit over a
    different day's items unchanged, and every one of those six could.
    The gate missed them because it collects lines beginning with `#` and
    runs of bold or italic sitting alone, and a label welded to the front
    of a sentence sits alone in none of those ways. A label is a label at
    any level, in any typeface, and now in any punctuation. The related
    specimen from the same issue is the aphoristic version, "Three labs,
    one bet:", where the colon props up a snap summary that the paragraph
    it closes has already earned. Added 2026-09-24 from the W39 grade.
    Enforced 2026-09-27, three days late, and the delay is the lesson. This
    entry named the gate's collection step and named the fix in the same
    sentence, and the gate was never changed, so two more specimens of this
    shape stayed live on the site: "For builders:" and "The procedure is
    extractable:", neither of them in the six above. The entry predates the
    standing rule at the top of this file by one day, which is why nothing
    asked whether it had landed. The gate now takes the text in front of any
    colon as its own unit of inspection and puts the heading question to that
    fragment rather than to the line around it, because a line whose second
    half is real writing passes a question its first half would fail
    (INC-2026-09-27-gate-unit-is-the-line).
47. The paragraph that reports and never lands. A result stated with its
    number, its baseline and its evidence grade, and then the next result
    starting in the same paragraph, so the reader is handed the arithmetic
    and left to work out what it means. 2026-W39 does it six times:
    "beating even the 41.7% achieved when the specialized harness stays
    attached at runtime" is the week's most surprising fact and no sentence
    anywhere says what it means for a builder. Entry 7 is the summary that
    restates the headline. This is its opposite, a paragraph that adds
    nothing but more facts. The fix is one sentence with no number in it,
    under every result, saying what the number makes true. Added 2026-09-24
    from her ruling that the issue must be enjoyable.
48. The line that is entirely bold, standing alone. It looks like emphasis
    in the markdown and it is a heading in every other sense: it announces
    the block under it, the eye reads it as furniture, and the heading gate
    at the end of prompts/digest.md already collects it. Two things make it
    worth its own entry now. The owner has asked for a one-line pull for the
    number that matters, which is exactly the shape that reaches for this.
    And the email template sets a bold line standing alone as a grey
    uppercase group label, verified against `pipeline/email_render.py` on
    2026-09-24, so the pull arrives in the inbox looking like the taxonomy
    label canon law 12 bans. Bold inside the sentence. Never the whole line.
    Added 2026-09-24 from the formatting ruling.
49. One shape for a whole issue. Not a sentence tell and not a word tell, a
    page tell, and it is the one the owner named when she said an issue was
    "a hassle to read". 2026-W39 is twenty-one paragraphs and nothing else:
    no list, no line standing on its own, no change of texture from the
    title to the close, in a week whose material included four replacements
    that were four of a kind and three constraints that were three of a
    kind. The tell is visible before a word is read, which is why it can be
    checked before the prose is. Count the shapes on the page. One is the
    finding. The cure is not decoration: it is noticing which of the day's
    material is parallel and setting that part as a list, per canon law 14.
    Added 2026-09-24 from the W39 shape read.
50. The hedge that licenses the claim it qualifies. The shape is a true
    concession, a comma, and then the assertion the concession should have
    stopped. 2026-W39: "The contexts differ, agent construction versus
    combat simulation, but the broader belief that expert-authored
    baselines set immovable ceilings took a hit this week." Every clause
    before the "but" is correct and honest, and the sentence uses that
    honesty as permission. This is not hedging in the usual sense and the
    usual cure makes it worse: deleting the qualifier leaves a bare false
    claim, and keeping it leaves a false claim that sounds careful. The
    test is which way the sentence would go without the hedge. A real
    qualifier narrows a claim that still stands. This one is load-bearing,
    and a claim that cannot stand without being apologized for is a claim
    to drop. Related to entry 47, the result that never lands, and its
    opposite in a way worth seeing: 47 is a finding with no meaning
    attached, this is a meaning with no finding under it. Added 2026-09-24
    from the fourth grade of W39, which is where four prose passes had
    missed it, because it is not a prose defect.
51. The rule's own name printed as a label. 2026-W39's reprint prints "**The
    number that matters:** 44.3% with the harness gone, up from 23.3%." There
    is no such phrase in the research. It is the name of a formatting rule in
    prompts/digest.md, line 169, and the generator printed the name of the
    rule it was obeying at the top of the line where it obeyed it. Entry 14
    asks whether a subscriber who has never seen the codebase could say what a
    word refers to, and it was written about the pipeline's vocabulary, the
    claim graph's and the ISO week's. This is the fourth vocabulary in the
    building and the only one the writer seat owns: every rule name in the
    generator is internal vocabulary by entry 14's own question. The specimen
    fails three other ways at once, which is what makes it worth its own
    entry rather than a cross-reference. It is the label welded to a sentence
    of entry 46. What follows the colon is a fragment and not the standing
    sentence canon law 14 asks for. And the rule it names is the one rule the
    issue was trying hardest to follow, so the tell arrives in the shape of
    compliance. Added 2026-09-24 from the fifth grade of W39. Enforced
    2026-09-25: the internal-vocabulary test in prompts/digest.md now names
    this file's own rule headings as internal vocabulary, where it had listed
    only the codebase's.
    That ending was true and it was not enough, corrected 2026-09-27. The
    internal-vocabulary test sits in the traction section's guidance and is
    advice to the writer, so it works on the line being composed and has no
    reach over finished output. The gate that reads finished output could
    still not see this string, for the reason entry 46 gives: the label is a
    fragment of a line and the gate collected lines. Both entries are
    enforced by the same change, and the general shape is worth carrying. An
    enforcement ending has to name the gate the defect would pass through,
    not merely a place in the file where the rule is now written down.
52. The fix by deletion. A sentence is struck, and the repair removes it
    rather than rewriting it, so the issue quietly loses the element that
    sentence was occupying. The owner struck W39's opening, "You spent last
    week watching agents get faster by doing less at test time", for assuming
    a returning reader. The reprint has no greeting at all. It cleared the
    gate, because a greeting that is absent cannot assume anything, and the
    greeting is house law she asked for back by name. The same move took the
    evidence grades out under the density ruling: the grade is a clause,
    compression cuts clauses, and four of them went. This is the cheapest
    failure in the register to commit, because it passes every check written
    for the defect and leaves nothing on the page to catch. Canon law 13
    already says of the thread that "the fix is always the same and it is
    never deletion", and that sentence needs to be read as binding the slot
    and not only the sentence in it. A ruling against how an element was
    written is never a ruling against the element. Added 2026-09-24 from the
    fifth grade of W39.
53. The prohibition that supplies the string. Entry 44 is the tell an
    instruction requires. This is the tell an instruction QUOTES. The reading
    list's heading slot in prompts/digest.md read, in full, `## {The heading
    for the reading list, written fresh and never the words "Read these
    yourself"...}`, and the issue printed "## Read these yourself". All four
    heading slots were written that way and each one carried its own forbidden
    name inside the braces the model was told to replace with its own writing.
    Two more of the file's sentences shipped in the same issue, both worked
    examples: the plain-meaning line and the number line, which were drawn
    from W39's own material because W39 is the issue that produced the ruling
    they illustrate. An exemplar written from the material the generator will
    be handed is not an illustration of the answer. It is the answer. The
    general test, and it applies to any prompt and any register, not only to
    this one: read the instruction from the position the writer occupies when
    they obey it. If the nearest quoted English at that position is the thing
    being banned, the sentence around it is not doing the work its author
    thinks. Hold specimens where the output is read, never where it is
    written. Added 2026-09-24 from the fifth grade of W39, where the
    invariant "no sentence quoted from this file as an example survives into
    the issue" had been standing in the same file the whole time.
54. The term introduced under one name and used under another. Entry 26 is the
    term of art standing bare, with no clause beside it. This is the term of
    art that got its clause, under a synonym, and is then used for the rest of
    the issue under the word that never got one. W39's reprint opens on
    "scaffolding: the extra instructions and tooling that make frontier models
    reliable on real tasks", which is the correct gloss correctly placed. It
    then uses "scaffolding" twice and "harness" thirty-eight times, beginning
    in the title, and nowhere says the two are the same thing. The outsider is
    handed a definition for the word the issue does not use. This survives the
    first-use pass because the pass looks for terms without clauses and this
    term has one, three paragraphs away, spelled differently. The test is not
    whether every term was defined. It is whether every term the reader
    actually meets was, counted in the words on the page. Added 2026-09-24
    from the fifth grade of W39. Enforced 2026-09-25: the first-use pass in
    prompts/digest.md now counts the term the reader meets rather than the
    term the writer defined, and gives the join to write when the sources
    force both words.
    LANDED prompts/digest.md: "the smaller count is the one to delete"
55. The greeting that narrates the reader's week. Entry 45 is the opening
    billed to a reader who was not there, and its tell is a pointer at a
    previous issue. This is the same charge with the pointer removed. The
    rehearsal print of 2026-09-26 opened "You have spent the week watching the
    field argue about whether agents need a heavy harness at deployment", and
    it is the first specimen in this register written by a generator that
    already held the rule against it. It names no issue. It contains no "last
    week" in entry 45's sense. It still tells a stranger what their week was,
    and only a returning reader can check it. What made the earlier line wrong
    was never the reference, it was the tense, and the register had recorded
    the reference because that is what the struck sentence happened to
    contain. The test is grammar and it comes back yes or no: is the subject
    "you", and is the verb in any past tense? Present perfect counts, which is
    the form that got through. The opposite failure sits beside it and the same
    reading catches both, because the reprint's "The agent-building world has
    spent the week arguing about scaffolding" removed the person rather than
    the tense, which is entry 52 again. Added 2026-09-26 from the owner's
    dispatch of 2026-09-25. Enforced the same day: the opening slot in
    prompts/digest.md now carries a written safe form rather than a
    prohibition, and the stands-alone gate carries the tense check with both
    specimens held at the position where finished output is read.
56. The example that supplies the frame rather than the string. Entry 53 is
    the prohibition that quotes the thing it bans, and its test is the nearest
    quoted English at the position where the writer stands. This is the
    survivor of that test: an example whose words are not copied and whose
    SHAPE is, every time. prompts/digest.md offered "Worth the hour if you are
    choosing between one agent and a planner plus a separate verifier" as the
    model reading-list line. Across the two prints of 2026-W39, five entries
    out of five open "Worth the hour if you are", and one of them completes it
    as "choosing between shipping a complex harness or teaching its structure
    to the model". Nothing was plagiarised and the section became a catalogue
    anyway. Entry 53's cure does not reach this, because moving the specimen
    or changing its subject leaves the frame intact, and a rule that says "let
    no two entries take the same shape" was already sitting two sentences
    below it. Two things have to happen together: the frame is named as spent
    and refused by its variants, and the repetition is counted where it is
    visible. The general form, for any slot in any register: an example at a
    writing position is a template even when the instruction beside it forbids
    templates, so an example there earns its place only if repeating it would
    be obviously absurd. Added 2026-09-26 from the fifth and sixth grades of
    W39. Enforced the same day: the reading list's line in prompts/digest.md
    names the frame as spent, refuses three rewordings of it by name, and
    counts openings and grammatical shapes across the section's entries.
57. The payload's field describing itself inside a sentence about the
    research. "New work from ACLArena, flagged for deep reading, measures what
    multi-stage post-training does to a model's capabilities", from the
    2026-09-26 print. Entry 14 asks whether a subscriber who has never seen
    the codebase could say what a word refers to, and the words it was written
    about are nouns, which are claim ids and support counts and the ISO week.
    This is the same failure in a participial phrase, and the phrase reads as
    provenance rather than as vocabulary, which is why it survives a pass
    looking for internal words. Put entry 14's question to the clause instead
    of to the word and it collapses at once: flagged by whom? The answer is
    this pipeline, and the reader has just been told a fact about alexandria's
    triage in the middle of a sentence about somebody's paper. The class is
    every reason a paper is in front of the writer rather than a reason it
    matters to the reader: "distilled this week", "scored highly in triage",
    "carries a procedure", "drawn from the traction stream". The payload
    explains itself to the generator and never to the subscriber. Added
    2026-09-26. Enforced the same day: the internal-vocabulary rule in
    prompts/digest.md now names the payload's own field semantics as the third
    vocabulary on its list, with the reader-facing form to write instead.
58. The rule obeyed where it counts and missed where it means. Not a sentence
    tell and not a page tell but a compliance tell, and it is the reason the
    owner has asked for enjoyability three times. Canon law 14 carries six
    rules. Five are measured inside a paragraph, which are its length, its
    results, its numbers, its plain-meaning line and its number on a line. One
    is measured on the page, which is how many shapes are on it. The reprint
    of 2026-W39 cut its longest paragraph from 191 words to 98, left nothing
    over 100, and shipped twenty-four paragraphs with no list, no subheading
    and no line standing alone. Every count in the law passed. The page has
    one shape, which is entry 49, and she read it and said enjoyability is
    still not fixed. The tell is visible in the diff rather than in the issue:
    a fix that moved only the countable numbers is a fix aimed at the
    measurement. Related to entry 51, where the generator printed the name of
    the rule it was obeying, and this is the structural version of the same
    thing, which is an artifact shaped around the check instead of the reader.
    Whoever writes a rule with a measurable half and a meant half orders them
    so the meant half is checked first, because the measurable one will always
    be cheaper. Added 2026-09-26 from the owner's dispatch of 2026-09-25.
    Enforced the same day: the shape gate in prompts/digest.md counts the
    shapes on the page before any of the word counts, and one kind of block
    fails an issue on its own whatever the other four counts say.
59. The system name promoted to an author. "New work from ACLArena" and "The
    Show-Harness work shows", both from the 2026-09-26 print, attribute
    findings to the titles of the papers that report them. The attribution law
    allows two forms, the institution from the payload and the named author as
    its fallback, and this is a third one invented at the moment both were
    unavailable, which is the moment it will always be invented. It reads as
    correct because the payload hands over benchmarks, pipelines, methods and
    datasets as capitalised proper nouns, and a proper noun in the subject
    slot of "found" or "shows" looks like a group of people. None of them is
    anybody. Related to entry 14 in an inverted way worth noticing: entry 14
    catches internal vocabulary reaching the reader, and this one is the
    payload's vocabulary reaching the reader disguised as a research group, so
    the word is fine and the grammar is the lie. The fix where the payload has
    no institution and no author is to write the finding with no attributive
    phrase at all. Added 2026-09-26. Enforced the same day: the attribution
    rule in prompts/digest.md now says there is no third fallback and names
    the four kinds of payload noun that arrive looking like one.
60. A count printed with the neighbouring count's verb. "The library read
    1,289 papers", from the print of 2026-09-26, on a day when 1,289 papers
    had been ingested that week and 164 had ever been read in full. This is
    not the slop lexicon and not a shape tell. It is a true number in a false
    sentence, and it survives every pass in the grading procedure because all
    five of them read the prose and this defect is in the arithmetic behind
    one word. The class is any sentence that takes one pipeline count and
    attaches an act the pipeline performed on a different, smaller set:
    "read" for ingested, "studied" for triaged, "verified" for linked,
    "distilled" for anything that was not distilled. The tell in the draft is
    a verb of effort standing next to the largest number available, because
    the largest number is always the cheapest act and the one a scale sentence
    reaches for. The test is one question and it is arithmetic rather than
    taste: which field is this number, and is the verb the act that field
    records? Added 2026-09-26 from the owner's dispatch of 2026-09-25.
    Enforced the same day: `prompts/digest.md` names the act each count
    records where the payload is described, the closing slot binds a verb of
    reading to the full-read count alone, and a reading gate at the end of the
    file collects every sentence whose subject is the library and puts the
    arithmetic question to each. Canon law 15 is the law this produced.
61. Standing copy, fixed in code, that no pass has ever graded. The masthead
    read "The latest in AI research, read in full and distilled weekly" from
    the day it was written until 2026-09-26, and it printed above every issue
    ever sent, against 166 full reads out of 8,956 papers. Entry 60 is the
    false sentence, and this entry is why it lived so long. A string constant is
    exempt from every gate this register has, because the gates run on what
    the model writes and this line is deliberately not written by the model,
    which was the good reason it was put in code. The comment above it said
    the point was that the brand line "never drifts", and a line that cannot
    drift also never comes up for review. The class is wider than the
    masthead: the preheader, the edition label, the footer, the standing
    close, subject prefixes, every string in `pipeline/` and `site/` that a
    subscriber reads. Two rules fall out. Every editorial run reads the
    reader-facing constants once, in code, and grades them as it grades a
    sentence in the issue. And a reader-facing string kept in code carries a
    comment naming the register that governs it, so the next person editing it
    knows a law applies. Added 2026-09-26, with the masthead repaired the same
    day under the owner's order giving its wording to this seat.
62. The heading that names the section's job instead of the day's news, in
    the one section whose job never changes. "Read these yourself" printed as
    the reading list's heading in the published 2026-W39 issue, in the site
    reprint of it, and in the rehearsal print of 2026-09-26. The third of
    those was written by a prompt that named that exact string as forbidden,
    at the end of the file, in a tripwire built for it. Entry 53 says a
    prohibition can supply the string it forbids, and that diagnosis does not
    fit here, because the slot the heading is written into had already been
    cleared of the phrase and the model printed it anyway. The cause is the
    section rather than the file. Three of the four sections are named after
    what the day's papers showed, and the fourth is named after something the
    issue does on every day it runs, so a line that describes the act is
    always available in that slot and it is always true. It is also warm and
    plain, so the class question that catches "Compounding" returns the wrong
    answer on it: the line does not look like taxonomy, it looks like
    writing. The tell is a heading whose subject is the newsletter's own
    activity rather than the material under it, and the test is the one the
    heading rule already states, which is whether the line would have fitted
    every issue ever sent. Added 2026-09-26. Enforced the same day in the
    reading list's heading slot, which now builds the heading from the picks,
    names the two forms that work, and says why the generic line is always in
    reach here. The string check that failed is filed for the engineer
    instead of rewritten a third time, because it is a closed set of four
    exact strings and a regular expression outside the model decides it.
63. One system, two numbers, one measure, nothing telling them apart. The
    print of 2026-09-26 said a distilled model "hits 44.3%" on a
    macro-average across three kinds of task, and four sentences later said
    the supervision method that produced that model "produces 30%" on the
    same macro-average. Both numbers were in the payload, neither was
    misread, and the second came from a smaller ablation the issue never
    named as one. Each sentence is true on its own and the page is not. This
    is not the false comparison the claims pass's first question catches,
    where two unlike quantities are set against each other. Here the two numbers are about one method, which
    is why no comparison gate sees them, and the reader is the first party to
    notice. The tell is an ablation number printed in the same register as a
    headline result, usually one paragraph later, usually because the payload
    hands both over under one metric name. Added 2026-09-26. Enforced the
    same day: a numbers gate in prompts/digest.md groups every figure by the
    system it describes before the headings are checked, and the claims pass
    in the canon gains the same question as its fourth.
64. The standing line corrected at its source, with every published copy
    keeping the false version. Entry 61 is the reader-facing string in code
    that no pass grades. This is the next failure in the same chain, and it
    happens after that entry has been acted on. The masthead's false reading
    claim was cut from `MASTHEAD` in `pipeline/weekly.py` on 2026-09-26. On
    2026-09-27 the only published issue still opens on it, in its second
    line: "The latest in AI research, read in full and distilled weekly".
    The cause is where the string joins the artifact. `add_masthead` splices
    the constant into the body before the body is stored, so the sentence is
    baked into output at write time rather than composed when a page renders,
    and `site/lib/content.js` serves the stored body whole from either the
    markdown fixture or Neon. Changing the constant governs the next issue
    and cannot reach one that already exists. The tell is not a phrase, it is
    a question to ask of any reader-facing string this register condemns:
    does the fix reach what is already published, or only what will be
    printed next? Where the answer is the second, the entry is half done, and
    for a claim about alexandria's own work the published half is the one a
    stranger reads first (canon law 15). Two repairs exist and the choice is
    the owner's: correct the stored bodies, or stop baking the line in and
    compose it at render time, which is the one that stops this recurring.
    Added 2026-09-27 from the grade of the published 2026-W39. Filed for the
    engineer in docs/ideas.md rather than enforced here, because no change to
    prompts/digest.md can reach a string the model does not write
    (INC-2026-09-27-law-15-live-in-the-archive).
65. The test that asks for the banned sentence. Entry 56 is the example that
    supplies the frame rather than the string, and this is where the frame
    hides when no example is left to carry it. The opening slot in
    prompts/digest.md ended on a list of tests, and one of them read "the
    greeting sounds like a person who knows what the reader's week has been
    like". Two hundred lines above it sat a hard rule with no exceptions: never
    a past-tense verb with "you" as its subject. The rule is the law and the
    test is the brief, and the brief asked for the reader's week. The only
    honest source for that noun is the reader's past, so the greeting came back
    as a report on what they had been doing. The print of 2026-09-28 opened
    "You have spent the week watching agents get faster by thinking less at
    test time", which is the third outing of a sentence the owner struck on
    2026-09-24. The tell is a rule and an instruction in one file that cannot
    both be obeyed, and the way to find it is to read what a slot ASKS for
    rather than what it forbids, because the asking is what gets written from.
    Position decides which one wins: the prohibition is read as law and the
    test is read as the assignment, and the assignment is at the bottom of the
    slot where the writing happens. Added 2026-09-28. Enforced the same day:
    the test now says the reader's JOB, which is knowable from here, and the
    slot records why the noun changed.
66. The issue's own diagnostic vocabulary printed at the reader. Entry 14 is
    internal vocabulary from the pipeline, and this is the same failure from
    the other register, which is the one the grading procedure keeps. The print
    of 2026-09-28 says "The edge between them fails the kind test". "Edge" is a
    row in alexandria's claim graph. "The kind test" is the name of a question
    in the canon's claims pass, asked while grading an issue that has already
    been written. Both were in prompts/digest.md, in one sentence, three words
    apart: "every one of these is you noticing that the edge fails the kind
    test and continuing anyway". That is entry 53 with a new source, because
    what supplied the string this time was not a prohibition quoting a bad
    example, it was the file reasoning about its own work in its own shorthand.
    A subscriber cannot look either phrase up. They are not jargon and not a
    term of art, they are the machine's names for its parts, and a reader who
    meets one learns only that the issue was assembled. Added 2026-09-28.
    Enforced the same day: the sentence now says "the two measures do not
    match", and the rule under it names the class, which is every word the file
    uses for the pipeline and every word it uses for its own checks.
    LANDED prompts/digest.md: "the two measures do not match"
67. The promise the issue does not keep. Entry 23 is the issue that never says
    what is in it, and this is the opposite failure by the same measure. The
    contents line of 2026-09-28 named three findings. Its second one, "a memory
    system that routes simple decisions to a fast controller and saves the
    heavy model for when it matters, cutting query latency by more than a
    third", from a named team, appears nowhere else in the issue. The section
    that ran in its place was never promised. Nothing was misread and no
    sentence is false. The reader who kept the promise in their head goes
    looking for a third of the issue that does not exist, and finding nothing
    is worse than never being told, because now they are also wondering what
    else they missed. The rule against this was already in the file, as
    "name only items that actually appear below", which is a count written as a
    preference. Added 2026-09-28. Enforced the same day: the opening slot now
    matches each promised item to the section that delivers it, by institution,
    system and result, before the opening is left.
68. The count said out loud that nobody counted. One section of 2026-09-28 is
    headed "Two new bets on how agents improve themselves". Its first sentence
    says "two different bets" and then lists three, "one that evolves the
    harness, one that distills it, and one that watches what happens when you
    stack training stages". Two items follow, and distillation, the second of
    the three listed, was the previous section's entire subject. Three
    sentences, three different answers, each one written correctly on its own.
    This is not a wrong number in the research, which every gate in the file
    watches for. It is the issue failing to count itself, and it is the
    cheapest error here to catch and the most damaging to be caught at, because
    a reader who counts two where three were promised concludes the issue does
    not know what is in it. The tell is any quantity whose subject is the
    issue's own contents: three findings, two labs, both results. Added
    2026-09-28. Enforced the same day as a hard gate in prompts/digest.md that
    counts every such quantity against the things underneath it.
69. The heading that its own body takes back. Entry 62 is the heading that
    names the section's job, and entry 19 is the heading that names a category.
    This one is written from the day's news, in voice, false for any other day,
    and still wrong, because the section under it disproves it. "The 82.2%
    ceiling was not a ceiling" stands over four paragraphs of 2026-09-28 whose
    conclusion is that the two results being compared measure different
    quantities, so nothing was established about the ceiling either way. The
    body is the claims pass working exactly as the canon wants: it names the
    category error and refuses the comparison. The heading was written before
    that happened and never revisited, and the heading is the part a skimmer
    keeps. This is the hedge of ban list 50 one level up. There, a sentence
    concedes the comparison fails and proceeds. Here the concession is the
    whole section and the heading proceeds without it. Added 2026-09-28.
    Enforced the same day: the heading gate now reads each heading against the
    block under it and asks whether the section ends where the heading says it
    does, and names the repair, which is that a comparison failing is itself
    the finding and makes the better heading.
70. The evidence grade as a stamp. Canon law 6 requires the grade in-line and
    prompts/digest.md requires it as "a short clause inside the item's own
    prose". The print of 2026-09-28 carried one on all three items and the
    count passed: "The evidence is the authors' own experiments across three
    domains, not yet replicated", "The evidence is single-team, single-paper",
    "The evidence is one paper, one model family". One stem, three sentences of
    their own, each at the same position in its item. Every one is accurate and
    the third is invisible, because by then the words "The evidence is" are the
    furniture between items rather than something being said. Entry 31 is the
    advice sentence in the same clothes every time and this is the grade in the
    same clothes, which is worth its own entry because the grade is the thing
    the owner named as product rather than weakness, and product that reads as
    a form has stopped being product. A gate that counts grades cannot see
    this, and counting is how the grade was made to survive at all. Added
    2026-09-28. Enforced the same day: the grade slot now forbids opening on
    the word "evidence" or on any stem already used in the issue, and requires
    the grade to be folded into a sentence doing other work.
71. The banned example and its repair, quoted side by side where the work is
    written. Entry 53 is the prohibition that supplies the string and entry 56
    is the example that supplies the frame. This is both at once, and it is the
    shape that produced the worst line of 2026-09-28. The opening slot in
    prompts/digest.md carried the owner's struck sentence, then six lines later
    the repair written to replace it, both quoted in full, both at the position
    where the opening gets written. The print took the subject and the tense from
    the struck one, three phrases from the repair including one clause word for
    word, and assembled an opening whose every part came from the prompt and no
    part came from that day's news. Neither quotation was careless. The struck
    sentence is the owner's own ruling and the repair is the canon's model of the
    fix, and putting them together looks like teaching. It is not teaching. **A
    negative example beside a positive example, at the position of writing, is a
    menu, and the output is a dish from both halves of it.** The tell is any pair
    of quoted specimens in one slot, whatever the sentences around them say, and
    the company standard is `L-A23` in docs/standards/lessons.md, which reached
    this repository on 2026-09-28 in the HQ sync and says it in one line: read
    the instruction from the position of whoever obeys it. Added 2026-09-28.
    Enforced the same day: both quotations left the opening slot, the struck
    sentence joined the two already held at the stands-alone gate, and the repair
    was rewritten about a subject no payload will ever hand the model, which is
    this file's existing technique for an example that must not be copied.
72. The gate whose unit is wider than the thing it governs. Entry 58 is the
    rule obeyed where it counts and missed where it means, and this is the
    structural cause underneath it: a check written correctly for the case in
    front of its author, applied to a case one size larger, reporting a pass.
    The print of 2026-09-28 carries three at once and they were found together
    on 2026-09-29. The link rule counts items and work is cited per paper, so
    an item naming three separate results carried no link and the count of
    items against links came out even. The kind test asks whether "the two
    claims" measure the same thing and the payload hands over one old claim
    against several newer ones, so one refusal was written over two pairings
    and the pairing that holds went out with the one that does not. The
    reading list's overlap rule named `new_claims` and coverage happens in any
    section, so the pick that had been covered in the traction section was
    recommended back to the reader who had just read it. Three gates, three
    passes, one defect. The tell is grammatical and it is in the gate rather
    than in the issue: a check phrased in the singular, "the item", "the two
    claims", "the stream", against material that arrives in groups. The
    company standard is `L-A21`, a gate is judged by what it can see, and
    `INC-2026-09-27-gate-unit-is-the-line` is the same finding about the
    heading gate, whose unit was a line where the defect was a fragment. Added
    2026-09-29. Enforced the same day: all three gates in prompts/digest.md
    now name their unit explicitly and the two that are arithmetic count off
    one shared list of every named piece of work in the issue.
73. The comparison refused in a group, and the conclusion kept anyway. Entry
    50 is the concession written and walked past, where a sentence notices the
    two measures do not match and continues. This is its opposite and it costs
    more. The print of 2026-09-28 was handed two results standing against one
    old benchmark number: 83.3% on RMBench against the old 82.2% on RMBench,
    and 87% in air-combat simulation against the same 82.2%. It wrote one
    verdict over both, "these numbers share a percent sign and little else",
    which is true of the second pairing and false of the first on the issue's
    own words, since it names RMBench twice. The valid comparison was
    discarded with the invalid one. Then the section printed its conclusion,
    "treat the original 82.2% as a local optimum on one benchmark family, not
    as a bound", which nothing on the page supports except the number the
    paragraph above had just thrown away. The claims pass was working. It was
    asked once where it should have been asked twice, and a pooled answer is
    always the answer for the weakest member of the pool. Note what this costs
    against what it was avoiding: refusing a bad comparison protects the
    reader, and refusing a good one and keeping its conclusion leaves an
    assertion with nothing under it, which is the thing a reader cannot check
    and cannot forgive. The small true result, a benchmark ceiling passed by
    1.1 points on that benchmark, never printed. Added 2026-09-29. Enforced
    the same day: the fell-behind slot judges one pairing at a time, writes
    the answer down before looking at the next, and then reads its own
    conclusion against the pairings that survived.
74. The grade that clears a coverage law by reading instead of counting. Not a
    prose tell. This is the editorial instrument failing, recorded here
    because the canon's grading passes are written in this register and the
    writer seat's own output obeys every law it enforces. The grade of
    2026-09-28 recorded "Law 8, links reach the full text. PASS. Four distinct
    URLs, all arxiv.org/html/, no abstract landing pages." Every word true.
    The issue had five items and three named pieces of work with no link
    between them. The verdict graded the form of the links that existed and
    never counted the items that had none. The canon requires every verdict to
    carry a quoted line as evidence, and that requirement quietly steers a
    grade toward the laws that can produce a quotation, because what a
    coverage law forbids is an absence and an absence cannot be quoted. The
    same grade recorded law 6's presence half as a pass on a count of three
    against an issue holding five. The tell, for any future grade: a law whose
    subject is "every item" or "every issue" is graded by a count with its
    command written down, never by a reading, and a pass on one of those with
    no number beside it has not been graded. `INC-2026-09-26-grade-cleared-a-
    printed-violation` is the first occurrence and this is the second. Added
    2026-09-29. Enforced the same day in prompts/digest.md, where both counts
    now run off one list, and filed in docs/ideas.md for the pre-send gate,
    where both are arithmetic and belong in a command rather than in a reading
    (`L-A22`).

75. The finding handed to another seat, with nothing that checks whether it
    is still true. Entry 61 is the reader-facing string no pass grades, and
    entry 64 is the correction that reaches the next issue and not the
    published one. This is the third failure in that chain and it happens
    after both of those entries have been acted on correctly. By
    2026-09-30 the masthead's false reading claim had a canon law written
    from it (law 15), two entries in this list, an incident id
    (`INC-2026-09-27-law-15-live-in-the-archive`), and a ledger entry for
    the engineer stating two repairs and a recommendation. Every one of
    those artifacts is accurate and none of them is wrong about anything.
    The line was still printed, above the fold, on the only published
    issue, and the two editorial grades that ran in between say nothing
    about it. The page had even been edited that morning, to apply a taste
    ruling given that morning, four lines from the bottom of the same file.
    The tell is not a phrase and it is not in the prose at all, which is
    why this list is where it belongs: every other entry here is checked
    by reading the artifact, and this one is checked by reading the
    register's own tail for entries that are still true. The question to
    ask of any entry ending in a ledger filing is whether anything that
    runs again would notice if the fix never arrives. Where the answer is
    no, the entry is a description and not a defence, and the register has
    confused writing something down with doing something about it (L-A9
    at one remove, because the rule was recorded and the recording was
    itself the enforcement anybody expected).
    Added 2026-09-30 from the grade of the published 2026-W39. Enforced
    the same day in the canon's grading procedure, which gains a sixth
    pass re-verifying every entry of this kind against the live artifact
    and printing the check, and in the standing rule at the top of this
    file, which gains a third ending. Both are enforced at the reliability
    of a model reading a file, which is the weak enforcement L-A22 names,
    so the command form is filed for the engineer in docs/ideas.md in the
    same pull request: a grep for the withdrawn string scoped to
    `site/content/issues/` and the stored bodies, which has no false
    positives and fails until the archive is correct
    (`INC-2026-09-30-standing-defect-unverified-for-three-grades`).

76. The specimen that fits the payload. Entry 53 is the prohibition that
    quotes the string, entry 56 is the example that supplies the frame, and
    entry 65 is the test that asks for the banned sentence. All three were
    answered with the same remedy, which is to hold specimens at the end of
    the generator where finished output is read rather than where a line gets
    written. That remedy is not the rule, and this entry is the proof.
    The heading gate added on 2026-09-28 to enforce entry 69 sits at the very
    end of prompts/digest.md, exactly where those three entries say a specimen
    is safe, and it quoted the offending heading verbatim. The print of
    2026-09-30, written by the prompt carrying that sentence, printed that
    heading verbatim over the same self-dismantling body, on the same two
    numbers. Meanwhile the four slot names are quoted eight times in the same
    file, several of them in the same gate, and have never printed once.
    So position is not what makes a specimen dangerous. Aboutness is. The slot
    names are about nothing a paper could be, so there is no moment where
    writing one is the obvious next move. "The 82.2% ceiling was not a
    ceiling" is a well-formed heading about a result sitting in the payload,
    so at the instant the model reaches that section it is not a warning, it
    is the best available draft. The test, and it applies to any prompt and
    any register: ask whether the specimen could be true of the material the
    writer is holding. Where it could, the specimen is a draft however loudly
    the sentence around it says otherwise, and no amount of moving it down the
    file helps.
    **The count, because one case is an anecdote and this is three for three.**
    The generator held exactly three worked examples about a real paper in the
    payload: the heading above, the claims pass's specimen of two results that
    share only a percent sign, and the same-measure pair of one method printed
    with two scores. All three defects appear in the print of 2026-09-30. Every
    other specimen in the file is about nothing a paper could be, including the
    four slot names quoted eight times and the number line's invented night
    shift, and not one of those has ever printed. The correlation is total and
    it runs the opposite way from position, since the heading gate and the slot
    names sit in the same paragraph block at the end of the file.
    The generator already knew the fix and used it in one place, at the number
    line, whose example is written "in a subject no payload will ever hand
    you, so that copying it is obviously wrong." Added 2026-09-30 from the
    grade of the newest print. Enforced the same day: all three specimens are
    rewritten in invented subjects, the heading gate states the aboutness test
    in its own text, and no worked example anywhere in the generator names a
    real result (`INC-2026-09-30-gate-supplied-its-own-banned-heading`).
    **A footnote that is really the entry's best evidence.** The run that wrote
    this entry broke it about an hour later, in the same pull request, by
    putting two real arrival counts into the instruction that tells the
    generator which count to print. It was caught by re-reading the diff
    against this entry and struck in the next commit. The pull is toward the
    concrete example, it does not spare the person writing the rule, and the
    only defence that has worked is a mechanical sweep of the file for figures
    and quoted output.

77. The evidence grade built on a frame rather than a stem. Entry 70 is the
    grade as a stamp, where three accurate grades opened on "The evidence is"
    and the third had stopped being read. Its fix named the stem: the gate
    forbids opening on the word "evidence" or on any stem already used, and
    requires the grade folded into a sentence doing other work.
    The print of 2026-09-30 obeyed that and produced four grades shaped the
    same way anyway: "One team, three domains, and the effect is large
    enough...", "One benchmark suite, one model family, and the forgetting is
    measured...", "One team, one benchmark, and the latency numbers are
    self-measured", "One benchmark, four models, and the CCE metric is...".
    Two of them open on the same two words, so the print also fails the 2026-09-28
    gate as literally written. All four are one frame with the nouns swapped, and
    the fourth is not a grade at all, because what follows its "and" is a
    compliment rather than a limit.
    The unit is the tell. Entry 70's gate reads the opening words, and a form
    survives every change to its opening words. This is entry 72 inverted: not a
    gate whose unit is wider than the thing it governs, but one whose unit is
    narrower, checking a phrase where the reader sees a pattern. The general
    test: lift every grade out of the issue and line them up. If they read as a
    matching set, they are furniture, whatever their first words are.
    Added 2026-09-30. Enforced the same day: the grade check's unit becomes the
    whole sentence and forbids two grades built on one frame, meaning the same
    parts in the same order however the words change, with the lift-them-out
    test written into the gate.

78. The scale sentence that prints a zero. Entry 60 is a count printed with
    the neighbouring count's verb, and canon law 15 was written from it: the
    library never claims to have read what it only ingested. The law worked.
    The print of 2026-09-30 closed on the week's arrivals with the correct
    verb and then reported, accurately, that none of them had been read in
    full. Every number was right, every verb was right, and the line told a
    reader deciding whether to pay twenty dollars that the product had read
    nothing.
    This is what an honesty law looks like when it is obeyed with no zero case
    written. The instruction offered both numbers in one sentence as the honest
    shape and said nothing about what to do when the second number is zero, so
    the generator printed the zero, which is the one reading of the law that
    damages the product while satisfying it. Law 15 already carries the answer
    in its own text, that an issue saying nothing about its own scale has lost
    nothing a reader came for, and the standing repair for a claim that cannot
    be made is to drop it rather than soften it. Printing its absence is a
    third option the law never offered and it is worse than either.
    A second half rides with it, about reach rather than value. The sentence
    said none were read in full "for this issue", which a subscriber reads as a
    statement about the papers in front of them. Three of the eight papers that
    print carried twelve thousand characters of full text each, and they were
    precisely the three in the reading list. Their distillation timestamps are
    03:18, 03:19 and 03:20 against a payload gathered at 03:13, so the count is
    taken before the reading it counts and understates by the reading list's
    size every single time. The sentence was true for five minutes and false
    before anybody could read it.
    Added 2026-09-30. Enforced the same day in two parts: the close prints no
    scale line at all when the full-read count is zero, and the count is stated
    about the week and never about the items below it. The sampling order is
    the engineer's, filed in docs/ideas.md the same day, because no wording can
    make a number true that was measured before the work it measures.

79. The gate conditioned on a fact its reader was never given. Entry 72 is
    the gate whose unit is wider than the thing it governs and entry 77 is the
    one whose unit is narrower. This is the third shape and it is the quietest,
    because the gate is written correctly and still cannot run.
    `prompts/digest.md` divides itself at the top into house law and
    weekly-only, and the weekly-only part is one demand: the Monday issue
    argues one case rather than listing findings. "A daily may list. Monday may
    not." The payload hands over the week label, the date range, the pipeline
    counts and five lists of material. Nothing in it says which cadence is
    being written. So the single most consequential structural rule in the file
    was conditioned on a fact the writer had no way to look up, and the print
    of 2026-09-30 shows the guess going both ways inside one issue, naming its
    contents as the day's and its findings as the week's.
    The general test, and it is the company's gate standard turned around.
    L-A21 says to name a change that would break what a gate governs and ask
    whether the gate would have seen it. This entry adds the prior question:
    name the fact the gate's own sentence depends on, then find where the
    writer reads that fact. Where the answer is nowhere, the gate has never
    fired and never will, and it has been reporting a pass the whole time.
    A rule conditioned on the calendar, on the reader, on the cadence or on
    anything else outside the artifact and outside the payload is not a rule
    yet. It is a rule plus a missing input.
    Added 2026-10-01. Enforced the same day: the prompt derives the cadence
    from the `dates` field, which spans days for a weekly and names one day for
    a daily, and that is a fact the payload actually carries.

80. The thesis only the close believes. Canon law 9 and the owner's ruling of
    2026-09-19 both say the weekly is the synthesis and must argue rather than
    list. An argument is expensive and a list is cheap, so the cheap thing
    gets written and a sentence of argument gets laid over it at the end, where
    it costs one paragraph and reads, at speed, exactly like the real thing.
    The print of 2026-09-30 closed on "The field is converging on a question:
    how much of the harness can disappear into the model, and what breaks when
    it does?" Five sections printed above it. That question reaches two of
    them. The close names a third by appending it with "And", and two sections
    appear in no frame the issue builds, not the opening and not the close.
    They are in the issue because they were in the payload.
    The tell is not the closing paragraph, which is usually the best writing on
    the page. The tell is a section that no sentence outside itself ever needs.
    Lift each section out and ask which step of the stated case it carries. A
    section that carries none was never part of an argument, and a case that
    does not need three of its five sections was not the issue's case, it was a
    summary of the two sections that happened to rhyme.
    This is entry 67's relative, the promise the issue does not keep, moved
    from the opening to the close. There the issue promises contents it fails
    to deliver. Here it delivers contents and then claims a shape they never
    had.
    Added 2026-10-01. Enforced the same day: before a Monday issue is output,
    the one case is written down as a sentence and every section is matched to
    a step of it, with cutting the section and replacing the case as the only
    two fixes.

81. The gloss spent on the easier of two words. Canon law 12a requires every
    term of art to carry its plain-words clause at first use, and the
    first-use pass in the generator is the longest gate in the file. The pass
    does not fail by skipping the duty. It fails by discharging it, visibly and
    well, on one word, after which the page looks like a page that glosses its
    terms.
    The print of 2026-09-30 handed over its central term in a clause an
    outsider can use and then carried the other term of its own title bare
    through eight appearances, the title, the contents line, a section heading,
    three body sentences, a bold lead and the closing line. Twenty-four terms
    in that issue would have stopped a builder from outside the research world.
    Three carried a clause.
    Two things make this one worth its own entry rather than a note under 54.
    The first is where the bare word sat. A title term is met before the reader
    has any reason to continue, so law 4's one line and law 12a's first use are
    the same line, and failing both at once is the most expensive single way to
    fail either. The second is why the duty did not reach it. The instruction
    to prefer the title's word existed, inside the rule about two names for one
    idea, and the bare word had no second name, so a correctly written duty sat
    in a conditional that never triggered. A duty parked inside another rule's
    scope is enforced only for the cases that other rule happens to cover.
    The general test: a gate that produces a visible success on one instance of
    its subject is not evidence it ran. Count the instances and count the
    successes, and where the subject is a closed list, check the closed list
    first and separately.
    Added 2026-10-01. Enforced the same day: the title's own nouns are a
    closed list, checked first and on their own, with the clause required in
    the title's sentence or the opening's first sentence and nowhere later.
    LANDED prompts/digest.md: "Start with the title, because it is a closed list"

82. The nickname that arrives with "the". The owner's ruling of 2026-09-19
    named this pair in her own words, that nicknames printed "before anyone
    said that teacher and student are nicknames for a big model training a
    small one" read "as gossip about strangers". The first-use pass lists the
    class by name. The print of 2026-09-30 printed one of the listed words
    anyway, thirteen days on, and the reason is a grammatical detail the gate
    had no instruction about.
    The sentence introduced one half of the pair with an indefinite article,
    correctly, and the other half with a definite one in the same breath. The
    definite article asserts that an introduction has already happened. The
    writer feels the introduction, because the two roles arrive together in the
    writer's head, and the reader gets only the half that was named.
    So the tell is the article and not the word, which is why a list of the
    words did not catch it. Any role noun, in any pair, under any nicknames the
    field uses, fails this the moment it arrives with "the" and no antecedent.
    Look for the sentence that INTRODUCES the role rather than the one that
    uses it, and where one sentence hands over one half with "a" and the other
    with "the", the second half is bare however naturally it reads.
    Added 2026-10-01. Enforced the same day: the role nouns get their own
    paragraph inside the first-use pass and the check is on the article, with
    naming the thing in that sentence or dropping the nickname as the two fixes.
    LANDED prompts/digest.md: "the role nouns have their own tell, and the tell is the article"

83. The general sentence over the particular number. The claims pass has four
    questions. Three compare one number against another and the fourth compares
    the issue against itself. All four clear a sentence that invents nothing,
    confuses no measures and still says something the evidence does not.
    The print of 2026-09-30 measured one system on one benchmark and found that
    under a third of its actions mattered. Its heading said that two thirds of
    the whole activity is noise, and the plain-meaning line under it said the
    same about all agents. One system was measured. Every system was described.
    The number is accurate to the decimal and the sentence reporting it is
    false, and no comparison exists anywhere for a comparison test to catch.
    The two places this happens are the two places a figure stops being a
    figure and becomes a statement, which are the heading and the line of plain
    meaning law 14 requires under every result. Both are written after the
    number is settled, both are written for effect, and both are read as
    general by default because that is what a heading is for.
    The test is two namings and a comparison. Name what was measured in full,
    which system and how many and on what task. Name what the sentence claims.
    Where the second is broader than the first, put the measured subject into
    the sentence, which usually costs three words, or keep the general claim
    and drop the number, which means the section has no finding and goes.
    Added 2026-10-01. Enforced the same day as a gate on finished output,
    beside the gate that checks the issue's numbers against each other.

84. The label welded to a sentence by a full stop. Entry 62 and the owner's
    rulings of 2026-09-19 are about taxonomy at the top of a block, and the
    generator's heading gate states the rule correctly, that a label is a
    label at any level and in any typeface. The collection step in front of
    that rule is where this keeps getting through, and it has been escaped
    twice now by the same move.
    The step had two halves. One collected lines, meaning a heading or a run
    of bold sitting alone on a line of its own. The other was added for the
    label that takes no line of its own, and it collected by colon: the text
    in front of a colon, bolded or plain. A print of 2026-09-30 opened four
    of its paragraphs on a bolded label that ended in a full stop. None sat
    alone, so the first half missed all four. None carried a colon, so the
    second half missed all four. One of them was a shape this register
    already condemns with the colon swapped for a period.
    Put the deciding question to any of them and it fails at once: a label
    that says a comparison is about to arrive, or that the next lines are
    what the news means for the reader, would have fitted every issue the
    product will ever send. They are furniture in the one typeface that
    guarantees the eye lands on them first, and a skimmer reading only the
    bolds gets the issue's filing system instead of its story.
    The general tell, and it is the reason this entry is not just an eighth
    string: a unit defined by a punctuation mark is escaped by changing the
    punctuation mark. Seven disguises have now walked past seven checks
    written for the one before, and every one of those checks matched a
    shape. The unit has to be the position.
    One more thing is worth recording about where the shape came from. The
    bold lead is licensed by canon law 14 in exactly one place, inside a
    bulleted list, one lead per bullet. The issue that printed four of them
    set no list anywhere, for the sixth grade running. The ornament arrived
    without the structure it was attached to, which is what an unanswered
    formatting escalation looks like on the page.
    One row appended 2026-10-05, not a restatement. The issue of that day set
    five bold leads and no list, for the ninth grade running, and it is the
    first artifact in this sequence that was NOT the one the escalation's
    patches were written blind against. So the escalation is now tested rather
    than merely unanswered, and the ornament still arrives without its
    structure. The one thing that changed is that the generator's single
    unconditional list requirement, which is the superseded group past two
    entries, was triggered by that issue's three entries and became a count on
    the draft in the same pull request.
    Added 2026-10-02. Enforced the same day: the heading gate's collection
    step loses both punctuation-shaped halves in favour of one positional
    unit, any run of bold or italic that BEGINS a line, whatever punctuates
    it and whether or not the line continues.
    LANDED prompts/digest.md: "any run of bold or italic text that BEGINS a line"

85. The hour recommended with nothing behind it, in the one slot whose format
    had no room for a grade. In-line evidence grades are house law in
    prompts/digest.md and canon law 6, binding every item at every cadence.
    The reading list's format spec named three parts and the grade was not
    one of them: a title, a link, and the line naming the reader's decision.
    So a print of 2026-09-30 carried a grade on every section above and none
    on any of its three picks, and the model was obeying the file in both
    places.
    This is the worst slot in the issue to lose it in, for two reasons. It is
    the only section that asks the reader to spend an hour, and it is the
    section where a whole subfield gets summarised in a clause. An entry that
    declares what the real bottleneck in some area is, on the authority of
    one unreplicated paper, with no number anywhere near it, is entry 83 one
    level up: the general sentence over the particular, with the particular
    left out altogether. The three questions of the claims pass all need two
    figures to compare, so a sentence carrying none of them reaches no check
    in the file.
    The general tell: where a slot's format is written as a closed list of
    parts, that list is the law for whoever fills it, and a duty stated
    anywhere else in the file does not reach inside it. Check every format
    spec against the rules said to bind every item, and where the spec has no
    place to put one of them, the spec is the defect and not the print.
    Added 2026-10-02. Enforced the same day: the reading-list entry carries
    what the work cannot establish inside its own sentence, and the title
    rule is restated there too, because the same print set its picks as
    bolded short names and one of them as a bare acronym where the paper's
    title goes.
    LANDED prompts/digest.md: "The title is the paper's own title, in italic"

86. The posture kept by deleting the verb. A rule written against a class of
    words is obeyed by writing the same thing without any word from that
    class, and the result passes every check the rule can run.
    The reading list banned verbs of presentation and listed them, shows,
    details, presents, provides, introduces and every synonym. A print of
    2026-09-30 contained none of them and opened all three of its entries on
    a bare noun phrase describing the paper: the study of a thing, the case
    for a thing, the model that does a thing. Three catalogue entries with no
    catalogue verb in them. The ban had named the symptom. The posture is
    carried by the subject, and a noun phrase needs no verb to hold it.
    Two of the three then took the same grammatical shape in their second
    sentence as well, against the same slot's own rule that no two entries
    share a shape, because once the opening is a description of the paper the
    sentence that addresses the reader has to arrive afterwards in whatever
    form is left.
    The general tell, and it generalises past this slot: where a rule bans a
    word class, ask what the sentence would look like with the class removed
    and nothing else changed. If the offending version survives that
    deletion, the rule is aimed at the wrong unit, and the unit is almost
    always the grammatical subject. A test on the subject cannot be escaped
    by deletion, because every sentence has one.
    Added 2026-10-02. Enforced the same day: the slot asks what the first
    words of the entry are ABOUT, with the reader, their decision or the
    thing they are about to build wrong as the only allowed answers, and the
    paper arriving inside the sentence rather than at the front of it. The
    frame ban in the same slot is also stated to bind its heading, because
    the sentence banned on the entries printed in the heading instead.
    LANDED prompts/digest.md: "What are the first words of the line ABOUT"

87. The law graded by grep, and the violation that used the synonym. A law
    written as a closed set of exact strings gets enforced with a string
    search, the search is honest and its exit code is recorded, and the
    verdict it produces is about the strings rather than about the law.
    Canon law 12 says framework names never print. The four internal names
    are "Trailblazing", "Gaining traction", "Left behind" and "Read these
    yourself", and five consecutive grades ran the same grep for those four
    over the page, the stored row and the newest print, got no output from
    any of them, and recorded law 12 as a pass on the strings. Runs 21 and
    22 then added "FAIL on the idea" and located the idea in three headings
    and four bold labels, which is correct and is not where the law is worst
    broken.
    It is broken in the second line of every issue the product has ever
    sent. `MASTHEAD` in `pipeline/weekly.py` reads "*What's new in AI
    research, what's gaining acceptance, and what newer evidence has
    overturned.*" Three of the four internal slots, in the file's own order,
    in plain-English synonyms: what's new is the new-work slot, what's
    gaining acceptance is the traction slot, what newer evidence has
    overturned is the fell-behind slot. The grep cannot match any of them
    because not one of the four strings appears, and the line sits 84
    characters into the same body the grep was run over.
    The reason no prompt gate catches it either: the model does not write
    this line. `add_masthead` splices the constant in after generation, so
    the heading gate, which reads finished output and whose first collection
    step takes every run of italic text sitting alone on its own line, reads
    output that does not contain it yet. This is entry 61's class, the
    reader-facing string in code that no pass grades, and entry 64's, the
    standing line whose fix cannot reach what is published. The third thing
    it is, and the new part, is a law whose verdict a grep can satisfy.
    The general tell: where a law names a closed set of strings, the grep is
    the floor of the verdict and never the verdict. Write the law's IDEA as
    a question and ask it of every standing line in the artifact, including
    the ones this seat cannot edit, and name the file they live in. A clean
    exit code on four strings is evidence about four strings.
    And the instrument was instructed. The canon's grading procedure said in
    its own words that law 12 "is the case where this costs nothing" and that
    the verdict is the grep. Five grades obeyed a procedure that was wrong,
    which is why this entry's fix is a correction to that procedure and not a
    note about care.
    Added 2026-10-03. Not enforceable from the prompt, and the reason is the
    splice. Enforcement lands in the canon's grading procedure instead, pass
    3, where the verdict now has three parts and the third asks the idea of
    every standing line with its source file named, and in the
    structure-watch filing of 2026-10-03 in docs/ideas.md,
    which is the third on this line: the first, of 2026-09-20, already named
    canon law 12 and recommended deleting the constant, and it is still
    `proposed` on day 13.

88. The specimen a payload could never have supplied, which is why nobody
    noticed it was still a template. This file defends its own examples with
    one test, stated at the skeleton: "Every example in this file is drawn
    from a subject the payload cannot contain." The test was written against
    the failure where a worked rewrite of an issue became that issue's prose,
    and for examples about research it holds.
    It protects nothing in a specimen that names no subject. A phrase about
    how strong the evidence is is payload-neutral by construction: it fits
    every issue, so there is no subject in it to be drawn from a week the
    generator was not handed, and it passes the test while being directly
    printable.
    The grade rule demonstrated a grade as a sentence counting two units of
    scale and then assessing them. Four hundred lines later the gate banned
    that exact frame by name, "One [unit], [unit], and [the assessment]", and
    recorded that a print carried it four times out of four with two of those
    opening on the specimen's own first two words. The reading-list rule
    listed the same facts in the same shape at the position where its entries
    get written. So the gate forbade the frame while two writing positions
    went on handing it over, which is the 2026-09-30 defect of the gate that
    supplied its own banned heading, repeating in the slot that is house law
    on every item at every cadence.
    The general tell, and it is the test this file's defence was missing: ask
    of every quoted specimen whether it could print verbatim in an issue
    about any research at all. If it could, the subject test does not reach
    it and the position decides. At a writing position, strike it and name no
    replacement, because a replacement offered where the writing happens is
    the next frame. At a gate, where finished output is being read, a
    specimen is evidence and may stay.
    Added 2026-10-03. Enforced the same day: the in-frame grade specimen is
    struck and the rule names no replacement, and the reading-list facts are
    stated as the questions they answer rather than as a shaped sentence.

89. The payload fact that went stale in the prompt. An instruction written
    while looking at one day's data records what that data was, the sentence
    is accurate and useful on the day it is written, and every run afterwards
    reads a verdict on its own input before it has looked at it.
    The traction slot of `prompts/digest.md` carried two, both added
    2026-09-23. "A paper going from zero citations to one, or from one to two,
    is a single reader rather than the field moving, and today all five movers
    are that size." And "`supported_claims` returns claims and never papers,
    so two rows can be one paper: today's twelve rows are ten papers, with two
    of them doubled."
    The newest print was handed twelve citation movers and twelve supported
    claims, not five movers, and it printed no traction section at all. The
    traction slot is section one of every issue at every cadence and the law it
    carries is the owner's oldest, "Traction matters a lot." The one sentence
    in the file that could have told a model to skip it told it, in the
    payload's own units, in the present tense, with the word "today".
    The general tell: a prompt is read on a day it was not written, so a
    sentence in it that describes the input is a claim about a day that has
    passed. The tense is the giveaway. Any "today", "this week", "all five",
    "today's twelve" in an instruction is either a rule stated as an
    observation or an observation that has escaped into the rules, and both
    repair the same way: turn it into the question the model asks of the
    payload in front of it, and let the count be whatever it is. The file may
    say how to judge a stream. It may never say what the stream contains.
    Added 2026-10-03. Enforced the same day: both sentences struck, each
    replaced by the question asked of the payload actually handed over, and
    the first replacement says in its own words that this file does not know
    how many movers there are or how big they are.
    **The sweep, added 2026-10-04, which is what the entry above was missing
    (entry 90).** The two sentences this entry was written from were struck and
    the rest of the file was never checked for the class. The command is
    `grep -n "today's\|of today\|the last issue\|the newest print"
    prompts/digest.md`, and run it every grade until it comes back empty of
    claims about the input. On 2026-10-04 it returned three live hits and a
    fourth inside this entry's own repair, all four struck that day: a
    non-ASCII census in the voice section, a row-and-paper count in the
    new-work slot, a quoted triage note in the reading list, and a payload
    count beside "the newest print" in the replacement above.
    LANDED prompts/digest.md: "This file does not know how many you have or how big they are"
90. The class named and not swept. Entry 89 is the specific defect. This is
    what the run that found it did with it, and the shape is general enough to
    bind every entry in this file from here on.
    Entry 89 was added 2026-10-03 from two sentences in the traction slot of
    `prompts/digest.md`. It is correct, it states its general tell well, and it
    names the giveaway: "Any 'today', 'this week', 'all five', 'today's twelve'
    in an instruction is either a rule stated as an observation or an
    observation that has escaped into the rules." The entry then struck the two
    sentences it had been written from, and nobody ran the entry's own giveaway
    over the rest of the file. One command, the next morning:
    `grep -n "today's\|of today" prompts/digest.md` returned three more. A
    census of one past payload's non-ASCII characters, inside the rule that
    forbids them. A row-and-paper count in the new-work slot, at a writing
    position, pre-deciding how long the section runs. And a quoted triage note
    from one day's `deep_reads`, printable verbatim, in the reading list. A
    fourth sat inside entry 89's own repair, which named a payload count and
    "the newest print", a referent that moves to the issue being written.
    The tell is the asymmetry between how an entry is found and how it is
    fixed. A defect is found in one specimen, because one specimen is what the
    artifact showed. The fix is applied to that specimen, because that is what
    the diff is for. Nothing in between asks the question the entry was just
    taught to ask. An entry that names a CLASS and repairs an INSTANCE has
    recorded a rule and left its own evidence lying around.
    So an entry whose text generalises carries a third thing beside its
    specimen and its enforcement: the sweep. Run the entry's own tell over the
    generator, print the count in the review, and fix every hit in the same
    pull request or say why a hit stays. Where the tell is a command, the
    command goes in the entry so the next run can re-run it rather than
    re-derive it. A count of one, written down, is also a result: it says the
    class has one member and the entry is closed.
    The boundary, because over-correcting this is the obvious next failure. A
    claim about the file's past OUTPUT is evidence for a rule and stays: "the
    last issue printed this file's example lead-in word for word" tells the
    model why a rule exists and nothing false about its input. A claim about
    the INPUT is the defect, because the model cannot check it and will act on
    it. Output is history. Input is a fact the model is about to be handed, and
    this file does not have it.
    Added 2026-10-04. Enforced the same day: the three live hits and the one
    inside entry 89's repair are struck in `prompts/digest.md`, and the sweep
    with its command is written into entry 89's own ending and into pass 4 of
    the canon's grading procedure, where the ban list is read.
    LANDED prompts/digest.md: "This file does not know how many papers are under your rows"
91. The measurement carried forward from the wrong artifact. Not a sentence in
    an issue. A number in the instrument that grades them, which is worse,
    because a figure in a review is the only thing a later run inherits without
    re-deriving it.
    The grade of 2026-10-03 reported, in its law 1 verdict: "The published page
    carries 152 non-ASCII characters and six em dashes." Its measurement table
    carried the same 152 in the published-page column. The published page is
    `site/content/issues/2026-W39.md` and it is pure ASCII:
    ```
    $ file site/content/issues/2026-W39.md
    site/content/issues/2026-W39.md: ASCII text, with very long lines (989)
    $ LC_ALL=C grep -c $'[\x80-\xff]' site/content/issues/2026-W39.md
    0
    ```
    The 152 is exact and it belongs to `2026-W37`, which carries 152 non-ASCII
    characters across seven distinct code points and eight em dashes. It was
    measured correctly in the grade of 2026-09-22, when W37 was the published
    issue, and that review says so in its own words: "152 non-ASCII characters
    in the published file and 134 in the row". Two artifacts later the figure
    was still being reported against whatever "the published page" now meant.
    Nothing was invented and no measurement was taken wrongly. The number
    outlived its subject, which a number in a table does by default, because a
    column heading is a pointer and the figure under it is a value.
    What makes this an entry rather than a slip is that the sentence forbidding
    it was written into the canon's grading procedure by the same pull request:
    "Grade one artifact per verdict. Two artifacts sharing a verdict line is
    where an attribution error becomes invisible." The table in that review has
    one row per metric and three artifact columns, so every row is a verdict
    line shared by three artifacts. The rule was obeyed in the prose and broken
    in the layout, and a table is where a measurement actually lives.
    The cost is specific and it is not the wrong number. It is that a FAIL was
    recorded against a clean artifact, so the one metric the generator has
    genuinely solved reads as its worst. A grade that cannot tell a fixed
    defect from a live one cannot tell anyone when to stop working on it.
    The repair is that a measurement names the artifact it was taken from and
    the command that took it, in the same cell or the row beneath, and is
    re-taken every run rather than carried. Where a figure is inherited from an
    earlier review, it is quoted with its date and its subject, both.
    Added 2026-10-04. Enforced the same day in pass 1 of the canon's grading
    procedure, which is where the measurements are taken
    (`INC-2026-10-04-measurement-attributed-to-the-wrong-artifact`).
92. The enforcement ending that nothing can re-run. The standing rule at the
    top of this file gives an entry three possible endings, and the second one
    is "the change to prompts/digest.md that now enforces it". Thirty-five
    entries carry an ending of that kind. One of them quotes the text that
    landed. The other thirty-four describe it: "the heading gate now reads each
    heading against the block under it", "the grade slot now forbids opening on
    the word 'evidence'", "the shape gate counts the shapes on the page before
    any of the word counts".
    Every one of those is true today. I checked all thirty-four by reading the
    generator, and nothing has been lost. That is the finding rather than the
    consolation: the register's second ending has no failing state, exactly as
    its third ending had none until pass 6 was built for it on 2026-09-30. A
    ledger filing sits at "proposed" and nothing turns red. A prose enforcement
    sits in a sentence nobody re-reads and nothing turns red either. The
    difference is only that the second one happens to be intact, and four runs
    have been editing the generator blind, striking text at the exact positions
    these endings point to.
    The lesson is already in this file and it is in the wrong place. Entry 51
    was corrected on 2026-09-27 and its correction says it outright: "An
    enforcement ending has to name the gate the defect would pass through, not
    merely a place in the file where the rule is now written down." That is a
    standing rule about every entry, recorded inside one entry, where it binds
    nothing and no run reads it as law. It is incident 20's shape at the scale
    of this register: the right words, in the right file, by the right seat,
    read by nothing between the ruling and the artifact.
    So the standing rule at the top of this file gains the requirement, and an
    enforcement ending quotes the text that landed wherever the change is a
    sentence, so a later run can check it with one command instead of a close
    reading. Where the change is a gate rather than a sentence, the ending
    names the gate and the step inside it, which is entry 51's correction
    promoted to law.
    Added 2026-10-04. Enforced the same day as a command rather than a
    sentence, which is `L-A22` and is the only ending this entry could honestly
    carry: `docs/voice/check_voice.py enforcements`. The standing rule at the
    top of this file defines the `LANDED` line the command checks, cites entry
    51's correction as its source, and says to seed the convention on the
    entries a run touches rather than backfilling thirty-four assertions
    nobody verified. Nine entries carry a checked line today.
    Tested against a known failure before being trusted, per `L-A21`: entry
    84's landed text was reworded in a scratch copy of the generator and the
    command reported `FAIL entry 84 (not in file)` and exited 1.
    What is NOT enforced, said plainly because `L-A22` requires it: nothing
    calls this command. Until a command that already runs does, this entry and
    the two before it are enforced at the reliability of someone choosing to
    type it. Filed in docs/ideas.md for the engineer.

93. The specimen that becomes the sentence, at the position where the model
    writes. This register already holds two entries about examples leaking into
    issues, 53 and 88, and both are about where an example is DRAWN FROM: a
    specimen written out of the week being graded is the answer rather than an
    illustration of it. This entry is about where an example SITS. A worked
    sentence quoted inside the slot the generator writes into is the nearest
    available draft, and it wins against any warning attached to it, including
    the words "neither is ever printed".
    The print of 2026-10-05 is the specimen and it carries four in one issue.
    Two lead-ins quoted in the fell-behind slot opened both of its groups
    verbatim, having been quoted there with a note that an earlier issue had
    already printed one of them word for word. A heading of the form "Three
    papers for anyone who ..." printed as the reading list's heading with its
    tail swapped for the day's material, three lines above the file's own
    sentence saying that a phrase quoted inside the slot is not a prohibition
    but the nearest available draft. And the heading rule opened by rendering
    the four slot jobs as plain English clauses, two of which printed as
    section headings, one of them verbatim.
    The tell, for a run reading the generator rather than an issue: a sentence
    in prompts/digest.md that a reader could lift into an issue unchanged,
    sitting inside a `{curly brace}` block or inside the rule that governs one.
    Quoted BANNED specimens are not this tell, because a model copying a banned
    specimen is caught by the ban. A quoted GOOD specimen has no such backstop,
    and the file's own remedy for the "worth the hour" frame is the one that
    works: delete it and name no replacement, because a replacement offered at
    that position is the next template.
    Added 2026-10-05. Enforced by deleting all four, which is the only move
    with a record of working on this class, plus the slot-job rename that
    removed the words two of the headings were lifted from.
    ```
    LANDED prompts/digest.md: "No turn of phrase is offered here, and there will not be one."
    ```
    Re-anchored 2026-10-18. The rule is unchanged and the sentence carrying it
    was rewritten when the generator lost its case history. The old anchor read
    "Two specimen turns stood here and both are deleted rather than re-warned."
    What is NOT enforced, said plainly: the file still teaches by worked example
    at other writing positions and this run did not inventory them, because
    counting them is a different job from grading an issue and a guessed count
    recorded as a sweep is worse than no sweep. Filed in docs/ideas.md.
    **Counted 2026-10-24, writer run 47, and the count is a command now:**
    `python3 docs/voice/check_voice.py specimens`. Three runs declined this
    sweep on the ground above and the last of them wrote "cannot be scored, and
    that is the honest verdict", which was true and is the reason the count had
    to become something other than a run's reading. The inventory and the four
    specimens it found are entry 135, and the one this entry's own tell did not
    reach is there too: a specimen at a writing position can fail the gate
    written to catch it.

94. The evidence grade that ate the meaning line. Not a wording defect. A
    position defect, and the register had no entry for a rule losing to a slot
    rather than to a phrase.
    The generator forbids the standalone grade twice, in its own words: the
    grade is "a clause inside a sentence", and it is "never as a second
    sentence stapled behind it". Both describe what the grade must not look
    like. Neither says where it goes. The print of 2026-10-05 ended seven items
    out of seven on a standalone grade, five of them a noun phrase with no verb
    in it, so both rules were broken at a position neither of them named.
    What it costs is a different law. Canon law 14's sixth rule reserves the
    end of an item for a line of plain meaning with no number in it. The grade
    was sitting in that position seven times, so the issue explained seven
    results and told a builder what to do about none of them. Two rules asked
    for one slot and the file never said which wins.
    The tell: an item whose last sentence names replication, sample size or
    whose experiments these were. Also any grade containing a semicolon, which
    is where that habit is strongest, because the two halves of a grade feel
    like a matched pair and are two sentences.
    Added 2026-10-05. Enforced by fixing the position rather than the wording,
    so the end of an item is declared unavailable.
    ```
    LANDED prompts/digest.md: "The last sentence of an item is not available."
    ```

95. The semicolon nobody was counting. Entry-worthy because of what it reveals
    about the shape of a rule rather than about the mark.
    The generator has named the semicolon for weeks, inside a bullet about four
    punctuation marks, and calls it "banned outright by canon law 1". The print
    of 2026-10-05 carried eight, against one in the print before it, and all
    eight were the same construction: two finished sentences in a balanced
    contrast, which is the shape that feels most like craft. The same issue
    carried zero em dashes and zero non-ASCII characters.
    The difference between the mark that went to zero and the mark that went to
    eight is that one of them was in a count and the other was in prose. That
    is the generalisable half and it has a limit, which entry 96 is about.
    Added 2026-10-05. Enforced as a count at the shape gate, beside the
    character census that holds.
    ```
    LANDED prompts/digest.md: "Count the semicolons. The target is zero and there is no budget, the same as the em dash."
    ```

96. The count that still fails, because it needs the payload and the draft at
    once. The honest limit on entry 95, written in the same run, because the
    tidy version of that lesson is false and a later run would have relied on
    it.
    Entry 95 says a rule stated as a count is kept. Two counts in the generator
    were not. Link coverage says "count before you output. Every item in every
    section carries its own link", and the print of 2026-10-05 named thirteen
    pieces of work and linked three, all three in the reading list, with zero
    links across the other three sections. Grade coverage says to count grades
    against every named piece of work, and that issue graded five of thirteen,
    with its entire fell-behind section ungraded: six named works, every one
    printing a benchmark number, no grade anywhere in the section. That is word
    for word the failure the count rule was written against.
    So the line is not whether a rule says "count". It is whether the check can
    be run on the finished draft by itself. A character census, a semicolon
    tally and a look at how many kinds of block are on the page read only what
    was just written. Counting links and grades against every named work means
    re-opening the payload while holding the draft, and that is the move that
    does not happen.
    The tell, for a run writing a new rule: if obeying the check requires a
    field the model has to go back and look up, the check will not be run, and
    making it louder will not change that.
    Added 2026-10-05. NOT enforceable in the generator, which is the point of
    the entry, and this is its second ending. A gate holding both the payload
    and the output can match named works against links and grades
    mechanically, and the pipeline is the only thing that holds both. Filed in
    docs/ideas.md for the engineer. Law 8 coverage has now failed after a
    prompt fix twice, so the writer charter's structure watch says it stops
    being prompt work at this point.

97. The count as the item's subject. A traction item whose main clause is a
    number moving, with the research it supposedly signals demoted to a
    subordinate clause.
    The specimen is the whole of the third block of the traction section in the
    print of 2026-10-05: "The citation pattern on the earlier distillation work
    also shifted. Rethinking On-Policy Distillation II, which argued that one
    training example suffices, moved from 2 to 4 citations as a newer paper
    showed that 0.1% of tokens can match full-token performance. The claim
    itself is now refined, not merely cited." Three sentences, and the subject
    of all three is our bookkeeping. The one thing in it a builder could use,
    that a newer paper matched full-token performance on a tenth of a percent
    of the tokens, is inside the clause that explains why the count moved.
    This is not a new rule. It is the rule the generator already states four
    paragraphs above the citation-mover instruction, that the payload tells the
    writer why a paper is in front of them and never tells the reader, applied
    to the one stream it had not been applied to. The grade of 2026-10-05 found
    this block, named it a partial fail on canon law 2, did not patch it, and
    wrote it down for the next run.
    The tell, and it reads on the finished draft alone: strike every number and
    every word about counting out of the block and read what is left. If nothing
    survives that a builder could act on, it is not an item.
    Added 2026-10-06. Enforced in the traction slot, where the stream is
    described, rather than in a general rule about numbers.
    ```
    LANDED prompts/digest.md: "A count moving is bookkeeping, and bookkeeping printed as news is the recipe rather than the product."
    ```

98. The shape count that counts lines nobody wrote. An entry about this seat's
    own instrument, because the error was in a grade before it was in an issue.
    Canon law 14's first count is how many KINDS of block are on the page, and
    the canon's own definition names four: a paragraph, a bulleted list, a line
    standing alone, a subheading inside a section. The grade of 2026-10-05
    recorded three kinds for that print and called it "real progress over W39's
    reprint". Counted by that definition it is two, and the print before it
    scored the same two, so the one axis the owner says can fail an issue by
    itself had not moved at all.
    Two ways to inflate it, and that grade used the first while the issue used
    the second. A bold lead opening a paragraph is not a shape, because the
    paragraph is still a paragraph, and the generator asks for a bold lead in
    four places so there are always several to count. And the standing lines are
    not the writer's: of the four non-paragraph blocks in that print, three were
    the masthead, the horizontal rule and the close, all of which arrive on
    every issue whatever the model does. The model wrote one, and it was a short
    paragraph.
    The tell: a shape count that went up without a list or a third-level heading
    appearing anywhere in the artifact. Those are the two devices canon law 14
    names, and if neither is present the count did not move.
    Added 2026-10-06. Enforced in two places, because the defect was in both.
    In the generator, at the shape gate.
    ```
    LANDED prompts/digest.md: "Count only the kinds of block YOU put"
    ```
    Re-anchored 2026-10-18 to the clause rather than the sentence, because the
    sentence now continues into the standing-lines discount and the clause is
    the part the entry is about.
    And in docs/voice/check_voice.py, which now takes the count that canon law
    14 says comes first. It took four of law 14's five counts and not the fifth,
    which is the one the law says can pass the other four and still fail, so the
    instrument measured everything except the axis the ruling is about. The same
    patch lets it be pointed at a path outside the repository, because the canon
    names the stored digests row as an artifact to grade and that row is not a
    file under site/content/issues/, so the one tool written to stop a figure
    drifting off its artifact used to raise an exception rather than measure it.

99. The traction stream with no clock. An entry whose subject is a query rather
    than a sentence, because no sentence can be written that avoids it.
    The print of 2026-10-05 reported a citation movement as that week's
    traction. The movement was measured on 2026-09-28, seven days before the
    issue was written, and it is the newest measurement that exists: the slow
    loop has not written to citation_log since.
    The staleness itself was found the same day by another seat and is in the
    incident register. What belongs here is the half that makes it permanent.
    The citation_movers query in pipeline/weekly.py takes the latest two checks
    for each paper, whenever they happened, and reports any increase. It has no
    time window. So the same twelve movers are handed to the generator every
    Monday for as long as the slow loop stays quiet, and each Monday they print
    as this week's. Run against the live database on 2026-10-06, the query
    returns the identical twelve rows it returned on 2026-10-05, every one of
    them measured in a window that closed on 2026-09-28, and eight of the twelve
    are a movement from zero citations to one.
    The payload then drops the dates. Each mover reaches the generator as a
    title, a url, citations_before and citations_now, so the model cannot tell a
    movement measured this morning from one measured a fortnight ago, and no
    rule written into the prompt can ask it to.
    Added 2026-10-06. NOT enforceable in the generator, and that is the entry.
    Filed in docs/ideas.md for the engineer, in two parts: window the query to
    the issue's own week, and carry the measurement date into the payload so a
    gate and the writer can both see it.
100. The worked example drawn from its own minority case. Six entries in this
    file are about a specimen the model copies as prose (53, 56, 65, 76, 88,
    93). This is the seventh member of that family and the first one where
    nothing was copied as prose at all. What got copied was a MAPPING, and the
    mapping was correct for one input in ten.
    prompts/digest.md carried exactly one string transformation, at the link
    rule: `arxiv.org/abs/2609.11042` becomes `https://arxiv.org/html/2609.11042`.
    The example's input has no version suffix. Of the 7,820 arXiv urls in the
    corpus the generator is handed, 6,994 carry one, so the single example for
    the single transformation this file asks for was taught from the 11% case.
    The print of 2026-10-05 shows what that produces, and the tell is the
    inconsistency rather than any one link. Three links, same issue, same
    model, same rule: `html/2609.29808v1` and `html/2610.01787v1` kept the
    version they were handed and `html/2609.22086` did not. No editor chose
    that. A model following an example whose shape does not fit its input
    splits the difference, and splitting the difference on an identifier is how
    a link stops pointing at a paper.
    Why the grades missed it, which is the half worth keeping. Two consecutive
    reviews graded this law's form and both wrote that the form was clean:
    "three of three are `arxiv.org/html/`". That is a check on the prefix, and
    law 8's subject is the identifier. A link's prefix is the part the rule
    talks about and the part a glance can verify. The identifier is the part
    that decides whether the reader reaches the paper. So the general form, and
    it applies to any register holding an example of a transformation: grade
    the example against the DISTRIBUTION of its real input, not against its own
    internal consistency, and when a rule transforms a string, the verdict
    compares the output to the payload's input character by character rather
    than to the pattern the rule describes.
    Added 2026-10-07. Enforced the same day in prompts/digest.md, which now
    carries a versioned id in the example and the sentence "Only the path
    segment changes. The identifier is copied, character for character, version
    suffix and all." Swept per entry 90: the file holds two arXiv ids and both
    are the one example, so the count is one and this entry is closed in the
    generator. docs/voice/canon.md's worked example under law 14 carries a bare
    id as well, and it is reported rather than struck, because that section
    changes only by the owner's ruling and the canon is never sent to the model.
    Gated the same day, because L-A22 says a rule enforced by a sentence is
    enforced at the reliability of a reading. `docs/voice/check_voice.py links`
    prints each link's path segment and identifier apart and fails when one
    artifact disagrees with itself about the version suffix. It fails the print
    of 2026-10-05 and passes a consistent fixture.
    LANDED docs/voice/check_voice.py: "one artifact disagrees with itself about the version"
    The gate's blind spot is in its own docstring rather than in a later grade:
    an artifact that drops the suffix from EVERY link passes, 2026-W39 is that
    case, and the stronger comparison against `papers.url` is undecidable while
    394 groups of rows hold one paper under several ids.
101. The sign-off written in two moves for a press that sends one. Not a word
    tell and not a page tell. It is a tell of the register this list has never
    had an entry for, which is prose graded in the file it was written in and
    never in the form it is received in. `prompts/digest.md` asks for two
    closing moves after the rule, a line that hands the day back to the reader
    and a line of scale. `parse_issue` in `pipeline/email_render.py` assigns
    the FIRST non-empty line after that rule to the `{{stats}}` slot and drops
    every line after it. So an issue that sets the two moves as two paragraphs
    reaches a subscriber missing one of them, and the one missing is the scale
    sentence, which is the single sentence canon law 15 was written to govern
    and the only sentence in an issue a reader cannot check against a linked
    paper. The print of 2026-10-05 ran both moves in one paragraph and arrived
    whole. Nothing in the generator asked for that, so it was the coin landing
    the right way up.
    The general form, because the tell is wider than the sign-off. A rule in a
    register is about the markdown. A reader is holding the render. Where those
    two disagree the register wins every grade and loses every send, and the
    disagreement is invisible to a reading of either file on its own, because
    each one is correct about its own half.
    Added 2026-10-08. Enforced the same day in prompts/digest.md, which now
    requires one paragraph.
    LANDED prompts/digest.md: "Both moves go in ONE paragraph, with no blank line between them."
    Gated the same day: `docs/voice/check_voice.py delivery` runs the real
    renderer over an artifact and prints every sign-off line the inbox does not
    receive. It passes a clean fixture at exit 0 and names the dropped scale
    sentence verbatim on a fixture that splits the two moves.
    LANDED docs/voice/check_voice.py: "sign-off lines"
    The typography is the filing half and no prompt reaches it. The slot that
    survives is set at 12px in grey monospace below the sign-off, which is the
    register of a system footnote, so the issue's closing judgment is demoted
    even when it is delivered. Filed in docs/ideas.md for the engineer.
102. The list that law 14 requires and the press flattens. Canon law 14 says
    parallel results go in a bulleted list with a short bold lead on each,
    because one shape for a whole issue is what the owner called a hassle to
    read. `parse_section` reads a top-level markdown bullet as the start of a
    new ITEM rather than as a point inside one, so `points` stays empty, no
    marker is set, and the bullets arrive in the inbox as consecutive body
    paragraphs in the same register as the prose around them. The site renders
    the same markdown as a real list, so the shape exists on one surface and is
    undone on the other, after every gate, by code.
    This is not a prediction. `site/content/issues/2026-W37.md` carries
    twenty-three top-level bullets across three sections and the renderer
    produces zero list points from them: ten parallel claims, four overturned
    ones and nine reading-list entries, every one of them set as a list by the
    writer and received as a paragraph. The file's eighteen rendered points all
    come from nested bullets in the one remaining section, so the whole-file
    counts of 27 and 18 hide the defect by adding the two paths together.
    The entry is written now rather than when it bites, because the generator
    on this branch is being patched toward law 14's list and the patch cannot
    reach a subscriber. Correcting one prediction in the register on the way
    past: docs/voice/canon.md's pass 6 says the middle-dot marker at
    `email_render.py` prints "on every bullet" of the first issue that obeys law
    14. It does not. The marker is only reached by an INDENTED bullet, and the
    top-level list law 14 actually asks for never gets that far. The character
    the canon worried about is the lesser half of a defect that deletes the
    shape instead of mis-setting it.
    Added 2026-10-08. No prompt change, because the markdown is already right
    and writing to the parser's shape would be the generator obeying a bug. The
    fix is one branch in `pipeline/email_render.py`, which is not this seat's
    file, so this is the second ending: filed in docs/ideas.md for the engineer
    and reported to the owner as blocking canon law 14 end to end.
    Gated the same day for visibility, which is all a gate can do from here:
    `docs/voice/check_voice.py delivery` prints the top-level bullet count
    beside the rendered point count and fails when an artifact has bullets and
    no points.
    LANDED docs/voice/check_voice.py: "rendered as list points"
103. The opening sentence that sells nothing because it is half a sentence. The
    press prints the opening's first sentence beside the subject line as the
    inbox preview, trimmed at one sentence by `preheader_for`, and a mail
    client shows roughly ninety characters of it. The opening is written to
    begin an issue a reader has already decided to open. The preview has the
    opposite job, which is to make them open it. 2026-10-05's first sentence is
    a hundred and twenty-eight characters, it is the setup half of an either-or
    whose answer is in the sentence after it, and what reached the inbox was
    "You ship agents that improve themselves or you ship agents that stay safe,
    and until this " with the rest cut off and no mark saying so.
    The ledger said this would happen on 2026-09-24, in the entry that built
    `preheader_for`: the derived preview "happens to be good. It is good by
    luck." That entry names this seat as whose call it is, and it has been open
    fourteen days through four editorial runs, because canon pass 6 re-checks
    the filings in this file and nothing re-checks a filing in the ledger
    addressed to this seat.
    Added 2026-10-08. Enforced the same day in prompts/digest.md.
    LANDED prompts/digest.md: "Your first sentence is also the inbox preview, so it has to work alone and"
    Gated the same day: `docs/voice/check_voice.py delivery` prints the preview
    length and the ninety-character truncation, and fails over ninety.
    LANDED docs/voice/check_voice.py: "inbox preview"
104. The slot name cleared from the rule and left standing in the slot. Entry 90
    is the class named and not swept, and this is that failure inside the repair
    of a different entry, which is how it hid.
    The print of 2026-10-05 put three headings on the page that were a slot
    name, a colon, and the day's news. The grade found it the same morning,
    traced the two worst of them to one sentence at the top of the heading rule
    that used to render the four slots as plain English clauses, struck that
    sentence, and wrote a paragraph explaining that a paraphrase of a banned
    heading is the banned heading. Good diagnosis, and it stopped at the rule.
    Two slot BODIES still opened on the same words. The traction body carried
    "a claim gaining ground" and the new-work body's first four words were "The
    genuinely new", which is the second of the three headings that printed,
    sitting four lines below the heading brace it governs. Both were found on
    2026-10-10 by one grep for the phrases the repair itself names.
    The tell is where a repair looks. A rule that explains a leak is read as
    the source of the leak, so the sweep runs over the rule's own paragraph and
    stops, and the slot a few lines down is the position the model actually
    writes from (L-A23, entry 93). So when a phrase is struck anywhere in this
    generator, grep the whole file for it before the commit, including the slot
    bodies, including the file's own prose about itself, and print the count.
    One hit is a result. Entry 89 found three that way and entry 90 was written
    to make it routine, and neither of them reached across into another entry's
    repair.
    Added 2026-10-10. Enforced the same day: both phrases rewritten in plain
    words that are not headings, with the reason recorded in the heading rule so
    a later run does not restore them as explanation.
    LANDED prompts/digest.md: "The words were struck from this bullet and left standing in the slots"
105. The enforcement that merged and never deployed. Not a prose tell. It is a
    defect in every ending this register has, and in the command written to
    check them.
    `prompts/digest.md` is read by a job inside a container image. The image is
    built by a deploy, nothing in this repository performs one automatically,
    and the press runs on a Monday cron. So the file that writes an issue is the
    file as it stood whenever a hand last deployed, and every "LANDED
    prompts/digest.md" line above asserts an enforcement in a working tree.
    On 2026-10-10 the two were eleven apart:

    ```
    psql "$NEON_RO_URL" -c "select runtime_sha, recorded_at from deploy_runtime
        where app = 'weekly' order by recorded_at desc limit 1"
      -> 0cbc51a0e248 | 2026-10-05 09:00:19+00
    python3 tools/delivery_health.py --surface deploy --no-notify
      -> weekly is 1.1 days behind (13 undeployed commits since 3bbf430)
    git show 3bbf430:prompts/digest.md | sha256sum | cut -c1-12
      -> c48d09624161        # the sha that wrote 2026-W40 on 2026-10-05
    python3 docs/voice/check_voice.py enforcements 3bbf430
      -> 11 FAIL on prompts/digest.md, 4 on docs/voice/check_voice.py, exit 1
    ```

    Six revisions of this seat's work were on `main` and none of them were in
    the machine. The semicolon count, the shape count, the heading repair, the
    one-paragraph sign-off, the inbox-preview rule and the buzzword count all
    read as landed in this file and were absent from the file the press reads.
    The reason this belongs here rather than only in the ledger is that four
    grades named the risk and named the wrong gate. Each one wrote that unless
    the branch merged before Monday, the next issue would come from the same
    generator. The branches merged on 2026-10-08 and the sentence stayed true,
    so the seat was watching a number that does not decide the outcome. The
    tell, for any register in this repository whose entries end in a file
    change: name the path the words take to the reader, and verify the ending at
    the last point on that path that you can read. For this seat that point is a
    git ref, not a branch.
    Added 2026-10-10. Gated the same day, which is the only half this seat owns:
    `docs/voice/check_voice.py enforcements <git-ref>` reads every LANDED path
    at a commit instead of from the working tree, and the canon's artifact check
    now takes three shas rather than two, so a grade says what wrote the last
    issue, what is on the branch, and what the press holds.
    LANDED docs/voice/check_voice.py: "read from   "
    The deploy itself is the engineer's and it is filed and URGENT in
    docs/ideas.md on 2026-10-08 and carried on 2026-10-10, so it is confirmed in
    place here with this seat's evidence rather than filed a second time.
    **And it has already cost a reader once, which makes this a specimen rather
    than a forecast.** `MASTHEAD` in `pipeline/weekly.py` lost its false reading
    claim in commit `cb99c37` on 2026-09-26, two days before a Monday send.
    The row that send wrote carries the old constant word for word:

    ```
    psql "$NEON_RO_URL" -c "select split_part(body, chr(10), 3) from digests
        where week = '2026-W39'"
      -> *The latest in AI research, read in full and distilled weekly: ...*
    git show cb99c37^:pipeline/weekly.py | grep -A4 '^MASTHEAD'
      -> the same sentence, which that commit deleted
    ```

    `add_masthead` splices the constant unconditionally, so the only way that
    text reaches a row written on 2026-09-28 is an image built before
    2026-09-26. Entry 64 read this defect as a fix that cannot reach what is
    already published, which is true of the archive. The send is the half that
    entry missed: the correction did not govern the next issue either. Canon law
    15's own founding specimen was therefore live in an inbox after the code was
    right, and nobody could see it, because every gate in this register reads
    the repository.
106. The figure still wearing the units and the precision of the table it came
    out of. Two tells with one cause, and the cause is that a number was
    transcribed where every other word on the page was written.
    The print of 2026-10-05 reported one kill switch latency twice. The opening
    and the item's own bold lead gave it in microseconds, which is the unit that
    makes it a single digit. Two sentences later the result itself arrived as
    "0.0048 ms, with a 95% confidence interval of [0.0042, 0.0057] ms". The
    conversion is exact, neither figure is wrong, and a reader meets one
    measurement as two numbers with nothing on the page saying they are the
    same one. They cannot tell whether the lead was rounding or describing
    something else until they have done the arithmetic themselves.
    The second tell is the decimal that ends in zero. The same print carried
    "86.20%", "97.40%" and "3.87-10.70 points". A trailing zero in a decimal is
    not a precision anybody chose. It is the width of a column, and it tells
    the reader that the second place was never considered, in a product whose
    whole promise is that somebody considered it.
    What makes this entry worth a number is where it hid. The claims pass's
    fourth question has read this artifact five times and cleared it every
    time, because that question compares two numbers on one measure and asks
    whether they agree. These agree. The question's unit of comparison was the
    numeral, and a unit change makes one quantity into two numerals that look
    nothing like each other, so the gate built to catch a figure disagreeing
    with itself cannot see a figure repeating itself in disguise. The
    generalisable half: a check that compares printed forms is a check about
    printing, so convert, normalise, or count before comparing anything a
    reader will read as a quantity.
    **Swept per entry 90, and the count is one, which closes it.** The tell is a
    gate whose comparison is a printed form:

    ```
    $ grep -n "the same number\|the same string\|identical\|verbatim" prompts/digest.md
      -> 12 hits, read by hand
    ```

    One is the gate repaired here. One is the counted-quantities gate, which
    compares a word against a tally and already says to count what is under the
    sentence rather than to read it, so it normalises before it compares. The
    other ten are about repeated wording and standing lines, where the printed
    form is the subject and comparing it is the point.
    Added 2026-10-11. Enforced twice the same day, as a conversion step in the
    gate that reads the figures against each other, and as a ninth count at the
    shape gate, because the leading zeros and the trailing zeros are both
    visible in the finished draft alone.
    ```
    LANDED prompts/digest.md: "Compare the quantity and not the numeral, because the same number in two units is two numbers to a reader."
    ```
    ```
    LANDED prompts/digest.md: "A ninth count, for the figure still wearing the units and the precision of the table it came out of."
    ```

107. The heading written from the issue's argument instead of from its own
    items. Not a label, which is what every previous heading entry in this
    register is about. This heading is specific, it is this day's, and it would
    be false over any other day's material, so it passes the one question the
    heading gate puts to everything it collects.
    The print of 2026-10-05 headed its fell-behind section on the assumptions
    that let agents run unchecked, which is the thread its opening had named and
    a good thread. Four things fell behind under it. One was an audit bound that
    turned out not to hold, one was a recursive self-improvement claim, and two
    were robot manipulation benchmarks superseded by harder ones. Two of the
    four are not assumptions about anything running unchecked, and nothing in
    the body argues with the heading or withdraws it. The section is simply not
    about what the line above it says it is about.
    The tell is a heading that names a property rather than stating a result,
    because a property is a claim about every item underneath and a result is a
    claim about one. "What fell behind: the assumptions that let agents run
    unchecked" asserts four times. The gate's existing step catches the heading
    a body dismantles, which is a contradiction, and this is a coverage failure,
    so there was nothing between the two to catch it.
    Why the argument is the source and not carelessness: this file requires the
    weekly to argue and requires every section to pick the argument up, so a
    writer holding one thread and four headings will write the thread into the
    headings, where it reads as craft. The argument belongs in the opening,
    where it is a claim about the issue. A heading belongs to its block.
    **Swept per entry 90, and the sweep found the condition rather than the
    phrase.** The fell-behind slot already carries the right rule, in these
    words: name the belief that fell "if one belief carries the section". Four
    unrelated beliefs fell that week, so the condition was false and the model
    wrote the conditional form anyway. A rule whose guard is a subordinate
    clause has no step where the guard is evaluated, which is this register's
    oldest lesson in a new position: the count is the gate and the clause is a
    description of one.
    Added 2026-10-11. Enforced twice the same day, as a count at the heading
    gate, beside the withdrawal check it was invisible to, and in the slot
    itself, where the condition is now a thing to check and carries the shape to
    use when it fails.
    ```
    LANDED prompts/digest.md: "A heading that names a property is a claim about every item under it."
    ```
    ```
    LANDED prompts/digest.md: "check that condition before you use that shape"
    ```

108. The weekly that says today. A period word that names the wrong span, in an
    issue whose own generator settles the span before the title is written and
    then never reads one back.
    The specimen is the published 2026-W40, four lines into the body, in the
    sentence that states the issue's whole case:

    > You ship agents that improve themselves or you ship agents that stay safe,
    > and until this week those two pipelines barely spoke. Today they are the
    > same conversation.

    "Until this week" is right. "Today" is a daily's word, and the two sit in
    adjacent sentences about the same fact, so the reader is told twice what they
    are holding and told it differently both times. Three other period words in
    the issue are correct, which is why this reads as a slip rather than as a
    wrong model of the product. It is the slip that matters: a reader who cannot
    tell whether this is Monday's weekly or Monday's daily cannot tell what the
    next one will be either.
    The generator has the rule and had it the whole time, in its own words at the
    top of the file: "One issue never carries both periods." It is read once,
    before the title, and the period words are written hundreds of words later.
    Every other rule on this register of that shape, the stands-alone tense, the
    attributive subject, the counts, the headings, the slot names, ended up with a
    gate that reads the finished text, because a rule read at the start of a long
    piece of writing is a rule in force for the first paragraph. This one had no
    gate and the sweep of the whole file for the word "cadence" finds it in ten
    places, none of them in the gates.
    Six grades never mentioned it. The reason is worth recording, because it is
    this register's commonest shape: no verdict owns the cadence. Law 11 is about
    length, law 13 is about standing alone, law 9 is about structure, and the
    period word falls between all three.
    Added 2026-10-12. Enforced the same day as a gate on finished output,
    immediately before the law 15 gate, reading every period word back against
    the cadence the payload settled, with one narrow exception for a period word
    inside somebody else's claim.
    ```
    LANDED prompts/digest.md: "Each one is either the cadence you settled or it is wrong, and the repair is the one word."
    ```
    **Swept 2026-10-13, which entry 90 required on the day this was written and
    the run that wrote it did for entry 109 only.** The sweep found the supply,
    the same way 109's did:
    `grep -nE "\b(Today|today|this week|yesterday)\b" prompts/digest.md`
    matched 49 lines. Most are this file talking to the writer, and the top of
    the file settles those in its own words: where it says "this week", a daily
    reads it as "today". Note the direction, because it is what sorts the rest.
    The convention translates "this week" for a daily and says nothing about
    "today" for a weekly, so a specimen carrying "this week" is covered and a
    specimen carrying "today" is a cadence handed to both.
    Three such specimens stood at positions where the model writes rather than
    at positions where it is instructed. The contents-line example opened on
    "Today, a dense reward that moved terminal agents fifteen points", in the
    opening slot, which is where "Today they are the same conversation" printed.
    The two absence specimens, at the citation-movers rule and in the
    fell-behind slot, both ended on "today" where the sentence needs no period
    word at all. All three are struck in the pull request of 2026-10-13.
    One specimen with a period word stays and the reason is custody: "Context
    beats architecture this week" is the owner's own example of a craft heading,
    quoted from her ruling in docs/voice/taste.md, and this seat does not strike
    her specimens.

109. The count that is right about how many and wrong about what they are. A
    collective noun covering a group none of whose members it is true of, under
    a number that is exactly correct.
    The specimen is the opening of 2026-W40:

    > Three labs showed that an agent can edit its own harness for four dollars,
    > that a POSIX signal can stop a rogue run in five microseconds, and that the
    > memory you write into weights may be the memory you lose.

    Three findings follow, three sections deliver them, and the second is "An
    independent researcher, Jose Luis Pino", which the issue's own item says sixty
    words later. The number is three and it is right. The noun is "labs" and it is
    false of a third of what it covers.
    The tell is the collective noun under a count, because a collective is a claim
    about every member in exactly the way a heading is a claim about every item
    under it, which is entry 107. The two entries are the same defect in two
    positions, and the reason neither gate caught the other's is that the counting
    gate was written to check arithmetic and the heading gate was written to check
    specificity. A number and a noun arrive in one phrase and only the number was
    ever read.
    The repair is the plainer noun, "three results" or "three separate pieces of
    work", or dropping the collective and naming them. Not the hedge: "three labs
    and one independent researcher" over a group of three is worse writing and
    still wrong about the count.
    **The generator supplied this one, and the sweep is the evidence.** Per entry
    90, the tell was run over `prompts/digest.md` before it was patched:
    `grep -nE "\b(Two|Three|Four|two|three|four) labs\b" prompts/digest.md`
    printed five hits outside the gates, at the bullet rule, the heading example,
    the greeting's safe form, and both contents-line examples. Three of those five
    sit at positions where the model is writing the opening, which is where "Three
    labs showed" was printed. Four are struck in this pull request. The fifth, at
    the bullet rule, states a condition rather than supplying a sentence, and it
    stays.
    **This entry is four days late and that is its own finding.** The defect was
    found on 2026-10-08 by pass 5, written into that review, given no entry and no
    patch, and found again on 2026-10-11 inside a PASS verdict as the clause after
    "except". Recorded as
    `INC-2026-10-12-a-finding-that-lived-only-in-a-review-had-no-failing-state`,
    and the procedure change is in the canon: every pass's new defect becomes an
    entry here, or the review says why none can hold it.
    Added 2026-10-12. Enforced the same day at the counting gate, which now names
    the members and asks whether the noun is true of all of them before it checks
    the arithmetic.
    ```
    LANDED prompts/digest.md: "A collective noun is a claim about every member, the same way a heading is a claim about every item under it."
    ```

110. The thing that did the research, hiding in a relative clause. The
    attributive subject entry 82 named, moved one clause to the right, where
    the gate written against it cannot see it.
    The specimens are the fell-behind section of 2026-W40, and every one of
    them sits in a sentence whose own subject the gate would clear:

    > Task-adapted low-level VLA policies **that reported** 86.20% on RoboTwin
    > 2.0 and 97.40% on LIBERO are now outperformed by two separate approaches:
    > Latent Interface Training, **which improves** LIBERO-Plus success by
    > 3.87-10.70 points, and Dynin-Robotics, **which attains** 78.4% on a
    > Franka Research 3 robot.

    The gate for this was in the generator in full, and in the deployed file,
    on the day that printed. It reads "find every sentence whose subject is a
    benchmark, a method, a pipeline, a system, a dataset or a paper title". A
    writer asking what that sentence's subject is answers "policies", moves on,
    and never reaches the three clauses doing the attributing. Six of these
    printed and five were subordinate.
    Two nouns compound it, and neither is on the gate's list. A study and an
    analysis are things rather than people, so "New paired feedback studies
    show 30 truthful recoveries" and "Ablation shows the combination beats
    either alone" are the same defect in words the list never named.
    This is the fourth entry on this register whose defect moved position
    rather than form: entry 93 was the turn sentence, entry 94 was the grade's
    position after its words were fixed, entry 108 was the period word written
    hundreds of words after the rule, and this one is a clause. Recorded as
    `INC-2026-10-13-a-generator-gate-read-the-main-clause-and-the-defect-moved-right`.
    Added 2026-10-13. Enforced the same day at the attribution gate, which now
    puts its question to every clause and names a study, a paper, an ablation
    and a claim among the subjects that are not people.
    ```
    LANDED prompts/digest.md: "So put the question to every clause, including the ones hanging off which, that and whose."
    ```

111. The item that says nobody did the work. Not a thing in the subject slot,
    which is entry 82 and entry 110. No agent in the item at all.
    The specimen is the whole fell-behind section of 2026-W40, four items, and
    its opening is the clearest:

    > Start with the number that turned out to be wrong. A prior claim held
    > that zero recoveries in 96 challenger episodes yielded a finite-sample
    > upper bound of 0.0468 on recovery probability. New paired feedback studies
    > show 30 truthful recoveries and zero neutral ones.

    A claim held and studies show. No institution, no author, no link, no
    grade, and nothing for a reader to weigh the reversal against. The two
    sections above it attribute every item they carry, so this is a slot
    failure rather than a habit: the counts are 5 of 12 named works across the
    issue and 0 of 4 in that section, and the slot's own rule in the generator
    says "attributed by institution" in those words.
    Why no gate caught it: every attribution gate on this register finds a
    SENTENCE that attributes the work wrongly, and an absence prints no
    sentence. The canon already has this shape written down for law 8 and law
    6, where a grade that inspects the links and grades that exist is the one
    check that cannot find a missing one, and the remedy there was two
    integers. This is the same remedy one register over.
    The repair is the institution from the `institutions` field of the claim's
    own paper, or the named author where the payload has none, and where the
    payload genuinely carries neither, the sentence is written with no
    attributive subject at all rather than with a thing in it.
    Added 2026-10-13. Enforced the same day at the attribution gate, as a count
    of named works against named works attributed to people, which is the form
    the coverage laws already use.
    **Corrected 2026-10-18, and the correction is about the repair rather than
    about the tell.** The entry above names the repair as the institution from
    the claim's own paper, and the four specimen items come from `deprecated`
    and `superseded`, which carry no institution and no author at all. So the
    first repair was never available to the section this entry is about, and
    nor was the second, and the gate as written was counting those four as
    misses for not inventing a name. The tell stands exactly as written: an
    item with no agent anywhere in it is still the defect, and the attribution
    rule's third form is still what fixes it. What changed is that the third
    form is now a pass at the gate rather than a shortfall, and the gate's
    denominator is the named works whose stream carries an attribution field.
    This is the same class as the payload field map added to the generator the
    same day: a rule that asks for a field the stream does not hold is answered
    by substitution or scored as a failure nobody could have avoided.
    ```
    LANDED prompts/digest.md: "every work on it is attributed to an institution or to a named author or the"
    ```

112. The count of its own contents that nobody could check, because the
    sentence picked the unit. Entry 109 is the count whose noun is false of a
    member. This is the count whose number is wrong and whose unit is
    unstated, so the number cannot be shown wrong.
    The specimen opens the new-work slot of 2026-W40:

    > Three papers this week test what happens when you push the agent stack
    > in directions no benchmark yet covers.

    Four items follow it, each a bold lead carrying its own piece of work.
    Three of the four name a paper. The fourth, "Branches that learn what to
    forget", names a team at Meta, Duke and UC Davis, no paper and no link, so
    a writer counting papers counts three and a reader counting items counts
    four. Either reading is a defect. If the fourth is a paper the number is
    wrong, and if it is not a paper then an item in the new-work slot carries
    no paper at all, which is the link coverage entry one register over.
    The gate was in the file that wrote this and it is the gate that calls
    itself "arithmetic rather than judgment". It says to count what appears
    under the sentence and never says what to count, and its four examples,
    three findings, two bets, two labs and both results, are all nouns naming
    the issue's own contents rather than units a reader can see. The file had
    already solved this exact problem one gate over, where link coverage was
    failing until it was told "Count named works, not items, because an item
    can name three of them".
    Ten grades read past it. Two of them had it in front of them: the review
    of 2026-10-06 quoted that sentence in a block of standalone lines
    while counting shapes, and the review of 2026-10-05 was counting where the
    grades sat. A quotation entered both reviews as evidence for one law and
    was never put to the others. Recorded as
    `INC-2026-10-14-a-count-gate-that-named-no-unit-passed-four-items-as-three`.
    Added 2026-10-14. Enforced the same day at the counting gate, which now
    fixes the unit as the blocks a reader sees rather than the noun the
    sentence used.
    The sweep entry 90 requires found one supply and it is struck in the same
    pull request. The honesty rule carried the model sentence "two papers carry
    this week's new work", quoted at a rule that tells the writer what to
    write, and the print took that frame with the count and the verb swapped.
    That is the third time a phrase quoted where the work happens has arrived
    in the issue as the nearest available draft, after the cadence supplies and
    the reading-list heading.
    ```
    LANDED prompts/digest.md: "Count the blocks a reader sees under the sentence, one for every bold lead, bullet or paragraph carrying its own piece of work, whatever noun your sentence happened to use."
    ```

113. The evidence grade that is the same sentence as the last one. Entry 94
    moved the grade out of the position the meaning line needed and left its
    shape alone. This is the shape.
    2026-W40 carried eight grades and four of them open on the identical three
    words:

    > The authors' own experiments, not yet replicated outside the group.
    > The authors' own experiments on GUI agents; no replication yet.
    > The authors' own traffic and benchmarks; no external replication.
    > The authors' own experiments against their Meta-Harness baseline.

    Two more are the same frame as each other, about the same paper, sixty
    lines apart: "One benchmark, one incident autopsy, one prototype" in the
    body and "One incident autopsy, one formal model, one prototype" in the
    reading list. Eight grades, three frames. Every one of them is accurate
    about its own paper, which is what makes this prose rather than error.
    The gate forbids all of it in its own words, and it was in the deployed
    file on the day: "No two grades in the issue begin the same way, none
    begins on the word 'evidence', and no two are built on the same frame."
    Three requirements and no count under any of them, and the step it does
    ask for is a judgment about your own prose, which is the condition canon
    pass 4 already names as the one a tired writer gets wrong. Every gate in
    that list that holds was turned into a count after a print walked past it.
    This one was not, so it has never failed and the frames repeat.
    What it costs is law 6 rather than law 1. A grade is in the issue so a
    reader can weigh one result against another, and four grades reading alike
    tell a reader the four works are alike, which these four are not. One is a
    held-out family of 24 cells, one is five rounds on live Adobe traffic, one
    is a single ablation against the group's own baseline.
    Added 2026-10-14. Enforced the same day at the same gate, as a written
    list of every grade in print order with two string comparisons over it.
    The sweep entry 90 requires found four supplies and all four are struck in
    the same pull request. The in-line grade rule opened on four model grades,
    quoted at the rule that tells a writer what to write, and the first of them
    is the three words this print used four times. A run of 2026-10-05 struck a
    fifth specimen from that same sentence for this same reason and left these
    four standing four lines above it, so the rule forbidding a reused stem was
    the rule supplying it. The two specimens in the rule's second half stay:
    they demonstrate the missing-measurement half, which is a kind of content
    rather than a frame, and this print used neither.
    ```
    LANDED prompts/digest.md: "The first three words of each line, and no two are the same string."
    ```

114. The word the issue leans on hardest, never introduced, because it never
    looked like a word that needed introducing. Entry 81 is the term of art in
    the TITLE with no gloss, which a closed list of three or four words catches.
    This is the thread noun in the body, and it is the commoner case and the
    worse one, because the word is load-bearing in every section.
    2026-W40 leans on "harness" eight times. It arrives in the opening's third
    sentence, "an agent can edit its own harness for four dollars", and it is
    still working in the last line before the close, "whether the $4.03 harness
    from SelfSearch survives independent replication". No clause introduces it
    anywhere in the issue. Four terms carry the issue: that one at eight,
    "weights" at five, and "held-out" and "recursive self-improvement" at three
    each. The count of them carrying a plain-words clause at first use is zero.
    The same count on 2026-W39 was three of three, taken in the review of
    2026-10-01 on that artifact, so this is a regression and not a standing
    state.
    This entry's own first draft said "the three terms" and then listed four,
    which is entry 112 committed in the register that was adding it. Caught by
    running entry 112's gate over this pull request before it shipped, and the
    count is the reason it was caught rather than the reading.
    What makes it an entry rather than one miss is that the rule covering it
    was complete, stated twice, and in the deployed file. The pass says to find
    the first place each term appears anywhere in the issue and that "first
    sentence must carry the term's plain-words clause". It also names the class
    this word belongs to, an ordinary English word doing a technical job, and
    says in its own words that this class "is the one this pass exists to catch,
    because it does not look like jargon on the page and so never gets listed".
    So the requirement is not missing. What is missing is the list. Nothing in
    the pass produces one, and a writer assembling it by eye selects on looking
    like jargon, which is the one property the target class does not have. The
    pass diagnosed its own failure mode in a subordinate clause and then left
    the step that would have answered it unwritten. The two prints it was
    written from failed on this same word, so it has now gone unintroduced
    three times under a rule that covers it in full.
    This is the same shape canon pass 3 already records for laws 6 and 8, where
    a check that inspects what exists is the one check that cannot find what is
    missing, and the remedy there was a count. Here the remedy is a list built
    by frequency, because frequency is mechanical and noticing is not.
    Found by the step added to canon pass 5 on 2026-10-14, which re-reads the
    blocks earlier reviews quoted and puts the laws the quoting verdict was not
    about to each one. The opening was quoted on 2026-10-12 for its cadence
    word and the quotation carries this defect in its third sentence.
    Added 2026-10-14. Enforced the same day at the first-use pass, which now
    builds its list by frequency before judging anything and runs the existing
    clause requirement down it entry by entry.
    ```
    LANDED prompts/digest.md: "Take every word and short phrase in the finished issue that appears three times or more and is not ordinary English doing an ordinary job."
    ```

115. The reading list recommends the papers the issue just finished
    describing, because the gate against it asks the writer to recognise a
    piece of work the issue never names. Entry 112 is the count whose unit was
    never fixed and entry 113 is the shape no count was ever taken of. This is
    the third of that family and the most expensive, because the section it
    ruins is the one asking the reader for an hour.
    2026-W40's reading list carries three picks. All three were described at
    length in the section directly above it, by bold leads that are written
    phrases rather than titles: "Kernel-level preemption in five microseconds"
    against *Hard Stop: Kernel-Level Preemption and Containment for Rogue
    Agentic Execution*, "Not all experience belongs in the weights" against
    *Not All Experience Belongs in the Weights: Component Routing for
    Self-Improving GUI Agents*, and "Procedural memory from real user traffic"
    against *Designer-RSI: Evolving Procedural Memory from User Traffic for
    Agentic Graphic Design*. The fourth item in that section is the one paper
    the reading list does not carry.
    The rule against it was complete, unconditional, and in the deployed file
    at `prompts/digest.md:949` of `3bbf430`: "A paper this issue has already
    covered at length is not a pick. [...] A paper covered anywhere above is
    covered. Drop the overlap and print what remains, even when what remains
    is one paper or none." It even carries the history of its own earlier
    failure, because a previous version named a single payload stream and was
    broadened after one pick slipped through from the traction section.
    What is missing is not the requirement. It is the comparison. The step the
    rule asks for is to check each pick "against the ISSUE you have just
    written, section by section", which is a reading, and a reading for an
    identity the artifact does not print. The body never prints a paper's
    title, so item one is a paragraph about an independent researcher who
    "formalized a containment architecture" and the pick is a full italic
    title, and deciding those are one piece of work is recognition rather than
    comparison. The two slots sit under two different format rules of this same
    file, one asking for a short written lead and the other for the paper's own
    title, so one piece of work carries two strings by design.
    The generator turns on the identity of a piece of work in four places and
    three of them already do it right, on the payload and before anything is
    chosen: `:839` counts the distinct papers in the rows handed over, `:914`
    groups the rows by paper before choosing, and `:1334` builds the one
    written list of named works that the link, grade and attribution gates are
    counted against. This was the fourth, it needed exactly that list, and it
    was the one pointed at the finished prose.
    What it cost is three laws rather than one. Law 11, because seven
    uncovered candidates in `deep_reads` went unprinted while every slot went
    to a paper the issue had already spent a paragraph on. Law 8, because the
    reading list is the only section in this print carrying a link, so the
    three links the issue has sit on three works it had already described
    without one. Law 6, because three papers carry six grades in two
    vocabularies, and the pair on the lead pick is close to verbatim.
    **The comparator is why this is an entry about a gate and not about a
    print.** `press_rehearsals` id 4 is the same model and the same
    `prompt_sha`, five and a half hours earlier, and its reading list carries
    GAVEL, Magenta and Just-In-Time Agent Memory, each appearing exactly once
    in the whole document and none of them covered above. One file, two runs,
    one obeying the rule and one breaking it in every slot. That is what a gate
    asking for a reading is, and it is L-A9 in the position where the standard
    costs most.
    Added 2026-10-15. Enforced the same day at the overlap check, which now
    compares each candidate against the named-works list the link, grade and
    attribution gates already build, matching on the payload's url where there
    is one and on the paper's own title where there is not. The sweep entry 90
    requires found four gates of this class and three were already correct, so
    the count is one and the entry closes.
    **And the ending is stated at its real strength, per L-A22.** The standard
    says that when a law has failed to fire, writing it more clearly is not the
    fix, and that where the check cannot go in a command the rule is recorded
    as enforced at the reliability of reading. This one is. The patch is made
    because it costs a paragraph and aligns this gate with the three that
    already group by paper, and the stronger half is filed in docs/ideas.md on
    2026-10-15 as a pipeline-side comparator, with entry 96 as its sibling.
    ```
    LANDED prompts/digest.md: "The check is a comparison against a list and never a reading of the sections."
    ```
116. The count whose unit only an obedient draft produces. Entry 112 fixed one
    count by fixing its unit, and the diagnosis stopped at that count. This is
    the same defect one step earlier: a gate that triggers on a number, where
    the thing being numbered is a feature of the shape the gate is trying to
    produce. Count it on a draft that already obeys and the number is right.
    Count it on the draft that broke the rule and the number is zero, because
    the objects it counts are what obeying would have created.
    The specimen is the one unconditional list requirement in the generator.
    The fell-behind slot said the superseded group "is a bulleted list and not
    a paragraph" past two entries, and the shape gate's sixth count said
    "Count the entries in that group. Three or more and the group is a list."
    An entry is a thing a list has. A group written as flowing prose has
    none of them, so the count the gate takes on the artifact that failed is
    zero and the gate reports clean.
    **The two prints of 2026-10-05 are what makes this an entry rather than a
    guess, because they fail it from opposite directions and neither one fails
    it by judging the number wrong.** The published body set three superseded
    pairs as three paragraphs of 74, 59 and 33 words. The rehearsal of the
    identical `prompt_sha` set four of them as four sentences inside one
    149-word paragraph, which is the 2026-W39 defect this rule's own text
    quotes back at itself. Run the gate as worded on the second one and it
    counts the entries in a group that has no entries, so the worse print is
    the one it clears.
    The payload is where the number already is. `superseded` carried five rows
    on 2026-10-05, available before a word was written, and the three
    neighbouring gates that work all count the rows handed over rather than
    the items drafted: `:839` counts distinct papers in the rows, `:914`
    groups the rows by paper before anything is chosen, and `:1334` builds the
    named-works list the link, grade and attribution gates are counted
    against. This was the fourth and it was the one pointed at the draft.
    The sweep entry 90 requires, over the class, which is a count whose
    operand is a drafted object:
    `grep -nE "Count the (entries|items|blocks|paragraphs|headings|grades|figures|semicolons|numbers)" prompts/digest.md`
    printed five hits and none of them is an instance. Semicolons at `:1697`,
    colon-carrying headings at `:1723` and leading-zero figures at `:1744`
    count characters and figures, which are in the draft whatever shape it
    took. `:2149` counts items in a section, the same. `:1974` is the one that
    was this class and entry 112 already fixed it, in those words: the unit is
    fixed there and not the writer's to pick. **A count of one, which closes
    the entry.**
    **Then the generalisation question, and it has one honest answer this
    patch does not reach.** Restated in a different part of speech the group is
    counted as pairs or replacements rather than entries, and the patch
    survives that, because a `superseded` row is a fixed object with a name in
    the payload. Restated in a subordinate clause, where a pair is folded into
    another item rather than standing as its own, the row is still printed and
    still counts. Restated in a different POSITION it is not caught at all:
    the parallel-results list in the traction slot at `:849` and in the
    new-work slot at `:876` have no count in them, because their trigger is a
    judgment about whether the day's results are the same kind of thing. A
    count cannot be fixed where there is no count, so those two keep failing
    invisibly and that is a filing rather than a wording.
    Added 2026-10-16. Enforced the same day in both positions, the composition
    slot and the sixth count, because the slot is where the prose is written
    and the count is where it was being checked too late.
    ```
    LANDED prompts/digest.md: "because that count is the shape and the shape is not a revision"
    LANDED prompts/digest.md: "Count the `superseded` rows that group came from, NOT the entries you can see in the draft"
    ```
117. The name spelled wrong to satisfy a rule that exempted it. Entry 40 is a
    mark doing a full stop's job and the ASCII rule has been in this generator
    since the voice overhaul, stated as a question put to every character:
    is this plain ASCII? It carried its exception in the same breath, "a
    person's or an institution's name as the payload spells it", and the
    exception had no direction. The rule says what to strike. Nothing said
    what to keep, and the paragraph underneath it says to assume every string
    handed over is contaminated rather than checking whether this one is.
    So the print of 2026-10-05 wrote:

    > An independent researcher, Jose Luis Pino, formalized a containment
    > architecture that halts rogue agent execution

    `select authors from papers where id='arxiv:2609.29808v1'` returns
    `{"José Luis Pino"}`. The issue misspelled a named researcher in the one
    sentence that attributes the work to him, and it scored zero non-ASCII
    characters doing it. The rehearsal of the identical `prompt_sha` spelled
    the name correctly.
    This is worse than the ordinary tell because of who it is about. An
    overstated result belongs to a lab and a reader who cares can check the
    link. A person's name is the one thing in an issue the person themself
    will read, and a stripped accent is not a typo the pipeline made. It is a
    rule being obeyed in the direction nobody wrote down.
    The sweep, over the class, which is an exception clause with no direction:
    `grep -nE "[Tt]he one exception|no exception|exception is" prompts/digest.md`
    printed three hits. `:219` and `:308` are prohibitions, "no assumed
    vocabulary and no exception for terms that feel basic" and "Punctuation,
    spacing, separators and mathematical symbols get no exception at all", and
    both point the way a prohibition points. `:306` is the only permission in
    the file and it is the one patched. **A count of one, which closes the
    entry.**
    Added 2026-10-16. Enforced the same day at the plain-ASCII bullet, which
    now states the exception as a step with a direction and names which side
    wins when the count and the name pull against each other.
    ```
    LANDED prompts/digest.md: "A name is copied out of `authors` character for character and is the one string on the page the contamination default below does not run on"
    ```
118. The count that cannot hold its own rule's exception, and the grade that
    read the count as the verdict. Entry 117 is the generator half of one
    morning's defect. This is the instrument half, it is the more general of
    the two, and it is about this seat rather than about the model.
    `docs/voice/check_voice.py measure` printed a bare non-ASCII census, one
    row per character with a count beside it, and set a non-zero exit on any
    hit. The rule it was built to measure carries an exception. A count has no
    way to express one, so the instrument scored the two prints of 2026-10-05
    exactly backwards: the body that stripped a researcher's accent exited
    clean at zero, and the body that spelled his name as the payload spells it
    exited non-zero at one.
    **The cost is on the record and it is a verdict in this seat's own
    register.** The grade of 2026-10-15 quoted that figure as evidence, in its
    own words, that the rehearsal "carries one non-ASCII character" and is
    therefore "worse under law 1". The character was an acute accent in José
    Luis Pino's name. Canon pass 1 has said since 2026-10-04 that a FAIL
    recorded against a clean artifact is worse than no grade, because it hides
    the one thing the generator has solved and nobody can tell when to stop
    working on it, and that sentence was written about a figure carried from
    the wrong artifact. This is the same sentence failing on a figure measured
    from the right artifact with the wrong unit.
    The sweep, over the class, which is a gate stated as a target of zero
    against a rule carrying an exception:
    `grep -nE "target is zero" prompts/digest.md`
    printed five hits, at the buzzword scan `:262`, the semicolon count
    `:1697`, the colon-carrying heading count `:1724`, the uncompared figure
    `:1734` and the trailing-zero scan `:1756`. Every one of those rules is an
    unconditional prohibition with no exception in it, so zero is the honest
    target for all five and none of them is an instance. The one rule in the
    org that carries an exception was never stated as a count in the
    generator at all. It was a count only in this file. **A count of one,
    which closes the entry.**
    Added 2026-10-16. Enforced the same day in `docs/voice/check_voice.py`,
    where the census now divides the characters by unicode category, which is
    the division the rule's own words make: punctuation, spacing, separators
    and symbols are scored and set the exit code, and a letter is printed with
    the word it sits in and handed to the grade, because the exception turns
    on whose name it is and no command knows that.
    ```
    LANDED docs/voice/check_voice.py: "the division is the character's unicode category and not the word it sits in"
    LANDED docs/voice/check_voice.py: "A letter is reported and left to the grade rather than scored, because the rule's exception turns on whose name it is and no command knows that."
    ```
119. The gate whose reason is a false claim about the artifact. Entry 115 was
    written yesterday, correctly, about a check that asked for a reading. Its
    repair carried a reason, and the reason is the defect this entry is about,
    because a gate that tells the model something untrue about its own output
    has spent the model's attention on a fiction.
    The sentence, in the generator for one day: the sections above name a paper
    by a written lead and this slot names it by its full title, "so one piece
    of work carries two different strings and recognising them as one piece of
    work is the step that does not happen."
    Two different strings, yes. Independent strings, no, and that is the whole
    question, because a lead written from a paper carries the paper's own
    words. Lowercase the bold leads of the print of 2026-10-05 against the
    titles of its three picks and every one of the three shares a run of three
    or more words with the lead that covered it:

    ```
    kernel level preemption                      lead 1 against pick 1
    not all experience belongs in the weights    lead 2 against pick 2
    procedural memory from                       lead 3 against pick 3
    ```

    The fourth item, the parallel-branch work, shares nothing with any pick,
    and it is the one item whose paper the reading list does not carry. Three
    true, none false, on the artifact the gate was written from.
    **How the false reason got written is the part worth keeping.** Item one of
    that section is a paragraph about an independent researcher who
    "formalized a containment architecture" and its pick is *Hard Stop:
    Kernel-Level Preemption and Containment for Rogue Agentic Execution*, so
    on item one the claim is nearly true and recognising them as one piece of
    work really does take more than a string. Items two and three were never
    looked at. The diagnosis was taken from the first specimen and generalised
    to a set of three, which is the 2026-10-13 class with the specimen in the
    diagnosis rather than in the gate, and it cost more than a sentence: the
    stronger fix was routed out of the prompt and filed for the engineer on
    the stated ground that no comparable string exists.
    **The sweep, and it is the inverse pattern that makes the result readable.**
    The class is a gate that declares a comparison impossible or unavailable:
    `grep -nE "because (the|this|it|one|a) [a-z ']{0,40}(never|does not|cannot|has no|is not)" prompts/digest.md`
    printed thirteen hits. Twelve are reasons about a class of writing rather
    than claims about what the artifact contains, and the thirteenth is the one
    patched. Two further lines run the other way and both are correct and both
    stay: `:1336` and `:2186` each say that a candidate passing "only because
    it failed to match a string" has not been checked at all. Those two are why
    the repair adds the string comparison as a first pass and keeps the list
    match, rather than replacing one with the other. **A count of one, which
    closes the entry.**
    **The determinacy of this one is not the usual argument and it should not be
    read as one.** `docs/voice/check_voice.py compare` puts the overlap axis in
    the undetermined class, so by the standard this register adopted today a
    further wording of it is not a test of anything. This patch is made anyway
    and on a different ground: a gate carrying a false statement is a defect
    whether or not fixing the statement changes an outcome, and the measurement
    of whether it does belongs to the comparator filed on 2026-10-15.
    Added 2026-10-16. Enforced the same day at the overlap check, which now
    names the comparison and the three specimens it catches.
    ```
    LANDED prompts/digest.md: "Take the short bold lead of every item you wrote above and the title of every candidate pick, lowercase both, and strike the pick wherever the two share a run of three or more words."
    ```
120. The gate whose floor sits above its own failing state. Canon law 14's
    first count is how many kinds of block are on the page, and that law says
    in its own words that one kind is a failing issue whatever the paragraph
    lengths say. The generator's shape count says the same and goes further,
    naming the blocks that do not belong to the writer: "the lines you did not
    write are not yours: the standing line under the title, the rule above the
    close, and the close itself arrive on every issue whatever you do."
    `docs/voice/check_voice.py` counted them anyway. Three of them are
    standalone-line blocks, so every issue this press can produce carries at
    least two kinds before the generator writes a word, and the row read 2 on
    the two prints of 2026-W40.
    The proof is one deletion. The published body's only non-paragraph block
    the writer actually wrote is the sentence "Three papers this week test what
    happens when you push the agent stack in directions no benchmark yet
    covers". Strike it and the writer's honest count is one kind, which is the
    categorical failure. The row still read 2, and `measure`'s own line, "one
    kind of block is a failing issue (canon law 14)", had been unreachable
    since it was written on 2026-10-06.
    **The cost is that the number was right by luck and read as a verdict.**
    Two prints of one generator scored 2 and 2, and the grade of 2026-10-16
    concluded from that pair that both were equally grey and that "the one with
    the longer sections put fewer shapes on it". Counting only the writer's
    blocks, the published body carries one standing line and the rehearsal
    carries thirteen. The axis counts kinds and nothing counted instances, so a
    thirteenfold difference in the exact device this law asks for arrived as
    two identical numbers.
    The sweep, over the class, which is a count whose operand includes blocks
    the rule it serves excludes: five counts in that file read blocks or the
    whole text. The shape count is this entry. The per-section count is entry
    121. The semicolon, em dash and non-ASCII censuses read the whole text,
    furniture included, and no furniture string carries any of those marks.
    `over100` counts every block, and the longest non-paragraph block in either
    print of 2026-W40 is 19 words against a threshold of 100, so it is in the
    class and cannot err. **A count of two, both patched here.**
    Added 2026-10-17. Enforced the same day in `docs/voice/check_voice.py`,
    where the furniture is named from `MASTHEAD` and `SHORT_EDITION_NOTE` in
    `pipeline/weekly.py` and from the two literal lines of the template, and
    the shape count in `axes` and in `measure` runs over the writer's blocks
    alone. The row is renamed, because the number's meaning changed and a grade
    must not read the new figure under the old name.
    ```
    LANDED docs/voice/check_voice.py: "Did the generator put this block on the page, or does it arrive anyway."
    LANDED docs/voice/check_voice.py: "the generator's own shape count already excludes in its own words"
    ```
121. The count that took a different unit from the rule it enforces, and
    punished the issue for obeying the same law twice. The generator's turn
    trigger is "any section running past about four paragraphs gets a written
    turn inside it". `axes` counted blocks. The other kinds of block in that
    section are the ones this same law requires: a line carrying the number
    that matters, a bulleted list where the results are parallel, and the turn
    itself.
    So the fix for a grey page made the page look long. Every device the writer
    added moved its section nearer a flag, and the flag's own remedy, the turn,
    counted as a paragraph too.
    The measurement, by section, on both prints of 2026-W40:

    ```
    digests 21      4+0  4+1  4+0  4+2    paragraphs + other blocks
    rehearsal 4     3+2  4+4  3+7  4+2
    ```

    Not one section in either print runs past four paragraphs. The row read 2
    and 4 and called both determined failures, so **all six flags were false**,
    and the worst-scoring section in the org was the rehearsal's third, which
    is three paragraphs and seven standing lines and is therefore the single
    best-formatted section either print produced.
    **The cost is a verdict in this seat's own register, one day after the same
    class was recorded.** The grade of 2026-10-16 quoted "the published body
    runs a five-paragraph and a nine-paragraph section" as evidence under law
    14, and ran its own awk count to get there. Canon pass 1: a FAIL recorded
    against a clean artifact is worse than no grade, because it hides the one
    thing the generator has solved and nobody can tell when to stop working on
    it. Entry 118 is the same sentence failing yesterday on the non-ASCII
    census. `INC-2026-10-17-the-instrument-overcounted-the-law-it-was-built-for`.
    The sweep, over the class, which is a trigger whose number carries a unit:
    `grep -nE "(past|over|more than|under|within|fewer than|no more than|at least) (about )?(one|two|three|four|five|six|seven|eight|nine|ten|[0-9]+) [a-z]+" prompts/digest.md`
    printed twelve hits, and the lines below are the file as it ships after this
    patch. The section trigger at `:1740` and its restatement at `:1722` are the
    one patched. The superseded group's "past two entries" at `:1004`, `:1015`
    and `:1758` is this exact class and entry 116
    closed it yesterday. The item-level trigger at `:426` and `:1557`, "an item
    that runs past three paragraphs gets written turns inside it", is the same
    class and no command counts it at all, so it keeps failing invisibly and
    that is a filing rather than a wording. The rest are prose about words and
    sentences with no command behind them. **Two instances, one patched here
    and one patched yesterday.**
    Added 2026-10-17. Enforced the same day in both places: in
    `docs/voice/check_voice.py`, where the per-section count takes paragraphs
    and not blocks, and in `prompts/digest.md`, where the trigger now says
    which blocks are not paragraphs and why counting them turns one half of
    this law against the other.
    ```
    LANDED prompts/digest.md: "Count paragraphs and not blocks, because the other kinds this law asks you for sit inside sections too"
    LANDED docs/voice/check_voice.py: "A paragraph, and not a block."
    ```
122. The model sentence printed verbatim, defended by a subject the payload
    turned out to hand over. The reading-list slot quoted a line as the shape a
    good entry takes, with the defence written beside it: "in a subject no
    payload will ever hand you, so that copying it is obviously wrong". The
    print of 2026-10-05 opened its reading list with that sentence, word for
    word, because the day's payload handed it a paper whose section 4 really is
    scheduling maths.

    > The scheduling maths is in section 4 and it is the part nobody gets right
    > by intuition.

    The specimen entered the generator on 2026-09-26 and the press still holds
    it. The rehearsal of the identical `prompt_sha` did not copy it, so the copy
    is one print's version of the failure and not the failure itself: both
    prints open their reading-list lines on the paper rather than on the
    reader's decision, one of three in the published body and three of three in
    the rehearsal, which is the shape this slot's own subject rule was written
    from. The axis is determined and the patch is testable.
    **The reason this is the third time, and the file already held the answer
    twice.** This slot has deleted two specimens for exactly this: the heading
    frame of the second form, and "Worth the hour if you are". Both deletions
    carry the same reason, that a phrase quoted inside the slot the model writes
    into is not a prohibition but the nearest available draft. Neither deletion
    reached the third specimen thirteen lines below, because its defence was
    subject matter, and subject matter is the one variable a payload controls.
    A quoted sentence is a draft whatever it is about.
    The sweep, over the class, which is a printable sentence quoted inside a
    slot the model writes into: `grep -nE '^\s*(ever hand you|is in|[A-Z][a-z]+ [a-z]+)[^"]*"[A-Z][^"]{25,}"' prompts/digest.md`
    is not the readable form of this one, so it was taken by hand over the four
    slots and the opening. The traction slot and the fell-behind slot quote no
    candidate sentence. The new-work slot quotes one and it is labelled in the
    same breath as a subject no payload hands over, "**Apple.** One model drives
    desktop, phone and browser, and it beats the specialists trained for each",
    and the number rule quotes another, "The night shift closes **83% of
    tickets** before morning, up from 41%". Both carry the defence this entry
    just falsified, and both stay for now with the defence weakened rather than
    deleted, because each is demonstrating a punctuation shape rather than a
    sentence's job and no payload in this product's corpus is about night shifts
    or Apple's desktop. That is a judgment and it is recorded as one.
    **One instance deleted, two left standing with the reason they rest on named
    as weaker than it reads.**
    Added 2026-10-17. Enforced the same day at the reading-list line rule, where
    the specimen is deleted and the three shapes it illustrated are described
    instead.
    ```
    LANDED prompts/digest.md: "Nothing in this slot is ever handed to you as a sentence you could print"
    ```
    Re-anchored 2026-10-18. The deletion the entry records still stands and the
    rule is now stated positively instead of as a tombstone, which is L-A23 in
    the direction it wants. The old anchor read "A third specimen stood here and
    is deleted, and it is the one that was printed."
123. The grade stapled behind the sentence that was supposed to carry it. The
    reading-list rule says to say what the work cannot establish "inside the
    entry's own sentence and never as a second sentence stapled behind it". It
    has failed on six entries out of six across both prints of 2026-W40, and
    every one of the six took the same three-sentence shape: the decision, then
    a sentence counting the units of evidence, then a sentence assessing them.

    > The scheduling maths is in section 4 and it is the part nobody gets right
    > by intuition. One incident autopsy, one formal model, one prototype you
    > can wire into LangGraph today. The latency claim is measured; the breach
    > narrative is single-source.

    That is one entry doing in three sentences what the rule asks of one, and
    its third sentence restates in different words the grade the body already
    gave the same paper sixty lines above ("The latency numbers are reproducible
    ... the breach narrative is not independently verified"), which is law 6's
    two-grades-on-one-work failure arriving through the shape rather than
    through the vocabulary.
    This is the lesson of the semicolon, which this file wrote down on
    2026-10-13 and is the clearest rule it owns: the difference between the mark
    that went to zero and the mark that went to eight is that one of them was in
    a count. This rule has run twice in prose and failed six times out of six,
    the axis is determined by the comparator, and so it becomes a count. The
    count is new rather than a re-wording, which is the distinction the grade of
    2026-10-16 refused to patch across.
    No sweep, because the class is a rule stated in prose that a count can hold,
    and that class is the subject of this entire register rather than of one
    entry.
    Added 2026-10-17. Enforced the same day at the grade rule in the
    reading-list slot, which now names the full stop before the grade as the
    thing to find and sets the target at zero.
    ```
    LANDED prompts/digest.md: "Read each finished entry and find the full stop before the grade."
    ```

124. Provenance standing where a missing measurement belongs. The generator
    asks the evidence grade for two halves, how strong the number is and what
    the work did not measure, and the second half is conditional on the payload
    supporting it. The payload never does. `pipeline/distill.py` stores
    `claim`, `evidence`, `topics` and `procedure`, every one of which records
    something a paper did, and no field anywhere records something a paper left
    out. So the slot gets filled with the nearest true sentence in reach, which
    is who ran the work or who has not repeated it.

    > The authors' own experiments, not yet replicated outside the group.
    > The authors' own traffic and benchmarks; no external replication.
    > The authors' own experiments against their Meta-Harness baseline.

    Six of the seven grades 2026-W40 printed take that shape, and the seventh,
    "no external benchmark", is the only one on the page that names a
    measurement rather than a person. The tell is that the clause reads like a
    limitation, sits in the position a limitation goes, and leaves the reader
    knowing nothing about the work's reach that they did not already know from
    the first half.
    This is not law 6 being broken. Law 6's own example is "authors' own
    experiments, not yet replicated", and that is the right example of the
    FIRST half. The defect is the first half printed twice under one grade,
    with the second half's slot spent on it.
    The strongest evidence that this is structural rather than careless: the
    hand-written rewrite in `docs/voice/benchmark-2026-10-18.md`, composed by
    this seat with the rule open, produced "nobody outside it has repeated the
    result" in the same position. A writer who knows the rule and has the paper
    cannot satisfy it from the payload either.
    No sweep, and no re-wording of the demand, because the demand is not the
    broken part. The missing field is filed for the engineer in docs/ideas.md
    on 2026-10-18. What the prompt can hold is the prohibition on substituting,
    and that is what landed.
    Added 2026-10-18. Enforced the same day at the evidence-grade rule, which
    now puts one question to the second half before it is kept.
    ```
    LANDED prompts/digest.md: "Does the clause name something the work did not measure, or does"
    ```

125. The selling sentence nobody wrote, lifted out of text addressed to a
    machine. Entry 61 is standing copy fixed in code that no pass ever graded,
    and its fix is that an editorial run reads the reader-facing constants in
    code once per run. This is the same failure one move further out, and that
    fix cannot reach it, because the sentence is not a constant and is not in
    the site's code at all.

    `site/lib/skill-shelves.js` takes each skill's `description`, cuts it at
    the first sentence, and the catalogue prints that fragment as the row's
    one-line pitch. The `description` is the text an agent's router matches a
    task against, so it is written for a machine, by the seat that owns
    `skills/`, under a 150-word budget enforced by a trigger test. It is good
    at the job it was written for. What a stranger reads on the page a sprint
    is now selling from is this:

    > Where to enforce the boundary an agent runs inside, and what each choice
    > measures.

    Nothing in it is false, no internal vocabulary appears in it, and entry 14
    therefore passes it. No editorial pass has ever read it either, because the
    string lives in `skills/*/SKILL.md` front matter, which a copy round over
    `site/` never opens, and the function that promotes it lives in a third
    directory that belongs to a third seat. Three surfaces, three owners, and
    the sentence that sells the product is the output of a slice.

    The tell, and it is checkable in one question: **who was this sentence
    written to?** A line in a selling slot that was addressed to a router, a
    schema, an index or another program reads as accurate and sells nothing,
    and her ruling of 2026-09-20 names the register exactly: "no more
    technical. we want to sell." The repair is never to rewrite the machine's
    text, which is correct as it stands and has its own gate. It is to write
    the reader's sentence as a second artifact and to give it somewhere to
    live.

    No sweep, and no change to `prompts/digest.md`, because the generator does
    not write site copy and nothing in a prompt can reach a slicing function.
    The nine candidate sentences are drafted in
    `docs/voice/skills-copy-2026-10-18.md` and the ending this entry carries is
    the ledger entry that asks for the field to put them in, filed
    2026-10-18, because the half this register cannot hold is that there is
    nowhere in the repository for a reader-facing sentence about a skill to go.
    Added 2026-10-18, from the copy round for the catalogue page.
126. The completeness word that belongs to the part, spent on the whole, with
    the true version standing next to it. Canon law 15 is a count given the
    neighbouring count's verb. This is a scope one line wide: a claim that is
    true of the unit, restated about the collection of units, where the
    collection has gaps the unit does not.

    The free column of `site/app/pricing/page.jsx` carries three bullets, and
    two of them are one word apart:

    > Every issue in full
    >
    > The complete archive

    The first is true and it is load-bearing, because the vision's §0 as
    amended 2026-09-17 makes the digest free in full, and `site/lib/content.js`
    enforces it in code: "an issue has no teaser split and no entitlement
    check: the whole body is public." The second takes that truth and moves it
    up a level, from each issue being whole to the series having no holes, and
    at that level it is false twice over. `site/lib/content.js:23` withholds
    2026-W37 from the listing and from its own route on the owner's order of
    2026-09-19, and the press has missed 2026-W41 and W42.

    What makes it a tell rather than a mistake is the adjacency. Neither
    sentence would survive alone in front of a reader who checked, and together
    the first one vouches for the second, so a pass that reads the line above
    arrives at the line below already satisfied. It is ban list 50's mechanism
    with the parts reversed: 50 is a true concession licensing a false
    assertion inside one sentence, and this is a true claim licensing a false
    one across two lines of a list.

    The tell is checkable in one question, and it is not about the word: **what
    is this sentence's subject, the item or the shelf?** A completeness word on
    the item is a promise about craft and it is usually true, because nothing is
    held back from a reader who arrives. The same word on the shelf is a promise
    about a record, and a record is the one thing in a product that an outage
    makes permanently false. The repair is never to soften the shelf's claim,
    which is law 15's rule and 50's: "most issues", "the archive so far" and "a
    complete archive from the pilot onward" are the same false sentence in
    coats. The repair is to say what the shelf actually offers a stranger, which
    here is that arriving late costs nothing and reading costs no account.

    **Swept, and this is the half worth keeping.** Four other lines on the site
    use the same vocabulary and every one of them is correctly scoped.
    `site/app/library/page.jsx:29`, "The weekly issue is free and complete",
    puts the word on the unit. `site/app/library/[week]/page.jsx:51`, "Every
    issue reads like this one, free and in full", the same. The library page's
    heading "Every issue" names the page's own scope, and both it and the line
    under it were approved by the owner on 2026-09-29. So the one defective
    instance is the one line of the five she never ruled on, and the four she
    approved get the scope right. That is the argument for this entry being a
    tell rather than an accident: her ear put the word on the part every time,
    and the copy written without her got it wrong the first time it tried.

    No sweep of `prompts/digest.md` and no change to it, because the generator
    does not write a tier card and no sentence in a prompt can reach a bullet
    in a React component. The ending this entry carries is the ledger entry
    filed 2026-10-18 asking for the gate that could, which is a check that
    reads the archive's published contents and fails a build when a site string
    asserts a completeness or a cadence the shelf does not show. Added
    2026-10-18, from the copy round on the pricing page, where the sentence had
    been live for thirty days.

127. The present tense worn by a machine that has not been built. Eleven
    sentences on the site say something about the quality of what we ship, and
    `docs/agents/quality-claims.md` names the code that would have to run for
    each one to be true. Three of the eleven have it. Four have nothing
    anywhere. The register has said so since 2026-09-30 and the pages have not
    changed, so on 2026-10-18 the mission page still read "proven against the
    same tasks with and without it, revised when the research sharpens it, and
    retired with the reason when the research overturns it", which is one
    sentence carrying a measurement that came back negative, a job that has
    never merged, and a field that does not exist.

    The tell is not a word, and that is what makes it hard to catch by reading.
    Every sentence in this class is grammatical, plausible, and written by
    somebody who believed it, because the thing it describes is the thing the
    org intends to build. Entry 50 is a true concession licensing a false
    assertion, 126 is a true claim about the item licensing a false one about
    the shelf, and this one is a true INTENTION licensing a false tense. The
    question that separates them is one: is this sentence about the research or
    about our artifact? "The research has shown this technique to work" is
    checkable against the corpus and is almost always true. "Each skill is
    proven with and without it" is checkable only against a measured delta, and
    on 2026-09-30 the library's first such measurement came back at 5.4 without
    the skill against 5.3 with it.

    The repair is the one law 15 already gives, which is to drop the claim
    rather than soften it, with one exception the register itself writes down.
    Where the machine is genuinely being built, the sentence may stand in the
    tense of a thing that does not exist yet, which is the form
    `site/app/routines/page.jsx` has used in public since it shipped and the
    form the pricing page already uses in the last bullet of its own paid tier
    while the intro four lines above sells the same routines as running. A page
    disagreeing with itself about whether a machine exists is this entry at its
    clearest.

    The ending, and it is a command rather than a line in the generator.
    `docs/voice/check_voice.py claims` reads every row of the register against
    every reader-facing surface and fails on a claim that is not held and not
    hedged, and on the same claim appearing somewhere the row does not name,
    which is how the revision promise reached three pages. It found seventeen
    live instances on the run that wrote it. `docs/voice/check_voice.py
    reading` does the same for law 15's vocabulary and found three, one of them
    the home page's own metric line, twenty-two days after the repair for it
    was drafted and filed. No sweep of `prompts/digest.md` and no change to it,
    for the reason entry 126 gives: the generator does not write a React
    component. Neither command is called by anything yet, so the ledger entry
    filed 2026-10-18 asks the engineer seat for the wiring, and until that
    lands these two are enforced at the reliability of a seat typing them.
    Added 2026-10-18, writer run 40.
    ```
    LANDED docs/voice/check_voice.py: "A gate that turns red on a file its own seat must not edit gets ignored, which is the failure mode after the failure mode this check exists for."
    LANDED docs/voice/check_voice.py: "The law is about what the library claims to have done."
    ```

128. The false claim whose subject is a pronoun, one sentence past the noun
    that makes it checkable. `site/app/llms.txt/route.js` has said "alexandria
    is an autonomous research pipeline. It reads the week's AI research" since
    the file was written, and that is canon law 15 broken in public on a
    reader-facing surface. Entry 127's command found three instances of the
    same law on 2026-10-18 and did not find this one, because its pattern
    needs the library named inside the sentence that carries the verb, and a
    paragraph that names it once and then pronominalises it has moved the
    subject out of reach while keeping the claim.

    This is not a weakness in that one pattern. It is the general shape of
    every check that keys on a subject, and it is worth its own entry because
    the repair is cheap and the class is wide. A false claim survives longest
    in the second sentence of a paragraph, where the prose has earned the
    right to say "it" and the checker has lost the word it was matching on.

    The owner has already ruled on this word from the other side. On
    2026-09-20 she rejected "it" as the subject of a mechanism sentence and
    named the word herself, so the form here is wrong twice over: false by
    law 15 and rejected by her register, and caught by neither gate for
    twenty-three days. Two rulings pointing at one sentence and no reader of
    either is the argument for the taste gate in the same run.

    The repair is the law's own vocabulary with the subject restored, and the
    candidate open on this surface is `docs/voice/llms-txt-2026-10-18.md`,
    which rewrites the body and already fixes the sentence. No change to
    `prompts/digest.md`: the generator does not write a route handler, which
    is the reason entries 126 and 127 give for the same thing.
    Added 2026-10-18, writer run 41.
    ```
    LANDED docs/voice/check_voice.py: "The subject is a pronoun, which is how three sentences of"
    ```

129. The relative clause spent on the head noun while the term of art rides
    past it. Entry 81 is this failure across an issue, where one word gets a
    good clause and the page then looks like a page that glosses its terms.
    This is the same failure inside a single noun phrase, and it is worth its
    own entry because the reader cannot feel it and no sentence-level check
    can see it.

    The specimen is one sentence of `site/content/issues/2026-W39.md`, which
    carries three club words and one relative clause:

    > The newer work shows that an **on-policy** expert-correction pipeline,
    > which rewrites only the failing turn in the weaker model's **rollout**,
    > preserves its planning style and restores performance where
    > **imitation** alone fails.

    The clause defines the pipeline. "On-policy" is a modifier in front of the
    noun the clause lands on, so it collects the sentence's apparent
    explanatoriness and keeps its meaning to itself. "Rollout" is inside the
    clause doing work. "Imitation" names a training method in a subordinate
    clause as though it were an ordinary English word. The issue defines none
    of the three anywhere, and the sentence reads as careful writing because
    one thing in it is in fact carefully explained.

    The tell is positional rather than lexical, which is why it is a tell and
    not a word. A term of art immediately BEFORE the comma that opens a
    defining clause is the shape to check, because that is the one position
    where a reader's sense that the sentence explained itself is strongest and
    least earned.

    This entry exists because it defeated a gate built in the same run. The
    first cut of `check_voice.py firstuse` asked whether a gloss marker
    appeared anywhere in the term's first sentence, and on this sentence it
    reported all three terms as glossed. Three real violations cleared by a
    check written to find them, in the file written to find them. The repair
    is to make the test relative to the term rather than to the sentence: read
    the window from the term onward and ask only about the next few characters,
    because a definition arrives adjacent to the word it defines. That is also
    what makes the looser markers safe, so an appositive carrying no "which"
    now counts, which the sentence-wide version had to exclude to avoid
    matching every comma.

    The general rule, and it is the second time this seat has written a version
    of it in six days: a check that asks whether the right KIND of thing is
    present nearby will pass on the artifact that has it nearby and means
    something else. Bind the evidence to the subject, not to the neighbourhood.
    Added 2026-10-23, writer run 42.
    ```
    LANDED docs/voice/check_voice.py: "The term, not the sentence. A definition is adjacent to the word it"
    ```

130. The governing file carrying its own text twice, where no gate reads the
    file itself. Entry 61 is the same disease on a reader-facing string: a
    string that never changes is never graded. This is that sentence turned on
    the instrument instead of the output, and it is worth its own entry because
    the artifact is the one this seat exists to evolve and the damage is
    invisible in every issue it writes.

    The specimen is `prompts/digest.md` on main on 2026-10-23, carrying four
    blocks of its own text twice. Two rule bullets, one slot instruction and
    one line, each written in beside the copy the file already held, with three
    of the four first copies ending in the middle of a sentence. The worst of
    them is quoted here as a pair, because the failure is the brace and not any
    word in it:

    > {Chosen, never listed. Print the papers you would actually tell a builder
    > to spend an hour on, [...] judgment is what the reader pays for.
    > {Chosen, never listed. Print the papers you would actually tell a builder
    > to spend an hour on, [...] judgment is what the reader pays for.

    That second brace never closed. Every slot from the reading list to the
    sign-off, including the closing line law 10 requires to print verbatim and
    last, sat nested inside an instruction block with no end, in a file whose
    own line 502 tells the model that text in curly braces is an instruction to
    it and is replaced by its own words.

    The tell is mechanical and it is three shapes of one thing, which is an
    edit that inserted replacement text without removing what it replaced: a
    run of lines the file carries twice in a row, a curly brace that never
    pairs, and a line ending mid-clause with a new block on the line under it.
    The third is the only one that catches a pair whose copies are not
    identical, which is how the trimmed and untrimmed versions of one worked
    case both stayed in the file.

    Why no prose rule can reach this. Nothing a model is told while writing an
    issue could have caught it, because the damage is in the instruction rather
    than in the output, and the three gates that do read this file read past it:
    the weighing gate measures its cost, the taste gate finds her rulings
    present in it, and the enforcements command verifies forty-six quoted
    anchors inside it. All three were reading a file that disagreed with itself
    about where its own instructions ended. So the enforcement is a command over
    the generator and the second ask is the engineer's, because
    `tools/check_registers.py` already reads sixteen shared files for this class
    and the criterion in its own comment, that more than one seat appends to the
    file, is satisfied by this one.

    The general rule, and it is the third run in a row this seat has written a
    version of it: a check that asks whether the right KIND of thing is present
    nearby will pass on the artifact that has it nearby and means something
    else. Entry 129 wrote it yesterday about a defining clause landing on the
    head noun. This entry writes it about `tools/check_registers.py`, whose
    damage test is seven characters of git conflict marker, built in answer to
    an incident that was clean duplicated text and no marker at all. The gate
    catches the loud form of the failure and never the form that caused it.
    Added 2026-10-23, writer run 43.
    ```
    LANDED docs/voice/check_voice.py: "counted repeated lines would call that damage. What is damage is a run that"
    ```

131. The sentence repaired in the machine that writes the next one, left
    standing in every one already written. The mark of the class is a gate
    whose surface list holds a module and no artifact that module produced.
    Canon law 15 cites one string as its evidence, and it names it as a
    masthead rather than as prose: "read in full and distilled weekly" on
    every issue ever sent, against 166 full reads out of 8,956 papers held.
    `MASTHEAD` in `pipeline/weekly.py` was repaired. The third line of
    `site/content/issues/2026-W39.md` still says it twenty-eight days later,
    and `site/lib/issues-core.js` settles what that costs, in its own words:
    "the record decides which weeks exist, the committed file decides the text
    of any week that has one." 2026-W39 has one and is not hidden, so the law's
    own quoted sentence is the first line a reader of the public archive meets.
    Two blindnesses, and they compound rather than overlap. `SURFACE_GLOBS`
    took `pipeline/weekly.py`, which is the string that will print next, and
    took nothing that has printed. And `READING` exempts "read in full",
    correctly, because that is the one act the word may name and "164 papers
    read in full" is the true sentence the law asks for. Between them, the
    check built for law 15 could not see the words law 15 quotes.
    The exemption is wrong for one form only. Attached to a count, read in full
    is a fact. Attached to a cadence, it is a claim about everything that
    arrived that week, which is the ingest number wearing the read number's
    verb. That distinction is checkable and it is now the branch.
    What makes this entry-worthy rather than a sighting: the hole was written
    down in the check's own docstring on the day it was built, as "a sentence
    that says read in full over a number that came from the ingest field passes
    here and is a worse version of the same lie." It was not a hypothetical
    being guarded against. It was already in print, in the archive, when the
    sentence predicting it was typed. A known gap recorded beside the gate that
    has it is a gap nothing closes, because the record reads as handled.
    The sweep, over the class, which is a reader-facing string fixed in code
    while the artifacts holding the old one stay published: the masthead is this
    entry. `SHORT_EDITION_NOTE` is the only other standing string
    `pipeline/weekly.py` writes into a body, and no committed issue carries it.
    **A count of one, and the generalisable half is the surface list rather
    than the string.** Every gate this seat owns reads `site/app`, `site/lib`,
    `site/emails` and two pipeline modules. The archive was on none of their
    lists, and the archive is the only surface where a repair cannot reach
    backwards.
    **The surface-list sweep, run in the same session, and it found a second
    one immediately.** `SURFACE` in the same file matched
    `site/**.{jsx,js,txt}` and not `.md`, so the gate built to stop a surface
    being redrafted could not see an archive candidate at all. It would have
    printed "no candidate here redrafts a surface already awaiting her word"
    about a surface outside its own regex, which is the one sentence a later
    run would have trusted. Two gates in one file, same error, and the second
    was found by applying L-A21's test to the first rather than by anything
    noticing. `claims` is the third and is left pointed where it is, with the
    reason in `docs/ideas.md` for the seat whose register it is. **So the count
    on the surface-list half is two fixed and one deliberately open**, and the
    lesson is that a gate's scope is reviewed when its law is, because they
    were written in the same breath and inherit the same blind spot.
    One more fell out of widening it, worth a line because it is the opposite
    failure. With `.md` matching, `candidates` accused this run of redrafting
    its own candidate, naming the file in the accusation. A surface held only
    by the file being checked is not a clash, it is the normal shape of a first
    draft, where the register row and the candidate land in one diff. Latent
    since the gate was written, because it only fires when both arrive
    together. **Widening a gate's scope surfaces its false positives as well as
    its blind spots, and the first firing after a widening is evidence about
    the gate rather than about the artifact.**
    Added 2026-10-23, writer run 44. Enforced the same day in
    `docs/voice/check_voice.py`, where `reading` takes `ARCHIVE_GLOBS` on top
    of the surface list and the cadence form is a branch of `READING`. The
    globs go to `reading` alone, because `claims` reads the same list and an
    issue body's sentences are claims about the research rather than about our
    artifact. The line itself is drafted at
    `docs/voice/archive-masthead-2026-10-23.md` for the frontend seat, because
    `site/` is not this seat's surface to set.
    ```
    LANDED docs/voice/check_voice.py: "The archive, which `reading` adds to the list above and no other check does."
    LANDED docs/voice/check_voice.py: "Attached to a count it"
    LANDED docs/voice/check_voice.py: "`md` is in the list because the archive is a surface"
    LANDED docs/voice/check_voice.py: "A surface held only by THIS candidate is not a clash"
    ```

132. The count that reaches a grade as punctuation when the law it detects is
    the one ruling the owner has had to give twice. Not a prose tell. A tell
    about where a law goes to die, which is the gap between a correct rule and
    the words a seat actually reads at the moment of judging.
    The newest issue the press has produced carries the heading "What is
    gaining ground: recursive self-improvement with fewer guardrails".
    "Gaining traction" is the framework's INTERNAL name. Her ruling of
    2026-09-19, given twice, is that the internal names are never printed and
    every heading a reader sees is written fresh from that day's news. It is
    canon law 12 and it is incident 20.
    The generator is not at fault and this was checked before the entry was
    written. Its seventh count already says what to look for in its own words,
    "a slot name, then a colon, then the day's news, which the heading rule
    spends a paragraph forbidding", so a sixth wording of it would be the
    patching this register keeps refusing.
    The instrument was at fault. `axes` returned the row as a bare integer and
    `measure` printed nothing for it at all, so the construction arrived at a
    grade as `headings carrying a colon: 1`. Twenty-one grades in
    `docs/voice/reviews/` scored this artifact and the figure is in several of
    them. A number a seat has to translate back into a law is a number a seat
    reads past, and the proof is that the law in question is the single most
    re-ruled item in this seat's charter and the count still went by as a mark.
    No sweep, because the class is the subject of entry 95's lesson seen from
    the other end. Entry 95 says a rule stated as a count is kept. This says a
    count whose law is not named at the point of printing is read as its
    operand. The two are the same observation about where a rule has to live.
    Added 2026-10-23, writer run 44. Enforced the same day in
    `docs/voice/check_voice.py`, where `measure` prints each colon-bearing
    heading under canon law 12 and incident 20 with the rule's own fix beside
    it. The precedent is one line above it in the same function, where the
    shape count has named canon law 14 since 2026-10-17.
    ```
    LANDED docs/voice/check_voice.py: "colon heading, canon law 12 and incident 20"
    ```
133. The number printed as copy whose provenance is a second reader of a file
    that already has one. A count beside a heading is a sentence, and the
    question a reader asks of it is the claims question: how do you know that.
    The answer here was a regular expression written on the page, in a second
    language, for a file whose contract already had a reader built because
    reading it this way loses entries.
    `site/app/desk/page.jsx` prints `Awaiting your verdict 524`. The figure
    comes from `parseIdeas`, which matches `/- Status:\s*(\w+)/` with no line
    anchor and no `m` flag. `tools/ledger.py --census` reads the same file
    through the contract and counts 525. The one entry the page cannot see is
    "2026-09-24 — A ledger entry can hide from every consumer by writing its
    status as a sentence", whose own status line reads `proposed` and whose
    first bullet quotes `grep "Status: accepted" docs/ideas.md` as the command
    that would have missed it. The unanchored pattern matches inside that
    quoted command. The entry about an entry hiding from every consumer is
    hidden from the owner's console by the mechanism it describes, quoted in
    its own body.
    The tell, stated so a later run can look for it rather than admire this
    one: **a surface that prints a count it derived itself, where the
    repository holds a reader for the same source.** It is not a prose
    judgment and it is not caught by reading the sentence, which is correct
    English about a wrong number. It is caught by running both readers.
    Third in a family, and the distinction is what the repair is. Entry 109 is
    the count whose noun is false of a member. Entry 112 is the count whose
    number is wrong and whose unit is unstated, "so the number cannot be shown
    wrong". This is the count whose unit is exact, whose number is wrong, and
    which CAN be shown wrong in one command, because a second reader of the
    same source already exists and disagrees. So the hedge that answers an
    unverifiable claim makes this one worse: writing "about 524" over a figure
    that is knowably 525 spends a word to keep the error. The repair is the
    anchor, never softer wording.
    Where this one came from matters to the next run. The card that sent this
    seat to the page asked for one string naming a remainder. The remainder is
    a count, so checking the count was inside the job and not beside it. **Any
    line this seat drafts that prints a number is a claim this seat verifies
    against the source, and the register that governs it is
    `docs/agents/quality-claims.md`'s question rather than its table,** because
    a count computed on the page has no row to find and still owes the answer.
    The sweep, over the class: `docs/ideas.md` is the only file in this
    repository with a published reading contract and more than one reader.
    `tools/ledger.py`, `tools/check_registers.py` (which imports the first's
    vocabulary rather than restating it, and is the right shape), and the desk.
    One offender, and the generalisable half is the duty above rather than the
    count.
    Added 2026-10-24, writer run 45. Enforced the same day, and the check reads
    the page's pattern out of the page rather than holding a copy, so a rewrite
    of the parse cannot pass it by accident. Probed against the fixed page:
    486 and 486, `rc=0`.
    ```
    LANDED docs/voice/check_voice.py: "the desk's pattern, read off the page"
    ```

134. The frame word the issue chose for itself, carried bare because the
    writer is the one person who already understands it. Not the jargon that
    looks like jargon, and not the word a frequency list surfaces because
    nobody would have thought to list it. The opposite of both: the word the
    issue leans on hardest, puts in its title, and repeats more than any
    other, which is exactly the word whose meaning the writer stopped seeing
    while choosing it.
    The specimen is one word and the evidence is every print the library has
    ever made. `harness` is BARE in all three.
    ```
    $ for f in site/content/issues/2026-W37.md site/content/issues/2026-W39.md \
               /tmp/wr46/w40-as-sent.md; do
    >   python3 docs/voice/check_voice.py firstuse "$f" | grep "'harness" | head -1
    > done
    2026-W37.md     BARE    club      x2   'harness'
    2026-W39.md     BARE    'harness' in the title, and no clause in the title's own
    w40-as-sent.md  BARE    club      x5   'harness/harnesses'
    ```
    In W39 it arrives in the title and is used twenty-four times. In W40, the
    newest print, it arrives in the lead and is used five times in the opening
    and first section alone. In W37 it arrives inside a paper's name. Three
    prints, two generators, one word, no clause.
    Why this is its own entry rather than a restatement of law 12a. The
    generator's first-use pass already holds the repair in its own words, "the
    word the TITLE uses is the word that gets the clause", and already holds
    the mechanical list-builder added 2026-10-14 for the words that do not look
    like jargon. Neither reaches this class. A frequency list surfaces this
    word first, since it is the most frequent thing in the issue, and the
    writer then reads it off the list and rules it ordinary, because by then it
    is ordinary to them. The tell is the ONLY one in this register where the
    word's high count is the reason it goes unglossed rather than evidence that
    it was.
    The sweep, over the class, and it is the whole corpus rather than a sample.
    Three artifacts can carry this defect and all three do. The generator
    cannot carry it: `prompts/digest.md` has no title and no reader who meets
    its vocabulary cold, so there is no hit to count there and this entry says
    so rather than reporting a sweep it did not run. The site's reader-facing
    surfaces are covered by `check_voice.py reading` and `claims` and are not
    this tell's surface, because a page is not an issue and its vocabulary is
    the owner's approved copy of 2026-09-29.
    Added 2026-10-24, writer run 46. **NOT enforced by a change to
    `prompts/digest.md`, and the absence is the entry.** Five rules in that
    file ask for this repair, four of them were in force when W40 printed, and
    W40 printed thirteen bare terms in its opening and first section against a
    whole-issue cap of five. The charter's step 4 says a structural fix that
    has failed twice through prompt changes goes to the ledger instead, so the
    ending of this entry is a filing rather than an anchor: the 2026-10-24
    entry in `docs/ideas.md` asking for the cap as a blocking rule in
    `tools/check_digest_quality.py`, which is the only reader that sees an
    issue before a reader does. A sixth sentence in the generator would be the
    third mistake the charter names, and it would be unfalsifiable until the
    press sends again, which it has not done in nineteen days.

135. The specimen that fails the gate written to catch it. Entry 93 is about
    where a worked example SITS, and this is the sharper form of it: the
    example sitting at a writing position is itself a violation of the rule it
    illustrates, so the file hands the model the defect and the prohibition in
    the same slot and the defect is the part at the writing position.
    The specimen is the greeting. The opening slot offered a sentence
    introduced in the file's own words as "written out so that following this
    rule is copying rather than composing", and that sentence's subject was
    "you" and its verb was present perfect. Four lines below it stood the hard
    rule: never a past-tense verb with "you" as its subject, no material earns
    an exception. The stands-alone gate at the end of the file runs a tense
    check for exactly that shape and names present perfect in its own list.
    Three greetings have shipped with that grammar, and the third shipped with
    the grammar rule already written.
    What makes it this entry rather than a third repeat of that rule. The slot
    had already done the hard part. It removed BOTH banned specimens from that
    position on the stated ground that "a banned sentence sitting at the
    position where a sentence gets written is the nearest available draft no
    matter what the paragraph around it says", and moved them to the gate. It
    then left the OFFERED sentence standing four lines above the rule, carrying
    the same grammar the two it had just removed carried. The warning was moved
    away from the writing position and the model was left there.
    The file's diagnosis of the third shipped failure is the proof that nothing
    reads this class. It blamed a test at the bottom of the slot for asking
    about the reader's WEEK rather than their JOB, and fixed that noun. The
    specimen at the top of the same slot was not looked at.
    The tell, and it is a command rather than a reading. Every hard gate in
    `prompts/digest.md` reads finished output and none of them has ever read
    that file. A specimen at a writing position IS a draft of that output, so
    the gates apply to it. Run the one the file calls grammar rather than
    judgment over the file's own specimens:
    ```
    python3 docs/voice/check_voice.py specimens
    ```
    The same command carries entry 93's unenforced half, which three runs
    declined to count because a guessed sweep is worse than no sweep: 252
    quoted spans, 191 at a writing position, 73 long enough to lift as a
    sentence, and 27 of those written about the payload's own subject after the
    owner's specimens are exempted by reaching into her register. That number
    is a ceiling and not a verdict, because roughly a third of the list is
    banned text and no command can tell banned from offered.
    Why the off-subject defence is not the repair, which the file had already
    worked out and had not generalised. The reading-list slot says in its own
    words that a specimen "defended as uncopyable" is still a draft, because
    "the usual defence is that no payload would ever hand you that subject, and
    the subject is the one thing a payload controls". That is right, and the
    claim above the template said the opposite about the whole file. The test
    that reconciles them: an off-subject example cannot be lifted for its
    CONTENT and can still be lifted for its SHAPE, since a shape survives
    having its subject swapped. So a position whose reusable part is a shape
    carries no example at all. The print of 2026-10-05 is the evidence, having
    lifted a heading frame with nothing but its tail changed.
    Added 2026-10-24, writer run 47. Enforced by deleting the specimen and
    describing the form, which is the only move with a record of working on
    this class, plus the command above, plus three other specimens found the
    same way: a thin-evidence line naming a payload stream at the reader, and
    three attributive phrases naming people at the position where an
    attribution gets written, under a rule whose own absolute is never-invent.
    ```
    LANDED prompts/digest.md: "The form is described and never drafted"
    LANDED prompts/digest.md: "a position whose reusable part is a shape"
    ```

136. The correction written downstream of the thing that generates the text.
    Not a prose tell. A tell about where a repair is put, and it belongs on
    this list because every entry above it is enforced by a change to a file
    and this is the class where that change is thrown away without anybody
    touching it.
    The specimen is the one the owner struck herself. Canon law 13 quotes
    "You have spent the week watching" and says "so is every tense of it".
    `site/content/issues/2026-W39.md` has opened on that sentence since
    2026-09-29 and it opens on it today. The repair was made on 2026-09-24,
    in `b7d6929`, and it was the right repair: "The agent-building world has
    spent the week arguing about scaffolding", which `prompts/digest.md` now
    prints as its own model answer. Five days later `820df48` re-rendered the
    archived file from the `digests` record and the repair was gone, because
    the repair had only ever been written into the render.
    The tell is a question about any fix to reader-facing words. Was this
    written into the artifact, or into the thing the artifact is produced
    from? A fix to a rendered file survives exactly until the next render, and
    nothing announces that it has been lost, because the commit that loses it
    is about something else and is usually correct on its own terms. Two
    commits touched that file afterwards and neither re-read the opening.
    Why it is not entry 131. That entry is the sentence repaired in the
    machine and left standing in the shipped copy, which is the same two
    places with the arrow the other way round. This is the sentence repaired
    in the shipped copy and never carried back, and the two together say the
    rule plainly: a repair lands in both or it lands in neither.
    Added 2026-10-24, writer run 49. Enforced by a command rather than by a
    sentence, because four patches to the generator could not reach a line the
    generator did not write:
    ```
    python3 docs/voice/check_voice.py standalone
    ```
    That reads the archive instead of the prompt. The pre-send half is the
    engineer's and is filed, because `tools/check_digest_quality.py` is the
    only gate that can stop a send and it has no rule for this law at all.
    ```
    LANDED docs/voice/check_voice.py: "no issue tells a reader what they have been doing"
    ```

137. The trim that keeps a rule's body and takes the line that made it a rule.
    This is a tell in the governing file rather than in an issue, which puts it
    beside entries 130 and 136. All three are about the text that writes the
    text, and this one is the only one where the damage is an absence, so there
    is nothing to quote and nothing to grep for.
    The shape. A rule in `prompts/digest.md` is a bullet: a bolded opening line
    that says what the rule is, then the body that says how to obey it. A pass
    that removes the specimens underneath such a rule can take the opening line
    with them, because the specimens are what the opening line introduces. What
    is left is the body, indented, welded to the end of whatever rule came
    before it, starting mid-sentence in lower case. It reads as a continuation
    of the rule above and it is a different rule.
    Two specimens, both in this seat's own commits, and both were live on
    `main` when this entry was written. `acb4474d` left canon law 6's evidence
    grade as "clause inside the item's own prose, not a footnote and not a
    separate line." hanging off the count-the-links rule. `62b00f2b` left canon
    law 12's final heading gate as "something: every line beginning with `#`"
    hanging off the attribution rule. The second is the harder loss, because
    that gate is the one that stops the framework's internal names reaching a
    reader, which is the ruling the owner has given twice.
    Why the trimming rule produces it rather than carelessness. The canon's
    section on the generator's weight says a run that adds tokens removes at
    least as many, and it says what the trimming may take: the argument for the
    rule, the dates, the account of which print produced which clause. Every
    one of those sits in the body of a bullet. So the pass that obeys the rule
    is working inside bullets all day, and the opening line is one line above
    the thing it is allowed to delete.
    The tell, as a question to ask of a diff rather than of prose. Does every
    line this pass removed belong to a rule that still has its own opening
    line? A trim is the one kind of edit that cannot be checked by reading what
    is left, because what is left reads like prose.
    Added 2026-10-25, writer run 50. Enforced by a command, because this is the
    class that reading cannot catch and because the gate that existed for edit
    damage was reading the opposite direction:
    ```
    python3 docs/voice/check_voice.py generator
    ```
    `truncations` reads the line a cut landed on, so it skips any line ending
    in a full stop and could never reach this pair. `headless` is the same
    defect from the other side, in the same gate, with nine cases pinning it.
    ```
    LANDED docs/voice/check_voice.py: "rules whose own opening line was cut"
    ```
    **Widened 2026-10-26, writer run 51, after the third specimen turned up
    where the gate could not look.** Both narrowings came from the one
    specimen this entry was written from. `headless` required the body line to
    be INDENTED, because a bullet's continuation is, and it skipped every line
    inside a ``` fence, because `fenced()` reasons that a fence quotes output.
    `prompts/digest.md:621` is the same cut in a plain paragraph inside the
    issue template: `d022e79a` on 2026-10-18, a trim under the weight rule,
    removed "**A stranger has to enjoy that sentence.** This is the test it has
    to pass" and the blank line above it, so the opening slot's outsider rule
    began "and it is the reason the line exists" welded to the rule about
    greetings. Neither narrowing could reach it, and the fence one is the
    worse of the two: this file's fence runs 520 to 1353, which is 39% of the
    generator and is the template rather than quoted output.
    The unit is a sentence, which is what the defect is about. The indent and
    the fence were never part of it, and the guard that does the work is the
    full stop on the line before, because a wrapped line never carries one.
    Fourteen cases now, three of them pinning the false positives the widening
    could have bought.

138. The verdict read out of a field that also records what the verdict used
    to be.
    This is a tell in a gate rather than in prose, which puts it beside
    entries 130, 136 and 137. It differs from all three in one way that
    matters: the other three leave a defect a reader could find by reading,
    and this one makes the gate say the opposite of what the register says,
    so reading the register and reading the gate's output both look like
    diligence and only one of them is right.
    The shape. A register records a state per row, and a row that changes
    state says what it changed from, because the transition is the evidence.
    So the field carries two state words and the gate searching it finds two
    verdicts. Which one it returns is decided by the order of the list it
    searches, and the list is written in the order somebody thought of the
    states.
    The specimen, live on `main` from 2026-10-24 and read by a grade on
    2026-10-25. `docs/agents/quality-claims.md` has a row for "the library
    grows every day" whose state cell is `**contradicted**, moved from
    `held` 2026-10-11`. `STATES` in `docs/voice/check_voice.py` opened with
    `held`, so the row resolved to held and the gate printed `ok` beside the
    sentence on `site/app/page.jsx:33`. The register's own measurement in the
    next cell is that the corpus had not grown for 3.35 days.
    Why the permissive verdict is the one that wins, and it is not chance.
    `held` is the state a row leaves, because a claim that was always false
    was never recorded as held, so the word appears in the history of exactly
    the rows whose verdict is now something else. It is also the state that
    means the sentence ships as written. A substring search over a field that
    narrates its own history is therefore biased toward shipping, on the rows
    that have most recently been found false.
    The tell, as a question to put to a gate rather than to prose. Does this
    gate read a field that a person also writes prose into, and if that prose
    mentions another possible value, which one does the gate return? Where
    the answer is "the first one in the list", the gate has no verdict, it has
    an ordering.
    Added 2026-10-26, writer run 51. Enforced by a command, because the
    defect is in the resolver and never in the text either side of it:
    ```
    python3 docs/voice/check_voice.py claims
    ```
    The scope is now the state cell's first bolded span, which is where this
    register writes its verdict, and the rest of the cell is the row's
    history. Where two verdicts survive inside that span the strictest is
    read and the row prints AMBIGUOUS, because a gate that guesses in the
    shipping direction is worse than no gate. Thirteen cases pin it, run
    before the register is read. Swept: one other first-match-wins resolution
    of a verdict exists in this seat's files and there is none, so the count
    is one and the entry closes on its own specimen.
    ```
    LANDED docs/voice/check_voice.py: "the strictest reading is taken and the"
    ```

139. The figure with two inputs, quoted with neither.
    A gate that reads a register against a set of surfaces produces a count
    that moves when either side moves. The count is the headline, the two
    inputs are printed above it, and a review quotes the headline, so the
    delta arrives in the grade with nothing to attribute it to.
    The specimen is this seat's own grade of 2026-10-25, which recorded that
    `check_voice.py claims` reported 23 unhedged claims "against 17 on
    2026-10-23, which is six more than a run that drafted nothing for these
    surfaces can account for", and then said in its own words that the delta
    was not diagnosed. It was diagnosable and it cost one command: the
    current gate run against the tree of 2026-10-23 returns 17, so no part of
    the rise was the gate and no part of it was the copy. The register went
    from 11 rows to 13 when the ExO seat's split landed on 2026-10-24, and
    two more rows of claims to check found four more sentences to fail.
    Why it reads as news about the copy. The count's name is about the
    surfaces, "unhedged or unnamed, live right now", so a run that has
    drafted no copy reads a rise as copy getting worse somewhere it was not
    looking. The other input is a file this seat may not edit, kept by
    another seat, on its own weekly cycle, and a row added there raises this
    seat's number without a word of copy changing.
    The tell, as a question to put to a figure before quoting it. How many
    things have to hold still for this number to mean what its name says, and
    is the number printed next to them? That is L-A47 in the company
    standard, an instrument's scope is part of its answer, applied to the one
    figure this seat quotes most.
    Added 2026-10-26, writer run 51. Enforced by a sentence rather than a
    gate, because the inputs were already on screen and the failure was
    quoting the headline away from them:
    ```
    LANDED docs/voice/check_voice.py: "(over {len(rows)} register rows and {len(scanned)} surfaces)"
    ```
    The count now carries its own scope on its own line, so a grade that
    quotes the figure quotes the two numbers that produce it.

140. The payload's field name used as the label over the thing it names.
    Entry 14 and the vocabulary rule in the generator both ban the payload's
    field names from reaching a reader, and the generator lists the shape by
    name: "carries a procedure", "flagged for deep reading", "scored highly in
    triage". Those are all the field name used as a FACT about the paper. This
    entry is the other grammar, and it is the one that got through: the field
    name used as the LABEL announcing the thing the rule is about to render.
    The specimen is 2026-W42, three times in one issue, every one of them the
    same construction. "The procedure is extractable:", then the steps as a
    comma-run. "The procedure is clean:", then the steps as a comma-run. "The
    procedure runs:", then the steps as a comma-run.
    Why it defeats the rule that was pointed at it. The vocabulary rule tests
    whether a clause makes a claim the subscriber cannot check, and asks
    "flagged by whom?" There is no such question to ask here. "The procedure
    is clean" claims nothing about the paper and nothing about alexandria; it
    is a stage direction, read as a transition, and the ban reads it as
    neither. The word is also an ordinary English noun, so no count of it
    separates the label from a legitimate use.
    **And the label costs more than a word, which is why this is not a tone
    entry.** The rule it sits under says a procedure is always list-shaped and
    must render as a numbered list. All three of these rendered as prose. A
    procedure is the only reliable supply of a list in this generator, and the
    issue that converted three of them printed `shapes 1`, which the shape rule
    calls a failing issue in its own words. The one tell carried the one law
    the issue most needed.
    The tell, as a question to put to a rule rather than to prose. Does this
    rule name a payload field and then ask for a render, and if so, does
    anything stop the field's name becoming the render's caption? A rule that
    says "render the `x`" has handed the model a word and a colon.
    Added 2026-10-26, writer run 51. Enforced by a sentence in the rule that
    produces the defect, which is where the canon's own generalisation step
    says the gate belongs:
    ```
    LANDED prompts/digest.md: "The list is the shape and not a suggestion, and this field's name is never"
    ```
    Swept: the generator names a payload field and asks for a render in one
    other place, the `citation_movers` translation at the vocabulary rule
    itself, and that rule already supplies the reader-facing words to use
    instead ("three separate papers built on it this week"), so it carries its
    own answer and needs nothing. The count is two and one was already closed.

141. The newest artifact named from the files on disk, when the product serves
    more than the repository holds.
    This is a tell in a grading procedure rather than in prose, and it is the
    fourth instance of one class. The canon already records three: which COPY
    of an issue to grade, which GENERATOR wrote it, and which EDITION the
    newest artifact is. Each one was a check that read the thing in front of it
    without asking whether that thing was the thing it was supposed to read.
    This is which SURFACE.
    The specimen. Runs 49 and 50 both opened on the sentence that
    `site/content/issues/2026-W39.md` was "the newest issue this runtime can
    reach", and run 50 spent its reasoning on why re-deriving a 27-day-old
    grade would be waste. It was waste. The archive directory holds two files
    and the live site was serving three issues, the newest of them `2026-W42`,
    seven days old and never graded by anybody.
    ```
    curl -s https://libraryofalexandria.dev/library | grep -oE '2026-W[0-9]+'
    2026-W39   2026-W40   2026-W42
    ```
    Why the wrong answer was the reachable one. The charter says to read "the
    newest published issue in the repo **or site**", and the procedure's own
    first question is which artifact by path. A path is a file, so the whole
    check reads as a question about the repository, and `NEON_RO_URL` being
    unset was taken to mean that everything outside the repository was shut.
    The site needs no credential. Neither does
    `tools/delivery_health.py --surface press`, which has answered this exact
    question since 2026-10-12 and names the newest week in one line.
    The tell, as a question to ask before a grade begins rather than of prose.
    What is the newest artifact a READER can reach, and is that the one in
    front of me? The repository is where this seat works and it is not where
    the product lives, so the two drift apart by exactly the number of issues
    nobody has committed.
    Added 2026-10-26, writer run 51. Enforced by a command, because this is the
    class where reading the file in front of you is the defect:
    ```
    python3 tools/delivery_health.py --surface press --no-notify
    ```
    It reports the newest week the press has written and whether the next is
    due, from a public endpoint with no credential, and it is the first step of
    a grade from here on. Swept: the canon's grading procedure names "the
    newest issue" in four places and every one of them now has this command
    above it in the order of work, which is the ordering the charter's step 1
    already implies and no run executed.
142. The caption set written in one grammar, where every caption is right and
    only the set is wrong.
    Entry 3 is the parent and it says "vary or die" in nine words with no
    count under it, so for 38 days it was a reading. This is the half of it
    that no gate pointed at a single line can see, because the unit of the
    tell is the SET.
    The specimen, and it is the surface a stranger is sent to. The skill
    library's shelf page carries a caption under every shelf heading. Four of
    the six on named shelves are the identical frame, which is a short
    verbless opener, a full stop, and a list of three:

    > The scaffold around a model. Tools, prompts, loop structure, and the
    > feedback the loop runs on.
    > Several agents dividing work. How they are organised, how they hand off,
    > and how they fail.
    > Post-training that updates the weights. Distillation, reward design, and
    > self-improvement.
    > Getting an answer out fast and cheap. Decoding, caching, and test-time
    > compute.

    Every one of them is accurate about its own shelf and none of them would
    be marked in isolation, which is what makes this prose rather than error.
    The set reads as furniture generated to fill seven slots, and a reader who
    has scrolled past three of them has learned to skip the fourth, which is
    the opposite of what a caption is for.
    How it survived. Three visual sweeps of this page read it, two copy rounds
    read the page it sits on, and the captions were never the artifact in
    front of any of them. They were committed on 2026-09-18 by the
    fifty-skill rebuild, eleven days before her ruling of 2026-09-29 that the
    subtitles were too choppy and that fragments were out, and no owner has
    ever ruled on one of them. A string set in code and never regenerated is
    never graded, which is entry 61, and this is entry 61 pointed at a set
    rather than at a line.
    The sharper finding in the same specimen is not countable and is recorded
    rather than gated. Not one of the seven captions contains a finite main
    verb, so not one of them is a sentence, and her ruling forbids exactly
    that. Deciding whether a clause carries a finite verb is not string work,
    and a fragile detector would report that verdict in the same format as the
    two honest counts below, so it is left to the reading in
    `docs/voice/shelf-names-2026-10-26.md` where a person can check it.
    Added 2026-10-26, writer run 53. Enforced the same day by a count, because
    entry 113 settled that a tell in this file holds only when it becomes one:
    "Every gate in that list that holds was turned into a count after a print
    walked past it." The gate reads every caption a sibling set declares and
    fails on two string tests, more than one caption on the same frame and two
    captions opening on the same two words, which is entry 113's own technique
    over a set instead of over an issue's evidence grades.
    ```
    python3 docs/voice/check_voice.py captions
    ```
    It reads 7 of the 7 captions the surface declares, fails today naming the
    four, and goes green on the nine drafted to replace them, which was
    verified before this entry was written rather than asserted by it. Twelve
    cases run before the file is opened, each one a caption string taken
    verbatim from the surface or from the drafted repair, because a pattern
    that miscounts prints its wrong count in the right format.
    The two tests are quoted so this ending is checkable rather than read,
    which is the convention of 2026-10-04 and the reason the prose-only count
    at the top of this file is meant to fall:
    ```
    LANDED docs/voice/check_voice.py: "captions share one frame"
    LANDED docs/voice/check_voice.py: "captions open on"
    ```
    Swept: `CAPTION_SETS` names every set in the repository that renders a
    caption under each member of a list, and today the shelves are the only
    one. A second set is one line, and the sweep is the reason the gate takes
    a set table rather than a path.
143. The rule that bans a phrase and then writes the phrase, in the position
    where the phrase gets drafted.
    This is the eighth member of the family entries 53, 56, 65, 76, 88, 93 and
    100 belong to, where the model copies a specimen the register handed it.
    Every earlier member was a specimen the file OFFERED, as a worked example
    or a mapping. This one is a specimen the file BANS, four hundred and eleven
    words from the ban, and that is what makes it the hardest of the eight to
    see: a reader who finds the phrase thinks of the ban rather than of the
    draft, because the ban is the thing the phrase is famous for.
    The specimen, and it printed. `2026-W40` went to readers on 2026-10-05
    under three headings:

    > ## What is gaining ground: recursive self-improvement with fewer guardrails
    > ## What is genuinely new: where memory lives and who can pull the plug
    > ## What fell behind: the assumptions that let agents run unchecked

    Canon law 12, incident 20, the one ruling the owner has given twice and the
    second time in the word "AGAIN". The generator forbids this twice over
    before the model reaches the heading slots. It bans "what is new" and "what
    fell behind" by name as "that failure in its commonest dress", and the next
    paragraph bans the colon that launders it, in the exact shape "What fell
    behind: the thing yesterday's consensus got wrong".
    And then the file wrote them. Line 44 listed the day's four slots as "what
    gained ground, what is genuinely new, what fell behind, what to read
    yourself", which is two of the three printed headings word for word and the
    third one inflection away. Line 1525 wrote "what is new tests it, what fell
    behind is the position it replaces", two of the five banned phrasings
    verbatim, inside the rule that teaches the weekly to argue. Line 373 named
    the slot the same way inside the rule that teaches heading craft.
    Why the earlier repair could not reach it, and this is the half worth
    keeping. The diagnosis was already in the file, in its own bold: "The ban
    is on the slot's IDEA and not on four strings, and the words that beat it
    came out of this file." A run wrote that sentence, enumerated five
    phrasings under it, and swept nothing. Entry 90 requires the sweep and
    entry 100's ending performs one. Neither is written as a duty the BAN owes
    itself, so a run that adds a phrase to a ban list reads it as a rule it is
    installing rather than as a string it has just introduced into the file.
    The tell, as a question to ask of an edit rather than of prose. Did this
    edit add a quoted specimen to the file, and if so, does the file use that
    specimen anywhere outside the quotation? Ask it of a ban exactly as entry
    100 asks it of a worked example, because the model reads a file and not a
    register, and a phrase in a prompt is a draft at every position except the
    one where the sentence around it says otherwise.
    Added 2026-10-26, writer run 54. Enforced the same day in
    `prompts/digest.md`, where all three specimens now use this file's internal
    names, which the tripwire at the end of the file already reads, so a leak
    from any of the three is a leak the existing gate catches rather than a new
    rule nobody can see fail. Weight: 33,953 tokens before and 33,947 after,
    six returned, because the internal names are shorter than the dress.
    Gated the same day, and it reads a SERIES rather than a phrase:
    ```
    python3 docs/voice/check_voice.py slotwords
    ```
    The phrase alone is ordinary English in this file four times over, at "Then
    what changed, with its number" and at "the reader who wants to check what
    changed", and a gate crying on those is a gate somebody deletes. Two or
    more slot-shaped phrases in one comma series is a list of the issue's slots
    and has no second reading. The five phrasings come out of the ban's own
    quoted list rather than from a copy of it, because a hand-kept copy is the
    next thing to drift and that is this entry one level up.
    ```
    LANDED docs/voice/check_voice.py: "slot series outside the ban"
    ```
    Verified both ways before this entry was written rather than asserted by
    it. Against `origin/main` the gate fails and names both standing
    specimens. Against the branch carrying the patch it is green. Five cases
    run before the file is opened, and three of them exist to stop the
    detector: the sign-off's own "what you would watch next, what is still
    unsettled, what this leaves a builder holding" is a series of the same
    grammar naming nothing the ban names, and a pattern tuned only against the
    two specimens fires on it.
    Swept, per entry 90, and the sweep is the entry. Three specimens in one
    file, and the one the ban paragraph itself quotes at lines 350 and 353
    stays, because a ban that cannot quote what it bans is not a ban. Nothing
    else in `prompts/digest.md` writes a slot in its reader-facing dress.
144. The figure quoted off a gate, with no line saying what the gate was
    pointed at.
    Numbered 144 because #560 holds 142 and 143 and merges first. The ban
    list allocates sequentially, which is the defect the incident register
    already fixed by switching to `INC-YYYY-MM-DD-slug` after four
    collisions (incident 29). A seat on a branch cannot see the highest
    number that exists. Recorded here rather than repaired, because
    renumbering 144 entries is not this run's errand.
    The specimen, and it is this seat twice in one day. Writer run 54 wrote
    "Zero em dashes, zero banned words" under the heading "This run's own
    prose, measured". Writer run 55 wrote that the gate "reads added lines
    out of a diff and therefore reports zero on a file already committed",
    and counted with `grep` instead. Run 54's sentence is true of the one
    file it means and false of the branch it shipped, where the gate exits 1
    with nine findings. Run 55's sentence is false of the gate outright. Both
    runs had pointed `selfcheck` at something it could not resolve, and a
    base ref git cannot resolve fails with an empty stdout, which is the same
    byte string as a clean diff.
    ```
    python3 docs/voice/check_voice.py selfcheck --help
      added lines read from   --help
        no semicolon and no em dash in any added line
      0 line(s) carry a mark this file cannot excuse.
    ```
    Why the tell is the sentence and not the gate. The gate is fixed in the
    same pull request as this entry, and the next instrument this seat points
    at itself will have its own blind spot. What survives the fix is the
    sentence shape. "Zero em dashes" is a result. "Zero em dashes across the
    branch, read from `origin/main`" is a result with its scope attached, and
    only the second one can be wrong out loud. This is the same class as
    entry 141, which asked which SURFACE a grade read, and as the ExO seat's
    rule of this morning, that a live test must measure the surface that
    acts. Entry 141 asked the question of the artifact. This one asks it of
    the instrument.
    The tell, as a question to ask of the seat's own review rather than of
    prose. Does every number in this section say what it was taken over, and
    would the reader be able to re-take it from what is written? A measurement
    without its scope reads as more certain than the reading it came from, and
    a review is the one artifact where that costs the next run a whole run.
    Added 2026-10-26, writer run 56. Enforced in the gate rather than by a
    reading, because the failure here was silence:
    ```
    python3 docs/voice/check_voice.py selfcheck <a-ref-that-does-not-exist>
      FAIL    <a-ref-that-does-not-exist>: ... unknown revision
      Nothing was measured, so nothing is clean.
    ```
    It exits 1. `added_lines` raises `BadRef` instead of yielding nothing, so
    every check that takes a ref fails loudly rather than reporting the
    better of two readings it cannot tell apart. Swept: `selfcheck` prints its
    base ref on the first line of its output already, which is what made this
    findable, and the eight cases in `SELFCHECK_CASES` run before any diff is
    read so the reading cannot drift without saying so. The gate and the step
    inside it, quoted so a later run can check it rather than read for it:
    ```
    LANDED docs/voice/check_voice.py: "Nothing was measured, so nothing is clean. This used to print a"
    LANDED docs/voice/check_voice.py: "The wrapped-span reading changed and SELFCHECK_CASES says how."
    LANDED docs/voice/check_voice.py: "a file this run created is invisible here until `git add`"
    ```
    The first is the step that used to be silent. The second is the step that
    refuses to read a diff at all when the reading itself has drifted. The
    third is the widest of the three. `git diff` reads tracked paths only, so
    every review, candidate and incident filing this seat writes was invisible
    to this gate until it was staged, which is the whole of the seat's output.
    The repaired gate's first run found a semicolon join in the incident entry
    reporting the gate, and that is the cheapest possible proof that the scope
    was the defect.
145. The overturn whose two ends are one paper.
    Numbered 145 because 144 is on the branch this one builds on. The
    allocator is still sequential and still the defect entry 144 recorded.
    The tell is not a word and not a phrase, which is why no entry on this
    register caught it through three editions. It is a sentence that is true
    about a paper and false about where the paper's finding came from. "This
    directly contradicts the earlier claim that task complexity above a
    model-size threshold forces near-linear information leakage" is live on
    the site today, and the near-linear leakage result is the theorem of the
    paper that sentence cites. The issue's own prose carries the refutation
    three sentences earlier, as something this paper showed.
    Three dresses, and the generator now carries all three in its SOURCE
    test. A phrase pointing back at the work being overturned, which has told
    you the two ends are one end before the verb arrives. A named work as the
    subject of a verb of prior belief, where that name is also a paper the
    section links. And the overturned belief already standing in the draft as
    the citing paper's own result, with two paragraphs of distance doing the
    work a second source should have done.
    Why it belongs here rather than only in the generator. Every other entry
    on this register is a shape in the prose, so a reader of the entry can
    find the next instance by reading. This one is a relation between the
    prose and a paper, and the only reason it is catchable at all is that two
    of the three dresses leave their evidence inside the sentence. The third
    does not, and no entry on this register will ever catch it. That half is
    the claims pass's seventh question in docs/voice/canon.md and it is a
    reading, by design, because the input is an abstract.
    The figure belonging to a paper the section never names is the same class
    and the worst member of it. 2026-W42 printed "omitting tenant-salt
    provenance enables 93% prompt identification from timing side-channels"
    and attributed it to "the same paper", which is a theory paper on
    chain-of-thought encryption that contains neither the mechanism nor the
    number. A mislabelled edge misleads the reader who follows the link. A
    figure under the wrong paper gives them nowhere to follow.
    Added 2026-10-26, writer run 57, from the research seat's audit of the
    live 2026-W42 against the two abstracts that section cites
    (`docs/research/notes/2026-10-26-w42-left-behind-audit.md`, three wrong
    out of three). Enforced in a gate rather than by a reading, because the
    failure here was a complete grade: this seat graded that same section the
    same morning against all sixteen laws and the six passes and reported its
    prose, which is the procedure working as written.
    ```
    python3 -I docs/voice/check_voice.py provenance --live
      the detector's own cases   5 pass
      2026-W39  0 finding(s)
      2026-W40  0 finding(s)
      2026-W42  2 finding(s)
        FAIL  line 47: points back at the work it overturns
        FAIL  line 49: the work that held it is a work this section links (vosti)
    ```
    Three claims a later run can check rather than read for.
    ```
    LANDED prompts/digest.md: "The third is SOURCE, and it is the one both others pass"
    LANDED prompts/digest.md: "A phrase reporting the absence is a phrase, so it fails the third form"
    LANDED docs/voice/check_voice.py: "One paper cannot overturn itself."
    ```
    The first is the test the section never had: two tests that compare the
    claims to each other both pass when one paper stands against itself.
    The second is the attribution third form's one dress that looks like
    compliance, which is the fourth defect in the same section and printed as
    "a team at an unnamed institution". The third is the gate, and it claims
    two of the three dresses and says in its own output that a clean exit is
    not a verdict on the section.
    Swept. The generator writes the backreference phrase nowhere outside the
    bullet that bans it, and `provenance` is clean on both committed editions
    and on 2026-W40 served, so the two live hits are the section the audit
    named and not a detector that fires on ordinary prose.

146. The instrument whose blind spot grows with the output it measures.
    Not a phrase, and the entry is here rather than in the ledger because
    the thing it bans is a reading rather than a repair: a gate's refusal
    read as a fact about the world instead of a fact about the gate.
    The specimen is the forwards half of the canon's grading procedure.
    `tools/delivery_health.py --surface deploy` recovers the commit the
    press was built from by replaying the image's content digest over the
    last `DEPLOY_HISTORY_LIMIT` commits to touch the app's files. That limit
    is 40. The `weekly` image's file list contains `prompts/digest.md`,
    which is the one file this seat edits on every run, so every writer run
    spends part of that window and the deployed commit walks toward the end
    of it. On 2026-10-27 it reached position 43 and the surface stopped
    answering.
    ```
    the deploy cannot be compared from here for: weekly
      (the drift cannot be dated from this checkout)
    the running digest 2e313065f5c7 matches none of the last 40 commits to
      touch this app's files, so the deploy was built from code that is not
      in this history
    ```
    The commit was `f16e2775`, nine days old, an ancestor of `origin/main`,
    in the checkout the surface had just read. Widening the window to 60
    returned it with 42 undeployed commits behind it. Three commits of margin
    were the whole difference between a number and a refusal, and the refusal
    describes a state nobody can act on, because code that is not in the
    history would mean somebody deployed an unpushed tree.
    What makes it an entry and not a bug report is the direction of the
    failure. The instrument goes blind in proportion to how much the seat
    reading it works, so it holds for a seat that patches nothing and fails
    for a seat that patches daily. Run 51 read 10.4 days and 31 commits off
    this surface on 2026-10-26. Run 60 read a refusal on 2026-10-27 with the
    deploy row unchanged since 2026-10-19 and the clone fully unshallowed.
    Nothing had moved except this seat's own commit count.
    ```
    Enforced docs/voice/check_voice.py: "press"
    LANDED docs/voice/check_voice.py: "REFUSED is the answer to act on rather than to read"
    LANDED docs/voice/canon.md: "Say the generator's age at the top of the grade"
    ```
    `check_voice.py press` asks the same question with the window widened, by
    calling `undeployed_commits` rather than replaying the digest a second
    time, and it treats an unreachable receipt as a failure rather than a
    pass. The limit itself is the engineer's and is in the ledger as of
    2026-10-27 with the second half of the ask, which is that a refusal says
    how far it looked.
    Swept. The three other commands in this file that read a bounded window
    are `enforcements`, which takes a ref and reads one tree, `selfcheck`,
    which reads a diff the caller names, and `sweep`, which reads the whole
    register. None of them bounds a search by a count, so there is no second
    instance of this shape here to repair.
