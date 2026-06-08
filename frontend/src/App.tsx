import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Worklist from "./pages/Worklist";
import Architecture from "./pages/Architecture";
import EncounterDetail from "./pages/EncounterDetail";
import Dashboard from "./pages/Dashboard";
import KnowledgeGraph from "./pages/KnowledgeGraph";
import EvalHarness from "./pages/EvalHarness";
import Learning from "./pages/Learning";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Worklist />} />
        <Route path="/architecture" element={<Architecture />} />
        <Route path="/encounter/:id" element={<EncounterDetail />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/knowledge-graph" element={<KnowledgeGraph />} />
        <Route path="/eval" element={<EvalHarness />} />
        <Route path="/learning" element={<Learning />} />
      </Routes>
    </Layout>
  );
}
