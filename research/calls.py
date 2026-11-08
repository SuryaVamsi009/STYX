"""
Research loop: Call registry (R1).
Append-only ledger of research calls.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
import uuid


@dataclass(frozen=True)
class Call:
    """Research call record - immutable once created."""
    id: str
    created_at: str  # ISO format
    origin: str  # "scan", "ai", "manual"
    symbol: str
    side: str  # "LONG" or "SHORT"
    entry_rule: str
    stop: float
    target: float
    horizon_days: int
    rationale: str  # Two lines max
    snapshot_id: str


class CallRegistry:
    """Append-only call registry."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, call: Call) -> None:
        """Append a call to the registry."""
        with open(self.path, "a") as f:
            f.write(json.dumps(asdict(call)) + "\n")

    def read_all(self) -> list[Call]:
        """Read all calls from the registry."""
        if not self.path.exists():
            return []
        calls = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    calls.append(Call(**data))
        return calls

    def create_call(
        self,
        origin: str,
        symbol: str,
        side: str,
        entry_rule: str,
        stop: float,
        target: float,
        horizon_days: int,
        rationale: str,
        snapshot_id: str,
    ) -> Call:
        """Create and append a new call."""
        call = Call(
            id=str(uuid.uuid4())[:8],
            created_at=datetime.utcnow().isoformat() + "Z",
            origin=origin,
            symbol=symbol,
            side=side,
            entry_rule=entry_rule,
            stop=stop,
            target=target,
            horizon_days=horizon_days,
            rationale=rationale,
            snapshot_id=snapshot_id,
        )
        self.append(call)
        return call


if __name__ == "__main__":
    # Quick test
    registry = CallRegistry(Path("research/calls.jsonl"))
    call = registry.create_call(
        origin="scan",
        symbol="RELIANCE",
        side="LONG",
        entry_rule="Close > 20EMA",
        stop=2400.0,
        target=2600.0,
        horizon_days=10,
        rationale="Trend follow on daily\nVIX below 15",
        snapshot_id="snap_20261108_090000",
    )
    print(f"Created call: {call.id}")
    all_calls = registry.read_all()
    print(f"Total calls: {len(all_calls)}")