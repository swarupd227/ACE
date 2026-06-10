import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plug, CheckCircle2, FileInput, ArrowRight, Cable, Code2, ScanLine } from "lucide-react";
import { api } from "../api";
import { Spinner } from "../lib";

const MODALITY_OPTIONS: Record<string, string[]> = {
  "Radiology":    ["CT", "X-Ray", "MRI", "Ultrasound", "Doppler"],
  "E&M":          ["New Patient", "Established Patient", "Consultation"],
  "ED":           ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"],
  "Pathology":    ["Surgical", "Cytology", "Autopsy"],
  "Surgical":     ["General", "Orthopedic", "Cardiovascular", "Laparoscopic"],
  "Cardiology":   ["ECG", "Echocardiogram", "Stress Test", "Catheterization"],
  "Orthopedics":  ["Joint Replacement", "Fracture", "Arthroscopy"],
};
const DEFAULT_MODALITIES = ["N/A"];

function modalitiesFor(specialty: string): string[] {
  return MODALITY_OPTIONS[specialty] ?? DEFAULT_MODALITIES;
}

const SAMPLE = `RADIOLOGY REPORT
PATIENT: Maria Delgado · MRN: 88412-7 · DOB: 03/14/1964 · Phone: (555) 201-8842
EXAM: CT chest with contrast
HISTORY: 61-year-old with persistent cough and abnormal chest X-ray.
TECHNIQUE: Helical CT of the thorax following IV contrast.
FINDINGS: 1.2 cm spiculated nodule in the right upper lobe. No effusion.
IMPRESSION: Right upper lobe pulmonary nodule, suspicious — recommend follow-up.
Electronically signed by Dr. A. Reyes, MD.`;

export default function Integrations() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["integrations"], queryFn: api.integrations });
  const { data: meta } = useQuery({ queryKey: ["meta"], queryFn: api.meta });
  const specs = meta?.specialties?.length ? meta.specialties : ["Radiology", "E&M", "ED", "Pathology", "Surgical"];
  const [form, setForm] = useState({ specialty: "Radiology", modality: "CT", payer: "Medicare", source_system: "eClinicalWorks", report_text: "" });
  const [last, setLast] = useState<any>(null);

  const ingest = useMutation({
    mutationFn: () => api.ingest({ ...form, pos: "22" }),
    onSuccess: (r) => {
      setLast(r);
      qc.invalidateQueries({ queryKey: ["encounters"] });
      qc.invalidateQueries({ queryKey: ["integrations"] });
      qc.invalidateQueries({ queryKey: ["controlTower"] });
    },
  });
  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  if (isLoading || !data) return <div className="grid place-items-center h-64"><Spinner className="h-6 w-6 text-ace-500" /></div>;

  return (
    <div className="space-y-5 fadeup">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900">Integrations &amp; Ingestion</h1>
        <p className="text-sm text-slate-500">Source-system connectivity and live chart ingestion into the coding queue. (Demo simulates connectors; the ingest below is live.)</p>
      </div>

      {/* Connectors */}
      <div className="grid md:grid-cols-3 gap-4">
        {data.connectors.map((c) => (
          <div key={c.name} className="card p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2"><Plug size={16} className="text-ace-600" /><span className="font-semibold text-slate-800">{c.name}</span></div>
              <span className="pill bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200"><CheckCircle2 size={11} /> {c.status}</span>
            </div>
            <div className="mt-1 text-xs text-slate-500">{c.type} · {c.channel}</div>
            <div className="mt-2 text-sm text-slate-600">{c.charts_ingested} charts ingested</div>
          </div>
        ))}
      </div>

      {/* Channels + API */}
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="card p-4 lg:col-span-1">
          <div className="flex items-center gap-2 mb-2"><Cable size={16} className="text-ace-600" /><h2 className="font-bold text-slate-800">Inbound channels</h2></div>
          <ul className="space-y-1.5 text-sm text-slate-600">{data.channels.map((ch) => <li key={ch}>• {ch}</li>)}</ul>
          <div className="mt-3 pt-3 border-t border-slate-100 text-xs text-slate-500 flex items-center gap-2">
            <Code2 size={14} /> Live REST API with an OpenAPI spec ({data.api_docs ?? "/docs"} on the API service). Batch = "Run autonomous coding" on the worklist.
          </div>
        </div>

        {/* Live ingest */}
        <div className="card p-4 lg:col-span-2">
          <div className="flex items-center gap-2 mb-3"><FileInput size={16} className="text-ace-600" /><h2 className="font-bold text-slate-800">Ingest a report (live)</h2></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">Specialty <span className="text-rose-400">*</span></span>
              <select
                className="rounded border border-slate-200 px-2 py-1.5 text-sm"
                value={form.specialty}
                onChange={(e) => {
                  const spec = e.target.value;
                  setForm((f) => ({ ...f, specialty: spec, modality: modalitiesFor(spec)[0] }));
                }}
              >
                {specs.map((s) => <option key={s}>{s}</option>)}
              </select>
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">Modality</span>
              <select
                className="rounded border border-slate-200 px-2 py-1.5 text-sm"
                value={form.modality}
                onChange={(e) => set("modality", e.target.value)}
              >
                {modalitiesFor(form.specialty).map((m) => <option key={m}>{m}</option>)}
              </select>
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">Payer <span className="text-rose-400">*</span></span>
              <input className="rounded border border-slate-200 px-2 py-1.5 text-sm" placeholder="Medicare" value={form.payer} onChange={(e) => set("payer", e.target.value)} />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">Source System</span>
              <select className="rounded border border-slate-200 px-2 py-1.5 text-sm" value={form.source_system} onChange={(e) => set("source_system", e.target.value)}>
                {data.connectors.map((c) => <option key={c.name}>{c.name}</option>)}
              </select>
            </label>
          </div>
          <textarea className="w-full rounded border border-slate-200 px-2 py-1.5 text-sm font-mono" rows={6} placeholder="Paste a clinical report — or upload your own chart file below…" value={form.report_text} onChange={(e) => set("report_text", e.target.value)} />
          <div className="mt-2 flex items-center gap-2 flex-wrap">
            <button className="btn-ghost py-1.5" onClick={() => set("report_text", SAMPLE)}>Load sample</button>
            <label className="btn-ghost py-1.5 cursor-pointer">
              <FileInput size={14} /> Upload chart file (.txt)
              <input
                type="file" accept=".txt,.text,.md,text/plain" className="hidden"
                onChange={async (e) => {
                  const f = e.target.files?.[0];
                  if (f) set("report_text", (await f.text()).trim());
                  e.target.value = "";
                }}
              />
            </label>
            <button
              className="btn-primary py-1.5"
              disabled={form.report_text.trim().length < 20 || ingest.isPending}
              title={form.report_text.trim().length < 20 ? "Paste or upload at least 20 characters of report text" : ""}
              onClick={() => ingest.mutate()}
            >
              {ingest.isPending ? <Spinner className="h-4 w-4" /> : <FileInput size={14} />} Ingest into queue
            </button>
            {form.report_text.trim().length > 0 && form.report_text.trim().length < 20 && (
              <span className="text-xs text-amber-600">needs ≥ 20 characters of report text</span>
            )}
            {last && (
              <span className="text-sm text-emerald-700 flex items-center gap-1">
                <CheckCircle2 size={15} /> Ingested {last.mrn} —
                <Link to="/" className="text-ace-600 hover:underline">open worklist <ArrowRight size={12} className="inline" /></Link>
              </span>
            )}
          </div>
          {ingest.isError && <div className="mt-2 text-xs text-rose-600">{(ingest.error as Error).message}</div>}
          <p className="mt-2 text-[11px] text-slate-400">Ingestion creates a real encounter in the queue; run coding on it from the worklist or Control Tower.</p>
        </div>
      </div>

      <ScannedDocCard specs={specs} />
    </div>
  );
}

