#!/usr/bin/env python3
"""
Generate STYX STATUS.md from evidence files and plan.json.

Usage:
    python scripts/status.py              # Print JSON summary to stdout
    python scripts/status.py --write      # Write STATUS.md
    python scripts/status.py --check      # Exit 1 if STATUS.md is stale
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EVIDENCE_DIR = Path("evidence")
PLAN_FILE = Path("docs/plan.json")
STATUS_FILE = Path("STATUS.md")

VALID_STATUSES = {"pass", "fail", "blocked"}
STATE_MAP = {
    "pass": "PASS",
    "fail": "FAIL",
    "blocked": "BLOCKED",
}
NOT_RUN = "NOT_RUN"
DEFERRED = "DEFERRED"

CLASS_FILLS = {
    "pass": "#2e7d32",      # green
    "fail": "#c62828",      # red
    "blocked": "#f57f17",   # amber
    "not_run": "#757575",   # grey
    "deferred": "#bdbdbd",  # light grey
}


def load_plan() -> dict[str, Any]:
    """Load and validate plan.json."""
    try:
        return json.loads(PLAN_FILE.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {PLAN_FILE}: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: Plan file not found: {PLAN_FILE}")
        sys.exit(1)


def load_evidence(filepath: Path) -> dict[str, Any] | None:
    """Load evidence file, return None if not found."""
    if not filepath.exists():
        return None
    try:
        return json.loads(filepath.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}")
        sys.exit(1)


def validate_gate_evidence(data: dict[str, Any], gate_num: int) -> str:
    """Validate gate evidence and return state. Exits on error."""
    # Check required keys
    required_keys = ["gate", "status", "recorded_at", "blockers"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        print(f"ERROR: Missing required keys in gate_{gate_num}.json: {missing}")
        sys.exit(1)

    # Validate gate number matches filename
    if data["gate"] != gate_num:
        print(f"ERROR: Expected gate {gate_num}, got {data['gate']}")
        sys.exit(1)

    # Validate status
    status = data["status"]
    if status not in VALID_STATUSES:
        valid = sorted(VALID_STATUSES)
        print(f"ERROR: Invalid status '{status}' in gate_{gate_num}.json. Must be one of {valid}")
        sys.exit(1)

    return STATE_MAP[status]


def validate_research_evidence(data: dict[str, Any], research_id: str) -> str:
    """Validate research evidence and return state. Exits on error."""
    required_keys = ["id", "status", "recorded_at", "blockers"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        print(f"ERROR: Missing required keys in {research_id}.json: {missing}")
        sys.exit(1)

    # Validate id matches filename
    if data["id"] != research_id:
        print(f"ERROR: Expected id {research_id}, got {data['id']}")
        sys.exit(1)

    # Validate status
    status = data["status"]
    if status not in VALID_STATUSES:
        valid = sorted(VALID_STATUSES)
        print(f"ERROR: Invalid status '{status}' in {research_id}.json. Must be one of {valid}")
        sys.exit(1)

    return STATE_MAP[status]


def get_gate_state(gate: dict[str, Any]) -> tuple[str, str | None, list[str]]:
    """Get state, recorded_at, and blockers for a gate."""
    gate_num = gate["n"]
    evidence_file = EVIDENCE_DIR / f"gate_{gate_num}.json"
    data = load_evidence(evidence_file)

    if data is None:
        # Gate 5 is deferred until evidence exists
        if gate.get("deferred", False):
            return DEFERRED, None, []
        return NOT_RUN, None, []

    state = validate_gate_evidence(data, gate_num)
    recorded_at = data.get("recorded_at")
    blockers = data.get("blockers", [])
    return state, recorded_at, blockers


def get_research_state(research: dict[str, Any]) -> tuple[str, str | None, list[str]]:
    """Get state, recorded_at, and blockers for a research step."""
    research_id = research["id"]
    evidence_file = EVIDENCE_DIR / f"research_{research_id.lower()}.json"
    data = load_evidence(evidence_file)

    if data is None:
        return NOT_RUN, None, []

    state = validate_research_evidence(data, research_id)
    recorded_at = data.get("recorded_at")
    blockers = data.get("blockers", [])
    return state, recorded_at, blockers


def truncate_blocker(blocker: str, max_len: int = 120) -> str:
    """Truncate blocker to max_len with ellipsis."""
    if len(blocker) <= max_len:
        return blocker
    return blocker[:max_len - 3] + "..."


def build_json_summary(plan: dict[str, Any]) -> dict[str, Any]:
    """Build the JSON summary object."""
    gates = plan["gates"]
    research = plan["research"]

    steps = []
    counts = {"PASS": 0, "FAIL": 0, "BLOCKED": 0, "NOT_RUN": 0, "DEFERRED": 0}

    # Process gates
    for gate in gates:
        state, recorded_at, blockers = get_gate_state(gate)
        steps.append({
            "id": gate["id"],
            "name": gate["name"],
            "state": state,
            "recorded_at": recorded_at,
            "blockers": blockers[:3],  # First 3 blockers
        })
        counts[state] = counts.get(state, 0) + 1

    # Process research
    for r in research:
        state, recorded_at, blockers = get_research_state(r)
        steps.append({
            "id": r["id"],
            "name": r["name"],
            "state": state,
            "recorded_at": recorded_at,
            "blockers": blockers[:3],
        })
        counts[state] = counts.get(state, 0) + 1

    # Find next step (first not PASS and not DEFERRED)
    next_step = None
    for step in steps:
        if step["state"] not in ("PASS", "DEFERRED"):
            next_step = {
                "id": step["id"],
                "name": step["name"],
                "state": step["state"],
                "blockers": step["blockers"][:1],  # First blocker only
            }
            break

    return {
        "steps": steps,
        "next": next_step,
        "counts": counts,
    }


def generate_mermaid(plan: dict[str, Any], summary: dict[str, Any]) -> str:
    """Generate Mermaid flowchart."""
    lines = ["flowchart LR"]

    # Pipeline gates subgraph
    lines.append("    subgraph Pipeline_gates[Pipeline gates]")
    gates = plan["gates"]
    for i, gate in enumerate(gates):
        step = next(s for s in summary["steps"] if s["id"] == gate["id"])
        label = f'{gate["id"]}["{gate["id"]} {gate["name"]}<br/>{step["state"]}"]'
        lines.append(f"        {label}")
        if i < len(gates) - 1:
            lines.append(f"        {gates[i]['id']} --> {gates[i+1]['id']}")
    lines.append("    end")

    # Research loop subgraph
    lines.append("    subgraph Research_loop[Research loop]")
    research = plan["research"]
    for i, r in enumerate(research):
        step = next(s for s in summary["steps"] if s["id"] == r["id"])
        label = f'{r["id"]}["{r["id"]} {r["name"]}<br/>{step["state"]}"]'
        lines.append(f"        {label}")
        if i < len(research) - 1:
            lines.append(f"        {research[i]['id']} --> {research[i+1]['id']}")
    lines.append("    end")

    # Dotted edge from research_starts_after to R1
    research_starts_after = plan["research_starts_after"]
    lines.append(f"    {research_starts_after} -.-> R1")

    # Class definitions
    lines.append("")
    lines.append("    classDef pass fill:#2e7d32,color:#fff;")
    lines.append("    classDef fail fill:#c62828,color:#fff;")
    lines.append("    classDef blocked fill:#f57f17,color:#fff;")
    lines.append("    classDef not_run fill:#757575,color:#fff;")
    lines.append("    classDef deferred fill:#bdbdbd,color:#fff,stroke-dasharray: 5 5;")

    # Class assignments
    for step in summary["steps"]:
        state_class = step["state"].lower()
        lines.append(f"    class {step['id']} {state_class};")

    return "\n".join(lines)


def generate_table(summary: dict[str, Any]) -> str:
    """Generate the status table."""
    lines = [
        "",
        "## Status Table",
        "",
        "| Step | State | Recorded | Blockers |",
        "|------|-------|----------|----------|",
    ]

    for step in summary["steps"]:
        recorded = step["recorded_at"] or "—"
        blockers = step["blockers"]
        if blockers:
            blocker_text = "<br/>".join(f"- {truncate_blocker(b)}" for b in blockers)
        else:
            blocker_text = "—"
        lines.append(f"| {step['id']} | {step['state']} | {recorded} | {blocker_text} |")

    return "\n".join(lines)


def generate_next_line(summary: dict[str, Any]) -> str:
    """Generate the Next line."""
    next_step = summary["next"]
    if next_step is None:
        return "\n**Next:** All steps complete."
    blockers = next_step["blockers"]
    blocker_text = f" — {truncate_blocker(blockers[0])}" if blockers else ""
    return f"\n**Next:** {next_step['id']} {next_step['name']} ({next_step['state']}){blocker_text}"


def write_status_md(plan: dict[str, Any], summary: dict[str, Any]) -> str:
    """Generate full STATUS.md content."""
    lines = [
        "# STYX Status",
        "",
        "Generated by scripts/status.py from evidence/. Do not edit by hand.",
        "",
        "```mermaid",
        generate_mermaid(plan, summary),
        "```",
        generate_table(summary),
        generate_next_line(summary),
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate STYX status")
    parser.add_argument("--write", action="store_true", help="Write STATUS.md")
    parser.add_argument("--check", action="store_true", help="Check if STATUS.md is current")
    args = parser.parse_args()

    if not args.write and not args.check:
        # Default: print JSON summary
        plan = load_plan()
        summary = build_json_summary(plan)
        print(json.dumps(summary, indent=2))
        return 0

    plan = load_plan()
    summary = build_json_summary(plan)
    new_content = write_status_md(plan, summary)

    if args.write:
        STATUS_FILE.write_text(new_content)
        print(f"Written {STATUS_FILE}")
        return 0

    if args.check:
        if not STATUS_FILE.exists():
            print(f"ERROR: {STATUS_FILE} does not exist")
            return 1
        current_content = STATUS_FILE.read_text()
        if current_content != new_content:
            msg = (
                f"ERROR: {STATUS_FILE} is stale. "
                "Run 'python scripts/status.py --write' to update."
            )
            print(msg)
            return 1
        print(f"{STATUS_FILE} is current")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())