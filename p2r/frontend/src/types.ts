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
  golden_cases: number;
  provisions_extracted: number;
  recommendations: number;
  model_version: string;
  metrics: {
    provision_coverage: number;
    code_recall: number;
    citation_rate: number;
    verdict_accuracy: number;
    attention_accuracy: number;
  };
  cases: EvalCase[];
}

export interface AceStatus {
  reachable: boolean;
  ace_base_url: string;
  ace_llm_available?: boolean;
  p2r_published_policies?: number;
  error?: string;
}
