"""
Knowledge Exporter: Export OmniLore tribal knowledge for distribution.

Enables Phase 5 by exporting all 299 knowledge entries in a portable format
that can be imported into oxproxion and other repositories.
"""

import json
import chromadb
from pathlib import Path
from typing import Dict, Any


class KnowledgeExporter:
    """Export tribal knowledge from ChromaDB to portable JSON format."""

    def __init__(self, knowledge_path: str = "/mnt/omnilore-store"):
        """Initialize exporter with ChromaDB path."""
        self.client = chromadb.PersistentClient(path=knowledge_path)
        self.collection = self.client.get_collection("omnilore_tribal_knowledge")

    def export_all(self, output_file: str = None) -> str:
        """Export all knowledge entries to JSON.

        Args:
            output_file: Path to save JSON export (default: phase5_knowledge.json)

        Returns:
            Path to exported file
        """
        if output_file is None:
            output_file = (
                Path(__file__).parent.parent.parent / "phase5_knowledge.json"
            )
        else:
            output_file = Path(output_file)

        # Paginate through all entries
        all_entries = []
        batch_size = 100
        offset = 0

        while True:
            results = self.collection.get(
                include=["documents", "metadatas"],
                limit=batch_size,
                offset=offset,
            )

            if not results["ids"]:
                break

            for id_, doc, meta in zip(
                results["ids"], results["documents"], results["metadatas"]
            ):
                all_entries.append(
                    {
                        "id": id_,
                        "query": meta.get("query", ""),
                        "response": doc,
                        "category": meta.get("category", "unknown"),
                        "confidence": meta.get("confidence", 0.0),
                        "created_at": meta.get("created_at", ""),
                    }
                )

            offset += len(results["ids"])

        # Write to JSON
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(
                {
                    "version": "1.0",
                    "timestamp": str(Path(__file__).stat().st_mtime),
                    "total_entries": len(all_entries),
                    "entries": all_entries,
                },
                f,
                indent=2,
            )

        return str(output_file)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of knowledge to be exported."""
        results = self.collection.get(include=["metadatas"])

        categories = {}
        for meta in results["metadatas"]:
            cat = meta.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_entries": self.collection.count(),
            "categories": categories,
            "min_confidence": min(
                (m.get("confidence", 0.0) for m in results["metadatas"]), default=0.0
            ),
            "avg_confidence": (
                sum(m.get("confidence", 0.0) for m in results["metadatas"])
                / len(results["metadatas"])
                if results["metadatas"]
                else 0.0
            ),
        }


if __name__ == "__main__":
    exporter = KnowledgeExporter()

    print("\n" + "=" * 60)
    print("📦 OMNILORE KNOWLEDGE EXPORTER")
    print("=" * 60)

    summary = exporter.get_summary()
    print("\n📊 Knowledge Summary:")
    print(f"   Total entries: {summary['total_entries']}")
    print(f"   Avg confidence: {summary['avg_confidence']:.2f}")
    print(f"   Categories: {len(summary['categories'])}")
    for cat, count in sorted(summary["categories"].items(), key=lambda x: -x[1])[:5]:
        print(f"     - {cat}: {count}")

    output_path = exporter.export_all()
    print(f"\n✅ Knowledge exported to: {output_path}")
    print("✅ Ready for Phase 5 distribution!")