function ScannedDocCard({ specs }: { specs: string[] }) {
  const qc = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [specialty, setSpecialty] = useState("Radiology");
  const [modality, setModality] = useState("XR");
  const [result, setResult] = useState<any>(null);

  const upload = useMutation({
    mutationFn: () => api.ingestDocument(file!, { specialty, modality, payer: "Medicare", pos: "22" }),
    onSuccess: (r) => {
      setResult(r);
      qc.invalidateQueries({ queryKey: ["encounters"] });
      qc.invalidateQueries({ queryKey: ["integrations"] });
      qc.invalidateQueries({ queryKey: ["controlTower"] });
    },
  });

  return (
    <div className="card p-4">
      <div className="flex items-center gap-2 mb-1">
        <ScanLine size={16} className="text-ace-600" />
        <h2 className="font-bold text-slate-800">Ingest a scanned document (PDF / image — live vision OCR)</h2>
      </div>
      <p className="text-xs text-slate-500 mb-3">
        Real charts arrive as document packets — scans, faxes, PDFs. The reasoning model transcribes the
        document verbatim (the Document Ingestion &amp; Conditioning front-end); the text then enters the
        same Stage 0–5 pipeline. Unreadable content is marked [illegible], never invented.
      </p>
      <div className="flex flex-wrap items-center gap-2">
        <input
          type="file" accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/png,image/jpeg,image/webp"
          onChange={(e) => { setFile(e.target.files?.[0] ?? null); setResult(null); }}
          className="text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-ace-50 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-ace-700 hover:file:bg-ace-100"
        />
        <select className="rounded border border-slate-200 px-2 py-1.5 text-sm" value={specialty} onChange={(e) => setSpecialty(e.target.value)}>
          {specs.map((s) => <option key={s}>{s}</option>)}
        </select>
        <input className="w-28 rounded border border-slate-200 px-2 py-1.5 text-sm" placeholder="Modality" value={modality} onChange={(e) => setModality(e.target.value)} />
        <button className="btn-primary py-1.5" disabled={!file || upload.isPending} onClick={() => upload.mutate()}>
          {upload.isPending ? <Spinner className="h-4 w-4" /> : <ScanLine size={14} />}
          {upload.isPending ? "Extracting…" : "Extract & ingest"}
        </button>
      </div>
      {upload.isError && <div className="mt-2 text-xs text-rose-600">{(upload.error as Error).message}</div>}
      {result && (
        <div className="mt-3 rounded-lg border border-emerald-200 bg-emerald-50/40 p-3">
          <div className="text-sm text-emerald-700 flex items-center gap-1 flex-wrap">
            <CheckCircle2 size={15} /> Extracted {result.extracted_chars} chars from {result.filename} → ingested as{" "}
            <Link to={`/encounter/${result.id}`} className="font-semibold text-ace-600 hover:underline">{result.mrn}</Link>
            <span className="text-xs text-emerald-600">({result.tokens.in + result.tokens.out} tokens)</span>
          </div>
          <pre className="mt-2 text-[11px] leading-relaxed text-slate-600 font-mono whitespace-pre-wrap max-h-36 overflow-y-auto">{result.extracted_preview}…</pre>
          <div className="mt-1 text-xs text-slate-500">Open the encounter and run coding — the extracted text flows through the normal pipeline.</div>
        </div>
      )}
    </div>
  );
}
