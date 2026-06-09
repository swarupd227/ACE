import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { Plus, Save, Trash2, X, Network, GitBranch, Boxes, Sparkles } from "lucide-react";
import { api } from "../api";
import { Spinner } from "../lib";
import type { Concept, CodeMap, Edge } from "../types";

const BLANK: Partial<Concept> = { cui: "", name: "", semantic_type: "", maps_to: [] };

function ConceptEditor({ initial, semanticTypes, onClose }: {
  initial: Partial<Concept>; semanticTypes: string[]; onClose: () => void;
}) {
  const qc = useQueryClient();
  const [c, setC] = useState<Partial<Concept>>({ ...initial, maps_to: initial.maps_to ?? [] });
  const isNew = !initial.id;
  const save = useMutation({
    mutationFn: () => (isNew ? api.createConcept(c) : api.updateConcept(initial.id!, c)),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["concepts"] });
      qc.invalidateQueries({ queryKey: ["kg"] });
      qc.invalidateQueries({ queryKey: ["refsum"] });
      onClose();
    },
  });
  const maps = c.maps_to ?? [];
  const setMap = (i: number, k: keyof CodeMap, v: string) =>
    setC((x) => ({ ...x, maps_to: (x.maps_to ?? []).map((m, j) => (j === i ? { ...m, [k]: v } : m)) }));
  const addMap = () => setC((x) => ({ ...x, maps_to: [...(x.maps_to ?? []), { system: "ICD10CM", code: "" }] }));
  const rmMap = (i: number) => setC((x) => ({ ...x, maps_to: (x.maps_to ?? []).filter((_, j) => j !== i) }));

  return (
    <div className="rounded-lg border-2 border-ace-200 bg-ace-50/40 p-3 space-y-2">
      <div className="grid grid-cols-2 gap-2">
        <input className="rounded border border-slate-200 px-2 py-1.5 text-sm" placeholder="Concept name (e.g. Pulmonary embolism)"
          value={c.name ?? ""} onChange={(e) => setC((x) => ({ ...x, name: e.target.value }))} />
        <select className="rounded border border-slate-200 px-2 py-1.5 text-sm" value={c.semantic_type ?? ""}
          onChange={(e) => setC((x) => ({ ...x, semantic_type: e.target.value }))}>
          <option value="">Semantic type…</option>
          {semanticTypes.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
      <div>
        <div className="text-[11px] uppercase tracking-wide text-slate-400 mb-1">Maps to codes (grounds the agent)</div>
        <div className="space-y-1.5">
          {maps.map((m, i) => (
            <div key={i} className="flex items-center gap-2">
              <select className="rounded border border-slate-200 px-2 py-1 text-sm" value={m.system}
                onChange={(e) => setMap(i, "system", e.target.value)}>
                {["ICD10CM", "CPT", "HCPCS"].map((s) => <option key={s}>{s}</option>)}
              </select>
              <input className="rounded border border-slate-200 px-2 py-1 text-sm font-mono w-32" placeholder="code"
                value={m.code} onChange={(e) => setMap(i, "code", e.target.value)} />
              <button className="text-rose-400 hover:text-rose-600" onClick={() => rmMap(i)}><Trash2 size={14} /></button>
            </div>
          ))}
          <button className="text-xs text-ace-600 hover:underline flex items-center gap-1" onClick={addMap}>
            <Plus size={12} /> add mapped code
          </button>
        </div>
      </div>
      <div className="flex justify-end gap-2">
        <button className="btn-ghost py-1.5" onClick={onClose}><X size={14} /> Cancel</button>
        <button className="btn-primary py-1.5" disabled={!c.name || save.isPending} onClick={() => save.mutate()}>
          {save.isPending ? <Spinner className="h-4 w-4" /> : <Save size={14} />} {isNew ? "Create concept" : "Save"}
        </button>
      </div>
      {save.isError && <div className="text-xs text-rose-600">{(save.error as Error).message}</div>}
    </div>
  );
}

