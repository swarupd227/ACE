"""Shared serialization helpers."""
from __future__ import annotations

from .. import models


def code_to_dict(c: models.CodeResult) -> dict:
    return {
        "id": c.id, "code_system": c.code_system, "code": c.code, "description": c.description,
        "role": c.role, "modifiers": c.modifiers, "sequence": c.sequence,
        "confidence": c.confidence, "conf_doc_match": c.conf_doc_match,
        "conf_historical": c.conf_historical, "conf_rule": c.conf_rule, "conf_model": c.conf_model,
        "chart_citations": c.chart_citations, "guideline_citations": c.guideline_citations,
        "rule_justification": c.rule_justification, "gate_results": c.gate_results,
        "status": c.status, "is_overridden": c.is_overridden, "override_code": c.override_code,
        "override_reason": c.override_reason, "accepted_by": c.accepted_by,
        "learning_applied": c.learning_applied,
    }


def run_to_dict(run: models.CodingRun) -> dict:
    return {
        "id": run.id, "encounter_id": run.encounter_id, "status": run.status,
        "routing_lane": run.routing_lane, "routing_reason": run.routing_reason,
        "model_version": run.model_version, "chart_summary": run.chart_summary,
        "eligibility": run.eligibility, "stage_log": run.stage_log,
        "overall_confidence": run.overall_confidence, "accuracy_estimate": run.accuracy_estimate,
        "latency_ms": run.latency_ms,
        "codes": [code_to_dict(c) for c in sorted(run.codes, key=lambda x: (x.code_system, x.sequence))],
    }
