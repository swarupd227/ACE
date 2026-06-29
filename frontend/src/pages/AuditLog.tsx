import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  ScrollText, RefreshCw, Download, Search, Cpu, ShieldCheck, ShieldAlert, Lock, FileSearch, ChevronRight,
} from "lucide-react";
import clsx from "clsx";
import { api } from "../api";
import { Spinner } from "../lib";
import type { AuditEvent } from "../types";

const SOURCES = [
  { key: "", label: "All activity" },
  { key: "coding", label: "Coding decisions" },
  { key: "governance", label: "Governance / config" },
];

function fmtTs(iso: string) {
  try {
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
      year: "numeric", month: "short", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit",
    });
  } catch {
    return iso;
  }
}

function SourceBadge({ source }: { source: string }) {
  if (source === "governance")
    return <span className="pill bg-violet-50 text-violet-700 ring-1 ring-violet-200"><ShieldCheck size={12} /> Governance</span>;
  return <span className="pill bg-sky-50 text-sky-700 ring-1 ring-sky-200"><FileSearch size={12} /> Coding</span>;
}

function Kpi({ label, value, hint }: { label: string; value: React.ReactNode; hint?: string }) {
  return (
    <div className="card p-4">
      <div className="text-xs uppercase tracking-wide text-slate-400">{label}</div>
      <div className="mt-1 text-2xl font-extrabold text-slate-900 tabular-nums">{value}</div>
      {hint && <div className="text-xs text-slate-400 mt-0.5">{hint}</div>}
    </div>
  );
}

function Row({ ev }: { ev: AuditEvent }) {
  const [open, setOpen] = useState(false);
  const hasDetail = ev.detail && Object.keys(ev.detail).length > 0;
  return (
    <>
      <tr
        className={clsx("border-b border-slate-100 hover:bg-slate-50", hasDetail && "cursor-pointer")}
        onClick={() => hasDetail && setOpen((v) => !v)}
      >
        <td className="px-3 py-2.5 align-top whitespace-nowrap">
          {hasDetail ? (
            <ChevronRight size={14} className={clsx("inline text-slate-400 transition-transform", open && "rotate-90")} />
          ) : <span className="inline-block w-3.5" />}
          <span className="ml-1 text-xs font-mono text-slate-500">{fmtTs(ev.ts)}</span>
        </td>
        <td className="px-3 py-2.5 align-top"><SourceBadge source={ev.source} /></td>
        <td className="px-3 py-2.5 align-top">
          <div className="text-sm font-medium text-slate-700">{ev.actor}</div>
          {ev.role && <div className="text-[11px] text-slate-400">{ev.role}</div>}
        </td>
        <td className="px-3 py-2.5 align-top">
          <span className="pill bg-slate-100 text-slate-600 ring-1 ring-slate-200">{ev.category}</span>
        </td>
        <td className="px-3 py-2.5 align-top text-sm text-slate-700">{ev.action}</td>
        <td className="px-3 py-2.5 align-top">
          {ev.encounter_id ? (
            <Link to={`/encounter/${ev.encounter_id}`} className="text-ace-600 hover:underline font-mono text-sm" onClick={(e) => e.stopPropagation()}>
              {ev.target || ev.encounter_id}
            </Link>
          ) : (
            <span className="font-mono text-sm text-slate-600">{ev.target || "—"}</span>
          )}
          {ev.specialty && <span className="ml-2 text-[11px] text-slate-400">{ev.specialty}</span>}
        </td>
        <td className="px-3 py-2.5 align-top">
          {ev.model_version && (
            <span className="pill bg-slate-50 text-slate-500 ring-1 ring-slate-200 font-mono text-[11px]">
              <Cpu size={11} /> {ev.model_version}
            </span>
          )}
        </td>
      </tr>
      {open && hasDetail && (
        <tr className="bg-slate-50/70">
          <td colSpan={7} className="px-10 py-2">
            <pre className="text-[11px] leading-relaxed text-slate-600 font-mono whitespace-pre-wrap break-all">
              {JSON.stringify(ev.detail, null, 2)}
            </pre>
          </td>
        </tr>
      )}
    </>
  );
}

