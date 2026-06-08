import { useQuery } from "@tanstack/react-query";
import {
  FileCheck2, ScanText, Boxes, Quote, ShieldCheck, Gauge, ArrowRight, Database, Cloud, Layers,
} from "lucide-react";
import { api } from "../api";

const stages = [
  { n: "0", icon: FileCheck2, title: "Eligibility Gate", prevents: "Coding ineligible charts", desc: "Required docs, approved specialty/procedure, valid auth, exclusion flags (trauma, interventional, incomplete). Fails → manual queue with reason." },
  { n: "1", icon: ScanText, title: "Document Conditioning", prevents: "Reasoning on bad input", desc: "Section ID, copy-forward / contradiction / unsigned detection, chart summarization." },
  { n: "2", icon: Boxes, title: "Entity Extraction", prevents: "Lost specificity", desc: "Structured slots: laterality, contrast, view count, encounter type, negation, temporality." },
  { n: "3", icon: Quote, title: "Cited Code Generation", prevents: "Uncitable / fabricated codes", desc: "Graph-RAG grounded; every code must cite chart lines + a guideline or it is rejected. Self-consistency on hard charts." },
  { n: "4", icon: ShieldCheck, title: "Validation Gates", prevents: "Compliance failures", desc: "Deterministic: code existence, specificity, NCCI, MUE, modifiers, sex/age, payer medical necessity." },
  { n: "5", icon: Gauge, title: "Calibration & Routing", prevents: "Confident wrong answers", desc: "4-factor calibrated confidence → STB / QA / Manual, with bounded-autonomy hard rules." },
];

export default function Architecture() {
  const { data: meta } = useQuery({ queryKey: ["meta"], queryFn: api.meta });
  const { data: ref } = useQuery({ queryKey: ["refsum"], queryFn: api.referenceSummary });

  return (
    <div className="space-y-6 fadeup">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900">Pipeline &amp; Architecture</h1>
        <p className="text-sm text-slate-500">A bounded, agentic pipeline — each stage can veto or downgrade a coding decision.</p>
      </div>

      {/* Pipeline */}
      <div className="grid md:grid-cols-3 xl:grid-cols-6 gap-3">
        {stages.map((s, i) => (
          <div key={s.n} className="card p-4 relative">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-ace-600 text-white grid place-items-center text-xs font-bold">{s.n}</div>
              <s.icon size={18} className="text-ace-600" />
            </div>
            <div className="mt-2 font-semibold text-slate-800 text-sm">{s.title}</div>
            <div className="mt-0.5 text-[11px] font-medium text-rose-500">prevents: {s.prevents}</div>
            <p className="mt-1.5 text-xs text-slate-500">{s.desc}</p>
            {i < stages.length - 1 && (
              <ArrowRight size={16} className="hidden xl:block absolute -right-2.5 top-1/2 -translate-y-1/2 text-slate-300 z-10" />
            )}
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        {/* Reference data provenance */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-3"><Database size={16} className="text-ace-600" /><h2 className="font-bold text-slate-800">Reference data</h2></div>
          <ul className="space-y-2 text-sm">
            {meta && Object.entries(meta.provenance).map(([k, v]) => (
              <li key={k} className="flex justify-between gap-3">
                <span className="font-mono text-slate-700">{k}</span>
                <span className="text-xs text-slate-500 text-right">{v}</span>
              </li>
            ))}
          </ul>
          {ref && (
            <div className="mt-3 pt-3 border-t border-slate-100 text-xs text-slate-500 grid grid-cols-2 gap-1">
              <span>ICD-10-CM: {ref.code_systems?.ICD10CM ?? 0}</span>
              <span>CPT: {ref.code_systems?.CPT ?? 0}</span>
              <span>NCCI edits: {ref.ncci_edits}</span>
              <span>MUE limits: {ref.mue_limits}</span>
              <span>Payer policies: {ref.payer_policies}</span>
              <span>Guidelines: {ref.guidelines}</span>
            </div>
          )}
        </div>

        {/* Specialty accelerator */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-3"><Layers size={16} className="text-ace-600" /><h2 className="font-bold text-slate-800">Specialty accelerator</h2></div>
          <p className="text-sm text-slate-600">One pipeline, configured per specialty + per client. New specialties deploy with minimal customization; client-specific coding preferences and payer-KG rules "port in".</p>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {["Radiology ✓", "E&M ✓", "ED ✓", "Pathology ✓", "Surgical ✓", "Inpatient (next)"].map((s) => (
              <span key={s} className="pill bg-ace-50 text-ace-700 ring-1 ring-ace-100">{s}</span>
            ))}
          </div>
        </div>

        {/* Production mapping */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-3"><Cloud size={16} className="text-ace-600" /><h2 className="font-bold text-slate-800">Production mapping</h2></div>
          <ul className="space-y-2 text-sm text-slate-600">
            <li>• Demo: self-contained Docker, {meta?.llm_mode === "anthropic" ? "Claude frontier" : meta?.llm_mode}.</li>
            <li>• Prod: Azure + Azure AI Foundry, US-region, multi-tenant (no co-mingling).</li>
            <li>• Integrates into RevAmp Coding Studio; EHR via Practice Admin / eCW / Cerner (FHIR/HL7/EDI).</li>
            <li>• Feedback: batch 24–48h → SLM fine-tune/distill; ML-Ops flags invalid codes.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
