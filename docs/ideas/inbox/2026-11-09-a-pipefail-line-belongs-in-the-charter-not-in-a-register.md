### 2026-11-09 - the pipe-eats-exit-code remedy is recorded correctly and fired on nobody, so it belongs where a seat reads before it works (engineer seat)

- Trigger: this run piped its full suite into `tail`, the suite died on a full
  disk, and the shell reported zero. Filed as
  `INC-2026-11-09-the-pipe-that-eats-an-exit-code-took-a-third-seat-run-and-it-was-the-seat-that-filed-the-first`.
  The first two instances were filed on 2026-11-02 **by this seat**, with the
  right remedy written out, and this seat typed the same pipe seven days later.
- What: the remedy is not the problem and writing it down again will not help.
  `set -o pipefail` or `${PIPESTATUS[0]}` is correct and it has been correct for
  a week. What is missing is a gate on checking rather than on recording, which
  is incident 20's standing finding and the thing `docs/agents/registers.md`
  exists to map. The charter already carries commands a seat must run at named
  moments: the unshallow pair before any comparison, the conflict-marker grep
  before shipping, `gh run list --workflow=checks.yml` before the log. Those
  fire because they are in the file every run reads at its start. A register
  entry fires on whoever opens the register, which is one seat, weekly.
- The proposal, concretely: one sentence in the `Check the register before you
  ship` section of `prompts/engineer-agent.md`, beside the existing commands,
  saying that a command whose exit code you intend to read is never piped, and
  that a pipe you want anyway needs `set -o pipefail` or `${PIPESTATUS[0]}`. The
  same sentence belongs in `docs/standards/lessons.md` under `any`, because the
  2026-11-02 entry has one instance from the skill seat and one from this one,
  so it is not a seat-specific habit.
- Why it is a proposal and not this run's diff: a charter edit is the owner's
  merge under §21, and this seat's charter forbids carrying a charter diff in
  the daily pull request in its own words. The lessons file is a vendored copy
  and a correction to it routes through the ExO seat's relay. So both halves are
  somebody else's merge, and filing is the whole of what this seat can do.
- First step: the PM posts it as a §22 ask with its own recommendation, since a
  charter line that adds a check is not a widening of this seat's authority and
  the forty-eight-hour silence rule applies.
- Cost: $0
- Status: proposed
