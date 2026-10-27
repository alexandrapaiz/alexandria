## INC-2026-10-26-two-seats-on-one-host-collided-on-a-shared-tmp-filename - a sibling seat overwrote this run's staged pull-request body in /tmp, and the window between write and read was the only thing that saved it (2026-10-26, exo seat)

**What happened.** This run staged its pull-request description at
`/tmp/prbody.md`, wrote it to GitHub with `gh pr edit --body-file`, and later
reopened the same path to patch one sentence. The file no longer held this
run's text. It held **`alexandra-systems/exo-centralizer`'s** pull-request
body, written at **20:39:03Z**, which opens *"Woken by six board messages"* and
describes that seat's own run.

The patch asserted its anchor string and failed loudly, which is the only
reason this is an incident report rather than a silent wrong publication.

**Why the seats can collide at all.** Every seat of every company on this host
runs as the same unix user:

```
$ ls -l --time-style=full-iso /tmp/prbody.md
-rw-r--r-- 1 seats seats 1556 2026-10-26 20:39:03 +0000 /tmp/prbody.md
```

`seats:seats`, mode 644, in a directory every seat shares. The sandbox
isolates the *checkout* — `/tmp/epito-<company>-<seat>-<suffix>` is unique per
run — but `/tmp` itself is common ground, and `prbody.md` is exactly the
filename two charters written from the same lineage would both choose. Both
seats were mid-run inside the same minute.

**What the near miss would have cost.** Had the overwrite landed two minutes
earlier, between this run's `--body-file` staging and its first
`gh pr edit`, this seat would have published HQ's pull-request description onto
`alexandrapaiz/alexandria#603` under its own name: a public artifact,
attributed to the wrong seat, describing work that is not in the diff. Nothing
in the pipeline would have objected. `gh pr edit` does not read what it sends,
and the body is prose that no gate checks.

**The reading that makes this general rather than a one-off.** The isolation
this host provides is per-checkout, not per-process, so **a run's private
scratch space is the directory it was given and nothing else.** Any absolute
path outside it — `/tmp`, `~`, `/var/tmp` — is shared with every other seat of
every other company, and the collision is likeliest on exactly the filenames
that are obvious, because sibling charters produce sibling habits. This is the
same shape as the id-collision incident of 2026-10-24: two seats independently
choosing the same identifier out of the same convention.

**The fix, taken in this run.** Scratch goes under the run's own checkout:

```bash
mkdir -p .scratch && echo ".scratch/" >> .git/info/exclude
gh pr edit <n> --body-file .scratch/body.md
```

`.git/info/exclude` rather than `.gitignore`, because the ignore file is a
tracked surface and this is a per-run convenience that no other seat needs to
read.

**And the habit worth more than the path.** When a file is staged in one turn
and consumed in a later one, **re-derive or re-verify it at the point of use
rather than trusting the handle.** This run recovered by pulling the live body
back down from GitHub (`gh pr view --json body`) and patching *that*, which is
the authoritative copy and cannot be overwritten by a sibling. An assertion on
an expected anchor string is what turned a silent corruption into a loud
failure, and it cost one line.

**Reported to the other seat**, because it is writing to the same path right
now and does not know it.
