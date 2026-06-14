import { createContext, useContext, useEffect, useState } from "react";

// P2R personas (internal). Demo-grade RBAC: nav + action gating in the UI; the active role is
// also sent as X-Actor/X-Role so the Decision Log attributes actions. Maps to SSO/scopes in prod.
export const ROLES = ["Admin", "Rule Author", "Reviewer", "Auditor"] as const;
export type Role = (typeof ROLES)[number];

// Which roles may use each capability (gates buttons/actions).
const CAP: Record<string, Role[]> = {
  ingest: ["Admin", "Rule Author"],            // Workbench ingest + generate
  acquire: ["Admin", "Rule Author"],           // run acquisition agent
  detect: ["Admin", "Rule Author"],            // denial detect + promote
  edit: ["Admin", "Rule Author", "Reviewer"],  // edit a candidate
  approve: ["Admin", "Reviewer"],              // sign-off
  publish: ["Admin"],                          // publish/rollback to the engine
  run_eval: ["Admin", "Rule Author", "Reviewer"],
  admin: ["Admin"],                            // Admin / Configuration
};

// Which roles can see each route (gates the sidebar).
const ACCESS: Record<string, Role[]> = {
  "/": ["Admin", "Rule Author"],
  "/sources": ["Admin", "Rule Author"],
  "/denials": ["Admin", "Rule Author"],
  "/review": ["Admin", "Rule Author", "Reviewer", "Auditor"],
  "/library": ["Admin", "Rule Author", "Reviewer", "Auditor"],
  "/eval": ["Admin", "Rule Author", "Reviewer", "Auditor"],
  "/audit": ["Admin", "Rule Author", "Reviewer", "Auditor"],
  "/admin": ["Admin"],
};

export function can(role: Role, capability: string): boolean {
  return (CAP[capability] ?? []).includes(role);
}
export function canAccess(route: string, role: Role): boolean {
  return ACCESS[route] ? ACCESS[route].includes(role) : true;
}

interface RoleCtx { role: Role; setRole: (r: Role) => void; }
const Ctx = createContext<RoleCtx>({ role: "Admin", setRole: () => {} });

export function RoleProvider({ children }: { children: React.ReactNode }) {
  const [role, setRoleState] = useState<Role>(() => (localStorage.getItem("p2r_role") as Role) || "Admin");
  useEffect(() => { localStorage.setItem("p2r_role", role); }, [role]);
  return <Ctx.Provider value={{ role, setRole: setRoleState }}>{children}</Ctx.Provider>;
}

export function useRole() { return useContext(Ctx); }
