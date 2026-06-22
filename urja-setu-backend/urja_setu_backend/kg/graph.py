"""Knowledge graph over the crude supply network (NetworkX).

Nodes: country, source, grade, corridor, refinery.
Edges: produces, is_grade, ships_via, compatible.

The graph powers procurement: given a blocked corridor, find sources whose route
avoids it and whose grade is accepted by the exposed refineries, ranked by
delivered cost and transit time.
"""

from __future__ import annotations

import networkx as nx

from urja_setu_backend.kg import data

_graph: nx.DiGraph | None = None


def build_graph() -> nx.DiGraph:
    g = nx.DiGraph()
    for s in data.CRUDE_SOURCES:
        g.add_node(("source", s["id"]), ntype="source", **s)
        g.add_node(("country", s["country"]), ntype="country")
        g.add_node(("grade", s["grade"]), ntype="grade")
        g.add_node(("corridor", s["corridor"]), ntype="corridor")
        g.add_edge(("country", s["country"]), ("source", s["id"]), rel="produces")
        g.add_edge(("source", s["id"]), ("grade", s["grade"]), rel="is_grade")
        g.add_edge(("source", s["id"]), ("corridor", s["corridor"]), rel="ships_via")
    for rid, slate in data.REFINERY_SLATES.items():
        g.add_node(("refinery", rid), ntype="refinery")
        for grade in slate:
            g.add_node(("grade", grade), ntype="grade")
            g.add_edge(("grade", grade), ("refinery", rid), rel="compatible")
    return g


def graph() -> nx.DiGraph:
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def stats() -> dict:
    g = graph()
    return {"nodes": g.number_of_nodes(), "edges": g.number_of_edges()}


def alternative_sources(blocked_corridor: str, brent_usd: float | None = None) -> list[dict]:
    """Rank crude sources whose route avoids `blocked_corridor`.

    Compatibility is checked against the refineries exposed to the blocked corridor
    (falls back to all refineries). Ranking: compatible first, then delivered cost,
    then transit time.
    """
    g = graph()
    exposed = set(data.CORRIDOR_REFINERIES.get(blocked_corridor, []))
    targets = exposed or set(data.REFINERY_SLATES)

    results: list[dict] = []
    for s in data.CRUDE_SOURCES:
        if s["corridor"] == blocked_corridor:
            continue  # this source's route uses the blocked corridor

        # Which exposed refineries can take this grade (graph adjacency).
        grade_node = ("grade", s["grade"])
        accepting = {
            r for (_, (_, r)) in g.out_edges(grade_node)  # ('grade',g)->('refinery',r)
            if g.nodes[("refinery", r)]["ntype"] == "refinery"
        } if g.has_node(grade_node) else set()
        compat_refineries = sorted(targets & accepting)

        freight = round(s["transit_days"] * data.FREIGHT_USD_PER_DAY, 2)
        delivered = round(s["spot_usd"] + freight, 2)
        results.append(
            {
                **s,
                "freight_usd": freight,
                "delivered_usd_bbl": delivered,
                "grade_compatible": bool(compat_refineries),
                "compat_refineries": compat_refineries,
                "route_label": data.ROUTE_LABEL.get(s["corridor"], s["corridor"]),
            }
        )

    results.sort(key=lambda x: (not x["grade_compatible"], x["delivered_usd_bbl"], x["transit_days"]))
    return results
