"""Does the kill-vocabulary check tell a retired code from a live one.

Run with `python3 -m pytest tests/test_kill_vocabulary.py -q`.

`tools/kill_vocabulary.py` reads the host's audit log and the board, neither of
which exists on a pull request checkout, so every test here builds its own
audit log in the host's exact format and substitutes the board reader. Nothing
touches `/srv/asc/state` or the network.

The property worth asserting is the one the tool was written for. On
2026-11-09 two seats tallied the audit log's `exit` field over its whole
history, got the union of two encodings — the GitHub Actions runner's signal
arithmetic before 2026-10-18, the host's words after it — and reached opposite
wrong conclusions, because the union of two encodings is a well-formed
vocabulary and nothing in the field says a value has been retired. So the
tests below check that the tally is split at the boundary, and that the
standards are read against the surfaces in **both** directions: a surface
writing a value no standard names, and a standard naming a value no surface
writes. The second direction is the silent one, and it is the one that had
never been checked.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import kill_vocabulary as kv


def audit_log(tmp_path, rows):
    path = tmp_path / "audit.jsonl"
    with path.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    return str(path)


def run_end(ts, exit_value, ms=1000):
    return {"action": "run.end", "agent": "alexandria-exo", "ts": ts,
            "exit": exit_value, "durationMs": ms}


ACTIONS_ERA = "2026-10-05T03:00:00.000Z"
HOST_ERA = "2026-11-09T03:00:00.000Z"


def test_the_boundary_splits_the_tally_rather_than_summing_across_it(tmp_path):
    path = audit_log(tmp_path, [
        run_end(ACTIONS_ERA, 143, ms=851_000),
        run_end(HOST_ERA, "timeout", ms=3_612_000),
    ])
    reading, why = kv.read_audit(path)
    assert why is None
    assert reading["rows"] == 2
    # The whole point: 143 is in one era and timeout in the other, and neither
    # era's counter knows about the other's value.
    assert dict(reading["vocab"]["actions"]) == {"143": 1}
    assert dict(reading["vocab"]["host"]) == {"timeout": 1}


def test_durations_are_kept_per_era_not_per_value(tmp_path):
    """A value that spans the boundary must not report one merged span: the
    spans are the evidence that two eras are two different events."""
    path = audit_log(tmp_path, [
        run_end(ACTIONS_ERA, 1, ms=900_000),
        run_end(HOST_ERA, 1, ms=9_000),
    ])
    reading, _ = kv.read_audit(path)
    assert reading["durations"][("actions", "1")] == [900.0]
    assert reading["durations"][("host", "1")] == [9.0]


def test_a_malformed_line_is_skipped_and_the_rest_of_the_file_is_still_read(tmp_path):
    path = tmp_path / "audit.jsonl"
    path.write_text(
        json.dumps(run_end(HOST_ERA, "timeout")) + "\nnot json at all\n"
        + json.dumps(run_end(HOST_ERA, "clone")) + "\n"
    )
    reading, why = kv.read_audit(str(path))
    assert why is None and reading["rows"] == 2


def test_rows_without_an_exit_field_are_not_counted(tmp_path):
    path = audit_log(tmp_path, [
        {"action": "run.end", "agent": "a", "ts": HOST_ERA},
        {"action": "cron", "agent": "a", "ts": HOST_ERA, "exit": 0},
        run_end(HOST_ERA, 0),
    ])
    reading, _ = kv.read_audit(path)
    assert reading["rows"] == 1


def test_a_missing_audit_log_is_a_reason_and_never_an_empty_vocabulary(tmp_path):
    reading, why = kv.read_audit(str(tmp_path / "nothing-here.jsonl"))
    assert reading is None
    assert "not on this filesystem" in why


def surfaces(monkeypatch, audit_rows, board_vocab, standards=None):
    """Point the tool at a built audit log and a substituted board."""
    def fake_board():
        vocab = {era: __import__("collections").Counter(values)
                 for era, values in board_vocab.items()}
        return {"rows": sum(sum(c.values()) for c in vocab.values()), "vocab": vocab,
                "durations": {}, "saturated": [], "errors": [], "window_days": 90}, None
    monkeypatch.setattr(kv, "read_audit", lambda path=None: (audit_rows, None))
    monkeypatch.setattr(kv, "read_board", fake_board)
    monkeypatch.setattr(kv, "named_in_standards",
                        lambda root=".": standards if standards is not None
                        else {"124": "docs/standards/pm.md"})


def reading_of(audit_vocab):
    import collections
    return {"rows": sum(sum(v.values()) for v in audit_vocab.values()),
            "vocab": {era: collections.Counter(values) for era, values in audit_vocab.items()},
            "durations": {}}


def test_a_live_kill_no_standard_names_is_a_finding(monkeypatch, capsys):
    surfaces(monkeypatch, reading_of({"host": {"timeout": 61, "0": 10}}), {"host": {"124": 27}})
    assert kv.main([]) == 1
    out = capsys.readouterr().out
    assert "writes 'timeout' on the live runtime (61 rows) and no standard names it" in out


def test_a_standard_naming_a_code_nothing_emits_is_a_finding(monkeypatch, capsys):
    """The silent direction. A wake that never fires reads as a quiet fleet."""
    surfaces(monkeypatch, reading_of({"host": {"0": 10}}), {"host": {"0": 10}},
             standards={"137": "docs/standards/pm.md"})
    assert kv.main([]) == 1
    assert "names exit 137 and no surface has written it ever" in capsys.readouterr().out


def test_a_code_retired_at_the_boundary_says_retired_rather_than_never(monkeypatch, capsys):
    surfaces(monkeypatch, reading_of({"actions": {"143": 28}, "host": {"0": 5}}),
             {"host": {"0": 5}}, standards={"143": "docs/standards/pm.md"})
    assert kv.main([]) == 1
    out = capsys.readouterr().out
    assert "no surface has written it since %s" % kv.RUNTIME_BOUNDARY in out
    assert "written it ever" not in out


def test_a_clean_pair_of_surfaces_is_exit_zero(monkeypatch, capsys):
    surfaces(monkeypatch, reading_of({"host": {"0": 10, "1": 3}}), {"host": {"124": 2}})
    assert kv.main([]) == 0
    assert "No findings" in capsys.readouterr().out


def test_an_unreadable_surface_is_exit_two_and_never_a_clean_zero(monkeypatch, capsys):
    """The 2026-10-11 rule: a check that cannot see must not report an
    all-clear. An unreadable surface proves nothing about that surface."""
    monkeypatch.setattr(kv, "read_audit", lambda path=None: (None, "no audit log here"))
    monkeypatch.setattr(kv, "read_board", lambda: (
        {"rows": 0, "vocab": {}, "durations": {}, "saturated": [], "errors": [],
         "window_days": 90}, None))
    monkeypatch.setattr(kv, "named_in_standards", lambda root=".": {})
    assert kv.main([]) == 2
    out = capsys.readouterr().out
    assert "UNREADABLE" in out and "this run proves nothing about them" in out


def test_the_json_form_carries_the_boundary_and_the_findings(monkeypatch, capsys):
    surfaces(monkeypatch, reading_of({"host": {"clone": 17}}), {"host": {"124": 1}})
    assert kv.main(["--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["boundary"] == kv.RUNTIME_BOUNDARY
    assert any("clone" in finding for finding in payload["findings"])
    assert payload["audit"]["vocab"]["host"] == {"clone": 17}


def test_saturation_is_reported_because_an_absence_through_a_window_is_not_proven(monkeypatch, capsys):
    import collections

    def fake_board():
        return {"rows": 200, "vocab": {"host": collections.Counter({"0": 200})},
                "durations": {}, "saturated": ["alexandria/pm"], "errors": [],
                "window_days": 90}, None
    monkeypatch.setattr(kv, "read_audit", lambda path=None: (reading_of({"host": {"0": 1}}), None))
    monkeypatch.setattr(kv, "read_board", fake_board)
    monkeypatch.setattr(kv, "named_in_standards", lambda root=".": {})
    kv.main([])
    assert "an absence here is not proven" in capsys.readouterr().out


def test_the_standards_are_read_off_the_file_rather_than_trusted_to_the_table(tmp_path):
    """The check must not outlive its own premise the way its subject did."""
    standards = tmp_path / "docs" / "standards"
    standards.mkdir(parents=True)
    (standards / "pm.md").write_text(
        "The bus wakes HQ's engineer on machinery: a run killed in any company "
        "(exit 111, 222, and 333), and every pull request opened on HQ.\n"
    )
    found = kv.named_in_standards(str(tmp_path))
    assert set(found) == {"111", "222", "333"}
