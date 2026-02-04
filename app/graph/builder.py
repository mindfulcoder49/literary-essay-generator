from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from app.graph.nodes import (
    discover_themes_node,
    draft_essay_node,
    expand_context_node,
    ingest_node,
    persist_results_node,
    retrieve_evidence_node,
    review_essay_node,
    revise_essay_node,
    summarize_book_node,
    write_theme_intros_node,
)
from app.graph.state import EssayGraphState


def _should_revise(state: EssayGraphState) -> str:
    if state.get("essay_approved", False):
        return "persist"
    if state.get("revision_count", 0) >= 2:
        return "persist"
    return "revise"


def build_essay_graph() -> StateGraph:
    graph = StateGraph(EssayGraphState)

    graph.add_node("ingest", ingest_node)
    graph.add_node("summarize_book", summarize_book_node)
    graph.add_node("discover_themes", discover_themes_node)
    graph.add_node("retrieve_evidence", retrieve_evidence_node)
    graph.add_node("expand_context", expand_context_node)
    graph.add_node("write_theme_intros", write_theme_intros_node)
    graph.add_node("draft_essay", draft_essay_node)
    graph.add_node("review_essay", review_essay_node)
    graph.add_node("revise_essay", revise_essay_node)
    graph.add_node("persist_results", persist_results_node)

    graph.add_edge(START, "ingest")
    graph.add_edge("ingest", "summarize_book")
    graph.add_edge("summarize_book", "discover_themes")
    graph.add_edge("discover_themes", "retrieve_evidence")
    graph.add_edge("retrieve_evidence", "expand_context")
    graph.add_edge("expand_context", "write_theme_intros")
    graph.add_edge("write_theme_intros", "draft_essay")
    graph.add_edge("draft_essay", "review_essay")

    graph.add_conditional_edges(
        "review_essay",
        _should_revise,
        {"persist": "persist_results", "revise": "revise_essay"},
    )

    graph.add_edge("revise_essay", "review_essay")
    graph.add_edge("persist_results", END)

    return graph.compile()
