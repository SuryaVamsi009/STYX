"""Tests for gate_check.py - STYX gate evidence validation."""

import json
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
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "99",
            "--evidence-file",
            "/nonexistent/gate_99.json",
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode != 0, "Should fail for missing gate evidence"
    assert "No evidence file found" in result.stdout


def _minimal_gate_0_evidence(provider: str = "NOT_SET", status: str = "blocked") -> dict:
    """Create a minimal valid gate_0 evidence dict."""
    return {
        "gate": 0,
        "status": status,
        "recorded_at": "2026-11-08",
        "scope": {
            "provider": provider,
            "route": "OpenAlgo Analyzer Mode",
            "environment": "Surya's own machine",
            "tool_versions": {"openalgo": "UNVERIFIED", "broker_integration": "UNVERIFIED"},
            "broker_account_reference": "NOT_RECORDED",
            "instrument": {
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "asset_type": "cash equity",
                "product": "MIS",
            },
            "paper_order": {"side": "Buy", "type": "Market", "quantity": 1, "status": "NOT_RUN"},
        },
        "approved_test_only_capital": {
            "amount_inr": 2000,
            "approved_by": "Surya",
            "purpose": "Single Gate 0 paper-order exercise only",
            "is_planning_capital": False,
            "leverage": {
                "MIS": "1x (no leverage)",
                "CNC": "1x (no leverage)",
                "futures_and_options": "not used",
            },
            "strategy_evidence": False,
            "reset_required_before": ["Gate 3", "any research run", "any strategy run"],
        },
        "checks": {
            "installed_openalgo_version": "UNVERIFIED",
            "version_matched_analyzer_mode_docs": "UNVERIFIED",
            "provider_terms": "UNVERIFIED",
            "analyzer_mode_pre_order_state": "NOT_RUN",
            "styx_source_order_call_search": {
                "status": "NO_MATCHES_FOUND",
                "patterns": [
                    "placeorder",
                    "smartorder",
                    "basketorder",
                    "FyersLiveExecClientFactory",
                    "exec_clients",
                ],
                "search_result": "No matches found",
            },
            "active_openalgo_route_audit": "NOT_RUN",
            "real_order_path_guard": "NOT_RUN",
            "capital_requirement_including_charges": "UNVERIFIED",
            "nse_regular_session": "NOT_RUN",
            "quiet_account_window": "NOT_RUN",
            "broker_orderbook_visibility_docs": "UNVERIFIED",
            "broker_orderbook_before_snapshot": "NOT_RUN",
            "broker_orderbook_after_snapshot": "NOT_RUN",
            "virtual_order_record": "NOT_RUN",
            "part_a": "NOT_RUN",
            "part_b": "NOT_RUN",
            "gate_check": "NOT_RUN",
        },
        "blockers": [
            "No local OpenAlgo installation or installed-version documentation "
            "is available; Analyzer Mode isolation is UNVERIFIED.",
            "Part A and Part B have not been run.",
        ],
        "credentials_recorded": False,
    }


