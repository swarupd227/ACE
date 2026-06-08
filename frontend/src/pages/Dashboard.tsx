import { useQuery } from "@tanstack/react-query";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, CartesianGrid,
} from "recharts";
import { TrendingUp, Zap, Gauge, Clock, AlertTriangle, Rocket } from "lucide-react";
import clsx from "clsx";
import { api } from "../api";
import { Spinner } from "../lib";

const LANE_COLORS: Record<string, string> = { STB: "#10b981", QA: "#f59e0b", MANUAL: "#f43f5e" };

function Kpi({ icon: Icon, label, value, sub, target }: { icon: any; label: string; value: string; sub?: string; target?: string }) {
  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
        <Icon size={14} /> {label}
      </div>
      <div className="mt-1 text-3xl font-extrabold text-slate-900 tabular-nums">{value}</div>
      <div className="mt-1 flex items-center justify-between">
        {sub && <span className="text-xs text-slate-500">{sub}</span>}
        {target && <span className="pill bg-ace-50 text-ace-700 ring-1 ring-ace-100">target {target}</span>}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { data, isLoading } = useQuery({ queryKey: ["dashboard"], queryFn: api.dashboard });
  if (isLoading || !data) return <div className="grid place-items-center h-64"><Spinner className="h-6 w-6 text-ace-500" /></div>;

  const pie = [
    { name: "STB", value: data.stb_count },
    { name: "QA", value: data.qa_count },
    { name: "MANUAL", value: data.manual_count },
  ].filter((d) => d.value > 0);

  const bars = data.by_specialty.map((s: any) => ({
    specialty: s.specialty,
    "STB %": Math.round(s.stb_rate * 100),
    "Accuracy %": Math.round(s.avg_accuracy * 100),
  }));

  return (
    <div className="space-y-5 fadeup">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900">Performance Dashboard</h1>
        <p className="text-sm text-slate-500">Progressive ramp toward the SLA targets — accuracy and STB grow with the learning loop.</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <Kpi icon={Zap} label="STB rate" value={`${Math.round(data.stb_rate * 100)}%`} sub={`${data.stb_count}/${data.eligible} eligible charts`} target="≥80%" />
        <Kpi icon={Gauge} label="Calibrated accuracy" value={`${Math.round(data.avg_accuracy * 100)}%`} sub="auto-coded lanes" target="≥90%" />
        <Kpi icon={TrendingUp} label="Manual effort reduction" value={`${Math.round(data.manual_effort_reduction * 100)}%`} sub="STB + ½ QA" target="≥30%" />
        <Kpi icon={Clock} label="Coding TAT reduction" value={`${Math.round(data.tat.reduction_pct * 100)}%`} sub={`${data.tat.baseline_min}m → ${data.tat.assisted_min}m`} target="≥10–15%" />
        <Kpi icon={AlertTriangle} label="Exception rate" value={`${Math.round(data.exception_rate * 100)}%`} sub="routed to manual" target="↓ over time" />
      </div>

      <div className="card p-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-bold text-slate-800 flex items-center gap-2"><Rocket size={16} className="text-ace-600" /> Automation maturity pathway</h2>
          <span className="pill bg-ace-50 text-ace-700 ring-1 ring-ace-100">Now: {data.maturity.stage} · STB {Math.round(data.maturity.stb_rate * 100)}% (target ≥{Math.round(data.maturity.target * 100)}%)</span>
        </div>
        <div className="flex items-center gap-2">
          {data.maturity.stages.map((s, i) => {
            const activeIdx = data.maturity.stages.indexOf(data.maturity.stage);
            const done = i <= activeIdx;
            return (
              <div key={s} className="flex-1">
                <div className={clsx("h-2 rounded-full", done ? "bg-ace-500" : "bg-slate-200")} />
                <div className={clsx("mt-1 text-[11px]", i === activeIdx ? "font-bold text-ace-700" : "text-slate-400")}>
                  {s}{i === activeIdx ? " ◀ now" : ""}
                </div>
              </div>
            );
          })}
        </div>
        <p className="mt-2 text-xs text-slate-400">Maturity advances as accuracy is certified (≥95%) and 100% audit tapers — STB share grows toward the ≥80% target.</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="card p-5 lg:col-span-2">
          <h2 className="font-bold text-slate-800 mb-3">STB rate &amp; accuracy by specialty</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={bars} barGap={6}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="specialty" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} domain={[0, 100]} unit="%" />
              <Tooltip />
              <Bar dataKey="STB %" fill="#6366f1" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Accuracy %" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-5">
          <h2 className="font-bold text-slate-800 mb-3">Routing mix</h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={pie} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2}>
                {pie.map((d) => <Cell key={d.name} fill={LANE_COLORS[d.name]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-3 text-xs">
            {pie.map((d) => (
              <span key={d.name} className="inline-flex items-center gap-1">
                <span className="h-2 w-2 rounded-full" style={{ background: LANE_COLORS[d.name] }} /> {d.name} ({d.value})
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="card p-4 bg-ace-50 border-ace-100 text-sm text-ace-900">
        <strong>Governance:</strong> during initial rollout VHT audits 100% of charts; the model earns
        certification once quality ≥ 95%. Auto-coded share then grows as audit sampling tapers.
      </div>
    </div>
  );
}
