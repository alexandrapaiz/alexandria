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

# The port is read from the environment, because 3000 is not ours to assume.
# On 2026-10-17 the agent container had an unrelated service listening on it,
# and this script's own stale-server check reported "an older one is still on
# 3000", which is a true sentence about the port and the wrong diagnosis: the
# listener was never a next-server of ours and killing it was not an option.
# Every script in this directory reads the same variable, so one export moves
# the whole harness.
PORT_FE="${FE_PORT:-3000}"
BASE_FE="http://127.0.0.1:${PORT_FE}"
echo "== port ${PORT_FE} =="

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
npx next start -p "$PORT_FE" > /tmp/next-serve.log 2>&1 &
STARTED=$!
for _ in $(seq 1 40); do
  sleep 1
  curl -sf -o /dev/null "$BASE_FE/" && break
done

# EADDRINUSE goes to the log and the backgrounded command still looks fine, so
# the log is read rather than trusted.
if grep -q EADDRINUSE /tmp/next-serve.log; then
  echo "FAIL: the server did not bind. Something is already on ${PORT_FE}." >&2
  echo "      If it is not one of ours, do not kill it: re-run with" >&2
  echo "      FE_PORT=<free port> instead, and export the same FE_PORT to" >&2
  echo "      every script in this directory." >&2
  exit 1
fi

# Added 2026-10-15, after the fourth occurrence
# (INC-2026-10-15-stale-server-survives-restart-fourth-occurrence). Property 3
# below compares the served stylesheet to the one on disk, which proves the
# server is this BUILD. It cannot prove the server is this PROCESS, and those
# came apart today: a stale server from the same build, started with a
# different environment, serves a byte-identical stylesheet and passes every
# check in this file. It answered 200 on every route while rendering an empty
# state, because the fixture variable this run started it with belonged to a
# process that had already died on EADDRINUSE.
#
# `next start` forks a worker, so the listener is the PID started above or a
# descendant of it. Anything else holding the port is a process this script did
# not start, which is the stale server by definition.
# This uses ps and nothing else on purpose. The first draft of this check
# asked `ss` for the pid holding the port, which is the direct question, and
# `ss` is not installed in the agent container, so the check skipped itself in
# silence. A guard that quietly does nothing in the one environment it was
# written for is worse than no guard, because the run reads its output and
# believes it passed.
#
# So the question is asked a different way, with a tool that is always there:
# every `next-server` alive after a successful start must descend from the
# process this script started. A survivor is one that does not.
#
# Narrowed 2026-10-17. The check above asked the question of EVERY next-server
# on the machine, which assumes every Next app on the box is ours. The agent
# container is shared, and on 2026-10-17 it ran an unrelated Next service that
# this check reported as our stale server, with a pid no run of this seat could
# have started and must not kill. So the set is cut to the servers serving THIS
# site: a process's `/proc/<pid>/cwd` is where it was started, `next start`
# runs in `site/`, and /proc is present wherever this script can run at all. A
# next-server whose cwd is some other tree is somebody else's and is none of
# this harness's business.
SITE_DIR="$(pwd -P)"
strays=
for srv in $(ps -eo pid=,args= | awk '$2=="next-server"{print $1}'); do
  cwd=$(readlink -f "/proc/$srv/cwd" 2>/dev/null || true)
  [ "$cwd" = "$SITE_DIR" ] || continue
  owner="$srv"
  while [ -n "$owner" ] && [ "$owner" != "1" ] && [ "$owner" != "$STARTED" ]; do
    owner=$(ps -o ppid= -p "$owner" 2>/dev/null | tr -d ' ' || true)
  done
  [ "$owner" = "$STARTED" ] || strays="$strays $srv"
done
if [ -n "$strays" ]; then
  echo "FAIL: next-server($strays) is serving $SITE_DIR, is alive, and did" >&2
  echo "      not come from this script's pid $STARTED. That is a stale" >&2
  echo "      server, and it may be the one answering on ${PORT_FE}." >&2
  exit 1
fi
echo "PID MATCH: every next-server in $SITE_DIR descends from $STARTED"

echo "== proving the server is THIS build =="
served=$(curl -s "$BASE_FE/" | grep -o '/_next/static/css/[^"]*' | head -1)
if [ -z "$served" ]; then
  echo "FAIL: the served page references no stylesheet at all." >&2
  exit 1
fi
if [ ! -f ".next${served#/_next}" ]; then
  echo "FAIL: served $served is not on disk. The server is an older build." >&2
  exit 1
fi
echo "HASH MATCH: $served"
