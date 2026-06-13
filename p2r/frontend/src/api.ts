import type {
  AceStatus, AuditEntry, DenialSignal, DocumentProvisions, DocumentRow, Lineage, Meta,
  PolicyDelta, PolicySource, Recommendation, ReplayResult, RuleIr, RuleLibraryEntry,
} from "./types";

const BASE = (import.meta as any).env?.VITE_API_BASE ?? "/api";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const j = await res.json();
      detail = j.detail || j.error || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  meta: () => req<Meta>("/meta"),

  // Ingestion
  ingestSample: () => req<{ document_id: string; provision_count: number }>("/ingest/policy/sample", { method: "POST" }),
  ingestPolicy: (payer: string, title: string, text: string) =>
    req<{ document_id: string; provision_count: number }>("/ingest/policy", {
      method: "POST", body: JSON.stringify({ payer, title, text }),
    }),

  // Documents + provisions
  documents: () => req<DocumentRow[]>("/documents"),
  documentProvisions: (docId: string) => req<DocumentProvisions>(`/documents/${docId}/provisions`),

  // Rule library
  ruleLibrary: () => req<RuleLibraryEntry[]>("/rule-library"),

  // Recommendations
  generate: (docId: string) =>
    req<{ document_id: string; payer: string; count: number; recommendations: Recommendation[] }>(
      `/recommendations/from-document/${docId}`, { method: "POST" }),
  recommendations: (p: { verdict?: string; attention?: boolean; status?: string } = {}) => {
    const qs = new URLSearchParams();
    if (p.verdict) qs.set("verdict", p.verdict);
    if (p.attention) qs.set("attention", "true");
    if (p.status) qs.set("status", p.status);
    const s = qs.toString();
    return req<Recommendation[]>(`/recommendations${s ? `?${s}` : ""}`);
  },
  editRecommendation: (id: string, patch: Partial<{ candidate_summary: string; reconciliation_verdict: string; code_sets: any }>) =>
    req<Recommendation>(`/recommendations/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),
  approve: (id: string) =>
    req<{ recommendation_id: string; status: string }>(`/recommendations/${id}/approve`, { method: "POST" }),
  publishToAce: (id: string) =>
    req<{ recommendation_id: string; published: number; policies: any[]; source: string; payer: string }>(
      `/recommendations/${id}/publish-to-ace`, { method: "POST" }),

  // ACE integration glimpse
  aceStatus: () => req<AceStatus>("/integration/ace/status"),

  // Golden-set eval harness
  evalGolden: () => req<GoldenCase[]>("/eval/golden"),
  evalRun: () => req<EvalReport>("/eval/run", { method: "POST" }),

  // P1 — source registry, acquisition agent, deltas, payer MDM
  sources: () => req<PolicySource[]>("/sources"),
  acquire: (id: string) => req<any>(`/sources/${id}/acquire`, { method: "POST" }),
  deltas: () => req<PolicyDelta[]>("/deltas"),
  payerMaster: () => req<{ payer_id: string; name: string; aliases: string[]; lines_of_business: string[] }[]>("/payer-master"),

  // P2 — denial pattern discovery
  denialsLoadSample: () => req<{ remittance_lines: number }>("/denials/load-sample", { method: "POST" }),
  denialsDetect: () => req<{ signals: number; remittance_lines: number; recent_window_days: number; results: DenialSignal[] }>("/denials/detect", { method: "POST" }),
  denialSignals: (status = "") => req<DenialSignal[]>(`/denials/signals${status ? `?status=${status}` : ""}`),
  promoteSignal: (id: string) => req<{ signal_id: string; recommendation_id: string; recommendation: Recommendation }>(`/denials/signals/${id}/promote`, { method: "POST" }),

  // P4 — rule IR / compiler, replay, rollback
  ruleIr: (id: string) => req<RuleIr>(`/recommendations/${id}/rule-ir`),
  replay: (id: string) => req<ReplayResult>(`/recommendations/${id}/replay`, { method: "POST" }),
  rollback: (id: string) => req<any>(`/recommendations/${id}/rollback`, { method: "POST" }),

  // UX — decision log + lineage
  audit: (phase = "") => req<AuditEntry[]>(`/audit${phase ? `?phase=${phase}` : ""}`),
  lineage: (id: string) => req<Lineage>(`/recommendations/${id}/lineage`),
};
