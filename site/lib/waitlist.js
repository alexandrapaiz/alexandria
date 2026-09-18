import fs from "node:fs/promises";
import path from "node:path";

// Where an email goes when someone asks to be told that subscriptions opened.
// Stripe does not exist yet and the site has no database client yet, so this
// is a local append-only file with one job: lose nothing, and keep the shape
// the real table already expects.
//
// The seam the engineer wires later is this function and nothing else:
//
//   insert into subscribers (email, tier, status)
//   values ($1, 'digest', 'waitlist')
//   on conflict (email) do nothing
//
// Two notes for whoever does that wiring. First, db/schema.sql currently
// constrains status to ('active', 'unsubscribed'), so 'waitlist' needs adding
// to that check before the insert will run. Second, the file below is local
// disk: on a serverless host it does not survive a redeploy, so it is a
// holding pen, not the list.
const STORE =
  process.env.WAITLIST_FILE ||
  path.join(process.cwd(), ".data", "waitlist.jsonl");

async function readRows() {
  const raw = await fs.readFile(STORE, "utf8").catch(() => "");
  return raw
    .split("\n")
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null; // a torn write must never take the endpoint down
      }
    })
    .filter(Boolean);
}

// Idempotent by email: asking twice is a person checking, not an error.
export async function saveWaitlistEmail(email, source) {
  const rows = await readRows();
  if (rows.some((r) => r.email === email)) return { created: false };
  await fs.mkdir(path.dirname(STORE), { recursive: true });
  await fs.appendFile(
    STORE,
    JSON.stringify({
      email,
      source,
      tier: "digest",
      status: "waitlist",
      joined_at: new Date().toISOString(),
    }) + "\n",
    "utf8"
  );
  return { created: true };
}
