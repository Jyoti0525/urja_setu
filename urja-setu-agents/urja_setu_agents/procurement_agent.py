"""Procurement Orchestrator — a LangGraph state machine.

    query (knowledge graph)  ->  rank (deterministic)  ->  rationale (LLM)

Like the Risk Agent, ingestion/graph access is injected, so this stays decoupled
from the backend. Numbers (cost, transit, compatibility, ranking) are deterministic;
the LLM only writes the human-readable rationale.
"""

from __future__ import annotations

from typing import Callable, TypedDict

from langgraph.graph import END, START, StateGraph

from urja_setu_agents.llm import LLMClient


class ProcState(TypedDict, total=False):
    blocked: str
    brent: float | None
    scenario_label: str
    candidates: list[dict]
    ranked: list[dict]
    rationales: dict[str, str]


QueryFn = Callable[[str, float | None], list[dict]]


def build_procurement_graph(llm: LLMClient, query_fn: QueryFn, *, top_n: int = 4):
    """Compile the Procurement Orchestrator graph."""

    def query_node(state: ProcState) -> dict:
        return {"candidates": query_fn(state["blocked"], state.get("brent"))}

    def rank_node(state: ProcState) -> dict:
        return {"ranked": (state.get("candidates") or [])[:top_n]}

    def rationale_node(state: ProcState) -> dict:
        return {
            "rationales": llm.procurement_rationales(
                state.get("scenario_label", ""), state.get("ranked", [])
            )
        }

    graph = StateGraph(ProcState)
    graph.add_node("query", query_node)
    graph.add_node("rank", rank_node)
    graph.add_node("rationale", rationale_node)
    graph.add_edge(START, "query")
    graph.add_edge("query", "rank")
    graph.add_edge("rank", "rationale")
    graph.add_edge("rationale", END)
    return graph.compile()
