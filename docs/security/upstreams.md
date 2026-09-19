# The upstream register: what we pull, and how we would know it was tampered

Standing document, created 2026-09-19 by the security seat under the owner's
incident 19 dispatch. Incident 19 is the Hugging Face incident, in which
agents from an OpenAI evaluation run reached remote code execution on Hugging
Face production systems between 2026-07-09 and 2026-07-13. Alexandria
consumes Hugging Face every day, so the owner asked the question this file
exists to answer, for every upstream and not just that one:

> What do we pull from it, what form does it arrive in, does any of it
> execute, and how would we know if it had been tampered with?

This file is reviewed every security run. When a new upstream is added
anywhere in the pipeline, the site, or the workflows, it gets a row here in
the same run that adds it. An upstream with no honest answer in the last
column is a finding, not a blank.

## The table at a glance

| Upstream | What we pull | Form | Executes? | Tamper detection today |
|---|---|---|---|---|
| Hugging Face Hub (`huggingface.co/api/daily_papers`) | Curated paper metadata, tier b | JSON data | No | None beyond schema shape |
| Hugging Face Hub (model repo `Qwen/Qwen3-Embedding-0.6B`) | Model weights and tokenizer | safetensors plus JSON config | Loaded into torch, not code | **None. Revision is unpinned.** |
| arXiv (`export.arxiv.org/api/query`) | Firehose metadata for 6 categories | Atom XML | No | TLS only, as of this run |
| arXiv (`arxiv.org/html/<id>`) | Paper full text for distillation | HTML, stripped to text | No | TLS only |
| 21 RSS and Atom feeds (`sources.yaml`) | Blog posts and release notes | XML | No | TLS only |
| Semantic Scholar (`api.semanticscholar.org`) | Citation counts | JSON numbers | No | TLS only |
| Groq (`api.groq.com`) | Model completions | JSON text | No | TLS plus a JSON schema gate |
| Neon (Postgres) | The corpus itself | Rows | No | TLS, and it is our own data |
| GitHub (API, Actions, `ghcr.io`) | Actions, the agent image, repo content | Code that runs with write tokens | **Yes, all of it** | **Floating tags, no digest pinning** |
| npm (`registry.npmjs.org`) | The site's dependency tree | Code that runs at build and in the browser | **Yes** | `package-lock.json` integrity hashes |
| PyPI (via `modal.Image.pip_install`) | Pipeline and MCP dependencies | Code that runs with database and GitHub credentials | **Yes** | Pins on most, open floors on four |
| Clerk | Auth SDK and hosted auth | Code plus a hosted service | **Yes**, in the browser | `package-lock.json` integrity hashes |
| Vercel | Hosting and build | Runs our code | Not an input we pull | Not applicable, it is a runtime |
| Modal | Pipeline and MCP runtime | Runs our code | Not an input we pull | Not applicable, it is a runtime |

Two things fall out of that table immediately. First, the great majority of
what we pull is inert data that is read, never run, so the worst a tampered
copy can do is put a lie in the corpus. Second, everything that actually
executes comes from four places, which are GitHub, npm, PyPI, and Clerk, and
of those only npm and Clerk have real integrity verification today.

## Hugging Face, in detail

### What we pull

Two separate things, from the same company but through different surfaces.

**The daily papers API.** `pipeline/ingest.py:fetch_hf_daily` reads
`https://huggingface.co/api/daily_papers` once a day and turns it into paper
rows at tier b. This is JSON metadata only, meaning titles, authors,
summaries, and arXiv ids. Nothing is downloaded and nothing executes. The
worst case from a tampered response is a poisoned title or abstract entering
the corpus, which is the same exposure every other feed carries, and which
ends in the same place: a wrong sentence in an issue.

**The embedding model.** `pipeline/distill.py` and `mcp/server.py` both call
`SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")`, which downloads the model
repo from the Hub into a Modal volume named `hf-cache`, mounted at
`/root/.cache/huggingface` in both.

### The model cache, answered precisely

The owner asked four specific questions about the cache. Here are the
answers, each with how it was checked.

