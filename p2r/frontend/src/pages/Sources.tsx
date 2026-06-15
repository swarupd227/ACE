import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Radar, RefreshCw, GitCompare, Building2, Plus, Power } from "lucide-react";
import clsx from "clsx";
import { api } from "../api";
import { Spinner } from "../lib";
import { useRole, can } from "../role";
import StreamConsole from "../components/StreamConsole";
import type { PolicyDelta } from "../types";

const BLANK = { payer: "", name: "", source_type: "PORTAL", location: "", cadence: "weekly" };

export default function Sources() {
  const qc = useQueryClient();
  const { role } = useRole();
  const isAdmin = can(role, "admin");
  const [err, setErr] = useState("");
  const [last, setLast] = useState<string>("");
  const [showAdd, setShowAdd] = useState(false);
  const [nw, setNw] = useState({ ...BLANK });
  const { data: sources } = useQuery({ queryKey: ["sources"], queryFn: api.sources });
  const { data: deltas } = useQuery({ queryKey: ["deltas"], queryFn: api.deltas });
  const { data: masters } = useQuery({ queryKey: ["payer-master"], queryFn: api.payerMaster });

  const actor = role.toLowerCase().replace(/\s+/g, "_");
  const [acqSrc, setAcqSrc] = useState<string | null>(null);  // source id currently streaming
  const invalidateSources = () => qc.invalidateQueries({ queryKey: ["sources"] });

  const createSource = useMutation({
    mutationFn: () => api.createSource(nw),
    onSuccess: () => { invalidateSources(); setShowAdd(false); setNw({ ...BLANK }); },
    onError: (e: any) => setErr(e.message),
  });
  const toggleSource = useMutation({
    mutationFn: (s: any) => api.updateSource(s.id, {
      payer: s.payer, name: s.name, source_type: s.source_type, location: s.location,
      cadence: s.cadence, status: s.status === "active" ? "disabled" : "active",
    }),
    onSuccess: invalidateSources,
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
        <div className="flex items-center justify-between">
          <div className="label">Registered sources</div>
          {isAdmin && (
            <button className="btn-ghost py-1" onClick={() => { setErr(""); setShowAdd((s) => !s); }}>
              <Plus size={15} /> Register source
            </button>
          )}
        </div>

        {isAdmin && showAdd && (
          <div className="card p-4 grid grid-cols-6 gap-2 items-end fadeup">
            {([["payer", "Payer"], ["name", "Source name"], ["location", "Location (URL / mailbox)"]] as const).map(([k, lbl]) => (
              <label key={k} className="text-xs text-slate-500 col-span-2">{lbl}
                <input value={(nw as any)[k]} onChange={(e) => setNw({ ...nw, [k]: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-sm" />
              </label>
            ))}
            <label className="text-xs text-slate-500 col-span-2">Type
              <select value={nw.source_type} onChange={(e) => setNw({ ...nw, source_type: e.target.value })}
                className="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-sm">
                {["PORTAL", "FEED", "EMAIL"].map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </label>
            <label className="text-xs text-slate-500 col-span-2">Cadence
              <select value={nw.cadence} onChange={(e) => setNw({ ...nw, cadence: e.target.value })}
                className="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-sm">
                {["daily", "weekly", "monthly"].map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </label>
            <button className="btn-primary col-span-2" disabled={createSource.isPending || !nw.payer || !nw.name}
              onClick={() => { setErr(""); createSource.mutate(); }}>
              {createSource.isPending ? <Spinner className="h-4 w-4" /> : <Plus size={15} />} Add source
            </button>
          </div>
        )}

        {(sources ?? []).map((s) => (
          <div key={s.id} className={clsx("card p-4 flex items-center justify-between gap-4", s.status !== "active" && "opacity-60")}>
            <div className="flex items-start gap-3 min-w-0">
              <Radar size={18} className="text-ace-500 mt-0.5 shrink-0" />
              <div className="min-w-0">
                <div className="text-sm font-semibold text-slate-800 truncate flex items-center gap-2">
                  {s.name}
                  {s.status !== "active" && <span className="pill bg-slate-100 text-slate-500">disabled</span>}
                </div>
                <div className="text-xs text-slate-500 font-mono truncate">{s.location}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">
                  {s.payer} · {s.source_type} · {s.cadence} · polled {s.fetch_count}× {s.last_checked && `· last ${s.last_checked.slice(0, 16).replace("T", " ")}`}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              {isAdmin && (
                <button className="btn-ghost" title={s.status === "active" ? "Disable" : "Enable"}
                  disabled={toggleSource.isPending} onClick={() => { setErr(""); toggleSource.mutate(s); }}>
                  <Power size={15} className={s.status === "active" ? "text-emerald-500" : "text-slate-400"} />
                </button>
              )}
              {can(role, "acquire") && (
                <button className="btn-primary" disabled={acqSrc !== null || s.status !== "active"}
                  onClick={() => { setErr(""); setLast(""); setAcqSrc(s.id); }}>
                  {acqSrc === s.id ? <Spinner className="h-4 w-4" /> : <RefreshCw size={15} />} Run acquisition
                </button>
              )}
            </div>
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

      {acqSrc && (
        <StreamConsole
          title="Running acquisition agent"
          path={`/sources/${acqSrc}/acquire/stream?actor=${encodeURIComponent(actor)}`}
          onClose={() => setAcqSrc(null)}
          onDone={(ev) => {
            const r = ev.result || {};
            setLast(r.changed ? `${r.change_type}: ${r.delta?.summary}` : "No change — content identical to last poll");
            setAcqSrc(null);
            invalidateSources();
            qc.invalidateQueries({ queryKey: ["deltas"] });
            qc.invalidateQueries({ queryKey: ["documents"] });
          }}
        />
      )}
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
