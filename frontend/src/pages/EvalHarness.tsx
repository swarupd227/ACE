import { useMutation, useQuery } from "@tanstack/react-query";
import { FlaskConical, Play } from "lucide-react";
import { api } from "../api";
import { Spinner, pct } from "../lib";

export default function EvalHarness() {
  const { data: summary } = useQuery({ queryKey: ["evalSummary"], queryFn: api.evalSummary });
  const { data: meta } = useQuery({ queryKey: ["meta"], queryFn: api.meta });
  const run = useMutation({ mutationFn: api.evalRun });

  return (
    <div className="space-y-5 fadeup">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Evaluation Harness</h1>
          <p className="text-sm text-slate-500">Frozen golden sets, adjudicated truth, honest metrics — accuracy reported against consensus with the IRR ceiling.</p>
        </div>
        <button className="btn-primary" disabled={run.isPending || !meta?.llm_available} onClick={() => run.mutate()}>
          {run.isPending ? <Spinner className="h-4 w-4" /> : <Play size={16} />} Run evaluation
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

      {run.isError && <div className="card p-4 text-rose-600 text-sm">{(run.error as Error).message}</div>}

      {run.data && (
        <div className="space-y-4">
          <div className="card p-5 bg-ace-900 text-white">
            <div className="text-xs uppercase tracking-wide text-slate-300">Overall chart-level accuracy (vs adjudicated consensus)</div>
            <div className="text-4xl font-extrabold tabular-nums mt-1">{pct(run.data.overall_chart_accuracy)}</div>
          </div>

          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
                <th className="px-4 py-3">Specialty</th><th className="px-4 py-3">Cases</th>
                <th className="px-4 py-3">ICD acc</th><th className="px-4 py-3">CPT acc</th>
                <th className="px-4 py-3">Chart acc</th><th className="px-4 py-3">Citation valid</th>
                <th className="px-4 py-3">STB share</th><th className="px-4 py-3">IRR ceiling</th>
              </tr></thead>
              <tbody className="divide-y divide-slate-100">
                {run.data.by_specialty.map((s: any) => (
                  <tr key={s.specialty}>
                    <td className="px-4 py-3 font-medium text-slate-700">{s.specialty}</td>
                    <td className="px-4 py-3">{s.size}</td>
                    <td className="px-4 py-3">{pct(s.icd_accuracy)}</td>
                    <td className="px-4 py-3">{pct(s.cpt_accuracy)}</td>
                    <td className="px-4 py-3 font-semibold">{pct(s.chart_accuracy)}</td>
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
            shows the realistic upper bound where qualified coders themselves disagree.
          </p>
        </div>
      )}

      {!run.data && (
        <div className="card p-4 text-sm text-slate-500">
          Run the harness to execute the live pipeline over the frozen golden sets and compute per-specialty
          accuracy, citation validity, and STB share. (Requires the reasoning model.)
        </div>
      )}
    </div>
  );
}
