# ACE — Presentation & Demo Video

Client-facing collateral for the ACE (Autonomous Coding Engine) review.

## Deliverables (committed)

| File | What it is |
|------|------------|
| `ACE_Architecture.pptx` | 16-slide deck: functional flow + technical architecture + the five payment models + design rationale (options considered & why) |
| `ACE_demo.mp4` | ~2.4-min end-to-end demo capture (H.264, plays anywhere incl. PowerPoint) |
| `sample_scanned_chart.pdf` | the scanned chart used for the live vision-OCR ingestion beat |

## Deck — regenerate

```bash
cd deck
npm install            # pptxgenjs
node build_deck.js     # -> ACE_Architecture.pptx
```

Slide map: 1 Title · 2 Why we built this · 3 What we heard from Vee · 4 The idea ·
5 **Functional flow** · 6 What the AI actually does · 7 **Technical architecture** ·
8 **Agentic pipeline (Stage 0–5)** · 9 Graph-RAG & KG · 10 Validation / routing / autonomy ·
11 **Five payment models (pro-fee · MS-DRG · HCC RAF · anesthesia units · APC/OPPS)** ·
12 Trust by design · 13 **Design rationale — options considered & why** · 14 Security & deployment ·
15 Adoption path · 16 Why Nous.

To re-export slide images for QA (Windows, requires Microsoft PowerPoint):
the `qa/` PNGs are produced via PowerPoint COM `SaveAs(<dir>, 18)`.

## Demo video — regenerate

The app must be running (`docker compose up` → UI on http://localhost:8080) and pre-coded
(`scripts/reset-demo.ps1`, or click **Run autonomous coding** once) so the worklist lanes are populated.

```bash
cd e2e
npm install
npx playwright install chromium
npx playwright test          # records e2e/recordings/.../video.webm

# convert to mp4 — finds the webm, trims the 0.3s recording-start gap,
# writes ../deck/ACE_demo.mp4 (ffmpeg-static is a dev dependency)
node convert.js
```

The test (`tests/demo.spec.js`) is a **logical end-to-end product tour** that mirrors the deck, with
branded on-screen captions per step: intake & integrations (incl. the scanned-document vision-OCR card) →
the worklist (three lanes) → a brief glimpse of the live coding agent → grounded & cited result →
confidence & rule checks → audit packet → **the payment models (MS-DRG card, HCC/RAF card)** → control
tower (queues, SLA, assignment) → CDI co-pilot → closed-loop learning → **the global Audit Log** → the
admin functions (configuration, **the switchable reasoning model**, knowledge-graph builder, reference
data, change log) → role-based access → outcomes dashboard **incl. model performance / drift**. The SSE
agent console is shown only as a short glimpse. Runtime ≈ 2.4 min.
