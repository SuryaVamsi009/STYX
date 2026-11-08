#!/usr/bin/env python3
"""
Gate evidence checker for STYX.
Reads evidence/gate_<n>.json and validates PASS/FAIL/BLOCKED status.
"""

import json
import sys
from pathlib import Path
from typing import Literal


GateStatus = Literal["PASS", "FAIL", "BLOCKED"]


def check_gate_evidence(gate_num: int) -> GateStatus:
    """Check evidence for a specific gate."""
    evidence_dir = Path("evidence")
    evidence_file = evidence_dir / f"gate_{gate_num}.json"

    if not evidence_file.exists():
        print(f"FAIL: Evidence file not found: {evidence_file}")
        return "FAIL"

    with open(evidence_file) as f:
        evidence = json.load(f)

    # Basic validation
    required_fields = ["gate", "status", "timestamp", "tool_versions", "evidence_summary"]
    for field in required_fields:
        if field not in evidence:
            print(f"FAIL: Missing required field: {field}")
            return "FAIL"

    if evidence["gate"] != gate_num:
        print(f"FAIL: Gate number mismatch: expected {gate_num}, got {evidence['gate']}")
        return "FAIL"

    status = evidence["status"]
    if status not in ("PASS", "FAIL", "BLOCKED"):
        print(f"FAIL: Invalid status: {status}")
        return "FAIL"

    print(f"Gate {gate_num}: {status}")
    print(f"  Timestamp: {evidence['timestamp']}")
    print(f"  Tool versions: {evidence['tool_versions']}")
    print(f"  Summary: {evidence['evidence_summary']}")

    if "limitations" in evidence:
        print(f"  Limitations: {evidence['limitations']}")

    return status


def main():
    if len(sys.argv) != 3 or sys.argv[1] != "--gate":
        print("Usage: python scripts/gate_check.py --gate <n>")
        sys.exit(1)

    try:
        gate_num = int(sys.argv[2])
    except ValueError:
        print("Error: Gate number must be an integer")
        sys.exit(1)

    if not 0 <= gate_num <= 6:
        print("Error: Gate number must be 0-6")
        sys.exit(1)

    status = check_gate_evidence(gate_num)
    sys.exit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()