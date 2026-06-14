import type {
  AceStatus, AuditEntry, DenialSignal, DocumentProvisions, DocumentRow, Lineage, Meta,
  PolicyDelta, PolicySource, Recommendation, ReplayResult, RuleIr, RuleLibraryEntry,
} from "./types";

const BASE = (import.meta as any).env?.VITE_API_BASE ?? "/api";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  // Attribute every action to the active role for the append-only Decision Log.
  const role = (typeof localStorage !== "undefined" && localStorage.getItem("p2r_role")) || "Admin";
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Actor": `${role.toLowerCase().replace(/\s+/g, "_")}`,
      "X-Role": role,
      ...(init?.headers ?? {}),
    },
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

  // Golden-set eval harness (multi-phase)
  evalGolden: () => req<GoldenCase[]>("/eval/golden"),
  evalRun: () => req<EvalReport>("/eval/run", { method: "POST" }),
  evalHistory: () => req<EvalReport[]>("/eval/history"),
  evalDenialGolden: () => req<{ code: string; carc: string; pattern: string; note: string; carc_reason: string }[]>("/eval/golden/denials"),
  createGolden: (g: any) => req("/eval/golden", { method: "POST", body: JSON.stringify(g) }),
  deleteGolden: (id: string) => req(`/eval/golden/${id}`, { method: "DELETE" }),

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

  // Admin — runtime config, LLM, rule library CRUD, sources CRUD
  adminConfig: () => req<{ config: any; defaults: any }>("/admin/config"),
  putConfig: (key: string, value: any) => req<{ config: any }>(`/admin/config/${key}`, { method: "PUT", body: JSON.stringify({ value }) }),
  resetConfig: () => req<{ config: any }>("/admin/config/reset", { method: "POST" }),
  llmStatus: () => req<{ available: boolean; model: string; anthropic_key: boolean; openai_key: boolean }>("/admin/llm/status"),
  testLlm: () => req<{ ok: boolean; model?: string; error?: string }>("/admin/llm/test", { method: "POST" }),
  createRule: (r: any) => req("/rule-library", { method: "POST", body: JSON.stringify(r) }),
  updateRule: (id: string, r: any) => req(`/rule-library/${id}`, { method: "PUT", body: JSON.stringify(r) }),
  deleteRule: (id: string) => req(`/rule-library/${id}`, { method: "DELETE" }),
  createSource: (s: any) => req("/sources", { method: "POST", body: JSON.stringify(s) }),
};
