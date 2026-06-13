import { NavLink } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import clsx from "clsx";
import { FileSearch, ClipboardCheck, Library, Cpu, ShieldCheck, Workflow } from "lucide-react";
import { api } from "../api";

const nav = [
  { to: "/", label: "Policy Workbench", icon: FileSearch, end: true },
  { to: "/review", label: "Review Queue", icon: ClipboardCheck },
  { to: "/library", label: "Rule Library", icon: Library },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const { data: meta } = useQuery({ queryKey: ["meta"], queryFn: api.meta });
  const { data: ace } = useQuery({ queryKey: ["ace-status"], queryFn: api.aceStatus, refetchInterval: 20000 });

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <aside className="shrink-0 w-64 bg-ace-900 text-slate-200 flex flex-col">
        <div className="py-5 px-5 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 shrink-0 rounded-lg bg-brand-500 grid place-items-center font-extrabold text-white text-sm">P2R</div>
            <div>
              <div className="font-bold text-white leading-tight">P2R</div>
              <div className="text-[11px] text-slate-400 leading-tight">Policy-to-Rule Intelligence</div>
            </div>
          </div>
          <div className="mt-3 text-[10px] uppercase tracking-wider text-slate-500">
            Nous RCM Framework
          </div>
        </div>

        <nav className="flex-1 py-4 px-3 space-y-1">
          {nav.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive ? "bg-white/10 text-white" : "text-slate-300 hover:bg-white/5 hover:text-white",
                )
              }
            >
              <n.icon size={18} className="shrink-0" />
              {n.label}
            </NavLink>
          ))}
        </nav>

        <div className="py-4 px-4 border-t border-white/10 space-y-2">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <ShieldCheck size={14} className="text-emerald-400 shrink-0" />
            Cited · confidence-gated · audit-first
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Cpu size={14} className={meta?.llm_available ? "text-emerald-400 shrink-0" : "text-rose-400 shrink-0"} />
            <span className="font-mono truncate">{meta?.llm_model ?? "…"}</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400" title="ACE integration glimpse (Phase 5)">
            <Workflow size={14} className={ace?.reachable ? "text-emerald-400 shrink-0" : "text-slate-500 shrink-0"} />
            <span className="truncate">
              {ace?.reachable ? `ACE linked · ${ace.p2r_published_policies ?? 0} published` : "ACE not linked"}
            </span>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 shrink-0 bg-white border-b border-slate-200 flex items-center justify-between px-6">
          <div className="text-sm text-slate-500">
            Nous RCM Framework <span className="text-slate-300">/</span>{" "}
            <span className="font-semibold text-slate-700">Policy-to-Rule Intelligence</span>
          </div>
          <div className="flex items-center gap-3">
            {meta && !meta.llm_available && (
              <span className="pill bg-rose-50 text-rose-700 ring-1 ring-rose-200">
                LLM not configured — extraction routes to HOLD
              </span>
            )}
            <span className="pill bg-brand-50 text-brand-700 ring-1 ring-brand-300">
              {meta?.llm_available ? "Claude (Anthropic)" : "LLM offline"}
            </span>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
