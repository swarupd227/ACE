import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { FlaskConical, Play, CheckCircle2, XCircle } from "lucide-react";
import { api } from "../api";
import { Spinner, pct, confColor } from "../lib";
import { useRole, can } from "../role";
import type { EvalReport } from "../types";

const METRIC_LABELS: Record<string, string> = {
  provision_coverage: "Provision coverage",
  code_recall: "Code recall",
  citation_rate: "Citation rate",
  verdict_accuracy: "Verdict accuracy",
  attention_accuracy: "Attention accuracy",
};

export default function EvalHarness() {
  const { role } = useRole();
  const [report, setReport] = useState<EvalReport | null>(null);
  const [err, setErr] = useState("");
  const { data: golden } = useQuery({ queryKey: ["eval-golden"], queryFn: api.evalGolden });

  const run = useMutation({
    mutationFn: api.evalRun,
    onSuccess: (r) => { setReport(r); setErr(""); },
    onError: (e: any) => setErr(e.message),
  });

  return (
    <div className="fadeup space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Evaluation Harness</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Runs the real pipeline against an adjudicated golden set — ingest → extract → validate →
            reconcile — and scores it. Nothing is hardcoded; every number comes from this run.
          </p>
        </div>
        {can(role, "run_eval") ? (
          <button className="btn-primary shrink-0" disabled={run.isPending} onClick={() => run.mutate()}>
            {run.isPending ? <Spinner className="h-4 w-4" /> : <Play size={16} />}
            {run.isPending ? "Running…" : "Run evaluation"}
          </button>
        ) : (
          <span className="pill bg-slate-100 text-slate-500 shrink-0">read-only ({role})</span>
        )}
      </div>

      {err && (
        <div className="card p-3 border-rose-200 bg-rose-50 text-sm text-rose-700">{err}</div>
      )}

      {report && (
        <>
          <div className="grid grid-cols-5 gap-3">
            {Object.entries(report.metrics).map(([k, v]) => (
              <div key={k} className="card p-4">
                <div className="label">{METRIC_LABELS[k] ?? k}</div>
                <div className={`text-2xl font-bold mt-1 ${confColor(v)}`}>{pct(v)}</div>
              </div>
            ))}
          </div>
          <div className="text-xs text-slate-500">
            {report.golden_cases} golden cases · {report.provisions_extracted} provisions extracted ·{" "}
            {report.recommendations} recommendations · <span className="font-mono">{report.model_version}</span>
          </div>

          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
                <tr>
                  <th className="text-left font-semibold px-4 py-2.5">Provision</th>
                  <th className="text-left font-semibold px-4 py-2.5">Expected → Actual verdict</th>
                  <th className="text-left font-semibold px-4 py-2.5">Codes</th>
                  <th className="text-left font-semibold px-4 py-2.5">Attention</th>
                  <th className="text-right font-semibold px-4 py-2.5">Conf</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {report.cases.map((c) => (
                  <tr key={c.provision_type} className="hover:bg-slate-50">
                    <td className="px-4 py-2.5">
                      <div className="font-semibold text-slate-700">{c.provision_type}</div>
                      <div className="text-[11px] text-slate-400">{c.note}</div>
                    </td>
                    <td className="px-4 py-2.5">
                      <div className="flex items-center gap-1.5">
                        {c.verdict_ok
                          ? <CheckCircle2 size={15} className="text-emerald-500 shrink-0" />
                          : <XCircle size={15} className="text-rose-500 shrink-0" />}
                        <span className="font-mono text-xs">
                          {c.expected_verdict} → {c.actual_verdict ?? "—"}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-2.5">
                      {c.missing_codes.length === 0
                        ? <span className="pill bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200">all present</span>
                        : <span className="pill bg-rose-50 text-rose-700 ring-1 ring-rose-200">missing {c.missing_codes.join(", ")}</span>}
                    </td>
                    <td className="px-4 py-2.5">
                      {c.attention_ok
                        ? <CheckCircle2 size={15} className="text-emerald-500" />
                        : <XCircle size={15} className="text-rose-500" />}
                    </td>
                    <td className="px-4 py-2.5 text-right">
                      <span className={`font-bold tabular-nums ${c.confidence != null ? confColor(c.confidence) : "text-slate-400"}`}>
                        {c.confidence != null ? pct(c.confidence) : "—"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {!report && (
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-600 mb-3">
            <FlaskConical size={16} className="text-ace-500" /> Golden set ({golden?.length ?? 0} cases)
          </div>
          <div className="space-y-2">
            {(golden ?? []).map((g) => (
              <div key={g.provision_type} className="flex items-center gap-3 text-sm">
                <span className="pill bg-ace-50 text-ace-700 ring-1 ring-ace-100 w-32 justify-center">{g.provision_type}</span>
                <span className="font-mono text-xs text-slate-500">{g.expected_verdict}</span>
                <span className="text-xs text-slate-400">{g.note}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
