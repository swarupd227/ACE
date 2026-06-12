import {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, BorderStyle, Table, TableRow, TableCell,
  WidthType, ShadingType, TableBorders, PageBreak,
  Header, Footer, ImageRun, TabStopPosition, TabStopType,
  convertInchesToTwip, LevelFormat, NumberFormat,
} from "docx";
import fs from "fs";

// ── Color palette ──
const NOUS_BLUE  = "1B3A5C";
const VHT_GREEN  = "2E7D32";
const ACCENT     = "1565C0";
const GRAY       = "616161";
const LIGHT_GRAY = "F5F5F5";
const WHITE      = "FFFFFF";
const BLACK      = "000000";

// ── Helpers ──
function heading(text, level = HeadingLevel.HEADING_1, opts = {}) {
  return new Paragraph({
    heading: level,
    spacing: { before: level === HeadingLevel.HEADING_1 ? 400 : 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: level === HeadingLevel.HEADING_1 ? 32 : level === HeadingLevel.HEADING_2 ? 26 : 22, color: NOUS_BLUE, font: "Calibri", ...opts })],
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120 },
    children: [new TextRun({ text, size: 21, font: "Calibri", color: BLACK, ...opts })],
  });
}

function boldPara(label, text) {
  return new Paragraph({
    spacing: { after: 100 },
    children: [
      new TextRun({ text: label, bold: true, size: 21, font: "Calibri", color: NOUS_BLUE }),
      new TextRun({ text, size: 21, font: "Calibri", color: BLACK }),
    ],
  });
}

function bullet(text, opts = {}) {
  return new Paragraph({
    bullet: { level: 0 },
    spacing: { after: 60 },
    children: [new TextRun({ text, size: 21, font: "Calibri", color: BLACK, ...opts })],
  });
}

function subBullet(text) {
  return new Paragraph({
    bullet: { level: 1 },
    spacing: { after: 40 },
    children: [new TextRun({ text, size: 20, font: "Calibri", color: GRAY })],
  });
}

function boldBullet(label, text) {
  return new Paragraph({
    bullet: { level: 0 },
    spacing: { after: 60 },
    children: [
      new TextRun({ text: label, bold: true, size: 21, font: "Calibri", color: NOUS_BLUE }),
      new TextRun({ text, size: 21, font: "Calibri", color: BLACK }),
    ],
  });
}

function talkingPoint(text) {
  return new Paragraph({
    indent: { left: convertInchesToTwip(0.4) },
    spacing: { after: 80 },
    children: [
      new TextRun({ text: "🗨 Talking Point: ", bold: true, size: 20, font: "Calibri", color: VHT_GREEN }),
      new TextRun({ text: `"${text}"`, italics: true, size: 20, font: "Calibri", color: GRAY }),
    ],
  });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function spacer(pts = 200) {
  return new Paragraph({ spacing: { before: pts, after: 0 }, children: [] });
}

function tableCell(text, opts = {}) {
  return new TableCell({
    width: opts.width ? { size: opts.width, type: WidthType.PERCENTAGE } : undefined,
    shading: opts.header ? { type: ShadingType.SOLID, color: NOUS_BLUE } : opts.shading ? { type: ShadingType.SOLID, color: opts.shading } : undefined,
    children: [new Paragraph({
      spacing: { before: 40, after: 40 },
      children: [new TextRun({
        text,
        size: opts.header ? 20 : 19,
        bold: !!opts.header,
        font: "Calibri",
        color: opts.header ? WHITE : BLACK,
      })],
    })],
  });
}

function makeTable(headers, rows) {
  const colWidth = Math.floor(100 / headers.length);
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [
      new TableRow({ children: headers.map(h => tableCell(h, { header: true, width: colWidth })) }),
      ...rows.map((row, i) => new TableRow({
        children: row.map(cell => tableCell(cell, { width: colWidth, shading: i % 2 === 1 ? LIGHT_GRAY : undefined })),
      })),
    ],
  });
}

function divider() {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: NOUS_BLUE, space: 1 } },
    children: [],
  });
}

