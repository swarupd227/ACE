import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle, CheckCircle2, Send, Pencil, Quote, Link2, ShieldCheck, X,
} from "lucide-react";
import { api } from "../api";
import {
  CodeChips, ConfidenceBar, ProvisionBadge, ReconBadge, StatusBadge, ValidationBadge, Spinner,
} from "../lib";
import type { Recommendation } from "../types";

const VERDICTS = ["", "NET_NEW", "UPDATE", "DUPLICATE", "CONFLICT"];

export default function ReviewQueue() {
  const qc = useQueryClient();
  const [verdict, setVerdict] = useState("");
  const [attention, setAttention] = useState(false);
  const [err, setErr] = useState("");

  const { data: recs, isLoading } = useQuery({
    queryKey: ["recommendations", verdict, attention],
    queryFn: () => api.recommendations({ verdict: verdict || undefined, attention }),
  });
  const { data: ace } = useQuery({ queryKey: ["ace-status"], queryFn: api.aceStatus, refetchInterval: 20000 });

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["recommendations"] });
    qc.invalidateQueries({ queryKey: ["ace-status"] });
  };

  const counts = {
    total: recs?.length ?? 0,
    attention: recs?.filter((r) => r.needs_attention).length ?? 0,
    published: recs?.filter((r) => r.published_to_ace).length ?? 0,
  };

  return (
    <div className="fadeup space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Review Queue</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Each candidate rule is validated against its policy evidence and reconciled against the
            existing rule library. Approve, then publish to ACE.
          </p>
        </div>
        <AcePanel ace={ace} />
      </div>

      {err && (
        <div className="card p-3 border-rose-200 bg-rose-50 text-sm text-rose-700 flex items-center justify-between">
          <span>{err}</span>
          <button className="text-rose-500 hover:text-rose-700" onClick={() => setErr("")}>dismiss</button>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 text-sm">
          <span className="label">Verdict</span>
          <select className="rounded-lg border border-slate-200 px-2 py-1.5 text-sm"
            value={verdict} onChange={(e) => setVerdict(e.target.value)}>
            {VERDICTS.map((v) => <option key={v} value={v}>{v || "All"}</option>)}
          </select>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer">
          <input type="checkbox" checked={attention} onChange={(e) => setAttention(e.target.checked)} />
          Needs attention only
        </label>
        <div className="ml-auto flex items-center gap-2 text-xs text-slate-500">
          <span className="pill bg-slate-100 text-slate-600">{counts.total} total</span>
          {counts.attention > 0 && <span className="pill bg-rose-50 text-rose-700 ring-1 ring-rose-200">{counts.attention} attention</span>}
          {counts.published > 0 && <span className="pill bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200">{counts.published} published</span>}
        </div>
      </div>

      {isLoading ? (
        <div className="card p-8 grid place-items-center"><Spinner className="h-6 w-6 text-ace-500" /></div>
      ) : (recs ?? []).length === 0 ? (
        <div className="card p-8 text-center text-sm text-slate-400">
          No recommendations yet — generate them from a policy in the Workbench.
        </div>
      ) : (
        <div className="space-y-3">
          {recs!.map((r) => (
            <RecCard key={r.id} rec={r} onChange={invalidate} onError={setErr} aceReachable={!!ace?.reachable} />
          ))}
        </div>
      )}
    </div>
  );
}

function AcePanel({ ace }: { ace?: { reachable: boolean; ace_base_url: string; p2r_published_policies?: number } }) {
  return (
    <div className="card p-3 w-72 shrink-0">
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
        <Link2 size={14} className={ace?.reachable ? "text-emerald-500" : "text-slate-400"} />
        ACE integration
      </div>
      <div className="mt-1 text-xs text-slate-500">
        {ace?.reachable ? (
          <>
            <span className="text-emerald-600 font-semibold">Connected</span> ·{" "}
            {ace.p2r_published_policies ?? 0} P2R policies live in ACE
          </>
        ) : (
          <span className="text-slate-400">Not reachable</span>
        )}
      </div>
      <div className="mt-0.5 text-[10px] font-mono text-slate-400 truncate">{ace?.ace_base_url}</div>
    </div>
  );
}

function RecCard({ rec, onChange, onError, aceReachable }: {
  rec: Recommendation; onChange: () => void; onError: (m: string) => void; aceReachable: boolean;
}) {
  const [editing, setEditing] = useState(false);
  const [summary, setSummary] = useState(rec.candidate_summary);
  const [verdict, setVerdict] = useState(rec.reconciliation_verdict);

  const save = useMutation({
    mutationFn: () => api.editRecommendation(rec.id, { candidate_summary: summary, reconciliation_verdict: verdict }),
    onSuccess: () => { setEditing(false); onChange(); },
    onError: (e: any) => onError(e.message),
  });
  const approve = useMutation({
    mutationFn: () => api.approve(rec.id),
    onSuccess: onChange, onError: (e: any) => onError(e.message),
  });
  const publish = useMutation({
    mutationFn: () => api.publishToAce(rec.id),
    onSuccess: onChange, onError: (e: any) => onError(e.message),
  });

  return (
    <div className={`card p-4 space-y-3 ${rec.needs_attention ? "border-rose-200" : ""}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <ProvisionBadge type={rec.provision_type} />
          <ReconBadge verdict={rec.reconciliation_verdict} />
          <ValidationBadge verdict={rec.validation_verdict} />
          <StatusBadge status={rec.status} />
          {rec.needs_attention && (
            <span className="pill bg-rose-50 text-rose-700 ring-1 ring-rose-200">
              <AlertTriangle size={12} /> attention
            </span>
          )}
        </div>
        <div className="w-40 shrink-0"><ConfidenceBar value={rec.confidence} /></div>
      </div>

      {editing ? (
        <textarea className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
          value={summary} onChange={(e) => setSummary(e.target.value)} />
      ) : (
        <div className="text-sm text-slate-700">{rec.candidate_summary}</div>
      )}

      <CodeChips codes={rec.code_sets} />

      {/* Validation evidence */}
      {rec.validation_rationale && (
        <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-600 space-y-1">
          <div className="label">Validation</div>
          <div>{rec.validation_rationale}</div>
          {rec.evidence?.[0]?.quote && (
            <div className="flex items-start gap-1.5 text-slate-500 italic mt-1">
              <Quote size={12} className="mt-0.5 shrink-0 text-ace-400" /> “{rec.evidence[0].quote}”
            </div>
          )}
        </div>
      )}

      {/* Reconciliation */}
      {rec.reconciliation_rationale && (
        <div className="rounded-lg bg-ace-50/60 p-3 text-xs text-slate-600 space-y-1">
          <div className="flex items-center gap-2">
            <span className="label">Reconciliation</span>
            {rec.matched_rule_id && (
              <span className="pill bg-white ring-1 ring-slate-200 font-mono text-slate-600">
                {rec.matched_rule_id} · overlap {Math.round(rec.code_overlap * 100)}%
              </span>
            )}
            {editing && (
              <select className="rounded border border-slate-200 px-1.5 py-0.5 text-xs ml-auto"
                value={verdict} onChange={(e) => setVerdict(e.target.value as any)}>
                {["NET_NEW", "UPDATE", "DUPLICATE", "CONFLICT"].map((v) => <option key={v} value={v}>{v}</option>)}
              </select>
            )}
          </div>
          <div>{rec.reconciliation_rationale}</div>
        </div>
      )}

      {/* Published receipt */}
      {rec.published_to_ace && rec.ace_publish?.policies && (
        <div className="rounded-lg bg-emerald-50 ring-1 ring-emerald-200 p-3 text-xs text-emerald-800">
          <div className="flex items-center gap-1.5 font-semibold">
            <ShieldCheck size={13} /> Published to ACE as {rec.ace_publish.source}
          </div>
          <div className="mt-1 font-mono">
            {rec.ace_publish.policies.map((p) => `${p.payer} ${p.code} (ACE #${p.ace_id})`).join(" · ")}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-end gap-2 pt-1 border-t border-slate-100">
        {editing ? (
          <>
            <button className="btn-ghost" onClick={() => { setEditing(false); setSummary(rec.candidate_summary); setVerdict(rec.reconciliation_verdict); }}>
              <X size={15} /> Cancel
            </button>
            <button className="btn-primary" disabled={save.isPending} onClick={() => save.mutate()}>
              {save.isPending ? <Spinner className="h-4 w-4" /> : <CheckCircle2 size={15} />} Save
            </button>
          </>
        ) : (
          <>
            {rec.status !== "PUBLISHED" && (
              <button className="btn-ghost" onClick={() => setEditing(true)}>
                <Pencil size={15} /> Edit
              </button>
            )}
            {rec.status === "PENDING_REVIEW" && (
              <button className="btn-primary" disabled={approve.isPending} onClick={() => approve.mutate()}>
                {approve.isPending ? <Spinner className="h-4 w-4" /> : <CheckCircle2 size={15} />} Approve
              </button>
            )}
            {rec.status === "APPROVED" && (
              <button className="btn-brand" disabled={publish.isPending || !aceReachable}
                title={aceReachable ? "Write this rule into ACE via its public policy API" : "ACE not reachable"}
                onClick={() => publish.mutate()}>
                {publish.isPending ? <Spinner className="h-4 w-4" /> : <Send size={15} />} Publish to ACE
              </button>
            )}
            {rec.status === "PUBLISHED" && (
              <span className="pill bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200">
                <ShieldCheck size={12} /> Published
              </span>
            )}
          </>
        )}
      </div>
    </div>
  );
}
