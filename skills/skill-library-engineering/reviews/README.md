# skill-library-engineering: consumer reports

The lane is open and empty. File as `YYYY-MM-DD-<consumer>.md` against the
contract in
[skills/_validation/reviews/README.md](../../_validation/reviews/README.md).

This skill has a peculiar standing. Its subject is the skill file, so alexandria
is its own heaviest consumer: every SKILL.md in this library is written under it
and the trigger suite in `skills/_validation/` is one of its prescriptions
running in production. That makes a report from outside the library worth
several from inside it.

Most wanted:

- **The grounding finding, with its configuration.** This skill says a
  hand-written skill measured net negative against loading nothing, and then
  asks you to write one. On 2026-10-26 that finding was narrowed by re-reading
  the paper: it holds in one of three published model-harness configurations
  and the other two were net positive. So the report this library most needs is
  from anyone who compared a described-from-the-task file against a
  recorded-runs file on their own tasks and in their own harness, whichever way
  it went.
- **The full-body repair.** Delta 3 says that showing the router the whole skill
  body does not fix a bad pick, on a measurement where the correct body was in
  the prompt for 92 percent of queries and the picker still chose another skill
  on 29 percent of them. Anyone who tried that repair and had it work holds a
  contradiction.
- **The metadata versus body fork.** The advice changes completely depending on
  what your harness routes on. A report should say which fork the consumer was
  on and whether the skill made that clear before they wrote anything.
- **Three rounds.** Cheap to check and easy to get wrong in either direction. If
  your fourth round earned its cost, that contradicts a number here.
