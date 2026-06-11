--
-- PostgreSQL database dump
--

\restrict URfhTffeCvEXXtbRHbBY6A5wSvplSv5as3ZIvRj2LNPhXh3dMcVkIJGtk7AbCBE

-- Dumped from database version 16.13 (Debian 16.13-1.pgdg12+1)
-- Dumped by pg_dump version 16.13 (Debian 16.13-1.pgdg12+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: anes_base_units; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.anes_base_units (
    id integer NOT NULL,
    code character varying(8) NOT NULL,
    base_units integer NOT NULL,
    source character varying(40) NOT NULL
);


--
-- Name: anes_base_units_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.anes_base_units_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: anes_base_units_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.anes_base_units_id_seq OWNED BY public.anes_base_units.id;


--
-- Name: anes_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.anes_results (
    id character varying(32) NOT NULL,
    run_id character varying(32) NOT NULL,
    encounter_id character varying(32) NOT NULL,
    code character varying(8) NOT NULL,
    base_units integer NOT NULL,
    time_minutes integer NOT NULL,
    time_units double precision NOT NULL,
    phys_modifier character varying(4) NOT NULL,
    phys_units integer NOT NULL,
    qual_circ jsonb NOT NULL,
    total_units double precision NOT NULL,
    conversion_factor double precision NOT NULL,
    estimated_allowable double precision NOT NULL,
    trace jsonb NOT NULL,
    resolved boolean NOT NULL
);


--
-- Name: apc_entries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.apc_entries (
    id integer NOT NULL,
    code character varying(8) NOT NULL,
    status_indicator character varying(4) NOT NULL,
    apc character varying(8) NOT NULL,
    apc_title character varying(120) NOT NULL,
    national_rate double precision NOT NULL,
    source character varying(40) NOT NULL
);


--
-- Name: apc_entries_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.apc_entries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: apc_entries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.apc_entries_id_seq OWNED BY public.apc_entries.id;


--
-- Name: apc_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.apc_results (
    id character varying(32) NOT NULL,
    run_id character varying(32) NOT NULL,
    encounter_id character varying(32) NOT NULL,
    lines jsonb NOT NULL,
    packaged jsonb NOT NULL,
    not_covered jsonb NOT NULL,
    facility_total double precision NOT NULL,
    trace jsonb NOT NULL,
    resolved boolean NOT NULL
);


--
-- Name: app_config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.app_config (
    key character varying(60) NOT NULL,
    value jsonb NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: audit_ledger; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_ledger (
    id character varying(32) NOT NULL,
    run_id character varying(32) NOT NULL,
    encounter_id character varying(32) NOT NULL,
    stage character varying(40) NOT NULL,
    actor character varying(40) NOT NULL,
    event character varying(80) NOT NULL,
    detail jsonb NOT NULL,
    model_version character varying(60) NOT NULL,
    ts timestamp with time zone NOT NULL
);


--
-- Name: cc_mcc; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cc_mcc (
    id integer NOT NULL,
    code character varying(16) NOT NULL,
    tier character varying(4) NOT NULL,
    source character varying(40) NOT NULL
);


--
-- Name: cc_mcc_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cc_mcc_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cc_mcc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cc_mcc_id_seq OWNED BY public.cc_mcc.id;


--
-- Name: cdi_queries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cdi_queries (
    id character varying(32) NOT NULL,
    encounter_id character varying(32) NOT NULL,
    run_id character varying(32) NOT NULL,
    specialty character varying(40) NOT NULL,
    status character varying(16) NOT NULL,
    question text NOT NULL,
    clinical_indicators text NOT NULL,
    options jsonb NOT NULL,
    target character varying(120) NOT NULL,
    potential_codes jsonb NOT NULL,
    rationale text NOT NULL,
    physician_response text NOT NULL,
    responded_by character varying(80) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    answered_at timestamp with time zone
);


--
-- Name: code_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.code_results (
    id character varying(32) NOT NULL,
    run_id character varying(32) NOT NULL,
    code_system character varying(12) NOT NULL,
    code character varying(16) NOT NULL,
    description text NOT NULL,
    role character varying(24) NOT NULL,
    modifiers jsonb NOT NULL,
    sequence integer NOT NULL,
    confidence double precision NOT NULL,
    conf_doc_match double precision NOT NULL,
    conf_historical double precision NOT NULL,
    conf_rule double precision NOT NULL,
    conf_model double precision NOT NULL,
    chart_citations jsonb NOT NULL,
    guideline_citations jsonb NOT NULL,
    rule_justification text NOT NULL,
    gate_results jsonb NOT NULL,
    status character varying(24) NOT NULL,
    is_overridden boolean NOT NULL,
    override_code character varying(16) NOT NULL,
    override_reason text NOT NULL,
    accepted_by character varying(80) NOT NULL,
    learning_applied boolean NOT NULL
);


--
-- Name: coding_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.coding_runs (
    id character varying(32) NOT NULL,
    encounter_id character varying(32) NOT NULL,
    status character varying(24) NOT NULL,
    routing_lane character varying(12) NOT NULL,
    routing_reason text NOT NULL,
    model_version character varying(60) NOT NULL,
    chart_summary text NOT NULL,
    eligibility jsonb NOT NULL,
    stage_log jsonb NOT NULL,
    overall_confidence double precision NOT NULL,
    accuracy_estimate double precision NOT NULL,
    latency_ms integer NOT NULL,
    input_tokens integer NOT NULL,
    output_tokens integer NOT NULL,
    llm_calls integer NOT NULL,
    escalated boolean NOT NULL,
    escalated_to character varying(80) NOT NULL,
    assigned_to character varying(80) NOT NULL,
    priority character varying(12) NOT NULL,
    ai_snapshot jsonb NOT NULL,
    started_at timestamp with time zone NOT NULL,
    finished_at timestamp with time zone,
    billed_at timestamp with time zone
);


--
-- Name: config_audit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.config_audit (
    id character varying(32) NOT NULL,
    at timestamp with time zone NOT NULL,
    actor character varying(60) NOT NULL,
    role character varying(40) NOT NULL,
    area character varying(40) NOT NULL,
    action character varying(16) NOT NULL,
    target character varying(160) NOT NULL,
    detail jsonb NOT NULL
);


--
-- Name: demographic_factors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.demographic_factors (
    id integer NOT NULL,
    sex character varying(1) NOT NULL,
    age_min integer NOT NULL,
    age_max integer NOT NULL,
    factor double precision NOT NULL,
    segment character varying(24) NOT NULL
);


--
-- Name: demographic_factors_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.demographic_factors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: demographic_factors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.demographic_factors_id_seq OWNED BY public.demographic_factors.id;


--
-- Name: drg_definitions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.drg_definitions (
    id integer NOT NULL,
    drg character varying(4) NOT NULL,
    title character varying(200) NOT NULL,
    mdc character varying(4) NOT NULL,
    mdc_title character varying(120) NOT NULL,
    drg_type character varying(8) NOT NULL,
    base_key character varying(40) NOT NULL,
    severity character varying(8) NOT NULL,
    weight double precision NOT NULL,
    source character varying(40) NOT NULL
);


--
-- Name: drg_definitions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.drg_definitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: drg_definitions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.drg_definitions_id_seq OWNED BY public.drg_definitions.id;


--
-- Name: drg_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.drg_results (
    id character varying(32) NOT NULL,
    run_id character varying(32) NOT NULL,
    encounter_id character varying(32) NOT NULL,
    drg character varying(4) NOT NULL,
    title character varying(200) NOT NULL,
    mdc character varying(4) NOT NULL,
    mdc_title character varying(120) NOT NULL,
    drg_type character varying(8) NOT NULL,
    severity character varying(8) NOT NULL,
    weight double precision NOT NULL,
    pdx character varying(16) NOT NULL,
    or_procedure character varying(8) NOT NULL,
    cc_mcc_drivers jsonb NOT NULL,
    trace jsonb NOT NULL,
    resolved boolean NOT NULL
);


--
-- Name: dx_hcc_map; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dx_hcc_map (
    id integer NOT NULL,
    dx_code character varying(16) NOT NULL,
    hcc character varying(8) NOT NULL
);


--
-- Name: dx_hcc_map_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dx_hcc_map_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dx_hcc_map_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dx_hcc_map_id_seq OWNED BY public.dx_hcc_map.id;


--
-- Name: encounters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.encounters (
    id character varying(32) NOT NULL,
    mrn character varying(32) NOT NULL,
    patient_name character varying(120) NOT NULL,
    age integer NOT NULL,
    sex character varying(1) NOT NULL,
    specialty character varying(40) NOT NULL,
    modality character varying(40) NOT NULL,
    encounter_type character varying(40) NOT NULL,
    payer character varying(60) NOT NULL,
    pos character varying(4) NOT NULL,
    dos character varying(10) NOT NULL,
    client character varying(80) NOT NULL,
    source_system character varying(40) NOT NULL,
    report_type character varying(40) NOT NULL,
    chart_text text NOT NULL,
    scenario character varying(80) NOT NULL,
    status character varying(24) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    received_at timestamp with time zone NOT NULL,
    doc_status character varying(16) DEFAULT 'final'::character varying,
    signed_by character varying(120) DEFAULT ''::character varying,
    signed_at timestamp with time zone,
    addendum_at timestamp with time zone
);


--
-- Name: golden_cases; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.golden_cases (
    id integer NOT NULL,
    specialty character varying(40) NOT NULL,
    chart_text text NOT NULL,
    truth jsonb NOT NULL,
    irr double precision NOT NULL,
    ambiguous boolean NOT NULL
);


--
-- Name: golden_cases_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.golden_cases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: golden_cases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.golden_cases_id_seq OWNED BY public.golden_cases.id;


--
-- Name: guideline_chunks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.guideline_chunks (
    id integer NOT NULL,
    source character varying(80) NOT NULL,
    section character varying(40) NOT NULL,
    text text NOT NULL,
    specialty character varying(40) NOT NULL
);


--
-- Name: guideline_chunks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.guideline_chunks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: guideline_chunks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.guideline_chunks_id_seq OWNED BY public.guideline_chunks.id;


--
-- Name: hcc_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hcc_categories (
    id integer NOT NULL,
    hcc character varying(8) NOT NULL,
    label character varying(160) NOT NULL,
    coefficient double precision NOT NULL,
    source character varying(40) NOT NULL
);


--
-- Name: hcc_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hcc_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hcc_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hcc_categories_id_seq OWNED BY public.hcc_categories.id;


--
-- Name: hcc_hierarchies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hcc_hierarchies (
    id integer NOT NULL,
    superior_hcc character varying(8) NOT NULL,
    suppressed_hcc character varying(8) NOT NULL
);


--
-- Name: hcc_hierarchies_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hcc_hierarchies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hcc_hierarchies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hcc_hierarchies_id_seq OWNED BY public.hcc_hierarchies.id;


--
-- Name: hcc_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hcc_results (
    id character varying(32) NOT NULL,
    run_id character varying(32) NOT NULL,
    encounter_id character varying(32) NOT NULL,
    raf double precision NOT NULL,
    demographic jsonb NOT NULL,
    hccs jsonb NOT NULL,
    suppressed jsonb NOT NULL,
    unmapped jsonb NOT NULL,
    trace jsonb NOT NULL,
    resolved boolean NOT NULL
);


--
-- Name: learning_examples; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.learning_examples (
    id character varying(32) NOT NULL,
    specialty character varying(40) NOT NULL,
    pattern_key character varying(120) NOT NULL,
    wrong_code character varying(16) NOT NULL,
    correct_code character varying(16) NOT NULL,
    code_system character varying(12) NOT NULL,
    reason text NOT NULL,
    snippet text NOT NULL,
    applied boolean NOT NULL,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: mdc_assignments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mdc_assignments (
    id integer NOT NULL,
    dx_prefix character varying(8) NOT NULL,
    mdc character varying(4) NOT NULL,
    mdc_title character varying(120) NOT NULL,
    medical_base_key character varying(40) NOT NULL
);


--
-- Name: mdc_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.mdc_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: mdc_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.mdc_assignments_id_seq OWNED BY public.mdc_assignments.id;


--
-- Name: modifier_rules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.modifier_rules (
    id integer NOT NULL,
    modifier character varying(4) NOT NULL,
    description text NOT NULL,
    applies_to character varying(40) NOT NULL,
    notes text NOT NULL
);


--
-- Name: modifier_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.modifier_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: modifier_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.modifier_rules_id_seq OWNED BY public.modifier_rules.id;


--
-- Name: mue_limits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mue_limits (
    id integer NOT NULL,
    code character varying(16) NOT NULL,
    max_units integer NOT NULL,
    rationale text NOT NULL,
    source character varying(40) NOT NULL
);


--
-- Name: mue_limits_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.mue_limits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: mue_limits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.mue_limits_id_seq OWNED BY public.mue_limits.id;


--
-- Name: ncci_edits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ncci_edits (
    id integer NOT NULL,
    column1 character varying(16) NOT NULL,
    column2 character varying(16) NOT NULL,
    modifier_allowed boolean NOT NULL,
    rationale text NOT NULL,
    source character varying(40) NOT NULL
);


--
-- Name: ncci_edits_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ncci_edits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ncci_edits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ncci_edits_id_seq OWNED BY public.ncci_edits.id;


--
-- Name: ontology_concepts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ontology_concepts (
    id integer NOT NULL,
    cui character varying(24) NOT NULL,
    name character varying(160) NOT NULL,
    semantic_type character varying(60) NOT NULL,
    maps_to jsonb NOT NULL
);


--
-- Name: ontology_concepts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ontology_concepts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ontology_concepts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ontology_concepts_id_seq OWNED BY public.ontology_concepts.id;


--
-- Name: ontology_edges; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ontology_edges (
    id integer NOT NULL,
    src_cui character varying(24) NOT NULL,
    rel character varying(40) NOT NULL,
    dst_cui character varying(24) NOT NULL
);


--
-- Name: ontology_edges_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ontology_edges_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ontology_edges_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ontology_edges_id_seq OWNED BY public.ontology_edges.id;


--
-- Name: or_procedures; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.or_procedures (
    id integer NOT NULL,
    pcs_code character varying(8) NOT NULL,
    surgical_base_key character varying(40) NOT NULL,
    mdc character varying(4) NOT NULL
);


--
-- Name: or_procedures_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.or_procedures_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: or_procedures_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.or_procedures_id_seq OWNED BY public.or_procedures.id;


--
-- Name: payer_policies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payer_policies (
    id integer NOT NULL,
    payer character varying(60) NOT NULL,
    code character varying(16) NOT NULL,
    policy_id character varying(40) NOT NULL,
    medical_necessity text NOT NULL,
    requires_auth boolean NOT NULL,
    modifier_pref character varying(60) NOT NULL,
    covered_dx jsonb NOT NULL,
    source character varying(60) NOT NULL
);


--
-- Name: payer_policies_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payer_policies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payer_policies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payer_policies_id_seq OWNED BY public.payer_policies.id;


--
-- Name: qual_circumstances; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.qual_circumstances (
    id integer NOT NULL,
    code character varying(8) NOT NULL,
    units integer NOT NULL,
    description character varying(160) NOT NULL
);


--
-- Name: qual_circumstances_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.qual_circumstances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: qual_circumstances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.qual_circumstances_id_seq OWNED BY public.qual_circumstances.id;


--
-- Name: reference_codes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reference_codes (
    id integer NOT NULL,
    code_system character varying(12) NOT NULL,
    code character varying(16) NOT NULL,
    description text NOT NULL,
    billable boolean NOT NULL,
    parent character varying(16) NOT NULL,
    sex_restriction character varying(1) NOT NULL,
    age_min integer NOT NULL,
    age_max integer NOT NULL,
    modality character varying(20) NOT NULL,
    effective_start character varying(10) NOT NULL,
    effective_end character varying(10) NOT NULL,
    source character varying(40) NOT NULL
);


--
-- Name: reference_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.reference_codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: reference_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.reference_codes_id_seq OWNED BY public.reference_codes.id;


--
-- Name: anes_base_units id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anes_base_units ALTER COLUMN id SET DEFAULT nextval('public.anes_base_units_id_seq'::regclass);


--
-- Name: apc_entries id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.apc_entries ALTER COLUMN id SET DEFAULT nextval('public.apc_entries_id_seq'::regclass);


--
-- Name: cc_mcc id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cc_mcc ALTER COLUMN id SET DEFAULT nextval('public.cc_mcc_id_seq'::regclass);


--
-- Name: demographic_factors id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.demographic_factors ALTER COLUMN id SET DEFAULT nextval('public.demographic_factors_id_seq'::regclass);


--
-- Name: drg_definitions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.drg_definitions ALTER COLUMN id SET DEFAULT nextval('public.drg_definitions_id_seq'::regclass);


--
-- Name: dx_hcc_map id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dx_hcc_map ALTER COLUMN id SET DEFAULT nextval('public.dx_hcc_map_id_seq'::regclass);


--
-- Name: golden_cases id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.golden_cases ALTER COLUMN id SET DEFAULT nextval('public.golden_cases_id_seq'::regclass);


--
-- Name: guideline_chunks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guideline_chunks ALTER COLUMN id SET DEFAULT nextval('public.guideline_chunks_id_seq'::regclass);


--
-- Name: hcc_categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hcc_categories ALTER COLUMN id SET DEFAULT nextval('public.hcc_categories_id_seq'::regclass);


--
-- Name: hcc_hierarchies id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hcc_hierarchies ALTER COLUMN id SET DEFAULT nextval('public.hcc_hierarchies_id_seq'::regclass);


--
-- Name: mdc_assignments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mdc_assignments ALTER COLUMN id SET DEFAULT nextval('public.mdc_assignments_id_seq'::regclass);


--
-- Name: modifier_rules id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.modifier_rules ALTER COLUMN id SET DEFAULT nextval('public.modifier_rules_id_seq'::regclass);


--
-- Name: mue_limits id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mue_limits ALTER COLUMN id SET DEFAULT nextval('public.mue_limits_id_seq'::regclass);


--
-- Name: ncci_edits id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ncci_edits ALTER COLUMN id SET DEFAULT nextval('public.ncci_edits_id_seq'::regclass);


--
-- Name: ontology_concepts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ontology_concepts ALTER COLUMN id SET DEFAULT nextval('public.ontology_concepts_id_seq'::regclass);


--
-- Name: ontology_edges id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ontology_edges ALTER COLUMN id SET DEFAULT nextval('public.ontology_edges_id_seq'::regclass);


--
-- Name: or_procedures id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.or_procedures ALTER COLUMN id SET DEFAULT nextval('public.or_procedures_id_seq'::regclass);


--
-- Name: payer_policies id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payer_policies ALTER COLUMN id SET DEFAULT nextval('public.payer_policies_id_seq'::regclass);


--
-- Name: qual_circumstances id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.qual_circumstances ALTER COLUMN id SET DEFAULT nextval('public.qual_circumstances_id_seq'::regclass);


--
-- Name: reference_codes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reference_codes ALTER COLUMN id SET DEFAULT nextval('public.reference_codes_id_seq'::regclass);


--
-- Name: anes_base_units anes_base_units_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anes_base_units
    ADD CONSTRAINT anes_base_units_code_key UNIQUE (code);


--
-- Name: anes_base_units anes_base_units_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anes_base_units
    ADD CONSTRAINT anes_base_units_pkey PRIMARY KEY (id);


--
-- Name: anes_results anes_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anes_results
    ADD CONSTRAINT anes_results_pkey PRIMARY KEY (id);


--
-- Name: anes_results anes_results_run_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anes_results
    ADD CONSTRAINT anes_results_run_id_key UNIQUE (run_id);


--
-- Name: apc_entries apc_entries_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.apc_entries
    ADD CONSTRAINT apc_entries_code_key UNIQUE (code);


--
-- Name: apc_entries apc_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.apc_entries
    ADD CONSTRAINT apc_entries_pkey PRIMARY KEY (id);


--
-- Name: apc_results apc_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.apc_results
    ADD CONSTRAINT apc_results_pkey PRIMARY KEY (id);


--
-- Name: apc_results apc_results_run_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.apc_results
    ADD CONSTRAINT apc_results_run_id_key UNIQUE (run_id);


--
-- Name: app_config app_config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_config
    ADD CONSTRAINT app_config_pkey PRIMARY KEY (key);


--
-- Name: audit_ledger audit_ledger_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_ledger
    ADD CONSTRAINT audit_ledger_pkey PRIMARY KEY (id);


--
-- Name: cc_mcc cc_mcc_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cc_mcc
    ADD CONSTRAINT cc_mcc_code_key UNIQUE (code);


--
-- Name: cc_mcc cc_mcc_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cc_mcc
    ADD CONSTRAINT cc_mcc_pkey PRIMARY KEY (id);


--
-- Name: cdi_queries cdi_queries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cdi_queries
    ADD CONSTRAINT cdi_queries_pkey PRIMARY KEY (id);


--
-- Name: code_results code_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.code_results
    ADD CONSTRAINT code_results_pkey PRIMARY KEY (id);


--
-- Name: coding_runs coding_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.coding_runs
    ADD CONSTRAINT coding_runs_pkey PRIMARY KEY (id);


--
-- Name: config_audit config_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.config_audit
    ADD CONSTRAINT config_audit_pkey PRIMARY KEY (id);


--
-- Name: demographic_factors demographic_factors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.demographic_factors
    ADD CONSTRAINT demographic_factors_pkey PRIMARY KEY (id);


--
-- Name: drg_definitions drg_definitions_drg_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.drg_definitions
    ADD CONSTRAINT drg_definitions_drg_key UNIQUE (drg);


--
-- Name: drg_definitions drg_definitions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.drg_definitions
    ADD CONSTRAINT drg_definitions_pkey PRIMARY KEY (id);


--
-- Name: drg_results drg_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.drg_results
    ADD CONSTRAINT drg_results_pkey PRIMARY KEY (id);


--
-- Name: drg_results drg_results_run_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.drg_results
    ADD CONSTRAINT drg_results_run_id_key UNIQUE (run_id);


--
-- Name: dx_hcc_map dx_hcc_map_dx_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dx_hcc_map
    ADD CONSTRAINT dx_hcc_map_dx_code_key UNIQUE (dx_code);


--
-- Name: dx_hcc_map dx_hcc_map_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dx_hcc_map
    ADD CONSTRAINT dx_hcc_map_pkey PRIMARY KEY (id);


--
-- Name: encounters encounters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounters
    ADD CONSTRAINT encounters_pkey PRIMARY KEY (id);


--
-- Name: golden_cases golden_cases_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.golden_cases
    ADD CONSTRAINT golden_cases_pkey PRIMARY KEY (id);


--
-- Name: guideline_chunks guideline_chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guideline_chunks
    ADD CONSTRAINT guideline_chunks_pkey PRIMARY KEY (id);


--
-- Name: hcc_categories hcc_categories_hcc_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hcc_categories
    ADD CONSTRAINT hcc_categories_hcc_key UNIQUE (hcc);


--
-- Name: hcc_categories hcc_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hcc_categories
    ADD CONSTRAINT hcc_categories_pkey PRIMARY KEY (id);


--
-- Name: hcc_hierarchies hcc_hierarchies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hcc_hierarchies
    ADD CONSTRAINT hcc_hierarchies_pkey PRIMARY KEY (id);


--
-- Name: hcc_results hcc_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hcc_results
    ADD CONSTRAINT hcc_results_pkey PRIMARY KEY (id);


--
-- Name: hcc_results hcc_results_run_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hcc_results
    ADD CONSTRAINT hcc_results_run_id_key UNIQUE (run_id);


--
-- Name: learning_examples learning_examples_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learning_examples
    ADD CONSTRAINT learning_examples_pkey PRIMARY KEY (id);


--
-- Name: mdc_assignments mdc_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mdc_assignments
    ADD CONSTRAINT mdc_assignments_pkey PRIMARY KEY (id);


--
-- Name: modifier_rules modifier_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.modifier_rules
    ADD CONSTRAINT modifier_rules_pkey PRIMARY KEY (id);


--
-- Name: mue_limits mue_limits_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mue_limits
    ADD CONSTRAINT mue_limits_code_key UNIQUE (code);


--
-- Name: mue_limits mue_limits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mue_limits
    ADD CONSTRAINT mue_limits_pkey PRIMARY KEY (id);


--
-- Name: ncci_edits ncci_edits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ncci_edits
    ADD CONSTRAINT ncci_edits_pkey PRIMARY KEY (id);


--
-- Name: ontology_concepts ontology_concepts_cui_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ontology_concepts
    ADD CONSTRAINT ontology_concepts_cui_key UNIQUE (cui);


--
-- Name: ontology_concepts ontology_concepts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ontology_concepts
    ADD CONSTRAINT ontology_concepts_pkey PRIMARY KEY (id);


--
-- Name: ontology_edges ontology_edges_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ontology_edges
    ADD CONSTRAINT ontology_edges_pkey PRIMARY KEY (id);


--
-- Name: or_procedures or_procedures_pcs_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.or_procedures
    ADD CONSTRAINT or_procedures_pcs_code_key UNIQUE (pcs_code);


--
-- Name: or_procedures or_procedures_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.or_procedures
    ADD CONSTRAINT or_procedures_pkey PRIMARY KEY (id);


--
-- Name: payer_policies payer_policies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payer_policies
    ADD CONSTRAINT payer_policies_pkey PRIMARY KEY (id);


--
-- Name: qual_circumstances qual_circumstances_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.qual_circumstances
    ADD CONSTRAINT qual_circumstances_code_key UNIQUE (code);


--
-- Name: qual_circumstances qual_circumstances_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.qual_circumstances
    ADD CONSTRAINT qual_circumstances_pkey PRIMARY KEY (id);


--
-- Name: reference_codes reference_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reference_codes
    ADD CONSTRAINT reference_codes_pkey PRIMARY KEY (id);


--
-- Name: reference_codes uq_refcode; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reference_codes
    ADD CONSTRAINT uq_refcode UNIQUE (code_system, code);


--
-- Name: ix_anes_results_encounter_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_anes_results_encounter_id ON public.anes_results USING btree (encounter_id);


--
-- Name: ix_apc_results_encounter_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_apc_results_encounter_id ON public.apc_results USING btree (encounter_id);


--
-- Name: ix_audit_ledger_encounter_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_ledger_encounter_id ON public.audit_ledger USING btree (encounter_id);


--
-- Name: ix_audit_ledger_run_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_ledger_run_id ON public.audit_ledger USING btree (run_id);


--
-- Name: ix_cdi_queries_encounter_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_cdi_queries_encounter_id ON public.cdi_queries USING btree (encounter_id);


--
-- Name: ix_drg_results_encounter_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_drg_results_encounter_id ON public.drg_results USING btree (encounter_id);


--
-- Name: ix_hcc_results_encounter_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hcc_results_encounter_id ON public.hcc_results USING btree (encounter_id);


--
-- Name: ix_learning_examples_pattern_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_learning_examples_pattern_key ON public.learning_examples USING btree (pattern_key);


--
-- Name: anes_results anes_results_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anes_results
    ADD CONSTRAINT anes_results_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.coding_runs(id);


--
-- Name: apc_results apc_results_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.apc_results
    ADD CONSTRAINT apc_results_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.coding_runs(id);


--
-- Name: code_results code_results_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.code_results
    ADD CONSTRAINT code_results_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.coding_runs(id);


--
-- Name: coding_runs coding_runs_encounter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.coding_runs
    ADD CONSTRAINT coding_runs_encounter_id_fkey FOREIGN KEY (encounter_id) REFERENCES public.encounters(id);


--
-- Name: drg_results drg_results_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.drg_results
    ADD CONSTRAINT drg_results_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.coding_runs(id);


--
-- Name: hcc_results hcc_results_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hcc_results
    ADD CONSTRAINT hcc_results_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.coding_runs(id);


--
-- PostgreSQL database dump complete
--

\unrestrict URfhTffeCvEXXtbRHbBY6A5wSvplSv5as3ZIvRj2LNPhXh3dMcVkIJGtk7AbCBE

