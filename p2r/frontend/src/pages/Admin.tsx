import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { SlidersHorizontal, Cpu, Library, Plug, Save, RotateCcw, Check, Plus, Trash2 } from "lucide-react";
import clsx from "clsx";
import { api } from "../api";
import { Spinner } from "../lib";
import { useRole, can } from "../role";

const TABS = [
  { id: "thresholds", label: "Detection & Thresholds", icon: SlidersHorizontal },
  { id: "model", label: "Reasoning Model", icon: Cpu },
  { id: "library", label: "Rule Library", icon: Library },
  { id: "integration", label: "Integration", icon: Plug },
] as const;

export default function Admin() {
  const { role } = useRole();
  const [tab, setTab] = useState<(typeof TABS)[number]["id"]>("thresholds");
  if (!can(role, "admin")) {
    return <div className="card p-8 text-center text-sm text-slate-500">Admin only — switch to the Admin role to manage configuration.</div>;
  }
  return (
    <div className="fadeup space-y-5">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Admin / Configuration</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Runtime settings that drive the engine — changes apply on the next run and are recorded
          in the Decision Log. Admin only.
        </p>
      </div>
      <div className="flex gap-1 border-b border-slate-200">
        {TABS.map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={clsx("flex items-center gap-1.5 px-3 py-2 text-sm font-medium border-b-2 -mb-px",
              tab === t.id ? "border-ace-600 text-ace-700" : "border-transparent text-slate-500 hover:text-slate-700")}>
            <t.icon size={15} /> {t.label}
          </button>
        ))}
      </div>
      {tab === "thresholds" && <Thresholds />}
      {tab === "model" && <ReasoningModel />}
      {tab === "library" && <RuleLibraryAdmin />}
      {tab === "integration" && <Integration />}
    </div>
  );
}

function useConfig() {
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ["admin-config"], queryFn: api.adminConfig });
  const save = useMutation({
    mutationFn: ({ key, value }: { key: string; value: any }) => api.putConfig(key, value),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-config"] }),
  });
  const reset = useMutation({ mutationFn: api.resetConfig, onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-config"] }) });
  return { cfg: q.data?.config, save, reset };
}

function Num({ label, value, onChange, step = "0.01" }: { label: string; value: number; onChange: (v: number) => void; step?: string }) {
  return (
    <label className="flex items-center justify-between gap-3 text-sm">
      <span className="text-slate-600">{label}</span>
      <input type="number" step={step} value={value} onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-28 rounded-lg border border-slate-200 px-2 py-1.5 text-sm tabular-nums" />
    </label>
  );
}

function Thresholds() {
  const { cfg, save, reset } = useConfig();
  const [c, setC] = useState<any>(null);
  useEffect(() => { if (cfg) setC({ confidence: { ...cfg.confidence }, denials: { ...cfg.denials } }); }, [cfg]);
  if (!c) return <Spinner className="h-6 w-6 text-ace-500" />;
  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="card p-4 space-y-3">
        <div className="font-semibold text-slate-700">Confidence ladder</div>
        <Num label="AUTO_LOAD ≥" value={c.confidence.auto_load} onChange={(v) => setC({ ...c, confidence: { ...c.confidence, auto_load: v } })} />
        <Num label="VERIFY ≥" value={c.confidence.verify} onChange={(v) => setC({ ...c, confidence: { ...c.confidence, verify: v } })} />
        <Num label="Needs-attention below" value={c.confidence.attention_below} onChange={(v) => setC({ ...c, confidence: { ...c.confidence, attention_below: v } })} />
        <button className="btn-primary w-full" disabled={save.isPending} onClick={() => save.mutate({ key: "confidence", value: c.confidence })}>
          {save.isPending ? <Spinner className="h-4 w-4" /> : <Save size={15} />} Save confidence
        </button>
      </div>
      <div className="card p-4 space-y-3">
        <div className="font-semibold text-slate-700">Denial detection</div>
        <Num label="Recent window (days)" value={c.denials.recent_window_days} step="1" onChange={(v) => setC({ ...c, denials: { ...c.denials, recent_window_days: v } })} />
        <Num label="Spike z-threshold" value={c.denials.z_threshold} step="0.1" onChange={(v) => setC({ ...c, denials: { ...c.denials, z_threshold: v } })} />
        <Num label="Lift threshold" value={c.denials.lift_threshold} step="0.1" onChange={(v) => setC({ ...c, denials: { ...c.denials, lift_threshold: v } })} />
        <Num label="Min denials" value={c.denials.min_denials} step="1" onChange={(v) => setC({ ...c, denials: { ...c.denials, min_denials: v } })} />
        <button className="btn-primary w-full" disabled={save.isPending} onClick={() => save.mutate({ key: "denials", value: c.denials })}>
          {save.isPending ? <Spinner className="h-4 w-4" /> : <Save size={15} />} Save detection
        </button>
      </div>
      <div className="col-span-2">
        <button className="btn-ghost" disabled={reset.isPending} onClick={() => reset.mutate()}>
          <RotateCcw size={15} /> Reset all config to defaults
        </button>
      </div>
    </div>
  );
}

