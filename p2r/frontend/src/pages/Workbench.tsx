import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileText, Sparkles, Upload, ChevronRight, Quote } from "lucide-react";
import { api } from "../api";
import {
  CodeChips, ConfidenceBar, ProvisionBadge, RoutingBadge, Spinner,
} from "../lib";
import type { DocumentRow } from "../types";

export default function Workbench() {
  const qc = useQueryClient();
  const nav = useNavigate();
  const [selected, setSelected] = useState<string | null>(null);
  const [showPaste, setShowPaste] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [payer, setPayer] = useState("");
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [err, setErr] = useState("");

  const { data: docs } = useQuery({ queryKey: ["documents"], queryFn: api.documents });

  const refreshDocs = (newDocId?: string) => {
    qc.invalidateQueries({ queryKey: ["documents"] });
    qc.invalidateQueries({ queryKey: ["ace-status"] });
    if (newDocId) setSelected(newDocId);
  };

  const ingestSample = useMutation({
    mutationFn: api.ingestSample,
    onSuccess: (r) => refreshDocs(r.document_id),
    onError: (e: any) => setErr(e.message),
  });

  const ingestPaste = useMutation({
    mutationFn: () => api.ingestPolicy(payer, title, text),
    onSuccess: (r) => { refreshDocs(r.document_id); setShowPaste(false); setText(""); setTitle(""); setPayer(""); },
    onError: (e: any) => setErr(e.message),
  });

  const ingestDoc = useMutation({
    mutationFn: (file: File) => api.ingestDocument(file, payer, title || file.name),
    onSuccess: (r) => { refreshDocs(r.document_id); setShowUpload(false); setTitle(""); setPayer(""); },
    onError: (e: any) => setErr(e.message),
  });

  const generate = useMutation({
    mutationFn: (docId: string) => api.generate(docId),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["recommendations"] }); nav("/review"); },
    onError: (e: any) => setErr(e.message),
  });

  return (
    <div className="fadeup space-y-5">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Policy Workbench</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Ingest a payer policy → the model extracts cited, confidence-gated provisions → generate
          candidate rules for review. Use the synthetic sample, paste any policy, or upload a public
          policy document (e.g. a CMS LCD). PHI-free policy documents only.
        </p>
      </div>

      {err && (
        <div className="card p-3 border-rose-200 bg-rose-50 text-sm text-rose-700 flex items-center justify-between">
          <span>{err}</span>
          <button className="text-rose-500 hover:text-rose-700" onClick={() => setErr("")}>dismiss</button>
        </div>
      )}

      {/* Ingest actions */}
      <div className="flex flex-wrap items-center gap-3">
        <button
          className="btn-brand"
          disabled={ingestSample.isPending}
          onClick={() => { setErr(""); ingestSample.mutate(); }}
        >
          {ingestSample.isPending ? <Spinner className="h-4 w-4" /> : <Sparkles size={16} />}
          Ingest sample policy
        </button>
        <button className="btn-ghost" onClick={() => { setErr(""); setShowPaste((s) => !s); }}>
          <FileText size={16} /> Paste a policy
        </button>
        <button className="btn-ghost" onClick={() => { setErr(""); setShowUpload((s) => !s); }}>
          <Upload size={16} /> Upload PDF / image
        </button>
      </div>

      {showUpload && (
        <div className="card p-4 space-y-3 fadeup">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="label mb-1">Payer</div>
              <input className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                value={payer} onChange={(e) => setPayer(e.target.value)} placeholder="e.g. Medicare (CMS LCD L34220)" />
            </div>
            <div>
              <div className="label mb-1">Title (optional)</div>
              <input className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                value={title} onChange={(e) => setTitle(e.target.value)} placeholder="defaults to the file name" />
            </div>
          </div>
          <div>
            <div className="label mb-1">Policy document (PDF, PNG, JPEG, WebP — scanned OK)</div>
            <input type="file" accept="application/pdf,image/png,image/jpeg,image/webp"
              disabled={ingestDoc.isPending}
              onChange={(e) => { const f = e.target.files?.[0]; if (f) { setErr(""); ingestDoc.mutate(f); } }}
              className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-ace-600 file:px-3 file:py-2 file:text-white file:font-semibold hover:file:bg-ace-700" />
          </div>
          {ingestDoc.isPending && (
            <div className="flex items-center gap-2 text-sm text-slate-500"><Spinner className="h-4 w-4" /> Extracting via OCR + model…</div>
          )}
          <div className="text-[11px] text-slate-400">Document is OCR'd by the shared vision model, then run through the same cited-extraction pipeline. 12 MB max.</div>
        </div>
      )}

      {showPaste && (
        <div className="card p-4 space-y-3 fadeup">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="label mb-1">Payer</div>
              <input className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                value={payer} onChange={(e) => setPayer(e.target.value)} placeholder="e.g. Meridian Health Plan" />
            </div>
            <div>
              <div className="label mb-1">Title</div>
              <input className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Advanced Imaging Policy" />
            </div>
          </div>
          <div>
            <div className="label mb-1">Policy text</div>
            <textarea className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-mono h-40"
              value={text} onChange={(e) => setText(e.target.value)}
              placeholder="Paste the full payer policy text here…" />
          </div>
          <div className="flex justify-end gap-2">
            <button className="btn-ghost" onClick={() => setShowPaste(false)}>Cancel</button>
            <button className="btn-primary" disabled={ingestPaste.isPending || text.trim().length < 40}
              onClick={() => { setErr(""); ingestPaste.mutate(); }}>
              {ingestPaste.isPending ? <Spinner className="h-4 w-4" /> : <FileText size={16} />}
              Extract provisions
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-12 gap-5">
        {/* Documents list */}
        <div className="col-span-4 space-y-2">
          <div className="label">Ingested policies ({docs?.length ?? 0})</div>
          {(docs ?? []).map((d) => (
            <DocCard key={d.id} doc={d} active={selected === d.id} onClick={() => setSelected(d.id)} />
          ))}
          {docs && docs.length === 0 && (
            <div className="card p-4 text-sm text-slate-500">
              No policies yet — ingest the sample to begin.
            </div>
          )}
        </div>

        {/* Provisions for the selected doc */}
        <div className="col-span-8">
          {selected ? (
            <ProvisionPanel docId={selected} onGenerate={() => { setErr(""); generate.mutate(selected); }}
              generating={generate.isPending} />
          ) : (
            <div className="card p-8 text-center text-sm text-slate-400">
              Select a policy to see its extracted provisions.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DocCard({ doc, active, onClick }: { doc: DocumentRow; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick}
      className={`card w-full text-left p-3 transition-colors ${active ? "ring-2 ring-ace-400" : "hover:bg-slate-50"}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-slate-800 truncate">{doc.title || "(untitled policy)"}</div>
          <div className="text-xs text-slate-500 truncate">{doc.payer || "—"}</div>
        </div>
        <span className="pill bg-ace-50 text-ace-700 ring-1 ring-ace-100 shrink-0">{doc.provision_count} prov</span>
      </div>
      <div className="mt-1 text-[11px] text-slate-400">{doc.doc_kind || "policy"} · {doc.source_type}</div>
    </button>
  );
}

function ProvisionPanel({ docId, onGenerate, generating }: { docId: string; onGenerate: () => void; generating: boolean }) {
  const { data, isLoading } = useQuery({
    queryKey: ["provisions", docId],
    queryFn: () => api.documentProvisions(docId),
  });

  if (isLoading) return <div className="card p-8 grid place-items-center"><Spinner className="h-6 w-6 text-ace-500" /></div>;
  if (!data) return null;

  return (
    <div className="space-y-3">
      <div className="card p-4 flex items-center justify-between">
        <div className="min-w-0">
          <div className="font-semibold text-slate-800 truncate">{data.document.title}</div>
          <div className="text-xs text-slate-500">{data.document.payer} · {data.document.doc_kind}</div>
        </div>
        <button className="btn-primary shrink-0" onClick={onGenerate} disabled={generating}>
          {generating ? <Spinner className="h-4 w-4" /> : <ChevronRight size={16} />}
          Generate rule recommendations
        </button>
      </div>

      {data.provisions.map((p) => (
        <div key={p.id} className="card p-4 space-y-2.5">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2 flex-wrap">
              <ProvisionBadge type={p.provision_type} />
              <RoutingBadge routing={p.routing} />
            </div>
            <div className="w-40"><ConfidenceBar value={p.confidence} /></div>
          </div>
          <div className="text-sm text-slate-700">{p.summary}</div>
          <CodeChips codes={p.code_sets} />
          {p.citation_spans?.length > 0 && (
            <div className="space-y-1 pt-1 border-t border-slate-100">
              {p.citation_spans.map((c, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-slate-500">
                  <Quote size={12} className="mt-0.5 shrink-0 text-ace-400" />
                  <span>
                    <span className="font-mono text-slate-400">L{c.line_start}-{c.line_end}</span>{" "}
                    <span className="italic">“{c.text}”</span>
                    {c.verified === false && <span className="ml-1 text-rose-500">(unverified)</span>}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
