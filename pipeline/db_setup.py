"""One-off database administration, run through Modal so credentials stay in its secret store.

    modal run pipeline/db_setup.py::apply_schema
    modal run pipeline/db_setup.py::stats
"""

import modal

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4")
    .add_local_file("db/schema.sql", "/root/db/schema.sql")
)

app = modal.App("alexandria-db", image=image)


@app.function(secrets=[modal.Secret.from_name("neon")])
def apply_schema():
    import os

    import psycopg

    sql = open("/root/db/schema.sql").read()
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.execute(sql)
        tables = conn.execute(
            "select table_name from information_schema.tables where table_schema = 'public' order by 1"
        ).fetchall()
    print("tables:", [t[0] for t in tables])


@app.function(secrets=[modal.Secret.from_name("neon")])
def stats():
    import os

    import psycopg

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        for table in ("papers", "triage_log", "claims", "promotions"):
            n = conn.execute(f"select count(*) from {table}").fetchone()[0]
            print(f"{table}: {n}")
        by_source = conn.execute(
            "select source, count(*) from papers group by source order by 2 desc"
        ).fetchall()
        for source, n in by_source:
            print(f"  papers from {source}: {n}")
        by_tier = conn.execute(
            "select tier, count(*) from papers group by tier order by 1"
        ).fetchall()
        for tier, n in by_tier:
            print(f"  tier {tier}: {n}")