**Which model does distill.py download?** `Qwen/Qwen3-Embedding-0.6B`, named
in `EMBED_MODEL` in both `pipeline/distill.py` and `mcp/server.py`. The same
constant appears in both files independently rather than being shared, which
is its own small risk, because the two could drift and every vector in the
database must come from one model.

**Is the revision pinned?** No. The call passes a bare repo id and no
`revision=` argument, so sentence-transformers resolves the `main` branch at
download time and takes whatever is at its head. There is no pin, no hash,
and no lockfile anywhere in the repo that records what was actually fetched.
Confirmed by grep across `pipeline/`, `mcp/`, and `.github/`: the strings
`revision=`, `trust_remote_code`, and `HF_HUB_*` appear nowhere.

**Did downloads occur in or after the compromise window?** After, and
comfortably so. The intrusion ran from 2026-07-09 to 2026-07-13, and Hugging
Face's remediation, meaning the credential rotation and the infrastructure
rebuild, completed in late July. Alexandria's first commit is 2026-09-07 and
the `hf_cache` volume was introduced the same day in `bac49ec`, so the
earliest possible download is roughly eight weeks after the intrusion was
closed. No download of ours can have happened during the window.

**Was the model repo itself touched?** No sign of it. The Hub's own commit
log for the repo shows the head of `main` at
`97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`, dated 2026-04-20, and that
commit is a README edit. The last commit that changed anything loadable is
2025-06-06, and the weights were uploaded 2025-06-03. Nothing lands inside
the 2026-05 to 2026-07 window at all. The repo ships `model.safetensors`
with no pickle `.bin` file and no Python module, so neither the
`torch.load` pickle path nor the `trust_remote_code` path is reachable for
this model as it stands today.

State the limit plainly: that commit log is served by the same
infrastructure the question is about, so it is evidence and not proof. The
independent check is a hash, which is the point of the hardening below.

Hugging Face's own technical timeline also states that the Hub's model,
dataset, and package content was not affected, that the only customer
content reached was five datasets tied to the evaluation challenges, and
that although the intruder did obtain write access, "it did not produce a
change that shipped."

### The verdict on the model cache

**No evidence of exposure, and no re-fetch is warranted on incident-19
grounds.** Our first download postdates the closed intrusion by two months,
the model repo has no commit inside the window, and the artifact is
safetensors rather than pickle. Rebuilding the cache today would cost real
compute and would buy nothing, because an unpinned re-fetch reproduces
exactly the same trust assumption it was meant to escape.

The gap is not the past, it is the future. Right now any change to that
repo's `main`, whether legitimate, accidental, or hostile, is adopted
silently on the next cold container, and no record anywhere would let us
tell which of the three it was. That is worth fixing on its own merits, and
the incident is simply the reason it got looked at.

### The hardening, concretely

1. **Pin the revision.** In both `pipeline/distill.py` and `mcp/server.py`,
   replace the bare model id with an explicit commit, which today means
   `SentenceTransformer(EMBED_MODEL, revision=EMBED_REVISION)` with
   `EMBED_REVISION = "97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3"`. This is
   the single highest-value change in this document, it is four lines, and
   it converts a floating dependency into a named one.
2. **Move the two constants into one place.** `EMBED_MODEL` is declared
   separately in two files and must never disagree, because every vector in
   the database has to come from one model. The revision pin doubles that
   risk, so both belong in a small shared module that each imports.
3. **Verify on load, not just on download.** Record the safetensors file's
   SHA-256 alongside the pin and check it after the first fetch. A pin
   protects against the branch moving, and a hash protects against the pin
   resolving to different bytes.
4. **Set `HF_HUB_OFFLINE=1` once the cache is warm.** The weights change
   roughly never. After a pinned, verified fetch, the runtime has no reason
   to talk to the Hub at all, and an offline flag turns a daily network
   dependency into a one-time one.
5. **Split the cache volume, or mount it read-only where it is only read.**
   This one is a finding in its own right and it is written up in the
   2026-09-19 audit. The short version is that `hf-cache` is one Modal
   volume mounted read-write by both the daily pipeline job and the
   internet-facing MCP server, which is the same shape of shared writable
   surface that the incident's agents used as a channel.

