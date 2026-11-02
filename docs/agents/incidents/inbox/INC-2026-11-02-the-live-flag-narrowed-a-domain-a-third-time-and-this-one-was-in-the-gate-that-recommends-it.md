## INC-2026-11-02-the-live-flag-narrowed-a-domain-a-third-time-and-this-one-was-in-the-gate-that-recommends-it - the live flag narrowed a domain a third time, and this one was in the gate that recommends it (2026-11-02, writer seat)

**What happened.** `docs/voice/check_voice.py reading` grades canon law 15 and
its default domain is 63 surfaces, 61 of them site code and 2 the committed
issue archive, because the law's own words bind "the masthead, the email, the
site and any line of copy drafted under the canon". The `--live` flag, added
2026-10-23, replaces the archive glob with the editions the product serves.
`reading` is the only gate in `TAKES_PATHS` whose default domain is code, so
for this one gate the replacement dropped the half the law names first.
Measured both ways before the repair:

```
$ python3 docs/voice/check_voice.py reading
surfaces read   63
lines giving the arriving count a verb of reading   4
[exit 1]

$ python3 docs/voice/check_voice.py reading --live
surfaces read   3
lines giving the arriving count a verb of reading   0
  every surface uses the verb the law allows
[exit 0]
```

The four it stopped seeing are `site/app/page.jsx:44`,
`site/app/terms/page.jsx:19` and two in `site/app/llms.txt/route.js`, all live
on pages anybody can open. `taste` inherits this gate's verdict for the owner's
2026-09-29 verdict 6, so the green reported one of her rulings as held while
the line breaking it was on the home page.

**Why it is in this register.** Third instance of a class this seat filed
yesterday.
`INC-2026-11-02-the-probe-was-widened-and-its-domain-narrowed-the-same-way-twice`
records instances one and two: a sweep of `tools/` whose domain was the shapes
this seat's own file happens to use, published clean twice over 1.7% of the
surface. That entry's own words are "twice in two nights this seat measured a
domain by the shapes its own file happens to use, published a clean result
over it, and had the narrowness pointed out by somebody else the first time".

Two things make this instance different and both are worse. The narrowing was
not chosen by a belief about the domain, it was chosen by a FLAG, so no
reading of the code or the output could have revealed it. And **the file
recommends the flag.** `editions` prints "`--live` on the passes that take
paths is the way to answer it inside one run", so a run that followed this
file's own printed advice got the false green. The first two instances needed
somebody to measure the domain. This one needed somebody to doubt an
instruction.

The underlying class is older and this is not its third instance. "An
instrument reporting a pass about a target it never resolved" was on its
eighth instance last night, per
`INC-2026-11-02-the-subcommand-dispatcher-answered-ok-to-a-name-it-did-not-have`.
What repeats specifically here is the measurement level rather than the
instrument: a clean result published over a domain narrower than the law's.

**A second defect in the same gate, found by asking what would have happened
if the edition HAD violated.** `reading` built its hit rows with a bare
`path.relative_to(ROOT)`, and `--live` hands it absolute paths in a tempdir
outside the repository. Reproduced on a planted edition before the fix:

```
RAISED ValueError: '/tmp/probe-f9ol64hf/2026-W99.md' is not in the subpath of
       '/tmp/epito-alexandria-writer-FtRz87'
```

So the gate had two states over the live domain and neither was a report: a
green that excluded the evidence, or an uncaught traceback. Seven of the eight
path-taking gates that call `relative_to` wrap it in `try`/`except ValueError`,
and `measure`'s copy carries the comment "used to raise rather than measure it
(2026-10-06)". `reading` joined the path-taking gates seventeen days after
that repair and never received it. That is its own small class worth naming: a
repair applied in seven places, missed by the one caller added next, and
invisible because the eighth caller's domain never reached the branch.

**What it cost.** Nine days, 2026-10-23 to 2026-11-02, in which
`reading --live` was available and would answer green. No grade in
`docs/voice/reviews/` used it, checked by grep, so no published verdict rests
on the false pass and the cost is the exposure rather than a wrong artifact.
The four violations it hid are real, are still live, and are in `site/`, which
is the frontend seat's surface. The repair for the home page's line was
drafted by this seat on 2026-09-26 in
`docs/voice/home-metric-line-2026-09-26.md` and the `reading` docstring already
records it as unset at twenty-two days.

**The fix, or why there is not one yet.** Both halves shipped in this pull
request, in `docs/voice/check_voice.py`, which is this seat's surface.
`reading_domain` splits the two halves so the code half is unconditional and
only the archive half is what a caller may point elsewhere. `shown_path` gives
`reading` the guard the other seven have. Four asserted cases,
`READING_DOMAIN_CASES`, run inside `dispatch`, and the guard is the domain
identity rather than any single case: restoring the replacing version fails
all three path cases at once. `reading --live` now reads 64 surfaces, 61 code
and 3 served editions, and exits 1 with the four real violations.

The generalisable half is ban list 155, "the flag whose name promises a
widening and whose operation is a swap", whose test is one question asked of
the option rather than the output: does this flag ADD members to the domain or
EXCHANGE them? A gate whose domain a caller can replace silently is a gate
that does not tell the caller what it read. `captions` in the same file already
does this correctly, refusing rather than printing a green when handed paths
outside its table, so the repair is the house style rather than an invention.

What is NOT fixed, and it is the reason this entry exists rather than only a
commit: the recommendation in `editions` that produced the false green is still
printed, and it is correct for every other gate. One flag with two meanings
across seventeen gates is a design this seat chose and should not be trusted to
audit alone, so it is named here for the ExO seat's weekly read.
