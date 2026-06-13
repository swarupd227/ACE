import type {
  AceStatus, DocumentProvisions, DocumentRow, Meta, Recommendation, RuleLibraryEntry,
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
};
