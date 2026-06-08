import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import clsx from "clsx";
import { Search, Database, GitBranch, Layers, RefreshCw, ShieldCheck, X } from "lucide-react";
import { api } from "../api";
import { Spinner } from "../lib";

const COLS: Record<string, { x: number; color: string; label: string }> = {
  payer: { x: 150, color: "#f26722", label: "Payers" },
  concept: { x: 480, color: "#6366f1", label: "Ontology concepts" },
  code: { x: 810, color: "#0ea5e9", label: "Codes" },
};

export default function KnowledgeGraph() {
  const { data, isLoading } = useQuery({ queryKey: ["kg"], queryFn: api.kg });
  const [sel, setSel] = useState<string | null>(null);
  const [q, setQ] = useState("");

  const layout = useMemo(() => {
    if (!data) return null;
    const byType: Record<string, any[]> = { payer: [], concept: [], code: [] };
    data.nodes.forEach((n) => (byType[n.type] ?? (byType[n.type] = [])).push(n));
    const pos: Record<string, { x: number; y: number; node: any }> = {};
    const rowH = 50, top = 36;
    Object.entries(byType).forEach(([type, nodes]) => {
      const col = COLS[type];
      if (!col) return;
      nodes.sort((a, b) => a.label.localeCompare(b.label));
      nodes.forEach((n, i) => { pos[n.id] = { x: col.x, y: top + i * rowH, node: n }; });
    });
    const height = top + Math.max(...Object.values(byType).map((a) => a.length)) * rowH + 20;
    return { pos, height };
  }, [data]);

  const adjacency = useMemo(() => {
    const m: Record<string, { rel: string; other: string; detail?: string; requires_auth?: boolean }[]> = {};
    data?.links.forEach((l) => {
      (m[l.source] ??= []).push({ rel: l.rel, other: l.target, detail: l.detail, requires_auth: l.requires_auth });
      (m[l.target] ??= []).push({ rel: l.rel, other: l.source, detail: l.detail, requires_auth: l.requires_auth });
    });
    return m;
  }, [data]);

  if (isLoading || !data || !layout) return <div className="grid place-items-center h-64"><Spinner className="h-6 w-6 text-ace-500" /></div>;

  const labelOf = (id: string) => data.nodes.find((n) => n.id === id)?.label ?? id;
  const matches = (n: any) => q && n.label.toLowerCase().includes(q.toLowerCase());
  const neighborIds = sel ? new Set((adjacency[sel] ?? []).map((a) => a.other).concat(sel)) : null;
  const selNode = sel ? data.nodes.find((n) => n.id === sel) : null;
  const counts = { payer: 0, concept: 0, code: 0 } as Record<string, number>;
  data.nodes.forEach((n) => (counts[n.type] = (counts[n.type] ?? 0) + 1));

  return (
    <div className="space-y-4 fadeup">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Knowledge Graph &amp; Graph-RAG</h1>
          <p className="text-sm text-slate-500">
            Payer policy + medical ontology + codes. The coding agent retrieves over this graph and may
            only emit codes it surfaces — grounding reasoning and reducing hallucination. Click a node to
            see what it drives.
          </p>
        </div>
        <div className="relative">
          <Search size={15} className="absolute left-2.5 top-2.5 text-slate-400" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search nodes…"
                 className="w-56 rounded-lg border border-slate-200 pl-8 pr-3 py-2 text-sm" />
        </div>
      </div>

      <div className="grid lg:grid-cols-[1fr_320px] gap-4">
        {/* Graph */}
        <div className="card p-4 overflow-x-auto">
          <div className="flex gap-10 mb-2 pl-4 text-xs font-semibold uppercase tracking-wide">
            {Object.entries(COLS).map(([t, c]) => (
              <span key={c.label} style={{ color: c.color }}>{c.label} ({counts[t] ?? 0})</span>
            ))}
          </div>
          <svg width={960} height={layout.height} className="min-w-[960px]">
            {data.links.map((l, i) => {
              const a = layout.pos[l.source], b = layout.pos[l.target];
              if (!a || !b) return null;
              const active = sel && (l.source === sel || l.target === sel);
              const mx = (a.x + b.x) / 2;
              return (
                <path key={i} d={`M ${a.x} ${a.y} C ${mx} ${a.y}, ${mx} ${b.y}, ${b.x} ${b.y}`} fill="none"
                      stroke={active ? "#6366f1" : "#cbd5e1"} strokeWidth={active ? 2 : 1}
                      opacity={sel && !active ? 0.12 : 0.65} />
              );
            })}
            {Object.values(layout.pos).map(({ x, y, node }) => {
              const col = COLS[node.type];
              const dim = (sel && neighborIds && !neighborIds.has(node.id)) || (q && !matches(node));
              const hit = matches(node);
              return (
                <g key={node.id} transform={`translate(${x},${y})`} className="cursor-pointer"
                   onClick={() => setSel(node.id === sel ? null : node.id)} opacity={dim ? 0.25 : 1}>
                  <circle r={sel === node.id ? 8 : hit ? 7 : 5} fill={col.color} stroke={hit ? "#111827" : "none"} strokeWidth={hit ? 2 : 0} />
                  <text x={node.type === "code" ? 12 : -12} y={4} textAnchor={node.type === "code" ? "start" : "end"}
                        className={clsx("text-[12px]", sel === node.id ? "fill-slate-900 font-semibold" : "fill-slate-600")}>
                    {node.label}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Detail / stats panel */}
        <div className="card p-4 h-fit lg:sticky lg:top-4">
          {selNode ? (
            <div>
              <div className="flex items-center justify-between">
                <span className="pill ring-1 ring-slate-200 bg-slate-100 text-slate-600 capitalize">{selNode.type}</span>
                <button onClick={() => setSel(null)} className="text-slate-400 hover:text-slate-700"><X size={15} /></button>
              </div>
              <h3 className="mt-2 font-bold text-slate-900">{selNode.label}</h3>
              {selNode.semantic_type && <div className="text-xs text-slate-500">{selNode.semantic_type}</div>}
              {selNode.system && <div className="text-xs text-slate-500">{selNode.system}</div>}
              <div className="mt-3 label">Connections ({(adjacency[sel!] ?? []).length})</div>
              <div className="mt-1 space-y-1.5 max-h-80 overflow-y-auto">
                {(adjacency[sel!] ?? []).map((a, i) => (
                  <div key={i} className="text-xs text-slate-600 border-l-2 border-ace-200 pl-2">
                    <span className="text-slate-400">{a.rel}</span> → <span className="font-medium">{labelOf(a.other)}</span>
                    {a.requires_auth && <span className="ml-1 text-amber-600">(prior auth)</span>}
                    {a.detail && <div className="text-slate-400">{a.detail}</div>}
                  </div>
                ))}
              </div>
              <p className="mt-3 text-[11px] text-slate-400">
                This node is part of the context the coding agent retrieves; payer links also drive the
                deterministic medical-necessity gate.
              </p>
            </div>
          ) : (
            <div>
              <div className="font-semibold text-slate-800 text-sm">Graph at a glance</div>
              <div className="mt-2 grid grid-cols-3 gap-2 text-center">
                {Object.entries(COLS).map(([t, c]) => (
                  <div key={t} className="rounded-lg bg-slate-50 p-2">
                    <div className="text-lg font-extrabold" style={{ color: c.color }}>{counts[t] ?? 0}</div>
                    <div className="text-[10px] uppercase tracking-wide text-slate-400">{t}s</div>
                  </div>
                ))}
              </div>
              <p className="mt-3 text-xs text-slate-500">
                {data.links.length} relationships. Edges: <span className="font-mono">maps_to</span>,{" "}
                <span className="font-mono">is_a</span>, <span className="font-mono">finding_site</span>,{" "}
                <span className="font-mono">associated_with</span>, <span className="font-mono">policy</span>.
              </p>
              <p className="mt-2 text-xs text-slate-400">Click any node to inspect it.</p>
            </div>
          )}
        </div>
      </div>

      {/* How we build it for a client */}
      <div>
        <h2 className="text-lg font-bold text-slate-900 mb-2">Building your knowledge graph</h2>
        <div className="grid md:grid-cols-3 gap-3">
          <BuildCard icon={Database} title="Ingest" color="#f26722"
            points={["Payer medical-policy bulletins (Anthem, Cigna, UHC…) parsed into policy nodes",
                     "Medicare LCD/NCD from the CMS coverage database", "Code sets (ICD-10-CM/CPT/HCPCS), NCCI/MUE"]} />
          <BuildCard icon={Layers} title="Ground in ontology" color="#6366f1"
            points={["Map concepts to codes from a licensed ontology (SNOMED CT / UMLS, RxNorm, LOINC)",
                     "Relationships (is_a, finding_site) power specificity + linkage",
                     "Reduces ontology-driven hallucination (codes must be graph-surfaced)"]} />
          <BuildCard icon={GitBranch} title="Curate & per-client overlay" color="#0ea5e9"
            points={["SME-curated payer preferences and client-specific coding rules 'port in' per client",
                     "Multi-tenant: no co-mingling; each client has its own overlay namespace",
                     "Captured coder corrections feed the graph (closed loop)"]} />
        </div>
        <div className="grid md:grid-cols-2 gap-3 mt-3">
          <div className="card p-4 flex items-start gap-3">
            <RefreshCw size={18} className="text-fuchsia-600 mt-0.5 shrink-0" />
            <div><div className="font-semibold text-slate-800 text-sm">Versioned &amp; monitored</div>
              <p className="text-xs text-slate-500">Every policy node is effective-dated and version-tracked; a payer bulletin change updates the node and is flagged before it can cause denial drift.</p></div>
          </div>
          <div className="card p-4 flex items-start gap-3">
            <ShieldCheck size={18} className="text-emerald-600 mt-0.5 shrink-0" />
            <div><div className="font-semibold text-slate-800 text-sm">Where it's leveraged</div>
              <p className="text-xs text-slate-500">Retrieval grounding for the coding agent, the deterministic medical-necessity gate, and the per-chart "Knowledge used" evidence on every encounter.</p></div>
          </div>
        </div>
      </div>
    </div>
  );
}

function BuildCard({ icon: Icon, title, points, color }: { icon: any; title: string; points: string[]; color: string }) {
  return (
    <div className="card p-4">
      <div className="flex items-center gap-2 font-semibold text-slate-800">
        <Icon size={16} style={{ color }} /> {title}
      </div>
      <ul className="mt-2 space-y-1.5 text-xs text-slate-600">
        {points.map((p, i) => <li key={i}>• {p}</li>)}
      </ul>
    </div>
  );
}
