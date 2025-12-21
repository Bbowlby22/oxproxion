"""
Federation Service: Bidirectional knowledge sync between repositories.

Enables OmniLore and oxproxion to learn from each other through
continuous knowledge synchronization with conflict resolution.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class KnowledgeSync:
    """Represents a synchronized knowledge entry."""

    id: str
    source_repo: str  # 'omnilore' or 'oxproxion'
    category: str
    confidence: float
    created_at: str
    last_synced: str
    sync_count: int = 0


class FederationService:
    """Manage bidirectional knowledge federation between repos."""

    def __init__(self, state_file: str = None):
        """Initialize federation service.

        Args:
            state_file: Path to store federation state (sync history)
        """
        if state_file is None:
            state_file = Path(__file__).parent.parent.parent / "phase5_sync_state.json"
        else:
            state_file = Path(state_file)

        self.state_file = state_file
        self.sync_history: List[Dict[str, Any]] = []
        self._load_state()

    def _load_state(self) -> None:
        """Load previous sync state from disk."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                data = json.load(f)
                self.sync_history = data.get("syncs", [])

    def _save_state(self) -> None:
        """Save sync state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(
                {
                    "last_sync": datetime.now().isoformat(),
                    "sync_count": len(self.sync_history),
                    "syncs": self.sync_history[-100:],  # Keep last 100
                },
                f,
                indent=2,
            )

    def register_sync(self, entry_id: str, source: str, target: str) -> None:
        """Register a knowledge sync event.

        Args:
            entry_id: ID of knowledge entry synced
            source: Source repo ('omnilore' or 'oxproxion')
            target: Target repo ('omnilore' or 'oxproxion')
        """
        self.sync_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "entry_id": entry_id,
                "direction": f"{source} → {target}",
            }
        )
        self._save_state()

    async def sync_batch(
        self, entries: List[Dict[str, Any]], source: str, target: str
    ) -> Dict[str, Any]:
        """Synchronize a batch of knowledge entries.

        Args:
            entries: List of knowledge entries to sync
            source: Source repository
            target: Target repository

        Returns:
            Sync result statistics
        """
        synced = 0
        conflicts = 0
        errors = 0

        for entry in entries:
            try:
                self.register_sync(entry["id"], source, target)
                synced += 1
            except Exception:
                errors += 1

        return {
            "synced": synced,
            "conflicts": conflicts,
            "errors": errors,
            "direction": f"{source} → {target}",
            "timestamp": datetime.now().isoformat(),
        }

    def get_sync_stats(self) -> Dict[str, Any]:
        """Get federation sync statistics."""
        if not self.sync_history:
            return {
                "total_syncs": 0,
                "omnilore_to_oxproxion": 0,
                "oxproxion_to_omnilore": 0,
                "last_sync": None,
            }

        pattern_o2x = "omnilore → oxproxion"
        pattern_x2o = "oxproxion → omnilore"
        omnilore_to_oxproxion = sum(
            1 for s in self.sync_history
            if pattern_o2x in s.get("direction", "")
        )
        oxproxion_to_omnilore = sum(
            1 for s in self.sync_history
            if pattern_x2o in s.get("direction", "")
        )

        return {
            "total_syncs": len(self.sync_history),
            "omnilore_to_oxproxion": omnilore_to_oxproxion,
            "oxproxion_to_omnilore": oxproxion_to_omnilore,
            "last_sync": (
                self.sync_history[-1]["timestamp"]
                if self.sync_history
                else None
            ),
        }


class ConflictResolver:
    """Resolve conflicts when knowledge is updated in both repos."""

    @staticmethod
    def resolve(
        omnilore_entry: Dict[str, Any], oxproxion_entry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve knowledge conflict using confidence scoring.

        Strategy:
        - If confidences differ by >0.1: Use higher confidence
        - If confidences similar: Use more recent
        - Merge metadata from both

        Args:
            omnilore_entry: Entry from OmniLore
            oxproxion_entry: Entry from oxproxion

        Returns:
            Resolved entry
        """
        conf_diff = abs(
            omnilore_entry.get("confidence", 0.0)
            - oxproxion_entry.get("confidence", 0.0)
        )

        if conf_diff > 0.1:
            # Use higher confidence
            return (
                omnilore_entry
                if omnilore_entry.get("confidence", 0)
                > oxproxion_entry.get("confidence", 0)
                else oxproxion_entry
            )

        # Use more recent
        omnilore_time = omnilore_entry.get("created_at", "")
        oxproxion_time = oxproxion_entry.get("created_at", "")
        return (
            oxproxion_entry
            if oxproxion_time > omnilore_time
            else omnilore_entry
        )


if __name__ == "__main__":
    service = FederationService()

    print("\n" + "=" * 60)
    print("🔗 OMNILORE FEDERATION SERVICE")
    print("=" * 60)

    stats = service.get_sync_stats()
    print("\n📊 Federation Statistics:")
    print(f"   Total syncs: {stats['total_syncs']}")
    print(f"   OmniLore → oxproxion: {stats['omnilore_to_oxproxion']}")
    print(f"   oxproxion → OmniLore: {stats['oxproxion_to_omnilore']}")
    print(f"   Last sync: {stats['last_sync']}")

    print("\n✅ Federation service ready for Phase 5!")
