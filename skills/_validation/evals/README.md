# Skill evals: the with-versus-without task sets

ADR-36 (owner-directed, 2026-09-29): every skill carries an eval. A skill's
claim on a builder's context window is a claim that the builder does better
work with it loaded than without it, and until that is measured the claim is
an assertion. A skill with no eval is `status: draft`, never `active`. A skill
whose eval shows no gain is retired with the numbers, which is a finding and
not a failure.

The tasks live next to the skill they measure, one file each:

```
skills/<slug>/evals/evals.json
```

This directory holds the contract they share. The harness that runs them is
the engineer's build (ADR-36 consequences, branch
`engineer/2026-09-30-skill-registrar-and-evals`); the tasks are the skill
seat's.

## The design

Every task runs twice, once with the skill loaded into the subject model's
context and once without, on the same subject model, with the same seed where
the provider allows it, repeated several times. The reported number is the
delta between the two arms and its spread. A delta inside the spread is not a
result.

- **Subject model.** The funded open model by default (Kimi, ADR-32), so the
  suite is cheap enough to re-run on every skill change. A Claude run is the
  monthly benchmark the OKR seat reports.
- **Judge.** For rubric tasks only, and always a different model from the
  subject. A judge that is also the subject grades its own homework.
- **Task provenance.** Every task names the paper whose situation it
  reproduces and the claim ids it exercises, per ADR-35. The task is the
  situation the paper studied, restated as work a builder would actually be
  handed.
- **Task coverage.** Added 2026-09-30. Every task also carries `sections`, the
  list of `## ` headings of its skill that the task actually exercises, copied
  verbatim so a string comparison resolves it. Controls carry an empty list,
  and so does a treatment task that tests a boundary rather than a section. The
  field exists because `source.claims` cannot do this job: it was wrong in two
  of the first eight suites, in both cases naming claims the skill does cite
  and a task that tested none of that section, which a claim-set comparison
  passes (`INC-2026-09-30-eval-task-claims-unchecked`). Two checks the harness
  should run off it, and the second is the one that catches the defect:
  every string in `sections` is a heading of that SKILL.md, and every heading
  of that SKILL.md other than the Apply checklist and the caveats appears in at
  least one task's `sections`. Both are decidable with no model. A section with
  no task is what a per-section *Validation:* tag has to say out loud (ADR-38),
  so it is a finding rather than an error.

## Two kinds of task

**Treatment tasks**, 6 to 10 per skill, are situations the skill is meant to
change. Each carries either a hard check or a rubric, never both.

**Control tasks**, 2 per skill, are situations the skill must not change. They
are written to be adjacent: they borrow the skill's vocabulary while needing
none of its content, so a skill that fires too eagerly or intrudes on ordinary
work shows up as a loss here. A control is passed when the delta between the
two arms sits inside the spread. A control that improves is as much a finding
as one that regresses, because it means the task belonged in the treatment set.

## The check

`check.type` is one of:

- `tests_pass`. The harness writes `files` into a scratch directory, puts the
  model's output at `answer_path`, runs `command`, and reads the exit code.
  `pass_condition` states what counts. The test file is part of the task and is
  never shown to the subject model.
- `parses`. The model's output must parse under `format` and satisfy every
  predicate in `assertions`. Each assertion is a named, machine-decidable
  statement about the parsed object. This is the check to reach for when the
  task's answer is a config, a patch, or a structured plan.
- `number_in_range`. `extract` names the quantity, and the answer passes when
  it lands within `range`. Used only where the paper fixes the number by
  arithmetic rather than by result, so the task is not a memory test.
- `rubric`. 3 to 5 criteria, each scored 0, 1 or 2 by the judge against
  written anchors. `criteria[].id` is stable so a regression can be traced to
  one criterion rather than to a total. The task's score is the sum; the
  reported result is the with-minus-without delta on that sum.

Rubric criteria are written so that the unaided answer can score well on the
ordinary-competence criteria and still lose the ones the skill exists for.
That separation is the point: a rubric where the skill wins every criterion is
measuring whether the judge can see the skill, not whether the skill helped.

## Fields

```jsonc
{
  "skill": "<slug>",              // must equal the directory name
  "suite_version": 1,
  "written": "YYYY-MM-DD",
  "author": "skill agent (ADR-22)",
  "adr": "ADR-36",
  "subject_model": "...", "judge": "...",
  "tasks": [{
    "id": "<slug-prefix>-t1",     // -t for treatment, -c for control
    "kind": "treatment" | "control",
    "form": "prompt" | "project", // a project carries starter `files`
    "situation": "the paper's setup in one line",
    "source": { "paper": "...", "arxiv": "arxiv.org/abs/...", "claims": [1,2] },
    "prompt": "what the subject model is handed, verbatim",
    "files": { "path": "contents" },      // project tasks only
    "without_skill": "the failure the unaided arm is expected to show",
    "with_skill": "what the loaded arm should do differently",
    "check": { "type": "...", ... }
  }]
}
```

`without_skill` is the hypothesis the task tests, and writing it down before
the run is what stops the suite from being scored after the fact. Where the
unaided arm turns out to do the right thing anyway, the honest result is that
the task does not discriminate, and it is replaced rather than reweighted.

## What these tasks do not measure

Whether the skill fires. That is the trigger test
(`skills/_validation/trigger_test.py` over each skill's `triggers.json`), and
it is a separate instrument with a separate failure mode. A skill can win its
eval and never load, which is the market's 69 percent problem, and it can fire
perfectly and teach nothing. Both instruments have to pass.
