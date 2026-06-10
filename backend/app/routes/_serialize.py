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


def drg_to_dict(d: models.DrgResult) -> dict:
    return {
        "drg": d.drg, "title": d.title, "mdc": d.mdc, "mdc_title": d.mdc_title,
        "drg_type": d.drg_type, "severity": d.severity, "weight": d.weight,
        "pdx": d.pdx, "or_procedure": d.or_procedure, "cc_mcc_drivers": d.cc_mcc_drivers,
        "trace": d.trace, "resolved": d.resolved,
    }


def hcc_to_dict(h: models.HccResult) -> dict:
    return {
        "raf": h.raf, "demographic": h.demographic, "hccs": h.hccs,
        "suppressed": h.suppressed, "unmapped": h.unmapped,
        "trace": h.trace, "resolved": h.resolved,
    }


def anes_to_dict(a: models.AnesResult) -> dict:
    return {
        "code": a.code, "base_units": a.base_units, "time_minutes": a.time_minutes,
        "time_units": a.time_units, "phys_modifier": a.phys_modifier, "phys_units": a.phys_units,
        "qual_circ": a.qual_circ, "total_units": a.total_units,
        "conversion_factor": a.conversion_factor, "estimated_allowable": a.estimated_allowable,
        "trace": a.trace, "resolved": a.resolved,
    }


def apc_to_dict(p: models.ApcResult) -> dict:
    return {
        "lines": p.lines, "packaged": p.packaged, "not_covered": p.not_covered,
        "facility_total": p.facility_total, "trace": p.trace, "resolved": p.resolved,
    }


def run_to_dict(run: models.CodingRun) -> dict:
    modified = bool(
        run.escalated
        or run.routing_reason.startswith("Reassigned")
        or any(c.is_overridden or c.accepted_by for c in run.codes)
    )
    return {
        "modified": modified,
        "id": run.id, "encounter_id": run.encounter_id, "status": run.status,
        "routing_lane": run.routing_lane, "routing_reason": run.routing_reason,
        "model_version": run.model_version, "chart_summary": run.chart_summary,
        "eligibility": run.eligibility, "stage_log": run.stage_log,
        "overall_confidence": run.overall_confidence, "accuracy_estimate": run.accuracy_estimate,
        "latency_ms": run.latency_ms, "escalated": run.escalated, "escalated_to": run.escalated_to,
        "assigned_to": run.assigned_to, "priority": run.priority,
        "drg": drg_to_dict(run.drg_result) if run.drg_result else None,
        "hcc": hcc_to_dict(run.hcc_result) if run.hcc_result else None,
        "anes": anes_to_dict(run.anes_result) if run.anes_result else None,
        "apc": apc_to_dict(run.apc_result) if run.apc_result else None,
        "codes": [code_to_dict(c) for c in sorted(run.codes, key=lambda x: (x.code_system, x.sequence))],
    }
