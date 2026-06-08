import { useQuery } from "@tanstack/react-query";
import { GraduationCap, ArrowRight } from "lucide-react";
import { api } from "../api";
import { Spinner, SystemBadge } from "../lib";

export default function Learning() {
  const { data, isLoading } = useQuery({ queryKey: ["learning"], queryFn: api.learning });

  return (
    <div className="space-y-5 fadeup">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900">Closed-Loop Learning</h1>
        <p className="text-sm text-slate-500">
          Coder corrections are captured with a reason and become retrieval exemplars that visibly shift
          later similar charts. In production this runs on a 24–48h batch into the SLM fine-tune pipeline.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-3">
        {["Capture correction + reason", "Index as pattern exemplar (Graph-RAG)", "Next similar chart shifts toward the correction"].map((t, i) => (
          <div key={i} className="card p-4 flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-ace-600 text-white grid place-items-center text-sm font-bold">{i + 1}</div>
            <span className="text-sm text-slate-600">{t}</span>
          </div>
        ))}
      </div>

      <div className="card overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-200 flex items-center gap-2">
          <GraduationCap size={16} className="text-ace-600" />
          <span className="font-semibold text-slate-700 text-sm">Captured corrections</span>
        </div>
        {isLoading ? (
          <div className="p-10 text-center"><Spinner className="h-5 w-5 mx-auto text-ace-500" /></div>
        ) : data && data.length ? (
          <table className="w-full text-sm">
            <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
              <th className="px-4 py-3">Specialty</th><th className="px-4 py-3">Correction</th>
              <th className="px-4 py-3">Reason</th><th className="px-4 py-3">Pattern</th>
            </tr></thead>
            <tbody className="divide-y divide-slate-100">
              {data.map((le: any) => (
                <tr key={le.id}>
                  <td className="px-4 py-3 text-slate-600">{le.specialty}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <SystemBadge system={le.code_system} />
                      {le.wrong_code && <span className="font-mono text-slate-400 line-through">{le.wrong_code}</span>}
                      <ArrowRight size={13} className="text-slate-400" />
                      <span className="font-mono font-bold text-emerald-600">{le.correct_code}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-slate-600 max-w-md">{le.reason}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-400">{le.pattern_key}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="p-8 text-center text-sm text-slate-400">
            No corrections yet. Override a code on any encounter to see the learning loop populate here.
          </div>
        )}
      </div>
    </div>
  );
}
