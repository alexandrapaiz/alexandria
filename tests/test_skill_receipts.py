"""The skill library shows its receipts (sprint 2026-09-28, item 3).

    python3 -m pytest tests/ -q

The bug this closes had been open since 2026-09-18 and was reconfirmed twice:
`parseSkill` in site/lib/content.js read frontmatter with
`new RegExp("^" + key + ":", "m")`, and every provenance field in a SKILL.md is
indented two spaces under `provenance:`. So `validated`, `extracted` and the
claim ids parsed as the empty string on all four skills, and the page rendered
without them and without complaining. A field that silently reads as absent is
the worst kind, because the page still looks finished.

Three kinds of check, and they are different tools.

The parsing and the prose are executed for real in
tests/skill-provenance.test.mjs, which this file also runs, so one pytest
command covers the layer. That half needs no node_modules.

The wiring is executed too, end to end, by importing site/lib/content.js with
the site as the working directory and asserting on what `listSkills()` actually
returns. That is the sprint item's acceptance criterion, so it is run rather
than grepped.

The component is read as source. The thing most likely to undo this work is not
a flaw in the parser, it is a later edit that drops the receipts block or moves
it onto the resting row, which the owner's order of 2026-09-18 forbids. A grep
is the right instrument for that.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"
SKILLS = REPO / "skills"


def code_only(source):
    """The source with its comments removed.

    These files explain in prose what they refuse to do, so an assertion that
    greps the raw text finds the sentence rather than the code.
    """
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    return re.sub(r"^\s*//.*$", "", source, flags=re.M)


CORE = code_only((SITE / "lib" / "skill-provenance.js").read_text())
CONTENT = code_only((SITE / "lib" / "content.js").read_text())
ROW = code_only((SITE / "app" / "components" / "SkillLibrary.jsx").read_text())
CSS = (SITE / "app" / "globals.css").read_text()


def node():
    exe = shutil.which("node")
    if exe is None:
        pytest.skip("node is not installed")
    return exe


# ----------------------------------------------------------------- the module

def test_the_pure_core_stays_import_free():
    """tests/skill-provenance.test.mjs loads it by evaluating its source, which
    only works while it has no imports to resolve."""
    assert not re.search(r"^\s*import\s", CORE, re.M)


def test_the_core_touches_no_filesystem_and_hashes_nothing():
    """Everything here is a function of its argument. Reading a directory or
    hashing a file is the wiring's job and belongs in content.js."""
    for forbidden in ("readFileSync", "readdirSync", "createHash", "process."):
        assert forbidden not in CORE, forbidden


def test_the_key_regex_that_could_not_see_an_indented_field_is_gone():
    """The exact expression that caused this, so nobody reintroduces it as a
    convenience: a key anchored at column 0 against a two-level document."""
    assert 'new RegExp(`^${key}' not in CONTENT
    assert 'new RegExp("^" + key' not in CONTENT
    assert "readProvenance(" in CONTENT


def test_content_reads_provenance_through_the_one_reader():
    assert re.search(r'import \{[^}]*readProvenance[^}]*\} from "\./skill-provenance\.js"', CONTENT)
    assert re.search(r'import \{[^}]*latestValidation[^}]*\} from "\./skill-provenance\.js"', CONTENT)


def test_the_sha_matches_the_one_the_trigger_test_records():
    """A receipt is pinned to a sha, so the page and the instrument have to
    agree on what a sha is or `current` is meaningless."""
    instrument = (SKILLS / "_validation" / "trigger_test.py").read_text()
    assert 'hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]' in instrument
    assert 'createHash("sha256").update(raw, "utf8").digest("hex").slice(0, 16)' in CONTENT


# -------------------------------------------------------------- the component

def test_the_receipts_render_inside_the_disclosure_and_not_on_the_resting_row():
    """The owner's order of 2026-09-18: a row at rest is one line, and nothing
    a row used to say at rest stays there. The receipts live in the panel."""
    assert "<SkillReceipts skill={s} />" in ROW
    summary = ROW[ROW.index("<summary className=\"skill-line\">") : ROW.index("</summary>")]
    for field in ("validation", "claims", "extracted", "validated"):
        assert field not in summary, f"{field} was put back on the resting line"


def test_the_component_renders_every_field_the_sprint_item_names():
    panel = ROW[ROW.index("function SkillReceipts(") : ROW.index("function SkillRow(")]
    assert "s.claims.join" in panel, "claim ids are counted but not rendered"
    assert "s.extracted" in panel
    assert "s.validated" in panel
    assert "receiptSentences(s.validation)" in panel


