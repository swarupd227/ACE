import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { SlidersHorizontal, ShieldAlert, FileCheck2, Timer, Layers, Users, Save, RotateCcw, Plus, Trash2, Check, History, Plug } from "lucide-react";
import { api } from "../api";
import { Spinner } from "../lib";

function useSaver(key: string, value: any) {
  const qc = useQueryClient();
  const [local, setLocal] = useState<any>(value);
  useEffect(() => { setLocal(value); }, [JSON.stringify(value)]);
  const save = useMutation({
    mutationFn: () => api.putConfig(key, local),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["adminConfig"] }),
  });
  const dirty = JSON.stringify(local) !== JSON.stringify(value);
  return { local, setLocal, save, dirty };
}

function SaveBar({ dirty, saving, onSave }: { dirty: boolean; saving: boolean; onSave: () => void }) {
  return (
    <div className="flex items-center gap-2 mt-3">
      <button className="btn-primary py-1.5" disabled={!dirty || saving} onClick={onSave}>
        {saving ? <Spinner className="h-4 w-4" /> : <Save size={14} />} Save
      </button>
      {dirty ? <span className="text-xs text-amber-600">unsaved changes</span> : <span className="text-xs text-emerald-600 flex items-center gap-1"><Check size={12} /> in effect on next coding run</span>}
    </div>
  );
}

function Slider({ label, value, onChange, min = 0, max = 1, step = 0.01, pct = true }: any) {
  return (
    <div>
      <div className="flex justify-between text-sm"><span className="text-slate-600">{label}</span><span className="font-mono font-semibold">{pct ? `${Math.round(value * 100)}%` : value}</span></div>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(parseFloat(e.target.value))} className="w-full accent-ace-600" />
    </div>
  );
}

function Toggle({ label, value, onChange, hint }: any) {
  return (
    <label className="flex items-center justify-between py-1.5 cursor-pointer">
      <span className="text-sm text-slate-700">{label}{hint && <span className="block text-xs text-slate-400">{hint}</span>}</span>
      <button type="button" onClick={() => onChange(!value)}
        className={clsx("relative inline-flex h-5 w-9 items-center rounded-full transition-colors shrink-0", value ? "bg-ace-600" : "bg-slate-300")}>
        <span className={clsx("inline-block h-4 w-4 transform rounded-full bg-white transition-transform", value ? "translate-x-4" : "translate-x-0.5")} />
      </button>
    </label>
  );
}

// ---- Tabs -------------------------------------------------------------------
function RoutingTab({ cfg }: { cfg: any }) {
  const r = useSaver("routing", cfg.routing);
  const w = useSaver("confidence_weights", cfg.confidence_weights);
  const sc = useSaver("self_consistency", cfg.self_consistency);
  const sum = (Object.values(w.local) as number[]).reduce((a, b) => a + b, 0);
  return (
    <div className="grid lg:grid-cols-2 gap-4">
      <div className="card p-4">
        <h3 className="font-bold text-slate-800 mb-2">Confidence routing thresholds</h3>
        <p className="text-xs text-slate-500 mb-3">Calibrated confidence ≥ STB → auto-bill; ≥ QA → QA review; else manual.</p>
        <div className="space-y-3">
          <Slider label="STB threshold" value={r.local.stb_threshold} onChange={(v: number) => r.setLocal({ ...r.local, stb_threshold: v })} min={0.5} max={1} />
          <Slider label="QA threshold" value={r.local.qa_threshold} onChange={(v: number) => r.setLocal({ ...r.local, qa_threshold: v })} min={0.3} max={1} />
        </div>
        <SaveBar dirty={r.dirty} saving={r.save.isPending} onSave={() => r.save.mutate()} />
      </div>

      <div className="card p-4">
        <h3 className="font-bold text-slate-800 mb-2">Accuracy-source weights (4-factor)</h3>
        <p className={clsx("text-xs mb-3", Math.abs(sum - 1) < 0.001 ? "text-slate-500" : "text-amber-600")}>Weights sum = {sum.toFixed(2)} {Math.abs(sum - 1) >= 0.001 && "(should be 1.00)"}</p>
        <div className="space-y-3">
          {["model", "doc_match", "rule", "historical"].map((k) => (
            <Slider key={k} label={k.replace("_", " ")} value={w.local[k]} onChange={(v: number) => w.setLocal({ ...w.local, [k]: v })} />
          ))}
        </div>
        <SaveBar dirty={w.dirty} saving={w.save.isPending} onSave={() => w.save.mutate()} />
      </div>

      <div className="card p-4">
        <h3 className="font-bold text-slate-800 mb-2">Self-consistency</h3>
        <label className="text-sm text-slate-600">Samples on hard encounters
          <input type="number" min={1} max={7} value={sc.local.hard_samples} onChange={(e) => sc.setLocal({ hard_samples: parseInt(e.target.value || "1") })}
            className="ml-2 w-16 rounded border border-slate-200 px-2 py-1 text-sm" />
        </label>
        <p className="mt-1 text-xs text-slate-400">More samples = better catch of confident-but-wrong; higher latency/cost.</p>
        <SaveBar dirty={sc.dirty} saving={sc.save.isPending} onSave={() => sc.save.mutate()} />
      </div>
    </div>
  );
}