function EdgeAdder({ concepts, relTypes, onClose }: {
  concepts: Concept[]; relTypes: string[]; onClose: () => void;
}) {
  const qc = useQueryClient();
  const [src, setSrc] = useState("");
  const [rel, setRel] = useState(relTypes[0] ?? "is_a");
  const [dst, setDst] = useState("");
  const add = useMutation({
    mutationFn: () => api.createEdge({ src_cui: src, rel, dst_cui: dst }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["edges"] });
      qc.invalidateQueries({ queryKey: ["kg"] });
      onClose();
    },
  });
  return (
    <div className="rounded-lg border-2 border-ace-200 bg-ace-50/40 p-3 space-y-2">
      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2">
        <select className="rounded border border-slate-200 px-2 py-1.5 text-sm" value={src} onChange={(e) => setSrc(e.target.value)}>
          <option value="">Source concept…</option>
          {concepts.map((c) => <option key={c.cui} value={c.cui}>{c.name}</option>)}
        </select>
        <select className="rounded border border-slate-200 px-2 py-1.5 text-sm text-ace-700 font-medium" value={rel} onChange={(e) => setRel(e.target.value)}>
          {relTypes.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
        <select className="rounded border border-slate-200 px-2 py-1.5 text-sm" value={dst} onChange={(e) => setDst(e.target.value)}>
          <option value="">Target concept…</option>
          {concepts.map((c) => <option key={c.cui} value={c.cui}>{c.name}</option>)}
        </select>
      </div>
      <div className="flex justify-end gap-2">
        <button className="btn-ghost py-1.5" onClick={onClose}><X size={14} /> Cancel</button>
        <button className="btn-primary py-1.5" disabled={!src || !dst || add.isPending} onClick={() => add.mutate()}>
          {add.isPending ? <Spinner className="h-4 w-4" /> : <GitBranch size={14} />} Add relationship
        </button>
      </div>
      {add.isError && <div className="text-xs text-rose-600">{(add.error as Error).message}</div>}
    </div>
  );
}

