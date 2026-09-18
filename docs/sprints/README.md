# Sprints

One file per sprint, named `sprint-YYYY-MM-DD.md` by its Monday. Written by
the project manager agent (prompts/pm-agent.md), committed by the owner's
merge, read by the engineer agent every morning. The newest file is the
current sprint.

Format:

```markdown
# Sprint YYYY-MM-DD — <sprint goal, one sentence>

## Backlog

1. **<item>** (engineer) — <what done means, verifiable in one session>
2. ...up to five items, in build order

## Notes for the engineer

- <orientation-critical notes, if any>

## Retrospective

<written by the PM agent the following Monday: shipped vs planned,
velocity vs prior sprints, blockers, one process improvement>
```
