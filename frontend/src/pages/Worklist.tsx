import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useState, useEffect, useMemo } from "react";
import clsx from "clsx";
import {
  Play, ArrowRight, Clock, Zap, Flag,
  Search, X, SlidersHorizontal,
  ChevronUp, ChevronDown, ChevronsUpDown,
} from "lucide-react";
import { api } from "../api";
import { useRole, can } from "../role";
import AgentConsole, { CODING_STEPS } from "../components/AgentConsole";
import { ConfidenceBar, LaneBadge, Spinner, laneColor } from "../lib";
import type { EncounterRow, Lane } from "../types";

const SPECIALTIES = [
  "Radiology", "E&M", "ED", "Pathology", "Surgical", "Cardiology",
  "Orthopedics", "OB/GYN", "GI/Endoscopy", "Dermatology", "Urology",
  "Anesthesia", "Ophthalmology", "ENT",
];

type SortField =
  | "patient_name" | "mrn" | "specialty" | "payer"
  | "dos" | "overall_confidence" | "routing_lane" | "received_at"
  | null;
type SortDir = "asc" | "desc";
type TabLane = "ALL" | "STB" | "QA" | "MANUAL";

interface Filters {
  specialties: string[];
  lanes: ("STB" | "QA" | "MANUAL")[];
  payers: string[];
  dosFrom: string;
  dosTo: string;
  confMin: number;
  confMax: number;
}

const DEFAULT_FILTERS: Filters = {
  specialties: [],
  lanes: [],
  payers: [],
  dosFrom: "",
  dosTo: "",
  confMin: 0,
  confMax: 100,
};

function formatReceivedAt(iso: string): { date: string; time: string } {
  const d = new Date(iso);
  return {
    date: d.toLocaleString("en-US", { month: "short", day: "numeric" }),
    time: d.toLocaleString("en-US", { hour: "numeric", minute: "2-digit", hour12: true }),
  };
}

function formatDos(dos: string): { monthDay: string; year: string } {
  // dos is "YYYY-MM-DD" — parse without timezone shift
  const [y, m, d] = dos.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  return {
    monthDay: date.toLocaleString("en-US", { month: "short", day: "numeric" }),
    year: String(y),
  };
}

function SortIcon({ field, sortField, sortDir }: { field: string; sortField: SortField; sortDir: SortDir }) {
  if (sortField !== field) return <ChevronsUpDown size={12} className="text-slate-300 shrink-0" />;
  return sortDir === "asc"
    ? <ChevronUp size={12} className="text-ace-600 shrink-0" />
    : <ChevronDown size={12} className="text-ace-600 shrink-0" />;
}

function SortTh({
  field, label, sortField, sortDir, onSort, className,
}: {
  field: SortField; label: string; sortField: SortField; sortDir: SortDir;
  onSort: (f: SortField) => void; className?: string;
}) {
  return (
    <th
      className={clsx("px-4 py-3 font-semibold cursor-pointer select-none hover:text-slate-600 whitespace-nowrap", className)}
      onClick={() => onSort(field)}
    >
      <span className="inline-flex items-center gap-1">
        {label}
        <SortIcon field={field as string} sortField={sortField} sortDir={sortDir} />
      </span>
    </th>
  );
}

function LaneCard({ lane, count, total }: { lane: Lane; count: number; total: number }) {
  const c = laneColor(lane);
  const sub =
    lane === "STB" ? "Auto-billed, no human touch"
    : lane === "QA" ? "Auditor verifies"
    : "Full human coding";
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between">
        <LaneBadge lane={lane} />
        <span className="text-2xl font-extrabold tabular-nums">{count}</span>
      </div>
      <div className="mt-2 text-xs text-slate-500">{sub}</div>
      <div className="mt-3 h-1.5 rounded-full bg-slate-100 overflow-hidden">
        <div className={clsx("h-full", c.solid)} style={{ width: total ? `${(count / total) * 100}%` : "0%" }} />
      </div>
    </div>
  );
}

