# The prose ban list — tells of AI-generated writing

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
2. Three-adjective lists. One precise adjective, or a number.
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
    LANDED prompts/digest.md: "Two specimen turns stood here and both are deleted rather than re-warned."
    ```
    What is NOT enforced, said plainly: the file still teaches by worked example
    at other writing positions and this run did not inventory them, because
    counting them is a different job from grading an issue and a guessed count
    recorded as a sweep is worse than no sweep. Filed in docs/ideas.md.

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
