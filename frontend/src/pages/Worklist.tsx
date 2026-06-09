import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useState } from "react";
import clsx from "clsx";
import { Play, ArrowRight, Clock, Zap, Flag } from "lucide-react";
import { api } from "../api";
import { useRole, can } from "../role";
import AgentConsole, { CODING_STEPS } from "../components/AgentConsole";
import { ConfidenceBar, LaneBadge, Spinner, laneColor } from "../lib";
import type { EncounterRow, Lane } from "../types";

function LaneCard({ lane, count, total }: { lane: Lane; count: number; total: number }) {
  const c = laneColor(lane);
  const sub =
    lane === "STB" ? "Auto-billed, no human touch" : lane === "QA" ? "Auditor verifies" : "Full human coding";
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between">
        <LaneBadge lane={lane} />
        <span className="text-2xl font-extrabold tabular-nums">{count}</span>
      </div>
      <div className="mt-2 text-xs text-slate-500">{sub}</div>
      <div className="mt-3 h-1.5 rounded-full bg-slate-100 overflow-hidden">
        <div className={clsx("h-full", c.solid)} style={{ width: total ? `${(count / total) * 100}%` : "0%" }} />
      </div>
    </div>
  );
}

export default function Worklist() {
  const qc = useQueryClient();
  const { data: rows, isLoading } = useQuery({ queryKey: ["encounters"], queryFn: api.encounters });
  const { data: meta } = useQuery({ queryKey: ["meta"], queryFn: api.meta });
  const [consoleEnc, setConsoleEnc] = useState<{ id: string; name: string } | null>(null);
  const [showBatch, setShowBatch] = useState(false);
  const { role } = useRole();
  const mayCode = can(role, "code");

  const list = rows ?? [];
  const coded = list.filter((r) => r.routing_lane);
  const counts = {
    STB: coded.filter((r) => r.routing_lane === "STB").length,
    QA: coded.filter((r) => r.routing_lane === "QA").length,
    MANUAL: coded.filter((r) => r.routing_lane === "MANUAL").length,
  };
  const stbRate = coded.length ? Math.round((counts.STB / coded.length) * 100) : 0;

  return (
    <div className="space-y-5 fadeup">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Coder Worklist</h1>
          <p className="text-sm text-slate-500">
            Radiology &amp; E&amp;M encounters · confidence-routed into Straight-Through Billing, QA, or Manual
          </p>
        </div>
        {mayCode ? (
          <button
            className="btn-brand"
            disabled={!meta?.llm_available}
            onClick={() => setShowBatch(true)}
            title={!meta?.llm_available ? "Configure ANTHROPIC_API_KEY to enable coding" : ""}
          >
            <Play size={16} /> Run autonomous coding
          </button>
        ) : (
          <span className="pill bg-slate-100 text-slate-500 ring-1 ring-slate-200">view-only ({role})</span>
        )}
      </div>

      {/* Lane summary */}
      <div className="grid grid-cols-4 gap-4">
        <div className="card p-4 bg-ace-900 text-white">
          <div className="flex items-center gap-2 text-xs text-slate-300">
            <Zap size={14} className="text-brand-300" /> STB RATE
          </div>
          <div className="mt-1 text-3xl font-extrabold tabular-nums">{stbRate}%</div>
          <div className="mt-2 text-xs text-slate-400">{coded.length} of {list.length} charts coded</div>
        </div>
        <LaneCard lane="STB" count={counts.STB} total={coded.length} />
        <LaneCard lane="QA" count={counts.QA} total={coded.length} />
        <LaneCard lane="MANUAL" count={counts.MANUAL} total={coded.length} />
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
              <th className="px-4 py-3 font-semibold">Patient / MRN</th>
              <th className="px-4 py-3 font-semibold">Specialty</th>
              <th className="px-4 py-3 font-semibold">Scenario</th>
              <th className="px-4 py-3 font-semibold">Payer</th>
              <th className="px-4 py-3 font-semibold">Lane</th>
              <th className="px-4 py-3 font-semibold w-40">Confidence</th>
              <th className="px-4 py-3 font-semibold">TAT</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isLoading && (
              <tr><td colSpan={8} className="px-4 py-10 text-center text-slate-400"><Spinner className="h-5 w-5 mx-auto" /></td></tr>
            )}
            {list.map((r: EncounterRow) => (
              <tr key={r.id} className="hover:bg-slate-50/70">
                <td className="px-4 py-3">
                  <div className="font-semibold text-slate-800">{r.patient_name}</div>
                  <div className="text-xs text-slate-400 font-mono">{r.mrn} · {r.source_system}</div>
                </td>
                <td className="px-4 py-3">
                  <span className="font-medium text-slate-700">{r.specialty}</span>
                  {r.modality && <span className="ml-1 text-xs text-slate-400">{r.modality}</span>}
                </td>
                <td className="px-4 py-3 max-w-[260px]">
                  <span className="text-xs text-slate-500">{r.scenario}</span>
                </td>
                <td className="px-4 py-3 text-slate-600">{r.payer}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <LaneBadge lane={r.routing_lane} />
                    {(r as any).escalated && (
                      <span title="Escalated · high priority" className="text-amber-500"><Flag size={13} /></span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  {r.routing_lane && r.routing_lane !== "MANUAL" ? (
                    <ConfidenceBar value={r.overall_confidence} />
                  ) : (
                    <span className="text-xs text-slate-300">—</span>
                  )}
                </td>
                <td className="px-4 py-3 text-xs text-slate-500">
                  {r.latency_ms ? (
                    <span className="inline-flex items-center gap-1"><Clock size={12} />{(r.latency_ms / 1000).toFixed(1)}s</span>
                  ) : "—"}
                </td>
                <td className="px-4 py-3 text-right whitespace-nowrap">
                  {!r.routing_lane ? (
                    mayCode ? (
                      <button
                        className="btn-ghost py-1.5"
                        disabled={!meta?.llm_available}
                        onClick={() => setConsoleEnc({ id: r.id, name: r.patient_name })}
                      >
                        <Play size={14} /> Code
                      </button>
                    ) : (
                      <span className="text-xs text-slate-300">queued</span>
                    )
                  ) : (
                    <Link to={`/encounter/${r.id}`} className="btn-ghost py-1.5">
                      Review <ArrowRight size={14} />
                    </Link>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {consoleEnc && (
        <AgentConsole
          url={`/encounters/${consoleEnc.id}/code/stream`}
          steps={CODING_STEPS}
          title={consoleEnc.name}
          onClose={() => setConsoleEnc(null)}
          onDone={() => qc.invalidateQueries({ queryKey: ["encounters"] })}
        />
      )}
      {showBatch && (
        <AgentConsole
          url="/coding/run-all/stream"
          label="Batch Orchestrator"
          title="uncoded charts"
          onClose={() => setShowBatch(false)}
          onDone={() => qc.invalidateQueries({ queryKey: ["encounters"] })}
        />
      )}
    </div>
  );
}
