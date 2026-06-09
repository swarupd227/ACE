import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useState } from "react";
import clsx from "clsx";
import { MessageSquareWarning, Stethoscope, ArrowRight, CheckCircle2 } from "lucide-react";
import { api } from "../api";
import { useRole, can } from "../role";
import { Spinner } from "../lib";
import type { CdiQuery } from "../types";

function QueryCard({ q }: { q: CdiQuery }) {
  const qc = useQueryClient();
  const { role } = useRole();
  const mayRespond = can(role, "cdi_respond");
  const [picked, setPicked] = useState<string>("");
  const respond = useMutation({
    mutationFn: (resp: string) => api.cdiRespond(q.id, resp),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["cdiQueue"] });
      qc.invalidateQueries({ queryKey: ["encounters"] });
      qc.invalidateQueries({ queryKey: ["encounter", q.encounter_id] });
    },
  });

  const answered = q.status === "answered";
  return (
    <div className={clsx("card p-4", answered && "opacity-80")}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <MessageSquareWarning size={16} className={answered ? "text-emerald-600" : "text-amber-600"} />
          <span className="font-semibold text-slate-800">{q.target || "Documentation clarification"}</span>
          <span className={clsx("pill ring-1", answered ? "bg-emerald-50 text-emerald-700 ring-emerald-200" : "bg-amber-50 text-amber-700 ring-amber-200")}>
            {q.status}
          </span>
          <span className="pill bg-slate-100 text-slate-600 ring-1 ring-slate-200">{q.specialty}</span>
        </div>
        {q.patient_name && (
          <Link to={`/encounter/${q.encounter_id}`} className="text-xs text-ace-600 hover:underline whitespace-nowrap">
            {q.patient_name} <ArrowRight size={12} className="inline" />
          </Link>
        )}
      </div>

      <p className="mt-2 text-sm font-medium text-slate-800">{q.question}</p>
      {q.clinical_indicators && (
        <p className="mt-1 text-xs text-slate-500"><span className="font-semibold">Indicators:</span> {q.clinical_indicators}</p>
      )}
      {q.rationale && <p className="mt-1 text-xs text-slate-400 italic">{q.rationale}</p>}

      {!answered ? (
        <div className="mt-3 border-t border-slate-100 pt-3">
          <div className="text-[11px] uppercase tracking-wide text-slate-400 mb-1.5 flex items-center gap-1">
            <Stethoscope size={12} /> Physician response (non-leading options)
          </div>
          {!mayRespond && <div className="text-xs text-slate-400 mb-1">Open to CDI Specialist / physician.</div>}
          <div className={clsx("flex flex-wrap gap-2", !mayRespond && "opacity-40 pointer-events-none")}>
            {q.options.map((o) => (
              <button
                key={o}
                disabled={respond.isPending}
                onClick={() => { setPicked(o); respond.mutate(o); }}
                className={clsx(
                  "rounded-lg border px-3 py-1.5 text-sm transition-colors",
                  picked === o ? "border-ace-500 bg-ace-50 text-ace-700" : "border-slate-200 hover:bg-slate-50 text-slate-700"
                )}
              >
                {respond.isPending && picked === o ? <Spinner className="h-3.5 w-3.5 inline" /> : null} {o}
              </button>
            ))}
          </div>
          {q.potential_codes?.length > 0 && (
            <div className="mt-2 text-xs text-slate-400">Candidate codes: {q.potential_codes.join(", ")}</div>
          )}
        </div>
      ) : (
        <div className="mt-3 border-t border-slate-100 pt-3 flex items-center gap-2 text-sm">
          <CheckCircle2 size={16} className="text-emerald-600" />
          <span className="text-slate-600">Physician answered: <span className="font-semibold text-slate-800">{q.physician_response}</span></span>
          <span className="text-xs text-slate-400">→ encounter re-coded</span>
        </div>
      )}
    </div>
  );
}

export default function Cdi() {
  const { data, isLoading } = useQuery({ queryKey: ["cdiQueue"], queryFn: api.cdiQueue });
  const open = (data ?? []).filter((q) => q.status === "open");
  const answered = (data ?? []).filter((q) => q.status === "answered");

  return (
    <div className="space-y-5 fadeup">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900">CDI / Physician Queries</h1>
        <p className="text-sm text-slate-500">
          When documentation is insufficient for a more specific or higher-acuity code, ACE drafts a
          compliant, non-leading query. The physician's answer re-codes the encounter — a CDI co-pilot,
          not a coder replacement.
        </p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="card p-4"><div className="text-xs uppercase tracking-wide text-slate-400">Open queries</div><div className="text-2xl font-extrabold text-amber-600">{open.length}</div></div>
        <div className="card p-4"><div className="text-xs uppercase tracking-wide text-slate-400">Answered</div><div className="text-2xl font-extrabold text-emerald-600">{answered.length}</div></div>
        <div className="card p-4"><div className="text-xs uppercase tracking-wide text-slate-400">How to generate</div><div className="text-sm text-slate-600 mt-1">Open an encounter → <span className="font-semibold">Scan for CDI</span></div></div>
      </div>

      {isLoading ? (
        <div className="grid place-items-center h-40"><Spinner className="h-6 w-6 text-ace-500" /></div>
      ) : (data && data.length) ? (
        <div className="space-y-3">
          {open.map((q) => <QueryCard key={q.id} q={q} />)}
          {answered.map((q) => <QueryCard key={q.id} q={q} />)}
        </div>
      ) : (
        <div className="card p-8 text-center text-sm text-slate-400">
          No CDI queries yet. Open any encounter and click <b>Scan for CDI opportunities</b> to check its documentation for gaps.
        </div>
      )}
    </div>
  );
}
