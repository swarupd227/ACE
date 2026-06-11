import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import {
  ArrowLeft, Check, FileText, ShieldCheck, X, ChevronRight, Quote, BookOpen, Sparkles, Scale, History, Cpu, FileSearch,
  Stethoscope, MessageSquareWarning, CheckCircle2, ArrowRightLeft, AlertTriangle, Flag, Undo2, Network,
} from "lucide-react";
import { api } from "../api";
import { useRole, can } from "../role";
import AgentConsole, { CODING_STEPS } from "../components/AgentConsole";
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
  const { role } = useRole();
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
          {code.learning_applied && (
            <span className="pill bg-fuchsia-50 text-fuchsia-700 ring-1 ring-fuchsia-200" title="Influenced by a captured coder correction">
              <Sparkles size={11} /> learned
            </span>
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
        {can(role, "override") ? (
          <>
            <button className="btn-ghost py-1.5" disabled={accept.isPending} onClick={() => accept.mutate()}>
              <Check size={14} /> Accept
            </button>
            <button className="btn-ghost py-1.5" onClick={() => setShowOverride((s) => !s)}>
              Override
            </button>
          </>
        ) : (
          <span className="text-xs text-slate-400">view-only ({role})</span>
        )}
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

function DrgCard({ drg }: { drg: NonNullable<Detail["run"]>["drg"] }) {
  const [open, setOpen] = useState(false);
  if (!drg) return null;
  if (!drg.resolved) {
    return (
      <div className="card p-4 border-l-4 border-amber-400">
        <div className="flex items-center gap-2 text-amber-700 font-semibold">
          <AlertTriangle size={16} /> MS-DRG unresolved — routed to human coder
        </div>
        <p className="text-sm text-slate-500 mt-1">
          The grouper could not assign a DRG from the coded data; a human completes grouping. (Curated demo subset.)
        </p>
      </div>
    );
  }
  const typeLabel = drg.drg_type === "SURG" ? "Surgical" : drg.drg_type === "MED" ? "Medical" : drg.drg_type;
  const sevLabel = drg.severity === "MCC" ? "with MCC" : drg.severity === "CC" ? "with CC" : "without CC/MCC";
  const sevColor =
    drg.severity === "MCC" ? "bg-rose-50 text-rose-700 ring-rose-200"
    : drg.severity === "CC" ? "bg-amber-50 text-amber-700 ring-amber-200"
    : "bg-slate-100 text-slate-600 ring-slate-200";
  return (
    <div className="card overflow-hidden border-l-4 border-ace-500">
      <div className="p-4 bg-ace-900 text-white">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-xs uppercase tracking-wide text-slate-300">MS-DRG · inpatient grouping</div>
            <div className="text-2xl font-extrabold mt-0.5">DRG {drg.drg}</div>
            <div className="text-sm text-slate-200">{drg.title}</div>
          </div>
          <div className="text-right shrink-0">
            <div className="text-xs uppercase tracking-wide text-slate-300">Relative weight</div>
            <div className="text-3xl font-extrabold tabular-nums">{drg.weight.toFixed(4)}</div>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="pill bg-white/10 text-white ring-1 ring-white/20">MDC {drg.mdc} · {drg.mdc_title}</span>
          <span className="pill bg-white/10 text-white ring-1 ring-white/20">{typeLabel}</span>
          <span className={clsx("pill ring-1", sevColor)}>{sevLabel}</span>
        </div>
      </div>
      <div className="p-4 space-y-2 text-sm">
        <div>
          <span className="text-slate-400">Principal diagnosis</span>{" "}
          <span className="font-mono font-semibold text-slate-700">{drg.pdx}</span>
        </div>
        {drg.or_procedure && (
          <div>
            <span className="text-slate-400">OR procedure</span>{" "}
            <span className="font-mono font-semibold text-slate-700">{drg.or_procedure}</span>{" "}
            <span className="text-xs text-slate-400">→ surgical partition</span>
          </div>
        )}
        {drg.cc_mcc_drivers.length > 0 && (
          <div>
            <span className="text-slate-400">Severity drivers</span>
            <div className="mt-1 flex flex-wrap gap-1.5">
              {drg.cc_mcc_drivers.map((d) => (
                <span key={d.code} className={clsx("pill ring-1", d.tier === "MCC" ? "bg-rose-50 text-rose-700 ring-rose-200" : "bg-amber-50 text-amber-700 ring-amber-200")}>
                  <span className="font-mono">{d.code}</span> · {d.tier}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
      <button
        className="w-full px-4 py-2 border-t border-slate-200 text-xs text-slate-500 hover:bg-slate-50 flex items-center justify-center gap-1"
        onClick={() => setOpen((v) => !v)}
      >
        <Network size={13} /> {open ? "Hide" : "Show"} grouper logic
        <ChevronRight size={13} className={clsx("transition-transform", open && "rotate-90")} />
      </button>
      {open && (
        <ol className="px-5 pb-4 pt-1 space-y-1.5">
          {drg.trace.map((t, i) => (
            <li key={i} className="text-xs text-slate-600 flex gap-2">
              <span className="font-mono text-ace-600 shrink-0 w-28">{t.step}</span>
              <span>{t.detail}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function HccCard({ hcc }: { hcc: NonNullable<Detail["run"]>["hcc"] }) {
  const [open, setOpen] = useState(false);
  if (!hcc) return null;
  if (!hcc.resolved) {
    return (
      <div className="card p-4 border-l-4 border-amber-400">
        <div className="flex items-center gap-2 text-amber-700 font-semibold">
          <AlertTriangle size={16} /> RAF unresolved — routed to human coder
        </div>
        <p className="text-sm text-slate-500 mt-1">
          The scorer could not compute a RAF (demographic segment outside the curated model); a human
          completes risk-adjustment review.
        </p>
      </div>
    );
  }
  return (
    <div className="card overflow-hidden border-l-4 border-ace-500">
      <div className="p-4 bg-ace-900 text-white">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-xs uppercase tracking-wide text-slate-300">CMS-HCC · risk adjustment</div>
            <div className="text-2xl font-extrabold mt-0.5">RAF {hcc.raf.toFixed(3)}</div>
            <div className="text-sm text-slate-200">
              {hcc.hccs.length} HCC{hcc.hccs.length === 1 ? "" : "s"} captured
              {hcc.demographic?.band ? ` · demographic ${hcc.demographic.band} (${hcc.demographic.factor?.toFixed(3)})` : ""}
            </div>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {hcc.hccs.map((h) => (
            <span key={h.hcc} className="pill bg-white/10 text-white ring-1 ring-white/20">
              HCC {h.hcc} · {h.label} · +{h.coefficient.toFixed(3)}
            </span>
          ))}
        </div>
      </div>
      <div className="p-4 space-y-2 text-sm">
        {hcc.hccs.map((h) => (
          <div key={h.hcc}>
            <span className="text-slate-400">HCC {h.hcc}</span>{" "}
            <span className="text-slate-700">{h.label}</span>{" "}
            <span className="font-mono text-xs text-slate-500">({h.dx.join(", ")})</span>
          </div>
        ))}
        {hcc.suppressed.length > 0 && (
          <div className="text-amber-700">
            Hierarchy: {hcc.suppressed.map((s) => `HCC ${s.hcc} suppressed by HCC ${s.by}`).join("; ")} —
            only the most severe in a family pays.
          </div>
        )}
        {hcc.unmapped.length > 0 && (
          <div className="text-slate-500">
            Does not risk-adjust: <span className="font-mono">{hcc.unmapped.join(", ")}</span>
          </div>
        )}
      </div>
      <button
        className="w-full px-4 py-2 border-t border-slate-200 text-xs text-slate-500 hover:bg-slate-50 flex items-center justify-center gap-1"
        onClick={() => setOpen((v) => !v)}
      >
        <Network size={13} /> {open ? "Hide" : "Show"} RAF computation
        <ChevronRight size={13} className={clsx("transition-transform", open && "rotate-90")} />
      </button>
      {open && (
        <ol className="px-5 pb-4 pt-1 space-y-1.5">
          {hcc.trace.map((t, i) => (
            <li key={i} className="text-xs text-slate-600 flex gap-2">
              <span className="font-mono text-ace-600 shrink-0 w-28">{t.step}</span>
              <span>{t.detail}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function AnesCard({ anes }: { anes: NonNullable<Detail["run"]>["anes"] }) {
  const [open, setOpen] = useState(false);
  if (!anes) return null;
  if (!anes.resolved) {
    return (
      <div className="card p-4 border-l-4 border-amber-400">
        <div className="flex items-center gap-2 text-amber-700 font-semibold">
          <AlertTriangle size={16} /> Anesthesia units unresolved — routed to human coder
        </div>
        <p className="text-sm text-slate-500 mt-1">
          The calculator needs a base-unit entry and documented anesthesia start/stop time; a human
          completes the unit calculation.
        </p>
      </div>
    );
  }
  const modifying = anes.phys_units + anes.qual_circ.reduce((s, q) => s + q.units, 0);
  return (
    <div className="card overflow-hidden border-l-4 border-ace-500">
      <div className="p-4 bg-ace-900 text-white">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-xs uppercase tracking-wide text-slate-300">Anesthesia units · {anes.code}</div>
            <div className="text-2xl font-extrabold mt-0.5">{anes.total_units.toFixed(2)} units</div>
            <div className="text-sm text-slate-200">
              {anes.base_units} base + {anes.time_units.toFixed(2)} time ({anes.time_minutes} min) + {modifying} modifying
            </div>
          </div>
          <div className="text-right shrink-0">
            <div className="text-xs uppercase tracking-wide text-slate-300">Estimated allowable</div>
            <div className="text-3xl font-extrabold tabular-nums">${anes.estimated_allowable.toFixed(2)}</div>
            <div className="text-xs text-slate-300">× ${anes.conversion_factor.toFixed(2)}/unit</div>
          </div>
        </div>
      </div>
      <div className="p-4 space-y-2 text-sm">
        <div>
          <span className="text-slate-400">Time units</span>{" "}
          <span className="text-slate-700">{anes.time_minutes} min documented ÷ 15 = {anes.time_units.toFixed(2)}</span>
        </div>
        {anes.phys_modifier && (
          <div>
            <span className="text-slate-400">Physical status</span>{" "}
            <span className="font-mono font-semibold text-slate-700">{anes.phys_modifier}</span>{" "}
            <span className="text-slate-600">→ +{anes.phys_units} unit{anes.phys_units === 1 ? "" : "s"}</span>{" "}
            <span className="text-xs text-slate-400">(commercial convention; Medicare pays 0)</span>
          </div>
        )}
        {anes.qual_circ.map((q) => (
          <div key={q.code}>
            <span className="text-slate-400">Qualifying circumstance</span>{" "}
            <span className="font-mono font-semibold text-slate-700">{q.code}</span>{" "}
            <span className="text-slate-600">{q.description} → +{q.units}</span>
          </div>
        ))}
      </div>
      <button
        className="w-full px-4 py-2 border-t border-slate-200 text-xs text-slate-500 hover:bg-slate-50 flex items-center justify-center gap-1"
        onClick={() => setOpen((v) => !v)}
      >
        <Network size={13} /> {open ? "Hide" : "Show"} unit calculation
        <ChevronRight size={13} className={clsx("transition-transform", open && "rotate-90")} />
      </button>
      {open && (
        <ol className="px-5 pb-4 pt-1 space-y-1.5">
          {anes.trace.map((t, i) => (
            <li key={i} className="text-xs text-slate-600 flex gap-2">
              <span className="font-mono text-ace-600 shrink-0 w-28">{t.step}</span>
              <span>{t.detail}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function ApcCard({ apc }: { apc: NonNullable<Detail["run"]>["apc"] }) {
  const [open, setOpen] = useState(false);
  if (!apc) return null;
  return (
    <div className="card overflow-hidden border-l-4 border-sky-500">
      <div className="p-4 bg-ace-900 text-white">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-xs uppercase tracking-wide text-slate-300">Facility side · APC / OPPS</div>
            <div className="text-2xl font-extrabold mt-0.5">${apc.facility_total.toFixed(2)}</div>
            <div className="text-sm text-slate-200">
              {apc.lines.length} payable line{apc.lines.length === 1 ? "" : "s"} · {apc.packaged.length} packaged
            </div>
          </div>
          <div className="text-right text-xs text-slate-300 max-w-[200px]">
            Same chart, two claims: the coded pro-fee lines above + this facility estimate (Addendum-B
            status indicators).
          </div>
        </div>
      </div>
      <div className="p-4 space-y-2 text-sm">
        {apc.lines.map((l) => (
          <div key={l.code} className="flex items-center justify-between gap-2">
            <div>
              <span className="font-mono font-semibold text-slate-700">{l.code}</span>{" "}
              <span className="pill bg-sky-50 text-sky-700 ring-1 ring-sky-200">SI {l.si}</span>{" "}
              <span className="text-slate-500 text-xs">APC {l.apc} · {l.apc_title}</span>
              {l.pct < 100 && <span className="ml-1 text-xs text-amber-600 font-semibold">{l.pct}% (multi-procedure)</span>}
            </div>
            <span className="font-semibold tabular-nums text-slate-700">${l.allowed.toFixed(2)}</span>
          </div>
        ))}
        {apc.packaged.map((p) => (
          <div key={p.code} className="flex items-center justify-between gap-2 text-slate-400">
            <div>
              <span className="font-mono">{p.code}</span>{" "}
              <span className="pill bg-slate-100 text-slate-500 ring-1 ring-slate-200">SI {p.si}</span>{" "}
              <span className="text-xs">{p.note}</span>
            </div>
            <span className="tabular-nums">$0.00</span>
          </div>
        ))}
        {apc.not_covered.length > 0 && (
          <div className="text-xs text-amber-600">
            Outside the curated Addendum-B subset: <span className="font-mono">{apc.not_covered.join(", ")}</span>
            {" "}— full file in production.
          </div>
        )}
      </div>
      <button
        className="w-full px-4 py-2 border-t border-slate-200 text-xs text-slate-500 hover:bg-slate-50 flex items-center justify-center gap-1"
        onClick={() => setOpen((v) => !v)}
      >
        <Network size={13} /> {open ? "Hide" : "Show"} OPPS pricing logic
        <ChevronRight size={13} className={clsx("transition-transform", open && "rotate-90")} />
      </button>
      {open && (
        <ol className="px-5 pb-4 pt-1 space-y-1.5">
          {apc.trace.map((t, i) => (
            <li key={i} className="text-xs text-slate-600 flex gap-2">
              <span className="font-mono text-ace-600 shrink-0 w-28">{t.step}</span>
              <span>{t.detail}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

export default function EncounterDetail() {
  const { id } = useParams();
  const { data, isLoading } = useQuery({ queryKey: ["encounter", id], queryFn: () => api.encounter(id!) });
  const qc = useQueryClient();
  const { role } = useRole();
  const [highlight, setHighlight] = useState<number[] | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [showAudit, setShowAudit] = useState(false);
  const [showConsole, setShowConsole] = useState(false);

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

      {showConsole && (
        <AgentConsole
          url={`/encounters/${d.id}/code/stream`}
          steps={CODING_STEPS}
          title={d.patient_name}
          onClose={() => setShowConsole(false)}
          onDone={() => qc.invalidateQueries({ queryKey: ["encounter", id] })}
        />
      )}

      {/* Header */}
      <div className="card p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-xl font-extrabold text-slate-900">{d.patient_name}</h1>
              <LaneBadge lane={lane} />
              {d.doc_status && d.doc_status !== "final" && (
                <span className="pill bg-amber-50 text-amber-700 ring-1 ring-amber-200 uppercase">
                  {d.doc_status} — unattested
                </span>
              )}
              {d.late_addendum && (
                <span className="pill bg-rose-50 text-rose-700 ring-1 ring-rose-200">
                  Late addendum after billing
                </span>
              )}
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
            {can(role, "code") && (
              <button className="btn-ghost py-1.5" onClick={() => setShowConsole(true)}>
                <Cpu size={14} /> Watch agent re-run
              </button>
            )}
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

      {run && <WorkflowActions run={run} />}

      {showAudit && run && <AuditPacket runId={run.id} />}

      {run && <GraphRagEvidence run={run} />}

      {run && <CdiPanel encId={d.id} />}

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
          {run?.drg && <DrgCard drg={run.drg} />}
          {run?.hcc && <HccCard hcc={run.hcc} />}
          {run?.anes && <AnesCard anes={run.anes} />}
          {run?.apc && <ApcCard apc={run.apc} />}
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

function GraphRagEvidence({ run }: { run: any }) {
  const [open, setOpen] = useState(true);
  const rag = (run.stage_log ?? []).find((s: any) => s.stage === "rag");
  if (!rag) return null;
  const onto = rag.ontology_paths ?? [];
  const pol = rag.payer_policies ?? [];
  const learned = rag.learned ?? [];
  const usedCount = onto.length + pol.length + learned.length;

  return (
    <div className="card p-4">
      <button className="flex items-center justify-between w-full" onClick={() => setOpen((o) => !o)}>
        <span className="flex items-center gap-2 font-semibold text-slate-700 text-sm">
          <Network size={16} className="text-ace-600" /> Knowledge used for this chart
          <span className="pill bg-ace-50 text-ace-700 ring-1 ring-ace-100">{usedCount} facts · {(rag.icd_candidates?.length ?? 0) + (rag.proc_candidates?.length ?? 0)} candidates</span>
        </span>
        <ChevronRight size={16} className={clsx("transition-transform text-slate-400", open && "rotate-90")} />
      </button>
      {open && (
        <div className="mt-3 grid md:grid-cols-3 gap-3 text-xs">
          <div>
            <div className="label mb-1">Ontology paths</div>
            {onto.length ? onto.map((o: any, i: number) => (
              <div key={i} className="mb-1 text-slate-600">
                <span className="font-semibold">{o.concept}</span>
                {o.maps_to?.length ? <span className="text-ace-700"> → {o.maps_to.map((m: any) => m.code).join(", ")}</span> : null}
                {o.edges?.length ? <div className="text-slate-400">{o.edges.map((e: any) => `${e.rel} ${e.to}`).join(" · ")}</div> : null}
              </div>
            )) : <div className="text-slate-400">none matched</div>}
          </div>
          <div>
            <div className="label mb-1">Payer policy applied</div>
            {pol.length ? pol.map((p: any, i: number) => (
              <div key={i} className="mb-1 text-slate-600">
                <span className="font-semibold">{p.payer} · {p.code}</span>
                {p.requires_auth ? <span className="ml-1 text-amber-600">(auth)</span> : null}
                <div className="text-slate-400">{p.medical_necessity}</div>
              </div>
            )) : <div className="text-slate-400">none for these codes</div>}
          </div>
          <div>
            <div className="label mb-1">Learned corrections</div>
            {learned.length ? learned.map((l: any, i: number) => (
              <div key={i} className="mb-1 text-fuchsia-700">use {l.use_code} (instead of {l.instead_of}) — {l.reason}</div>
            )) : <div className="text-slate-400">none</div>}
          </div>
        </div>
      )}
    </div>
  );
}

function WorkflowActions({ run }: { run: any }) {
  const qc = useQueryClient();
  const inval = () => {
    qc.invalidateQueries({ queryKey: ["encounter", run.encounter_id] });
    qc.invalidateQueries({ queryKey: ["encounters"] });
  };
  const reassign = useMutation({
    mutationFn: ({ lane, reason }: { lane: string; reason: string }) => api.reassign(run.id, lane, reason),
    onSuccess: inval,
  });
  const escalate = useMutation({
    mutationFn: () => api.escalate(run.id, "Senior Coder / CDI", "Flagged for senior review"),
    onSuccess: inval,
  });
  const rollback = useMutation({ mutationFn: () => api.rollback(run.id), onSuccess: inval });
  const [addText, setAddText] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const addendum = useMutation({
    mutationFn: () => api.addendum(run.encounter_id, addText),
    onSuccess: () => { setAddText(""); setShowAdd(false); inval(); },
  });
  const { role } = useRole();
  const mayReassign = can(role, "reassign");
  const mayEscalate = can(role, "escalate");
  const mayRollback = can(role, "rollback");
  const lanes: { key: "STB" | "QA" | "MANUAL"; label: string; reason: string }[] = [
    { key: "STB", label: "STB", reason: "Approved for straight-through billing" },
    { key: "QA", label: "QA", reason: "Sent for QA verification" },
    { key: "MANUAL", label: "Manual", reason: "Routed to manual coder" },
  ];

  return (
    <div className="card p-4">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
        {!mayReassign && !mayEscalate && !mayRollback && (
          <span className="text-sm text-slate-400">Workflow actions are view-only for the {role} role.</span>
        )}
        {mayReassign && (
        <div className="flex items-center gap-2">
          <ArrowRightLeft size={16} className="text-ace-600" />
          <span className="text-sm font-semibold text-slate-700">Reassign queue:</span>
          {lanes.map((l) => (
            <button
              key={l.key}
              disabled={reassign.isPending || run.routing_lane === l.key}
              onClick={() => reassign.mutate({ lane: l.key, reason: l.reason })}
              className={clsx(
                "rounded-md border px-2.5 py-1 text-xs font-semibold",
                run.routing_lane === l.key
                  ? "border-ace-300 bg-ace-50 text-ace-700 cursor-default"
                  : "border-slate-200 hover:bg-slate-50 text-slate-700"
              )}
            >
              {l.label}{run.routing_lane === l.key ? " (current)" : ""}
            </button>
          ))}
        </div>
        )}

        <div className="flex items-center gap-2">
          {mayEscalate && (
          <button
            className="btn-ghost py-1.5"
            disabled={escalate.isPending || run.escalated}
            onClick={() => escalate.mutate()}
          >
            <AlertTriangle size={14} className="text-amber-500" />
            {run.escalated ? "Escalated" : "Escalate to senior reviewer"}
          </button>
          )}
          {run.escalated && (
            <span className="pill bg-amber-50 text-amber-700 ring-1 ring-amber-200">
              <Flag size={11} /> {run.escalated_to} · high priority
            </span>
          )}
        </div>

        {run.modified && mayRollback && (
          <button className="btn-ghost py-1.5" disabled={rollback.isPending} onClick={() => rollback.mutate()}
                  title="Discard human edits and restore the original AI recommendation">
            <Undo2 size={14} className="text-slate-500" /> {rollback.isPending ? "Reverting…" : "Revert to AI recommendation"}
          </button>
        )}

        <button className="btn-ghost py-1.5" onClick={() => setShowAdd((v) => !v)}
                title="Append a timestamped physician addendum — after billing it raises a compliance flag">
          <FileText size={14} className="text-slate-500" /> Add addendum
        </button>
      </div>
      {showAdd && (
        <div className="mt-3 flex items-start gap-2">
          <textarea
            className="flex-1 rounded border border-slate-200 px-2 py-1.5 text-sm font-mono" rows={2}
            placeholder="Physician addendum text — timestamped now; if this chart already billed, it flags as a LATE addendum…"
            value={addText} onChange={(e) => setAddText(e.target.value)}
          />
          <button className="btn-primary py-1.5" disabled={addText.trim().length < 10 || addendum.isPending}
                  onClick={() => addendum.mutate()}>
            {addendum.isPending ? <Spinner className="h-4 w-4" /> : <FileText size={14} />} Append
          </button>
        </div>
      )}
      {(reassign.isPending || escalate.isPending) && (
        <div className="mt-2 text-xs text-slate-400 flex items-center gap-1"><Spinner className="h-3 w-3" /> applying…</div>
      )}
    </div>
  );
}

function CdiPanel({ encId }: { encId: string }) {
  const qc = useQueryClient();
  const { role } = useRole();
  const mayCdi = can(role, "cdi_respond");
  const [scanConsole, setScanConsole] = useState(false);
  const { data: queries } = useQuery({ queryKey: ["cdi", encId], queryFn: () => api.cdiForEncounter(encId) });
  const respond = useMutation({
    mutationFn: ({ id, resp }: { id: string; resp: string }) => api.cdiRespond(id, resp),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["cdi", encId] });
      qc.invalidateQueries({ queryKey: ["encounter", encId] });
    },
  });
  const list = queries ?? [];

  return (
    <div className="card p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Stethoscope size={16} className="text-ace-600" />
          <span className="font-semibold text-slate-700 text-sm">CDI / Physician Queries</span>
          {list.length > 0 && <span className="pill bg-amber-50 text-amber-700 ring-1 ring-amber-200">{list.length}</span>}
        </div>
        {mayCdi && (
          <button className="btn-ghost py-1.5" onClick={() => setScanConsole(true)}>
            <MessageSquareWarning size={14} /> Scan for CDI opportunities
          </button>
        )}
      </div>

      {scanConsole && (
        <AgentConsole
          url={`/encounters/${encId}/cdi-scan/stream`}
          label="CDI Agent"
          title="documentation review"
          onClose={() => setScanConsole(false)}
          onDone={() => qc.invalidateQueries({ queryKey: ["cdi", encId] })}
        />
      )}

      {list.length === 0 && (
        <p className="mt-2 text-xs text-slate-400">No queries yet. Run a scan to check for documentation gaps.</p>
      )}

      <div className="mt-3 space-y-3">
        {list.map((q) => (
          <div key={q.id} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-slate-800 text-sm">{q.target}</span>
              <span className={clsx("pill ring-1", q.status === "answered" ? "bg-emerald-50 text-emerald-700 ring-emerald-200" : "bg-amber-50 text-amber-700 ring-amber-200")}>{q.status}</span>
            </div>
            <p className="mt-1 text-sm text-slate-700">{q.question}</p>
            {q.clinical_indicators && <p className="mt-1 text-xs text-slate-500"><b>Indicators:</b> {q.clinical_indicators}</p>}
            {q.status !== "answered" ? (
              mayCdi ? (
                <div className="mt-2 flex flex-wrap gap-2">
                  {q.options.map((o) => (
                    <button key={o} disabled={respond.isPending}
                      onClick={() => respond.mutate({ id: q.id, resp: o })}
                      className="rounded-md border border-slate-200 bg-white px-2.5 py-1 text-xs hover:bg-ace-50 hover:border-ace-300">
                      {o}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="mt-2 text-xs text-slate-400">Awaiting CDI / physician response.</div>
              )
            ) : (
              <div className="mt-2 flex items-center gap-1.5 text-xs text-slate-600">
                <CheckCircle2 size={14} className="text-emerald-600" /> Answered: <b>{q.physician_response}</b> → re-coded
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
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