def test_validate_gate_0_provider_not_set_blocked(tmp_path):
    """NOT_SET provider is valid for blocked status."""
    evidence = _minimal_gate_0_evidence(provider="NOT_SET", status="blocked")
    evidence_file = tmp_path / "gate_0.json"
    evidence_file.write_text(json.dumps(evidence))

    import subprocess

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "0",
            "--evidence-file",
            str(evidence_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode == 0, (
        f"Should pass for NOT_SET provider with blocked status: {result.stderr}"
    )


def test_validate_gate_0_provider_angel_one_blocked(tmp_path):
    """Angel One provider is valid for blocked status."""
    evidence = _minimal_gate_0_evidence(provider="Angel One", status="blocked")
    evidence_file = tmp_path / "gate_0.json"
    evidence_file.write_text(json.dumps(evidence))

    import subprocess

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "0",
            "--evidence-file",
            str(evidence_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode == 0, (
        f"Should pass for Angel One provider with blocked status: {result.stderr}"
    )


def test_validate_gate_0_provider_fyers_blocked(tmp_path):
    """Fyers provider is valid for blocked status."""
    evidence = _minimal_gate_0_evidence(provider="Fyers", status="blocked")
    evidence_file = tmp_path / "gate_0.json"
    evidence_file.write_text(json.dumps(evidence))

    import subprocess

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "0",
            "--evidence-file",
            str(evidence_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode == 0, (
        f"Should pass for Fyers provider with blocked status: {result.stderr}"
    )


def test_validate_gate_0_provider_not_set_fail(tmp_path):
    """NOT_SET provider is valid for fail status."""
    evidence = _minimal_gate_0_evidence(provider="NOT_SET", status="fail")
    evidence_file = tmp_path / "gate_0.json"
    evidence_file.write_text(json.dumps(evidence))

    import subprocess

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "0",
            "--evidence-file",
            str(evidence_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode == 0, (
        f"Should pass for NOT_SET provider with fail status: {result.stderr}"
    )


def test_validate_gate_0_provider_angel_one_fail(tmp_path):
    """Angel One provider is valid for fail status."""
    evidence = _minimal_gate_0_evidence(provider="Angel One", status="fail")
    evidence_file = tmp_path / "gate_0.json"
    evidence_file.write_text(json.dumps(evidence))

    import subprocess

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "0",
            "--evidence-file",
            str(evidence_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode == 0, (
        f"Should pass for Angel One provider with fail status: {result.stderr}"
    )


def test_validate_gate_0_provider_fyers_fail(tmp_path):
    """Fyers provider is valid for fail status."""
    evidence = _minimal_gate_0_evidence(provider="Fyers", status="fail")
    evidence_file = tmp_path / "gate_0.json"
    evidence_file.write_text(json.dumps(evidence))

    import subprocess

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "0",
            "--evidence-file",
            str(evidence_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode == 0, (
        f"Should pass for Fyers provider with fail status: {result.stderr}"
    )


def test_validate_gate_0_provider_not_set_pass_fails(tmp_path):
    """NOT_SET provider is INVALID for pass status."""
    evidence = _minimal_gate_0_evidence(provider="NOT_SET", status="pass")
    evidence_file = tmp_path / "gate_0.json"
    evidence_file.write_text(json.dumps(evidence))

    import subprocess

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "0",
            "--evidence-file",
            str(evidence_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode != 0, "Should fail for NOT_SET provider with pass status"
    assert "provider" in result.stdout.lower() or "provider" in result.stderr.lower()


def test_validate_gate_0_provider_angel_one_pass(tmp_path):
    """Angel One provider is valid for pass status."""
    evidence = _minimal_gate_0_evidence(provider="Angel One", status="pass")
    evidence_file = tmp_path / "gate_0.json"
    evidence_file.write_text(json.dumps(evidence))

    import subprocess

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "0",
            "--evidence-file",
            str(evidence_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode == 0, (
        f"Should pass for Angel One provider with pass status: {result.stderr}"
    )


def test_validate_gate_0_provider_fyers_pass(tmp_path):
    """Fyers provider is valid for pass status."""
    evidence = _minimal_gate_0_evidence(provider="Fyers", status="pass")
    evidence_file = tmp_path / "gate_0.json"
    evidence_file.write_text(json.dumps(evidence))

    import subprocess

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "0",
            "--evidence-file",
            str(evidence_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode == 0, (
        f"Should pass for Fyers provider with pass status: {result.stderr}"
    )


def test_validate_gate_0_provider_invalid_zerodha(tmp_path):
    """Invalid provider (Zerodha) should fail."""
    evidence = _minimal_gate_0_evidence(provider="Zerodha", status="blocked")
    evidence_file = tmp_path / "gate_0.json"
    evidence_file.write_text(json.dumps(evidence))

    import subprocess

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "0",
            "--evidence-file",
            str(evidence_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode != 0, "Should fail for invalid provider Zerodha"
    assert "provider" in result.stdout.lower() or "provider" in result.stderr.lower()


def test_validate_gate_0_provider_empty_string(tmp_path):
    """Empty string provider should fail."""
    evidence = _minimal_gate_0_evidence(provider="", status="blocked")
    evidence_file = tmp_path / "gate_0.json"
    evidence_file.write_text(json.dumps(evidence))

    import subprocess

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "0",
            "--evidence-file",
            str(evidence_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode != 0, "Should fail for empty string provider"
    assert "provider" in result.stdout.lower() or "provider" in result.stderr.lower()


def test_validate_gate_0_provider_missing_key(tmp_path):
    """Missing provider key should fail."""
    evidence = _minimal_gate_0_evidence(provider="Angel One", status="blocked")
    del evidence["scope"]["provider"]
    evidence_file = tmp_path / "gate_0.json"
    evidence_file.write_text(json.dumps(evidence))

    import subprocess

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/gate_check.py",
            "--gate",
            "0",
            "--evidence-file",
            str(evidence_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path("."),
    )
    assert result.returncode != 0, "Should fail for missing provider key"
    assert "provider" in result.stdout.lower() or "provider" in result.stderr.lower()
