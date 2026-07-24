"""Tests for the rolling history-file accumulation in the dashboard aggregator."""

import csv
import datetime

from repo_health_dashboard.utils.utils import update_history_csv


def _write_csv(path, fieldnames, rows):
    """Write rows (list of dicts) to a CSV with the given header."""
    with open(path, "w", newline="", encoding="utf8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _read_csv(path):
    with open(path, newline="", encoding="utf8") as handle:
        return list(csv.DictReader(handle))


def test_history_appends_new_snapshot(tmp_path):
    main = tmp_path / "dashboard_main.csv"
    history = tmp_path / "dashboard_history.csv"

    fields = ["repo_name", "TIMESTAMP", "github_actions"]
    _write_csv(history, fields, [{"repo_name": "a", "TIMESTAMP": "2026-05-01", "github_actions": "True"}])
    _write_csv(main, fields, [{"repo_name": "a", "TIMESTAMP": "2026-05-08", "github_actions": "False"}])

    update_history_csv(str(main), str(history), history_days=90, today=datetime.date(2026, 5, 8))

    rows = _read_csv(history)
    stamps = sorted({r["TIMESTAMP"] for r in rows})
    assert stamps == ["2026-05-01", "2026-05-08"]


def test_history_rerun_same_day_is_idempotent(tmp_path):
    main = tmp_path / "dashboard_main.csv"
    history = tmp_path / "dashboard_history.csv"
    fields = ["repo_name", "TIMESTAMP"]

    _write_csv(main, fields, [{"repo_name": "a", "TIMESTAMP": "2026-05-08"}])
    for _ in range(3):
        update_history_csv(str(main), str(history), today=datetime.date(2026, 5, 8))

    rows = _read_csv(history)
    assert len(rows) == 1  # same-day re-runs replace, not duplicate


def test_history_prunes_old_snapshots(tmp_path):
    main = tmp_path / "dashboard_main.csv"
    history = tmp_path / "dashboard_history.csv"
    fields = ["repo_name", "TIMESTAMP"]

    _write_csv(history, fields, [
        {"repo_name": "a", "TIMESTAMP": "2026-01-01"},   # >90d before today → pruned
        {"repo_name": "a", "TIMESTAMP": "2026-05-01"},   # kept
    ])
    _write_csv(main, fields, [{"repo_name": "a", "TIMESTAMP": "2026-05-08"}])

    update_history_csv(str(main), str(history), history_days=90, today=datetime.date(2026, 5, 8))

    stamps = sorted({r["TIMESTAMP"] for r in _read_csv(history)})
    assert stamps == ["2026-05-01", "2026-05-08"]


def test_history_trims_heavy_columns(tmp_path):
    """List/blob and non-essential github.* columns are dropped from history."""
    main = tmp_path / "dashboard_main.csv"
    history = tmp_path / "dashboard_history.csv"
    fields = [
        "repo_name", "TIMESTAMP",
        "exists.openedx.yaml",              # kept (check column)
        "readme.bad_links",                 # kept (scoring reads it)
        "github.last_push",                 # kept (score-feeding github metric)
        "github.contributor_count_90d",     # kept (score-feeding github metric)
        "github.description",               # dropped (github metadata)
        "github.build_details",             # dropped (blob)
        "dependencies.pypi_all.list",       # dropped (.list)
        "language_bytes.python",            # dropped (language_bytes.*)
    ]
    row = {f: "x" for f in fields}
    row.update({"repo_name": "a", "TIMESTAMP": "2026-05-08"})
    _write_csv(main, fields, [row])

    update_history_csv(str(main), str(history), today=datetime.date(2026, 5, 8))

    cols = set(_read_csv(history)[0].keys())
    assert {"exists.openedx.yaml", "readme.bad_links",
            "github.last_push", "github.contributor_count_90d"} <= cols
    assert {"github.description", "github.build_details",
            "dependencies.pypi_all.list", "language_bytes.python"}.isdisjoint(cols)


def test_history_default_retention_is_30_days(tmp_path):
    """Rows older than the 30-day default are pruned."""
    main = tmp_path / "dashboard_main.csv"
    history = tmp_path / "dashboard_history.csv"
    fields = ["repo_name", "TIMESTAMP"]
    _write_csv(history, fields, [
        {"repo_name": "a", "TIMESTAMP": "2026-04-01"},   # 37 days before → pruned
        {"repo_name": "a", "TIMESTAMP": "2026-04-20"},   # 18 days before → kept
    ])
    _write_csv(main, fields, [{"repo_name": "a", "TIMESTAMP": "2026-05-08"}])

    update_history_csv(str(main), str(history), today=datetime.date(2026, 5, 8))

    stamps = sorted({r["TIMESTAMP"] for r in _read_csv(history)})
    assert stamps == ["2026-04-20", "2026-05-08"]


def test_history_unions_new_columns(tmp_path):
    """A snapshot that adds a new column must not lose older snapshots' data."""
    main = tmp_path / "dashboard_main.csv"
    history = tmp_path / "dashboard_history.csv"

    _write_csv(history, ["repo_name", "TIMESTAMP"], [{"repo_name": "a", "TIMESTAMP": "2026-05-01"}])
    _write_csv(main, ["repo_name", "TIMESTAMP", "github.release_count_12mo"],
               [{"repo_name": "a", "TIMESTAMP": "2026-05-08", "github.release_count_12mo": "5"}])

    update_history_csv(str(main), str(history), today=datetime.date(2026, 5, 8))

    rows = _read_csv(history)
    assert "github.release_count_12mo" in rows[0].keys()
    old = next(r for r in rows if r["TIMESTAMP"] == "2026-05-01")
    assert old["github.release_count_12mo"] == ""  # backfilled empty, row preserved