function BoundedTab({ cfg }: { cfg: any }) {
  const b = useSaver("bounded_autonomy", cfg.bounded_autonomy);
  const items: [string, string, string][] = [
    ["block_flag", "Blocking conditioning flag", "unsigned / contradiction → human"],
    ["ambiguous_or_contradiction", "Ambiguous / contradictory docs", "route ambiguous charts to human"],
    ["critical_care", "Critical-care codes", "highest-dollar calls always reviewed"],
    ["ncci_break", "NCCI bundle conflict", "unbundling needs human confirmation"],
  ];
  return (
    <div className="card p-4 max-w-xl">
      <h3 className="font-bold text-slate-800 mb-1">Bounded-autonomy hard rules</h3>
      <p className="text-xs text-slate-500 mb-2">When ON, these force human review regardless of confidence.</p>
      {items.map(([k, label, hint]) => <Toggle key={k} label={label} hint={hint} value={b.local[k]} onChange={(v: boolean) => b.setLocal({ ...b.local, [k]: v })} />)}
      <SaveBar dirty={b.dirty} saving={b.save.isPending} onSave={() => b.save.mutate()} />
    </div>
  );
}

function EligibilityTab({ cfg }: { cfg: any }) {
  const e = useSaver("eligibility", cfg.eligibility);
  return (
    <div className="card p-4 max-w-xl">
      <h3 className="font-bold text-slate-800 mb-2">Stage-0 eligibility rules</h3>
      <label className="text-sm text-slate-600">Minimum documentation length (chars)
        <input type="number" min={0} max={1000} value={e.local.min_doc_chars} onChange={(ev) => e.setLocal({ ...e.local, min_doc_chars: parseInt(ev.target.value || "0") })}
          className="ml-2 w-20 rounded border border-slate-200 px-2 py-1 text-sm" />
      </label>
      <div className="mt-2">
        <Toggle label="Exclude interventional radiology" value={e.local.exclude_interventional} onChange={(v: boolean) => e.setLocal({ ...e.local, exclude_interventional: v })} />
        <Toggle label="Exclude trauma activations" value={e.local.exclude_trauma} onChange={(v: boolean) => e.setLocal({ ...e.local, exclude_trauma: v })} />
        <Toggle label="Exclude incomplete encounters" value={e.local.exclude_incomplete} onChange={(v: boolean) => e.setLocal({ ...e.local, exclude_incomplete: v })} />
      </div>
      <SaveBar dirty={e.dirty} saving={e.save.isPending} onSave={() => e.save.mutate()} />
    </div>
  );
}

function SlaTab({ cfg }: { cfg: any }) {
  const s = useSaver("sla_targets_min", cfg.sla_targets_min);
  return (
    <div className="card p-4 max-w-xl">
      <h3 className="font-bold text-slate-800 mb-2">SLA targets (minutes per queue)</h3>
      <div className="space-y-2">
        {Object.keys(s.local).map((q) => (
          <label key={q} className="flex items-center justify-between text-sm text-slate-600">
            {q}
            <input type="number" min={1} value={s.local[q]} onChange={(e) => s.setLocal({ ...s.local, [q]: parseInt(e.target.value || "1") })}
              className="w-24 rounded border border-slate-200 px-2 py-1 text-sm" />
          </label>
        ))}
      </div>
      <SaveBar dirty={s.dirty} saving={s.save.isPending} onSave={() => s.save.mutate()} />
    </div>
  );
}

function SpecialtiesTab({ cfg }: { cfg: any }) {
  const sp = useSaver("specialties", cfg.specialties);
  const upd = (i: number, patch: any) => sp.setLocal(sp.local.map((s: any, j: number) => (j === i ? { ...s, ...patch } : s)));
  return (
    <div className="card p-4 max-w-2xl">
      <h3 className="font-bold text-slate-800 mb-1">Specialty accelerator</h3>
      <p className="text-xs text-slate-500 mb-3">Enable/disable specialties and set the model tier. <b>Hard</b> = Opus + self-consistency. New specialties onboard via config + a golden set — not a rebuild.</p>
      <table className="w-full text-sm">
        <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200"><th className="py-2">Specialty</th><th className="py-2">Enabled</th><th className="py-2">Hard (Opus + self-consistency)</th></tr></thead>
        <tbody className="divide-y divide-slate-100">
          {sp.local.map((s: any, i: number) => (
            <tr key={s.name}>
              <td className="py-2 font-medium text-slate-700">{s.name}</td>
              <td className="py-2"><Toggle label="" value={s.enabled} onChange={(v: boolean) => upd(i, { enabled: v })} /></td>
              <td className="py-2"><Toggle label="" value={s.hard} onChange={(v: boolean) => upd(i, { hard: v })} /></td>
            </tr>
          ))}
        </tbody>
      </table>
      <SaveBar dirty={sp.dirty} saving={sp.save.isPending} onSave={() => sp.save.mutate()} />
    </div>
  );
}

