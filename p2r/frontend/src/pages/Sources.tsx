import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Radar, RefreshCw, GitCompare, Building2 } from "lucide-react";
import { api } from "../api";
import { Spinner } from "../lib";
import type { PolicyDelta } from "../types";

export default function Sources() {
  const qc = useQueryClient();
  const [err, setErr] = useState("");
  const [last, setLast] = useState<string>("");
  const { data: sources } = useQuery({ queryKey: ["sources"], queryFn: api.sources });
  const { data: deltas } = useQuery({ queryKey: ["deltas"], queryFn: api.deltas });
  const { data: masters } = useQuery({ queryKey: ["payer-master"], queryFn: api.payerMaster });

  const acquire = useMutation({
    mutationFn: (id: string) => api.acquire(id),
    onSuccess: (r) => {
      setLast(r.changed ? `${r.change_type}: ${r.delta?.summary}` : "No change — content identical to last poll");
      qc.invalidateQueries({ queryKey: ["sources"] });
      qc.invalidateQueries({ queryKey: ["deltas"] });
      qc.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (e: any) => setErr(e.message),
  });

  return (
    <div className="fadeup space-y-5">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Sources & Acquisition</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          The acquisition agent polls a registered payer source, detects when the policy content
          changes, ingests the new version and records a structured delta. Payer identity is mastered (MDM).
        </p>
      </div>

      {err && <div className="card p-3 border-rose-200 bg-rose-50 text-sm text-rose-700">{err}</div>}
      {last && <div className="card p-3 border-ace-200 bg-ace-50 text-sm text-ace-700">{last}</div>}

      {/* Sources */}
      <div className="space-y-2">
        <div className="label">Registered sources</div>
        {(sources ?? []).map((s) => (
          <div key={s.id} className="card p-4 flex items-center justify-between gap-4">
            <div className="flex items-start gap-3 min-w-0">
              <Radar size={18} className="text-ace-500 mt-0.5 shrink-0" />
              <div className="min-w-0">
                <div className="text-sm font-semibold text-slate-800 truncate">{s.name}</div>
                <div className="text-xs text-slate-500 font-mono truncate">{s.location}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">
                  {s.payer} · {s.source_type} · {s.cadence} · polled {s.fetch_count}× {s.last_checked && `· last ${s.last_checked.slice(0, 16).replace("T", " ")}`}
                </div>
              </div>
            </div>
            <button className="btn-primary shrink-0" disabled={acquire.isPending} onClick={() => { setErr(""); acquire.mutate(s.id); }}>
              {acquire.isPending ? <Spinner className="h-4 w-4" /> : <RefreshCw size={15} />} Run acquisition
            </button>
          </div>
        ))}
      </div>

      {/* Deltas */}
      <div className="space-y-2">
        <div className="label">Change deltas</div>
        {(deltas ?? []).length === 0 ? (
          <div className="card p-4 text-sm text-slate-400">No changes detected yet — run acquisition twice to see a revision delta.</div>
        ) : (
          (deltas ?? []).map((d) => <DeltaCard key={d.id} d={d} />)
        )}
      </div>

      {/* Payer master */}
      <div className="space-y-2">
        <div className="label">Payer master (MDM)</div>
        {(masters ?? []).map((m) => (
          <div key={m.payer_id} className="card p-3 flex items-center gap-3 text-sm">
            <Building2 size={16} className="text-slate-400" />
            <span className="font-semibold text-slate-700">{m.name}</span>
            <span className="pill bg-slate-100 text-slate-500 font-mono">{m.payer_id}</span>
            <span className="text-xs text-slate-400">LOB: {m.lines_of_business.join(", ")}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function DeltaCard({ d }: { d: PolicyDelta }) {
  return (
    <div className="card p-4 space-y-2">
      <div className="flex items-center gap-2">
        <GitCompare size={15} className="text-violet-500" />
        <span className="pill bg-violet-50 text-violet-700 ring-1 ring-violet-200">{d.change_type}</span>
        <span className="text-sm font-medium text-slate-700">{d.summary}</span>
      </div>
      {d.added.length > 0 && (
        <div className="text-xs"><span className="text-emerald-600 font-semibold">added:</span> {d.added.join(", ")}</div>
      )}
      {d.changed.length > 0 && (
        <div className="space-y-1">
          {d.changed.map((c) => (
            <div key={c.type} className="text-xs text-slate-600">
              <span className="font-semibold text-amber-600">{c.type}</span>
              {c.added_signals?.length ? <span className="ml-1 text-emerald-600">+[{c.added_signals.join(", ")}]</span> : null}
              {c.removed_signals?.length ? <span className="ml-1 text-rose-600">−[{c.removed_signals.join(", ")}]</span> : null}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