export default function AuditLog() {
  const [source, setSource] = useState("");
  const [q, setQ] = useState("");
  const [encounter, setEncounter] = useState("");
  const [category, setCategory] = useState("");

  const { data, isFetching, refetch } = useQuery({
    queryKey: ["globalAudit", source, q, encounter],
    queryFn: () => api.globalAudit({ source, q, encounter, limit: 400 }),
    refetchInterval: 20000,
  });

  const events = useMemo(
    () => (data?.events ?? []).filter((e) => !category || e.category === category),
    [data, category]
  );
  const categories = Object.keys(data?.facets.by_category ?? {});

  const exportCsv = () => {
    const cols = ["ts", "source", "actor", "role", "category", "action", "target", "specialty", "encounter_id", "run_id", "model_version"];
    const esc = (v: any) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const lines = [cols.join(","), ...events.map((e: any) => cols.map((c) => esc(e[c])).join(","))];
    const blob = new Blob([lines.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "ace_audit_log.csv"; a.click();
    URL.revokeObjectURL(url);
  };

  const s = data?.summary;

  // E11 — tamper-evident chain: seal computes the hash chain; verify recomputes + reports breaks.
  const [integrity, setIntegrity] = useState<{ ok: boolean; sealed_rows: number; broken_at: any } | null>(null);
  const [busy, setBusy] = useState<"" | "seal" | "verify">("");
  const onSeal = async () => { setBusy("seal"); try { await api.auditSeal(); setIntegrity(await api.auditVerify()); } finally { setBusy(""); } };
  const onVerify = async () => { setBusy("verify"); try { setIntegrity(await api.auditVerify()); } finally { setBusy(""); } };

  return (
    <div className="space-y-5 fadeup">
      <div className="flex items-end justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <ScrollText className="text-ace-600" /> Audit Log
          </h1>
          <p className="text-sm text-slate-500 max-w-3xl">
            One append-only trail across the platform — every coding decision (pipeline stage, override,
            reassignment, rollback) and every governance change (config, policy, model, reference data).
            The per-chart Audit packet and the Admin Change Log remain as scoped drill-downs.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn-ghost" onClick={() => refetch()}>
            {isFetching ? <Spinner className="h-4 w-4" /> : <RefreshCw size={15} />} Refresh
          </button>
          <button className="btn-ghost" onClick={exportCsv} disabled={!events.length}>
            <Download size={15} /> Export CSV
          </button>
          <button className="btn-ghost" onClick={onSeal} disabled={!!busy} title="Compute the tamper-evident hash chain over the ledger">
            {busy === "seal" ? <Spinner className="h-4 w-4" /> : <Lock size={15} />} Seal
          </button>
          <button className="btn-ghost" onClick={onVerify} disabled={!!busy} title="Recompute the chain and detect any tampering">
            {busy === "verify" ? <Spinner className="h-4 w-4" /> : <ShieldCheck size={15} />} Verify integrity
          </button>
          {integrity && (
            <span className={clsx("pill ring-1 inline-flex items-center gap-1",
              integrity.ok ? "bg-emerald-50 text-emerald-700 ring-emerald-200" : "bg-rose-50 text-rose-700 ring-rose-200")}>
              {integrity.ok ? <ShieldCheck size={13} /> : <ShieldAlert size={13} />}
              {integrity.ok ? `intact · ${integrity.sealed_rows} sealed` : `tampered @ ${integrity.broken_at?.event ?? "?"}`}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Kpi label="Events shown" value={events.length} hint={s ? `${s.matched} matched` : ""} />
        <Kpi label="Coding decisions" value={s?.coding_events ?? "—"} />
        <Kpi label="Governance changes" value={s?.governance_events ?? "—"} />
        <Kpi label="Distinct actors" value={s?.distinct_actors ?? "—"} />
      </div>

      {/* Filters */}
      <div className="card p-3 space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          {SOURCES.map((sObj) => (
            <button
              key={sObj.key}
              onClick={() => setSource(sObj.key)}
              className={clsx(
                "px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                source === sObj.key ? "bg-ace-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              )}
            >
              {sObj.label}
            </button>
          ))}
          <div className="flex-1" />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="rounded-lg border border-slate-200 px-2 py-1.5 text-sm text-slate-700"
          >
            <option value="">All categories</option>
            {categories.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div className="grid md:grid-cols-2 gap-2">
          <label className="flex items-center gap-2 rounded-lg border border-slate-200 px-2.5">
            <Search size={15} className="text-slate-400" />
            <input
              value={q} onChange={(e) => setQ(e.target.value)}
              placeholder="Search actor, action, detail…"
              className="flex-1 py-2 text-sm outline-none"
            />
          </label>
          <label className="flex items-center gap-2 rounded-lg border border-slate-200 px-2.5">
            <FileSearch size={15} className="text-slate-400" />
            <input
              value={encounter} onChange={(e) => setEncounter(e.target.value)}
              placeholder="Filter by MRN / encounter id…"
              className="flex-1 py-2 text-sm outline-none font-mono"
            />
          </label>
        </div>
      </div>

      {/* Timeline */}
      <div className="card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="text-left text-[11px] uppercase tracking-wide text-slate-400 border-b border-slate-200 bg-slate-50/60">
              <th className="px-3 py-2.5 font-semibold">When</th>
              <th className="px-3 py-2.5 font-semibold">Source</th>
              <th className="px-3 py-2.5 font-semibold">Actor</th>
              <th className="px-3 py-2.5 font-semibold">Category</th>
              <th className="px-3 py-2.5 font-semibold">Event</th>
              <th className="px-3 py-2.5 font-semibold">Target</th>
              <th className="px-3 py-2.5 font-semibold">Model</th>
            </tr>
          </thead>
          <tbody>
            {events.map((ev) => <Row key={ev.id} ev={ev} />)}
          </tbody>
        </table>
        {!events.length && (
          <div className="p-8 text-center text-sm text-slate-400">
            {isFetching ? "Loading audit trail…" : "No audit events match these filters."}
          </div>
        )}
      </div>
    </div>
  );
}
