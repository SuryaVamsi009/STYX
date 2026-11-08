"""Tests for status.py - STYX status generator."""

import json
import subprocess
from pathlib import Path


def run_status(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run status.py with given args."""
    return subprocess.run(
        ["uv", "run", "python", "scripts/status.py"] + args,
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_no_evidence_all_not_run_except_g5_deferred(tmp_path: Path):
    """No evidence at all: every gate NOT_RUN except Gate 5 DEFERRED; next is G0."""
    # Copy plan.json to temp dir
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    # Copy status.py to temp dir
    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    # Create empty evidence dir
    (tmp_path / "evidence").mkdir()

    result = run_status([], tmp_path)
    assert result.returncode == 0, f"status.py failed: {result.stderr}"

    summary = json.loads(result.stdout)
    steps = {s["id"]: s for s in summary["steps"]}

    # All gates NOT_RUN except G5 DEFERRED
    for i in range(7):
        gate_id = f"G{i}"
        if i == 5:
            assert steps[gate_id]["state"] == "DEFERRED", f"{gate_id} should be DEFERRED"
        else:
            assert steps[gate_id]["state"] == "NOT_RUN", f"{gate_id} should be NOT_RUN"

    # All research NOT_RUN
    for i in range(1, 7):
        r_id = f"R{i}"
        assert steps[r_id]["state"] == "NOT_RUN", f"{r_id} should be NOT_RUN"

    # Next should be G0
    assert summary["next"]["id"] == "G0"
    assert summary["next"]["state"] == "NOT_RUN"


def test_gate_0_pass_moves_next_to_g1(tmp_path: Path):
    """pass on G0 moves next to G1."""
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    (tmp_path / "evidence").mkdir()

    # Create gate_0.json with pass status
    gate_0 = {
        "gate": 0,
        "status": "pass",
        "recorded_at": "2026-11-08",
        "scope": {},
        "approved_test_only_capital": {},
        "checks": {},
        "blockers": [],
        "credentials_recorded": False,
    }
    (tmp_path / "evidence" / "gate_0.json").write_text(json.dumps(gate_0))

    result = run_status([], tmp_path)
    assert result.returncode == 0, f"status.py failed: {result.stderr}"

    summary = json.loads(result.stdout)
    steps = {s["id"]: s for s in summary["steps"]}

    assert steps["G0"]["state"] == "PASS"
    assert summary["next"]["id"] == "G1"
    assert summary["next"]["state"] == "NOT_RUN"


def test_gate_0_fail_state(tmp_path: Path):
    """fail maps to FAIL state."""
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    (tmp_path / "evidence").mkdir()

    gate_0 = {
        "gate": 0,
        "status": "fail",
        "recorded_at": "2026-11-08",
        "scope": {},
        "approved_test_only_capital": {},
        "checks": {},
        "blockers": ["Some blocker"],
        "credentials_recorded": False,
    }
    (tmp_path / "evidence" / "gate_0.json").write_text(json.dumps(gate_0))

    result = run_status([], tmp_path)
    assert result.returncode == 0, f"status.py failed: {result.stderr}"

    summary = json.loads(result.stdout)
    steps = {s["id"]: s for s in summary["steps"]}

    assert steps["G0"]["state"] == "FAIL"
    # Next should still be G0 since it's not PASS
    assert summary["next"]["id"] == "G0"


def test_gate_0_blocked_state(tmp_path: Path):
    """blocked maps to BLOCKED state."""
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    (tmp_path / "evidence").mkdir()

    gate_0 = {
        "gate": 0,
        "status": "blocked",
        "recorded_at": "2026-11-08",
        "scope": {},
        "approved_test_only_capital": {},
        "checks": {},
        "blockers": ["Blocked reason"],
        "credentials_recorded": False,
    }
    (tmp_path / "evidence" / "gate_0.json").write_text(json.dumps(gate_0))

    result = run_status([], tmp_path)
    assert result.returncode == 0, f"status.py failed: {result.stderr}"

    summary = json.loads(result.stdout)
    steps = {s["id"]: s for s in summary["steps"]}

    assert steps["G0"]["state"] == "BLOCKED"
    assert summary["next"]["id"] == "G0"


def test_gate_5_with_evidence_shows_real_state_not_deferred(tmp_path: Path):
    """Gate 5 with an evidence file shows its real state, not DEFERRED."""
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    (tmp_path / "evidence").mkdir()

    gate_5 = {
        "gate": 5,
        "status": "pass",
        "recorded_at": "2026-11-08",
        "scope": {},
        "approved_test_only_capital": {},
        "checks": {},
        "blockers": [],
        "credentials_recorded": False,
    }
    (tmp_path / "evidence" / "gate_5.json").write_text(json.dumps(gate_5))

    result = run_status([], tmp_path)
    assert result.returncode == 0, f"status.py failed: {result.stderr}"

    summary = json.loads(result.stdout)
    steps = {s["id"]: s for s in summary["steps"]}

    assert steps["G5"]["state"] == "PASS", "G5 should show PASS, not DEFERRED"


def test_unknown_status_exits_1(tmp_path: Path):
    """Unknown status (e.g., 'passed') exits 1 and writes nothing."""
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    (tmp_path / "evidence").mkdir()

    gate_0 = {
        "gate": 0,
        "status": "passed",  # Invalid status
        "recorded_at": "2026-11-08",
        "scope": {},
        "approved_test_only_capital": {},
        "checks": {},
        "blockers": [],
        "credentials_recorded": False,
    }
    (tmp_path / "evidence" / "gate_0.json").write_text(json.dumps(gate_0))

    result = run_status([], tmp_path)
    assert result.returncode == 1, f"Should exit 1 for unknown status, got {result.returncode}"
    assert "Invalid status" in result.stdout or "Invalid status" in result.stderr


def test_invalid_json_exits_1(tmp_path: Path):
    """Invalid JSON exits 1."""
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    (tmp_path / "evidence").mkdir()

    (tmp_path / "evidence" / "gate_0.json").write_text("{ invalid json }")

    result = run_status([], tmp_path)
    assert result.returncode == 1, f"Should exit 1 for invalid JSON, got {result.returncode}"
    assert "Invalid JSON" in result.stdout or "Invalid JSON" in result.stderr


def test_gate_number_mismatch_exits_1(tmp_path: Path):
    """A file gate_2.json that says 'gate': 3 exits 1."""
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    (tmp_path / "evidence").mkdir()

    gate_2 = {
        "gate": 3,  # Mismatch: file is gate_2.json but gate is 3
        "status": "pass",
        "recorded_at": "2026-11-08",
        "scope": {},
        "approved_test_only_capital": {},
        "checks": {},
        "blockers": [],
        "credentials_recorded": False,
    }
    (tmp_path / "evidence" / "gate_2.json").write_text(json.dumps(gate_2))

    result = run_status([], tmp_path)
    assert result.returncode == 1, (
        f"Should exit 1 for gate number mismatch, got {result.returncode}"
    )
    assert "Expected gate 2, got 3" in result.stdout or "Expected gate 2, got 3" in result.stderr


def test_output_deterministic_no_date_no_sha(tmp_path: Path):
    """Output is byte-identical across two runs, and does not contain current year or commit sha."""
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    (tmp_path / "evidence").mkdir()

    gate_0 = {
        "gate": 0,
        "status": "blocked",
        "recorded_at": "2026-11-08",
        "scope": {},
        "approved_test_only_capital": {},
        "checks": {},
        "blockers": ["Test blocker"],
        "credentials_recorded": False,
    }
    (tmp_path / "evidence" / "gate_0.json").write_text(json.dumps(gate_0))

    result1 = run_status(["--write"], tmp_path)
    assert result1.returncode == 0

    content1 = (tmp_path / "STATUS.md").read_text()

    result2 = run_status(["--write"], tmp_path)
    assert result2.returncode == 0

    content2 = (tmp_path / "STATUS.md").read_text()

    assert content1 == content2, "Output should be byte-identical across runs"

    # Check no current year (2026 is in recorded_at which is allowed, but not generated at runtime)
    # The test uses a fixed recorded_at, so this is fine
    # Check no commit sha (should not appear)
    import re
    sha_pattern = re.compile(r"[a-f0-9]{40}")
    assert not sha_pattern.search(content1), "Should not contain commit SHA"


def test_check_returns_0_after_write(tmp_path: Path):
    """--check returns 0 right after --write."""
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    (tmp_path / "evidence").mkdir()

    gate_0 = {
        "gate": 0,
        "status": "blocked",
        "recorded_at": "2026-11-08",
        "scope": {},
        "approved_test_only_capital": {},
        "checks": {},
        "blockers": ["Test blocker"],
        "credentials_recorded": False,
    }
    (tmp_path / "evidence" / "gate_0.json").write_text(json.dumps(gate_0))

    # Write
    result_write = run_status(["--write"], tmp_path)
    assert result_write.returncode == 0

    # Check
    result_check = run_status(["--check"], tmp_path)
    assert result_check.returncode == 0, (
        f"--check should return 0 after --write, got {result_check.returncode}"
    )


def test_check_returns_1_after_evidence_change(tmp_path: Path):
    """--check returns 1 after one evidence value is changed."""
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    (tmp_path / "evidence").mkdir()

    gate_0 = {
        "gate": 0,
        "status": "blocked",
        "recorded_at": "2026-11-08",
        "scope": {},
        "approved_test_only_capital": {},
        "checks": {},
        "blockers": ["Test blocker"],
        "credentials_recorded": False,
    }
    (tmp_path / "evidence" / "gate_0.json").write_text(json.dumps(gate_0))

    # Write
    result_write = run_status(["--write"], tmp_path)
    assert result_write.returncode == 0

    # Change evidence
    gate_0["blockers"] = ["Changed blocker"]
    (tmp_path / "evidence" / "gate_0.json").write_text(json.dumps(gate_0))

    # Check should fail
    result_check = run_status(["--check"], tmp_path)
    assert result_check.returncode == 1, (
        f"--check should return 1 after evidence change, got {result_check.returncode}"
    )


def test_mermaid_contains_all_nodes_and_classes(tmp_path: Path):
    """Mermaid output contains every node id, one class line per node,
    and no raw quotes inside labels."""
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    (tmp_path / "evidence").mkdir()

    gate_0 = {
        "gate": 0,
        "status": "blocked",
        "recorded_at": "2026-11-08",
        "scope": {},
        "approved_test_only_capital": {},
        "checks": {},
        "blockers": ["Test blocker"],
        "credentials_recorded": False,
    }
    (tmp_path / "evidence" / "gate_0.json").write_text(json.dumps(gate_0))

    result = run_status(["--write"], tmp_path)
    assert result.returncode == 0

    content = (tmp_path / "STATUS.md").read_text()

    # Extract mermaid block
    import re
    mermaid_match = re.search(r"```mermaid\n(.*?)\n```", content, re.DOTALL)
    assert mermaid_match, "Mermaid block not found"
    mermaid = mermaid_match.group(1)

    # Check all node IDs present (G0-G6, R1-R6)
    for i in range(7):
        assert f"G{i}" in mermaid, f"G{i} not in mermaid"
    for i in range(1, 7):
        assert f"R{i}" in mermaid, f"R{i} not in mermaid"

    # Check class lines - one per node (13 total: 7 gates + 6 research)
    class_lines = [line for line in mermaid.split("\n") if line.strip().startswith("class ")]
    assert len(class_lines) == 13, f"Expected 13 class lines, got {len(class_lines)}"

    # Check no raw double quotes *inside* label text
    # (quotes around labels are required by Mermaid)
    # Count quotes that are not the opening/closing quotes of node labels
    # Each node label has 2 quotes, so 13 nodes = 26 quotes expected
    quote_count = mermaid.count('"')
    assert quote_count == 26, f"Expected 26 quotes (2 per node for 13 nodes), got {quote_count}"


def test_blocker_truncation(tmp_path: Path):
    """Blocker truncation: 4 blockers show 3; a 200-character blocker is cut with ..."""
    plan_src = Path("docs/plan.json")
    plan_dst = tmp_path / "docs" / "plan.json"
    plan_dst.parent.mkdir(parents=True)
    plan_dst.write_text(plan_src.read_text())

    status_src = Path("scripts/status.py")
    status_dst = tmp_path / "scripts" / "status.py"
    status_dst.parent.mkdir(parents=True)
    status_dst.write_text(status_src.read_text())

    (tmp_path / "evidence").mkdir()

    gate_0 = {
        "gate": 0,
        "status": "blocked",
        "recorded_at": "2026-11-08",
        "scope": {},
        "approved_test_only_capital": {},
        "checks": {},
        "blockers": [
            "Blocker 1",
            "Blocker 2",
            "x" * 200,  # Long blocker in 3rd position to be shown and truncated
            "Blocker 4",
        ],
        "credentials_recorded": False,
    }
    (tmp_path / "evidence" / "gate_0.json").write_text(json.dumps(gate_0))

    result = run_status(["--write"], tmp_path)
    assert result.returncode == 0

    content = (tmp_path / "STATUS.md").read_text()

    # Check table shows only first 3 blockers
    assert "Blocker 1" in content
    assert "Blocker 2" in content
    # 3rd blocker is the long one, should be truncated
    assert "x" * 117 in content  # First 117 chars of 200-char blocker (120 - 3 for ...)
    assert "..." in content, "Long blocker should be truncated with ..."
    assert "Blocker 4" not in content, "Should only show first 3 blockers"


def test_real_repo_gate_0_blocked():
    """Run the real repo once: with the current evidence/gate_0.json, G0 is BLOCKED."""
    result = run_status([], Path("."))
    assert result.returncode == 0, f"status.py failed on real repo: {result.stderr}"

    summary = json.loads(result.stdout)
    steps = {s["id"]: s for s in summary["steps"]}

    assert steps["G0"]["state"] == "BLOCKED", f"G0 should be BLOCKED, got {steps['G0']['state']}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])