import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Workbench from "./pages/Workbench";
import ReviewQueue from "./pages/ReviewQueue";
import RuleLibrary from "./pages/RuleLibrary";
import EvalHarness from "./pages/EvalHarness";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Workbench />} />
        <Route path="/review" element={<ReviewQueue />} />
        <Route path="/library" element={<RuleLibrary />} />
        <Route path="/eval" element={<EvalHarness />} />
      </Routes>
    </Layout>
  );
}
