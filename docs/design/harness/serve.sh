#!/usr/bin/env bash
# Build and serve the site for a visual run, with the check three incidents
# have now prescribed and none has ever committed.
#
# INC-2026-09-23-phantom-production-bug, INC-2026-09-24-stale-server-kill-noop
# and INC-2026-10-07-stale-server-third-occurrence are all one failure: a
# `next build` run under a live `next start` leaves the old server answering
# with the previous build's asset hashes, so every chunk 400s and the page
# renders unstyled and unhydrated while curl still reports 200.
#
# Three properties this script holds that the prose fixes did not:
#   1. the server is identified by what it is, from ps, with an exact field
#      match that cannot match this script's own argv (`pkill -f next` does)
#   2. the start is verified by the process existing and the port answering,
#      not by a subshell's exit code, which is what hid EADDRINUSE
#   3. the stylesheet the server serves is compared to the one on disk, which
#      is the only check that actually proves the server is this build
set -euo pipefail
cd "$(dirname "$0")/../../../site"

echo "== stopping any server from a previous build =="
for pid in $(ps -eo pid=,args= | awk '$2=="next-server"{print $1}'); do
  echo "   killing next-server $pid"; kill "$pid" 2>/dev/null || true
done
for pid in $(ps -eo pid=,args= | awk '/next start/ && !/awk/{print $1}'); do
  kill "$pid" 2>/dev/null || true
done
sleep 2

echo "== build =="
npm run build

echo "== start =="
npx next start -p 3000 > /tmp/next-serve.log 2>&1 &
for _ in $(seq 1 40); do
  sleep 1
  curl -sf -o /dev/null http://127.0.0.1:3000/ && break
done

# EADDRINUSE goes to the log and the backgrounded command still looks fine, so
# the log is read rather than trusted.
if grep -q EADDRINUSE /tmp/next-serve.log; then
  echo "FAIL: the server did not bind; an older one is still on 3000." >&2
  exit 1
fi

echo "== proving the server is THIS build =="
served=$(curl -s http://127.0.0.1:3000/ | grep -o '/_next/static/css/[^"]*' | head -1)
if [ -z "$served" ]; then
  echo "FAIL: the served page references no stylesheet at all." >&2
  exit 1
fi
if [ ! -f ".next${served#/_next}" ]; then
  echo "FAIL: served $served is not on disk. The server is an older build." >&2
  exit 1
fi
echo "HASH MATCH: $served"
