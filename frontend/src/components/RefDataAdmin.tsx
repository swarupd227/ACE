import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { Search, Plus, Save, Trash2, X, ShieldCheck, Database } from "lucide-react";
import { api } from "../api";
import { Spinner } from "../lib";
import type { RefCode, Ncci, Mue, Modifier } from "../types";

type Sub = "codes" | "ncci" | "mue" | "modifiers" | "provenance";

function Banner({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-2.5 text-xs text-emerald-800 flex items-center gap-2">
      <ShieldCheck size={14} /> {children}
    </div>
  );
}

/* ---------------- Code sets ---------------- */
const BLANK_CODE: Partial<RefCode> = { code_system: "ICD10CM", code: "", description: "", billable: true, modality: "", source: "ClientOverlay" };

function CodeEditor({ initial, onClose }: { initial: Partial<RefCode>; onClose: () => void }) {
  const qc = useQueryClient();
  const [c, setC] = useState<Partial<RefCode>>({ ...initial });
  const isNew = !initial.id;
  const save = useMutation({
    mutationFn: () => (isNew ? api.createRefCode(c) : api.updateRefCode(initial.id!, c)),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["refcodes"] }); qc.invalidateQueries({ queryKey: ["refsum"] }); onClose(); },
  });
  const set = (k: keyof RefCode, v: any) => setC((x) => ({ ...x, [k]: v }));
  return (
    <div className="rounded-lg border-2 border-ace-200 bg-ace-50/40 p-3 space-y-2">
      <div className="grid grid-cols-4 gap-2">
        <select className="rounded border border-slate-200 px-2 py-1.5 text-sm" value={c.code_system} onChange={(e) => set("code_system", e.target.value)}>
          {["ICD10CM", "CPT", "HCPCS"].map((s) => <option key={s}>{s}</option>)}
        </select>
        <input className="rounded border border-slate-200 px-2 py-1.5 text-sm font-mono" placeholder="code" value={c.code ?? ""} onChange={(e) => set("code", e.target.value)} />
        <input className="rounded border border-slate-200 px-2 py-1.5 text-sm" placeholder="modality (CPT radiology)" value={c.modality ?? ""} onChange={(e) => set("modality", e.target.value)} />
        <label className="flex items-center gap-2 text-sm text-slate-600"><input type="checkbox" checked={!!c.billable} onChange={(e) => set("billable", e.target.checked)} /> billable</label>
      </div>
      <input className="w-full rounded border border-slate-200 px-2 py-1.5 text-sm" placeholder="description" value={c.description ?? ""} onChange={(e) => set("description", e.target.value)} />
      <div className="flex justify-end gap-2">
        <button className="btn-ghost py-1.5" onClick={onClose}><X size={14} /> Cancel</button>
        <button className="btn-primary py-1.5" disabled={!c.code || !c.description || save.isPending} onClick={() => save.mutate()}>
          {save.isPending ? <Spinner className="h-4 w-4" /> : <Save size={14} />} {isNew ? "Create" : "Save"}
        </button>
      </div>
      {save.isError && <div className="text-xs text-rose-600">{(save.error as Error).message}</div>}
    </div>
  );
}

