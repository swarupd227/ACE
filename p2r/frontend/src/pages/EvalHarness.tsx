import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Play, CheckCircle2, XCircle, History, Activity, FileSearch, ClipboardCheck, Gauge, Trash2, ChevronRight, ChevronDown } from "lucide-react";
import clsx from "clsx";
import { api } from "../api";
import { Spinner, pct, confColor } from "../lib";
import { useRole, can } from "../role";
import EvalConsole from "../components/EvalConsole";
import type { EvalReport } from "../types";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="label">{label}</div>
      <div className="mt-0.5">{children}</div>
    </div>
  );
}

function Metric({ label, v }: { label: string; v: number }) {
  return (
    <div>
      <div className="label">{label}</div>
      <div className={clsx("text-xl font-bold mt-0.5", confColor(v))}>{pct(v)}</div>
    </div>
  );
}

export default function EvalHarness() {
  const { role } = useRole();
  const qc = useQueryClient();
  const [report, setReport] = useState<EvalReport | null>(null);
  const [streaming, setStreaming] = useState(false);
  const [openGolden, setOpenGolden] = useState<string | null>(null);
  const { data: golden } = useQuery({ queryKey: ["eval-golden"], queryFn: api.evalGolden });
  const { data: hist } = useQuery({ queryKey: ["eval-history"], queryFn: api.evalHistory });
  const delGolden = useMutation({ mutationFn: (id: string) => api.deleteGolden(id), onSuccess: () => qc.invalidateQueries({ queryKey: ["eval-golden"] }) });

  const ph = report?.phases;
  return (
    <div className="fadeup space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Evaluation Harness</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Runs the real pipeline against the golden set and scores every phase — extraction (P1),
            denial detection (P2), reconciliation (P3) and confidence calibration. All computed live.
          </p>
        </div>
        {can(role, "run_eval") ? (
          <button className="btn-primary shrink-0" disabled={streaming} onClick={() => setStreaming(true)}>
            {streaming ? <Spinner className="h-4 w-4" /> : <Play size={16} />}
            {streaming ? "Running…" : "Run evaluation"}
          </button>
        ) : <span className="pill bg-slate-100 text-slate-500 shrink-0">read-only ({role})</span>}
      </div>

      {streaming && (
        <EvalConsole
          onClose={() => setStreaming(false)}
          onDone={(r) => { setReport(r); setStreaming(false); qc.invalidateQueries({ queryKey: ["eval-history"] }); }}
        />
      )}

      {ph && (
        <>
          <div className="flex items-center gap-3">
            <div className="text-sm text-slate-500">Overall</div>
            <div className={clsx("text-3xl font-extrabold", confColor(report!.overall_score))}>{pct(report!.overall_score)}</div>
            <div className="text-xs text-slate-400 font-mono">{report!.model_version}</div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="card p-4 space-y-2">
              <div className="flex items-center gap-1.5 font-semibold text-slate-700"><FileSearch size={15} className="text-ace-500" /> P1 · Extraction</div>
              <div className="grid grid-cols-3 gap-2">
                <Metric label="Coverage" v={ph.P1.provision_coverage} />
                <Metric label="Code recall" v={ph.P1.code_recall} />
                <Metric label="Citations" v={ph.P1.citation_validity} />
              </div>
            </div>
            <div className="card p-4 space-y-2">
              <div className="flex items-center gap-1.5 font-semibold text-slate-700"><Activity size={15} className="text-rose-500" /> P2 · Detection</div>
              <div className="grid grid-cols-3 gap-2">
                <Metric label="Recall" v={ph.P2.recall} />
                <Metric label="Precision" v={ph.P2.precision} />
                <div><div className="label">Recovered</div><div className="text-xl font-bold mt-0.5 text-slate-700">{ph.P2.recovered}/{ph.P2.planted}</div></div>
              </div>
            </div>
            <div className="card p-4 space-y-2">
              <div className="flex items-center gap-1.5 font-semibold text-slate-700"><ClipboardCheck size={15} className="text-emerald-500" /> P3 · Reconciliation</div>
              <div className="grid grid-cols-2 gap-2">
                <Metric label="Verdict acc" v={ph.P3.verdict_accuracy} />
                <Metric label="Attention acc" v={ph.P3.attention_accuracy} />
              </div>
            </div>
          </div>

          <div className="card p-4 flex items-center gap-6 text-sm">
            <div className="flex items-center gap-1.5 font-semibold text-slate-700"><Gauge size={15} className="text-violet-500" /> Calibration</div>
            <div>mean conf when <b className="text-emerald-600">correct</b>: {ph.calibration.mean_conf_correct != null ? pct(ph.calibration.mean_conf_correct) : "—"} ({ph.calibration.n_correct})</div>
            <div>when <b className="text-rose-600">wrong</b>: {ph.calibration.mean_conf_wrong != null ? pct(ph.calibration.mean_conf_wrong) : "—"} ({ph.calibration.n_wrong})</div>
          </div>

          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
                <tr><th className="text-left font-semibold px-4 py-2.5">Provision</th><th className="text-left font-semibold px-4 py-2.5">Expected → Actual</th><th className="text-left font-semibold px-4 py-2.5">Codes</th><th className="text-right font-semibold px-4 py-2.5">Conf</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {ph.cases.map((c) => (
                  <tr key={c.provision_type} className="hover:bg-slate-50">
                    <td className="px-4 py-2.5 font-semibold text-slate-700">{c.provision_type}</td>
                    <td className="px-4 py-2.5"><div className="flex items-center gap-1.5">{c.verdict_ok ? <CheckCircle2 size={15} className="text-emerald-500" /> : <XCircle size={15} className="text-rose-500" />}<span className="font-mono text-xs">{c.expected_verdict} → {c.actual_verdict ?? "—"}</span></div></td>
                    <td className="px-4 py-2.5">{c.missing_codes.length === 0 ? <span className="pill bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200">all present</span> : <span className="pill bg-rose-50 text-rose-700 ring-1 ring-rose-200">missing {c.missing_codes.join(", ")}</span>}</td>
                    <td className="px-4 py-2.5 text-right"><span className={clsx("font-bold tabular-nums", c.confidence != null ? confColor(c.confidence) : "text-slate-400")}>{c.confidence != null ? pct(c.confidence) : "—"}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Run history / drift */}
      <div className="space-y-2">
        <div className="flex items-center gap-1.5 label"><History size={13} /> Run history & model drift</div>
        {(hist ?? []).length === 0 ? (
          <div className="card p-4 text-sm text-slate-400">No runs yet.</div>
        ) : (
          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
                <tr><th className="text-left font-semibold px-4 py-2.5">When</th><th className="text-left font-semibold px-4 py-2.5">Model</th><th className="text-right font-semibold px-4 py-2.5">Overall</th><th className="text-right font-semibold px-4 py-2.5">P1</th><th className="text-right font-semibold px-4 py-2.5">P2 recall</th><th className="text-right font-semibold px-4 py-2.5">P3 verdict</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {hist!.map((r, i) => (
                  <tr key={r.run_id ?? i} className="hover:bg-slate-50">
                    <td className="px-4 py-2.5 text-xs text-slate-400 tabular-nums">{r.created_at?.slice(0, 19).replace("T", " ")}</td>
                    <td className="px-4 py-2.5 font-mono text-xs">{r.model_version}</td>
                    <td className={clsx("px-4 py-2.5 text-right font-bold", confColor(r.overall_score))}>{pct(r.overall_score)}</td>
                    <td className="px-4 py-2.5 text-right tabular-nums">{pct(r.phases.P1.provision_coverage)}</td>
                    <td className="px-4 py-2.5 text-right tabular-nums">{pct(r.phases.P2.recall)}</td>
                    <td className="px-4 py-2.5 text-right tabular-nums">{pct(r.phases.P3.verdict_accuracy)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Golden set manager */}
      <div className="space-y-2">
        <div className="label">Golden set ({golden?.length ?? 0} adjudicated cases) — click a row to expand</div>
        {(golden ?? []).map((g, i) => {
          const id = g.id ?? String(i);
          const open = openGolden === id;
          return (
            <div key={id} className="card overflow-hidden">
              <div className="p-3 flex items-center gap-3 text-sm cursor-pointer hover:bg-slate-50"
                onClick={() => setOpenGolden(open ? null : id)}>
                {open ? <ChevronDown size={15} className="text-slate-400 shrink-0" /> : <ChevronRight size={15} className="text-slate-400 shrink-0" />}
                <span className="pill bg-ace-50 text-ace-700 ring-1 ring-ace-100 w-32 justify-center">{g.provision_type}</span>
                <span className="font-mono text-xs text-slate-500">{g.expected_verdict}</span>
                <span className="text-xs text-slate-400 flex-1 truncate">{g.note}</span>
                {can(role, "admin") && g.id && (
                  <button className="btn-ghost text-rose-600 py-1" onClick={(e) => { e.stopPropagation(); delGolden.mutate(g.id!); }}><Trash2 size={14} /></button>
                )}
              </div>
              {open && (
                <div className="px-4 pb-3 pt-1 border-t border-slate-100 grid grid-cols-2 gap-x-6 gap-y-2 text-sm fadeup">
                  <Field label="Provision type"><span className="font-mono">{g.provision_type}</span></Field>
                  <Field label="Expected reconciliation verdict"><span className="font-mono">{g.expected_verdict}</span></Field>
                  <Field label="Expected codes">
                    {g.expected_codes.length ? (
                      <div className="flex flex-wrap gap-1">
                        {g.expected_codes.map((c) => <span key={c} className="pill bg-violet-50 text-violet-700 ring-1 ring-violet-200 font-mono">{c}</span>)}
                      </div>
                    ) : <span className="text-slate-400">none</span>}
                  </Field>
                  <Field label="Expected 'needs attention'">
                    <span className={clsx("pill ring-1", g.expected_attention ? "bg-rose-50 text-rose-700 ring-rose-200" : "bg-slate-100 text-slate-600 ring-slate-200")}>
                      {g.expected_attention ? "yes" : "no"}
                    </span>
                  </Field>
                  <div className="col-span-2"><Field label="Adjudicator note"><span className="text-slate-600">{g.note}</span></Field></div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
