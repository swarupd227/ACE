import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Worklist from "./pages/Worklist";
import ControlTower from "./pages/ControlTower";
import EncounterDetail from "./pages/EncounterDetail";
import Dashboard from "./pages/Dashboard";
import PolicyAdmin from "./pages/PolicyAdmin";
import Integrations from "./pages/Integrations";
import EvalHarness from "./pages/EvalHarness";
import Learning from "./pages/Learning";
import Cdi from "./pages/Cdi";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Worklist />} />
        <Route path="/control-tower" element={<ControlTower />} />
        <Route path="/cdi" element={<Cdi />} />
        <Route path="/encounter/:id" element={<EncounterDetail />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/policy" element={<PolicyAdmin />} />
        <Route path="/integrations" element={<Integrations />} />
        <Route path="/eval" element={<EvalHarness />} />
        <Route path="/learning" element={<Learning />} />
      </Routes>
    </Layout>
  );
}