function CodesTab() {
  const qc = useQueryClient();
  const [system, setSystem] = useState("");
  const [q, setQ] = useState("");
  const { data, isLoading } = useQuery({ queryKey: ["refcodes", system, q], queryFn: () => api.refCodes(system, q) });
  const [editing, setEditing] = useState<number | "new" | null>(null);
  const del = useMutation({ mutationFn: (id: number) => api.deleteRefCode(id), onSuccess: () => { qc.invalidateQueries({ queryKey: ["refcodes"] }); qc.invalidateQueries({ queryKey: ["refsum"] }); } });
  return (
    <div className="space-y-3">
      <Banner>Client overlay codes and edits here join the code sets the agent retrieves and the validation gates check (billable, sex/age, specificity).</Banner>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <select className="rounded-lg border border-slate-200 px-2 py-2 text-sm" value={system} onChange={(e) => setSystem(e.target.value)}>
            <option value="">All systems</option>{["ICD10CM", "CPT", "HCPCS"].map((s) => <option key={s}>{s}</option>)}
          </select>
          <div className="relative">
            <Search size={15} className="absolute left-2.5 top-2.5 text-slate-400" />
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search code / description…" className="w-64 rounded-lg border border-slate-200 pl-8 pr-3 py-2 text-sm" />
          </div>
        </div>
        <button className="btn-primary" onClick={() => setEditing("new")}><Plus size={15} /> Add code (overlay)</button>
      </div>
      {editing === "new" && <CodeEditor initial={BLANK_CODE} onClose={() => setEditing(null)} />}
      {isLoading ? <div className="grid place-items-center h-32"><Spinner className="h-5 w-5 text-ace-500" /></div> : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
              <th className="px-3 py-2">System</th><th className="px-3 py-2">Code</th><th className="px-3 py-2">Description</th>
              <th className="px-3 py-2">Billable</th><th className="px-3 py-2">Source</th><th className="px-3 py-2"></th>
            </tr></thead>
            <tbody className="divide-y divide-slate-100">
              {(data ?? []).map((c) => editing === c.id ? (
                <tr key={c.id}><td colSpan={6} className="p-2"><CodeEditor initial={c} onClose={() => setEditing(null)} /></td></tr>
              ) : (
                <tr key={c.id} className="hover:bg-slate-50/70">
                  <td className="px-3 py-2 text-xs text-slate-500">{c.code_system}</td>
                  <td className="px-3 py-2 font-mono">{c.code}</td>
                  <td className="px-3 py-2 text-slate-600 max-w-md text-xs">{c.description}</td>
                  <td className="px-3 py-2 text-xs">{c.billable ? "yes" : "no"}</td>
                  <td className="px-3 py-2 text-xs"><span className={clsx("pill ring-1", c.source.includes("Overlay") ? "bg-ace-50 text-ace-700 ring-ace-200" : "bg-slate-100 text-slate-500 ring-slate-200")}>{c.source}</span></td>
                  <td className="px-3 py-2 text-right whitespace-nowrap">
                    <button className="btn-ghost py-1 mr-1" onClick={() => setEditing(c.id)}>Edit</button>
                    <button className="text-rose-400 hover:text-rose-600" onClick={() => del.mutate(c.id)}><Trash2 size={14} /></button>
                  </td>
                </tr>
              ))}
              {(data ?? []).length === 0 && <tr><td colSpan={6} className="p-6 text-center text-sm text-slate-400">No codes match.</td></tr>}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ---------------- NCCI ---------------- */
function NcciTab() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["ncci"], queryFn: api.ncci });
  const [add, setAdd] = useState(false);
  const [f, setF] = useState<Partial<Ncci>>({ column1: "", column2: "", modifier_allowed: true, rationale: "" });
  const create = useMutation({ mutationFn: () => api.createNcci(f), onSuccess: () => { qc.invalidateQueries({ queryKey: ["ncci"] }); setAdd(false); setF({ column1: "", column2: "", modifier_allowed: true, rationale: "" }); } });
  const del = useMutation({ mutationFn: (id: number) => api.deleteNcci(id), onSuccess: () => qc.invalidateQueries({ queryKey: ["ncci"] }) });
  return (
    <div className="space-y-3">
      <Banner>NCCI PTP edits drive the deterministic <b>bundling gate</b>. Column-2 codes are bundled into column-1; modifier_allowed=0 means a hard bundle (no 59/X override).</Banner>
      <div className="flex justify-end"><button className="btn-primary" onClick={() => setAdd((v) => !v)}><Plus size={15} /> Add edit</button></div>
      {add && (
        <div className="rounded-lg border-2 border-ace-200 bg-ace-50/40 p-3 flex flex-wrap items-center gap-2">
          <input className="rounded border border-slate-200 px-2 py-1.5 text-sm font-mono w-28" placeholder="column1" value={f.column1 ?? ""} onChange={(e) => setF({ ...f, column1: e.target.value })} />
          <input className="rounded border border-slate-200 px-2 py-1.5 text-sm font-mono w-28" placeholder="column2" value={f.column2 ?? ""} onChange={(e) => setF({ ...f, column2: e.target.value })} />
          <label className="flex items-center gap-1.5 text-sm text-slate-600"><input type="checkbox" checked={!!f.modifier_allowed} onChange={(e) => setF({ ...f, modifier_allowed: e.target.checked })} /> modifier allowed</label>
          <input className="rounded border border-slate-200 px-2 py-1.5 text-sm flex-1 min-w-40" placeholder="rationale" value={f.rationale ?? ""} onChange={(e) => setF({ ...f, rationale: e.target.value })} />
          <button className="btn-primary py-1.5" disabled={!f.column1 || !f.column2 || create.isPending} onClick={() => create.mutate()}>{create.isPending ? <Spinner className="h-4 w-4" /> : <Save size={14} />} Add</button>
        </div>
      )}
      {isLoading ? <div className="grid place-items-center h-32"><Spinner className="h-5 w-5 text-ace-500" /></div> : (
        <div className="card overflow-hidden"><table className="w-full text-sm">
          <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
            <th className="px-3 py-2">Payable (col 1)</th><th className="px-3 py-2">Bundled (col 2)</th><th className="px-3 py-2">Modifier</th><th className="px-3 py-2">Rationale</th><th className="px-3 py-2"></th>
          </tr></thead>
          <tbody className="divide-y divide-slate-100">
            {(data ?? []).map((e) => (
              <tr key={e.id} className="hover:bg-slate-50/70">
                <td className="px-3 py-2 font-mono">{e.column1}</td><td className="px-3 py-2 font-mono">{e.column2}</td>
                <td className="px-3 py-2 text-xs">{e.modifier_allowed ? "allowed (59/X)" : <span className="text-rose-600">hard bundle</span>}</td>
                <td className="px-3 py-2 text-xs text-slate-500 max-w-md">{e.rationale}</td>
                <td className="px-3 py-2 text-right"><button className="text-rose-400 hover:text-rose-600" onClick={() => del.mutate(e.id)}><Trash2 size={14} /></button></td>
              </tr>
            ))}
          </tbody>
        </table></div>
      )}
    </div>
  );
}

