import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Terminal, X } from "lucide-react";
import { Spinner } from "../lib";

const BASE = (import.meta as any).env?.VITE_API_BASE ?? "/api";
const PHASE_COLOR: Record<string, string> = {
  setup: "text-slate-400", P1: "text-sky-300", P2: "text-rose-300",
  P3: "text-emerald-300", score: "text-violet-300",
  COVERAGE: "text-sky-300", PRIOR_AUTH: "text-violet-300", FREQUENCY: "text-amber-300",
  MODIFIER: "text-emerald-300", DOCUMENTATION: "text-slate-300", BUNDLING: "text-rose-300", POS: "text-teal-300",
};

// Generic live agent-console for a long-running action, driven by Server-Sent Events.
// `path` is the SSE endpoint (with any query string). onDone receives the parsed `done` event.
export default function StreamConsole({ path, title, onDone, onClose }: {
  path: string; title: string; onDone: (ev: any) => void; onClose: () => void;
}) {
  const [lines, setLines] = useState<{ phase?: string; message: string }[]>([]);
  const [err, setErr] = useState("");
  const [done, setDone] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const es = new EventSource(`${BASE}${path}`);
    es.onmessage = (m) => {
      const ev = JSON.parse(m.data);
      if (ev.type === "log") setLines((l) => [...l, { phase: ev.phase, message: ev.message }]);
      else if (ev.type === "done") { setDone(true); es.close(); onDone(ev); }
      else if (ev.type === "error") { setErr(ev.message); es.close(); }
    };
    es.onerror = () => { es.close(); };  // stream ends after 'done'; don't auto-reconnect
    return () => es.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [lines]);

  return createPortal(
    <div className="fixed inset-0 z-50 grid place-items-center bg-slate-900/50 p-4">
      <div className="w-full max-w-2xl rounded-xl bg-ace-900 text-slate-200 shadow-card overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <Terminal size={16} className="text-emerald-400" /> {title}
            {!done && !err && <Spinner className="h-4 w-4 text-slate-400" />}
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white"><X size={18} /></button>
        </div>
        <div className="p-4 font-mono text-xs h-80 overflow-y-auto space-y-1">
          {lines.map((l, i) => (
            <div key={i}>
              {l.phase && <span className={PHASE_COLOR[l.phase] || "text-slate-400"}>[{l.phase}]</span>}{" "}
              <span className="text-slate-200">{l.message}</span>
            </div>
          ))}
          {err && <div className="text-rose-400">error: {err}</div>}
          {done && <div className="text-emerald-400">✓ complete.</div>}
          <div ref={bottomRef} />
        </div>
        <div className="px-4 py-2.5 border-t border-white/10 flex justify-end">
          <button onClick={onClose} className="btn-ghost bg-white/10 border-white/10 text-slate-200 hover:bg-white/20">
            {done || err ? "Close" : "Run in background"}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
