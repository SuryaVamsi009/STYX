"""Validate Pulse gate evidence files.

Run via: uv run python scripts/gate_check.py --gate <n>
"""

import argparse
import json
import sys
from pathlib import Path


def validate_gate_0(evidence_path: Path) -> int:
    """Validate gate_0.json evidence file structure."""
    try:
        data = json.loads(evidence_path.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {evidence_path}: {e}")
        return 1

    # Check required top-level keys
    required_keys = [
        "gate",
        "status",
        "recorded_at",
        "scope",
        "approved_test_only_capital",
        "checks",
        "blockers",
        "credentials_recorded",
    ]
    missing = [k for k in required_keys if k not in data]
    if missing:
        print(f"ERROR: Missing required keys in gate_0.json: {missing}")
        return 1

    # Validate gate number
    if data["gate"] != 0:
        print(f"ERROR: Expected gate 0, got {data['gate']}")
        return 1

    # Validate status
    valid_statuses = ["pass", "fail", "blocked"]
    if data["status"] not in valid_statuses:
        print(f"ERROR: Invalid status '{data['status']}'. Must be one of {valid_statuses}")
        return 1

    # Validate scope
    scope = data.get("scope", {})
    required_scope_keys = ["provider", "route", "environment", "instrument"]
    missing_scope = [k for k in required_scope_keys if k not in scope]
    if missing_scope:
        print(f"ERROR: Missing required scope keys: {missing_scope}")
        return 1

    # Validate provider
    provider = scope.get("provider")
    allowed_providers = ["NOT_SET", "Angel One", "Fyers"]
    if provider not in allowed_providers:
        print(f"ERROR: Invalid provider '{provider}'. Must be one of {allowed_providers}")
        return 1

    # If status is pass, provider must be Angel One or Fyers (not NOT_SET)
    if data["status"] == "pass" and provider == "NOT_SET":
        print("ERROR: Provider must be 'Angel One' or 'Fyers' when status is 'pass', not 'NOT_SET'")
        return 1

    # Validate instrument
    instrument = scope.get("instrument", {})
    required_instrument_keys = ["symbol", "exchange", "asset_type", "product"]
    missing_instrument = [k for k in required_instrument_keys if k not in instrument]
    if missing_instrument:
        print(f"ERROR: Missing required instrument keys: {missing_instrument}")
        return 1

    # Validate approved_test_only_capital
    capital = data.get("approved_test_only_capital", {})
    if not capital:
        print("WARNING: approved_test_only_capital is empty or missing")

    # Validate checks
    checks = data.get("checks", {})
    # These are expected to be present (some UNVERIFIED, some NOT_RUN)
    # Just check it's a dict
    if not isinstance(checks, dict):
        print("ERROR: checks must be a dict")
        return 1

    # Validate blockers
    blockers = data.get("blockers", [])
    if not isinstance(blockers, list):
        print("ERROR: blockers must be a list")
        return 1

    # Validate credentials_recorded
    if not isinstance(data.get("credentials_recorded"), bool):
        print("ERROR: credentials_recorded must be a bool")
        return 1

    print(f"Gate 0 evidence validated successfully: {data['gate']} - {data['status']}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Validate Pulse gate evidence files")
    parser.add_argument("--gate", type=int, required=True, help="Gate number to validate")
    parser.add_argument(
        "--evidence-file",
        type=Path,
        help="Path to evidence file (default: evidence/gate_<n>.json)",
    )
    args = parser.parse_args()

    if args.evidence_file:
        evidence_file = args.evidence_file
    else:
        evidence_dir = Path("evidence")
        evidence_file = evidence_dir / f"gate_{args.gate}.json"

    if not evidence_file.exists():
        print(f"ERROR: No evidence file found: {evidence_file}")
        if not args.evidence_file:
            print(f"Searched in: {evidence_dir}")
        return 1

    # Route to appropriate validator based on gate number
    if args.gate == 0:
        return validate_gate_0(evidence_file)
    else:
        print(f"Gate {args.gate} validation not yet implemented")
        # For gates > 0, just check the file exists and is valid JSON
        try:
            json.loads(evidence_file.read_text())
            print(f"Gate {args.gate} evidence file is valid JSON")
            return 0
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in gate_{args.gate}.json: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