export default function Worklist() {
  const qc = useQueryClient();
  const { data: rows, isLoading } = useQuery({ queryKey: ["encounters"], queryFn: api.encounters });
  const { data: meta } = useQuery({ queryKey: ["meta"], queryFn: api.meta });
  const [consoleEnc, setConsoleEnc] = useState<{ id: string; name: string } | null>(null);
  const [showBatch, setShowBatch] = useState(false);
  const { role } = useRole();
  const mayCode = can(role, "code");

  const [activeTab, setActiveTab] = useState<TabLane>("ALL");

  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  useEffect(() => {
    const t = setTimeout(() => setSearch(searchInput), 300);
    return () => clearTimeout(t);
  }, [searchInput]);

  const [sortField, setSortField] = useState<SortField>("received_at");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  const [filterOpen, setFilterOpen] = useState(false);
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);

  const list = rows ?? [];
  const coded = list.filter((r) => r.routing_lane);
  const counts = {
    STB: coded.filter((r) => r.routing_lane === "STB").length,
    QA: coded.filter((r) => r.routing_lane === "QA").length,
    MANUAL: coded.filter((r) => r.routing_lane === "MANUAL").length,
  };
  const stbRate = coded.length ? Math.round((counts.STB / coded.length) * 100) : 0;

  const tabCounts: Record<TabLane, number> = {
    ALL: list.length,
    STB: counts.STB,
    QA: counts.QA,
    MANUAL: counts.MANUAL,
  };

  const specs = meta?.specialties ?? [];
  const specProse =
    specs.length === 0 ? "Multi-specialty"
    : specs.length === 1 ? specs[0]
    : specs.slice(0, -1).join(", ") + " & " + specs[specs.length - 1];

  const allPayers = useMemo(() => {
    const set = new Set<string>();
    list.forEach((r) => r.payer && set.add(r.payer));
    return Array.from(set).sort();
  }, [list]);

  const activeFilterCount = useMemo(() => {
    let n = 0;
    if (filters.specialties.length) n++;
    if (filters.lanes.length) n++;
    if (filters.payers.length) n++;
    if (filters.dosFrom || filters.dosTo) n++;
    if (filters.confMin > 0 || filters.confMax < 100) n++;
    return n;
  }, [filters]);

  function handleSort(field: SortField) {
    if (sortField === field) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDir(field === "received_at" ? "desc" : "asc");
    }
  }

  const visibleList = useMemo(() => {
    let result = list;

    if (activeTab !== "ALL") {
      result = result.filter((r) => r.routing_lane === activeTab);
    }

    if (search.trim()) {
      const q = search.trim().toLowerCase();
      result = result.filter(
        (r) => r.patient_name.toLowerCase().includes(q) || r.mrn.toLowerCase().includes(q),
      );
    }

    if (filters.specialties.length) {
      result = result.filter((r) => filters.specialties.includes(r.specialty));
    }

    if (filters.lanes.length) {
      result = result.filter((r) =>
        r.routing_lane ? filters.lanes.includes(r.routing_lane as "STB" | "QA" | "MANUAL") : true,
      );
    }

    if (filters.payers.length) {
      result = result.filter((r) => filters.payers.includes(r.payer));
    }

    if (filters.dosFrom) result = result.filter((r) => r.dos >= filters.dosFrom);
    if (filters.dosTo)   result = result.filter((r) => r.dos <= filters.dosTo);

    if (filters.confMin > 0 || filters.confMax < 100) {
      result = result.filter((r) => {
        if (!r.routing_lane) return true;
        const pct = Math.round((r.overall_confidence ?? 0) * 100);
        return pct >= filters.confMin && pct <= filters.confMax;
      });
    }

    if (sortField) {
      const sf = sortField;
      result = [...result].sort((a, b) => {
        const av: unknown = sf === "received_at"
          ? (a.received_at ?? "")
          : (a as unknown as Record<string, unknown>)[sf] ?? "";
        const bv: unknown = sf === "received_at"
          ? (b.received_at ?? "")
          : (b as unknown as Record<string, unknown>)[sf] ?? "";
        if (typeof av === "number" && typeof bv === "number") {
          return sortDir === "asc" ? av - bv : bv - av;
        }
        const cmp = String(av).localeCompare(String(bv));
        return sortDir === "asc" ? cmp : -cmp;
      });
    }

    return result;
  }, [list, activeTab, search, filters, sortField, sortDir]);

  function clearFilters() {
    setFilters(DEFAULT_FILTERS);
  }

  function clearAll() {
    clearFilters();
    setSearchInput("");
    setSearch("");
  }

  const toggleSpecialty = (s: string) =>
    setFilters((f) => ({
      ...f,
      specialties: f.specialties.includes(s)
        ? f.specialties.filter((x) => x !== s)
        : [...f.specialties, s],
    }));

  const toggleLane = (l: "STB" | "QA" | "MANUAL") =>
    setFilters((f) => ({
      ...f,
      lanes: f.lanes.includes(l)
        ? f.lanes.filter((x) => x !== l)
        : [...f.lanes, l],
    }));

  const togglePayer = (p: string) =>
    setFilters((f) => ({
      ...f,
      payers: f.payers.includes(p)
        ? f.payers.filter((x) => x !== p)
        : [...f.payers, p],
    }));

  return (
    <div className="space-y-5 fadeup">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Coder Worklist</h1>
          <p className="text-sm text-slate-500">
            {specProse} encounters · confidence-routed into Straight-Through Billing, QA, or Manual
          </p>
        </div>
        {mayCode ? (
          <button
            className="btn-brand"
            disabled={!meta?.llm_available}
            onClick={() => setShowBatch(true)}
            title={!meta?.llm_available ? "Configure a reasoning model in Admin → Reasoning Model to enable coding" : ""}
          >
            <Play size={16} /> Run autonomous coding
          </button>
        ) : (
          <span className="pill bg-slate-100 text-slate-500 ring-1 ring-slate-200">view-only ({role})</span>
        )}
      </div>

      {/* Lane summary */}
      <div className="grid grid-cols-4 gap-4">
        <div className="card p-4 bg-ace-900 text-white">
          <div className="flex items-center gap-2 text-xs text-slate-300">
            <Zap size={14} className="text-brand-300" /> STB RATE
          </div>
          <div className="mt-1 text-3xl font-extrabold tabular-nums">{stbRate}%</div>
          <div className="mt-2 text-xs text-slate-400">{coded.length} of {list.length} charts coded</div>
        </div>
        <LaneCard lane="STB" count={counts.STB} total={coded.length} />
        <LaneCard lane="QA"  count={counts.QA}  total={coded.length} />
        <LaneCard lane="MANUAL" count={counts.MANUAL} total={coded.length} />
      </div>

      {/* Table card */}
      <div className="card overflow-hidden">

        {/* ── Lane tabs (top of card) ── */}
        <div className="flex border-b border-slate-100">
          {(["ALL", "STB", "QA", "MANUAL"] as TabLane[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={clsx(
                "px-5 py-2.5 text-sm font-medium border-b-2 transition-colors",
                activeTab === tab
                  ? "border-ace-600 text-ace-700"
                  : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300",
              )}
            >
              {tab === "ALL" ? "All" : tab}
              <span className={clsx(
                "ml-1.5 text-[11px] px-1.5 py-0.5 rounded-full",
                activeTab === tab ? "bg-ace-100 text-ace-700" : "bg-slate-100 text-slate-500",
              )}>
                {tabCounts[tab]}
              </span>
            </button>
          ))}
        </div>

        {/* ── Search + filter toolbar ── */}
        <div className="px-4 py-3 border-b border-slate-100 space-y-3">
          <div className="flex items-center gap-3 flex-wrap">
            {/* Search input */}
            <div className="relative flex-1 min-w-[200px] max-w-sm">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              <input
                type="text"
                placeholder="Search patient name or MRN…"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full pl-9 pr-8 py-1.5 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-ace-500/30 focus:border-ace-500"
              />
              {searchInput && (
                <button
                  onClick={() => { setSearchInput(""); setSearch(""); }}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  <X size={13} />
                </button>
              )}
            </div>

            {/* Filter toggle */}
            <button
              onClick={() => setFilterOpen((o) => !o)}
              className={clsx(
                "inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg border transition-colors whitespace-nowrap",
                filterOpen || activeFilterCount > 0
                  ? "border-ace-500 bg-ace-50 text-ace-700"
                  : "border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50",
              )}
            >
              <SlidersHorizontal size={14} />
              Filters
              {activeFilterCount > 0 && (
                <span className="inline-flex items-center justify-center h-4 min-w-[1rem] px-1 text-[10px] font-bold rounded-full bg-ace-600 text-white">
                  {activeFilterCount}
                </span>
              )}
            </button>

            {/* Clear all */}
            {(activeFilterCount > 0 || search) && (
              <button onClick={clearAll} className="text-sm text-slate-500 hover:text-slate-700 whitespace-nowrap">
                Clear all
              </button>
            )}

            {/* Result count */}
            <span className="ml-auto text-xs text-slate-400 whitespace-nowrap">
              Showing {visibleList.length} of {list.length} encounters
            </span>
          </div>

          {/* ── Collapsible filters panel ── */}
          {filterOpen && (
            <div className="pt-3 pb-1 border-t border-slate-100">
              <div className="grid grid-cols-2 gap-5 md:grid-cols-4">

                {/* Specialty */}
                <div>
                  <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">Specialty</p>
                  <div className="max-h-44 overflow-y-auto space-y-1 pr-1">
                    {SPECIALTIES.map((s) => (
                      <label key={s} className="flex items-center gap-2 cursor-pointer group">
                        <input
                          type="checkbox"
                          checked={filters.specialties.includes(s)}
                          onChange={() => toggleSpecialty(s)}
                          className="rounded border-slate-300 text-ace-600 focus:ring-ace-500"
                        />
                        <span className="text-sm text-slate-700 group-hover:text-slate-900">{s}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Lane */}
                <div>
                  <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">Lane</p>
                  <div className="space-y-1.5">
                    {(["STB", "QA", "MANUAL"] as const).map((l) => (
                      <label key={l} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={filters.lanes.includes(l)}
                          onChange={() => toggleLane(l)}
                          className="rounded border-slate-300 text-ace-600 focus:ring-ace-500"
                        />
                        <LaneBadge lane={l} />
                      </label>
                    ))}
                  </div>
                </div>

                {/* Payer */}
                <div>
                  <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">Payer</p>
                  {allPayers.length === 0
                    ? <span className="text-xs text-slate-400">No data yet</span>
                    : (
                      <div className="max-h-44 overflow-y-auto space-y-1 pr-1">
                        {allPayers.map((p) => (
                          <label key={p} className="flex items-center gap-2 cursor-pointer group">
                            <input
                              type="checkbox"
                              checked={filters.payers.includes(p)}
                              onChange={() => togglePayer(p)}
                              className="rounded border-slate-300 text-ace-600 focus:ring-ace-500"
                            />
                            <span className="text-sm text-slate-700 group-hover:text-slate-900 truncate">{p}</span>
                          </label>
                        ))}
                      </div>
                    )}
                </div>

                {/* DOS + Confidence */}
                <div className="space-y-4">
                  <div>
                    <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">Date of Service</p>
                    <div className="space-y-1.5">
                      <input
                        type="date"
                        value={filters.dosFrom}
                        onChange={(e) => setFilters((f) => ({ ...f, dosFrom: e.target.value }))}
                        className="w-full text-xs border border-slate-200 rounded px-2 py-1 text-slate-700 focus:outline-none focus:ring-1 focus:ring-ace-500"
                      />
                      <input
                        type="date"
                        value={filters.dosTo}
                        onChange={(e) => setFilters((f) => ({ ...f, dosTo: e.target.value }))}
                        className="w-full text-xs border border-slate-200 rounded px-2 py-1 text-slate-700 focus:outline-none focus:ring-1 focus:ring-ace-500"
                      />
                    </div>
                  </div>

                  <div>
                    <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                      Confidence: {filters.confMin}% – {filters.confMax}%
                    </p>
                    <div className="space-y-1">
                      <input
                        type="range" min={0} max={100} step={5}
                        value={filters.confMin}
                        onChange={(e) => {
                          const v = Number(e.target.value);
                          setFilters((f) => ({ ...f, confMin: Math.min(v, f.confMax - 5) }));
                        }}
                        className="w-full accent-ace-600"
                      />
                      <input
                        type="range" min={0} max={100} step={5}
                        value={filters.confMax}
                        onChange={(e) => {
                          const v = Number(e.target.value);
                          setFilters((f) => ({ ...f, confMax: Math.max(v, f.confMin + 5) }));
                        }}
                        className="w-full accent-ace-600"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {activeFilterCount > 0 && (
                <button onClick={clearFilters} className="mt-3 text-xs text-rose-500 hover:text-rose-700 font-medium">
                  Clear all filters
                </button>
              )}
            </div>
          )}
        </div>

        {/* ── Table (horizontally scrollable) ── */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm min-w-[960px]">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-200">
                <SortTh field="patient_name" label="Patient / MRN" sortField={sortField} sortDir={sortDir} onSort={handleSort} className="w-[150px] max-w-[150px]" />
                <SortTh field="specialty"    label="Specialty"     sortField={sortField} sortDir={sortDir} onSort={handleSort} />
                <th className="px-4 py-3 font-semibold w-[120px] max-w-[120px]">Scenario</th>
                <SortTh field="payer"              label="Payer"       sortField={sortField} sortDir={sortDir} onSort={handleSort} className="w-[100px] max-w-[100px]" />
                <SortTh field="dos"                label="DOS"         sortField={sortField} sortDir={sortDir} onSort={handleSort} />
                <SortTh field="received_at"        label="Received"    sortField={sortField} sortDir={sortDir} onSort={handleSort} />
                <SortTh field="routing_lane"       label="Lane"        sortField={sortField} sortDir={sortDir} onSort={handleSort} />
                <SortTh field="overall_confidence" label="Confidence"  sortField={sortField} sortDir={sortDir} onSort={handleSort} className="w-40" />
                <th className="px-4 py-3 font-semibold whitespace-nowrap min-w-[80px] overflow-visible">TAT</th>
                <th className="px-4 py-3 sticky right-0 bg-white shadow-[-4px_0_6px_-2px_rgba(0,0,0,0.04)] min-w-[120px]" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading && (
                <tr>
                  <td colSpan={10} className="px-4 py-10 text-center text-slate-400">
                    <Spinner className="h-5 w-5 mx-auto" />
                  </td>
                </tr>
              )}
              {!isLoading && list.length === 0 && (
                <tr>
                  <td colSpan={10} className="px-4 py-12 text-center">
                    <div className="font-medium text-slate-600">No charts in the worklist yet</div>
                    {can(role, "ingest") ? (
                      <div className="text-sm text-slate-400 mt-1">
                        Bring one in via{" "}
                        <Link to="/integrations" className="text-ace-600 hover:underline font-medium">
                          Integrations &amp; Ingestion
                        </Link>
                        {" "}— paste a clinical report and click <b>Ingest into queue</b>. It lands here, ready to code.
                      </div>
                    ) : (
                      <div className="text-sm text-slate-400 mt-1">
                        Charts arrive from the connected EHR / PMS, or via Integrations &amp; Ingestion.
                      </div>
                    )}
                  </td>
                </tr>
              )}
              {!isLoading && list.length > 0 && visibleList.length === 0 && (
                <tr>
                  <td colSpan={10} className="px-4 py-8 text-center text-sm text-slate-400">
                    No encounters match the current search or filters.
                  </td>
                </tr>
              )}
              {visibleList.map((r: EncounterRow) => (
                <tr key={r.id} className="hover:bg-slate-50/70">
                  {/* Patient / MRN — max 150px, truncated */}
                  <td className="px-4 py-3 w-[150px] max-w-[150px]">
                    <div className="font-semibold text-slate-800 truncate" title={r.patient_name}>{r.patient_name}</div>
                    <div className="text-xs text-slate-400 font-mono truncate" title={`${r.mrn} · ${r.source_system}`}>{r.mrn} · {r.source_system}</div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="font-medium text-slate-700">{r.specialty}</span>
                    {r.modality && <span className="ml-1 text-xs text-slate-400">{r.modality}</span>}
                  </td>
                  {/* Scenario — max 120px, truncated */}
                  <td className="px-4 py-3 w-[120px] max-w-[120px]">
                    <span className="text-xs text-slate-500 truncate block" title={r.scenario ?? undefined}>{r.scenario}</span>
                  </td>
                  {/* Payer — max 100px, truncated */}
                  <td className="px-4 py-3 w-[100px] max-w-[100px]">
                    <span className="text-slate-600 truncate block" title={r.payer ?? undefined}>{r.payer}</span>
                  </td>
                  {/* DOS */}
                  <td className="px-4 py-3 text-center whitespace-nowrap">
                    {r.dos ? (() => {
                      const { monthDay, year } = formatDos(r.dos);
                      return (
                        <>
                          <div className="text-xs text-slate-600">{monthDay}</div>
                          <div className="text-[11px] text-slate-400">{year}</div>
                        </>
                      );
                    })() : <span className="text-xs text-slate-300">—</span>}
                  </td>
                  {/* Received At */}
                  <td className="px-4 py-3 text-center whitespace-nowrap">
                    {r.received_at ? (() => {
                      const { date, time } = formatReceivedAt(r.received_at);
                      return (
                        <>
                          <div className="text-xs text-slate-600">{date}</div>
                          <div className="text-[11px] text-slate-400">{time}</div>
                        </>
                      );
                    })() : <span className="text-xs text-slate-300">—</span>}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5">
                      <LaneBadge lane={r.routing_lane} />
                      {r.escalated && (
                        <span title="Escalated · high priority" className="text-amber-500">
                          <Flag size={13} />
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {r.routing_lane && r.routing_lane !== "MANUAL" ? (
                      <ConfidenceBar value={r.overall_confidence} />
                    ) : (
                      <span className="text-xs text-slate-300">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500 whitespace-nowrap min-w-[80px] overflow-visible">
                    {r.latency_ms ? (
                      <span className="inline-flex items-center gap-1 whitespace-nowrap">
                        <Clock size={12} />{(r.latency_ms / 1000).toFixed(1)}s
                      </span>
                    ) : "—"}
                  </td>
                  {/* Action — sticky right */}
                  <td className="px-4 py-3 text-right whitespace-nowrap sticky right-0 bg-white shadow-[-4px_0_6px_-2px_rgba(0,0,0,0.04)] group-hover:bg-slate-50/70 min-w-[120px]">
                    {!r.routing_lane ? (
                      mayCode ? (
                        <button
                          className="btn-ghost py-1.5"
                          disabled={!meta?.llm_available}
                          onClick={() => setConsoleEnc({ id: r.id, name: r.patient_name })}
                        >
                          <Play size={14} /> Code
                        </button>
                      ) : (
                        <span className="text-xs text-slate-300">queued</span>
                      )
                    ) : (
                      <Link to={`/encounter/${r.id}`} className="btn-ghost py-1.5">
                        Review <ArrowRight size={14} />
                      </Link>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {consoleEnc && (
        <AgentConsole
          url={`/encounters/${consoleEnc.id}/code/stream`}
          steps={CODING_STEPS}
          title={consoleEnc.name}
          onClose={() => setConsoleEnc(null)}
          onDone={() => qc.invalidateQueries({ queryKey: ["encounters"] })}
        />
      )}
      {showBatch && (
        <AgentConsole
          url="/coding/run-all/stream"
          label="Batch Orchestrator"
          title="uncoded charts"
          onClose={() => setShowBatch(false)}
          onDone={() => qc.invalidateQueries({ queryKey: ["encounters"] })}
        />
      )}
    </div>
  );
}