/* ---------------- MUE ---------------- */
function MueTab() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["mue"], queryFn: api.mue });
  const [add, setAdd] = useState(false);
  const [f, setF] = useState<Partial<Mue>>({ code: "", max_units: 1, rationale: "" });
  const create = useMutation({ mutationFn: () => api.createMue(f), onSuccess: () => { qc.invalidateQueries({ queryKey: ["mue"] }); setAdd(false); setF({ code: "", max_units: 1, rationale: "" }); } });
  const del = useMutation({ mutationFn: (id: number) => api.deleteMue(id), onSuccess: () => qc.invalidateQueries({ queryKey: ["mue"] }) });
  return (
    <div className="space-y-3">
      <Banner>MUE limits drive the <b>units gate</b> — the max units of a code per day. max_units &lt; 1 blocks the code.</Banner>
      <div className="flex justify-end"><button className="btn-primary" onClick={() => setAdd((v) => !v)}><Plus size={15} /> Add limit</button></div>
      {add && (
        <div className="rounded-lg border-2 border-ace-200 bg-ace-50/40 p-3 flex flex-wrap items-center gap-2">
          <input className="rounded border border-slate-200 px-2 py-1.5 text-sm font-mono w-28" placeholder="code" value={f.code ?? ""} onChange={(e) => setF({ ...f, code: e.target.value })} />
          <input type="number" className="rounded border border-slate-200 px-2 py-1.5 text-sm w-24" placeholder="max units" value={f.max_units ?? 1} onChange={(e) => setF({ ...f, max_units: Number(e.target.value) })} />
          <input className="rounded border border-slate-200 px-2 py-1.5 text-sm flex-1 min-w-40" placeholder="rationale" value={f.rationale ?? ""} onChange={(e) => setF({ ...f, rationale: e.target.value })} />
          <button className="btn-primary py-1.5" disabled={!f.code || create.isPending} onClick={() => create.mutate()}>{create.isPending ? <Spinner className="h-4 w-4" /> : <Save size={14} />} Add</button>
        </div>
      )}
      {isLoading ? <div className="grid place-items-center h-32"><Spinner className="h-5 w-5 text-ace-500" /></div> : (
        <div className="card overflow-hidden"><table className="w-full text-sm">
          <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
            <th className="px-3 py-2">Code</th><th className="px-3 py-2">Max units/day</th><th className="px-3 py-2">Rationale</th><th className="px-3 py-2"></th>
          </tr></thead>
          <tbody className="divide-y divide-slate-100">
            {(data ?? []).map((m) => (
              <tr key={m.id} className="hover:bg-slate-50/70">
                <td className="px-3 py-2 font-mono">{m.code}</td><td className="px-3 py-2">{m.max_units}</td>
                <td className="px-3 py-2 text-xs text-slate-500 max-w-md">{m.rationale}</td>
                <td className="px-3 py-2 text-right"><button className="text-rose-400 hover:text-rose-600" onClick={() => del.mutate(m.id)}><Trash2 size={14} /></button></td>
              </tr>
            ))}
          </tbody>
        </table></div>
      )}
    </div>
  );
}

