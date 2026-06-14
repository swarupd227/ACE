export interface Meta {
  platform: string;
  module: string;
  phase: string;
  shared_core: string[];
  llm_available: boolean;
  llm_model: string;
  ir_artifact_types: string[];
}

export interface CodeSets {
  cpt?: string[];
  icd?: string[];
  hcpcs?: string[];
  modifiers?: string[];
  pos?: string[];
}

export interface DocumentRow {
  id: string;
  payer: string;
  title: string;
  doc_kind: string;
  provision_count: number;
  source_type: string;
  ingested_at: string | null;
}

export interface Citation {
  line_start: number;
  line_end: number;
  text: string;
  verified?: boolean;
}

export interface Provision {
  id: string;
  provision_type: string;
  summary: string;
  code_sets: CodeSets;
  conditions: Record<string, any>;
  effective_from: string;
  effective_thru: string;
  citation_spans: Citation[];
  confidence: number;
  conf_model: number;
  conf_validator: number;
  routing: string;
}

export interface DocumentProvisions {
  document: { id: string; payer: string; title: string; doc_kind: string };
  provisions: Provision[];
}

export interface RuleLibraryEntry {
  id: string;
  payer: string;
  title: string;
  code_sets: CodeSets;
  status: string;
}

export type ReconVerdict = "NET_NEW" | "UPDATE" | "DUPLICATE" | "CONFLICT";
export type ValVerdict = "SUPPORTED" | "PARTIAL" | "UNSUPPORTED" | "";
export type RecStatus = "PENDING_REVIEW" | "APPROVED" | "PUBLISHED";

export interface Recommendation {
  id: string;
  payer: string;
  provision_type: string;
  candidate_summary: string;
  code_sets: CodeSets;
  validation_verdict: ValVerdict;
  validation_rationale: string;
  evidence: { provision_id: string; quote: string }[];
  reconciliation_verdict: ReconVerdict;
  matched_rule_id: string;
  reconciliation_rationale: string;
  code_overlap: number;
  confidence: number;
  status: RecStatus;
  needs_attention: boolean;
  published_to_ace: boolean;
  ace_publish: {
    payer?: string;
    source?: string;
    policies?: { code: string; ace_id: number; payer: string }[];
    ace_base_url?: string;
  };
}

export interface GoldenCase {
  id?: string;
  provision_type: string;
  expected_verdict: string;
  expected_codes: string[];
  expected_attention: boolean;
  note: string;
}

export interface EvalCase {
  provision_type: string;
  found: boolean;
  expected_verdict: string;
  actual_verdict: string | null;
  verdict_ok: boolean;
  matched_rule_id: string | null;
  expected_codes: string[];
  missing_codes: string[];
  expected_attention: boolean;
  actual_attention: boolean | null;
  attention_ok: boolean;
  confidence: number | null;
  note: string;
}

export interface EvalReport {
  run_id?: string;
  model_version: string;
  overall_score: number;
  golden_cases?: number;
  created_at?: string | null;
  phases: {
    P1: { provision_coverage: number; code_recall: number; citation_validity: number };
    P2: { recall: number; precision: number; planted: number; found: number; recovered: number };
    P3: { verdict_accuracy: number; attention_accuracy: number };
    calibration: { mean_conf_correct: number | null; mean_conf_wrong: number | null; n_correct: number; n_wrong: number };
    cases: EvalCase[];
  };
}

export interface AceStatus {
  reachable: boolean;
  ace_base_url: string;
  ace_llm_available?: boolean;
  p2r_published_policies?: number;
  error?: string;
}

// P1 — sources / acquisition / deltas
export interface PolicySource {
  id: string; payer: string; name: string; source_type: string; location: string;
  cadence: string; status: string; fetch_count: number; last_checked: string; last_document_id: string;
}
export interface PolicyDelta {
  id: string; source_id: string; payer: string; document_id: string; prev_document_id: string;
  change_type: string; added: string[]; removed: string[];
  changed: { type: string; before: string; after: string; added_signals?: string[]; removed_signals?: string[] }[];
  summary: string; created_at: string | null;
}

// P2 — denial signals
export interface DenialSignal {
  id: string; payer: string; procedure_code: string; denial_carc: string; pattern_type: string;
  recent_denials: number; recent_total: number; recent_rate: number; baseline_rate: number;
  lift: number; z_score: number; score: number; rank: number; status: string;
  evidence: { aggregates?: Record<string, any>; sample_lines?: any[] };
  proposed_rule: { provision_type: string; summary: string; code_sets: CodeSets };
  promoted_recommendation_id: string;
}

// P4 — rule IR / replay
export interface RuleIr {
  ir: {
    rule_id: string; version: number; payer: string; rule_type: string; action: string;
    applies_to: CodeSets; statement: string; disposition: string; origin: string;
    confidence: number; provenance: Record<string, any>;
  };
  artifacts: { ace: any[]; generic: Record<string, any> };
}
export interface ReplayResult {
  recommendation_id: string; rule_type?: string; codes?: string[]; addresses_carc?: string[];
  claims_matched: number; current_denials?: number; current_denial_rate?: number;
  addressable_denials?: number; projected_denial_rate?: number; projected_denial_reduction?: number;
  addressable_amount?: number; sample_claims?: any[]; note?: string;
}

// UX — audit + lineage
export interface AuditEntry {
  id: string; phase: string; action: string; actor: string; entity_type: string;
  entity_id: string; payer: string; summary: string; lineage: Record<string, any>; created_at: string | null;
}
export interface Lineage {
  recommendation: Record<string, any>;
  source: any;
  deployment: any;
  decisions: AuditEntry[];
}
