"""The social card the site serves to a link preview.

    python3 -m pytest tests/test_social_card.py -q

Until 2026-11-02 the site served a `<title>`, a description and nothing else,
so every link to it rendered as a bare hostname in Slack, WhatsApp, Discord, X
and LinkedIn. `site/lib/social-card.js` is the declaration that fixes it and
`tests/social-card.test.mjs` executes it; this file runs that one, so a single
pytest command still covers the whole path, and adds the two readings that are
about where a value lives rather than about what it computes.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def code_only(source):
    """The file without its `//` comments.

    Both subjects explain themselves at length and both name the hostname in
    prose, which is the right place for it. The question below is about where a
    value a program reads is written down, so the prose has to come out first or
    the check answers about the explanation instead of the code. Neither file
    contains a block comment or a `//` inside a string literal, and the two
    assertions that follow would fail loudly rather than quietly if one ever did.
    """
    return re.sub(r"^\s*//.*$", "", source, flags=re.M)


CARD = code_only((ROOT / "site" / "lib" / "social-card.js").read_text())
LAYOUT = code_only((ROOT / "site" / "app" / "layout.jsx").read_text())
CARD_RAW = (ROOT / "site" / "lib" / "social-card.js").read_text()


def test_the_origin_is_read_and_not_retyped():
    """The hostname has one home, `lib/public-routes.js`, by that file's own rule."""
    assert "libraryofalexandria.dev" not in CARD
    assert "libraryofalexandria.dev" not in LAYOUT
    assert 'from "../lib/public-routes.js"' in LAYOUT


def test_the_card_declares_no_image_path_while_the_site_has_no_image():
    """A tag pointing at a 404 is worse than an absent tag: the crawler caches the break."""
    if (ROOT / "site" / "public").exists():
        pytest.skip("site/public exists now; the image decision is open again")
    assert "export const OG_IMAGE = null;" in CARD_RAW


def test_social_card_logic():
    """Runs tests/social-card.test.mjs, which executes the real module."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed; run `node --test tests/social-card.test.mjs`")
    proc = subprocess.run(
        [node, "--test", str(Path(__file__).parent / "social-card.test.mjs")],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
