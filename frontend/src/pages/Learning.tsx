import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { GraduationCap, ArrowRight, Trash2 } from "lucide-react";
import { api } from "../api";
import { Spinner, SystemBadge } from "../lib";

export default function Learning() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["learning"], queryFn: api.learning });
  const toggle = useMutation({
    mutationFn: ({ id, applied }: { id: string; applied: boolean }) => api.patchLearning(id, applied),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["learning"] }),
  });
  const del = useMutation({
    mutationFn: (id: string) => api.deleteLearning(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["learning"] }),
  });

  const rows = data ?? [];
  const applied = rows.filter((r: any) => r.applied).length;

  return (
    <div className="space-y-4 fadeup">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Closed-Loop Learning</h1>
          <p className="text-sm text-slate-500">
            Captured coder corrections that ground future coding (Graph-RAG exemplars). Toggle one off to
            withdraw it from retrieval; in production these batch into the SLM fine-tune pipeline (24–48h).
          </p>
        </div>
        <div className="flex gap-3">
          <div className="card px-4 py-2 text-center"><div className="text-xl font-extrabold">{rows.length}</div><div className="text-[10px] uppercase tracking-wide text-slate-400">captured</div></div>
          <div className="card px-4 py-2 text-center"><div className="text-xl font-extrabold text-emerald-600">{applied}</div><div className="text-[10px] uppercase tracking-wide text-slate-400">active</div></div>
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-200 flex items-center gap-2">
          <GraduationCap size={16} className="text-ace-600" />
          <span className="font-semibold text-slate-700 text-sm">Learned corrections</span>
        </div>
        {isLoading ? (
          <div className="p-10 text-center"><Spinner className="h-5 w-5 mx-auto text-ace-500" /></div>
        ) : rows.length ? (
          <table className="w-full text-sm">
            <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
              <th className="px-4 py-3">Specialty</th><th className="px-4 py-3">Correction</th>
              <th className="px-4 py-3">Reason</th><th className="px-4 py-3">Pattern</th>
              <th className="px-4 py-3">Active</th><th className="px-4 py-3"></th>
            </tr></thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((le: any) => (
                <tr key={le.id} className={clsx(!le.applied && "opacity-50")}>
                  <td className="px-4 py-3 text-slate-600">{le.specialty}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <SystemBadge system={le.code_system} />
                      {le.wrong_code && <span className="font-mono text-slate-400 line-through">{le.wrong_code}</span>}
                      <ArrowRight size={13} className="text-slate-400" />
                      <span className="font-mono font-bold text-emerald-600">{le.correct_code}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-slate-600 max-w-md text-xs">{le.reason}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-400">{le.pattern_key}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => toggle.mutate({ id: le.id, applied: !le.applied })}
                      className={clsx("relative inline-flex h-5 w-9 items-center rounded-full transition-colors", le.applied ? "bg-emerald-500" : "bg-slate-300")}
                      title={le.applied ? "Active — used in retrieval" : "Withdrawn from retrieval"}>
                      <span className={clsx("inline-block h-4 w-4 transform rounded-full bg-white transition-transform", le.applied ? "translate-x-4" : "translate-x-0.5")} />
                    </button>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button className="text-rose-400 hover:text-rose-600" onClick={() => del.mutate(le.id)}><Trash2 size={14} /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="p-8 text-center text-sm text-slate-400">
            No corrections yet. Override a code on any encounter to populate this.
          </div>
        )}
      </div>
    </div>
  );
}
