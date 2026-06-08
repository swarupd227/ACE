import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import {
  ArrowLeft, Check, FileText, ShieldCheck, X, ChevronRight, Quote, BookOpen, Sparkles, Scale, History, Cpu, FileSearch,
} from "lucide-react";
import { api } from "../api";
import { ConfidenceBar, LaneBadge, Spinner, SystemBadge, confColor, laneColor, laneLabel, pct } from "../lib";
import type { CodeResult, EncounterDetail as Detail } from "../types";

function Factor({ icon: Icon, label, value }: { icon: any; label: string; value: number }) {
  return (
    <div className="flex items-center gap-2">
      <Icon size={13} className="text-slate-400 shrink-0" />
      <span className="text-xs text-slate-500 w-24 shrink-0">{label}</span>
      <div className="h-1.5 flex-1 rounded-full bg-slate-200 overflow-hidden">
        <div className={clsx("h-full", value >= 0.9 ? "bg-emerald-500" : value >= 0.75 ? "bg-amber-500" : "bg-rose-500")} style={{ width: pct(value) }} />
      </div>
      <span className={clsx("text-xs font-semibold tabular-nums w-8 text-right", confColor(value))}>{pct(value)}</span>
    </div>
  );
}

function CodeCard({ code, onSelect, selected, onHighlight }: {
  code: CodeResult; selected: boolean; onSelect: () => void; onHighlight: (lines: number[] | null) => void;
}) {
  const qc = useQueryClient();
  const { id } = useParams();
  const [showOverride, setShowOverride] = useState(false);
  const [ovCode, setOvCode] = useState("");
  const [ovReason, setOvReason] = useState("");

  const accept = useMutation({
    mutationFn: () => api.accept(code.id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["encounter", id] }),
  });
  const override = useMutation({
    mutationFn: () => api.override(code.id, ovCode.trim(), ovReason.trim()),
    onSuccess: () => {
      setShowOverride(false);
      qc.invalidateQueries({ queryKey: ["encounter", id] });
      qc.invalidateQueries({ queryKey: ["learning"] });
    },
  });

  const statusStyle =
    code.status === "accepted" ? "border-emerald-200" : code.status === "rejected" ? "border-rose-200" : "border-amber-200";
  const allLines = code.chart_citations.flatMap((c) =>
    Array.from({ length: c.line_end - c.line_start + 1 }, (_, i) => c.line_start + i)
  );

  return (
    <div
      className={clsx("rounded-xl border-2 bg-white p-4 transition-shadow", statusStyle, selected && "ring-2 ring-ace-400")}
      onMouseEnter={() => onHighlight(allLines)}
      onMouseLeave={() => onHighlight(null)}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <SystemBadge system={code.code_system} />
          <span className="font-mono text-lg font-bold text-slate-900">
            {code.is_overridden ? code.override_code : code.code}
          </span>
          {code.is_overridden && (
            <span className="pill bg-indigo-50 text-indigo-700 ring-1 ring-indigo-200">overridden</span>
          )}
          {code.modifiers.map((m) => (
            <span key={m} className="pill bg-slate-100 text-slate-600 ring-1 ring-slate-200">-{m}</span>
          ))}
          <span className="pill bg-slate-50 text-slate-500 ring-1 ring-slate-200 capitalize">{code.role}</span>
        </div>
        <div className="text-right shrink-0">
          <div className={clsx("text-lg font-extrabold tabular-nums", confColor(code.confidence))}>{pct(code.confidence)}</div>
          <div className="text-[10px] uppercase tracking-wide text-slate-400">calibrated</div>
        </div>
      </div>

      <p className="mt-1 text-sm text-slate-600">{code.description}</p>

      {/* 4-factor confidence (VHT requirement) */}
      <div className="mt-3 rounded-lg bg-slate-50 p-3 space-y-1.5">
        <div className="text-[10px] uppercase tracking-wide text-slate-400 mb-1">Confidence sources</div>
        <Factor icon={FileSearch} label="Doc match" value={code.conf_doc_match} />
        <Factor icon={History} label="Historical" value={code.conf_historical} />
        <Factor icon={Scale} label="Rule engine" value={code.conf_rule} />
        <Factor icon={Cpu} label="Model" value={code.conf_model} />
      </div>

      {/* Citations */}
      {code.chart_citations.length > 0 && (
        <div className="mt-3">
          <div className="text-[10px] uppercase tracking-wide text-slate-400 flex items-center gap-1 mb-1"><Quote size={11} /> Chart evidence</div>
          {code.chart_citations.map((c, i) => (
            <div
              key={i}
              className="text-xs text-slate-600 border-l-2 border-brand-300 pl-2 py-0.5 mb-1 hover:bg-brand-50 cursor-pointer"
              onMouseEnter={(e) => { e.stopPropagation(); onHighlight(Array.from({ length: c.line_end - c.line_start + 1 }, (_, k) => c.line_start + k)); }}
            >
              <span className="font-semibold text-slate-500">{c.section} L{c.line_start}-{c.line_end}:</span> "{c.text}"
            </div>
          ))}
        </div>
      )}
      {code.guideline_citations.length > 0 && (
        <div className="mt-2">
          <div className="text-[10px] uppercase tracking-wide text-slate-400 flex items-center gap-1 mb-1"><BookOpen size={11} /> Guideline</div>
          {code.guideline_citations.map((g, i) => (
            <div key={i} className="text-xs text-slate-500">
              <span className="font-semibold">{g.source} {g.section}:</span> {g.text}
            </div>
          ))}
        </div>
      )}
      {code.rule_justification && (
        <p className="mt-2 text-xs italic text-slate-500">{code.rule_justification}</p>
      )}

      {/* Validation gates */}
      <div className="mt-3">
        <div className="text-[10px] uppercase tracking-wide text-slate-400 mb-1">Validation gates</div>
        <div className="flex flex-wrap gap-1.5">
          {code.gate_results.map((g) => (
            <span
              key={g.gate}
              title={g.detail}
              className={clsx("pill ring-1", g.passed ? "bg-emerald-50 text-emerald-700 ring-emerald-200" : "bg-rose-50 text-rose-700 ring-rose-200")}
            >
              {g.passed ? <Check size={11} /> : <X size={11} />} {g.gate}
            </span>
          ))}
        </div>
      </div>

      {/* Coder workspace */}
      <div className="mt-3 pt-3 border-t border-slate-100 flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
        <button className="btn-ghost py-1.5" disabled={accept.isPending} onClick={() => accept.mutate()}>
          <Check size={14} /> Accept
        </button>
        <button className="btn-ghost py-1.5" onClick={() => setShowOverride((s) => !s)}>
          Override
        </button>
        {code.accepted_by && <span className="text-xs text-emerald-600">✓ accepted</span>}
      </div>
      {showOverride && (
        <div className="mt-2 rounded-lg bg-slate-50 p-3 space-y-2" onClick={(e) => e.stopPropagation()}>
          <input className="w-full rounded-md border border-slate-200 px-2 py-1.5 text-sm font-mono" placeholder="Correct code (e.g. 71045)" value={ovCode} onChange={(e) => setOvCode(e.target.value)} />
          <input className="w-full rounded-md border border-slate-200 px-2 py-1.5 text-sm" placeholder="Reason (captured for learning)" value={ovReason} onChange={(e) => setOvReason(e.target.value)} />
          <button className="btn-primary py-1.5 w-full" disabled={!ovCode || !ovReason || override.isPending} onClick={() => override.mutate()}>
            {override.isPending ? <Spinner className="h-4 w-4" /> : <Sparkles size={14} />} Submit correction → learning loop
          </button>
        </div>
      )}
    </div>
  );
}

