"""Rendering a digest body cannot put HTML on the page (the 2026-09-19 finding).

    python3 -m pytest tests/ -q

The bug this closes: `site/app/library/[week]/page.jsx` passed an issue body
through `marked.parse` into `dangerouslySetInnerHTML`, and `marked` has not
sanitized HTML since v8. The body is written by gpt-oss-120b from arXiv text,
and anyone can put text on arXiv, so the chain from a crafted passage in a
paper to live HTML on alexandr.ia had no human in it.

Three kinds of check live here, and they are different tools.

The decision logic is executed for real in tests/markdown.test.mjs, which this
file also runs so one pytest command covers the whole layer. It needs no
node_modules, which is why it is the half that runs in CI.

The wiring is read as source. Executing it needs `marked` installed, and the
thing most likely to reintroduce the bug is not a flaw in the escaping, it is
a fourth surface added later that renders a body the direct way. A grep is the
right instrument for that and it runs everywhere.

The real parser against a corpus of attacks is tools/check_markdown_render.mjs,
run here when marked happens to be installed and skipped when it is not.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def code_only(source):
    """The source with its comments removed.

    Both of these files explain in prose what they refuse to do, so an
    assertion that greps the raw text finds the sentence saying `marked.use()`
    is never called and fails on the sentence. What is being asserted is a
    property of the code, so strip the commentary first.
    """
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    return re.sub(r"^\s*//.*$", "", source, flags=re.M)


CORE = code_only((REPO / "site" / "lib" / "markdown-core.js").read_text())
WRAPPER = code_only((REPO / "site" / "lib" / "markdown.js").read_text())

# Every sink on the site, and why each one is allowed to be one. A new
# dangerouslySetInnerHTML anywhere fails this until someone decides about it,
# which is the point: the gap was one unreviewed sink.
KNOWN_SINKS = {
    "site/app/library/[week]/page.jsx",   # the issue body, via renderMarkdown
    "site/app/desk/page.jsx",             # the sprint file, via renderMarkdown
    "site/app/components/SkillLibrary.jsx",  # html already rendered in skills/page.jsx
    "site/app/layout.jsx",                # a hardcoded HTML comment, no input
}


def jsx_files():
    return sorted(
        p for p in (REPO / "site").rglob("*.jsx") if "node_modules" not in p.parts
    )


def rel(path):
    return path.relative_to(REPO).as_posix()


# ------------------------------------------------------------------ the wiring

def test_no_surface_parses_markdown_on_its_own():
    """The whole fix is that there is one place markdown becomes HTML. A route
    that imports marked directly bypasses the escaping and the tripwire both."""
    importers = [
        rel(p)
        for p in (REPO / "site").rglob("*.js*")
        if "node_modules" not in p.parts and re.search(r'from\s+"marked"', code_only(p.read_text()))
    ]
    assert importers == ["site/lib/markdown.js"], importers


def test_no_surface_calls_marked_parse():
    offenders = [
        rel(p)
        for p in (REPO / "site").rglob("*.js*")
        if "node_modules" not in p.parts and "marked.parse" in code_only(p.read_text())
    ]
    assert offenders == [], offenders


def test_every_sink_is_a_known_sink():
    sinks = {rel(p) for p in jsx_files() if "dangerouslySetInnerHTML" in code_only(p.read_text())}
    assert sinks == KNOWN_SINKS, f"unreviewed sink: {sinks ^ KNOWN_SINKS}"


def test_the_three_body_surfaces_render_through_the_hardened_path():
    for path in (
        "site/app/library/[week]/page.jsx",
        "site/app/desk/page.jsx",
        "site/app/skills/page.jsx",
    ):
        source = code_only((REPO / path).read_text())
        assert "renderMarkdown(" in source, path
        assert re.search(r'import \{ renderMarkdown \} from ".*markdown\.js"', source), path


def test_the_hardening_cannot_be_switched_off_by_another_import():
    """marked.use() mutates the library's shared singleton, so any other
    importer could turn the renderer off. A private instance cannot be."""
    assert "new Marked(" in WRAPPER
    assert "marked.use(" not in WRAPPER
    assert "hardenedRenderer()" in WRAPPER


def test_the_render_path_fails_closed():
    """The tripwire is worth nothing if its answer is ignored."""
    assert "unsafeHtmlReason(" in WRAPPER
    assert "escapedFallback(" in WRAPPER
    guard = WRAPPER[WRAPPER.index("const reason = unsafeHtmlReason(") :]
    assert "if (reason)" in guard
    assert "return escapedFallback(source)" in guard


def test_the_pure_core_stays_import_free():
    """tests/markdown.test.mjs loads it by evaluating its source, which only
    works while it has no imports to resolve."""
    assert not re.search(r"^\s*import\s", CORE, re.M)


def test_the_core_holds_no_parser_of_its_own():
    """Everything here is a function of its argument. A core that reached for
    marked would be the wiring, and could not be tested without it."""
    assert "new Marked" not in CORE
    assert "require(" not in CORE


def test_data_urls_are_not_a_safe_scheme():
    """A data: URL is a document the browser will run, and no issue needs one.
    This is asserted in the source as well as in the executed test because it
    is the one entry someone would add back for a convenience."""
    schemes = re.search(r"SAFE_SCHEMES = \[(.*?)\]", CORE, re.S).group(1)
    assert '"data"' not in schemes
    for scheme in ('"http"', '"https"', '"mailto"'):
        assert scheme in schemes


# ------------------------------------------------------------- executed checks

def test_markdown_core_logic():
    """Runs tests/markdown.test.mjs, which executes the real module."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed; run `node --test tests/markdown.test.mjs`")
    proc = subprocess.run(
        [node, "--test", str(Path(__file__).parent / "markdown.test.mjs")],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_the_real_parser_against_the_attack_corpus():
    """The integration half. Needs marked, so it skips where node_modules is
    absent rather than pretending the corpus ran."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    if not (REPO / "site" / "node_modules" / "marked" / "package.json").exists():
        pytest.skip("marked is not installed; run `cd site && npm install`")
    proc = subprocess.run(
        [node, str(REPO / "tools" / "check_markdown_render.mjs")],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
