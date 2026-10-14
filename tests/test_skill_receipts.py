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
import sys
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


def _excused_for_citing_nothing():
    """The slugs whose empty `provenance.claims` the provenance panel excuses.

    Read from the place that owns the judgment rather than re-derived here.
    `waiting_on_the_queue` in tools/panel_provenance.py decides whether a skill
    citing no claim ids is a draft waiting on a read the pipeline owes it or a
    skill that has quietly opted out of revision, and it is the gate that turns
    `main` red when it decides the second.

    Recomputing that judgment in this file with a looser rule is exactly how the
    two answers drift apart, which is the defect these assertions were failing
    on. The panel learned the draft excuse on 2026-10-05 and the page's own
    assertions did not, so `main` stayed red on a library the panel had already
    ruled clean. One law, one implementation, two callers.
    """
    sys.path.insert(0, str(REPO / "tools"))
    import panel_provenance as panel      # noqa: E402
    import skill_registrar as registrar   # noqa: E402

    rows, _problems = registrar.read_skills()
    excused = set()
    for row in rows:
        raw = (SKILLS / row.slug / "SKILL.md").read_text()
        if panel.waiting_on_the_queue(row, raw):
            excused.add(row.slug)
    return excused


def test_every_skill_the_page_receives_carries_its_provenance():
    """The acceptance criterion, executed against the real files."""
    skills = _list_skills()
    excused = _excused_for_citing_nothing()
    assert len(skills) >= 4, skills
    for s in skills:
        assert s["name"], s
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", s["extracted"]), s["name"]
        # Papers are required of everybody. A skill that names no source is
        # unreviewable whatever its status, and no excuse reaches this line.
        assert s["papers"], f"{s['name']}: no papers reached the page"
        if not s["claims"]:
            assert s["name"] in excused, (
                f"{s['name']}: no claim ids reached the page and the provenance "
                "panel does not excuse it. Either the skill cites claims it does "
                "not have, or it is published advice resting on nothing."
            )
            assert s["status"] == "draft", (
                f"{s['name']}: excused for citing nothing while published. The "
                "excuse is for drafts."
            )


def test_the_excuse_is_narrow_enough_to_still_be_a_gate():
    """A carve-out that excused the whole library would read as green forever.

    The assertion above is only worth having while most of the library is still
    held to it, so this is the one that fails if the excuse ever becomes the
    rule. It is also the test that notices when a draft finally gets its claim
    ids and the excuse should be retired rather than carried.
    """
    skills = _list_skills()
    citing = [s["name"] for s in skills if s["claims"]]
    assert len(citing) >= len(skills) - 1, (
        f"{len(skills) - len(citing)} of {len(skills)} skills cite no claim ids. "
        f"Citing: {citing}"
    )


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
    """The sprint item's named case: this skill's validation note reaches the page.

    This used to pin `199` in the claim list as its proof that ids arrive. That
    is a proxy, and on 2026-09-30 the proxy broke for a correct reason: ADR-38's
    quality bar cut three sections from this skill, and the skill's own
    `revisions:` entry records that claims 199, 136, 140, 190 and 243 left the
    provenance with the sections they supported. A test that pins one id forbids
    the revision the library's own law requires.

    So the proof is the law instead of the number. The ids the page shows are
    the ids the file lists, and the ids a revision retired are gone from both.
    """
    he = next(s for s in _list_skills() if s["name"] == "harness-engineering")
    assert "A/B trial" in he["validated"]

    sys.path.insert(0, str(REPO / "tools"))
    import skill_registrar as registrar   # noqa: E402

    raw = (SKILLS / "harness-engineering" / "SKILL.md").read_text()
    fm, _body = registrar.split_frontmatter(raw)
    listed = (registrar.parse_frontmatter(fm).get("provenance") or {}).get("claims") or []
    assert listed, "the file itself lists no claim ids, so the page has nothing to show"
    assert he["claims"] == [str(c).strip() for c in listed], (
        "the claim ids on the page are not the ids in the file"
    )

    retired = {"199", "136", "140", "190", "243"}
    assert not retired & set(he["claims"]), (
        "a claim id the 2026-09-30 revision retired is back on the page without "
        "the section that supported it"
    )


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


# ------------------------------------------- ADR-13's reviewer, in this step

def test_the_provenance_reviewer_passes_every_skill_the_library_publishes():
    """ADR-13's provenance reviewer, over the real library, inside a CI step.

    `tests/test_panel_provenance.py` holds the reviewer's 43 cases, and
    `checks.yml` names fourteen test files as individual steps, so a new file
    in `tests/` runs nowhere until a hand edits a workflow and no agent seat
    can push one (INC-2026-10-02-markdown-suite-claims-a-ci-step-it-never-had,
    and pending-workflow-changes item 17 is the structural fix). This step is
    the one whose paths already include `skills/**` and `db/schema.sql`, which
    are exactly the two files that can break a provenance review, so the suite
    runs here until that item is applied.

    What turns red, and when: a skill that cites a claim id twice, names no
    paper, cites a paper it lists twice, or marks its own judgment in words the
    library's vocabulary does not recognise, on the pull request that adds it.
    And a migration that renames a column the reviewer selects, because the
    suite resolves its SQL against db/schema.sql.
    """
    proc = subprocess.run(
        [sys.executable, "-m", "pytest",
         str(Path(__file__).parent / "test_panel_provenance.py"), "-q"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_the_page_and_the_reviewer_read_the_same_provenance():
    """Two readers of one block, held to the same answer.

    `site/lib/skill-provenance.js` feeds the page and `tools/skill_registrar.py`
    feeds the reviewer and the promotions row. They were written separately,
    they parse the same indented YAML subset, and the defect this whole file
    exists for was one of them reading a field as empty while the other read it
    fine. So the claim ids the page shows are compared against the claim ids
    the reviewer judges, skill by skill.
    """
    sys.path.insert(0, str(REPO / "tools"))
    import skill_registrar as reg

    rows = {row.name: row.claim_ids for row in reg.read_skills()[0]}
    for skill in _list_skills():
        ids = [int(c) for c in skill["claims"]]
        assert ids == rows[skill["name"]], skill["name"]
