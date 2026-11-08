"""Tests for gate_check.py - STYX gate evidence validation."""

from pathlib import Path


def test_gate_check_script_exists():
    """Verify gate_check.py script exists."""
    script_path = Path("scripts/gate_check.py")
    assert script_path.exists(), "Missing scripts/gate_check.py"


def test_gate_check_validates_gate_0():
    """Verify gate_check.py can validate gate_0.json."""
    import subprocess

    result = subprocess.run(
        ["uv", "run", "python", "scripts/gate_check.py", "--gate", "0"],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode == 0, f"gate_check.py --gate 0 failed: {result.stderr}"
    assert "validated successfully" in result.stdout


def test_gate_check_missing_evidence():
    """Verify gate_check.py reports error when evidence file missing."""
    import subprocess

    result = subprocess.run(
        ["uv", "run", "python", "scripts/gate_check.py", "--gate", "99"],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode != 0, "Should fail for missing gate evidence"
    assert "No evidence file found" in result.stdout
