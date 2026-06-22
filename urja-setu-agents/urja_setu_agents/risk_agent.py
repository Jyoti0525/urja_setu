"""Risk Intelligence Agent — a LangGraph state machine.

    fetch  ->  extract (LLM)  ->  score (deterministic)

The agent stays decoupled from the backend: ingestion and scoring are injected
as callables, so this library has no backend dependency (clean layering).
"""

from __future__ import annotations

from typing import Callable, TypedDict

from langgraph.graph import END, START, StateGraph

from urja_setu_agents.llm import LLMClient


class RiskState(TypedDict, total=False):
    corridors: list[dict]
    articles: dict
    price: dict
    sanctions: dict
    extracted: dict
    scored: list[dict]


FetchFn = Callable[[list[dict]], dict]
ScoreFn = Callable[[dict], list[dict]]


def build_risk_graph(llm: LLMClient, fetch_fn: FetchFn, score_fn: ScoreFn):
    """Compile the Risk Intelligence Agent graph."""

    def fetch_node(state: RiskState) -> dict:
        # Returns {"articles": ..., "price": ..., "sanctions": ...}
        return fetch_fn(state["corridors"])

    def extract_node(state: RiskState) -> dict:
        extracted = llm.extract_corridor_risk(
            state["corridors"], state.get("articles", {}), state.get("price", {})
        )
        return {"extracted": extracted}

    def score_node(state: RiskState) -> dict:
        return {"scored": score_fn(state)}

    graph = StateGraph(RiskState)
    graph.add_node("fetch", fetch_node)
    graph.add_node("extract", extract_node)
    graph.add_node("score", score_node)
    graph.add_edge(START, "fetch")
    graph.add_edge("fetch", "extract")
    graph.add_edge("extract", "score")
    graph.add_edge("score", END)
    return graph.compile()
