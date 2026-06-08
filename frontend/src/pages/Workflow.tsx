import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import clsx from "clsx";
import {
  Database, FileCheck2, Cpu, GitBranch, Zap, ClipboardCheck, UserCog, Receipt, RefreshCw, ArrowRight, ArrowDown,
} from "lucide-react";
import { api } from "../api";
import { Spinner, laneColor } from "../lib";

function Box({ icon: Icon, title, sub, tone = "slate" }: { icon: any; title: string; sub?: string; tone?: string }) {
  const tones: Record<string, string> = {
    slate: "bg-white border-slate-200",
    ace: "bg-ace-50 border-ace-200",
    brand: "bg-brand-50 border-brand-200",
  };
  return (
    <div className={clsx("rounded-xl border p-3 text-center shadow-card", tones[tone])}>
      <Icon size={20} className="mx-auto text-ace-600" />
      <div className="mt-1 text-sm font-semibold text-slate-800">{title}</div>
      {sub && <div className="text-[11px] text-slate-500">{sub}</div>}
    </div>
  );
}

function Arrow({ down = false }: { down?: boolean }) {
  return down ? (
    <ArrowDown className="mx-auto my-1 text-slate-300" size={20} />
  ) : (
    <ArrowRight className="shrink-0 self-center text-slate-300" size={20} />
  );
}

function LaneColumn({ lane, count, role, action }: { lane: "STB" | "QA" | "MANUAL"; count: number; role: string; action: string }) {
  const c = laneColor(lane);
  const title = lane === "STB" ? "Straight-Through Billing" : lane === "QA" ? "QA Review" : "Manual Coding";
  return (
    <div className={clsx("rounded-xl border p-4", c.bg, c.ring, "ring-1")}>
      <div className="flex items-center justify-between">
        <span className={clsx("font-semibold", c.text)}>{title}</span>
        <span className="text-2xl font-extrabold tabular-nums">{count}</span>
      </div>
      <div className="mt-2 text-xs text-slate-600"><span className="font-semibold">Owner:</span> {role}</div>
      <div className="text-xs text-slate-600"><span className="font-semibold">Action:</span> {action}</div>
    </div>
  );
}

export default function Workflow() {
  const { data: stats } = useQuery({ queryKey: ["dashboard"], queryFn: api.dashboard });
  const { data: meta } = useQuery({ queryKey: ["meta"], queryFn: api.meta });
  if (!stats) return <div className="grid place-items-center h-64"><Spinner className="h-6 w-6 text-ace-500" /></div>;

  return (
    <div className="space-y-5 fadeup">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900">Operational Workflow</h1>
        <p className="text-sm text-slate-500">
          End-to-end process: intake → eligibility → autonomous coding → confidence routing → human-in-the-loop → billing,
          with a closed feedback loop. Runs inside RevAmp's Coding Studio.
        </p>
      </div>

      {/* Top linear flow */}
      <div className="card p-5">
        <div className="grid grid-cols-[1fr_auto_1fr_auto_1fr_auto_1fr] gap-2 items-stretch">
          <Box icon={Database} title="Intake" sub="Practice Admin · eCW · Cerner (FHIR/HL7/EDI)" />
          <Arrow />
          <Box icon={FileCheck2} title="Stage 0 · Eligibility" sub="docs · auth · specialty · exclusions" tone="ace" />
          <Arrow />
          <Box icon={Cpu} title="Stages 1–5 · AI Pipeline" sub="condition · extract · cite · validate · calibrate" tone="ace" />
          <Arrow />
          <Box icon={GitBranch} title="Confidence Router" sub="calibrated + bounded autonomy" tone="brand" />
        </div>

        <ArrowDown className="mx-auto my-2 text-slate-300" size={22} />

        {/* Three lanes */}
        <div className="grid md:grid-cols-3 gap-3">
          <LaneColumn lane="STB" count={stats.stb_count} role="None — automated" action="Auto-submit claim (837)" />
          <LaneColumn lane="QA" count={stats.qa_count} role="CDI / Coding Auditor" action="Verify → accept or correct" />
          <LaneColumn lane="MANUAL" count={stats.manual_count} role="Certified Coder" action="Full human coding (reason flagged)" />
        </div>

        <ArrowDown className="mx-auto my-2 text-slate-300" size={22} />

        <div className="grid md:grid-cols-2 gap-3">
          <Box icon={Receipt} title="Billing / Claim submission" sub={`${stats.coded} charts coded · STB rate ${Math.round(stats.stb_rate * 100)}%`} tone="brand" />
          <div className="rounded-xl border border-fuchsia-200 bg-fuchsia-50 p-3 flex items-center gap-3">
            <RefreshCw size={20} className="text-fuchsia-600 shrink-0" />
            <div>
              <div className="text-sm font-semibold text-fuchsia-800">Closed feedback loop</div>
              <div className="text-[11px] text-fuchsia-700">
                Coder corrections (with reason) → 24–48h batch → SLM fine-tune + Graph-RAG exemplars → back into the pipeline.
                ML-Ops flags invalid/junk codes.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Roles + governance */}
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-2"><UserCog size={16} className="text-ace-600" /><h2 className="font-bold text-slate-800">Human-in-the-loop (RevAmp worklist)</h2></div>
          <ul className="text-sm text-slate-600 space-y-1.5">
            <li>• Chart summary + rationale + cited evidence per code</li>
            <li>• Color-coded 4-factor confidence + observability</li>
            <li>• Accept / update / override with captured reason</li>
            <li>• Routed to specialty-matched queue, never generic</li>
          </ul>
          <Link to="/" className="btn-ghost mt-3 py-1.5">Open the worklist <ArrowRight size={14} /></Link>
        </div>

        <div className="card p-5">
          <div className="flex items-center gap-2 mb-2"><ClipboardCheck size={16} className="text-ace-600" /><h2 className="font-bold text-slate-800">Orchestration controls</h2></div>
          <ul className="text-sm text-slate-600 space-y-1.5">
            <li>• Intelligent routing of low-confidence encounters</li>
            <li>• Bounded-autonomy hard rules (e.g., critical care → QA)</li>
            <li>• Eligibility failures → manual queue w/ reason codes</li>
            <li>• QA routing · escalation · re-reason on gate failure</li>
            <li>• Append-only audit ledger (replayable decisions)</li>
          </ul>
        </div>

        <div className="card p-5 bg-ace-50 border-ace-100">
          <div className="flex items-center gap-2 mb-2"><Zap size={16} className="text-ace-700" /><h2 className="font-bold text-ace-900">Governance &amp; ramp</h2></div>
          <ul className="text-sm text-ace-900/80 space-y-1.5">
            <li>• VHT audits 100% during initial rollout</li>
            <li>• Model certified at ≥95% quality</li>
            <li>• Audit sampling tapers → STB share grows</li>
            <li>• Progressive accuracy ramp → ≥90% / ≥80% STB</li>
          </ul>
        </div>
      </div>

      <p className="text-xs text-slate-400">
        Model: {meta?.model_version}. The <Link to="/cdi" className="text-ace-600 hover:underline">CDI / physician-query</Link>{" "}
        module drafts compliant, non-leading queries when documentation is insufficient, and re-codes on the physician's answer.
      </p>
    </div>
  );
}
