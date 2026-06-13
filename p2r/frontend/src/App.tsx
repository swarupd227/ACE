import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Workbench from "./pages/Workbench";
import Sources from "./pages/Sources";
import DenialDiscovery from "./pages/DenialDiscovery";
import ReviewQueue from "./pages/ReviewQueue";
import RuleLibrary from "./pages/RuleLibrary";
import EvalHarness from "./pages/EvalHarness";
import DecisionLog from "./pages/DecisionLog";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Workbench />} />
        <Route path="/sources" element={<Sources />} />
        <Route path="/denials" element={<DenialDiscovery />} />
        <Route path="/review" element={<ReviewQueue />} />
        <Route path="/library" element={<RuleLibrary />} />
        <Route path="/eval" element={<EvalHarness />} />
        <Route path="/audit" element={<DecisionLog />} />
      </Routes>
    </Layout>
  );
}