function RosterTab({ cfg }: { cfg: any }) {
  const r = useSaver("roster", cfg.roster);
  const upd = (i: number, patch: any) => r.setLocal(r.local.map((m: any, j: number) => (j === i ? { ...m, ...patch } : m)));
  return (
    <div className="card p-4 max-w-2xl">
      <h3 className="font-bold text-slate-800 mb-2">Users &amp; roster</h3>
      <p className="text-xs text-slate-500 mb-3">People available for assignment in the Control Tower. (Maps to your IdP / SSO directory in production.)</p>
      <div className="space-y-2">
        {r.local.map((m: any, i: number) => (
          <div key={i} className="flex items-center gap-2">
            <input value={m.name} onChange={(e) => upd(i, { name: e.target.value })} className="flex-1 rounded border border-slate-200 px-2 py-1.5 text-sm" />
            <select value={m.role} onChange={(e) => upd(i, { role: e.target.value })} className="rounded border border-slate-200 px-2 py-1.5 text-sm">
              {["Coder", "QA Auditor", "CDI Specialist", "Supervisor"].map((x) => <option key={x}>{x}</option>)}
            </select>
            <button className="text-rose-400 hover:text-rose-600" onClick={() => r.setLocal(r.local.filter((_: any, j: number) => j !== i))}><Trash2 size={15} /></button>
          </div>
        ))}
      </div>
      <button className="btn-ghost py-1.5 mt-2" onClick={() => r.setLocal([...r.local, { name: "New User", role: "Coder" }])}><Plus size={14} /> Add user</button>
      <SaveBar dirty={r.dirty} saving={r.save.isPending} onSave={() => r.save.mutate()} />
    </div>
  );
}

function ConnectorsTab({ cfg }: { cfg: any }) {
  const c = useSaver("connectors", cfg.connectors ?? []);
  const upd = (i: number, patch: any) => c.setLocal(c.local.map((m: any, j: number) => (j === i ? { ...m, ...patch } : m)));
  return (
    <div className="card p-4 max-w-3xl">
      <h3 className="font-bold text-slate-800 mb-1">Source-system connectors</h3>
      <p className="text-xs text-slate-500 mb-3">PMS/EHR systems shown on the Integrations screen. Toggle a connector off to simulate a disconnected feed. (Maps to real FHIR/HL7/EDI endpoints in production.)</p>
      <div className="space-y-2">
        {c.local.map((m: any, i: number) => (
          <div key={i} className="flex items-center gap-2">
            <input value={m.name} onChange={(e) => upd(i, { name: e.target.value })} placeholder="name" className="w-44 rounded border border-slate-200 px-2 py-1.5 text-sm" />
            <input value={m.type} onChange={(e) => upd(i, { type: e.target.value })} placeholder="type (EHR/PMS)" className="w-40 rounded border border-slate-200 px-2 py-1.5 text-sm" />
            <input value={m.channel} onChange={(e) => upd(i, { channel: e.target.value })} placeholder="channel" className="flex-1 rounded border border-slate-200 px-2 py-1.5 text-sm" />
            <Toggle label="" value={m.enabled !== false} onChange={(v: boolean) => upd(i, { enabled: v })} />
            <button className="text-rose-400 hover:text-rose-600" onClick={() => c.setLocal(c.local.filter((_: any, j: number) => j !== i))}><Trash2 size={15} /></button>
          </div>
        ))}
      </div>
      <button className="btn-ghost py-1.5 mt-2" onClick={() => c.setLocal([...c.local, { name: "New Source", type: "EHR", channel: "FHIR R4", enabled: true }])}><Plus size={14} /> Add connector</button>
      <SaveBar dirty={c.dirty} saving={c.save.isPending} onSave={() => c.save.mutate()} />
    </div>
  );
}

const AREA_TONE: Record<string, string> = {
  config: "bg-ace-50 text-ace-700 ring-ace-200",
  policy: "bg-amber-50 text-amber-700 ring-amber-200",
  ontology: "bg-indigo-50 text-indigo-700 ring-indigo-200",
  guideline: "bg-sky-50 text-sky-700 ring-sky-200",
  reference: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  ncci: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  mue: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  modifier: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  golden: "bg-fuchsia-50 text-fuchsia-700 ring-fuchsia-200",
};

