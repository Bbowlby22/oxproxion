"""
Knowledge Importer: Import tribal knowledge into any repository.

Enables Phase 5 by allowing oxproxion and other repos to import
OmniLore's 299 knowledge entries into their own ChromaDB instances.
"""

import json
import chromadb
from pathlib import Path
from typing import Dict, Any


class KnowledgeImporter:
    """Import tribal knowledge from JSON into ChromaDB."""

    def __init__(self, knowledge_path: str = None):
        """Initialize importer with ChromaDB path.

        Args:
            knowledge_path: Path to ChromaDB (default: repo-specific)
        """
        if knowledge_path is None:
            knowledge_path = (
                Path(__file__).parent.parent.parent / "data" / "chromadb"
            )

        self.knowledge_path = Path(knowledge_path)
        self.knowledge_path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.knowledge_path))

        # Create collection if it doesn't exist
        try:
            self.collection = self.client.get_collection(
                "omnilore_tribal_knowledge"
            )
        except Exception:
            self.collection = self.client.create_collection(
                name="omnilore_tribal_knowledge",
                metadata={"description": "Distributed tribal knowledge"},
            )

    def import_from_file(self, json_file: str) -> Dict[str, Any]:
        """Import knowledge from JSON file.

        Args:
            json_file: Path to phase5_knowledge.json

        Returns:
            Import statistics
        """
        json_path = Path(json_file)
        if not json_path.exists():
            raise FileNotFoundError(f"Knowledge file not found: {json_file}")

        with open(json_path) as f:
            data = json.load(f)

        entries = data.get("entries", [])
        if not entries:
            raise ValueError("No entries found in knowledge file")

        # Import in batches
        ids = []
        documents = []
        metadatas = []

        for entry in entries:
            ids.append(entry["id"])
            documents.append(entry["response"])
            metadatas.append(
                {
                    "query": entry.get("query", ""),
                    "category": entry.get("category", "unknown"),
                    "confidence": entry.get("confidence", 0.0),
                    "created_at": entry.get("created_at", ""),
                    "imported_from": "omnilore",
                }
            )

        # Add to collection
        self.collection.add(ids=ids, documents=documents, metadatas=metadatas)

        return {
            "imported_entries": len(entries),
            "total_in_collection": self.collection.count(),
            "knowledge_path": str(self.knowledge_path),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of imported knowledge."""
        try:
            results = self.collection.get(include=["metadatas"])
        except Exception:
            return {"total_entries": 0, "categories": {}, "status": "empty"}

        categories = {}
        for meta in results["metadatas"]:
            cat = meta.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_entries": self.collection.count(),
            "categories": categories,
            "avg_confidence": (
                sum(m.get("confidence", 0.0) for m in results["metadatas"])
                / len(results["metadatas"])
                if results["metadatas"]
                else 0.0
            ),
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python knowledge_importer.py <path_to_knowledge.json>")
        sys.exit(1)

    importer = KnowledgeImporter()

    print("\n" + "=" * 60)
    print("📚 OMNILORE KNOWLEDGE IMPORTER")
    print("=" * 60)

    result = importer.import_from_file(sys.argv[1])
    print("\n✅ Import successful!")
    print(f"   Imported: {result['imported_entries']} entries")
    print(f"   Total in collection: {result['total_in_collection']}")
    print(f"   Storage: {result['knowledge_path']}")

    summary = importer.get_summary()
    print("\n📊 Knowledge Summary:")
    print(f"   Total entries: {summary['total_entries']}")
    print(f"   Avg confidence: {summary['avg_confidence']:.2f}")
    print(f"   Categories: {len(summary['categories'])}")
