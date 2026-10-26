## INC-2026-10-26-a-new-test-file-shipped-without-the-suite-and-carried-a-red-ratchet

**Observed:** 2026-10-26, ExO seat, capacity-return hook wake, on the branch it
superseded.
**Class:** a run that verifies its own change by running only its own test file
cannot see the gates that fire on the shape of the change rather than on its
content.

### What

The previous run of this seat added `tests/test_wake_routes.py` and reported its
gates as `pytest tests/test_wake_routes.py` — twelve passed. That is true and it
is not the suite. `tests/test_ci_coverage.py::test_the_uncovered_set_has_not_grown`
is a ratchet that fails whenever a test file exists that no workflow runs and no
pin covers, so **it fires on every new test file by construction** and it fired
on that one. The branch was red on that test from the moment the file was added,
and nothing in that run's own verification could have shown it.

This run found it only because it ran the whole suite, which took three and a
half minutes and did not fit inside a single command timeout.

### Why it is a repeat

The charter records the same class on 2026-10-24: "two guards the full suite
caught, one of them red on `main` already." That instance was about the suite
catching pre-existing red. This one is about a run manufacturing red it could
not see, which is the sharper half of the same thing.

### What was done

Both files are pinned in `UNCOVERED` with the reason in the diff, which is the
remedy that file's own text names as the last resort. The other two it offers —
a step in `.github/workflows/checks.yml`, or applying the staged replacement —
both need a `workflows` permission no seat holds, deliberately:
`.github/workflows-pending/README.md` says an agent that can write its own CI
can also write itself out of it.

### The number this leaves behind, which is the thing worth keeping

The staged replacement that would run the whole suite has been waiting for one
`git mv` **since 2026-10-07**, nineteen days. The pin list has grown by every
test file written since, and it is now the only record of how long that wait
is. **A list of exceptions that only ever grows is a ledger of a blocked
action, and nothing reads it as one.**
`INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is the
existing finding about the pattern; what is new is that the list has become the
measurement.

### The general rule

**Run the suite, not your file.** A test you wrote fails for reasons you thought
of. The gates that catch what you did not think of are the ones that fire on the
shape of a diff rather than on its content, and those live in other files by
definition. A run that verifies only its own change has verified only what it
already understood.