/* ---------------- Modifiers ---------------- */
function ModifiersTab() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["modifiers"], queryFn: api.modifiers });
  const [add, setAdd] = useState(false);
  const [f, setF] = useState<Partial<Modifier>>({ modifier: "", description: "", applies_to: "" });
  const create = useMutation({ mutationFn: () => api.createModifier(f), onSuccess: () => { qc.invalidateQueries({ queryKey: ["modifiers"] }); setAdd(false); setF({ modifier: "", description: "", applies_to: "" }); } });
  const del = useMutation({ mutationFn: (id: number) => api.deleteModifier(id), onSuccess: () => qc.invalidateQueries({ queryKey: ["modifiers"] }) });
  return (
    <div className="space-y-3">
      <Banner>The modifier registry drives the <b>modifier-validity gate</b> — the agent may only attach modifiers that exist here.</Banner>
      <div className="flex justify-end"><button className="btn-primary" onClick={() => setAdd((v) => !v)}><Plus size={15} /> Add modifier</button></div>
      {add && (
        <div className="rounded-lg border-2 border-ace-200 bg-ace-50/40 p-3 flex flex-wrap items-center gap-2">
          <input className="rounded border border-slate-200 px-2 py-1.5 text-sm font-mono w-20" placeholder="mod" value={f.modifier ?? ""} onChange={(e) => setF({ ...f, modifier: e.target.value })} />
          <input className="rounded border border-slate-200 px-2 py-1.5 text-sm flex-1 min-w-40" placeholder="description" value={f.description ?? ""} onChange={(e) => setF({ ...f, description: e.target.value })} />
          <input className="rounded border border-slate-200 px-2 py-1.5 text-sm w-40" placeholder="applies to" value={f.applies_to ?? ""} onChange={(e) => setF({ ...f, applies_to: e.target.value })} />
          <button className="btn-primary py-1.5" disabled={!f.modifier || !f.description || create.isPending} onClick={() => create.mutate()}>{create.isPending ? <Spinner className="h-4 w-4" /> : <Save size={14} />} Add</button>
        </div>
      )}
      {isLoading ? <div className="grid place-items-center h-32"><Spinner className="h-5 w-5 text-ace-500" /></div> : (
        <div className="card overflow-hidden"><table className="w-full text-sm">
          <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
            <th className="px-3 py-2">Modifier</th><th className="px-3 py-2">Description</th><th className="px-3 py-2">Applies to</th><th className="px-3 py-2"></th>
          </tr></thead>
          <tbody className="divide-y divide-slate-100">
            {(data ?? []).map((m) => (
              <tr key={m.id} className="hover:bg-slate-50/70">
                <td className="px-3 py-2 font-mono font-semibold">{m.modifier}</td>
                <td className="px-3 py-2 text-slate-600 text-xs max-w-md">{m.description}</td>
                <td className="px-3 py-2 text-xs text-slate-500">{m.applies_to || "—"}</td>
                <td className="px-3 py-2 text-right"><button className="text-rose-400 hover:text-rose-600" onClick={() => del.mutate(m.id)}><Trash2 size={14} /></button></td>
              </tr>
            ))}
          </tbody>
        </table></div>
      )}
    </div>
  );
}

/* ---------------- Provenance ---------------- */
function ProvenanceTab() {
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
          <span>MUE limits: {ref.mue_limits}</span><span>Modifiers: {ref.modifiers}</span>
          <span>Payer policies: {ref.payer_policies}</span><span>Guidelines: {ref.guidelines}</span>
          <span>Ontology concepts: {ref.ontology_concepts}</span>
        </div>}
        <p className="mt-3 text-xs text-slate-400">Effective-dated; production swaps in licensed AMA CPT and SNOMED/UMLS ontology (same shape).</p>
      </div>
    </div>
  );
}

export default function RefDataAdmin() {
  const [sub, setSub] = useState<Sub>("codes");
  const subs: [Sub, string][] = [["codes", "Code sets"], ["ncci", "NCCI bundling"], ["mue", "MUE limits"], ["modifiers", "Modifiers"], ["provenance", "Provenance"]];
  return (
    <div className="space-y-3">
      <div className="flex gap-1.5 flex-wrap">
        {subs.map(([k, label]) => (
          <button key={k} onClick={() => setSub(k)}
            className={clsx("rounded-full px-3 py-1 text-xs font-medium ring-1",
              sub === k ? "bg-ace-600 text-white ring-ace-600" : "bg-white text-slate-600 ring-slate-200 hover:bg-slate-50")}>
            {label}
          </button>
        ))}
      </div>
      {sub === "codes" && <CodesTab />}
      {sub === "ncci" && <NcciTab />}
      {sub === "mue" && <MueTab />}
      {sub === "modifiers" && <ModifiersTab />}
      {sub === "provenance" && <ProvenanceTab />}
    </div>
  );
}
