"""Ragas adapter seam (E8 follow-up).

Ragas computes RAG-QA metrics (faithfulness, context precision/recall, answer relevancy) using
a judge LLM. Those fit retrieval-grounded QA more than code-assignment accuracy, so the
platform's PRIMARY, code-appropriate metrics are precision/recall/F1 against adjudicated truth
(computed in the eval harness). This module is the integration point: once the judge model /
Azure setup is decided, implement `score()` to run ragas over the (chart, retrieved_context,
rationale) triples. Until then it reports availability honestly — no fabricated scores.
"""
from __future__ import annotations


def available() -> bool:
    try:
        import ragas  # noqa: F401
        return True
    except Exception:
        return False


def score(cases: list | None = None) -> dict:
    """Seam — returns Ragas metrics when wired; otherwise an honest 'not available' marker."""
    if not available():
        return {
            "available": False,
            "note": ("Ragas adapter not wired yet — primary metrics are precision/recall/F1 vs "
                     "adjudicated truth. Install `ragas` + configure a judge model to enable "
                     "faithfulness / context-precision metrics on the retrieval+rationale."),
        }
    return {"available": True,
            "note": "ragas installed — implement score() to compute faithfulness / context metrics"}
