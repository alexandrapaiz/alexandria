# The prose ban list — tells of AI-generated writing

Companion to docs/design/ban-list.md, for words. The writer seat
checks every issue against this list, APPENDS new tells as the
generated-prose aesthetic drifts, and never deletes an entry without
the owner's word.

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
14. Internal vocabulary printed at the reader. "(3 supports)" is a
    count of edges in alexandria's claim graph, not a fact about the
    research, and no subscriber can decode it. Say what the number
    means in plain words. The same goes for triage scores, tiers,
    claim ids, and the ISO week code.
15. The complete dump in place of a judged selection. A section that
    prints every row the query returned has outsourced the editing to
    the database. Nine "read these yourself" entries is a list; five
    chosen ones is a recommendation, and the reader pays for the
    choosing.
16. One paper wearing several hats. Splitting a single paper across
    two or three items, or calling two papers "several teams", makes a
    thin week look broad. State plainly when findings share a source.
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
26. The label that moved down a level. "**Contradicted**" and
    "**Replaced**" in bold at the head of a group inside a section do
    the same job as "Gaining traction" at the head of a section: they
    sort rows, they fit every issue, and they hand the reader the
    blueprint. A category word is a category word whether it carries a
    `##` or a pair of asterisks. Added 2026-09-19 from 2026-W37, where
    the generator's own example lead-in printed verbatim.
27. The advice sentence in the same clothes every time. "Builders
    should replace binary success/failure signals", "Practitioners
    should adopt these token-level continuity tricks", "Builders of
    long-horizon agents should embed such feedback": three items, three
    identical constructions, and by the third the reader has stopped
    reading the sentence and started recognizing it. Naming the
    consequence is house law, so vary what it attaches to, not only its
    verb. Added 2026-09-19 from 2026-W37, three items out of three.
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
