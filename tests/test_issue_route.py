"""The archive publishes the record, and a missing database cannot unpublish it.

    python3 tests/test_issue_route.py     # or under pytest

The press writes a row to `digests` when it mails an issue. The public archive
read markdown files committed by hand, and nothing connected the two: four
commits under `site/content/issues/`, every one of them a person noticing.
`site/lib/issues-live.js` closes that, and this command holds the three
properties that decide whether closing it was safe.

The shaping and the queries are executed for real in tests/issues.test.mjs,
which this file also runs so that one pytest command covers the whole path. No
database, no node_modules, no build.

What is read as source here is the part a unit test cannot reach: which
function each route calls, and the rendering mode the route declares. The mode
is the load-bearing one. The week route used to carry `dynamicParams = false`
with a comment explaining that an unpublished address would otherwise go
through on-demand static generation and answer 500 instead of 404, because the
404 it rendered read headers through the root layout's ClerkProvider. That
guard is incompatible with an archive whose weeks arrive after the build, so it
is gone and the route is dynamic from the start instead.

That substitution was measured rather than argued, on this branch, against a
real production build of the site:

    cd site && npm install && npx next build
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=... npx next start -p 3112
    for p in / /library /library/2026-W39 /library/2026-W37 \
             /library/2026-W01 /library/nonsense; do
      curl -s -o /dev/null -w "%{http_code} $p\n" localhost:3112$p; done

    200 /                     200 /library           200 /library/2026-W39
    404 /library/2026-W37     404 /library/2026-W01  404 /library/nonsense

A clean 404 on an unpublished week, a retired week still retired, and the
listing publishing exactly what it publishes in production today. The build is
not run from here because CI installs no node_modules, so the assertions below
hold the reason the result is what it is.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

CORE = (REPO / "site" / "lib" / "issues-core.js").read_text()
LIVE = (REPO / "site" / "lib" / "issues-live.js").read_text()
CONTENT = (REPO / "site" / "lib" / "content.js").read_text()
LISTING = (REPO / "site" / "app" / "library" / "page.jsx").read_text()
WEEK = (REPO / "site" / "app" / "library" / "[week]" / "page.jsx").read_text()

FAILURES: list[str] = []


def check(label: str, ok: bool) -> None:
    print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    if not ok:
        FAILURES.append(label)


def section(name: str) -> None:
    print(f"\n{name}")


def test_both_routes_read_the_record():
    section("both library routes read the record")
    check("the listing calls publishedIssues", "publishedIssues()" in LISTING)
    check("the listing no longer reads the filesystem directly",
          "listIssues" not in LISTING)
    check("the week route calls publishedIssue", "publishedIssue(week)" in WEEK)
    check("the week route no longer reads the filesystem directly",
          "getIssue" not in WEEK)


def test_the_rendering_mode_is_the_one_the_404_needs():
    section("the rendering mode, which is why the old guard could go")
    for name, src in (("listing", LISTING), ("week route", WEEK)):
        check(f"{name}: force-dynamic",
              re.search(r'dynamic\s*=\s*"force-dynamic"', src) is not None)
    check("the week route does not fix its weeks at build time",
          "generateStaticParams" not in WEEK)
    # The word survives in the comment that explains why the guard went. What
    # must be gone is the export, because `dynamicParams = false` would 404
    # every week that arrived after the last build.
    check("and does not carry the guard that would 404 a published week",
          re.search(r"^export const dynamicParams", WEEK, re.M) is None)
    check("an unresolvable week still becomes a 404 and not a blank issue",
          "notFound()" in WEEK)


def test_it_fails_closed():
    section("a database that cannot be read publishes what the files publish")
    check("no DATABASE_URL yields no connection rather than an empty archive",
          re.search(r"return url \? neon\(url\) : null", LIVE) is not None)
    check("readListing returns null on a throw",
          re.search(r"} catch {\s*return null;\s*}", CORE) is not None)
    check("the merge treats null rows as 'did not look'",
          "rows ?? []" in CORE)
    check("the live reader is the only half that imports Neon",
          "@neondatabase/serverless" in LIVE
          and re.search(r"^import", CORE, re.M) is None)


def test_one_copy_of_every_rule():
    section("one copy of every rule the pages depend on")
    check("the record's bodies are parsed by content.js's own parseIssue",
          "export function parseIssue" in CONTENT
          and "parseIssue" in LIVE
          and "parse: parseIssue" in LIVE)
    check("HIDDEN_WEEKS is content.js's set and not a second one",
          "hidden: HIDDEN_WEEKS" in LIVE and "HIDDEN_WEEKS = new Set" in CONTENT)
    # The core names 2026-W37 in a comment, because that week is the reason
    # HIDDEN_WEEKS exists. What it must not hold is the set: a second list of
    # retired weeks is a second place the owner's veto can be forgotten.
    check("the core holds no hidden-week set of its own",
          "new Set" not in CORE and "hidden," in CORE)


def test_the_listing_read_is_bounded():
    section("what the host meters (L-E9)")
    check("the listing read is collapsed into a window",
          "memo(readListing)" in LIVE)
    check("the week read is not, because it is keyed by the URL's week",
          "memo(readWeek)" not in LIVE)
    check("the window is a constant and not a magic number at the call site",
          re.search(r"ttlMs = 60_000", CORE) is not None)


def test_the_public_listing_cannot_serve_an_issue_body():
    section("the listing's shape")
    # The listing query reads only the head of each body, so a body that
    # reached the page from there would be a truncated issue presented as a
    # whole one. The shape is asserted by execution in tests/issues.test.mjs;
    # what is held here is that the query is the reason.
    check("the listing query reads a prefix of the body",
          re.search(r"left\(body, \$\{LISTING_HEAD\}\)", CORE) is not None)
    check("the merge builds the listing field by field",
          re.search(r"\.map\(\(\{ week, title, dates, excerpt, source \}\)", CORE)
          is not None)


def test_the_javascript_suite_runs():
    section("site/lib/issues-core.js, executed (tests/issues.test.mjs)")
    node = shutil.which("node")
    if not node:
        check("node is available to run the shaping tests", False)
        return
    proc = subprocess.run(
        [node, "--test", str(REPO / "tests" / "issues.test.mjs")],
        capture_output=True, text=True,
    )
    for line in proc.stdout.splitlines():
        if line.startswith(("ok ", "not ok ", "# pass", "# fail")):
            print(f"  {line}")
    check("every shaping test passes", proc.returncode == 0)
    if proc.returncode != 0:
        print(proc.stdout[-3000:])
        print(proc.stderr[-2000:])


def main() -> int:
    for fn in (
        test_both_routes_read_the_record,
        test_the_rendering_mode_is_the_one_the_404_needs,
        test_it_fails_closed,
        test_one_copy_of_every_rule,
        test_the_listing_read_is_bounded,
        test_the_public_listing_cannot_serve_an_issue_body,
        test_the_javascript_suite_runs,
    ):
        fn()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} failure(s)")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("the archive reads the record, and fails closed to the files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