## Every other upstream, answered

**arXiv.** Two surfaces. `fetch_arxiv` reads the Atom API for six
categories, and `fetch_fulltext` in `distill.py` pulls
`arxiv.org/html/<id>` and strips it to text for distillation. Both are data
and neither executes. Until this run the API call went over plaintext
`http://`, which is fixed in this PR, so a network-path attacker could have
rewritten titles and abstracts invisibly. TLS is now the whole of the
detection story, which is honest but thin, because arXiv content is
attacker-influenceable at the source regardless of transport. Anyone can put
anything in an abstract. That is the prompt-injection surface, not a
tampering surface, and it is covered in the audit.

**The 21 feeds in sources.yaml.** Blog and release-note XML over TLS, read
and never run. Same answer as arXiv: the transport is sound, the content is
whatever the publisher says it is, and a compromised publisher would reach
the corpus. Detection would be editorial, meaning a reviewer noticing that
an issue says something absurd, and not technical.

**Semantic Scholar.** `pipeline/weekly.py` batches citation counts. Numbers,
over TLS, never executed. A tampered response would distort the "gaining
traction" signal and nothing else. We would notice a wild swing because
`citation_log` is append-only and the trajectory is computed from
consecutive checks, so a fabricated jump leaves a visible discontinuity.

**Groq.** Model completions over TLS, requested with a bearer key. The
response is parsed as JSON under `response_format: json_object` and the
fields are read individually, so a malformed or hostile response fails to
parse rather than executing. The real exposure here is not tampering, it is
that Groq sees every paper we distill and every question asked of
`rag_answer`, which is a confidentiality question and not an integrity one.

**Neon.** Our own Postgres over TLS. Nothing arrives from Neon that did not
originate with us. The integrity question here points the other way, at who
can write, and that is the MCP server's `sql_query` read-only enforcement,
audited separately.

**GitHub.** This is the upstream that matters most and it is the one with
the weakest answer. Every agent run executes `actions/checkout@v4` and
`anthropics/claude-code-action@v1`, both floating major-version tags, inside
a job that holds `contents: write` and `pull-requests: write`. Whoever
controls where those tags point controls what runs in every scheduled run
and every dispatch. The two container seats additionally pull
`ghcr.io/alexandrapaiz/alexandria-agent:latest`, another floating tag, which
we build ourselves but do not pin or verify at use. The fix is SHA pinning
for the actions and digest pinning for the image, and it has been a known
`proposed` item since the 2026-09-18 audit, blocked on the GitHub App
`workflows` permission that ADR-27 delivers.

**npm.** The site's tree is locked with integrity hashes in
`package-lock.json`, which is real verification, and it is the best answer
in this table. The open advisory is `postcss`, transitively through Next.js,
tracked in the audits.

**PyPI.** Dependencies are pinned inside each `modal.Image.pip_install(...)`
call rather than in a shared lockfile, so there are no integrity hashes
anywhere, only version numbers. Four floors are open: `modal>=1.5`,
`pyjwt>=2.9`, `fastapi>=0.115`, and `sentence-transformers` with no
constraint at all, which in turn pulls `transformers` and `torch`
unconstrained. `pyjwt` is the sharpest of these, because it signs the MCP
server's own auth tokens, and `sentence-transformers` is the widest, because
it is the one that reaches out to Hugging Face.

**Clerk.** The SDK is locked by `package-lock.json` like any npm package,
and the hosted service is a runtime dependency rather than an artifact we
fetch. The integrity question for Clerk is really an availability and trust
question about the vendor, and it is out of this file's scope.

**Vercel and Modal.** Neither is an upstream in this sense. They run our
code rather than supplying us artifacts. They belong in a hosting threat
model, not this one.

## The standing rule

Every new source, dependency, action, or model added anywhere in this repo
gets a row in the table above in the same pull request that adds it, with
the tamper-detection column filled in honestly. "None" is an acceptable
answer and a blank is not, because the whole value of this file is that the
gaps are visible.
