import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { Clock, AlertTriangle, UserCheck, Flag, Stethoscope, ArrowRight, Layers } from "lucide-react";
import { api } from "../api";
import { Spinner, LaneBadge } from "../lib";
import type { CtItem, CtQueue } from "../types";

function fmtAge(min: number) {
  if (min < 60) return `${Math.round(min)}m`;
  const h = Math.floor(min / 60);
  return `${h}h ${Math.round(min % 60)}m`;
}
function slaStyle(s: string) {
  if (s === "breached") return "bg-rose-50 text-rose-700 ring-rose-200";
  if (s === "at_risk") return "bg-amber-50 text-amber-700 ring-amber-200";
  return "bg-emerald-50 text-emerald-700 ring-emerald-200";
}

export default function ControlTower() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["controlTower"], queryFn: api.controlTower, refetchInterval: 15000 });
  const [activeKey, setActiveKey] = useState<string>("QA");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [assignee, setAssignee] = useState("");

  const assign = useMutation({
    mutationFn: () => api.assign(Array.from(selected), assignee),
    onSuccess: () => {
      setSelected(new Set());
      qc.invalidateQueries({ queryKey: ["controlTower"] });
      qc.invalidateQueries({ queryKey: ["encounters"] });
    },
  });

  const active: CtQueue | undefined = useMemo(
    () => data?.queues.find((q) => q.key === activeKey) ?? data?.queues[0],
    [data, activeKey]
  );

  if (isLoading || !data) return <div className="grid place-items-center h-64"><Spinner className="h-6 w-6 text-ace-500" /></div>;

  const toggle = (id: string) =>
    setSelected((s) => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n; });
  const items = active?.items ?? [];
  const allSel = items.length > 0 && items.every((i) => selected.has(i.run_id));

  return (
    <div className="space-y-4 fadeup">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Control Tower</h1>
          <p className="text-sm text-slate-500">Live work queues, SLA aging, and workforce assignment. Auto-refreshes.</p>
        </div>
        <div className="flex gap-3">
          <Stat label="In flight" value={data.summary.total} />
          <Stat label="Unassigned" value={data.summary.unassigned} tone={data.summary.unassigned ? "amber" : "slate"} />
          <Stat label="SLA breached" value={data.summary.breached} tone={data.summary.breached ? "rose" : "slate"} />
        </div>
      </div>

      {/* Queue selector */}
      <div className="grid grid-cols-5 gap-3">
        {data.queues.map((q) => (
          <button key={q.key} onClick={() => { setActiveKey(q.key); setSelected(new Set()); }}
            className={clsx("card p-3 text-left transition-shadow", active?.key === q.key ? "ring-2 ring-ace-400" : "hover:shadow-md")}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-600">{q.label}</span>
              {q.breached > 0 && <span className="pill bg-rose-50 text-rose-700 ring-1 ring-rose-200"><AlertTriangle size={10} />{q.breached}</span>}
            </div>
            <div className="mt-1 text-2xl font-extrabold tabular-nums">{q.count}</div>
            <div className="text-[10px] text-slate-400">SLA {fmtAge(q.sla_target_min)}</div>
          </button>
        ))}
      </div>

      {/* Assignment bar */}
      {selected.size > 0 && (
        <div className="card p-3 flex items-center gap-3 bg-ace-50 border-ace-200">
          <UserCheck size={16} className="text-ace-600" />
          <span className="text-sm font-medium text-slate-700">{selected.size} selected</span>
          <select value={assignee} onChange={(e) => setAssignee(e.target.value)}
            className="rounded-md border border-slate-200 px-2 py-1.5 text-sm">
            <option value="">Assign to…</option>
            {data.roster.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
          <button className="btn-primary py-1.5" disabled={!assignee || assign.isPending} onClick={() => assign.mutate()}>
            {assign.isPending ? <Spinner className="h-4 w-4" /> : <UserCheck size={14} />} Assign
          </button>
          <button className="btn-ghost py-1.5" onClick={() => setSelected(new Set())}>Clear</button>
        </div>
      )}

      {/* Queue items */}
      <div className="card overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-200 flex items-center gap-2">
          <Layers size={16} className="text-slate-400" />
          <span className="font-semibold text-slate-700 text-sm">{active?.label}</span>
          <span className="text-xs text-slate-400">· {items.length} items · sorted by age</span>
        </div>
        {items.length === 0 ? (
          <div className="p-8 text-center text-sm text-slate-400">Queue is empty.</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
                <th className="px-3 py-2 w-8"><input type="checkbox" checked={allSel}
                  onChange={() => setSelected(allSel ? new Set() : new Set(items.map((i) => i.run_id)))} /></th>
                <th className="px-3 py-2">Patient / MRN</th>
                <th className="px-3 py-2">Specialty</th>
                <th className="px-3 py-2">Lane</th>
                <th className="px-3 py-2">Age in queue</th>
                <th className="px-3 py-2">SLA</th>
                <th className="px-3 py-2">Owner</th>
                <th className="px-3 py-2"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((it: CtItem) => (
                <tr key={it.run_id} className={clsx("hover:bg-slate-50/70", selected.has(it.run_id) && "bg-ace-50/40")}>
                  <td className="px-3 py-2"><input type="checkbox" checked={selected.has(it.run_id)} onChange={() => toggle(it.run_id)} /></td>
                  <td className="px-3 py-2">
                    <div className="font-medium text-slate-800 flex items-center gap-1.5">
                      {it.patient_name}
                      {it.escalated && <Flag size={12} className="text-amber-500" />}
                      {it.has_open_cdi && <Stethoscope size={12} className="text-ace-500" />}
                    </div>
                    <div className="text-xs text-slate-400 font-mono">{it.mrn} · {it.payer}</div>
                  </td>
                  <td className="px-3 py-2 text-slate-600">{it.specialty}</td>
                  <td className="px-3 py-2"><LaneBadge lane={it.lane as any} /></td>
                  <td className="px-3 py-2 text-slate-600"><Clock size={12} className="inline mr-1 text-slate-400" />{fmtAge(it.age_minutes)}</td>
                  <td className="px-3 py-2"><span className={clsx("pill ring-1", slaStyle(it.sla_status))}>{it.sla_status.replace("_", " ")}</span></td>
                  <td className="px-3 py-2 text-xs">{it.assigned_to || <span className="text-slate-300">unassigned</span>}</td>
                  <td className="px-3 py-2 text-right"><Link to={`/encounter/${it.encounter_id}`} className="btn-ghost py-1"><ArrowRight size={13} /></Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function Stat({ label, value, tone = "slate" }: { label: string; value: number; tone?: string }) {
  const c = tone === "rose" ? "text-rose-600" : tone === "amber" ? "text-amber-600" : "text-slate-900";
  return (
    <div className="card px-4 py-2 text-center">
      <div className={clsx("text-xl font-extrabold tabular-nums", c)}>{value}</div>
      <div className="text-[10px] uppercase tracking-wide text-slate-400">{label}</div>
    </div>
  );
}