// ── Build document ──
const doc = new Document({
  creator: "Nous Infosystems",
  title: "ACE - Autonomous Coding Engine | Demo Documentation",
  description: "Comprehensive demo documentation for ACE presentation to Vee Healthtek leadership",
  styles: {
    default: {
      document: { run: { font: "Calibri", size: 21 } },
      heading1: { run: { font: "Calibri", size: 32, bold: true, color: NOUS_BLUE } },
      heading2: { run: { font: "Calibri", size: 26, bold: true, color: NOUS_BLUE } },
      heading3: { run: { font: "Calibri", size: 22, bold: true, color: ACCENT } },
    },
  },
  sections: [{
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "ACE — Autonomous Coding Engine | Confidential", size: 16, color: GRAY, font: "Calibri", italics: true })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Nous Infosystems × Vee Healthtek | Confidential — Not for redistribution", size: 14, color: GRAY, font: "Calibri" })],
        })],
      }),
    },
    children: [

      // ════════════════════════════════════════════════════════════════
      // TITLE PAGE
      // ════════════════════════════════════════════════════════════════
      spacer(1200),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ACE", size: 72, bold: true, font: "Calibri", color: NOUS_BLUE })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "Autonomous Coding Engine", size: 40, font: "Calibri", color: ACCENT })] }),
      spacer(100),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Comprehensive Demo Documentation", size: 28, font: "Calibri", color: GRAY })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Client Presentation Guide", size: 24, font: "Calibri", color: GRAY })] }),
      spacer(300),
      divider(),
      spacer(100),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Prepared by Nous Infosystems for Vee Healthtek", size: 22, font: "Calibri", color: NOUS_BLUE })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "June 2026 | Version 1.0", size: 20, font: "Calibri", color: GRAY })] }),
      spacer(100),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "Audience: ", bold: true, size: 20, font: "Calibri", color: NOUS_BLUE }),
        new TextRun({ text: "Vee Healthtek Leadership & NousSosAll AI Partner Team", size: 20, font: "Calibri", color: GRAY }),
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [
        new TextRun({ text: "Stakeholders: ", bold: true, size: 20, font: "Calibri", color: NOUS_BLUE }),
        new TextRun({ text: "Amrish Kumar (CTAIO), Michelle Castillon (CPTO), Murali (Ops), JC (Data Science)", size: 20, font: "Calibri", color: GRAY }),
      ]}),

      pageBreak(),

      // ════════════════════════════════════════════════════════════════
      // TABLE OF CONTENTS
      // ════════════════════════════════════════════════════════════════
      heading("Table of Contents"),
      divider(),
      ...[
        "1.  Executive Summary & Application Overview",
        "2.  Technical Architecture Summary",
        "3.  The Agentic Pipeline (Stage 0–5)",
        "4.  Feature Walkthrough — Operational Screens",
        "    4.1  Worklist & Three-Lane Queue",
        "    4.2  Encounter Detail & Citation Engine",
        "    4.3  Control Tower & Workforce Management",
        "    4.4  CDI / Physician Queries",
        "    4.5  Integrations & Ingestion",
        "5.  Feature Walkthrough — Intelligence & Learning",
        "    5.1  Closed-Loop Learning",
        "    5.2  Evaluation Harness",
        "    5.3  Performance Dashboard",
        "6.  Feature Walkthrough — Admin & Configuration",
        "    6.1  Policy & Knowledge Admin (KG Builder)",
        "    6.2  Admin Configuration Panel",
        "    6.3  Reference Data Management",
        "    6.4  Role-Based Access Control (RBAC)",
        "    6.5  Audit Trail & Governance",
        "7.  Feature Walkthrough — Payment Models",
        "    7.1  MS-DRG Grouper (Inpatient)",
        "    7.2  CMS-HCC Risk Adjustment (RAF)",
        "    7.3  Anesthesia Unit Calculation",
        "    7.4  APC / OPPS (Facility Pricing)",
        "8.  Demo Flow — Client Presentation Script",
        "9.  The Nous Defensibility Moat",
        "10. Proposal Summary & Timeline",
        "11. Appendix — Tech Stack & Deployment",
      ].map(t => new Paragraph({
        spacing: { after: 40 },
        children: [new TextRun({ text: t, size: 21, font: "Calibri", color: t.startsWith("    ") ? GRAY : NOUS_BLUE, bold: !t.startsWith("    ") })],
      })),

      pageBreak(),

      // ════════════════════════════════════════════════════════════════
      // SECTION 1: EXECUTIVE SUMMARY
      // ════════════════════════════════════════════════════════════════
      heading("1. Executive Summary & Application Overview"),
      divider(),

      heading("What is ACE?", HeadingLevel.HEADING_2),
      para("ACE (Autonomous Coding Engine) is a self-contained, agentic medical coding application built by Nous Infosystems for Vee Healthtek. It is designed to function as the engine inside Vee Healthtek's RevAmp Coding Studio, automating the translation of clinical documentation into audit-defensible medical codes."),
      spacer(80),

      heading("What It Does", HeadingLevel.HEADING_3),
      bullet("Translates clinical documentation (physician notes, radiology reports, operative notes, ED records) into standardized medical codes: ICD-10-CM (diagnoses), CPT (procedures), HCPCS (supplies/services), and modifiers."),
      bullet("Routes each coded chart into one of three lanes — Straight-Through Billing (STB), QA Review, or Manual Coding — based on a calibrated 4-factor confidence score."),
      bullet("Proves every coding decision with a complete evidence chain: chart-line citations, guideline references, and deterministic validation gate results."),
      bullet("Provides a complete, audit-defensible trail for every decision — ready for RAC audits, payer reviews, and compliance requirements."),
      spacer(80),

      heading("Why It Matters — Business Value", HeadingLevel.HEADING_3),
      makeTable(
        ["Metric", "Target", "Impact"],
        [
          ["Coding Accuracy", "≥ 90% (progressive ramp)", "Reduced denials, fewer rework cycles"],
          ["STB / Automation Rate", "≥ 80% of charts", "Massive reduction in manual coding labor"],
          ["Manual Effort Reduction", "≥ 30%", "Coders focus on complex cases, not routine work"],
          ["Turnaround Time", "10–15% improvement", "Faster billing cycles, improved cash flow"],
          ["Defensibility", "100% audit trail", "Every code has citation + guideline + model version"],
        ],
      ),
      spacer(80),

      heading("Multi-Specialty Coverage", HeadingLevel.HEADING_3),
      para("ACE currently supports 16 specialties through a single \"Specialty Accelerator\" — new specialties are onboarded through configuration and content, not engineering rebuilds:"),
      ...[
        "Radiology (anchor specialty — X-ray, CT, MRI, Ultrasound)",
        "Evaluation & Management (E&M) — office visits, consultations",
        "Emergency Department (ED) — including critical care",
        "Pathology — lab, cytology, surgical pathology",
        "Surgical — general, orthopedic procedures",
        "Cardiology — echocardiograms, ECGs, catheterization",
        "Orthopedics — joint replacement, injection",
        "OB/GYN — prenatal, delivery, gynecological",
        "GI / Endoscopy — colonoscopy, EGD",
        "Dermatology — biopsies, lesion removal",
        "Urology — cystoscopy, lithotripsy",
        "Anesthesia — unit-based payment calculation",
        "Ophthalmology — cataract, retinal procedures",
        "ENT — sinus, tonsillectomy, audiometry",
        "Inpatient (MS-DRG) — diagnosis-related group payment",
        "HCC / Risk Adjustment — RAF scoring for MA plans",
      ].map(s => bullet(s)),

      pageBreak(),

      // ════════════════════════════════════════════════════════════════
      // SECTION 2: TECHNICAL ARCHITECTURE
      // ════════════════════════════════════════════════════════════════
      heading("2. Technical Architecture Summary"),
      divider(),

      para("This section explains the technical architecture in plain language for both technical and business stakeholders."),
      spacer(80),

      heading("High-Level Architecture", HeadingLevel.HEADING_2),
      para("ACE is a three-tier web application running entirely in Docker containers:"),
      spacer(40),
      makeTable(
        ["Layer", "Technology", "What It Does"],
        [
          ["Frontend (User Interface)", "React + TypeScript + Tailwind CSS", "The screens coders, auditors, and admins interact with — the worklist, encounter detail, dashboards, and configuration panels"],
          ["Backend (API + AI Pipeline)", "FastAPI (Python) + SQLAlchemy", "The brain — processes charts through a 5-stage AI pipeline, runs validation gates, manages all business logic and AI model calls"],
          ["Database", "PostgreSQL + pgvector", "Stores everything: encounter data, reference code tables (ICD-10/CPT/HCPCS), the knowledge graph, audit logs, evaluation results, and learning exemplars"],
          ["AI Models", "Anthropic Claude (Sonnet/Opus)", "The reasoning engine — analyzes clinical text, extracts entities, and generates cited codes. Also supports Azure OpenAI, OpenAI, vLLM, and Ollama"],
          ["Web Server", "Nginx", "Serves the frontend and routes API calls to the backend"],
        ],
      ),
      spacer(80),

      heading("How Data Flows", HeadingLevel.HEADING_2),
      para("1. Clinical documentation arrives from EHR/PMS systems (Practice Admin, eClinicalWorks, Cerner) via FHIR, HL7, EDI, or file upload."),
      para("2. The chart enters the agentic pipeline (Stage 0-5), where AI and deterministic rules work together."),
      para("3. The pipeline produces coded results with citations, confidence scores, and validation gate outcomes."),
      para("4. Charts are routed to the appropriate lane (STB / QA / Manual) based on calibrated confidence."),
      para("5. Human coders interact via the worklist — accepting, overriding, or escalating coded charts."),
      para("6. Corrections feed back into the system as learning exemplars, improving future coding."),
      spacer(80),

      heading("Key Architectural Decisions", HeadingLevel.HEADING_2),
      boldBullet("Citation-as-Gate: ", "No code is emitted without chart-line evidence and a guideline reference. This is structural, not just a prompt instruction."),
      boldBullet("Deterministic Where Determinism Belongs: ", "Code existence, NCCI bundling, MUE limits, modifier validation, and sex/age edits are all rule-engine lookups — LLMs are not used for exhaustive lookups."),
      boldBullet("Honest Failure: ", "If no LLM is reachable, every chart routes to the manual queue with reason 'LLM_UNAVAILABLE'. The system never fabricates codes."),
      boldBullet("Graph-RAG Grounding: ", "The coding agent may only emit codes that retrieval surfaces from the knowledge graph. Hallucination control is a structural property, not a prompt hope."),
      boldBullet("PII Masking: ", "Direct identifiers (name, MRN, DOB, SSN, phone) are masked before any model call. Age, sex, and dates of service are preserved because coding requires them."),
      boldBullet("Append-Only Audit: ", "Every decision is logged with timestamps, actor, model version, and full context — replayable and tamper-evident."),

      pageBreak(),

      // ════════════════════════════════════════════════════════════════
      // SECTION 3: THE AGENTIC PIPELINE
      // ════════════════════════════════════════════════════════════════
      heading("3. The Agentic Pipeline (Stage 0–5)"),
      divider(),

      para("Every chart passes through a 5-stage pipeline that combines AI reasoning with deterministic rule engines. Each stage can veto or downgrade a chart — failures route to human review, never to auto-billing."),
      spacer(80),

      heading("Stage 0 — Eligibility Gate", HeadingLevel.HEADING_2),
      boldPara("Type: ", "Deterministic (no AI model involved)"),
      boldPara("Purpose: ", "Determine if the chart is eligible for autonomous coding before any AI processing begins."),
      para("Checks performed:"),
      bullet("Minimum document length (configurable — rejects blank or stub charts)"),
      bullet("Approved specialty (must be in the enabled specialty list)"),
      bullet("Exclusion flags: interventional radiology, trauma, incomplete documentation, addendum pending"),
      bullet("Required documentation present"),
      talkingPoint("Charts that shouldn't be coded autonomously are caught before any AI costs are incurred."),
      spacer(80),

      heading("Stage 1 — Document Conditioning (LLM)", HeadingLevel.HEADING_2),
      boldPara("Type: ", "AI-powered (Claude Sonnet)"),
      boldPara("Purpose: ", "Understand the document structure and flag quality issues before clinical extraction."),
      para("What it does:"),
      bullet("Section identification (HPI, Assessment/Plan, Findings, Impression, etc.)"),
      bullet("Copy-forward detection — identifies verbatim carry-over from prior notes"),
      bullet("Contradiction detection — flags when HPI and A&P conflict"),
      bullet("Unsigned note detection"),
      bullet("OCR artifact identification"),
      bullet("Addendum pending flags"),
      bullet("Generates a structured chart summary for downstream stages"),
      talkingPoint("This is where real-world document messiness is caught — copy-forward, unsigned notes, OCR artifacts — before the system tries to code."),
      spacer(80),

      heading("Stage 2 — Clinical Entity Extraction (LLM)", HeadingLevel.HEADING_2),
      boldPara("Type: ", "AI-powered (Claude Sonnet)"),
      boldPara("Purpose: ", "Extract structured clinical entities from the narrative text."),
      para("Extracted entities:"),
      bullet("Diagnoses with laterality, certainty, and temporality"),
      bullet("Procedures with specifics (contrast type, view count, approach)"),
      bullet("E&M factors: complexity, risk, data reviewed, MDM elements"),
      bullet("Encounter type, place of service"),
      bullet("Negations and rule-outs (critical for preventing upcoding)"),
      talkingPoint("The AI extracts exactly what coders extract — laterality, contrast, negation — but with structured schema enforcement, so nothing is missed."),
      spacer(80),

      heading("Graph-RAG Retrieval (Between Stage 2 and 3)", HeadingLevel.HEADING_2),
      boldPara("Type: ", "Deterministic retrieval over knowledge graph"),
      boldPara("Purpose: ", "Ground the coding agent in real reference data — codes, guidelines, policies, and ontology."),
      para("What is retrieved:"),
      bullet("ICD-10-CM candidate codes (ranked by lexical match to extracted entities)"),
      bullet("CPT/HCPCS procedure candidates"),
      bullet("Guideline excerpts (from indexed ICD-10 Official Guidelines)"),
      bullet("Payer-specific policies (Anthem, Cigna, Medicare LCD/NCD rules)"),
      bullet("Ontology paths (concept relationships: finding_site, is_a, associated_with)"),
      bullet("Learned corrections (from prior coder overrides on similar charts)"),
      talkingPoint("The agent can only propose codes that this retrieval surfaces. This is the structural hallucination control — not a prompt instruction, but an architectural constraint."),
      spacer(80),

      heading("Stage 3 — Cited Code Generation (LLM)", HeadingLevel.HEADING_2),
      boldPara("Type: ", "AI-powered (Claude Sonnet; Opus for complex cases)"),
      boldPara("Purpose: ", "Generate the actual code assignments with mandatory citations."),
      para("Key requirements:"),
      bullet("Every code MUST cite specific chart line numbers as supporting evidence"),
      bullet("Every code MUST reference a coding guideline"),
      bullet("Schema-bound structured output (the model cannot return free-form text)"),
      bullet("Self-consistency on hard charts: N independent samples, majority vote"),
      bullet("Per-code confidence breakdown across 4 factors"),
      spacer(40),

      heading("Stage 3b — Citation Verification (Deterministic)", HeadingLevel.HEADING_3),
      boldPara("Purpose: ", "Verify that every cited chart line actually contains the claimed supporting text."),
      bullet("If a code's citation doesn't exist at the cited line numbers, the code is rejected"),
      bullet("Prevents fabricated documentation — a critical defense against AI hallucination"),
      talkingPoint("This is the 'show your work' requirement, machine-verified. A code without real evidence in the chart is rejected, period."),
      spacer(80),

      heading("Stage 4 — Validation & Compliance Gates (Deterministic)", HeadingLevel.HEADING_2),
      boldPara("Type: ", "Pure rule-engine (no AI model involved)"),
      boldPara("Purpose: ", "Apply every compliance rule in the coding rulebook — deterministically."),
      spacer(40),
      makeTable(
        ["Gate", "What It Checks", "Why It Matters"],
        [
          ["Code Existence", "Is this a real, effective-dated code?", "Catches fabricated or expired codes"],
          ["Specificity", "Is a more specific child code required?", "Prevents non-billable parent codes when specificity exists"],
          ["Sex / Age Edits", "Is this code valid for the patient's demographics?", "Pediatric codes on adults, male codes on females — caught"],
          ["Modifier Validity", "Is the modifier real and applicable?", "Invalid modifiers → claim denial"],
          ["NCCI Bundling", "Are these procedures bundled per CMS rules?", "The #1 source of denials — caught deterministically"],
          ["MUE Limits", "Are units within medically unlikely edit limits?", "Excessive units → audit flag"],
          ["Medical Necessity (LCD/NCD)", "Does the payer cover this code for this diagnosis?", "Payer-specific necessity from the knowledge graph"],
          ["Place of Service", "Is the POS consistent with the codes?", "Facility vs professional alignment"],
          ["Sequencing (UHDDS)", "Is the principal diagnosis correctly sequenced?", "Inpatient coding rules"],
          ["Critical Care", "Is this a critical-care code?", "Always routes to human review regardless of confidence"],
        ],
      ),
      talkingPoint("These are the rules your coders carry in their heads. In ACE, they're enforced by a rule engine — consistently, on every chart, at machine speed."),
      spacer(80),

      heading("Stage 5 — Calibration & Routing", HeadingLevel.HEADING_2),
      boldPara("Type: ", "Deterministic calculation + routing decision"),
      boldPara("Purpose: ", "Compute a calibrated confidence score and route the chart to the appropriate lane."),
      spacer(40),
      heading("The 4-Factor Confidence Model", HeadingLevel.HEADING_3),
      makeTable(
        ["Factor", "Weight", "What It Measures"],
        [
          ["AI Model Certainty", "40%", "Self-reported confidence × self-consistency agreement across multiple samples"],
          ["Clinical Document Match", "25%", "Quality and coverage of chart-line citations supporting each code"],
          ["Rule Engine Validation", "25%", "Gate pass ratio (how many of the 10 deterministic gates passed)"],
          ["Historical Patterns", "10%", "Alignment with gold standard exemplars and learned corrections"],
        ],
      ),
      spacer(40),
      heading("Routing Thresholds (Admin-Configurable)", HeadingLevel.HEADING_3),
      makeTable(
        ["Confidence Range", "Lane", "What Happens"],
        [
          ["≥ 0.90", "Straight-Through Billing (STB)", "Auto-billed with audit trail. No human touch required."],
          ["0.75 – 0.89", "QA Review", "Presented to a QA auditor with AI recommendations for fast review."],
          ["< 0.75", "Manual Coding", "Routed to a human coder for full manual coding."],
        ],
      ),
      spacer(40),
      heading("Bounded Autonomy Rules", HeadingLevel.HEADING_3),
      para("Even if confidence is high, certain chart types always route to human review:"),
      bullet("Critical care codes (99291, 99292) — highest-dollar, highest-scrutiny"),
      bullet("Ambiguous or rule-out diagnoses"),
      bullet("NCCI bundling overrides requiring modifier justification"),
      talkingPoint("Bounded autonomy is the economic insight: the win is volume on routine charts, not risking the hardest cases. High-confidence critical care still gets human eyes."),

      pageBreak(),

      // ════════════════════════════════════════════════════════════════
      // SECTION 4: OPERATIONAL SCREENS
      // ════════════════════════════════════════════════════════════════
      heading("4. Feature Walkthrough — Operational Screens"),
      divider(),

      // 4.1 WORKLIST
      heading("4.1 Worklist & Three-Lane Queue", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Worklist (landing page)"),
      boldPara("Audience: ", "Coders, QA Auditors, Supervisors"),
      spacer(40),

      heading("What It Shows", HeadingLevel.HEADING_3),
      bullet("Table of all encounters with columns: Patient, MRN, Specialty, Payer, DOS, Confidence, Lane, Received Time"),
      bullet("Three-lane tabs: ALL | STB | QA | MANUAL — with count and rate for each"),
      bullet("Filters: by specialty, lane, payer, date-of-service range, confidence range"),
      bullet("Sort: by any column (patient name, MRN, specialty, payer, DOS, confidence, lane, received time)"),
      bullet("Summary statistics tiles: Total Charts, STB Count & Rate, QA Count, Manual Count"),
      spacer(40),

      heading("Step-by-Step Walkthrough", HeadingLevel.HEADING_3),
      boldBullet("Step 1: ", "Open the application — the Worklist is the default landing page."),
      boldBullet("Step 2: ", "Observe the three-lane tabs showing the distribution of charts across STB, QA, and Manual queues."),
      boldBullet("Step 3: ", "Use filters to narrow by specialty (e.g., Radiology) or lane (e.g., STB only)."),
      boldBullet("Step 4: ", "Click 'Code' on an uncoded chart — the Agent Console opens and streams the live pipeline run."),
      boldBullet("Step 5: ", "Watch the agentic pipeline execute in real time: Eligibility → Conditioning → Extraction → RAG → Coding → Validation → Routing."),
      boldBullet("Step 6: ", "Use 'Run Autonomous Coding' for batch processing of all uncoded charts."),
      talkingPoint("This is the operating picture your coders and managers live in. Every chart, every status, every confidence score — at a glance."),
      spacer(80),

      // 4.2 ENCOUNTER DETAIL
      heading("4.2 Encounter Detail & Citation Engine", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Encounter Detail (click any chart from the Worklist)"),
      boldPara("Audience: ", "Coders, QA Auditors"),
      spacer(40),

      heading("What It Shows", HeadingLevel.HEADING_3),
      bullet("Full chart text with numbered lines"),
      bullet("Coded results panel: each code with 4-factor confidence breakdown"),
      bullet("Citation highlights: hover a code → the supporting chart lines light up"),
      bullet("Guideline citations: the specific coding guideline referenced for each code"),
      bullet("Validation gate results: per-code pass/fail for all 10 deterministic gates"),
      bullet("Pipeline trace: Stage 0–5 execution log with latency and token counts"),
      bullet("Knowledge used: the specific codes, policies, and ontology paths that informed this chart"),
      bullet("Audit packet: downloadable evidence chain for RAC/payer audit defense"),
      spacer(40),

      heading("Human Actions Available", HeadingLevel.HEADING_3),
      boldBullet("Accept: ", "Coder confirms the AI-generated code is correct."),
      boldBullet("Override with Reason: ", "Coder provides a different code and explains why — captured as a learning exemplar."),
      boldBullet("Reassign Queue: ", "Move the chart between STB ↔ QA ↔ Manual (e.g., spot audit: STB → QA)."),
      boldBullet("Escalate: ", "Route to a senior coder or CDI specialist for complex cases."),
      boldBullet("Revert to AI: ", "Undo all human edits and restore the original AI recommendation."),
      talkingPoint("Every code points at the words that justify it. Hover a code, and the chart text lights up. This is your RAC audit defense, generated automatically."),
      spacer(80),

      // 4.3 CONTROL TOWER
      heading("4.3 Control Tower & Workforce Management", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Control Tower"),
      boldPara("Audience: ", "Supervisors, Operations Managers"),
      spacer(40),

      heading("What It Shows", HeadingLevel.HEADING_3),
      bullet("Live work queues: STB / QA / Manual / Escalated / CDI — with real-time counts"),
      bullet("SLA aging: each chart shows how long it has been in the queue, with breach flags for overdue items"),
      bullet("Per-item detail: patient, MRN, specialty, payer, priority, assigned coder, SLA status"),
      bullet("Workforce roster: available coders/auditors and their current load"),
      spacer(40),

      heading("Step-by-Step Walkthrough", HeadingLevel.HEADING_3),
      boldBullet("Step 1: ", "Open Control Tower from the sidebar navigation."),
      boldBullet("Step 2: ", "Observe live queue counts and SLA status across all lanes."),
      boldBullet("Step 3: ", "Click a queue to expand and see individual items with aging."),
      boldBullet("Step 4: ", "Select charts and assign them to a specific coder or auditor from the roster."),
      boldBullet("Step 5: ", "Identify SLA breaches (red flags) and reassign or escalate as needed."),
      talkingPoint("This is the manager's operating view — live queues, SLA, workforce assignment. Your ops team runs coding operations from this screen."),
      spacer(80),

      // 4.4 CDI
      heading("4.4 CDI / Physician Queries", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "CDI / Physician Queries"),
      boldPara("Audience: ", "CDI Specialists, Physicians"),
      spacer(40),

      heading("What It Does", HeadingLevel.HEADING_3),
      para("When ACE detects that a chart could be coded more specifically with additional clinical documentation, it drafts a compliant, non-leading physician query. This is the CDI (Clinical Documentation Improvement) workflow."),
      spacer(40),

      heading("Step-by-Step Walkthrough", HeadingLevel.HEADING_3),
      boldBullet("Step 1: ", "Open an encounter where documentation is ambiguous (e.g., EM20002 — anemia E&M chart)."),
      boldBullet("Step 2: ", "Note the initial code: D64.9 (anemia, unspecified) — the type of anemia isn't documented."),
      boldBullet("Step 3: ", "Click 'Scan for CDI Opportunities' — the CDI Agent console streams live as it reviews documentation, checks codes, and drafts a query."),
      boldBullet("Step 4: ", "Review the drafted query: it states the clinical indicators (Hgb 8.2, iron started), offers options including 'Unable to determine', and does NOT lead the physician."),
      boldBullet("Step 5: ", "Select the physician's answer (e.g., 'Iron deficiency anemia') — the encounter automatically re-codes to D50.9 (iron-deficiency anemia), more specific and audit-defensible."),
      talkingPoint("This is the CDI revenue and integrity story — AI as a co-pilot. It drafts the query, the physician decides, and coding updates on the answer. Compliant, non-leading, automated."),
      spacer(80),

      // 4.5 INTEGRATIONS
      heading("4.5 Integrations & Ingestion", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Integrations & Ingestion"),
      boldPara("Audience: ", "IT, Operations"),
      spacer(40),

      heading("What It Shows", HeadingLevel.HEADING_3),
      bullet("Connected source systems: Practice Admin (VHT-owned PMS), eClinicalWorks, Cerner"),
      bullet("Supported channels: FHIR R4, HL7 v2, EDI 837, SFTP, REST API"),
      bullet("Live ingestion: load a sample report → Ingest into queue → it appears in the Worklist"),
      bullet("Document upload: supports scanned charts (PDF, images) — the model transcribes via vision OCR"),
      bullet("API documentation: sample JSON shapes, endpoint references"),
      spacer(40),

      heading("Step-by-Step Walkthrough", HeadingLevel.HEADING_3),
      boldBullet("Step 1: ", "Open Integrations from the sidebar."),
      boldBullet("Step 2: ", "Show the connected source systems and channel types."),
      boldBullet("Step 3: ", "Load a sample JSON encounter → click Ingest → the chart appears live in the Worklist."),
      boldBullet("Step 4: ", "Upload a scanned document (PDF/image) → watch the model transcribe it via vision OCR → the extracted text appears → run coding → same pipeline, same citations."),
      talkingPoint("Charts arrive from the EHR/PMS — text or scanned documents. The connectors are simulated for demo, but the ingest pipeline is real. Production adds Azure Document Intelligence for bulk OCR."),

      pageBreak(),

      // ════════════════════════════════════════════════════════════════
      // SECTION 5: INTELLIGENCE & LEARNING
      // ════════════════════════════════════════════════════════════════
      heading("5. Feature Walkthrough — Intelligence & Learning"),
      divider(),

      // 5.1 CLOSED-LOOP LEARNING
      heading("5.1 Closed-Loop Learning", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Closed-Loop Learning"),
      boldPara("Audience: ", "Coders, QA Auditors, Data Science"),
      spacer(40),

      heading("How It Works", HeadingLevel.HEADING_3),
      para("When a coder overrides an AI-generated code and provides a reason, that correction is captured as a learning exemplar. On the next similar chart, the system's Graph-RAG retrieval surfaces that correction, visibly shifting the coding output toward the corrected behavior."),
      spacer(40),

      heading("Live Demo Flow — The Money Moment", HeadingLevel.HEADING_3),
      boldBullet("Step 1: ", "Open RAD10009 ('learning loop A'). Note the abdominal-pain code the model picked."),
      boldBullet("Step 2: ", "Click Override, enter a client-specific preference (e.g., correct code + reason: 'Client policy: use R10.84 for abdominal-pain studies'). Submit."),
      boldBullet("Step 3: ", "Open the Closed-Loop Learning page — the correction now appears, keyed to the chart pattern."),
      boldBullet("Step 4: ", "Go to RAD10010 ('learning loop B'), click Code → it now adopts the corrected code with a 'learned' badge and higher historical confidence."),
      talkingPoint("Corrections don't evaporate. In production, this runs as a 24–48 hour batch into the SLM fine-tune pipeline. The system gets smarter with every override."),
      spacer(80),

      // 5.2 EVALUATION HARNESS
      heading("5.2 Evaluation Harness", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Evaluation Harness"),
      boldPara("Audience: ", "Data Science, QA, Leadership"),
      spacer(40),

      heading("What It Does", HeadingLevel.HEADING_3),
      para("The evaluation harness runs the live coding pipeline against a frozen set of 'golden' cases with independently adjudicated truth values. This provides honest, reproducible accuracy measurement."),
      spacer(40),

      heading("Metrics Reported", HeadingLevel.HEADING_3),
      makeTable(
        ["Metric", "What It Measures"],
        [
          ["Code Existence", "Did the model produce real, effective-dated codes?"],
          ["Top-1 Accuracy", "Was the first-choice code correct?"],
          ["Specificity", "Did it code to the most specific level supported by documentation?"],
          ["Modifier Accuracy", "Were modifiers applied correctly?"],
          ["DRG Accuracy", "For inpatient: was the DRG correct?"],
          ["Citation Validity", "Were chart-line citations real and accurate?"],
          ["ECE (Calibration Error)", "Does the confidence score match actual accuracy?"],
          ["STB Share", "What percentage of charts achieved straight-through billing?"],
          ["Adversarial", "Did it resist upcoding, fabrication, and ambiguous diagnoses?"],
        ],
      ),
      spacer(40),
      heading("Key Feature: Honest Reporting", HeadingLevel.HEADING_3),
      para("Accuracy is reported alongside the inter-rater reliability (IRR) ceiling — the agreement rate among human coders on the same cases. This prevents vanity metrics: if human coders agree 92% of the time, claiming 95% AI accuracy would be suspect."),
      talkingPoint("We never claim to beat the laws of inter-coder agreement. We report honestly. This is what survives a CTO's scrutiny and a payer audit."),
      spacer(80),

      // 5.3 DASHBOARD
      heading("5.3 Performance Dashboard", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Performance Dashboard"),
      boldPara("Audience: ", "Leadership, Operations, QA"),
      spacer(40),

      heading("KPIs Displayed", HeadingLevel.HEADING_3),
      bullet("Total charts processed / coded / eligible"),
      bullet("STB rate (percentage achieving straight-through billing)"),
      bullet("Calibrated accuracy"),
      bullet("Manual effort reduction (coder-minutes saved)"),
      bullet("Turnaround time reduction (manual baseline vs AI-assisted)"),
      bullet("Exception rate"),
      spacer(40),
      heading("Additional Views", HeadingLevel.HEADING_3),
      bullet("By-Specialty Breakdown: table of metrics per specialty"),
      bullet("Model Performance: active model, token usage, API calls, latency (p95), override rate"),
      bullet("By-Model Comparison: if multiple models are used, compare STB%, latency, tokens"),
      bullet("Maturity Pathway: Foundation → Scaling → Approaching → Autonomous (target ≥ 80% STB)"),
      talkingPoint("This is the leadership view — one screen, all KPIs. The maturity pathway shows exactly where you are on the journey to autonomous coding."),

      pageBreak(),

      // ════════════════════════════════════════════════════════════════
      // SECTION 6: ADMIN & CONFIGURATION
      // ════════════════════════════════════════════════════════════════
      heading("6. Feature Walkthrough — Admin & Configuration"),
      divider(),

      // 6.1 KG BUILDER
      heading("6.1 Policy & Knowledge Admin (KG Builder)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Policy & Knowledge Admin"),
      boldPara("Audience: ", "Admins, Coding Directors, Data Science"),
      spacer(40),

      heading("Sub-Sections", HeadingLevel.HEADING_3),

      boldBullet("Payer Policies: ", "CRUD editor for payer-specific rules (Anthem, Cigna, Medicare). Fields: payer, code, policy ID, medical necessity rules, prior-auth requirements, modifier preferences, covered diagnoses. These policies drive the medical necessity gate on every coding run."),
      spacer(40),
      boldBullet("KG Builder (Knowledge Graph): ", "Interactive ontology editor. Add/edit/delete medical concepts (e.g., 'Pulmonary embolism' — semantic type: Disease or Syndrome), map them to ICD-10/CPT codes, draw relationships (is_a, finding_site, associated_with). Changes are immediately available to Graph-RAG on the next coding run."),
      spacer(40),
      boldBullet("Coding Guidelines: ", "Add/edit indexed guideline excerpts (source, section, specialty, text). These are retrieved by Graph-RAG and used for citation verification. Your coding rules, governed in one place."),
      spacer(40),
      boldBullet("Explore Graph: ", "Interactive Cytoscape force-directed visualization of the ontology. Search, zoom, drag, click nodes to inspect relationships."),
      spacer(40),
      boldBullet("Data Sources: ", "Shows provenance — what's real public-domain CMS data, what's demo placeholder (CPT), what's curated."),
      spacer(40),

      heading("Live Demo Flow", HeadingLevel.HEADING_3),
      boldBullet("Step 1: ", "Open KG Builder. Click 'Add concept' → enter 'Pulmonary embolism' (semantic type: Disease or Syndrome)."),
      boldBullet("Step 2: ", "Map it to ICD10CM:I26.99 and CPT:71275. Create."),
      boldBullet("Step 3: ", "Add a relationship: Pulmonary embolism → finding_site → Lung."),
      boldBullet("Step 4: ", "Switch to Explore Graph — the new node is already visible in the interactive graph."),
      talkingPoint("The ontology isn't a picture — it's editable, and the agent reads it on every run. This is how a client curates the knowledge graph without engineering. Production swaps in licensed SNOMED CT / UMLS at the same shape."),
      spacer(80),

      // 6.2 ADMIN CONFIG
      heading("6.2 Admin Configuration Panel", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Admin → Configuration"),
      boldPara("Audience: ", "Admins, Platform Operators"),
      spacer(40),

      heading("Configurable Areas", HeadingLevel.HEADING_3),
      makeTable(
        ["Configuration Area", "What It Controls", "Example"],
        [
          ["Routing & Calibration", "STB/QA confidence thresholds", "Move STB threshold from 0.90 to 0.95 for tighter control"],
          ["Confidence Weights", "The 4-factor weight distribution", "Increase rule-engine weight from 0.25 to 0.30"],
          ["Bounded Autonomy", "Hard rules for human-required cases", "Toggle critical care always-to-human on/off"],
          ["Eligibility", "Minimum doc length, exclusion flags", "Raise min_doc_chars from 200 to 500"],
          ["SLA Targets", "Per-lane turnaround time targets", "STB: 180min, QA: 480min, Manual: 1440min"],
          ["Specialty Accelerator", "Enable/disable specialties, model tier", "Enable Ophthalmology, set to Sonnet tier"],
          ["Users & Roster", "Coder/auditor assignments", "Add a new QA auditor to the roster"],
          ["Connectors", "Toggle PMS/EHR feeds on/off", "Enable eClinicalWorks integration"],
          ["Reasoning Model", "LLM provider, model, endpoint", "Switch from Anthropic to Azure OpenAI"],
          ["Privacy", "PII masking toggles", "Mask SSN, phone; keep age, sex"],
        ],
      ),
      talkingPoint("Every threshold is a setting, not a code change. Your admins tune the platform — no engineering ticket, no redeploy."),
      spacer(80),

      // 6.3 REFERENCE DATA
      heading("6.3 Reference Data Management", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Policy & Knowledge Admin → Reference Data"),
      boldPara("Audience: ", "Admins, Coding Directors"),
      spacer(40),
      para("Full CRUD management for the data tables that drive the deterministic validation gates:"),
      boldBullet("Code Sets: ", "ICD-10-CM, CPT, HCPCS — add/edit/delete codes with effective dates, descriptions, billable flags, sex/age restrictions."),
      boldBullet("NCCI Bundling Edits: ", "Procedure-to-procedure edits that drive the bundling gate. Add a new edit and it's enforced on the next coding run."),
      boldBullet("MUE Limits: ", "Medically unlikely edits — maximum units per code per day."),
      boldBullet("Modifier Rules: ", "Modifier validity — which modifiers are real and when they apply."),
      talkingPoint("These aren't a static reference dump — they drive the deterministic validation gates on the next run. Add an NCCI edit and it catches bundling violations immediately."),
      spacer(80),

      // 6.4 RBAC
      heading("6.4 Role-Based Access Control (RBAC)", HeadingLevel.HEADING_2),
      para("ACE implements role-based access that controls both navigation and action buttons:"),
      spacer(40),
      makeTable(
        ["Role", "Can See", "Can Do"],
        [
          ["Admin", "Everything", "All actions including config, policy, KG, integrations"],
          ["Coder", "Worklist, CDI, Dashboard", "Run coding, override codes, escalate"],
          ["QA Auditor", "Worklist (view-only), Control Tower", "Override, reassign, rollback — cannot run coding"],
          ["CDI Specialist", "CDI queue", "Respond to physician queries — coding actions gated"],
          ["Supervisor", "Control Tower, Dashboards", "Assign work, reassign, rollback"],
        ],
      ),
      spacer(40),
      para("In the demo, roles are switchable via the top-bar Role dropdown. In production, roles map to SSO groups with tenant scoping."),
      talkingPoint("Navigation AND every action button respect the role. Your compliance team asked who can do what — here it is, enforced in the application."),
      spacer(80),

      // 6.5 AUDIT
      heading("6.5 Audit Trail & Governance", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Audit Log"),
      boldPara("Audience: ", "Compliance, QA, Leadership"),
      spacer(40),
      para("ACE maintains two types of audit trails:"),
      boldBullet("Coding Audit: ", "Per-encounter, per-code: every stage of the pipeline, every gate result, every human action (accept, override, reassign, escalate, rollback), with timestamps, actor, and model version."),
      boldBullet("Governance Audit: ", "Append-only change log for all admin actions: config changes, policy edits, knowledge graph edits, guideline changes, reference data updates, golden-set changes. Who (by role), when, what area, action, and target."),
      spacer(40),
      para("Both audit trails are:"),
      bullet("Append-only (tamper-resistant)"),
      bullet("Filterable by source, category, actor, date range"),
      bullet("Exportable as audit packets"),
      bullet("Include model version for reproducibility"),
      talkingPoint("This is your RAC-audit defense, generated automatically. Every decision is replayable with the same chart, model version, and reference data."),

      pageBreak(),

      // ════════════════════════════════════════════════════════════════
      // SECTION 7: PAYMENT MODELS
      // ════════════════════════════════════════════════════════════════
      heading("7. Feature Walkthrough — Payment Models"),
      divider(),
      para("Beyond standard CPT/ICD coding, ACE includes deterministic payment model calculations for four reimbursement methodologies:"),
      spacer(80),

      heading("7.1 MS-DRG Grouper (Inpatient)", HeadingLevel.HEADING_2),
      boldPara("What: ", "Medicare Severity Diagnosis-Related Group assignment for inpatient encounters."),
      boldPara("How: ", "Principal diagnosis → MDC (Major Diagnostic Category) → surgical/medical partition → base DRG → CC/MCC severity tier."),
      boldPara("Output: ", "DRG number, relative weight, severity driver (the secondary diagnosis that moved the DRG and payment)."),
      boldPara("Demo: ", "Open IP10001 (pneumonia) or IP10002 (colon resection) to see the DRG result card."),
      talkingPoint("This is where CDI revenue lives — capture the documented MCC and the DRG and reimbursement change. The grouper is real; tables are a curated CMS subset."),
      spacer(80),

      heading("7.2 CMS-HCC Risk Adjustment (RAF)", HeadingLevel.HEADING_2),
      boldPara("What: ", "Hierarchical Condition Category scoring for Medicare Advantage risk adjustment."),
      boldPara("How: ", "Diagnosis → HCC mapping → hierarchy suppression (superior HCC suppresses inferior) → demographic base factor × sum of HCC coefficients."),
      boldPara("Output: ", "RAF score, demographic factor, each HCC with its coefficient, hierarchy suppressions applied."),
      boldPara("Demo: ", "Open HC10001 (Annual Wellness Visit) to see the RAF result card."),
      talkingPoint("Risk adjustment is strategic: RevCap is already HCC-focused, so ACE extends it with agentic capture and a defensible audit trail. The hierarchy suppression is live — only the most severe in a family pays."),
      spacer(80),

      heading("7.3 Anesthesia Unit Calculation", HeadingLevel.HEADING_2),
      boldPara("What: ", "Anesthesia-specific payment: (base units + time units + modifying units) × conversion factor."),
      boldPara("How: ", "Base units from CMS file, time units from documented start/stop (15-minute increments — never estimated by the model), physical-status modifier units per payer convention."),
      boldPara("Output: ", "Unit breakdown card: base + time + modifying = total units × $/unit = estimated allowable."),
      boldPara("Demo: ", "Open AN10001 (laparoscopic cholecystectomy anesthesia) to see the unit calculation."),
      talkingPoint("Anesthesia doesn't pay like CPT line-items. The model codes the CPT and diagnosis; the deterministic calculator handles the payment math. The conversion factor is admin-configurable by locality and payer."),
      spacer(80),

      heading("7.4 APC / OPPS (Facility Pricing)", HeadingLevel.HEADING_2),
      boldPara("What: ", "Outpatient Prospective Payment System — facility-side pricing for hospital outpatient departments."),
      boldPara("How: ", "Each code carries a status indicator from CMS Addendum B. The pricer applies comprehensive APC logic, packaging, and multiple-procedure discounting."),
      boldPara("Output: ", "Per-code status indicators, APC assignments, session payments, packaging of minor procedures."),
      boldPara("Demo: ", "Open GI90003 (double scope at hospital outpatient) — the same chart produces TWO claims: professional fee (both scopes) and facility fee under OPPS (one session payment)."),
      talkingPoint("Two claims from one chart — professional pays both scopes, facility pays once via comprehensive APC packaging. This asymmetry is what outpatient CDI teams manage, and ACE makes it visible."),

      pageBreak(),

      // ════════════════════════════════════════════════════════════════
      // SECTION 8: DEMO FLOW
      // ════════════════════════════════════════════════════════════════
      heading("8. Demo Flow — Client Presentation Script"),
      divider(),
      para("Recommended 20–25 minute demo flow for the Bangalore presentation. Each section includes the screen to show, the key action, and the talking point to deliver."),
      spacer(80),

      heading("Opening (30 sec)", HeadingLevel.HEADING_2),
      para("One-line framing:"),
      talkingPoint("This is ACE — the autonomous coding engine that runs inside RevAmp's Coding Studio. It's a bounded, agentic pipeline: every code is cited, validated, calibrated, and routed — and when it isn't sure, it hands the chart to a human. Let me show you on real charts."),
      spacer(80),

      heading("Scene 1: Control Tower (2 min)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Control Tower"),
      boldPara("Action: ", "Show live work queues (STB / QA / Manual / Escalated / CDI) with SLA aging and breach flags. Click a queue, select charts, assign to coders."),
      talkingPoint("This is the operating picture — live queues, SLA, and workforce assignment."),
      spacer(80),

      heading("Scene 2: Integrations & Ingestion (1.5 min)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Integrations & Ingestion"),
      boldPara("Action: ", "Show connected systems. Load a sample report → Ingest → appears in Worklist. Upload a scanned document → vision OCR → extracted text → run coding."),
      talkingPoint("Charts arrive from the EHR/PMS — the connectors are simulated, the ingest — text or scanned — is real."),
      spacer(80),

      heading("Scene 3: Live Coding Run (3 min)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Worklist → Code an uncoded chart"),
      boldPara("Action: ", "Click Code on an uncoded chart. Watch the Agent Console stream the live pipeline: Eligibility → Conditioning → Extraction → RAG → Coding → Validation → Routing."),
      talkingPoint("You watch the agent think and call its tools — not a spinner. This is the agentic moment."),
      spacer(80),

      heading("Scene 4: Clean Radiology → STB (3 min)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Encounter Detail for RAD10001 (chest X-ray)"),
      boldPara("Action: ", "Hover codes → chart highlights. Show 4-factor confidence. Point out modifier 26 and component_modifier gate. Show validation gates all green → STB. Expand pipeline trace."),
      talkingPoint("Every code points at the words that justify it. Facility read = professional component — the system codes it the way your radiology coders do."),
      spacer(80),

      heading("Scene 5: NCCI Bundling (2 min)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Encounter Detail for RAD10002 (CT abdomen + pelvis)"),
      boldPara("Action: ", "Show one combined 74177 — NOT unbundled 74150 + 72192. Point out the NCCI gate."),
      talkingPoint("This is the unbundling mistake that drives denials — caught deterministically, not hoped away."),
      spacer(80),

      heading("Scene 6: Overcoding Prevention (2 min)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Encounter Detail for RAD10003 (rule-out chest X-ray)"),
      boldPara("Action: ", "Chart says 'rule out pneumonia'; film is clear. System codes R05.9 (cough), NOT pneumonia. Show the uncertain diagnosis guideline citation."),
      talkingPoint("This is the upcoding failure mode regulators care about. The system reads the guideline and applies it."),
      spacer(80),

      heading("Scene 7: Exception Handling (1 min)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Encounter Detail for RAD10004 / RAD10005"),
      boldPara("Action: ", "Both routed Manual at Stage 0 eligibility with a reason (incomplete docs / interventional out-of-scope)."),
      talkingPoint("It refuses to code what it shouldn't. No fabrication — ever."),
      spacer(80),

      heading("Scene 8: ED + Critical Care (2 min)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "ED30001 (standard ED visit) → ED30002 (critical care)"),
      boldPara("Action: ", "ED30001 → 99284 (ED E&M) → STB. ED30002 → 99291 (critical care) → QA by bounded-autonomy rule."),
      talkingPoint("Highest-dollar, highest-scrutiny calls stay with humans — by rule, regardless of confidence."),
      spacer(80),

      heading("Scene 9: CDI / Physician Query — LIVE (3 min)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "EM20002 (anemia E&M chart)"),
      boldPara("Action: ", "Show initial D64.9 (unspecified anemia). Click Scan for CDI Opportunities → watch CDI Agent stream live → query drafted. Click physician answer 'Iron deficiency anemia' → re-codes to D50.9."),
      talkingPoint("AI as a CDI co-pilot. It drafts the query, the physician decides, and coding updates on the answer."),
      spacer(80),

      heading("Scene 10: Closed-Loop Learning — LIVE (3 min)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "RAD10009 → Override → Learning page → RAD10010 → Code"),
      boldPara("Action: ", "Override RAD10009 with a client preference. Show correction in Learning page. Code RAD10010 → adopts corrected code with 'learned' badge."),
      talkingPoint("Corrections don't evaporate. The system gets smarter with every override. In production, this feeds the fine-tune pipeline."),
      spacer(80),

      heading("Scene 11: Admin & Platform (3 min)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Admin → Configuration, Policy & Knowledge Admin"),
      boldPara("Action: ", "Build a KG concept live. Edit a payer policy. Change routing threshold. Show specialty accelerator. Switch roles to demonstrate RBAC."),
      talkingPoint("Anyone can demo a coding model. Nobody hands you a configurable platform. Your admins build the knowledge graph, tune the thresholds, and govern who can do what."),
      spacer(80),

      heading("Scene 12: Defensibility (2 min)", HeadingLevel.HEADING_2),
      boldPara("Screen: ", "Audit packet on any coded chart → Evaluation Harness → Dashboard"),
      boldPara("Action: ", "Show the audit evidence chain. Run evaluation → show accuracy vs IRR ceiling. Show maturity pathway."),
      talkingPoint("Your RAC audit defense, generated automatically. Accuracy reported honestly, not a vanity 95%."),
      spacer(80),

      heading("Close (30 sec)", HeadingLevel.HEADING_2),
      talkingPoint("Working today, not slideware. Radiology depth your coders will recognize, E&M and ED on the same accelerator, every decision defensible, and it bounds itself when it can't be sure. And it's a platform — your admins build the knowledge graph, tune the thresholds, and govern who can do what, without calling us."),

      pageBreak(),

      // ════════════════════════════════════════════════════════════════
      // SECTION 9: NOUS MOAT
      // ════════════════════════════════════════════════════════════════
      heading("9. The Nous Defensibility Moat"),
      divider(),

      para("A coding worklist, a coding screen, and an LLM call are commodity — any competent team can build them. The defensible value is in the methodology, the accelerator, and the operating discipline underneath."),
      spacer(80),

      heading("What's Replicable vs. What's Hard to Copy", HeadingLevel.HEADING_2),
      makeTable(
        ["Layer", "Replicable?", "Where the Value Is"],
        [
          ["Coding UI / Worklist", "Yes — commodity", "—"],
          ["Single LLM 'code this chart' call", "Yes — commodity", "—"],
          ["Evaluation & Calibration Harness", "Hard to replicate", "Frozen golden sets, per-specialty calibration, IRR-honest reporting, drift detection"],
          ["Defensibility Engine", "Hard to replicate", "Citation-gated coding, deterministic validation gates, replayable audit packets, bounded autonomy"],
          ["Specialty Accelerator", "Hard to replicate", "Config-driven specialty onboarding in hours, not months"],
          ["Graph-RAG + Knowledge Graph", "Moderate", "Curated payer-policy + medical-ontology KG driving the necessity gate"],
          ["Closed-Loop Learning + ML-Ops", "Moderate", "Captured corrections → exemplars → fine-tune pipeline"],
          ["Admin-Configurable Platform", "Moderate", "All thresholds and rules admin-tunable at runtime"],
        ],
      ),
      spacer(80),

      heading("Five Things Competitors Can't Easily Copy", HeadingLevel.HEADING_2),
      spacer(40),
      boldBullet("1. The Evaluation & Calibration Harness — the moat. ", "Anyone can fine-tune a model. Few can sustain frozen, adjudicated golden sets across 16 specialties, rebuild calibration after every code-set update, and detect drift before it becomes a denial spike. The harness reports accuracy vs. adjudicated consensus with the IRR ceiling — not a vanity number."),
      spacer(40),
      boldBullet("2. The Defensibility Engine. ", "Every code carries a chart-line citation + guideline reference (verified), runs through 10 deterministic gates, and produces a replayable audit packet. Bounded autonomy keeps the highest-stakes calls with humans. Accuracy without defensibility is a denial waiting to happen."),
      spacer(40),
      boldBullet("3. The Specialty Accelerator. ", "A new specialty or client is configuration + a golden set, not a six-month rebuild. This is the economic story: time-to-new-specialty in days, not months."),
      spacer(40),
      boldBullet("4. Graph-RAG over a curated knowledge graph. ", "The agent is grounded in a payer-policy + medical-ontology graph and may only emit codes it surfaces. Building and maintaining this graph (payer-bulletin ingestion, ontology curation, versioning, per-client overlays) is operational IP."),
      spacer(40),
      boldBullet("5. Admin-configurable platform + operating model. ", "A platform an admin operates: routing thresholds, confidence weights, SLAs, specialties — all tunable at runtime. Combined with the control tower, human pods, and governance ramp, this is a capability VHT runs, not a tool VHT rents."),

      pageBreak(),

      // ════════════════════════════════════════════════════════════════
      // SECTION 10: PROPOSAL SUMMARY
      // ════════════════════════════════════════════════════════════════
      heading("10. Proposal Summary & Timeline"),
      divider(),

      heading("Timeline", HeadingLevel.HEADING_2),
      makeTable(
        ["Phase", "Window", "Goal"],
        [
          ["Phase 0 — Demo", "June 15–16, 2026", "Prove approach, workflow, architecture, explainability with live ACE demo"],
          ["Phase 1 — Mobilize & Foundations", "Weeks 1–4", "Azure/Foundry setup, data integration, reference curation, golden-set build"],
          ["Phase 2 — Shadow Mode", "Weeks 4–8", "Run alongside coders, daily disagreement reports, per-specialty calibration"],
          ["Phase 3 — Controlled STB Go-Live", "Weeks 8–12", "Radiology STB for 1–2 clients, 100% audit → taper to certification"],
          ["Phase 4 — Scale", "Weeks 12+", "Add ED + more clients, SLM accelerator, denial-feedback loop"],
        ],
      ),
      spacer(80),

      heading("Governance Model", HeadingLevel.HEADING_2),
      para("VHT audits 100% of charts during initial rollout. The model earns certification at ≥ 95% quality, after which audit sampling tapers and STB share grows. This is a progressive trust-building model, not a flip-the-switch deployment."),
      spacer(80),

      heading("What Nous Needs from VHT", HeadingLevel.HEADING_2),
      bullet("Data access to pilot clients (Practice Admin / eCW / Cerner) and AI/data agreements"),
      bullet("Domain SME support — coding/CDI experts for golden-set adjudication"),
      bullet("Payer-policy inputs — bulletins/medical-necessity for pilot payers (Anthem, Cigna, Medicare)"),
      bullet("Sample de-identified charts per specialty and daily volume data"),
      bullet("Azure/Foundry access (US-region) with Anthropic availability confirmation"),
      spacer(80),

      heading("Commercial Model", HeadingLevel.HEADING_2),
      para("Outcome-based, fixed-scope SOW aligned to automation performance (STB share / accuracy / effort reduction), with milestone-based payments tied to Phases 0–4."),

      pageBreak(),

      // ════════════════════════════════════════════════════════════════
      // SECTION 11: APPENDIX
      // ════════════════════════════════════════════════════════════════
      heading("11. Appendix — Tech Stack & Deployment"),
      divider(),

      heading("Technology Stack", HeadingLevel.HEADING_2),
      makeTable(
        ["Component", "Technology", "Version"],
        [
          ["Backend Framework", "FastAPI", "0.115.6"],
          ["ORM", "SQLAlchemy", "2.0.36"],
          ["Database", "PostgreSQL + pgvector", "16"],
          ["LLM SDK", "Anthropic SDK", "0.42.0"],
          ["Frontend Framework", "React", "18.3.1"],
          ["Language", "TypeScript", "5.6"],
          ["Build Tool", "Vite", "5.4"],
          ["CSS", "Tailwind CSS", "3.4"],
          ["State Management", "TanStack Query (React Query)", "5.62"],
          ["Graph Visualization", "Cytoscape", "3.34"],
          ["Charts", "Recharts", "2.13"],
          ["Containerization", "Docker + docker-compose", "Latest"],
          ["Web Server", "Nginx", "1.27-alpine"],
          ["Python", "3.12", "—"],
          ["Node.js (build)", "20-alpine", "—"],
        ],
      ),
      spacer(80),

      heading("Deployment", HeadingLevel.HEADING_2),
      heading("Quick Start", HeadingLevel.HEADING_3),
      para("1. Copy .env.example to .env and add your ANTHROPIC_API_KEY"),
      para("2. Run: docker compose up --build"),
      para("3. Open UI: http://localhost:8080"),
      para("4. API docs: http://localhost:8000/docs"),
      spacer(40),
      heading("Docker Services", HeadingLevel.HEADING_3),
      makeTable(
        ["Service", "Image", "Port", "Purpose"],
        [
          ["db", "pgvector:pg16", "5432 (internal)", "PostgreSQL + pgvector database"],
          ["api", "Custom (Python 3.12-slim)", "8000 (internal)", "FastAPI backend + agentic pipeline"],
          ["web", "Custom (Nginx 1.27-alpine)", "8080 (public)", "React frontend + API reverse proxy"],
        ],
      ),
      spacer(80),

      heading("Production Target", HeadingLevel.HEADING_2),
      para("Azure + Azure AI Foundry, US-region, multi-tenant. The demo's Claude API path maps directly to a Foundry endpoint. Model endpoint is configurable: Foundry Azure OpenAI / Anthropic-in-Foundry / local."),
      spacer(80),

      heading("Data Provenance", HeadingLevel.HEADING_2),
      makeTable(
        ["Data", "Source", "Notes"],
        [
          ["ICD-10-CM", "Real CMS/NCHS public-domain", "2025 effective, plus 2024 prior year"],
          ["HCPCS Level II", "Real CMS public-domain", "Current codes"],
          ["CPT", "DEMO PLACEHOLDER", "Real numbers, our own descriptors — swap licensed AMA for production"],
          ["NCCI/MUE", "Modeled on real CMS logic", "Subset"],
          ["Ontology", "Demo concept set", "Swap SNOMED CT / UMLS in production"],
          ["Charts", "Synthetic, PHI-free", "Pipeline genuinely codes them; no pre-stored answers"],
          ["MS-DRG", "Real CMS tables", "Curated subset"],
          ["HCC", "CMS-HCC V24", "Public coefficients and mappings"],
          ["Anesthesia", "CMS base unit file", "Public data"],
          ["APC/OPPS", "CMS Addendum B", "Public facility pricing"],
        ],
      ),

      spacer(200),
      divider(),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "— End of Document —", size: 22, color: GRAY, font: "Calibri", italics: true })] }),
      spacer(100),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Prepared by Nous Infosystems | Confidential", size: 18, color: NOUS_BLUE, font: "Calibri" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "For questions, contact the Nous AI Engineering team", size: 16, color: GRAY, font: "Calibri" })] }),
    ],
  }],
});

// ── Generate ──
const buffer = await Packer.toBuffer(doc);
const outPath = "ACE_Demo_Documentation.docx";
fs.writeFileSync(outPath, buffer);
console.log(`Written: ${outPath} (${(buffer.length / 1024).toFixed(0)} KB)`);
