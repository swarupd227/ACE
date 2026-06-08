export type Lane = "STB" | "QA" | "MANUAL" | "";

export interface EncounterRow {
  id: string;
  mrn: string;
  patient_name: string;
  age: number;
  sex: string;
  specialty: string;
  modality: string;
  payer: string;
  dos: string;
  client: string;
  source_system: string;
  scenario: string;
  status: string;
  routing_lane: Lane;
  routing_reason: string;
  overall_confidence: number;
  latency_ms: number;
  run_id: string | null;
}

export interface Citation {
  section: string;
  line_start: number;
  line_end: number;
  text: string;
}
export interface GuidelineCitation {
  source: string;
  section: string;
  text: string;
}
export interface GateResult {
  gate: string;
  passed: boolean;
  detail: string;
}
export interface CodeResult {
  id: string;
  code_system: string;
  code: string;
  description: string;
  role: string;
  modifiers: string[];
  sequence: number;
  confidence: number;
  conf_doc_match: number;
  conf_historical: number;
  conf_rule: number;
  conf_model: number;
  chart_citations: Citation[];
  guideline_citations: GuidelineCitation[];
  rule_justification: string;
  gate_results: GateResult[];
  status: string;
  is_overridden: boolean;
  override_code: string;
  override_reason: string;
  accepted_by: string;
}
export interface StageLogEntry {
  stage: string;
  title: string;
  [k: string]: any;
}
export interface Run {
  id: string;
  encounter_id: string;
  status: string;
  routing_lane: Lane;
  routing_reason: string;
  model_version: string;
  chart_summary: string;
  eligibility: any;
  stage_log: StageLogEntry[];
  overall_confidence: number;
  accuracy_estimate: number;
  latency_ms: number;
  codes: CodeResult[];
}
export interface EncounterDetail {
  id: string;
  mrn: string;
  patient_name: string;
  age: number;
  sex: string;
  specialty: string;
  modality: string;
  encounter_type: string;
  payer: string;
  pos: string;
  dos: string;
  client: string;
  source_system: string;
  report_type: string;
  scenario: string;
  status: string;
  chart_lines: { n: number; text: string }[];
  run: Run | null;
}
export interface Meta {
  product: string;
  framing: string;
  env: string;
  llm_mode: string;
  llm_available: boolean;
  model_default: string;
  model_hard: string;
  model_version: string;
  self_consistency_samples: number;
  specialties: string[];
  provenance: Record<string, string>;
}
export interface Dashboard {
  total_encounters: number;
  coded: number;
  stb_count: number;
  qa_count: number;
  manual_count: number;
  stb_rate: number;
  avg_accuracy: number;
  avg_latency_ms: number;
  manual_effort_reduction: number;
  by_specialty: any[];
}
