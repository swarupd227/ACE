import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Database, Activity, TrendingUp, ArrowUpRight, Spline } from "lucide-react";
import { api } from "../api";
import { Spinner, pct } from "../lib";
import type { DenialSignal } from "../types";
import clsx from "clsx";

function PatternBadge({ p }: { p: string }) {
  const map: Record<string, string> = {
    SPIKE: "bg-rose-50 text-rose-700 ring-rose-200",
    EMERGING: "bg-amber-50 text-amber-700 ring-amber-200",
    PERSISTENT: "bg-violet-50 text-violet-700 ring-violet-200",
  };
  return <span className={clsx("pill ring-1", map[p] || "bg-slate-100 text-slate-600 ring-slate-200")}>{p}</span>;
}

export default function DenialDiscovery() {
  const qc = useQueryClient();
  const nav = useNavigate();
  const [err, setErr] = useState("");
  const { data: signals } = useQuery({ queryKey: ["denial-signals"], queryFn: () => api.denialSignals() });

  const load = useMutation({ mutationFn: api.denialsLoadSample, onError: (e: any) => setErr(e.message) });
  const detect = useMutation({
    mutationFn: api.denialsDetect,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["denial-signals"] }),
    onError: (e: any) => setErr(e.message),
  });
  const promote = useMutation({
    mutationFn: (id: string) => api.promoteSignal(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["denial-signals"] }); qc.invalidateQueries({ queryKey: ["recommendations"] }); nav("/review"); },
    onError: (e: any) => setErr(e.message),
  });

  return (
    <div className="fadeup space-y-5">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Denial Pattern Discovery</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Statistics-first mining over pooled 835 remittance data: a two-proportion changepoint test
          surfaces emerging denial patterns and proposes candidate rules. PHI-free synthetic data.
        </p>
      </div>

      {err && <div className="card p-3 border-rose-200 bg-rose-50 text-sm text-rose-700">{err}</div>}

      <div className="flex flex-wrap items-center gap-3">
        <button className="btn-ghost" disabled={load.isPending} onClick={() => { setErr(""); load.mutate(); }}>
          {load.isPending ? <Spinner className="h-4 w-4" /> : <Database size={16} />} Load 835 sample
        </button>
        <button className="btn-primary" disabled={detect.isPending} onClick={() => { setErr(""); detect.mutate(); }}>
          {detect.isPending ? <Spinner className="h-4 w-4" /> : <Activity size={16} />} Detect signals
        </button>
        {detect.data && (
          <span className="text-xs text-slate-500">
            {detect.data.signals} signals from {detect.data.remittance_lines.toLocaleString()} lines · recent window {detect.data.recent_window_days}d
          </span>
        )}
      </div>

      {(signals ?? []).length === 0 ? (
        <div className="card p-8 text-center text-sm text-slate-400">
          No signals yet — load the 835 sample, then detect.
        </div>
      ) : (
        <div className="space-y-3">
          {signals!.map((s) => <SignalCard key={s.id} s={s} onPromote={() => promote.mutate(s.id)} promoting={promote.isPending} />)}
        </div>
      )}
    </div>
  );
}

function SignalCard({ s, onPromote, promoting }: { s: DenialSignal; onPromote: () => void; promoting: boolean }) {
  return (
    <div className="card p-4 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="pill bg-slate-800 text-white">#{s.rank}</span>
          <PatternBadge p={s.pattern_type} />
          <span className="pill bg-violet-50 text-violet-700 ring-1 ring-violet-200 font-mono">CPT {s.procedure_code}</span>
          <span className="pill bg-slate-100 text-slate-600 font-mono">CARC {s.denial_carc}</span>
          {s.status === "PROMOTED" && <span className="pill bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200">promoted</span>}
        </div>
        <div className="text-right">
          <div className="text-[11px] text-slate-400 uppercase tracking-wide">score</div>
          <div className="text-lg font-bold text-slate-800 tabular-nums">{s.score}</div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3 text-sm">
        <Stat label="Recent denial rate" value={pct(s.recent_rate)} accent="text-rose-600" icon={<TrendingUp size={13} />} />
        <Stat label="Baseline" value={pct(s.baseline_rate)} />
        <Stat label="Lift" value={`${s.lift}×`} accent="text-amber-600" />
        <Stat label="z-score" value={`${s.z_score}`} icon={<Spline size={13} />} />
      </div>

      <div className="rounded-lg bg-ace-50/60 p-3 text-xs text-slate-600">
        <span className="label">Proposed rule</span>
        <span className="ml-2 pill bg-white ring-1 ring-slate-200">{s.proposed_rule.provision_type}</span>
        <div className="mt-1">{s.proposed_rule.summary}</div>
      </div>

      <div className="flex items-center justify-between pt-1 border-t border-slate-100">
        <div className="text-xs text-slate-400">
          {s.recent_denials}/{s.recent_total} claims denied in window · {(s.evidence.sample_lines?.length ?? 0)} sample lines
        </div>
        {s.status === "PROMOTED" ? (
          <span className="text-xs text-emerald-600 font-semibold">→ in review queue</span>
        ) : (
          <button className="btn-primary" disabled={promoting} onClick={onPromote}>
            {promoting ? <Spinner className="h-4 w-4" /> : <ArrowUpRight size={15} />} Promote to review
          </button>
        )}
      </div>
    </div>
  );
}

function Stat({ label, value, accent, icon }: { label: string; value: string; accent?: string; icon?: React.ReactNode }) {
  return (
    <div>
      <div className="label flex items-center gap-1">{icon}{label}</div>
      <div className={clsx("font-bold tabular-nums mt-0.5", accent || "text-slate-700")}>{value}</div>
    </div>
  );
}
