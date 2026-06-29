import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FlaskConical, Play, Plus, Save, Trash2, X, Database } from "lucide-react";
import { api } from "../api";
import AgentConsole from "../components/AgentConsole";
import { Spinner, pct } from "../lib";
import type { Golden } from "../types";

const FALLBACK_SPECS = ["Radiology", "E&M", "ED", "Pathology", "Surgical"];
const BLANK_G: Partial<Golden> = { specialty: "Radiology", chart_text: "", truth: { icd: [], cpt: [] }, irr: 0.9, ambiguous: false };

function GoldenEditor({ initial, onClose }: { initial: Partial<Golden>; onClose: () => void }) {
  const qc = useQueryClient();
  const { data: meta } = useQuery({ queryKey: ["meta"], queryFn: api.meta });
  const SPECS = meta?.specialties?.length ? meta.specialties : FALLBACK_SPECS;
  const [g, setG] = useState<Partial<Golden>>({ ...initial });
  const isNew = !initial.id;
  const save = useMutation({
    mutationFn: () => (isNew ? api.createGolden(g) : api.updateGolden(initial.id!, g)),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["golden"] }); qc.invalidateQueries({ queryKey: ["evalSummary"] }); onClose(); },
  });
  const setTruth = (k: "icd" | "cpt", v: string) =>
    setG((x) => ({ ...x, truth: { ...(x.truth ?? {}), [k]: v.split(",").map((s) => s.trim()).filter(Boolean) } }));
  return (
    <div className="rounded-lg border-2 border-ace-200 bg-ace-50/40 p-3 space-y-2">
      <div className="grid grid-cols-3 gap-2">
        <select className="rounded border border-slate-200 px-2 py-1.5 text-sm" value={g.specialty} onChange={(e) => setG({ ...g, specialty: e.target.value })}>
          {SPECS.map((s) => <option key={s}>{s}</option>)}
        </select>
        <label className="flex items-center gap-2 text-sm text-slate-600">IRR ceiling
          <input type="number" step={0.01} min={0} max={1} value={g.irr ?? 0.9} onChange={(e) => setG({ ...g, irr: Number(e.target.value) })} className="w-20 rounded border border-slate-200 px-2 py-1 text-sm" />
        </label>
        <label className="flex items-center gap-2 text-sm text-slate-600"><input type="checkbox" checked={!!g.ambiguous} onChange={(e) => setG({ ...g, ambiguous: e.target.checked })} /> ambiguous case</label>
      </div>
      <textarea className="w-full rounded border border-slate-200 px-2 py-1.5 text-sm font-mono" rows={4} placeholder="Adjudicated chart text (the gold report)…" value={g.chart_text ?? ""} onChange={(e) => setG({ ...g, chart_text: e.target.value })} />
      <div className="grid grid-cols-2 gap-2">
        <input className="rounded border border-slate-200 px-2 py-1.5 text-sm font-mono" placeholder="truth ICD-10 (comma)" value={(g.truth?.icd ?? []).join(", ")} onChange={(e) => setTruth("icd", e.target.value)} />
        <input className="rounded border border-slate-200 px-2 py-1.5 text-sm font-mono" placeholder="truth CPT/HCPCS (comma)" value={(g.truth?.cpt ?? []).join(", ")} onChange={(e) => setTruth("cpt", e.target.value)} />
      </div>
      <div className="flex justify-end gap-2">
        <button className="btn-ghost py-1.5" onClick={onClose}><X size={14} /> Cancel</button>
        <button className="btn-primary py-1.5" disabled={!g.chart_text || g.chart_text.length < 40 || save.isPending} onClick={() => save.mutate()}>
          {save.isPending ? <Spinner className="h-4 w-4" /> : <Save size={14} />} {isNew ? "Add case" : "Save"}
        </button>
      </div>
      {save.isError && <div className="text-xs text-rose-600">{(save.error as Error).message}</div>}
    </div>
  );
}