function ChangeLogTab() {
  const { data, isLoading } = useQuery({ queryKey: ["adminAudit"], queryFn: api.adminAudit, refetchInterval: 10000 });
  if (isLoading) return <div className="grid place-items-center h-40"><Spinner className="h-5 w-5 text-ace-500" /></div>;
  const rows = data ?? [];
  return (
    <div className="card overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-200 flex items-center gap-2">
        <History size={16} className="text-slate-400" />
        <span className="font-semibold text-slate-700 text-sm">Governance change log</span>
        <span className="text-xs text-slate-400">· append-only · every admin edit, who & when · {rows.length} entries</span>
      </div>
      {rows.length === 0 ? (
        <div className="p-8 text-center text-sm text-slate-400">No changes recorded yet. Edit a config, policy, the KG, or reference data — it lands here.</div>
      ) : (
        <table className="w-full text-sm">
          <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
            <th className="px-3 py-2">When</th><th className="px-3 py-2">Actor</th><th className="px-3 py-2">Area</th>
            <th className="px-3 py-2">Action</th><th className="px-3 py-2">Target</th><th className="px-3 py-2">Detail</th>
          </tr></thead>
          <tbody className="divide-y divide-slate-100">
            {rows.map((r) => (
              <tr key={r.id} className="hover:bg-slate-50/70 align-top">
                <td className="px-3 py-2 text-xs text-slate-500 whitespace-nowrap">{new Date(r.at).toLocaleString()}</td>
                <td className="px-3 py-2 text-xs"><span className="font-medium text-slate-700">{r.role || r.actor}</span></td>
                <td className="px-3 py-2"><span className={clsx("pill ring-1", AREA_TONE[r.area] ?? "bg-slate-100 text-slate-600 ring-slate-200")}>{r.area}</span></td>
                <td className="px-3 py-2 text-xs font-medium text-slate-600">{r.action}</td>
                <td className="px-3 py-2 font-mono text-xs text-slate-700">{r.target}</td>
                <td className="px-3 py-2 text-xs text-slate-400 max-w-xs truncate">{Object.keys(r.detail || {}).length ? JSON.stringify(r.detail) : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

const TABS: [string, string, any][] = [
  ["routing", "Routing & Calibration", SlidersHorizontal],
  ["bounded", "Bounded Autonomy", ShieldAlert],
  ["eligibility", "Eligibility", FileCheck2],
  ["sla", "SLA Targets", Timer],
  ["specialties", "Specialty Accelerator", Layers],
  ["roster", "Users & Roster", Users],
  ["connectors", "Connectors", Plug],
  ["changelog", "Change Log", History],
];

export default function Admin() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["adminConfig"], queryFn: api.adminConfig });
  const [tab, setTab] = useState("routing");
  const reset = useMutation({ mutationFn: api.resetConfig, onSuccess: () => qc.invalidateQueries({ queryKey: ["adminConfig"] }) });

  if (isLoading || !data) return <div className="grid place-items-center h-64"><Spinner className="h-6 w-6 text-ace-500" /></div>;
  const cfg = data.config;

  return (
    <div className="space-y-4 fadeup">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Admin · Platform Configuration</h1>
          <p className="text-sm text-slate-500">These settings drive the engine at runtime — no code changes, no redeploy. Edits apply on the next coding run.</p>
        </div>
        <button className="btn-ghost py-1.5" disabled={reset.isPending} onClick={() => reset.mutate()}><RotateCcw size={14} /> Reset to defaults</button>
      </div>

      <div className="flex gap-1 border-b border-slate-200 flex-wrap">
        {TABS.map(([k, label, Icon]) => (
          <button key={k} onClick={() => setTab(k)} className={clsx("flex items-center gap-1.5 px-3 py-2 text-sm font-medium border-b-2 -mb-px", tab === k ? "border-ace-500 text-ace-700" : "border-transparent text-slate-500 hover:text-slate-700")}>
            <Icon size={15} /> {label}
          </button>
        ))}
      </div>

      {tab === "routing" && <RoutingTab cfg={cfg} />}
      {tab === "bounded" && <BoundedTab cfg={cfg} />}
      {tab === "eligibility" && <EligibilityTab cfg={cfg} />}
      {tab === "sla" && <SlaTab cfg={cfg} />}
      {tab === "specialties" && <SpecialtiesTab cfg={cfg} />}
      {tab === "roster" && <RosterTab cfg={cfg} />}
      {tab === "connectors" && <ConnectorsTab cfg={cfg} />}
      {tab === "changelog" && <ChangeLogTab />}
    </div>
  );
}
