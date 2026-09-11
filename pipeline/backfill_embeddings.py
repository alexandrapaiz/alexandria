"""One-off backfill: embed bronze paper abstracts with Qwen3-Embedding-0.6B.

Gives papers the same vector space as claims, enabling dedupe, related-paper
lookups, and semantic search over the full bronze layer. Manual-run only —
no schedule (new papers can be embedded by future runs of the same function;
if this becomes routine it can fold into an existing cron).

    modal run pipeline/backfill_embeddings.py
"""

import modal

EMBED_MODEL = "Qwen/Qwen3-Embedding-0.6B"
BATCH = 64

image = modal.Image.debian_slim().pip_install(
    "psycopg[binary]==3.2.4", "sentence-transformers"
)
app = modal.App("alexandria-backfill", image=image)
hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)


@app.function(
    secrets=[modal.Secret.from_name("neon")],
    volumes={"/root/.cache/huggingface": hf_cache},
    timeout=3600,
)
def backfill() -> int:
    import os

    import psycopg
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(EMBED_MODEL)
    done = 0
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        while True:
            rows = conn.execute(
                """
                select id, title, coalesce(abstract, '')
                from papers where embedding is null
                order by fetched_at limit %s
                """,
                (BATCH,),
            ).fetchall()
            if not rows:
                break
            texts = [f"{title}\n\n{abstract[:2000]}" for _, title, abstract in rows]
            vectors = model.encode(texts, normalize_embeddings=True)
            for (pid, _, _), vec in zip(rows, vectors):
                conn.execute(
                    "update papers set embedding = %s::vector where id = %s",
                    (str(vec.tolist()), pid),
                )
            conn.commit()
            done += len(rows)
            print(f"embedded {done} papers")
    return done


@app.local_entrypoint()
def main():
    print(f"total embedded: {backfill.remote()}")
