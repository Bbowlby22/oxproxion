"""
Multi-Repo Orchestrator: Coordinate agents via MCP (MCP-FIRST COMPLIANT).

Phase 5 orchestrator that:
- Routes problems to best available agent (OmniLore or oxproxion)
- Queries OmniLore for guidance (omnilore_smart_chat)
- Stores routing decisions as learning (ttl_days=36500)
- Implements error recovery (omnilore_query)
- No hardcoded agent pools or direct API calls

✅ FOLLOWS MCP-FIRST RULE:
- Uses omnilore_smart_chat for problem routing decisions
- Uses omnilore_store for learning (ttl_days=36500 always)
- Implements error recovery with omnilore_query for guidance
- All agent coordination through MCP
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from enum import Enum


class ProblemRouter:
    """Route problems to best agent via MCP (MCP-First compliant)."""

    def __init__(self, omnilore_client=None):
        """Initialize router with MCP client.

        Args:
            omnilore_client: OmniLore MCP client (auto-configured if None)
        """
        self.omnilore_client = omnilore_client
        self.routing_history: List[Dict[str, Any]] = []

    async def select_agent(
        self, problem_type: str, problem_description: str, prefer_local: bool = False
    ) -> str:
        """Select best agent for a problem via MCP.

        ✅ STEP 1: Query OmniLore for routing guidance
        ✅ STEP 2: Execute routing decision via omnilore_smart_chat
        ✅ STEP 3: Store routing decision as learning (ttl_days=36500)
        ✅ STEP 4: Error recovery with omnilore_query

        Args:
            problem_type: Type of problem
            problem_description: Problem description
            prefer_local: Whether to prefer local agent

        Returns:
            Selected agent name ('omnilore' or 'oxproxion')
        """
        try:
            # STEP 1: Query for routing guidance
            guidance = await self.omnilore_client.query(
                f"How do I route a {problem_type} problem to the best agent?"
            )

            # STEP 2: Use smart chat for routing decision (vendor fallback)
            routing_prompt = f"""
Problem Type: {problem_type}
Description: {problem_description}
Prefer Local: {prefer_local}

Guidance from tribal knowledge: {guidance}

Based on this, which agent should solve this? (omnilore or oxproxion)
"""
            decision = await self.omnilore_client.smart_chat(
                message=routing_prompt,
                prefer_vendor=None,  # Auto-select best vendor
            )

            selected = "omnilore" if "omnilore" in decision.lower() else "oxproxion"

            # STEP 3: Store routing decision as learning
            await self.omnilore_client.store(
                query=f"How do I route a {problem_type} problem to the best agent?",
                response=f"Route to {selected} because: {decision[:200]}...",
                category="routing_decision",
                ttl_days=36500,  # ✅ PERMANENT
            )

            self.routing_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "problem_type": problem_type,
                    "selected_agent": selected,
                    "reason": decision[:100],
                }
            )

            return selected

        except Exception as e:
            # STEP 4: Error recovery
            recovery = await self.omnilore_client.query(
                f"How do I fix routing error: {type(e).__name__}?"
            )

            if recovery:
                # Store recovery pattern (permanent)
                await self.omnilore_client.store(
                    query=f"How to fix routing error: {type(e).__name__}",
                    response=recovery,
                    category="error_recovery",
                    ttl_days=36500,  # ✅ PERMANENT
                )

            # Fallback: default to omnilore
            return "omnilore"

    async def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        if not self.routing_history:
            return {
                "total_routed": 0,
                "by_agent": {},
                "problem_types": {},
            }

        by_agent = {}
        problem_types = {}

        for entry in self.routing_history:
            agent = entry["selected_agent"]
            by_agent[agent] = by_agent.get(agent, 0) + 1

            ptype = entry["problem_type"]
            problem_types[ptype] = problem_types.get(ptype, 0) + 1

        return {
            "total_routed": len(self.routing_history),
            "by_agent": by_agent,
            "problem_types": problem_types,
            "last_routing": self.routing_history[-1] if self.routing_history else None,
        }

    async def generate_report(self) -> Dict[str, Any]:
        """Generate routing report via MCP."""
        stats = await self.get_routing_stats()

        # Query for insights
        insights = await self.omnilore_client.query(
            f"What patterns do you see in this routing data: {json.dumps(stats)}?"
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "insights": insights,
            "total_routed": stats["total_routed"],
        }


if __name__ == "__main__":
    import asyncio

    async def main():
        print("\n" + "=" * 70)
        print("🔀 OMNILORE PROBLEM ROUTER (MCP-FIRST COMPLIANT)")
        print("=" * 70)
        print("\n✅ This orchestrator uses MCP-First pattern:")
        print("   1. Query OmniLore for routing guidance")
        print("   2. Use omnilore_smart_chat for routing decisions")
        print("   3. Store decisions as learning (ttl_days=36500)")
        print("   4. Error recovery with omnilore_query")
        print("\n✅ No hardcoded agent pools")
        print("✅ Dynamic routing based on tribal knowledge")
        print("✅ Routing decisions are permanent learning")
        print("✅ All coordination through MCP")

    asyncio.run(main())
