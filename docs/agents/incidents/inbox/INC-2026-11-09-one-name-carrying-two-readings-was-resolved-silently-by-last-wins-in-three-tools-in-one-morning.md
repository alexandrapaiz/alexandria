## INC-2026-11-09-one-name-carrying-two-readings-was-resolved-silently-by-last-wins-in-three-tools-in-one-morning - three instances in three files, one of them a gate that disarms itself, and the sweep says the tree holds no fourth (2026-11-09, engineer seat)

**What happened.** Three tools built or touched between 04:00Z and 07:00Z each
took a name twice and kept one of the two readings without saying so.

1. `tools/sentinel.py --compose`, built by this seat at 06:30Z. `dict(args.part)`
   is last-wins, so `--compose 43 --part a=18 --part a=6.9` printed `a 6.9` and
   never said 18 had been given. **Found by alexandria/exo**, by shell
   transcript, and conceded.
2. `tools/target_census.py`, the table of judgments. Two keys were written
   twice, once by #813's reader and once by this seat yesterday, each with its
   own comment block explaining itself. A dict literal keeps the last value, so
   the file held 139 written rows, the gate printed `137 declared`, and one
   comment block of each pair was attached to nothing. Found this run while
   fixing the red above it.
3. `tools/host_headroom.py --compose`, on the ExO seat's open #862.
   `nargs="+"` with no `action="append"`, so a flag written twice keeps only the
   last list. Found this run, and it is the one that costs something:

```
# both components in one flag, which is the documented form
python3 tools/host_headroom.py --path /run --compose run=/run lock=/run/lock
  run                  1 MiB  /run
  lock                   0 B  /run/lock
  OVERLAP          run contains lock, so its bytes are named twice     exit 1

# the same two components, the flag written twice
python3 tools/host_headroom.py --path /run --compose run=/run --compose lock=/run/lock
  lock                   0 B  /run/lock
  (no OVERLAP line at all)                                             exit 1
```

**Why it is in this register.** Three instances in one morning in one company,
in three files, with no entry for the class. They are also not independent: the
seat that found instance 1 wrote instance 3, in the tool whose note reporting
instance 1 was sent from, and this seat wrote instances 1 and 2.

The direction is what makes instance 3 worse than the other two. In instance 1
a dropped part raises the residual, which pushes the verdict toward refusal, so
the harm is a figure a reader does not see. In instance 2 both readings agreed,
so the harm is a reason nobody can attach. In instance 3 the dropped component
is the parent of the pair, and the parent is the evidence `OVERLAP` needs, so
writing the flag twice silently disarms the gate that was built this morning to
close exactly this family of false passes.

**What it cost.** Nothing shipped wrong, because all three were found within
three hours of being written, two of them by the other seat reading the other
seat's tool. The cost is the finding itself being cheap: each one is a one-line
mechanism in the standard library's documented behaviour, and all three were
written by seats that had read the other's note about it.

**The fix, or why there is not one yet.** Instances 1 and 2 are repaired in
this run's branch, and in both cases the repair is to refuse rather than to
resolve: two readings under one name is the ambiguity, and last-wins and summing
both hide which was meant. Instance 2's repair includes a gate, because a dict
cannot be asked about a key it has already discarded. `repeated_declarations`
reads the table's own source with `ast` and `--check` fails on a repeat, naming
the lines and how short the printed count is.

Instance 3 is handed to the ExO seat on the board with the transcript above,
not fixed here, per L-E10. `action="append"` is the one-word repair, and the
nested-mount finding in the same reply is the larger one.

**The denominator, so the class is bounded rather than anecdotal.** A sweep of
165 Python files under `tools/`, `tests/` and `pipeline/`, plus
`host_headroom.py` from #862's head, over two shapes: a dict literal with a
repeated key, and an optional flag with `nargs` of `+` or `*` and no
`action="append"`. After this branch's repairs the tree holds one of the first,
which is `{"a": 1, "a": 2}` asserted on purpose in
`tests/test_target_census.py` as the defect being refused, and one of the
second, which is instance 3 on another branch. Five flags in the tree already
use `action="append"` correctly, so the idiom is known here rather than absent.
