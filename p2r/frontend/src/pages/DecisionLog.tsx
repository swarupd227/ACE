import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ScrollText, Lock } from "lucide-react";
import clsx from "clsx";
import { api } from "../api";

const PHASES = ["", "P1", "P2", "P3", "P4", "UX"];

function PhaseBadge({ p }: { p: string }) {
  const map: Record<string, string> = {
    P1: "bg-sky-50 text-sky-700 ring-sky-200",
    P2: "bg-rose-50 text-rose-700 ring-rose-200",
    P3: "bg-ace-50 text-ace-700 ring-ace-100",
    P4: "bg-emerald-50 text-emerald-700 ring-emerald-200",
    UX: "bg-amber-50 text-amber-700 ring-amber-200",
  };
  return <span className={clsx("pill ring-1 font-mono", map[p] || "bg-slate-100 text-slate-600 ring-slate-200")}>{p}</span>;
}

export default function DecisionLog() {
  const [phase, setPhase] = useState("");
  const { data: entries } = useQuery({ queryKey: ["audit", phase], queryFn: () => api.audit(phase) });

  return (
    <div className="fadeup space-y-5">
      <div>
        <h1 className="text-xl font-bold text-slate-800 flex items-center gap-2">
          Decision Log <Lock size={15} className="text-slate-400" />
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Append-only governance ledger across every phase — who did what, when, with full lineage.
          Immutable: entries are never updated or deleted.
        </p>
      </div>

      <div className="flex items-center gap-2 text-sm">
        <span className="label">Phase</span>
        <select className="rounded-lg border border-slate-200 px-2 py-1.5 text-sm" value={phase} onChange={(e) => setPhase(e.target.value)}>
          {PHASES.map((p) => <option key={p} value={p}>{p || "All"}</option>)}
        </select>
        <span className="ml-auto text-xs text-slate-400">{entries?.length ?? 0} entries</span>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
            <tr>
              <th className="text-left font-semibold px-4 py-2.5 w-16">Phase</th>
              <th className="text-left font-semibold px-4 py-2.5 w-28">Action</th>
              <th className="text-left font-semibold px-4 py-2.5">Summary</th>
              <th className="text-left font-semibold px-4 py-2.5 w-28">Actor</th>
              <th className="text-left font-semibold px-4 py-2.5 w-36">When</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {(entries ?? []).map((e) => (
              <tr key={e.id} className="hover:bg-slate-50 align-top">
                <td className="px-4 py-2.5"><PhaseBadge p={e.phase} /></td>
                <td className="px-4 py-2.5 font-mono text-xs font-semibold text-slate-700">{e.action}</td>
                <td className="px-4 py-2.5 text-slate-600">{e.summary}</td>
                <td className="px-4 py-2.5 text-xs text-slate-500">{e.actor}</td>
                <td className="px-4 py-2.5 text-xs text-slate-400 tabular-nums">{e.created_at?.slice(0, 19).replace("T", " ")}</td>
              </tr>
            ))}
            {(entries ?? []).length === 0 && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-sm text-slate-400">
                <ScrollText size={20} className="mx-auto mb-2 text-slate-300" /> No log entries yet.
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