function ReasoningModel() {
  const { data: status } = useQuery({ queryKey: ["llm-status"], queryFn: api.llmStatus });
  const test = useMutation({ mutationFn: api.testLlm });
  return (
    <div className="card p-4 space-y-3 max-w-lg">
      <div className="font-semibold text-slate-700">Active reasoning model</div>
      <div className="text-sm font-mono text-slate-600">{status?.model ?? "…"}</div>
      <div className="flex gap-2 text-xs">
        <span className={clsx("pill ring-1", status?.available ? "bg-emerald-50 text-emerald-700 ring-emerald-200" : "bg-rose-50 text-rose-700 ring-rose-200")}>
          {status?.available ? "available" : "offline"}
        </span>
        <span className="pill bg-slate-100 text-slate-600">Anthropic key: {status?.anthropic_key ? "set" : "—"}</span>
      </div>
      <button className="btn-primary" disabled={test.isPending} onClick={() => test.mutate()}>
        {test.isPending ? <Spinner className="h-4 w-4" /> : <Check size={15} />} Test connection
      </button>
      {test.data && (
        <div className={clsx("text-sm", test.data.ok ? "text-emerald-600" : "text-rose-600")}>
          {test.data.ok ? `OK · ${test.data.model}` : `Failed · ${test.data.error}`}
        </div>
      )}
      <div className="text-[11px] text-slate-400">API keys are read from the environment only — never stored or shown.</div>
    </div>
  );
}

function RuleLibraryAdmin() {
  const qc = useQueryClient();
  const { data: rules } = useQuery({ queryKey: ["rule-library"], queryFn: api.ruleLibrary });
  const [nw, setNw] = useState({ id: "", payer: "", title: "", cpt: "" });
  const create = useMutation({
    mutationFn: () => api.createRule({ id: nw.id, payer: nw.payer, title: nw.title, code_sets: { cpt: nw.cpt ? nw.cpt.split(",").map((s) => s.trim()) : [] } }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["rule-library"] }); setNw({ id: "", payer: "", title: "", cpt: "" }); },
  });
  const del = useMutation({ mutationFn: (id: string) => api.deleteRule(id), onSuccess: () => qc.invalidateQueries({ queryKey: ["rule-library"] }) });
  return (
    <div className="space-y-3">
      <div className="card p-4 grid grid-cols-5 gap-2 items-end">
        {([["id", "Rule id"], ["payer", "Payer"], ["title", "Title"], ["cpt", "CPT (comma-sep)"]] as const).map(([k, lbl]) => (
          <label key={k} className="text-xs text-slate-500">{lbl}
            <input value={(nw as any)[k]} onChange={(e) => setNw({ ...nw, [k]: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-sm" />
          </label>
        ))}
        <button className="btn-primary" disabled={create.isPending || !nw.id || !nw.payer} onClick={() => create.mutate()}>
          {create.isPending ? <Spinner className="h-4 w-4" /> : <Plus size={15} />} Add
        </button>
      </div>
      {(rules ?? []).map((r) => (
        <div key={r.id} className="card p-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm">
            <span className="pill bg-ace-50 text-ace-700 ring-1 ring-ace-100 font-mono">{r.id}</span>
            <span className="text-slate-500">{r.payer}</span>
            <span className="text-slate-700">{r.title}</span>
          </div>
          <button className="btn-ghost text-rose-600" onClick={() => del.mutate(r.id)}><Trash2 size={15} /></button>
        </div>
      ))}
    </div>
  );
}

function Integration() {
  const { cfg, save } = useConfig();
  const [c, setC] = useState<any>(null);
  useEffect(() => { if (cfg) setC({ ...cfg.integration }); }, [cfg]);
  if (!c) return <Spinner className="h-6 w-6 text-ace-500" />;
  return (
    <div className="card p-4 space-y-3 max-w-2xl">
      <label className="text-sm text-slate-600 block">ACE base URL
        <input value={c.ace_base_url} onChange={(e) => setC({ ...c, ace_base_url: e.target.value })}
          className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-mono" />
      </label>
      <label className="text-sm text-slate-600 block">Source tag
        <input value={c.source_tag} onChange={(e) => setC({ ...c, source_tag: e.target.value })}
          className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-mono" />
      </label>
      <label className="text-sm text-slate-600 block">Demo-payer denylist (never published to; comma-sep)
        <input value={(c.demo_payer_denylist || []).join(", ")} onChange={(e) => setC({ ...c, demo_payer_denylist: e.target.value.split(",").map((s: string) => s.trim()).filter(Boolean) })}
          className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
      </label>
      <button className="btn-primary" disabled={save.isPending} onClick={() => save.mutate({ key: "integration", value: c })}>
        {save.isPending ? <Spinner className="h-4 w-4" /> : <Save size={15} />} Save integration
      </button>
    </div>
  );
}