export default function KgBuilder() {
  const qc = useQueryClient();
  const { data: concepts, isLoading } = useQuery({ queryKey: ["concepts"], queryFn: api.concepts });
  const { data: edges } = useQuery({ queryKey: ["edges"], queryFn: api.edges });
  const { data: meta } = useQuery({ queryKey: ["ontoMeta"], queryFn: api.ontologyMeta });
  const [editing, setEditing] = useState<number | "new" | null>(null);
  const [addingEdge, setAddingEdge] = useState(false);

  const delC = useMutation({
    mutationFn: (id: number) => api.deleteConcept(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["concepts"] });
      qc.invalidateQueries({ queryKey: ["edges"] });
      qc.invalidateQueries({ queryKey: ["kg"] });
      qc.invalidateQueries({ queryKey: ["refsum"] });
    },
  });
  const delE = useMutation({
    mutationFn: (id: number) => api.deleteEdge(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["edges"] }); qc.invalidateQueries({ queryKey: ["kg"] }); },
  });

  const nameByCui = useMemo(() => {
    const m: Record<string, string> = {};
    (concepts ?? []).forEach((c) => (m[c.cui] = c.name));
    return m;
  }, [concepts]);

  const semanticTypes = meta?.semantic_types ?? [];
  const relTypes = meta?.rel_types ?? ["is_a"];

  if (isLoading) return <div className="grid place-items-center h-40"><Spinner className="h-5 w-5 text-ace-500" /></div>;

  return (
    <div className="space-y-4">
      <div className="rounded-lg bg-indigo-50 border border-indigo-200 p-2.5 text-xs text-indigo-800 flex items-center gap-2">
        <Sparkles size={14} /> Concepts and relationships here are read by Graph-RAG on <b>every coding run</b>.
        A new concept with mapped codes is surfaced to the coding agent (as an ontology path) on the next chart that mentions it —
        building the KG here directly changes what the agent is grounded on. Production swaps in licensed SNOMED CT / UMLS at the same shape.
      </div>

      {/* Concepts */}
      <div className="card overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2"><Boxes size={16} className="text-indigo-500" />
            <span className="font-semibold text-slate-700 text-sm">Ontology concepts</span>
            <span className="text-xs text-slate-400">· {concepts?.length ?? 0}</span>
          </div>
          <button className="btn-primary py-1.5" onClick={() => setEditing("new")}><Plus size={14} /> Add concept</button>
        </div>
        {editing === "new" && <div className="p-3 border-b border-slate-100"><ConceptEditor initial={BLANK} semanticTypes={semanticTypes} onClose={() => setEditing(null)} /></div>}
        <table className="w-full text-sm">
          <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
            <th className="px-3 py-2">Concept</th><th className="px-3 py-2">Semantic type</th>
            <th className="px-3 py-2">CUI</th><th className="px-3 py-2">Maps to</th><th className="px-3 py-2"></th>
          </tr></thead>
          <tbody className="divide-y divide-slate-100">
            {(concepts ?? []).map((c) => editing === c.id ? (
              <tr key={c.id}><td colSpan={5} className="p-2"><ConceptEditor initial={c} semanticTypes={semanticTypes} onClose={() => setEditing(null)} /></td></tr>
            ) : (
              <tr key={c.id} className="hover:bg-slate-50/70">
                <td className="px-3 py-2 font-medium text-slate-700">{c.name}</td>
                <td className="px-3 py-2 text-xs text-slate-500">{c.semantic_type || "—"}</td>
                <td className="px-3 py-2 font-mono text-xs text-slate-400">{c.cui}</td>
                <td className="px-3 py-2 text-xs">
                  {(c.maps_to ?? []).length ? c.maps_to.map((m, i) => (
                    <span key={i} className="pill bg-blue-50 text-blue-700 ring-1 ring-blue-200 mr-1">{m.system}:{m.code}</span>
                  )) : <span className="text-slate-300">unmapped</span>}
                </td>
                <td className="px-3 py-2 text-right whitespace-nowrap">
                  <button className="btn-ghost py-1 mr-1" onClick={() => setEditing(c.id)}>Edit</button>
                  <button className="text-rose-400 hover:text-rose-600" onClick={() => delC.mutate(c.id)}><Trash2 size={14} /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Edges */}
      <div className="card overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2"><Network size={16} className="text-indigo-500" />
            <span className="font-semibold text-slate-700 text-sm">Relationships</span>
            <span className="text-xs text-slate-400">· {edges?.length ?? 0}</span>
          </div>
          <button className="btn-primary py-1.5" disabled={(concepts?.length ?? 0) < 2} onClick={() => setAddingEdge(true)}>
            <Plus size={14} /> Add relationship
          </button>
        </div>
        {addingEdge && <div className="p-3 border-b border-slate-100"><EdgeAdder concepts={concepts ?? []} relTypes={relTypes} onClose={() => setAddingEdge(false)} /></div>}
        <div className="p-3 flex flex-wrap gap-2">
          {(edges ?? []).length === 0 && !addingEdge && <span className="text-sm text-slate-400">No relationships yet.</span>}
          {(edges ?? []).map((e: Edge) => (
            <span key={e.id} className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white pl-3 pr-1.5 py-1 text-xs">
              <span className="font-medium text-slate-700">{nameByCui[e.src_cui] || e.src_cui}</span>
              <span className="text-ace-600 font-mono">—{e.rel}→</span>
              <span className="font-medium text-slate-700">{nameByCui[e.dst_cui] || e.dst_cui}</span>
              <button className="ml-1 text-slate-300 hover:text-rose-500" onClick={() => delE.mutate(e.id)}><X size={12} /></button>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
