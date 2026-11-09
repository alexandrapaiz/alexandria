"""The headroom reporter, tested against the arithmetic that was published wrong.

Incident 32's rule: a gate is tested against an artifact known to fail it before
the gate is trusted. There are two artifacts here and neither is synthetic.

The first is the mount shape on this host, which is what makes `df` and `du`
disagree by two thirds: `/tmp` is a bind of
`/dev/sda1[/tmp/systemd-private-<id>-epitod.service-<id>/tmp]`. That string is
replayed as a fixture rather than read live, because a test that asserts
against the live mount passes for the wrong reason on a box shaped differently
and fails for the wrong reason on a box shaped correctly.

The second is this seat's own relay row of 2026-11-02, which published
`/srv/asc` at 18G and `/tmp/epito-*` at 6.9G under the words "Composition
measured", against a device then at about 43G used. 18 + 6.9 = 24.9, so the
residual was 18G -- as large as the largest component named. `--compose` must
fail that composition, and the numbers from the row are fed in directly.

    python3 -m pytest tests/test_host_headroom.py -q
"""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("host_headroom", REPO / "tools" / "host_headroom.py")
hh = importlib.util.module_from_spec(spec)
sys.modules["host_headroom"] = hh
spec.loader.exec_module(hh)

GIB = 1073741824

# The live source string from `findmnt -n -o SOURCE --target /tmp` on this host,
# 2026-11-09. The bracket is the whole signal the tool reads.
BIND_SOURCE = (
    "/dev/sda1[/tmp/systemd-private-f872118bc3fe484ea895d87dcf8c1e40"
    "-epitod.service-AALRh1/tmp]"
)


# --- the mount shape, which is why the two numbers differ -------------------

def test_subtree_bind_is_detected_and_the_shadowed_source_is_named(monkeypatch, tmp_path):
    monkeypatch.setattr(hh, "_run", lambda cmd: BIND_SOURCE + "\n")
    shape = hh.mount_shape(str(tmp_path))
    assert shape["is_subtree_bind"] is True
    assert shape["source"] == "/dev/sda1"
    assert shape["subtree"].startswith("/tmp/systemd-private-")
    assert shape["basis"] == "findmnt"
    # The bind source is shadowed by the mount that came from it, so the path
    # does not resolve from inside the namespace. Reported, not assumed.
    assert shape["source_reachable"] is False


def test_a_device_root_mount_is_not_called_a_bind(monkeypatch, tmp_path):
    monkeypatch.setattr(hh, "_run", lambda cmd: "/dev/sda1\n")
    shape = hh.mount_shape(str(tmp_path))
    assert shape["is_subtree_bind"] is False
    assert shape["subtree"] is None
    # No bracket means nothing to resolve, so the field stays unanswered
    # rather than being filled in with a guess.
    assert shape["source_reachable"] is None


def test_without_findmnt_the_inode_is_the_second_witness(monkeypatch, tmp_path):
    """A box with no findmnt still gets an answer, labelled as the weaker one."""
    monkeypatch.setattr(hh, "_run", lambda cmd: None)
    shape = hh.mount_shape(str(tmp_path))
    # tmp_path is a directory inside a filesystem, so its inode is not 2.
    assert shape["is_subtree_bind"] is True
    assert shape["basis"] == "inode only; findmnt absent"
    assert shape["source"] is None


# --- the three numbers ------------------------------------------------------

def _stub_headroom(monkeypatch, used, visible, total=44 * GIB, partial=False):
    monkeypatch.setattr(hh, "device_used",
                        lambda path: ({"used": used, "avail": total - used,
                                       "total": total}, None))
    monkeypatch.setattr(hh, "visible_bytes",
                        lambda path: ({"bytes": visible, "partial": partial}, None))
    monkeypatch.setattr(hh, "mount_shape",
                        lambda path: {"source": "/dev/sda1", "subtree": "/tmp/x",
                                      "is_subtree_bind": True, "inode": 1846697,
                                      "source_reachable": False, "basis": "findmnt"})
    monkeypatch.setattr(hh, "deleted_open_bytes",
                        lambda: {"bytes": 768, "descriptors": 3,
                                 "pids_unreadable": 0, "floor": True})


def test_the_gap_is_the_subtraction_and_both_inputs_survive(monkeypatch):
    """The whole point: never one number. All three are in the report."""
    _stub_headroom(monkeypatch, used=43 * GIB, visible=14 * GIB)
    r = hh.headroom("/tmp")
    assert r["measured"] is True
    assert r["device_used_bytes"] == 43 * GIB
    assert r["visible_bytes"] == 14 * GIB
    assert r["gap_bytes"] == 29 * GIB
    assert r["gap_share_of_used"] == pytest.approx(0.674, abs=0.002)


def test_a_partial_walk_is_flagged_rather_than_reported_as_a_total(monkeypatch):
    _stub_headroom(monkeypatch, used=43 * GIB, visible=14 * GIB, partial=True)
    assert hh.headroom("/tmp")["visible_walk_partial"] is True


def test_an_unmeasurable_device_refuses_rather_than_reporting_fine(monkeypatch):
    monkeypatch.setattr(hh, "device_used", lambda path: (None, "statvfs(/nope): boom"))
    r = hh.headroom("/nope")
    assert r["measured"] is False
    assert "boom" in r["reason"]
    # The exit code must distinguish "cannot answer" from "nothing wrong".
    monkeypatch.setattr(sys, "argv", ["host_headroom.py", "--path", "/nope"])
    assert hh.main() == 2


