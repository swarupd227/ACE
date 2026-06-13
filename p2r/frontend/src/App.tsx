import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Workbench from "./pages/Workbench";
import ReviewQueue from "./pages/ReviewQueue";
import RuleLibrary from "./pages/RuleLibrary";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Workbench />} />
        <Route path="/review" element={<ReviewQueue />} />
        <Route path="/library" element={<RuleLibrary />} />
      </Routes>
    </Layout>
  );
}
