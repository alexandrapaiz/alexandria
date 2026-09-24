# The prose ban list — tells of AI-generated writing

Companion to docs/design/ban-list.md, for words. The writer seat
checks every issue against this list, APPENDS new tells as the
generated-prose aesthetic drifts, and never deletes an entry without
the owner's word. Since her ruling of 2026-09-19 it governs site copy
as well as issues, so a page of the site is read against these tells
exactly as an issue is.

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
    compliance. Added 2026-09-24 from the fifth grade of W39.
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
    from the fifth grade of W39.