# --- the composition rule, against this seat's own published claim ----------

def test_the_relay_rows_own_composition_fails(monkeypatch):
    """18G + 6.9G published as a measured composition of a 43G device."""
    _stub_headroom(monkeypatch, used=43 * GIB, visible=14 * GIB)
    sizes = {"/srv/asc": 18 * GIB, "/tmp/epito": int(6.9 * GIB)}
    monkeypatch.setattr(hh, "visible_bytes",
                        lambda path: ({"bytes": sizes.get(path, 14 * GIB),
                                       "partial": False}, None))
    r = hh.compose("/tmp", [("srv", "/srv/asc"), ("sandboxes", "/tmp/epito")])
    comp = r["composition"]
    assert comp["named_bytes"] == pytest.approx(24.9 * GIB, rel=0.01)
    assert comp["residual_bytes"] == pytest.approx(18.1 * GIB, rel=0.01)
    assert comp["covers_share_of_used"] == pytest.approx(0.579, abs=0.002)
    # The residual is as large as the largest thing named, which is the
    # condition that makes the word "composition" false.
    assert comp["residual_exceeds_largest"] is True


def test_a_composition_that_accounts_for_itself_passes(monkeypatch):
    _stub_headroom(monkeypatch, used=43 * GIB, visible=14 * GIB)
    sizes = {"/a": 30 * GIB, "/b": 11 * GIB}
    monkeypatch.setattr(hh, "visible_bytes",
                        lambda path: ({"bytes": sizes.get(path, 0), "partial": False}, None))
    comp = hh.compose("/tmp", [("a", "/a"), ("b", "/b")])["composition"]
    assert comp["residual_bytes"] == 2 * GIB
    assert comp["residual_exceeds_largest"] is False


def test_the_residual_rule_is_the_largest_component_and_not_a_percentage(monkeypatch):
    """A composition can cover most of a device and still be failed, correctly.

    Two components of 1 GiB each on a 43 GiB device cover 4.7 per cent and the
    residual dwarfs them; a single 22 GiB component covers 51 per cent and the
    residual is 21 GiB, just under it. The second is the honest one: the thing
    it does not name is smaller than the thing it does.
    """
    _stub_headroom(monkeypatch, used=43 * GIB, visible=14 * GIB)
    monkeypatch.setattr(hh, "visible_bytes",
                        lambda path: ({"bytes": 22 * GIB, "partial": False}, None))
    comp = hh.compose("/tmp", [("one", "/one")])["composition"]
    assert comp["residual_bytes"] == 21 * GIB
    assert comp["residual_exceeds_largest"] is False


def test_an_unreadable_component_does_not_silently_shrink_the_residual(monkeypatch):
    """A component that cannot be walked counts as zero and says so.

    Counting it as zero is the safe direction: it inflates the residual, which
    fails the claim, rather than deflating it into a pass.
    """
    _stub_headroom(monkeypatch, used=43 * GIB, visible=14 * GIB)

    def only_the_component_is_unreadable(path):
        # The /tmp walk still succeeds; it is the component that cannot be read.
        # Stubbing both would test the refusal path instead, which is covered
        # by test_an_unmeasurable_device_refuses_rather_than_reporting_fine.
        if path == "/tmp":
            return {"bytes": 14 * GIB, "partial": False}, None
        return None, "du: permission denied"

    monkeypatch.setattr(hh, "visible_bytes", only_the_component_is_unreadable)
    comp = hh.compose("/tmp", [("x", "/x")])["composition"]
    assert comp["components"][0]["bytes"] is None
    assert "permission denied" in comp["components"][0]["error"]
    assert comp["residual_bytes"] == 43 * GIB
    assert comp["residual_exceeds_largest"] is True


def test_compose_exits_one_on_an_unnamed_majority(monkeypatch, capsys):
    _stub_headroom(monkeypatch, used=43 * GIB, visible=14 * GIB)
    monkeypatch.setattr(hh, "visible_bytes",
                        lambda path: ({"bytes": 2 * GIB, "partial": False}, None))
    monkeypatch.setattr(sys, "argv",
                        ["host_headroom.py", "--compose", "srv=/srv/asc"])
    assert hh.main() == 1
    assert "RESIDUAL" in capsys.readouterr().out


def test_a_malformed_compose_spec_refuses(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["host_headroom.py", "--compose", "/srv/asc"])
    assert hh.main() == 2


# --- the report never attributes the gap to a seat --------------------------

def test_the_human_report_names_the_gap_as_off_namespace(monkeypatch, capsys):
    _stub_headroom(monkeypatch, used=43 * GIB, visible=14 * GIB)
    monkeypatch.setattr(sys, "argv", ["host_headroom.py"])
    assert hh.main() == 0
    out = capsys.readouterr().out
    assert "gap" in out
    assert "outside this mount namespace" in out
    assert "no seat-side reclaimer can reach it" in out
    # And it must carry the clock, because this volume swings 2 GiB in a minute.
    assert "taken" in out or "T" in out


def test_a_ruled_out_figure_does_not_print_as_zero_gib():
    """768 bytes beside a 29 GiB gap must read as ruled out, not as unmeasured."""
    assert hh._g(768) == "768 B"
    assert hh._g(500 * 1048576) == "500 MiB"
    assert hh._g(43 * GIB) == "43.0 GiB"


def test_self_check_lists_the_properties():
    lines = hh._self_check()
    assert any("never attributed to a seat" in line for line in lines)
    assert any("largest component" in line for line in lines)
    assert any("deletes" in line for line in lines)
