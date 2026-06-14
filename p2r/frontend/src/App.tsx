import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Workbench from "./pages/Workbench";
import Sources from "./pages/Sources";
import DenialDiscovery from "./pages/DenialDiscovery";
import ReviewQueue from "./pages/ReviewQueue";
import RuleLibrary from "./pages/RuleLibrary";
import EvalHarness from "./pages/EvalHarness";
import DecisionLog from "./pages/DecisionLog";
import Admin from "./pages/Admin";
import { useRole, canAccess } from "./role";

// Route-level access guard: even on direct-URL navigation, a role only sees screens it may use.
function Guard({ route, children }: { route: string; children: React.ReactNode }) {
  const { role } = useRole();
  if (!canAccess(route, role)) {
    return (
      <div className="card p-8 text-center text-sm text-slate-500 fadeup">
        This screen isn’t available for the <span className="font-semibold">{role}</span> role.
        Switch roles from the top-right selector if you need access.
      </div>
    );
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Guard route="/"><Workbench /></Guard>} />
        <Route path="/sources" element={<Guard route="/sources"><Sources /></Guard>} />
        <Route path="/denials" element={<Guard route="/denials"><DenialDiscovery /></Guard>} />
        <Route path="/review" element={<Guard route="/review"><ReviewQueue /></Guard>} />
        <Route path="/library" element={<Guard route="/library"><RuleLibrary /></Guard>} />
        <Route path="/eval" element={<Guard route="/eval"><EvalHarness /></Guard>} />
        <Route path="/audit" element={<Guard route="/audit"><DecisionLog /></Guard>} />
        <Route path="/admin" element={<Guard route="/admin"><Admin /></Guard>} />
      </Routes>
    </Layout>
  );
}
