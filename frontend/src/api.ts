const BASE = (import.meta as any).env?.VITE_API_BASE ?? "/api";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
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
  dashboard: () => req<import("./types").Dashboard>("/dashboard/stats"),
  kg: () => req<{ nodes: any[]; links: any[] }>("/kg/graph"),
  referenceSummary: () => req<any>("/reference/summary"),
  guidelines: () => req<any[]>("/guidelines"),
  learning: () => req<any[]>("/learning"),
  evalSummary: () => req<any>("/eval/summary"),
  evalRun: () => req<any>("/eval/run", { method: "POST" }),
};
