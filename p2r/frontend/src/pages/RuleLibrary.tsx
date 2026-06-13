import { useQuery } from "@tanstack/react-query";
import { Library } from "lucide-react";
import { api } from "../api";
import { CodeChips, Spinner } from "../lib";

export default function RuleLibrary() {
  const { data: rules, isLoading } = useQuery({ queryKey: ["rule-library"], queryFn: api.ruleLibrary });

  return (
    <div className="fadeup space-y-5">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Rule Library</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          The existing deployed rules that candidate recommendations are reconciled against. These are
          the source of NET_NEW / UPDATE / DUPLICATE / CONFLICT verdicts.
        </p>
      </div>

      {isLoading ? (
        <div className="card p-8 grid place-items-center"><Spinner className="h-6 w-6 text-ace-500" /></div>
      ) : (rules ?? []).length === 0 ? (
        <div className="card p-8 text-center text-sm text-slate-400">Rule library is empty.</div>
      ) : (
        <div className="space-y-3">
          {rules!.map((r) => (
            <div key={r.id} className="card p-4 flex items-start justify-between gap-4">
              <div className="space-y-2 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="pill bg-ace-50 text-ace-700 ring-1 ring-ace-100 font-mono">{r.id}</span>
                  <span className="text-xs text-slate-500">{r.payer}</span>
                  <span className="pill bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200">{r.status}</span>
                </div>
                <div className="text-sm text-slate-700">{r.title}</div>
                <CodeChips codes={r.code_sets} />
              </div>
              <Library size={18} className="text-slate-300 shrink-0" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