function GoldenManager() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { data } = useQuery({ queryKey: ["golden"], queryFn: api.golden, enabled: open });
  const [editing, setEditing] = useState<number | "new" | null>(null);
  const del = useMutation({ mutationFn: (id: number) => api.deleteGolden(id), onSuccess: () => { qc.invalidateQueries({ queryKey: ["golden"] }); qc.invalidateQueries({ queryKey: ["evalSummary"] }); } });
  return (
    <div className="card overflow-hidden">
      <button className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-50" onClick={() => setOpen((v) => !v)}>
        <span className="flex items-center gap-2 font-semibold text-slate-700 text-sm"><Database size={15} className="text-ace-600" /> Manage golden set (adjudicated truth)</span>
        <span className="text-xs text-slate-400">{open ? "hide" : "curate the eval cases →"}</span>
      </button>
      {open && (
        <div className="border-t border-slate-200 p-3 space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-500">These adjudicated cases ARE the evaluation truth. The harness runs the live pipeline over each and scores against this set.</p>
            <button className="btn-primary py-1.5" onClick={() => setEditing("new")}><Plus size={14} /> Add gold case</button>
          </div>
          {editing === "new" && <GoldenEditor initial={BLANK_G} onClose={() => setEditing(null)} />}
          <div className="space-y-2">
            {(data ?? []).map((g) => editing === g.id ? (
              <GoldenEditor key={g.id} initial={g} onClose={() => setEditing(null)} />
            ) : (
              <div key={g.id} className="rounded-lg border border-slate-200 p-2.5">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="pill bg-ace-50 text-ace-700 ring-1 ring-ace-200">{g.specialty}</span>
                    {(g.truth?.icd ?? []).map((c) => <span key={c} className="pill bg-slate-100 text-slate-600 ring-1 ring-slate-200 font-mono">{c}</span>)}
                    {(g.truth?.cpt ?? []).map((c) => <span key={c} className="pill bg-blue-50 text-blue-700 ring-1 ring-blue-200 font-mono">{c}</span>)}
                    <span className="text-xs text-slate-400">IRR {pct(g.irr)}</span>
                  </div>
                  <div className="flex gap-1 whitespace-nowrap">
                    <button className="btn-ghost py-1" onClick={() => setEditing(g.id)}>Edit</button>
                    <button className="text-rose-400 hover:text-rose-600" onClick={() => del.mutate(g.id)}><Trash2 size={14} /></button>
                  </div>
                </div>
                <p className="mt-1 text-xs text-slate-500 line-clamp-2">{g.chart_text}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function EvalHarness() {
  const { data: summary } = useQuery({ queryKey: ["evalSummary"], queryFn: api.evalSummary });
  const { data: meta } = useQuery({ queryKey: ["meta"], queryFn: api.meta });
  const [showConsole, setShowConsole] = useState(false);
  const [result, setResult] = useState<any>(null);

  return (
    <div className="space-y-5 fadeup">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Evaluation Harness</h1>
          <p className="text-sm text-slate-500">Frozen golden sets, adjudicated truth, honest metrics — accuracy reported against consensus with the IRR ceiling.</p>
        </div>
        <button className="btn-primary" disabled={!meta?.llm_available} onClick={() => setShowConsole(true)}>
          <Play size={16} /> Run evaluation
        </button>
      </div>

      <div className="grid md:grid-cols-3 gap-3">
        {summary?.golden_sets?.map((g: any) => (
          <div key={g.specialty} className="card p-4">
            <div className="flex items-center gap-2 text-slate-800 font-semibold"><FlaskConical size={15} className="text-ace-600" /> {g.specialty}</div>
            <div className="mt-2 text-sm text-slate-500">{g.size} adjudicated cases</div>
            <div className="text-sm text-slate-500">IRR ceiling: <span className="font-semibold text-slate-700">{pct(g.irr_ceiling)}</span></div>
          </div>
        ))}
      </div>

      <GoldenManager />

      {result && (
        <div className="space-y-4">
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="card p-5 bg-ace-900 text-white">
              <div className="text-xs uppercase tracking-wide text-slate-300">Overall chart-level accuracy (vs adjudicated consensus)</div>
              <div className="text-4xl font-extrabold tabular-nums mt-1">{pct(result.overall_chart_accuracy)}</div>
            </div>
            {result.overall_metrics && (
              <div className="card p-5">
                <div className="text-xs uppercase tracking-wide text-slate-400">Code-level micro precision / recall / F1 (all specialties)</div>
                <div className="mt-2 flex gap-8">
                  <div><div className="text-2xl font-extrabold tabular-nums text-slate-700">{pct(result.overall_metrics.overall_prf.precision)}</div><div className="text-[11px] text-slate-400">Precision</div></div>
                  <div><div className="text-2xl font-extrabold tabular-nums text-slate-700">{pct(result.overall_metrics.overall_prf.recall)}</div><div className="text-[11px] text-slate-400">Recall</div></div>
                  <div><div className="text-2xl font-extrabold tabular-nums text-ace-700">{pct(result.overall_metrics.overall_prf.f1)}</div><div className="text-[11px] text-slate-400">F1</div></div>
                </div>
                <div className="mt-2 text-[11px] text-slate-400">
                  Dx F1 {pct(result.overall_metrics.diagnosis_prf.f1)} · Proc F1 {pct(result.overall_metrics.procedure_prf.f1)} · TP {result.overall_metrics.overall_prf.tp} / FP {result.overall_metrics.overall_prf.fp} / FN {result.overall_metrics.overall_prf.fn}
                </div>
              </div>
            )}
          </div>

          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
                <th className="px-4 py-3">Specialty</th><th className="px-4 py-3">Cases</th>
                <th className="px-4 py-3">ICD acc</th><th className="px-4 py-3">CPT/PCS acc</th>
                <th className="px-4 py-3">DRG acc</th><th className="px-4 py-3">RAF acc</th>
                <th className="px-4 py-3">Units acc</th><th className="px-4 py-3">Facility acc</th>
                <th className="px-4 py-3">Chart acc</th><th className="px-4 py-3">P / R / F1</th>
                <th className="px-4 py-3">Citation valid</th>
                <th className="px-4 py-3">STB share</th><th className="px-4 py-3">IRR ceiling</th>
              </tr></thead>
              <tbody className="divide-y divide-slate-100">
                {result.by_specialty.map((s: any) => (
                  <tr key={s.specialty}>
                    <td className="px-4 py-3 font-medium text-slate-700">{s.specialty}</td>
                    <td className="px-4 py-3">{s.size}</td>
                    <td className="px-4 py-3">{pct(s.icd_accuracy)}</td>
                    <td className="px-4 py-3">{pct(s.cpt_accuracy)}</td>
                    <td className="px-4 py-3">{s.drg_accuracy != null ? pct(s.drg_accuracy) : "—"}</td>
                    <td className="px-4 py-3">{s.raf_accuracy != null ? pct(s.raf_accuracy) : "—"}</td>
                    <td className="px-4 py-3">{s.units_accuracy != null ? pct(s.units_accuracy) : "—"}</td>
                    <td className="px-4 py-3">{s.facility_accuracy != null ? pct(s.facility_accuracy) : "—"}</td>
                    <td className="px-4 py-3 font-semibold">{pct(s.chart_accuracy)}</td>
                    <td className="px-4 py-3 tabular-nums text-slate-600">{s.overall_prf ? `${pct(s.overall_prf.precision)} / ${pct(s.overall_prf.recall)} / ${pct(s.overall_prf.f1)}` : "—"}</td>
                    <td className="px-4 py-3">{pct(s.citation_validity)}</td>
                    <td className="px-4 py-3">{pct(s.stb_share)}</td>
                    <td className="px-4 py-3 text-slate-500">{pct(s.irr_ceiling)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="text-xs text-slate-500">
            We report accuracy against post-adjudication consensus, not a single coder — the IRR ceiling
            shows the realistic upper bound where qualified coders themselves disagree. Precision/recall/F1
            are micro-averaged from per-code TP/FP/FN against the adjudicated truth.
          </p>
          {result.ragas && (
            <p className="text-[11px] text-slate-400">
              Ragas adapter: <span className={result.ragas.available ? "text-emerald-600" : "text-slate-500"}>{result.ragas.available ? "available" : "not wired"}</span> — {result.ragas.note}
            </p>
          )}
        </div>
      )}

      {!result && !showConsole && (
        <div className="card p-4 text-sm text-slate-500">
          Run the harness to execute the live pipeline over the frozen golden sets and compute per-specialty
          accuracy, citation validity, and STB share. (Requires the reasoning model.) Progress streams live
          per case — each golden chart is coded by the real pipeline (~20s each).
        </div>
      )}

      {showConsole && (
        <AgentConsole
          url="/eval/run/stream"
          title="golden set"
          label="Evaluation Harness"
          onClose={() => setShowConsole(false)}
          onDone={(d) => setResult(d)}
        />
      )}
    </div>
  );
}
