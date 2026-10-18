# Engineer run note, 2026-10-18 — the skills become installable

The run's report is the pull request description. This note holds the three
things a later run will want and a description is the wrong place for.

## The install path, measured rather than described

Every number below came out of `claude` on this machine on 2026-10-18, against
a fresh `git clone` of the branch rather than the working tree, so what was
measured is what is committed.

```
git clone --depth 1 --branch <this branch> https://github.com/alexandrapaiz/alexandria.git
claude plugin marketplace add /tmp/clone-proof     # Successfully added marketplace: alexandria
claude plugin install alexandria-skills@alexandria # Successfully installed plugin
claude plugin details alexandria-skills
```

```
Component inventory
  Skills (9)  agent-containment, agent-memory-selection, agent-security-measurement,
              context-window-engineering, evaluation-integrity, harness-engineering,
              recursive-harness-self-improvement, self-improving-post-training-loops,
              skill-library-engineering
  Agents (0)  Hooks (0)  MCP servers (0)  LSP servers (0)

Projected token cost
  Always-on:   ~1,887 tok   added to every session
```

The per-skill on-invoke costs, from the same output, run 1.5k to 6.7k tokens.
`evaluation-integrity` is the most expensive at ~6.7k and
`context-window-engineering` the cheapest at ~1.5k.

## Three things learned about the format that are not in its documentation

1. **A declared `skills` path is additive, not authoritative.** A manifest
   carrying `"skills": ["./nope"]` still loaded all nine from the conventional
   `skills/<name>/SKILL.md` location, so a wrong declaration changes nothing
   at runtime and is invisible. `claude plugin validate . --strict` does catch
   it, with `Path not found: ./nope. The runtime loader will report this as a
   load failure.` The live manifest therefore declares no component paths at
   all: the convention is the single source of truth, and a second
   declaration of it can only rot.

2. **`claude plugin validate .` walks the marketplace entry into the plugin.**
   Pointed at the repository root it resolves `marketplace.json`, follows the
   entry's `source` to `plugin.json`, and reports an error inside the second
   as `plugins[0] plugin.json → skills[0]`. One command covers both files.

3. **`contents` in the `--json` report is empty in every mode tried here.**
   The skills, agents and commands a plugin ships are not listed by
   `validate`. `claude plugin details <name>` lists them, and it needs the
   plugin installed. So the only way to see what a plugin actually ships is to
   install it, which is why this run installed from a clone instead of
   asserting from the manifest.

## A failed attempt worth not repeating

`claude plugin marketplace add alexandrapaiz/alexandria` against `main` fails
today with `Marketplace file not found at
~/.claude/plugins/marketplaces/alexandrapaiz-alexandria/.claude-plugin/marketplace.json`,
which is correct: the manifest is on this branch and not yet on `main`. The
CLI cleans up its own clone on that failure, so there is no leftover checkout
to point at a branch, and `marketplace add` takes no git ref. That is why the
proof above goes through a local clone. After this merges, the two published
lines are the real test and anyone can run them.

## What this run did not take, and why

`docs/agents/press-rehearsal.md` is still a specification with no code behind
it, and this charter asks a run that declines it to say so. Declined again
today for a different reason than a busy sprint: the owner reset the product
on 2026-10-17 and the five sellable conditions in the PM's regroom are the
work, and the press rehearsal's third gate guards a provider change that no
one is making this week. It stays the right thing to build on the first day
the press is the subject again.
