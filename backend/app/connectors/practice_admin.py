"""Practice Admin (VHT-owned PMS) connector — the MVP integration target (E1).

`sandbox` mode implements the expected contract in-process so the inbound-pull → code →
outbound-handoff round-trip works today. `live` mode talks to the real Practice Admin REST
API at the configured base_url with a bearer token from the environment. The live endpoint
paths and payload shapes below are the contract we expect and confirm in Phase-1 discovery —
isolating them here means going live is a config change, not a rewrite.
"""
from __future__ import annotations

import os
import uuid

import httpx

from .base import ConnectorStatus, HandoffResult, InboundChart, PMSConnector
from .sandbox_charts import SANDBOX_CHARTS


class PracticeAdminConnector(PMSConnector):
    name = "Practice Admin"
    connector = "practice_admin"

    def __init__(self, cfg: dict):
        pms = (cfg or {}).get("pms", {}) or {}
        self.mode = pms.get("mode", "sandbox")
        self.base_url = (pms.get("base_url") or "").rstrip("/")
        self.auth_token_env = pms.get("auth_token_env", "PRACTICE_ADMIN_TOKEN")
        self.auto_handoff_stb = bool(pms.get("auto_handoff_stb", True))
        self.timeout = float(pms.get("timeout_s", 20))

    # --- helpers -----------------------------------------------------------
    def _token(self) -> str:
        return os.getenv(self.auth_token_env, "")

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._token()}", "Accept": "application/json"}

    def _is_live(self) -> bool:
        return self.mode == "live" and bool(self.base_url)

    # --- status ------------------------------------------------------------
    def status(self) -> ConnectorStatus:
        if not self._is_live():
            return ConnectorStatus(
                name=self.name, connector=self.connector, mode="sandbox", reachable=True,
                auto_handoff_stb=self.auto_handoff_stb,
                detail="In-process sandbox — point `pms.base_url` at the real API and set mode=live to switch.")
        reachable, detail = False, ""
        try:
            with httpx.Client(timeout=self.timeout, headers=self._headers()) as c:
                r = c.get(f"{self.base_url}/health")
                reachable = r.status_code < 500
                detail = f"GET /health → {r.status_code}"
        except Exception as exc:  # noqa: BLE001 — surface transport errors honestly
            detail = str(exc)
        return ConnectorStatus(
            name=self.name, connector=self.connector, mode="live", reachable=reachable,
            base_url=self.base_url, auto_handoff_stb=self.auto_handoff_stb,
            detail=detail, extra={"token_present": bool(self._token())})

    # --- inbound -----------------------------------------------------------
    def pull_charts(self, limit: int = 5) -> list[InboundChart]:
        if not self._is_live():
            # Sandbox: each pull returns fresh "arrivals" (unique external_id suffix).
            out: list[InboundChart] = []
            for i in range(limit):
                row = SANDBOX_CHARTS[i % len(SANDBOX_CHARTS)]
                suffix = uuid.uuid4().hex[:6]
                out.append(InboundChart(
                    external_id=f"{row['external_id']}-{suffix}",
                    specialty=row["specialty"], payer=row["payer"], modality=row.get("modality", ""),
                    patient_name=row.get("patient_name", "Sandbox Patient"), age=row.get("age", 55),
                    sex=row.get("sex", "F"), pos=row.get("pos", "11"), dos=row.get("dos", ""),
                    doc_status=row.get("doc_status", "final"), text=row["text"]))
            return out
        # Live contract (confirm in discovery): GET /charts?status=new&limit=N
        with httpx.Client(timeout=self.timeout, headers=self._headers()) as c:
            r = c.get(f"{self.base_url}/charts", params={"status": "new", "limit": limit})
            r.raise_for_status()
            rows = r.json()
        charts: list[InboundChart] = []
        for row in rows:
            charts.append(InboundChart(
                external_id=str(row.get("id") or row.get("external_id") or ""),
                specialty=row.get("specialty", ""), payer=row.get("payer", ""),
                mrn=row.get("mrn", ""), patient_name=row.get("patient_name", "PMS Patient"),
                age=int(row.get("age", 55)), sex=row.get("sex", "F"),
                modality=row.get("modality", ""), pos=str(row.get("pos", "11")),
                dos=row.get("dos", ""), doc_status=row.get("doc_status", ""),
                text=row.get("text"), document=None, content_type=row.get("content_type")))
        return charts

    # --- outbound ----------------------------------------------------------
    def push_result(self, payload: dict) -> HandoffResult:
        if not self._is_live():
            # Sandbox: acknowledge as the real PMS would — create a work item id, queue for billing.
            wid = "PA-WI-" + uuid.uuid4().hex[:10].upper()
            return HandoffResult(ok=True, work_item_id=wid, billing_status="accepted",
                                 detail="sandbox acknowledgement")
        # Live contract (confirm in discovery): POST /coding-results → {work_item_id, billing_status}
        try:
            with httpx.Client(timeout=self.timeout, headers=self._headers()) as c:
                r = c.post(f"{self.base_url}/coding-results", json=payload)
                r.raise_for_status()
                data = r.json()
            return HandoffResult(
                ok=True, work_item_id=str(data.get("work_item_id", "")),
                billing_status=data.get("billing_status", "accepted"),
                detail=f"POST /coding-results → {r.status_code}")
        except Exception as exc:  # noqa: BLE001
            return HandoffResult(ok=False, billing_status="error", detail=str(exc))


def get_connector(cfg: dict) -> PracticeAdminConnector:
    """Factory — today Practice Admin; the seam lets Epic/others slot in later by `pms.connector`."""
    return PracticeAdminConnector(cfg)
