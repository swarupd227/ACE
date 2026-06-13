"""P2R API — Phase 0/1 skeleton.

Proves the platform structure: a standalone FastAPI service that boots in isolation
and consumes the shared `core/` package (LLM client + canonical IR). No phase logic
yet — that lands in Phases 2+ (policy ingestion → validation → authoring).
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# One-way reuse: P2R imports the shared core. Nothing here touches the ACE app.
from core import llm_client
from core.ir import Artifact, ArtifactType, Citation, Provenance

app = FastAPI(title="P2R — Policy-to-Rule Intelligence (Nous RCM Framework)", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "p2r", "shared_core": "linked"}


@app.get("/meta")
def meta() -> dict:
    """Confirms the reused core is wired: reports the active model and whether the
    LLM backend is reachable, using the same client ACE runs on."""
    return {
        "platform": "Nous RCM Intelligence Framework",
        "module": "P2R — Policy-to-Rule",
        "phases": ["P1 ingestion", "P2 denial discovery", "P3 validation", "P4 authoring"],
        "shared_core": ["llm_client", "ir"],
        "llm_available": llm_client.llm_available(),
        "llm_model": llm_client.model_version(),
        "ir_artifact_types": [t.value for t in ArtifactType],
    }


@app.get("/ir/example")
def ir_example() -> dict:
    """A tiny demonstration that a P2R rule and an ACE code are the same IR shape."""
    rule = Artifact(
        artifact_type=ArtifactType.RULE,
        payload={"verdict": "NET-NEW", "summary": "(skeleton — real rules land in Phase 4)"},
        citations=[Citation(source_id="demo-policy", char_start=0, char_end=10, text="(placeholder)")],
        provenance=Provenance(model_version=llm_client.model_version()),
        confidence=0.0,
        resolved=False,
    )
    return rule.model_dump(mode="json")
