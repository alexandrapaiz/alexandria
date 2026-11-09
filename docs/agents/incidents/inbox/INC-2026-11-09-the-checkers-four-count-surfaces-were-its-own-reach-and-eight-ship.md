## INC-2026-11-09-the-checkers-four-count-surfaces-were-its-own-reach-and-eight-ship - the plugin drift checker reported four problems over four surfaces it had been told about, and there are eight (2026-11-09, engineer seat)

**What happened.** The tenth skill landed on `main` tonight and
`tools/check_plugin_manifest.py` reported four reader-facing surfaces saying
nine. This seat's earlier run fixed all four and the checker went green. The
four was not the library's drift. It was the checker's reach: two paths were
written into module constants, `.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json`, and two prose files were written into
`GUARDED_PROSE`, so a count anywhere else was not clean, it was unread. The
skill seat found two more within the hour, `skills/README.md` and
`.cursor-plugin/plugin.json`, and said the defect in one sentence: what decided
the four was the instrument's reach rather than the library's drift. Running a
derived census over the install path found two more again, both on
`site/app/llms.txt/route.js`, which is served to the public at
`/llms.txt` and carried the same install sentence `README.md` had already had
corrected: "That installs nine skills." Eight surfaces, four of them outside the
only gate that exists for them. Two further counts have the noun elided, "the
same nine" and "every one of the nine shares", and no pattern short of a parser
reaches those.

**Why it is in this register.** This is the coverage-mistaken-for-population
class, and it is at least the third live instance.
`INC-2026-11-02-the-confident-zero-class-was-measured-in-three-more-tools-and-two-sweeps-had-covered-four-of-fifty-six`
is the same shape in `tools/`: two sweeps had covered four of fifty-six and the
number each printed was its own denominator.
`INC-2026-11-09-the-count-that-no-artifact-can-reach-is-now-in-the-device-the-law-says-comes-first`,
filed by this seat earlier today, is the condition no artifact can reach, which
is this class at zero. What makes today's instance worth its own entry rather
than a line on one of those is that the gate here was green, recent, tested
against failing artifacts, and written by the seat that owns the surface. A
hand list does not look like a gap. It looks like a clean pass, and this one
printed "The install line and the manifests agree."

**What it cost.** The cursor manifest shipped 2026-10-26 and was correct that
day, so its own drift was hours old. `/llms.txt` has advertised nine skills
since the tenth landed, and the install sentence a reader pastes from the public
site disagreed with the one in `README.md` for the whole window. The seat cost
is the one that repeats: two seats and three runs spent a pass each on a count
that one derived census answers, and the second seat had to find the first
seat's blind spot by hand.

**The fix, or why there is not one yet.** Shipped in the same pull request as
this entry. Manifests are discovered by the `<ecosystem>-plugin/` directory
convention rather than listed, and every `description` in one is read at
whatever depth it sits. The prose half gets a census: every file under declared
roots that names a count is enumerated, each carries a disposition of `live`,
`block` or `internal`, and a surface nobody has classified fails. That is
INC-2026-11-02's own remedy, which is `tools/target_census.py`'s shape:
enumerate the population, declare a judgment per member, fail on the unjudged
member, and print the denominator rather than asserting it. What the fix does
not reach is written into the file beside the pattern, because the lesson of
this entry is that an undeclared reach reads as a clean pass.
