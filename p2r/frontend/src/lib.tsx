import clsx from "clsx";
import type { CodeSets, ReconVerdict, ValVerdict } from "./types";

export function pct(v: number) {
  return `${Math.round((v || 0) * 100)}%`;
}

export function confColor(v: number) {
  if (v >= 0.9) return "text-emerald-600";
  if (v >= 0.7) return "text-amber-600";
  return "text-rose-600";
}
function confBg(v: number) {
  if (v >= 0.9) return "bg-emerald-500";
  if (v >= 0.7) return "bg-amber-500";
  return "bg-rose-500";
}

export function ConfidenceBar({ value }: { value: number }) {
  return (
    <div className="flex items-center gap-2 min-w-[120px]">
      <div className="h-2 flex-1 rounded-full bg-slate-200 overflow-hidden">
        <div className={clsx("h-full rounded-full transition-all", confBg(value))} style={{ width: pct(value) }} />
      </div>
      <span className={clsx("text-xs font-bold tabular-nums w-9 text-right", confColor(value))}>{pct(value)}</span>
    </div>
  );
}

// Reconciliation verdict — the headline of the review queue.
export function ReconBadge({ verdict }: { verdict: ReconVerdict }) {
  const map: Record<ReconVerdict, string> = {
    NET_NEW: "bg-sky-50 text-sky-700 ring-sky-200",
    UPDATE: "bg-violet-50 text-violet-700 ring-violet-200",
    DUPLICATE: "bg-slate-100 text-slate-600 ring-slate-200",
    CONFLICT: "bg-rose-50 text-rose-700 ring-rose-200",
  };
  return <span className={clsx("pill ring-1", map[verdict] || "bg-slate-100 text-slate-600 ring-slate-200")}>{verdict}</span>;
}

export function ValidationBadge({ verdict }: { verdict: ValVerdict }) {
  const map: Record<string, string> = {
    SUPPORTED: "bg-emerald-50 text-emerald-700 ring-emerald-200",
    PARTIAL: "bg-amber-50 text-amber-700 ring-amber-200",
    UNSUPPORTED: "bg-rose-50 text-rose-700 ring-rose-200",
  };
  return <span className={clsx("pill ring-1", map[verdict] || "bg-slate-100 text-slate-500 ring-slate-200")}>{verdict || "—"}</span>;
}

export function ProvisionBadge({ type }: { type: string }) {
  return <span className="pill bg-ace-50 text-ace-700 ring-1 ring-ace-100">{type}</span>;
}

export function RoutingBadge({ routing }: { routing: string }) {
  const map: Record<string, string> = {
    AUTO_LOAD: "bg-emerald-50 text-emerald-700 ring-emerald-200",
    VERIFY: "bg-amber-50 text-amber-700 ring-amber-200",
    HOLD: "bg-rose-50 text-rose-700 ring-rose-200",
  };
  return <span className={clsx("pill ring-1", map[routing] || "bg-slate-100 text-slate-500 ring-slate-200")}>{routing || "—"}</span>;
}

export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    PENDING_REVIEW: "bg-slate-100 text-slate-600 ring-slate-200",
    APPROVED: "bg-sky-50 text-sky-700 ring-sky-200",
    PUBLISHED: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  };
  const label = status === "PENDING_REVIEW" ? "PENDING" : status;
  return <span className={clsx("pill ring-1", map[status] || "bg-slate-100 text-slate-500 ring-slate-200")}>{label}</span>;
}

export function CodeChips({ codes }: { codes: CodeSets }) {
  const groups: [string, string[] | undefined, string][] = [
    ["CPT", codes.cpt, "bg-violet-50 text-violet-700 ring-violet-200"],
    ["ICD", codes.icd, "bg-sky-50 text-sky-700 ring-sky-200"],
    ["HCPCS", codes.hcpcs, "bg-teal-50 text-teal-700 ring-teal-200"],
    ["MOD", codes.modifiers, "bg-amber-50 text-amber-700 ring-amber-200"],
    ["POS", codes.pos, "bg-slate-100 text-slate-600 ring-slate-200"],
  ];
  const any = groups.some(([, arr]) => (arr?.length ?? 0) > 0);
  if (!any) return <span className="text-xs text-slate-400">no codes</span>;
  return (
    <div className="flex flex-wrap gap-1">
      {groups.map(([label, arr, cls]) =>
        (arr ?? []).map((c) => (
          <span key={`${label}-${c}`} className={clsx("pill ring-1 font-mono", cls)}>
            <span className="opacity-50 mr-0.5">{label}</span>{c}
          </span>
        ))
      )}
    </div>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <svg className={clsx("animate-spin", className)} viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}
