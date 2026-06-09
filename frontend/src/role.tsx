import { createContext, useContext, useState, ReactNode } from "react";

export type Role = "Admin" | "Coder" | "QA Auditor" | "CDI Specialist" | "Supervisor";
export const ROLES: Role[] = ["Admin", "Coder", "QA Auditor", "CDI Specialist", "Supervisor"];

// Which roles may see each route. (Demo-grade RBAC; maps to real SSO/RBAC + scopes in production.)
const ACCESS: Record<string, Role[]> = {
  "/": ["Admin", "Coder", "QA Auditor", "CDI Specialist", "Supervisor"],
  "/control-tower": ["Admin", "QA Auditor", "Supervisor"],
  "/cdi": ["Admin", "CDI Specialist", "Coder"],
  "/dashboard": ["Admin", "QA Auditor", "Supervisor", "Coder"],
  "/policy": ["Admin"],
  "/integrations": ["Admin"],
  "/eval": ["Admin", "Supervisor"],
  "/learning": ["Admin", "QA Auditor", "Supervisor"],
  "/admin": ["Admin"],
};

export function canAccess(path: string, role: Role): boolean {
  return (ACCESS[path] ?? ["Admin"]).includes(role);
}

// Capability flags used to gate in-screen actions.
export function can(role: Role, capability: string): boolean {
  const CAP: Record<string, Role[]> = {
    code: ["Admin", "Coder"],
    override: ["Admin", "Coder", "QA Auditor"],
    reassign: ["Admin", "QA Auditor", "Supervisor"],
    escalate: ["Admin", "Coder", "QA Auditor"],
    rollback: ["Admin", "QA Auditor", "Supervisor"],
    assign: ["Admin", "Supervisor"],
    cdi_respond: ["Admin", "CDI Specialist"],
    edit_policy: ["Admin"],
    configure: ["Admin"],
    ingest: ["Admin", "Coder"],
  };
  return (CAP[capability] ?? ["Admin"]).includes(role);
}

const Ctx = createContext<{ role: Role; setRole: (r: Role) => void }>({ role: "Admin", setRole: () => {} });

export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, setRoleState] = useState<Role>((localStorage.getItem("ace_role") as Role) || "Admin");
  const setRole = (r: Role) => { localStorage.setItem("ace_role", r); setRoleState(r); };
  return <Ctx.Provider value={{ role, setRole }}>{children}</Ctx.Provider>;
}

export const useRole = () => useContext(Ctx);
