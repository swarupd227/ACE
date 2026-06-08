import { useEffect, useMemo, useRef, useState } from "react";
import cytoscape from "cytoscape";
// @ts-ignore — no bundled types
import fcose from "cytoscape-fcose";
import { Search, X, ZoomIn, ZoomOut, Maximize2 } from "lucide-react";

cytoscape.use(fcose);

const TYPE_COLOR: Record<string, string> = { payer: "#f26722", concept: "#6366f1", code: "#0ea5e9" };

type KgNode = { id: string; label: string; type: string; system?: string; semantic_type?: string };
type KgLink = { source: string; target: string; rel: string; detail?: string; requires_auth?: boolean };

export default function OntologyGraph({ nodes, links }: { nodes: KgNode[]; links: KgLink[] }) {
  const boxRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [q, setQ] = useState("");
  const [sel, setSel] = useState<KgNode | null>(null);

  const adjacency = useMemo(() => {
    const m: Record<string, { rel: string; other: string; detail?: string; requires_auth?: boolean }[]> = {};
    links.forEach((l) => {
      (m[l.source] ??= []).push({ rel: l.rel, other: l.target, detail: l.detail, requires_auth: l.requires_auth });
      (m[l.target] ??= []).push({ rel: l.rel, other: l.source, detail: l.detail, requires_auth: l.requires_auth });
    });
    return m;
  }, [links]);
  const labelOf = (id: string) => nodes.find((n) => n.id === id)?.label ?? id;

  useEffect(() => {
    if (!boxRef.current) return;
    const cy = cytoscape({
      container: boxRef.current,
      elements: [
        ...nodes.map((n) => ({ data: { id: n.id, label: n.label, type: n.type } })),
        ...links.map((l, i) => ({ data: { id: `e${i}`, source: l.source, target: l.target, rel: l.rel } })),
      ],
      style: [
        {
          selector: "node",
          style: {
            "background-color": (ele: any) => TYPE_COLOR[ele.data("type")] ?? "#94a3b8",
            label: "data(label)", "font-size": 9, color: "#334155",
            "text-valign": "bottom", "text-halign": "center", "text-margin-y": 3,
            width: 16, height: 16, "border-width": 0,
            shape: (ele: any) => (ele.data("type") === "code" ? "round-rectangle" : ele.data("type") === "payer" ? "diamond" : "ellipse"),
          } as any,
        },
        { selector: "node:selected", style: { "border-width": 3, "border-color": "#1e1b4b", width: 22, height: 22 } as any },
        {
          selector: "edge",
          style: {
            width: 1.4, "line-color": "#cbd5e1", "curve-style": "bezier",
            "target-arrow-shape": "triangle", "target-arrow-color": "#cbd5e1", "arrow-scale": 0.8,
            label: "data(rel)", "font-size": 7, color: "#94a3b8",
            "text-rotation": "autorotate", "text-background-color": "#fff", "text-background-opacity": 0.85, "text-background-padding": "1px",
          } as any,
        },
        { selector: ".faded", style: { opacity: 0.12 } as any },
        { selector: ".hl", style: { "line-color": "#6366f1", "target-arrow-color": "#6366f1", width: 2.5 } as any },
      ],
      layout: { name: "fcose", animate: true, randomize: true, idealEdgeLength: 95, nodeRepulsion: 7000, padding: 24 } as any,
      wheelSensitivity: 0.25,
    });
    cyRef.current = cy;

    cy.on("tap", "node", (evt) => {
      const id = evt.target.id();
      const node = nodes.find((n) => n.id === id) ?? null;
      setSel(node);
      cy.elements().addClass("faded").removeClass("hl");
      const nbr = evt.target.closedNeighborhood();
      nbr.removeClass("faded");
      nbr.edges().addClass("hl");
    });
    cy.on("tap", (evt) => { if (evt.target === cy) { setSel(null); cy.elements().removeClass("faded hl"); } });

    return () => cy.destroy();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodes, links]);

  // search → highlight/filter
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    if (!q) { cy.elements().removeClass("faded"); return; }
    const ql = q.toLowerCase();
    cy.elements().addClass("faded");
    const matched = cy.nodes().filter((n: any) => (n.data("label") || "").toLowerCase().includes(ql));
    matched.removeClass("faded");
    matched.connectedEdges().removeClass("faded").connectedNodes().removeClass("faded");
  }, [q]);

  const fit = () => cyRef.current?.animate({ fit: { eles: cyRef.current.elements(), padding: 24 }, duration: 300 });
  const zoom = (f: number) => { const cy = cyRef.current; if (cy) cy.animate({ zoom: cy.zoom() * f, center: { eles: cy.elements() } }, { duration: 150 }); };

  return (
    <div className="grid lg:grid-cols-[1fr_300px] gap-4">
      <div className="card p-0 overflow-hidden relative">
        <div className="absolute top-2 left-2 right-2 z-10 flex items-center justify-between gap-2">
          <div className="relative">
            <Search size={14} className="absolute left-2.5 top-2.5 text-slate-400" />
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search ontology…"
              className="w-56 rounded-lg border border-slate-200 bg-white/95 pl-8 pr-3 py-1.5 text-sm shadow-sm" />
          </div>
          <div className="flex gap-1">
            <button onClick={() => zoom(1.2)} className="btn-ghost p-1.5 bg-white/95"><ZoomIn size={14} /></button>
            <button onClick={() => zoom(0.83)} className="btn-ghost p-1.5 bg-white/95"><ZoomOut size={14} /></button>
            <button onClick={fit} className="btn-ghost p-1.5 bg-white/95"><Maximize2 size={14} /></button>
          </div>
        </div>
        <div ref={boxRef} className="h-[64vh] w-full bg-[radial-gradient(circle_at_1px_1px,#e2e8f0_1px,transparent_0)] [background-size:20px_20px]" />
        <div className="absolute bottom-2 left-2 flex gap-3 text-[11px] bg-white/90 rounded px-2 py-1">
          {Object.entries(TYPE_COLOR).map(([t, c]) => (
            <span key={t} className="inline-flex items-center gap-1 capitalize"><span className="h-2 w-2 rounded-full" style={{ background: c }} />{t}</span>
          ))}
        </div>
      </div>

      {/* detail */}
      <div className="card p-4 h-fit">
        {sel ? (
          <div>
            <div className="flex items-center justify-between">
              <span className="pill ring-1 ring-slate-200 bg-slate-100 text-slate-600 capitalize">{sel.type}</span>
              <button onClick={() => { setSel(null); cyRef.current?.elements().removeClass("faded hl"); }} className="text-slate-400 hover:text-slate-700"><X size={15} /></button>
            </div>
            <h3 className="mt-2 font-bold text-slate-900">{sel.label}</h3>
            {sel.system && <div className="text-xs text-slate-500">{sel.system}</div>}
            <div className="mt-3 label">Relationships ({(adjacency[sel.id] ?? []).length})</div>
            <div className="mt-1 space-y-1.5 max-h-[44vh] overflow-y-auto">
              {(adjacency[sel.id] ?? []).map((a, i) => (
                <div key={i} className="text-xs text-slate-600 border-l-2 border-ace-200 pl-2">
                  <span className="text-slate-400">{a.rel}</span> → <span className="font-medium">{labelOf(a.other)}</span>
                  {a.requires_auth && <span className="ml-1 text-amber-600">(prior auth)</span>}
                  {a.detail && <div className="text-slate-400">{a.detail}</div>}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-sm text-slate-500">
            Interactive ontology graph (Cytoscape · fcose force layout). Drag nodes, zoom, search, and
            click any node to inspect its relationships. Payer→code edges are managed in the Policies tab.
          </div>
        )}
      </div>
    </div>
  );
}
