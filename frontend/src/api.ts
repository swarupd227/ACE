const BASE = (import.meta as any).env?.VITE_API_BASE ?? "/api";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  // Attribute every mutation to the active role for the admin change-log.
  const role = (typeof localStorage !== "undefined" && localStorage.getItem("ace_role")) || "Admin";
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Actor": `${role.toLowerCase().replace(/\s+/g, "_")}:demo`,
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
  meta: () => req<import("./types").Meta>("/meta"),
  encounters: () => req<import("./types").EncounterRow[]>("/encounters"),
  encounter: (id: string) => req<import("./types").EncounterDetail>(`/encounters/${id}`),
  code: (id: string) => req<import("./types").Run>(`/encounters/${id}/code`, { method: "POST" }),
  runAll: () => req<{ coded: number; lanes: Record<string, number> }>("/coding/run-all", { method: "POST" }),
  audit: (runId: string) => req<any[]>(`/runs/${runId}/audit`),
  accept: (codeId: string) =>
    req(`/codes/${codeId}/accept`, { method: "POST", body: JSON.stringify({ coder_id: "coder:demo" }) }),
  override: (codeId: string, override_code: string, reason: string) =>
    req(`/codes/${codeId}/override`, {
      method: "POST",
      body: JSON.stringify({ override_code, reason, coder_id: "coder:demo" }),
    }),
  cdiScan: (encId: string) => req<import("./types").CdiQuery[]>(`/encounters/${encId}/cdi-scan`, { method: "POST" }),
  cdiForEncounter: (encId: string) => req<import("./types").CdiQuery[]>(`/encounters/${encId}/cdi`),
  cdiQueue: () => req<import("./types").CdiQuery[]>("/cdi/queries"),
  cdiRespond: (queryId: string, response: string) =>
    req<{ query: import("./types").CdiQuery; recoded: boolean; run: import("./types").Run | null }>(
      `/cdi/queries/${queryId}/respond`,
      { method: "POST", body: JSON.stringify({ response, responder: "physician:demo" }) }
    ),
  reassign: (runId: string, lane: string, reason: string) =>
    req<import("./types").Run>(`/runs/${runId}/reassign`, {
      method: "POST",
      body: JSON.stringify({ lane, reason, actor: "coder:demo" }),
    }),
  rollback: (runId: string) => req<import("./types").Run>(`/runs/${runId}/rollback`, { method: "POST" }),
  escalate: (runId: string, to: string, reason: string) =>
    req<import("./types").Run>(`/runs/${runId}/escalate`, {
      method: "POST",
      body: JSON.stringify({ to, reason, actor: "coder:demo" }),
    }),
  controlTower: () => req<import("./types").ControlTower>("/control-tower"),
  assign: (runIds: string[], assignedTo: string) =>
    req<{ assigned: number; to: string }>("/control-tower/assign", {
      method: "POST", body: JSON.stringify({ run_ids: runIds, assigned_to: assignedTo }),
    }),
  policies: () => req<import("./types").Policy[]>("/policies"),
  createPolicy: (p: Partial<import("./types").Policy>) =>
    req<import("./types").Policy>("/policies", { method: "POST", body: JSON.stringify(p) }),
  updatePolicy: (id: number, p: Partial<import("./types").Policy>) =>
    req<import("./types").Policy>(`/policies/${id}`, { method: "PUT", body: JSON.stringify(p) }),
  deletePolicy: (id: number) => req(`/policies/${id}`, { method: "DELETE" }),
  // --- Knowledge Graph Builder (ontology concepts + edges + guidelines) ---
  ontologyMeta: () => req<{ rel_types: string[]; semantic_types: string[] }>("/ontology/meta"),
  concepts: () => req<import("./types").Concept[]>("/ontology/concepts"),
  createConcept: (c: Partial<import("./types").Concept>) =>
    req<import("./types").Concept>("/ontology/concepts", { method: "POST", body: JSON.stringify(c) }),
  updateConcept: (id: number, c: Partial<import("./types").Concept>) =>
    req<import("./types").Concept>(`/ontology/concepts/${id}`, { method: "PUT", body: JSON.stringify(c) }),
  deleteConcept: (id: number) => req(`/ontology/concepts/${id}`, { method: "DELETE" }),
  edges: () => req<import("./types").Edge[]>("/ontology/edges"),
  createEdge: (e: import("./types").EdgeIn) =>
    req<import("./types").Edge>("/ontology/edges", { method: "POST", body: JSON.stringify(e) }),
  deleteEdge: (id: number) => req(`/ontology/edges/${id}`, { method: "DELETE" }),
  kgGuidelines: () => req<import("./types").Guideline[]>("/ontology/guidelines"),
  createGuideline: (g: Partial<import("./types").Guideline>) =>
    req<import("./types").Guideline>("/ontology/guidelines", { method: "POST", body: JSON.stringify(g) }),
  updateGuideline: (id: number, g: Partial<import("./types").Guideline>) =>
    req<import("./types").Guideline>(`/ontology/guidelines/${id}`, { method: "PUT", body: JSON.stringify(g) }),
  deleteGuideline: (id: number) => req(`/ontology/guidelines/${id}`, { method: "DELETE" }),
  patchLearning: (id: string, applied: boolean) =>
    req(`/learning/${id}`, { method: "PATCH", body: JSON.stringify({ applied }) }),
  deleteLearning: (id: string) => req(`/learning/${id}`, { method: "DELETE" }),
  integrations: () => req<import("./types").Integrations>("/integrations"),
  ingest: (body: Record<string, any>) =>
    req<{ id: string; mrn: string; specialty: string; status: string; source_system: string }>(
      "/ingest", { method: "POST", body: JSON.stringify(body) }),
  adminConfig: () => req<{ config: any; meta: Record<string, string>; defaults: any }>("/admin/config"),
  putConfig: (key: string, value: any) =>
    req(`/admin/config/${key}`, { method: "PUT", body: JSON.stringify({ value }) }),
  resetConfig: () => req("/admin/config/reset", { method: "POST" }),
  adminAudit: () => req<import("./types").AuditChange[]>("/admin/audit"),
  // --- Reference Data admin (drives the validation gates) ---
  refCodes: (system = "", q = "") => req<import("./types").RefCode[]>(`/reference/codes?system=${encodeURIComponent(system)}&q=${encodeURIComponent(q)}`),
  createRefCode: (c: Partial<import("./types").RefCode>) => req<import("./types").RefCode>("/reference/codes", { method: "POST", body: JSON.stringify(c) }),
  updateRefCode: (id: number, c: Partial<import("./types").RefCode>) => req<import("./types").RefCode>(`/reference/codes/${id}`, { method: "PUT", body: JSON.stringify(c) }),
  deleteRefCode: (id: number) => req(`/reference/codes/${id}`, { method: "DELETE" }),
  ncci: () => req<import("./types").Ncci[]>("/reference/ncci"),
  createNcci: (e: Partial<import("./types").Ncci>) => req<import("./types").Ncci>("/reference/ncci", { method: "POST", body: JSON.stringify(e) }),
  deleteNcci: (id: number) => req(`/reference/ncci/${id}`, { method: "DELETE" }),
  mue: () => req<import("./types").Mue[]>("/reference/mue"),
  createMue: (m: Partial<import("./types").Mue>) => req<import("./types").Mue>("/reference/mue", { method: "POST", body: JSON.stringify(m) }),
  updateMue: (id: number, m: Partial<import("./types").Mue>) => req<import("./types").Mue>(`/reference/mue/${id}`, { method: "PUT", body: JSON.stringify(m) }),
  deleteMue: (id: number) => req(`/reference/mue/${id}`, { method: "DELETE" }),
  modifiers: () => req<import("./types").Modifier[]>("/reference/modifiers"),
  createModifier: (m: Partial<import("./types").Modifier>) => req<import("./types").Modifier>("/reference/modifiers", { method: "POST", body: JSON.stringify(m) }),
  deleteModifier: (id: number) => req(`/reference/modifiers/${id}`, { method: "DELETE" }),
  dashboard: () => req<import("./types").Dashboard>("/dashboard/stats"),
  kg: () => req<{ nodes: any[]; links: any[] }>("/kg/graph"),
  referenceSummary: () => req<any>("/reference/summary"),
  guidelines: () => req<any[]>("/guidelines"),
  learning: () => req<any[]>("/learning"),
  evalSummary: () => req<any>("/eval/summary"),
  evalRun: () => req<any>("/eval/run", { method: "POST" }),
};
