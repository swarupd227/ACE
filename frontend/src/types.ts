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
  received_at?: string;
  client: string;
  source_system: string;
  scenario: string;
  status: string;
  routing_lane: Lane;
  routing_reason: string;
  overall_confidence: number;
  latency_ms: number;
  escalated: boolean;
  priority: string;
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
  learning_applied: boolean;
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
  escalated: boolean;
  escalated_to: string;
  assigned_to: string;
  priority: string;
  modified: boolean;
  drg: DrgResult | null;
  hcc: HccResult | null;
  anes: AnesResult | null;
  apc: ApcResult | null;
  codes: CodeResult[];
}
export interface ApcResult {
  lines: { code: string; si: string; apc: string; apc_title: string; rate: number; pct: number; allowed: number }[];
  packaged: { code: string; si: string; note: string }[];
  not_covered: string[];
  facility_total: number;
  trace: { step: string; detail: string }[];
  resolved: boolean;
}
export interface AnesResult {
  code: string;
  base_units: number;
  time_minutes: number;
  time_units: number;
  phys_modifier: string;
  phys_units: number;
  qual_circ: { code: string; units: number; description: string }[];
  total_units: number;
  conversion_factor: number;
  estimated_allowable: number;
  trace: { step: string; detail: string }[];
  resolved: boolean;
}
export interface HccResult {
  raf: number;
  demographic: { band?: string; factor?: number; segment?: string };
  hccs: { hcc: string; label: string; coefficient: number; dx: string[] }[];
  suppressed: { hcc: string; by: string }[];
  unmapped: string[];
  trace: { step: string; detail: string }[];
  resolved: boolean;
}
export interface DrgResult {
  drg: string;
  title: string;
  mdc: string;
  mdc_title: string;
  drg_type: "MED" | "SURG" | string;
  severity: "MCC" | "CC" | "NONE" | string;
  weight: number;
  pdx: string;
  or_procedure: string;
  cc_mcc_drivers: { code: string; tier: "CC" | "MCC"; description: string }[];
  trace: { step: string; detail: string }[];
  resolved: boolean;
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
export interface CdiQuery {
  id: string;
  encounter_id: string;
  specialty: string;
  status: string;
  question: string;
  clinical_indicators: string;
  options: string[];
  target: string;
  potential_codes: string[];
  rationale: string;
  physician_response: string;
  responded_by: string;
  created_at: string | null;
  patient_name?: string;
  mrn?: string;
}

export interface CtItem {
  run_id: string;
  encounter_id: string;
  patient_name: string;
  mrn: string;
  specialty: string;
  payer: string;
  lane: string;
  priority: string;
  escalated: boolean;
  assigned_to: string;
  age_minutes: number;
  has_open_cdi: boolean;
  sla_status: string;
}
export interface CtQueue {
  key: string;
  label: string;
  sla_target_min: number;
  count: number;
  breached: number;
  items: CtItem[];
}
export interface ControlTower {
  roster: string[];
  sla_targets: Record<string, number>;
  summary: { total: number; unassigned: number; breached: number };
  queues: CtQueue[];
}
export interface Policy {
  id: number;
  payer: string;
  code: string;
  policy_id: string;
  medical_necessity: string;
  requires_auth: boolean;
  modifier_pref: string;
  covered_dx: string[];
  source: string;
}

export interface CodeMap {
  system: string;
  code: string;
}
export interface Concept {
  id: number;
  cui: string;
  name: string;
  semantic_type: string;
  maps_to: CodeMap[];
}
export interface Edge {
  id: number;
  src_cui: string;
  rel: string;
  dst_cui: string;
}
export interface EdgeIn {
  src_cui: string;
  rel: string;
  dst_cui: string;
}
export interface Guideline {
  id: number;
  source: string;
  section: string;
  text: string;
  specialty: string;
}

export interface LlmStatus {
  provider: string;
  model_default: string;
  model_hard: string;
  base_url: string;
  active: string;
  available: boolean;
  anthropic_key_present: boolean;
  openai_key_present: boolean;
}
export interface AuditChange {
  id: string;
  at: string;
  actor: string;
  role: string;
  area: string;
  action: string;
  target: string;
  detail: Record<string, any>;
}
export interface AuditEvent {
  id: string;
  ts: string;
  source: "coding" | "governance";
  actor: string;
  role: string;
  category: string;
  action: string;
  target: string;
  specialty: string;
  encounter_id: string;
  run_id: string;
  model_version: string;
  detail: Record<string, any>;
}
export interface GlobalAudit {
  events: AuditEvent[];
  summary: {
    matched: number;
    coding_events: number;
    governance_events: number;
    distinct_actors: number;
    newest: string | null;
    oldest: string | null;
  };
  facets: {
    by_source: Record<string, number>;
    by_category: Record<string, number>;
    by_actor: Record<string, number>;
  };
}
export interface RefCode {
  id: number;
  code_system: string;
  code: string;
  description: string;
  billable: boolean;
  modality: string;
  sex_restriction: string;
  age_min: number;
  age_max: number;
  source: string;
  effective_start?: string;
  effective_end?: string;
}
export interface Ncci {
  id: number;
  column1: string;
  column2: string;
  modifier_allowed: boolean;
  rationale: string;
  source: string;
}
export interface Mue {
  id: number;
  code: string;
  max_units: number;
  rationale: string;
  source: string;
}
export interface Modifier {
  id: number;
  modifier: string;
  description: string;
  applies_to: string;
  notes: string;
}

export interface Golden {
  id: number;
  specialty: string;
  chart_text: string;
  truth: { icd?: string[]; cpt?: string[] };
  irr: number;
  ambiguous: boolean;
}

export interface Dashboard {
  total_encounters: number;
  coded: number;
  eligible: number;
  eligible_excluded: number;
  stb_count: number;
  qa_count: number;
  manual_count: number;
  stb_rate: number;
  avg_accuracy: number;
  avg_latency_ms: number;
  manual_effort_reduction: number;
  exception_rate: number;
  tat: { baseline_min: number; assisted_min: number; reduction_pct: number };
  maturity: { stage: string; stb_rate: number; target: number; stages: string[] };
  by_specialty: any[];
  model_performance: {
    active_model: string;
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
    llm_calls: number;
    avg_tokens_per_chart: number;
    avg_calls_per_chart: number;
    avg_latency_ms: number;
    p95_latency_ms: number;
    avg_confidence: number;
    override_rate: number;
    by_model: {
      model: string;
      charts: number;
      stb_rate: number;
      avg_confidence: number;
      avg_latency_ms: number;
      avg_tokens: number;
      override_rate: number;
    }[];
  };
}

export interface Integrations {
  connectors: { name: string; type: string; channel: string; status: string; charts_ingested: number }[];
  channels: string[];
  api_docs: string;
  note: string;
}