export default function EncounterDetail() {
  const { id } = useParams();
  const { data, isLoading } = useQuery({ queryKey: ["encounter", id], queryFn: () => api.encounter(id!) });
  const [highlight, setHighlight] = useState<number[] | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [showAudit, setShowAudit] = useState(false);

  const highlightSet = useMemo(() => new Set(highlight ?? []), [highlight]);

  if (isLoading || !data) return <div className="grid place-items-center h-64"><Spinner className="h-6 w-6 text-ace-500" /></div>;
  const d: Detail = data;
  const run = d.run;
  const lane = run?.routing_lane ?? "";
  const lc = laneColor(lane);

  return (
    <div className="space-y-4 fadeup">
      <Link to="/" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-800">
        <ArrowLeft size={15} /> Worklist
      </Link>

      {/* Header */}
      <div className="card p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-extrabold text-slate-900">{d.patient_name}</h1>
              <LaneBadge lane={lane} />
            </div>
            <div className="mt-1 text-sm text-slate-500">
              {d.age}{d.sex} · {d.specialty}{d.modality && ` · ${d.modality}`} · {d.payer} · POS {d.pos} · DOS {d.dos}
              <span className="ml-2 font-mono text-xs text-slate-400">{d.mrn} · {d.source_system}</span>
            </div>
            <div className="mt-1 text-xs text-brand-600 font-medium">{d.scenario}</div>
          </div>
          <div className="text-right shrink-0 space-y-1">
            {run && lane !== "MANUAL" && (
              <div className={clsx("text-2xl font-extrabold", confColor(run.overall_confidence))}>{pct(run.overall_confidence)}</div>
            )}
            {run && <div className="text-[11px] text-slate-400 font-mono">{run.model_version}</div>}
            {run && <div className="text-[11px] text-slate-400">{(run.latency_ms / 1000).toFixed(1)}s</div>}
            <button className="btn-ghost py-1.5" onClick={() => setShowAudit((s) => !s)}>
              <ShieldCheck size={14} /> Audit packet
            </button>
          </div>
        </div>

        {run && (
          <div className={clsx("mt-4 rounded-lg p-3 ring-1 flex items-start gap-2", lc.bg, lc.ring)}>
            <ChevronRight size={16} className={clsx("mt-0.5", lc.text)} />
            <div>
              <div className={clsx("text-sm font-semibold", lc.text)}>Routed to {laneLabel(lane)}</div>
              <div className="text-xs text-slate-600">{run.routing_reason}</div>
            </div>
          </div>
        )}
      </div>

      {showAudit && run && <AuditPacket runId={run.id} />}

      <div className="grid lg:grid-cols-2 gap-4">
        {/* Chart viewer */}
        <div className="card p-0 overflow-hidden h-fit lg:sticky lg:top-4">
          <div className="px-4 py-3 border-b border-slate-200 flex items-center gap-2">
            <FileText size={16} className="text-slate-400" />
            <span className="font-semibold text-slate-700 text-sm">Clinical chart</span>
            <span className="text-xs text-slate-400">· hover a code to highlight its evidence</span>
          </div>
          <div className="p-4 font-mono text-[13px] leading-relaxed max-h-[70vh] overflow-y-auto">
            {d.chart_lines.map((ln) => (
              <div key={ln.n} className={clsx("flex gap-3 px-1 rounded transition-colors", highlightSet.has(ln.n) && "bg-brand-100")}>
                <span className="text-slate-300 select-none w-6 text-right shrink-0">{ln.n}</span>
                <span className="text-slate-700 whitespace-pre-wrap">{ln.text || " "}</span>
              </div>
            ))}
          </div>
          {run?.chart_summary && (
            <div className="px-4 py-3 border-t border-slate-200 bg-slate-50">
              <div className="label mb-1">AI chart summary</div>
              <p className="text-sm text-slate-600">{run.chart_summary}</p>
            </div>
          )}
        </div>

        {/* Codes + pipeline */}
        <div className="space-y-3">
          {!run && <div className="card p-6 text-center text-slate-400">Not coded yet.</div>}
          {run?.codes.map((c) => (
            <CodeCard key={c.id} code={c} selected={selected === c.id} onSelect={() => setSelected(c.id)} onHighlight={setHighlight} />
          ))}
          {run && run.codes.length === 0 && (
            <div className="card p-6 text-center text-slate-500">
              No codes emitted — routed to manual queue. {run.routing_reason}
            </div>
          )}
          {run && <PipelineTrace stageLog={run.stage_log} eligibility={run.eligibility} />}
        </div>
      </div>
    </div>
  );
}

