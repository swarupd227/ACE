import { NavLink } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import clsx from "clsx";
import {
  LayoutList, LayoutDashboard, BarChart3, ShieldCheck, FlaskConical, GraduationCap,
  Cpu, Stethoscope, Plug, SlidersHorizontal, UserCog, ScrollText,
} from "lucide-react";
import { api } from "../api";
import { useRole, ROLES, canAccess } from "../role";

const nav = [
  { to: "/", label: "Worklist", icon: LayoutList, end: true },
  { to: "/control-tower", label: "Control Tower", icon: LayoutDashboard },
  { to: "/cdi", label: "CDI / Physician Queries", icon: Stethoscope },
  { to: "/dashboard", label: "Performance Dashboard", icon: BarChart3 },
  { to: "/policy", label: "Policy & Knowledge Admin", icon: ShieldCheck },
  { to: "/integrations", label: "Integrations & Ingestion", icon: Plug },
  { to: "/eval", label: "Evaluation Harness", icon: FlaskConical },
  { to: "/learning", label: "Closed-Loop Learning", icon: GraduationCap },
  { to: "/audit", label: "Audit Log", icon: ScrollText },
  { to: "/admin", label: "Admin / Configuration", icon: SlidersHorizontal },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const { data: meta } = useQuery({ queryKey: ["meta"], queryFn: api.meta });
  const { role } = useRole();
  const visibleNav = nav.filter((n) => canAccess(n.to, role));

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <aside className="w-64 shrink-0 bg-ace-900 text-slate-200 flex flex-col">
        <div className="px-5 py-5 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-lg bg-brand-500 grid place-items-center font-extrabold text-white">A</div>
            <div>
              <div className="font-bold text-white leading-tight">ACE</div>
              <div className="text-[11px] text-slate-400 leading-tight">Autonomous Coding Engine</div>
            </div>
          </div>
          <div className="mt-3 text-[10px] uppercase tracking-wider text-slate-500">
            inside RevAmp · Coding Studio
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {visibleNav.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive ? "bg-white/10 text-white" : "text-slate-300 hover:bg-white/5 hover:text-white"
                )
              }
            >
              <n.icon size={18} />
              {n.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-white/10 space-y-2">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <ShieldCheck size={14} className="text-emerald-400" />
            HIPAA-shaped · US-region · audit-logged
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Cpu size={14} className={meta?.llm_available ? "text-emerald-400" : "text-rose-400"} />
            <span className="font-mono truncate">{meta?.model_version ?? "…"}</span>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 shrink-0 bg-white border-b border-slate-200 flex items-center justify-between px-6">
          <div className="text-sm text-slate-500">
            Vee Healthtek <span className="text-slate-300">/</span>{" "}
            <span className="font-semibold text-slate-700">Autonomous Medical Coding</span>
          </div>
          <div className="flex items-center gap-3">
            {meta && !meta.llm_available && (
              <span className="pill bg-rose-50 text-rose-700 ring-1 ring-rose-200">
                LLM not configured — charts route to manual queue
              </span>
            )}
            <span className="pill bg-brand-50 text-brand-700 ring-1 ring-brand-300">
              {!meta ? "…" : meta.llm_mode === "anthropic" ? "Claude (Anthropic)" : meta.llm_mode === "openai_compatible" ? "OpenAI-compatible" : meta.llm_mode}
            </span>
            <RoleSwitcher />
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}

function RoleSwitcher() {
  const { role, setRole } = useRole();
  return (
    <div className="flex items-center gap-1.5" title="Switch role (demo RBAC; maps to SSO/scopes in prod)">
      <UserCog size={15} className="text-slate-400" />
      <select
        value={role}
        onChange={(e) => setRole(e.target.value as any)}
        className="rounded-lg border border-slate-200 px-2 py-1.5 text-sm font-medium text-slate-700"
      >
        {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
      </select>
    </div>
  );
}
