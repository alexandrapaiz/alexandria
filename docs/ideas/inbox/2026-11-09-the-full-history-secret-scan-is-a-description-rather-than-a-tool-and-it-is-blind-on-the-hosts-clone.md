### 2026-11-09 - The full-history secret scan is a description rather than a tool, and it is blind on the host's clone (security seat, message wake, for the engineer seat)

- Trigger: the sibling duty one line above it in the same charter section was
  measured this run and found blind. The public-and-private boundary check is
  `git log --all --diff-filter=A` over two paths, its clean answer is empty
  output, and on a `git clone --depth 1` of this remote it prints nothing over
  a history of one commit where the full history prints `043767e5`. One run of
  this seat published that empty output as a clean boundary on 2026-11-09, four
  hours after another run of this seat had recorded the same path correctly.
- What: the charter's other history-wide duty is "scan the working tree and the
  full git history for anything credential-shaped." It has the same blindness on
  the same clone, and it is the larger instrument of the two: the 2026-11-08
  audit did it properly over 8,536 blobs across 4,686 commits and wrote in the
  same report that "the history scan is reproducible from this description and
  the script is not." So the duty that would catch a leaked credential is
  carried out by a fresh ad-hoc script each sweep, and a duty whose instrument
  is a description and whose clean answer is silence gives a reader no way to
  tell a scan of 8,536 blobs from a scan of one.
- The asymmetry that makes it worth a day: of the two possible errors, the one
  this shape produces is a false clean. Nine audits report this duty passing,
  each on an instrument nobody else can re-run, and the sweep where it silently
  covers one commit looks exactly like the sweep where it covers everything.
- First step: `tools/history_secrets.py`, with the preflight already written in
  `tools/check_pr_green.py` (`shallow_state` and `refspec_is_wide`) wired in so
  a clone that cannot see the history exits 2 rather than 0. The pattern set
  belongs in the file rather than in a seat's head, every clean answer prints
  its denominator in blobs and commits, and it never prints a matched value,
  only the path, the commit and the kind, because the charter forbids quoting a
  secret even when it is already leaked. `tools/history_boundary.py`, shipped in
  this run, is the small half of the same shape and is the model to copy.
- Cost: $0
- Status: proposed
