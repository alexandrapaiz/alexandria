## INC-2026-11-02-this-seat-put-its-own-red-in-seen-and-not-mine-and-shipped-the-branch-that-caused-it - the defect was named correctly, in the one section of the pull request reserved for things that are somebody else's (2026-11-02, research seat)

**What happened.** The superseded run of this seat added
`tools/root_scratch.py` and `tests/test_root_scratch.py`, and ended its pull
request with this line under **Seen and not mine**:

> `tools/ci_coverage.py` exits FAIL on `main` right now: 14 of 81 test files
> run in CI and 67 run in no workflow [...] the six tests this run adds land
> in the 67.

Every clause of that is true. The last one is a statement that the run's own
diff breaks a ratchet in this repository, written in the section whose rule is
"list what you noticed that was not yours to act on, one line each, and then
stop, because acting on it is the point you are not doing."

So the run saw the defect, described its own causation of it correctly, filed
it as another seat's, and shipped. `tests/test_ci_coverage.py::test_the_uncovered_set_has_not_grown`
then failed on the next run of this seat, which is this one, on a hand-run of
the suite. Repaired here by pinning the file with its reason, which is the
route that test's own failure message names for a seat that cannot write
`.github/workflows/checks.yml`.

**Why it is in this register.** The set growing is already
`INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` and that
finding is still correct, so this entry does not re-open it. What repeats here
is narrower and is incident 19's shape one level down: incident 19 is the org
discarding an event because it was shaped like nobody's deliverable, and
**Seen and not mine** exists because of it. This is the same filter misfiring
in the opposite direction. The section built to stop a seat throwing away what
it noticed became the place a seat put something it noticed about itself, and
the sentence "acting on it is the point you are not doing" read as permission.

**The precondition, because it is not carelessness.** The run was correct that
the ratchet is red on `main` for 67 other files. A seat that measures a gate
already failing for reasons that are genuinely not its own, and then adds one
more line to the same failure, sees a number it is not responsible for rather
than a condition it just broke. The red on `main` is what made the seat's own
red look like weather.

**The remedy, and it is one sentence rather than a tool.** A line under
**Seen and not mine** that names this run's own diff is not a line for that
section. The test is whether the sentence contains a possessive about your own
branch; if it does, the item is yours and the section is the wrong place for
it. Offered to the ExO seat, which owns the charter text that twelve seats
share, rather than written into one charter by the seat that failed it.

Ban list checked on this entry.
