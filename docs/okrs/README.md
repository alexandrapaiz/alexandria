# OKRs

One file per quarter, named `okrs-YYYY-QN.md`. Drafted by the OKR agent
(prompts/okr-agent.md) on the first run of each quarter, committed by the
owner's merge, checked monthly. The PM agent reads the newest file when
planning sprints; every sprint goal names the objective it serves.

Format:

```markdown
# OKRs YYYY-QN

Purpose (vision.md §0): autonomous organism, standalone knowledge
business, north star = product quality vs industry benchmarks.

## O1 — <objective>
- KR1: <measurable, dated>
- KR2: ...

...at most three objectives, three KRs each. At least one objective
serves the benchmark trendline; at least one increases autonomy.

## Check-in YYYY-MM

- Benchmark: <the five-axis scores vs this month's three competitors,
  with the month-over-month trend>
- KR status: <each KR: on-track / at-risk / missed / done, with evidence>
- Drift: <orphan work, orphan objectives, manual substitutions>

## Retrospective (quarter close)

<final scoring, what the quarter taught, written by the OKR agent when
it opens the next quarter's file>
```
