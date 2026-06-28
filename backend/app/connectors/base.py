"""PMS/EHR connector seam (E1).

One interface every source system implements, so Practice Admin today and Epic tomorrow
look identical to the pipeline. A connector does two things:

  * pull_charts()  — inbound: fetch new charts to code
  * push_result()  — outbound: write the coded result back as a work item / billing-queue entry

The adapter has two modes:
  * "sandbox" — an in-process implementation of the EXPECTED contract, so the full round-trip
    is demonstrable before the client's API credentials exist. Clearly labelled; no live calls.
  * "live"    — real HTTP against the configured base_url with a bearer token from the
    environment (never stored in the DB). Endpoint paths / field names are the contract we
    expect and confirm in Phase-1 discovery.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class InboundChart:
    """A chart pulled from the source system, normalised to what ingestion needs."""
    external_id: str                      # the PMS's own id (order/document id) — our idempotency key
    specialty: str
    payer: str
    mrn: str = ""
    patient_name: str = "PMS Patient"
    age: int = 55
    sex: str = "F"
    modality: str = ""
    pos: str = "11"
    dos: str = ""
    doc_status: str = ""                  # final | preliminary | amended (from the feed when present)
    text: str | None = None              # transcribed/structured note text, if the feed provides it
    document: bytes | None = None        # raw scanned packet (PDF/image) → vision OCR, if provided
    content_type: str | None = None      # media type for `document`


@dataclass
class HandoffResult:
    ok: bool
    work_item_id: str = ""
    billing_status: str = ""             # accepted | queued | rejected | error
    detail: str = ""


@dataclass
class ConnectorStatus:
    name: str
    connector: str
    mode: str                            # sandbox | live
    reachable: bool
    base_url: str = ""
    auto_handoff_stb: bool = True
    detail: str = ""
    extra: dict = field(default_factory=dict)


class PMSConnector(ABC):
    name: str = "PMS"
    connector: str = "pms"

    @abstractmethod
    def status(self) -> ConnectorStatus: ...

    @abstractmethod
    def pull_charts(self, limit: int = 5) -> list[InboundChart]: ...

    @abstractmethod
    def push_result(self, payload: dict) -> HandoffResult:
        """payload: {external_id, mrn, specialty, payer, lane, confidence, codes:[{system,code,modifiers,description}]}"""
        ...
