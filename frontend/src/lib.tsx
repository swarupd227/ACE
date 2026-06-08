import clsx from "clsx";
import type { Lane } from "./types";

export function laneColor(lane: Lane) {
  switch (lane) {
    case "STB":
      return { bg: "bg-emerald-50", text: "text-emerald-700", ring: "ring-emerald-200", dot: "bg-emerald-500", solid: "bg-emerald-500" };
    case "QA":
      return { bg: "bg-amber-50", text: "text-amber-700", ring: "ring-amber-200", dot: "bg-amber-500", solid: "bg-amber-500" };
    case "MANUAL":
      return { bg: "bg-rose-50", text: "text-rose-700", ring: "ring-rose-200", dot: "bg-rose-500", solid: "bg-rose-500" };
    default:
      return { bg: "bg-slate-100", text: "text-slate-500", ring: "ring-slate-200", dot: "bg-slate-400", solid: "bg-slate-400" };
  }
}

export function laneLabel(lane: Lane) {
  if (lane === "STB") return "Straight-Through Billing";
  if (lane === "QA") return "QA Review";
  if (lane === "MANUAL") return "Manual Coder";
  return "Not coded";
}

export function confColor(v: number) {
  if (v >= 0.9) return "text-emerald-600";
  if (v >= 0.75) return "text-amber-600";
  return "text-rose-600";
}
export function confBg(v: number) {
  if (v >= 0.9) return "bg-emerald-500";
  if (v >= 0.75) return "bg-amber-500";
  return "bg-rose-500";
}

export function pct(v: number) {
  return `${Math.round(v * 100)}%`;
}

export function LaneBadge({ lane, className }: { lane: Lane; className?: string }) {
  const c = laneColor(lane);
  return (
    <span className={clsx("pill ring-1", c.bg, c.text, c.ring, className)}>
      <span className={clsx("h-1.5 w-1.5 rounded-full", c.dot)} />
      {lane || "—"}
    </span>
  );
}

export function ConfidenceBar({ value, showLabel = true }: { value: number; showLabel?: boolean }) {
  return (
    <div className="flex items-center gap-2 min-w-[120px]">
      <div className="h-2 flex-1 rounded-full bg-slate-200 overflow-hidden">
        <div className={clsx("h-full rounded-full transition-all", confBg(value))} style={{ width: pct(value) }} />
      </div>
      {showLabel && <span className={clsx("text-xs font-bold tabular-nums w-9 text-right", confColor(value))}>{pct(value)}</span>}
    </div>
  );
}

export function SystemBadge({ system }: { system: string }) {
  const map: Record<string, string> = {
    ICD10CM: "bg-sky-50 text-sky-700 ring-sky-200",
    CPT: "bg-violet-50 text-violet-700 ring-violet-200",
    HCPCS: "bg-teal-50 text-teal-700 ring-teal-200",
  };
  return <span className={clsx("pill ring-1", map[system] || "bg-slate-100 text-slate-600 ring-slate-200")}>{system}</span>;
}

export function Spinner({ className }: { className?: string }) {
  return (
    <svg className={clsx("animate-spin", className)} viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}