function PipelineTrace({ stageLog, eligibility }: { stageLog: any[]; eligibility: any }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="card p-4">
      <button className="flex items-center justify-between w-full" onClick={() => setOpen((o) => !o)}>
        <span className="font-semibold text-slate-700 text-sm">Pipeline trace · Stage 0–5</span>
        <ChevronRight size={16} className={clsx("transition-transform text-slate-400", open && "rotate-90")} />
      </button>
      {open && (
        <ol className="mt-3 space-y-2">
          {(stageLog ?? []).map((s, i) => (
            <li key={i} className="rounded-lg border border-slate-150 bg-slate-50 p-3">
              <div className="text-xs font-semibold text-ace-700">{s.title || s.stage}</div>
              <pre className="mt-1 text-[11px] text-slate-500 whitespace-pre-wrap break-words max-h-40 overflow-y-auto">
                {JSON.stringify(stripBig(s), null, 1)}
              </pre>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function stripBig(s: any) {
  const { stage, title, ...rest } = s;
  return rest;
}

function AuditPacket({ runId }: { runId: string }) {
  const { data } = useQuery({ queryKey: ["audit", runId], queryFn: () => api.audit(runId) });
  return (
    <div className="card p-4">
      <div className="flex items-center gap-2 mb-2">
        <ShieldCheck size={16} className="text-emerald-600" />
        <span className="font-semibold text-slate-700 text-sm">Audit defense packet · append-only evidence chain</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead><tr className="text-left text-slate-400">
            <th className="py-1 pr-4">Time</th><th className="py-1 pr-4">Stage</th><th className="py-1 pr-4">Actor</th>
            <th className="py-1 pr-4">Event</th><th className="py-1">Model</th>
          </tr></thead>
          <tbody className="divide-y divide-slate-100">
            {(data ?? []).map((a) => (
              <tr key={a.id}>
                <td className="py-1.5 pr-4 text-slate-400 font-mono">{new Date(a.ts).toLocaleTimeString()}</td>
                <td className="py-1.5 pr-4 font-medium text-slate-600">{a.stage}</td>
                <td className="py-1.5 pr-4 text-slate-500">{a.actor}</td>
                <td className="py-1.5 pr-4 text-slate-700">{a.event}</td>
                <td className="py-1.5 text-slate-400 font-mono">{a.model_version}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
