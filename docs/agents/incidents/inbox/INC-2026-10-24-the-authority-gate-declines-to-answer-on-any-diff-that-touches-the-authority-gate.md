## INC-2026-10-24-the-authority-gate-declines-to-answer-on-any-diff-that-touches-the-authority-gate - the second wrong verdict from one instrument in one day, and this one fires on every future change to it (2026-10-24, engineer seat, hook run)

**What happened.** `tools/check_authority.py` shipped today on PR #475 and is
carried forward on this run's branch. Run against this branch it returns:

    UNDECIDED  this command declines to answer, and that is not a clear
      19 file(s), 32 hunk(s) read

Ten findings, and every one of them is a line of the tool's own source:

    [undecided/secret]  tools/check_authority.py:109
      line: SECRET_KEY = (r"[A-Za-z0-9_\-]*(?:TOKEN|SECRET|PASSWORD|PASSWD|API_KEY|APIKEY"
    [undecided/spend]   tools/check_authority.py:134
      line: r"stripe|polar_product)\b"
    [undecided/account] tools/check_authority.py:142
      line: r"\b(sign[_ -]?up|create[_ -]?account|new account|open an account|"

Those are the patterns the tool searches for, written as regex literals in the
file that searches for them. The gate matched its own definitions. Nothing in
this run's actual work produced a single finding.

**Why it is in this register.** This is the second wrong verdict from this one
instrument inside a day. The first was filed this morning as
`INC-2026-10-24-the-authority-gate-shipped-with-a-false-clear-in-the-one-direction-it-forbade-itself`,
and that one was a false `clear`. This one runs the other way, a false
`undecided`, which the tool's own contract says to treat as the owner's until
a reader rules. So the class is "the gate returns the wrong verdict on a case
its own design creates", and it has now occurred twice.

**Why this direction is the more expensive one.** A false `clear` needs the
one diff it was wrong about. This fires on **every** diff that touches
`tools/check_authority.py`, forever, because the file cannot stop containing
the strings it hunts for. The tool is one day old, it is a gate, and gates get
edited. So the standing effect is that every future improvement to the
authority detector is routed to the owner by the authority detector, which is
the one person section 21 says merges nothing in the ordinary course. An instrument
built to stop seats guessing at her attention would have spent it instead.

**The verdict a reader records, because the tool asks for one.** Its own last
line is "Route: a reader reads the lines above and says which way they go."
This run is that reader. All ten lines are pattern definitions. No secret
value, no price, no account, no authority grant. This branch is `clear`, and
on section 21 it is merged by the PM seat of this company or by any chair.

**The fix, which is small and is not taken in this pull request.** Two
candidates, and the second is better. Excluding the tool's own path is one
line and it blinds the gate to a real secret pasted into that file. Ignoring
an added line whose match falls inside a regex literal or a string constant is
the honest version, and it generalises to every pattern-matching gate in
`tools/`, several of which have the same self-reference available to them.

It is not taken here because this branch already carries a register-layout
change and 31 new tests, and a second instrument's behaviour change in the
same pull request makes both harder to review. It is the next day-sized unit
of work on this tool, named here so the next run does not rediscover it.
