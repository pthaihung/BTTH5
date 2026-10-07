"""CLI workload contract, including reserving IDs on invalid first occurrences."""

import json
import subprocess
import sys

import pytest

import paths

SCRIPT = paths.WORKSPACE_DIR / "skills/csv-quality/scripts/check_csv.py"
CSV = "task_id,owner,hours\nT01,Lan,4\nT02,Lan,5\nT03,Minh,3\nT04,Minh,abc\nT02,Lan,5\nT05,,2\n"


def run_csv(tmp_path, text, threshold):
    source = tmp_path / "input.csv"
    source.write_text(text, encoding="utf-8")
    before = source.read_bytes()
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(SCRIPT), "--input", str(source), "--max-hours", str(threshold)],
        capture_output=True, text=True, encoding="utf-8", timeout=10,
    )
    assert source.read_bytes() == before
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    return json.loads(result.stdout)


@pytest.mark.parametrize("threshold,overloaded", [
    (8, [{"owner": "Lan", "total_hours": 9}]), (9, []),
])
def test_workload_given_csv(tmp_path, threshold, overloaded):
    result = run_csv(tmp_path, CSV, threshold)
    assert result["max_hours"] == threshold
    assert result["hours_by_owner"] == {"Lan": 9, "Minh": 3}
    assert result["overloaded_owners"] == overloaded
    assert result["excluded_rows"] == [
        {"line": 5, "task_id": "T04", "reasons": ["invalid_hours"]},
        {"line": 6, "task_id": "T02", "reasons": ["duplicate_id"]},
        {"line": 7, "task_id": "T05", "reasons": ["missing_owner"]},
    ]
    assert result["row_count"] == 6
    assert result["missing_owner_count"] == result["invalid_hours_count"] == result["duplicate_id_count"] == 1


def test_invalid_first_occurrence_reserves_id(tmp_path):
    result = run_csv(tmp_path, "task_id,owner,hours\nE01,Lan,abc\nE01,Lan,5\nE02,Minh,0\n", 0)
    assert result["hours_by_owner"] == {"Minh": 0}
    assert result["overloaded_owners"] == []
    assert result["excluded_rows"] == [
        {"line": 2, "task_id": "E01", "reasons": ["invalid_hours"]},
        {"line": 3, "task_id": "E01", "reasons": ["duplicate_id"]},
    ]


def test_all_exclusion_reasons_are_preserved_in_order(tmp_path):
    text = "task_id,owner,hours\nX,Who,1\nX,,bad,extra\n,,bad,extra\nY,,2\nY,Who,3\n"
    result = run_csv(tmp_path, text, 1)
    assert result["hours_by_owner"] == {"Who": 1}
    assert result["overloaded_owners"] == []
    assert result["excluded_rows"] == [
        {"line": 3, "task_id": "X", "reasons": ["wrong_field_count", "duplicate_id", "missing_owner", "invalid_hours"]},
        {"line": 4, "task_id": None, "reasons": ["wrong_field_count", "missing_task_id", "missing_owner", "invalid_hours"]},
        {"line": 5, "task_id": "Y", "reasons": ["missing_owner"]},
        {"line": 6, "task_id": "Y", "reasons": ["duplicate_id"]},
    ]
    assert result["row_count"] == 5 and result["missing_owner_count"] == 3
    assert result["invalid_hours_count"] == 2 and result["duplicate_id_count"] == 2


def test_trim_case_zero_and_blank_lines(tmp_path):
    result = run_csv(tmp_path, "task_id,owner,hours\n A , Lan , 2 \nA,Lan,3\nB,lan,0\n\nC,An,1.5\n", 1)
    assert result["hours_by_owner"] == {"An": 1.5, "Lan": 2, "lan": 0}
    assert result["overloaded_owners"] == [{"owner": "An", "total_hours": 1.5}, {"owner": "Lan", "total_hours": 2}]
    assert result["row_count"] == 4
    assert result["excluded_rows"] == [{"line": 3, "task_id": "A", "reasons": ["duplicate_id"]}]


@pytest.mark.parametrize("threshold", [None, "-1", "NaN", "inf", "-inf", "abc", ""])
def test_missing_or_invalid_threshold_is_cli_error(tmp_path, threshold):
    source = tmp_path / "input.csv"
    source.write_text(CSV)
    args = [sys.executable, "-X", "utf8", str(SCRIPT), "--input", str(source)]
    if threshold is not None:
        args.append(f"--max-hours={threshold}")
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", timeout=10)
    assert result.returncode != 0
    assert result.stderr and not result.stdout


def test_wrong_field_first_occurrence_also_reserves_id(tmp_path):
    result = run_csv(tmp_path, "task_id,owner,hours\nX,Lan,2,extra\nX,Lan,5\n", 0)
    assert result["hours_by_owner"] == {}
    assert result["excluded_rows"] == [
        {"line": 2, "task_id": "X", "reasons": ["wrong_field_count"]},
        {"line": 3, "task_id": "X", "reasons": ["duplicate_id"]},
    ]