def test_the_stale_receipt_is_marked_without_breaking_the_colour_law():
    """--contra is reserved by the :root comment for `contradicts` edges and
    their legend swatch, on the owner's dispatch of 2026-09-25, and it says in
    its own words that it enters nothing else."""
    block = CSS[CSS.index(".skill-receipts {") : CSS.index(".lib-offer {")]
    assert "--contra" not in code_only(block), "the receipts block spends the one reserved colour"
    assert ".skill-receipts dd.is-stale {" in block
    assert "is-stale" in ROW


# ------------------------------------------------------------- executed checks

def test_the_core_logic_and_the_real_library():
    """Runs tests/skill-provenance.test.mjs, which executes the real module
    against the four real SKILL.md files and the real result bundles."""
    proc = subprocess.run(
        [node(), "--test", str(Path(__file__).parent / "skill-provenance.test.mjs")],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def _list_skills():
    """What the page actually receives. content.js resolves its paths off
    process.cwd(), which Next.js sets to site/, so the check has to as well."""
    script = (
        'const m = await import("./lib/content.js");'
        "process.stdout.write(JSON.stringify(m.listSkills()"
        '.map(({ body, ...s }) => s)));'
    )
    proc = subprocess.run(
        [node(), "--input-type=module", "-e", script],
        cwd=SITE,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.loads(proc.stdout)


def test_every_skill_the_page_receives_carries_its_provenance():
    """The acceptance criterion, executed against the real files."""
    skills = _list_skills()
    assert len(skills) >= 4, skills
    for s in skills:
        assert s["name"], s
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", s["extracted"]), s["name"]
        assert s["claims"], f"{s['name']}: no claim ids reached the page"
        assert s["papers"], f"{s['name']}: no papers reached the page"


def test_every_skill_the_page_receives_shows_a_dated_validation_result():
    for s in _list_skills():
        v = s["validation"]
        assert v, f"{s['name']}: no validation result reached the page"
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", v["date"]), s["name"]
        assert v["engine"], s["name"]
        assert v["total"] > 0, s["name"]
        assert v["current"] is True, (
            f"{s['name']}: the receipt was measured against a different revision "
            "of SKILL.md, so the page will say so. Re-run "
            "skills/_validation/trigger_test.py."
        )


def test_harness_engineering_shows_the_note_the_sprint_item_names():
    he = next(s for s in _list_skills() if s["name"] == "harness-engineering")
    assert "A/B trial" in he["validated"]
    assert "199" in he["claims"]


def test_a_corrupt_result_bundle_does_not_take_the_catalogue_down():
    """One unreadable receipt must not blank the page. A skill with no readable
    receipt already renders as unmeasured, which is the honest outcome."""
    assert "JSON.parse" in CONTENT
    guard = CONTENT[CONTENT.index("export function listValidations()") :]
    assert "try {" in guard and "catch" in guard


# ------------------------------------------------------- the registers it binds

def test_the_claim_ids_ship_with_the_sentence_that_decodes_them():
    """docs/voice/ban-list.md entry 14 names claim ids as internal vocabulary
    printed at the reader, and governs site copy since the owner's ruling of
    2026-09-19. Its amended test is whether someone who has never seen the
    codebase could say what the number refers to. The sprint item asks for the
    ids on the page, so the ids carry their own decoder."""
    panel = ROW[ROW.index("function SkillReceipts(") : ROW.index("function SkillRow(")]
    assert "skill-claims-note" in panel, "the claim ids render with nothing to decode them"
    assert "claim graph" in panel
    assert 'href="/graph"' in panel, "the sentence has to resolve somewhere a reader can go"


def test_the_receipts_copy_is_plain_ascii():
    """Ban list entry 13, amended 2026-09-21 by incident 27: the entry is the
    class, which is every character outside plain ASCII, and not only the three
    it names. A curly apostrophe or an en dash in this block would be the same
    defect the writer seat found in 2026-W37."""
    panel = ROW[ROW.index("function SkillReceipts(") : ROW.index("function SkillRow(")]
    offenders = sorted({c for c in panel if ord(c) > 127})
    assert offenders == [], offenders
    sentences = code_only(CORE)
    offenders = sorted({c for c in sentences if ord(c) > 127})
    assert offenders == [], offenders


def test_no_heading_in_the_receipts_carries_an_explanatory_subtitle():
    """L-E1 in docs/standards/lessons.md, the owner's law that predates the
    company: bare nouns in her interfaces, units in note slots."""
    panel = ROW[ROW.index("function SkillReceipts(") : ROW.index("function SkillRow(")]
    heads = re.findall(r'className="skill-detail-head">([^<]*)<', panel)
    assert heads == ["The receipts"], heads
    for head in heads:
        assert ":" not in head and "(" not in head, head
