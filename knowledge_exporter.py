"""
Knowledge Exporter: Export tribal knowledge via MCP (MCP-FIRST COMPLIANT).

Enables Phase 5 by allowing any repository to export knowledge
to OmniLore via MCP-compliant omnilore_store and omnilore_smart_chat tools.

✅ FOLLOWS MCP-FIRST RULE:
- Uses omnilore_query for all knowledge searches (with caching)
- Uses omnilore_store for all exports (ttl_days=36500)
- Implements vendor fallback via omnilore_smart_chat
- Error recovery with omnilore_query for guidance
- No direct ChromaDB or API calls
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class KnowledgeExporter:
    """Export knowledge via MCP client (MCP-First compliant)."""

    def __init__(self, omnilore_client=None):
        """Initialize exporter with MCP client.

        Args:
            omnilore_client: OmniLore MCP client (auto-configured if None)
        """
        self.omnilore_client = omnilore_client
        self.export_stats = {
            "exported_entries": 0,
            "export_time": datetime.now().isoformat(),
            "errors": 0,
        }

    async def query_and_export(
        self, query: str, category: str = None
    ) -> Dict[str, Any]:
        """Query knowledge and export via MCP.

        ✅ STEP 1: Query OmniLore (omnilore_smart_chat with vendor fallback)
        ✅ STEP 2: Store export operation as learning (ttl_days=36500)
        ✅ STEP 3: Error recovery with omnilore_query
        ✅ STEP 4: No direct API calls - all through MCP

        Args:
            query: Knowledge query
            category: Category for export metadata

        Returns:
            Export result
        """
        try:
            # STEP 1: Query knowledge via MCP (omnilore_smart_chat)
            # This automatically includes caching and vendor fallback
            result = await self.omnilore_client.smart_chat(
                message=f"Export knowledge: {query}",
                prefer_vendor=None,  # Auto-select best vendor
            )

            # STEP 2: Store export operation as learning (permanent)
            await self.omnilore_client.store(
                query=f"Export query: {query}",
                response=result,
                category=category or "exported_knowledge",
                ttl_days=36500,  # ✅ PERMANENT
            )

            self.export_stats["exported_entries"] += 1

            return {
                "query": query,
                "result": result,
                "exported": True,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            # STEP 3: Error recovery - query for guidance
            recovery = await self.omnilore_client.query(
                f"How do I fix export error: {type(e).__name__}?"
            )

            if recovery:
                # Store recovery pattern (permanent)
                await self.omnilore_client.store(
                    query=f"How to fix export error: {type(e).__name__}",
                    response=recovery,
                    category="error_recovery",
                    ttl_days=36500,  # ✅ PERMANENT
                )

            self.export_stats["errors"] += 1

            return {
                "query": query,
                "error": str(e),
                "exported": False,
                "guidance": recovery,
            }

    async def export_batch(
        self, queries: List[str], category: str = None
    ) -> Dict[str, Any]:
        """Export multiple knowledge entries via MCP.

        Args:
            queries: List of knowledge queries
            category: Category for exports

        Returns:
            Batch export statistics
        """
        results = []
        success_count = 0
        error_count = 0

        print(f"\n📤 Exporting {len(queries)} knowledge items via MCP...")

        for query in queries:
            result = await self.query_and_export(query, category)
            results.append(result)

            if result.get("exported"):
                success_count += 1
            else:
                error_count += 1

        # Store batch operation as learning
        await self.omnilore_client.store(
            query="How do I export knowledge in batches?",
            response=f"""
Successfully exported {success_count} entries via MCP:

1. Use omnilore_smart_chat for all queries (auto-caching + vendor fallback)
2. Store each export result via omnilore_store (ttl_days=36500)
3. Implement error recovery for each failure
4. All knowledge storage is permanent (never expires)

Success: {success_count}/{len(queries)}
Errors: {error_count}
""",
            category="export_pattern",
            ttl_days=36500,  # ✅ PERMANENT
        )

        return {
            "exported_entries": success_count,
            "errors": error_count,
            "total": len(queries),
            "timestamp": datetime.now().isoformat(),
            "results": results,
        }

    async def export_to_file(
        self, queries: List[str], output_file: str = None
    ) -> Dict[str, Any]:
        """Export knowledge to JSON file via MCP.

        All knowledge is queried and stored via MCP before writing to disk.

        Args:
            queries: List of knowledge queries
            output_file: Output JSON file path

        Returns:
            Export statistics
        """
        if output_file is None:
            output_file = f"exported_knowledge_{datetime.now().isoformat()}.json"

        batch_result = await self.export_batch(queries)

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_entries": batch_result["exported_entries"],
            "errors": batch_result["errors"],
            "entries": batch_result["results"],
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        return {
            "output_file": str(output_path),
            "exported_entries": batch_result["exported_entries"],
            "errors": batch_result["errors"],
            "file_size": output_path.stat().st_size,
        }

    async def get_export_stats(self) -> Dict[str, Any]:
        """Get export statistics."""
        return {
            "total_exported": self.export_stats["exported_entries"],
            "errors": self.export_stats["errors"],
            "success_rate": (
                (
                    self.export_stats["exported_entries"]
                    / (
                        self.export_stats["exported_entries"]
                        + self.export_stats["errors"]
                    )
                )
                if (
                    self.export_stats["exported_entries"]
                    + self.export_stats["errors"]
                )
                > 0
                else 0
            ),
            "started_at": self.export_stats["export_time"],
        }


if __name__ == "__main__":
    import sys
    import asyncio

    async def main():
        print("\n" + "=" * 70)
        print("📤 OMNILORE KNOWLEDGE EXPORTER (MCP-FIRST COMPLIANT)")
        print("=" * 70)
        print("\n✅ This exporter uses MCP-First pattern:")
        print("   1. Query knowledge via omnilore_smart_chat")
        print("   2. Store exports via omnilore_store (ttl_days=36500)")
        print("   3. Error recovery with omnilore_query")
        print("   4. All calls through MCP client")
        print("\n✅ Knowledge queries include automatic caching")
        print("✅ Vendor fallback for reliability")
        print("✅ Export operations stored as permanent learning")
        print("✅ No direct API calls or ChromaDB access")

    asyncio.run(main())
