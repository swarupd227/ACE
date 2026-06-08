import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { Search, Plus, Save, Trash2, X, ShieldCheck, Lock, Unlock, Network, Database } from "lucide-react";
import { api } from "../api";
import OntologyGraph from "../components/OntologyGraph";
import { Spinner } from "../lib";
import type { Policy } from "../types";

const BLANK: Partial<Policy> = { payer: "", code: "", medical_necessity: "", requires_auth: false, covered_dx: [], source: "ClientOverlay" };

function PolicyEditor({ initial, onClose }: { initial: Partial<Policy>; onClose: () => void }) {
  const qc = useQueryClient();
  const [p, setP] = useState<Partial<Policy>>({ ...initial });
  const isNew = !initial.id;
  const save = useMutation({
    mutationFn: () => {
      const body = { ...p, covered_dx: (p.covered_dx as any) ?? [] };
      return isNew ? api.createPolicy(body) : api.updatePolicy(initial.id!, body);
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["policies"] }); qc.invalidateQueries({ queryKey: ["kg"] }); onClose(); },
  });
  const set = (k: keyof Policy, v: any) => setP((x) => ({ ...x, [k]: v }));

  return (
    <div className="rounded-lg border-2 border-ace-200 bg-ace-50/40 p-3 space-y-2">
      <div className="grid grid-cols-2 gap-2">
        <input className="rounded border border-slate-200 px-2 py-1.5 text-sm" placeholder="Payer (e.g. Anthem)" value={p.payer ?? ""} onChange={(e) => set("payer", e.target.value)} />
        <input className="rounded border border-slate-200 px-2 py-1.5 text-sm font-mono" placeholder="Code (e.g. 74177)" value={p.code ?? ""} onChange={(e) => set("code", e.target.value)} />
      </div>
      <textarea className="w-full rounded border border-slate-200 px-2 py-1.5 text-sm" rows={2} placeholder="Medical necessity / policy text" value={p.medical_necessity ?? ""} onChange={(e) => set("medical_necessity", e.target.value)} />
      <input className="w-full rounded border border-slate-200 px-2 py-1.5 text-sm font-mono" placeholder="Covered dx prefixes, comma-separated (e.g. R10, N20)"
        value={(p.covered_dx ?? []).join(", ")} onChange={(e) => set("covered_dx", e.target.value.split(",").map((s) => s.trim()).filter(Boolean))} />
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 text-sm text-slate-600">
          <input type="checkbox" checked={!!p.requires_auth} onChange={(e) => set("requires_auth", e.target.checked)} /> Requires prior authorization
        </label>
        <div className="flex gap-2">
          <button className="btn-ghost py-1.5" onClick={onClose}><X size={14} /> Cancel</button>
          <button className="btn-primary py-1.5" disabled={!p.payer || !p.code || save.isPending} onClick={() => save.mutate()}>
            {save.isPending ? <Spinner className="h-4 w-4" /> : <Save size={14} />} {isNew ? "Create" : "Save"}
          </button>
        </div>
      </div>
    </div>
  );
}

