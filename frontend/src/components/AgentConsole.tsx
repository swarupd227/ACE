import { useEffect, useRef, useState } from "react";
import clsx from "clsx";
import { X, Cpu, CheckCircle2, Loader2, AlertTriangle } from "lucide-react";
import { LaneBadge } from "../lib";
import type { Run } from "../types";

const API_BASE = (import.meta as any).env?.VITE_API_BASE ?? "/api";

type Line = { actor: string; msg: string; level: string; ts?: string };

const STEPS: [string, string][] = [
  ["0", "Eligibility"], ["1", "Conditioning"], ["2", "Extraction"],
  ["rag", "Graph-RAG"], ["3", "Coding"], ["4", "Validation"], ["5", "Routing"],
];

const LEVEL: Record<string, string> = {
  head: "text-white font-semibold",
  info: "text-slate-300",
  tool: "text-cyan-300",
  good: "text-emerald-300",
  warn: "text-amber-300",
  bad: "text-rose-300",
};

function hhmmss(ts?: string) {
  if (!ts) return "";
  try { return new Date(ts).toLocaleTimeString([], { hour12: false }); } catch { return ""; }
}

export default function AgentConsole({
  encounterId, title, onClose, onDone,
}: { encounterId: string; title: string; onClose: () => void; onDone?: (run: Run) => void }) {
  const [lines, setLines] = useState<Line[]>([]);
  const [reached, setReached] = useState<Set<string>>(new Set());
  const [status, setStatus] = useState<"running" | "done" | "error">("running");
  const [result, setResult] = useState<{ lane: string; reason: string } | null>(null);
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const es = new EventSource(`${API_BASE}/encounters/${encounterId}/code/stream`);
    es.onmessage = (e) => {
      const ev = JSON.parse(e.data);
      if (ev.type === "log") setLines((l) => [...l, ev]);
      else if (ev.type === "stage") setReached((s) => new Set(s).add(ev.key));
      else if (ev.type === "routing") setResult({ lane: ev.lane, reason: ev.reason });
      else if (ev.type === "done") { setStatus("done"); es.close(); onDone?.(ev.run); }
      else if (ev.type === "error") {
        setStatus("error");
        setLines((l) => [...l, { actor: "error", msg: ev.detail, level: "bad" }]);
        es.close();
      }
    };
    es.onerror = () => es.close(); // no auto-reconnect (would re-trigger a run)
    return () => es.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [encounterId]);

  useEffect(() => { if (boxRef.current) boxRef.current.scrollTop = boxRef.current.scrollHeight; }, [lines]);

  return (
    <div className="fixed inset-0 z-50 bg-black/50 grid place-items-center p-4" onClick={onClose}>
      <div className="w-full max-w-3xl rounded-xl overflow-hidden shadow-2xl" onClick={(e) => e.stopPropagation()}>
        {/* header */}
        <div className="bg-ace-900 text-white px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu size={16} className="text-brand-300" />
            <span className="font-semibold">Autonomous Coding Agent</span>
            <span className="text-xs text-slate-400">· {title}</span>
          </div>
          <div className="flex items-center gap-3">
            {status === "running" && <span className="flex items-center gap-1.5 text-xs text-cyan-300"><Loader2 size={13} className="animate-spin" /> working…</span>}
            {status === "done" && <span className="flex items-center gap-1.5 text-xs text-emerald-300"><CheckCircle2 size={13} /> complete</span>}
            {status === "error" && <span className="flex items-center gap-1.5 text-xs text-rose-300"><AlertTriangle size={13} /> error</span>}
            <button onClick={onClose} className="text-slate-400 hover:text-white"><X size={16} /></button>
          </div>
        </div>

        {/* step bar */}
        <div className="bg-ace-900/95 px-4 pb-3 flex gap-1.5">
          {STEPS.map(([key, label]) => (
            <div key={key} className="flex-1">
              <div className={clsx("h-1 rounded-full transition-colors", reached.has(key) ? "bg-brand-400" : "bg-white/10")} />
              <div className={clsx("mt-1 text-[10px]", reached.has(key) ? "text-slate-200" : "text-slate-500")}>{label}</div>
            </div>
          ))}
        </div>

        {/* console */}
        <div ref={boxRef} className="bg-[#0b1020] h-[52vh] overflow-y-auto px-4 py-3 font-mono text-[12.5px] leading-relaxed">
          {lines.map((ln, i) => (
            <div key={i} className="flex gap-2 fadeup">
              <span className="text-slate-600 select-none shrink-0">{hhmmss(ln.ts)}</span>
              <span className={clsx("shrink-0", ln.actor.startsWith("  ") ? "text-slate-500" : "text-ace-300")}>
                {ln.actor.trim()}
              </span>
              <span className="text-slate-600">›</span>
              <span className={clsx(LEVEL[ln.level] ?? "text-slate-300", "whitespace-pre-wrap")}>{ln.msg}</span>
            </div>
          ))}
          {status === "running" && <div className="text-cyan-400 animate-pulse">▋</div>}
        </div>

        {/* footer */}
        <div className="bg-ace-900 text-white px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm">
            {result ? (<><span className="text-slate-400">Routing decision:</span><LaneBadge lane={result.lane as any} /><span className="text-xs text-slate-400">{result.reason}</span></>)
              : <span className="text-xs text-slate-400">streaming the agent's stages and tool calls…</span>}
          </div>
          <button className="btn-ghost py-1.5" disabled={status === "running"} onClick={onClose}>
            {status === "running" ? "running…" : "Close"}
          </button>
        </div>
      </div>
    </div>
  );
}
