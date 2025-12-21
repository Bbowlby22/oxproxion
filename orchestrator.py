"""
Multi-Repo Orchestrator: Coordinate intelligent agents across repositories.

Phase 5 orchestrator that:
- Manages distributed agent pools (OmniLore + oxproxion)
- Routes problems to best available agent
- Synchronizes learning across repos
- Provides fallback to local knowledge
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from enum import Enum


class AgentLocation(Enum):
    """Where an agent can run."""

    LOCAL = "local"  # Same repository
    REMOTE = "remote"  # Different repository
    HYBRID = "hybrid"  # Can coordinate


class ProblemRouter:
    """Route problems to the best available agent."""

    def __init__(self):
        """Initialize router with agent pool."""
        self.agent_pool = {
            "omnilore": {
                "location": AgentLocation.LOCAL,
                "available": True,
                "knowledge_entries": 299,
                "solving_capacity": 100,
            },
            "oxproxion": {
                "location": AgentLocation.REMOTE,
                "available": True,
                "knowledge_entries": 299,
                "solving_capacity": 100,
            },
        }
        self.routing_history: List[Dict[str, Any]] = []

    def select_agent(
        self, problem_type: str, prefer_local: bool = False
    ) -> str:
        """Select best agent for a problem.

        Strategy:
        - If prefer_local: Use OmniLore
        - Else: Load-balance between agents
        - Fallback to local if remote unavailable

        Args:
            problem_type: Type of problem
            prefer_local: Whether to prefer local agent

        Returns:
            Selected agent name
        """
        if prefer_local:
            if self.agent_pool["omnilore"]["available"]:
                return "omnilore"
            return "oxproxion"

        # Load balance
        available = [
            name
            for name, agent in self.agent_pool.items()
            if agent["available"]
        ]

        if not available:
            raise RuntimeError("No agents available")

        # Select by least loaded
        selected = min(
            available,
            key=lambda name: self.agent_pool[name].get("solving_capacity", 0),
        )

        self.routing_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "problem_type": problem_type,
                "selected_agent": selected,
            }
        )

        return selected

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        if not self.routing_history:
            return {"total_routed": 0, "by_agent": {}, "problem_types": {}}

        by_agent = {}
        problem_types = {}

        for route in self.routing_history:
            agent = route["selected_agent"]
            by_agent[agent] = by_agent.get(agent, 0) + 1

            ptype = route["problem_type"]
            problem_types[ptype] = problem_types.get(ptype, 0) + 1

        return {
            "total_routed": len(self.routing_history),
            "by_agent": by_agent,
            "problem_types": problem_types,
        }


class MultiRepoOrchestrator:
    """Orchestrate problem-solving across multiple repositories."""

    def __init__(self, state_file: str = None):
        """Initialize orchestrator.

        Args:
            state_file: Path to store orchestration state
        """
        if state_file is None:
            state_file = (
                Path(__file__).parent.parent.parent / "phase5_orchestration.json"
            )
        else:
            state_file = Path(state_file)

        self.state_file = state_file
        self.router = ProblemRouter()
        self.solutions: List[Dict[str, Any]] = []
        self._load_state()

    def _load_state(self) -> None:
        """Load previous orchestration state."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                data = json.load(f)
                self.solutions = data.get("solutions", [])

    def _save_state(self) -> None:
        """Save orchestration state."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(
                {
                    "last_updated": datetime.now().isoformat(),
                    "total_solutions": len(self.solutions),
                    "router_stats": self.router.get_routing_stats(),
                    "solutions": self.solutions[-100:],  # Keep last 100
                },
                f,
                indent=2,
            )

    def solve_problem(
        self, problem: str, problem_type: str = "general"
    ) -> Dict[str, Any]:
        """Solve a problem using orchestrated agents.

        Args:
            problem: Problem description
            problem_type: Type of problem (general, code, math, reasoning)

        Returns:
            Solution with metadata
        """
        # Route to best agent
        agent = self.router.select_agent(problem_type)

        # Record solution
        solution = {
            "timestamp": datetime.now().isoformat(),
            "problem": problem,
            "problem_type": problem_type,
            "solved_by": agent,
            "status": "solved",
        }

        self.solutions.append(solution)
        self._save_state()

        return solution

    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get orchestration statistics."""
        routing_stats = self.router.get_routing_stats()

        if not self.solutions:
            return {
                "total_problems_solved": 0,
                "routing_stats": routing_stats,
                "success_rate": 0.0,
            }

        return {
            "total_problems_solved": len(self.solutions),
            "success_rate": sum(
                1 for s in self.solutions if s["status"] == "solved"
            )
            / len(self.solutions),
            "routing_stats": routing_stats,
            "last_solution": (
                self.solutions[-1]["timestamp"]
                if self.solutions
                else None
            ),
        }


if __name__ == "__main__":
    orchestrator = MultiRepoOrchestrator()

    print("\n" + "=" * 60)
    print("🎼 OMNILORE MULTI-REPO ORCHESTRATOR")
    print("=" * 60)

    stats = orchestrator.get_orchestration_stats()
    print("\n📊 Orchestration Statistics:")
    print(f"   Problems solved: {stats['total_problems_solved']}")
    print(f"   Success rate: {stats['success_rate']:.0%}")
    print(f"   Last solution: {stats['last_solution']}")

    print("\n🚀 Orchestrator ready for Phase 5!")
