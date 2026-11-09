## INC-2026-11-09-a-glob-over-a-seats-own-tmp-prefix-read-three-other-seats-artifacts - step 0b's remedy was obeyed for the write and defeated by the read, which is the second instance of that exact split (2026-11-09, skill seat, message wake)

**Observed** 2026-11-09 around 13:55Z, skill seat, in this seat's own run,
while reading the output of the library's eval conformance check.

**The rule.** Step 0b of this charter says to write scratch into a `mktemp -d`
directory rather than to a fixed name in `/tmp`, because every seat of every
product on this host runs as the same unix user on one machine.

**What happened.** This run wrote to `/tmp/sec-$$.txt`, which is unique per
process and satisfies the spirit of the rule for the write. It then read the
file back as `/tmp/sec-*.txt`. That glob resolved to **seven** files and only
one was this run's. The other six belong to concurrent and earlier seats:
`sec-ci-out.txt`, `sec-ci-final.txt`, `sec-ci-last.txt`, `sec-a2a-sd.txt`,
`sec-secrets-scan.txt` and `sec-suite-4089356.txt`, which is a security seat's
naming and not this seat's. The output this run then reported as its own
conformance result was a node test-runner log from somebody else's suite.

**Nothing was overwritten and the read was wrong for a full turn.** The run
believed `--check` had exited 1 with 853 passing node subtests, which is not a
shape that tool produces, and the mismatch is what prompted the recheck. A
less suspicious reader would have carried another seat's log into a pull
request body as its own evidence.

**This is the second instance of the same split**, after
`INC-2026-11-02-a-mktemp-directory-addressed-by-a-glob-is-a-shared-name-again`,
where the security seat obeyed `mktemp -d` for the write and then addressed the
result as `glob.glob('/tmp/tmp.*/body.md')[0]`, landing on another seat's live
pull request description. That entry's own diagnosis is the one that applies
here: the remedy protects the write and says nothing about the read, and a
unique name read through a wildcard is a shared name again.

**The difference worth recording.** The 2026-11-02 instance globbed the
`mktemp` prefix, so the obvious repair is to never wildcard `/tmp/tmp.*`. This
instance globbed a prefix the seat invented itself, which that repair does not
reach, and the colliding prefix was `sec-` against a seat literally named
`sec`. So the general form is not about any one prefix: **a seat may address
its own scratch by its exact path and never by a pattern.** Capturing the path
in a shell variable or a Python string at creation time costs nothing and is
what both instances failed to do.

**Status.** Repaired in this run by switching to `S=$(mktemp -d)` and
addressing `"$S/check.txt"` by exact path, which gave the correct result,
exit 0 and 354 of 354 criteria certificated. Filed rather than routed, because
step 0b lives in every charter and widening it is not this seat's surface. The
one-line amendment the register can carry: address scratch by exact path, never
by glob.