function PoliciesTab() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["policies"], queryFn: api.policies });
  const [q, setQ] = useState("");
  const [editing, setEditing] = useState<number | "new" | null>(null);
  const del = useMutation({ mutationFn: (id: number) => api.deletePolicy(id), onSuccess: () => { qc.invalidateQueries({ queryKey: ["policies"] }); qc.invalidateQueries({ queryKey: ["kg"] }); } });

  const list = (data ?? []).filter((p) => !q || `${p.payer} ${p.code} ${p.medical_necessity}`.toLowerCase().includes(q.toLowerCase()));

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div className="relative">
          <Search size={15} className="absolute left-2.5 top-2.5 text-slate-400" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search payer / code / text…" className="w-72 rounded-lg border border-slate-200 pl-8 pr-3 py-2 text-sm" />
        </div>
        <button className="btn-primary" onClick={() => setEditing("new")}><Plus size={15} /> Add policy / client overlay</button>
      </div>

      <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-2.5 text-xs text-emerald-800 flex items-center gap-2">
        <ShieldCheck size={14} /> Edits here take effect immediately — these policies drive the deterministic medical-necessity gate on the next coding run.
      </div>

      {editing === "new" && <PolicyEditor initial={BLANK} onClose={() => setEditing(null)} />}

      {isLoading ? <div className="grid place-items-center h-32"><Spinner className="h-5 w-5 text-ace-500" /></div> : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
              <th className="px-3 py-2">Payer</th><th className="px-3 py-2">Code</th><th className="px-3 py-2">Medical necessity</th>
              <th className="px-3 py-2">Covered dx</th><th className="px-3 py-2">Auth</th><th className="px-3 py-2">Source</th><th className="px-3 py-2"></th>
            </tr></thead>
            <tbody className="divide-y divide-slate-100">
              {list.map((p) => editing === p.id ? (
                <tr key={p.id}><td colSpan={7} className="p-2"><PolicyEditor initial={p} onClose={() => setEditing(null)} /></td></tr>
              ) : (
                <tr key={p.id} className="hover:bg-slate-50/70">
                  <td className="px-3 py-2 font-medium text-slate-700">{p.payer}</td>
                  <td className="px-3 py-2 font-mono">{p.code}</td>
                  <td className="px-3 py-2 text-slate-600 max-w-md text-xs">{p.medical_necessity}</td>
                  <td className="px-3 py-2 text-xs">{p.covered_dx.map((d) => <span key={d} className="pill bg-slate-100 text-slate-600 ring-1 ring-slate-200 mr-1">{d}</span>)}</td>
                  <td className="px-3 py-2">{p.requires_auth ? <Lock size={14} className="text-amber-500" /> : <Unlock size={14} className="text-slate-300" />}</td>
                  <td className="px-3 py-2 text-xs text-slate-400">{p.source}</td>
                  <td className="px-3 py-2 text-right whitespace-nowrap">
                    <button className="btn-ghost py-1 mr-1" onClick={() => setEditing(p.id)}>Edit</button>
                    <button className="text-rose-400 hover:text-rose-600" onClick={() => del.mutate(p.id)}><Trash2 size={14} /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function GraphTab() {
  const { data } = useQuery({ queryKey: ["kg"], queryFn: api.kg });
  if (!data) return <div className="grid place-items-center h-40"><Spinner className="h-5 w-5 text-ace-500" /></div>;
  return <OntologyGraph nodes={data.nodes} links={data.links} />;
}

function SourcesTab() {
  const { data: meta } = useQuery({ queryKey: ["meta"], queryFn: api.meta });
  const { data: ref } = useQuery({ queryKey: ["refsum"], queryFn: api.referenceSummary });
  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div className="card p-5">
        <div className="flex items-center gap-2 mb-3"><Database size={16} className="text-ace-600" /><h2 className="font-bold text-slate-800">Data provenance</h2></div>
        <ul className="space-y-2 text-sm">
          {meta && Object.entries(meta.provenance).map(([k, v]) => (
            <li key={k} className="flex justify-between gap-3"><span className="font-mono text-slate-700">{k}</span><span className="text-xs text-slate-500 text-right">{v as string}</span></li>
          ))}
        </ul>
      </div>
      <div className="card p-5">
        <h2 className="font-bold text-slate-800 mb-3">Loaded reference data</h2>
        {ref && <div className="text-sm text-slate-600 grid grid-cols-2 gap-1">
          <span>ICD-10-CM: {ref.code_systems?.ICD10CM ?? 0}</span><span>CPT: {ref.code_systems?.CPT ?? 0}</span>
          <span>HCPCS: {ref.code_systems?.HCPCS ?? 0}</span><span>NCCI edits: {ref.ncci_edits}</span>
          <span>MUE limits: {ref.mue_limits}</span><span>Payer policies: {ref.payer_policies}</span>
          <span>Guidelines: {ref.guidelines}</span><span>Ontology concepts: {ref.ontology_concepts}</span>
        </div>}
        <p className="mt-3 text-xs text-slate-400">Effective-dated; production swaps in licensed AMA CPT and SNOMED/UMLS ontology (same shape).</p>
      </div>
    </div>
  );
}

export default function PolicyAdmin() {
  const [tab, setTab] = useState<"policies" | "graph" | "sources">("policies");
  const tabs: [typeof tab, string, any][] = [["policies", "Payer Policies", ShieldCheck], ["graph", "Explore Graph", Network], ["sources", "Data Sources", Database]];
  return (
    <div className="space-y-4 fadeup">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900">Policy &amp; Knowledge Admin</h1>
        <p className="text-sm text-slate-500">Manage the payer policies and knowledge that ground coding. Edits drive the medical-necessity gate.</p>
      </div>
      <div className="flex gap-1 border-b border-slate-200">
        {tabs.map(([k, label, Icon]) => (
          <button key={k} onClick={() => setTab(k)}
            className={clsx("flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 -mb-px",
              tab === k ? "border-ace-500 text-ace-700" : "border-transparent text-slate-500 hover:text-slate-700")}>
            <Icon size={15} /> {label}
          </button>
        ))}
      </div>
      {tab === "policies" && <PoliciesTab />}
      {tab === "graph" && <GraphTab />}
      {tab === "sources" && <SourcesTab />}
    </div>
  );
}
