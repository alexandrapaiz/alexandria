# 2026-09-19 — the digest email, designed

The owner's order of 2026-09-19, relayed by the chair: the digest must look
like a newsletter and email is the delivery. This run designed
`site/emails/digest.html` and verified it by rendering real content into it
and looking at the pixels at 375 and 640.

## The evidence

| File | What it shows |
|---|---|
| `weekly-375-before.png`, `weekly-640-before.png` | what subscribers get today: `send_newsletter()`'s Georgia wrapper around raw rendered markdown, reproduced byte for byte by `before-plain-2026-W37.html` |
| `weekly-640-before-items.png` | the structural bug in today's email: the markdown's nested bullets flatten to the same level as the items they belong to, so evidence lines read as separate findings |
| `weekly-375-after.png`, `weekly-640-after.png` | the same 2026-W37 issue in the template |
| `weekly-640-after-items.png` | an item block: finding, body, numbered procedure, source link, host and path as the receipt |
| `weekly-375-after-sections.png` | the section rhythm down the issue |
| `weekly-640-after-close.png`, `daily-375-after-close.png` | the dual-audience close, the receipts line, the unsubscribe |
| `daily-375-after.png`, `daily-640-after.png` | a daily-shaped issue, sections Compounding / New and unproven / Left behind, evidence graded per item |
| `weekly-375-after-dark.png`, `daily-640-after-dark.png` | `prefers-color-scheme: dark`, designed rather than auto-inverted |
| `weekly-375-after-no-style-block.png` | the `<style>` block deleted, which is what Gmail does for accounts that are not Google accounts. The inline baseline carries the issue alone |
| `empty-day-375-after.png` | the smallest state the pipeline can send: the empty day from PR #35, no sections, no receipts |
| `fix-narrow-space-3x-before.png`, `fix-narrow-space-3x-after.png` | at 3x: the writing model's U+202F made "Claude Opus 5" read as "ClaudeOpus5" and put a gap before every percent sign. Normalised at fill time |
| `benchmark-morningbrew-640.png`, `benchmark-tldr-640.png` | the two issues studied for structure, 2026-09-18, captured with Playwright |

## Reproducing

    python3 docs/design/reviews/2026-09-19/render_sample.py

Writes `sample-weekly-2026-W37.html` and `sample-daily-2026-09-19.html` next
to itself from `site/content/issues/2026-W37.md` and `sample-daily.md`. The
two sample markdown files are fixtures written for this review, not issues,
and were never sent.
