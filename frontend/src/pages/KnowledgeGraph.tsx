import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import clsx from "clsx";
import { api } from "../api";
import { Spinner } from "../lib";

const COLS: Record<string, { x: number; color: string; label: string }> = {
  payer: { x: 140, color: "#f26722", label: "Payers" },
  concept: { x: 470, color: "#6366f1", label: "Ontology concepts" },
  code: { x: 800, color: "#0ea5e9", label: "Codes" },
};

export default function KnowledgeGraph() {
  const { data, isLoading } = useQuery({ queryKey: ["kg"], queryFn: api.kg });
  const [hover, setHover] = useState<string | null>(null);

  const layout = useMemo(() => {
    if (!data) return null;
    const byType: Record<string, any[]> = { payer: [], concept: [], code: [] };
    data.nodes.forEach((n) => (byType[n.type] ?? (byType[n.type] = [])).push(n));
    const pos: Record<string, { x: number; y: number; node: any }> = {};
    const rowH = 56;
    const top = 40;
    Object.entries(byType).forEach(([type, nodes]) => {
      const col = COLS[type];
      if (!col) return;
      nodes.forEach((n, i) => {
        pos[n.id] = { x: col.x, y: top + i * rowH, node: n };
      });
    });
    const height = top + Math.max(...Object.values(byType).map((a) => a.length)) * rowH + 20;
    return { pos, height };
  }, [data]);

  if (isLoading || !data || !layout) return <div className="grid place-items-center h-64"><Spinner className="h-6 w-6 text-ace-500" /></div>;

  return (
    <div className="space-y-4 fadeup">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900">Knowledge Graph &amp; Graph-RAG</h1>
        <p className="text-sm text-slate-500">
          Payer policy + medical ontology + code links. The coding agent retrieves over this graph and may
          only emit codes it surfaces — grounding reasoning and reducing ontology-driven hallucination.
        </p>
      </div>

      <div className="card p-4 overflow-x-auto">
        <div className="flex gap-10 mb-2 pl-4 text-xs font-semibold uppercase tracking-wide">
          {Object.values(COLS).map((c) => (
            <span key={c.label} style={{ color: c.color }}>{c.label}</span>
          ))}
        </div>
        <svg width={940} height={layout.height} className="min-w-[940px]">
          {data.links.map((l, i) => {
            const a = layout.pos[l.source];
            const b = layout.pos[l.target];
            if (!a || !b) return null;
            const active = hover && (l.source === hover || l.target === hover);
            const mx = (a.x + b.x) / 2;
            return (
              <path
                key={i}
                d={`M ${a.x} ${a.y} C ${mx} ${a.y}, ${mx} ${b.y}, ${b.x} ${b.y}`}
                fill="none"
                stroke={active ? "#6366f1" : "#cbd5e1"}
                strokeWidth={active ? 2 : 1}
                opacity={hover && !active ? 0.2 : 0.7}
              />
            );
          })}
          {Object.values(layout.pos).map(({ x, y, node }) => {
            const col = COLS[node.type];
            return (
              <g key={node.id} transform={`translate(${x},${y})`}
                 onMouseEnter={() => setHover(node.id)} onMouseLeave={() => setHover(null)}
                 className="cursor-pointer">
                <circle r={hover === node.id ? 8 : 6} fill={col.color} />
                <text x={node.type === "code" ? 12 : -12} y={4}
                      textAnchor={node.type === "code" ? "start" : "end"}
                      className={clsx("text-[12px]", hover === node.id ? "fill-slate-900 font-semibold" : "fill-slate-600")}>
                  {node.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      <div className="grid md:grid-cols-3 gap-3">
        <Legend color="#f26722" title="Payers" desc="Anthem, Cigna, Medicare — policies & prior-auth rules attach to codes." />
        <Legend color="#6366f1" title="Concepts" desc="Medical ontology (SNOMED-style) with is_a / finding_site / associated_with edges." />
        <Legend color="#0ea5e9" title="Codes" desc="ICD-10-CM / CPT the concepts and policies map to." />
      </div>
    </div>
  );
}

function Legend({ color, title, desc }: { color: string; title: string; desc: string }) {
  return (
    <div className="card p-4">
      <div className="flex items-center gap-2 font-semibold text-slate-800">
        <span className="h-2.5 w-2.5 rounded-full" style={{ background: color }} /> {title}
      </div>
      <p className="mt-1 text-xs text-slate-500">{desc}</p>
    </div>
  );
}
