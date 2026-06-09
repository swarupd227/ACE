# ACE — Presentation & Demo Video

Client-facing collateral for the ACE (Autonomous Coding Engine) review.

## Deliverables (committed)

| File | What it is |
|------|------------|
| `ACE_Architecture.pptx` | 14-slide deck: functional flow + detailed technical architecture + design rationale (options considered & why) |
| `ACE_demo.mp4` | < 2-min end-to-end demo capture (H.264, plays anywhere incl. PowerPoint) |

## Deck — regenerate

```bash
cd deck
npm install            # pptxgenjs
node build_deck.js     # -> ACE_Architecture.pptx
```

Slide map: 1 Title · 2 Context & objectives · 3 At-a-glance · 4 **Functional flow** ·
5 Where AI makes the difference · 6 **System architecture** · 7 **Agentic pipeline (Stage 0–5)** ·
8 Graph-RAG & KG · 9 Validation / routing / autonomy · 10 Defensibility & governance ·
11 **Design rationale — options considered & why** · 12 Security & deployment · 13 Adoption roadmap · 14 Why Nous.

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

# convert to mp4 (ffmpeg-static is a dev dependency)
node -e "const f=require('ffmpeg-static'),{execFileSync}=require('child_process');\
execFileSync(f,['-y','-i','recordings/demo-ACE-end-to-end-demo/video.webm',\
'-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart','../deck/ACE_demo.mp4'],{stdio:'inherit'})"
```

The test (`tests/demo.spec.js`) is a **logical end-to-end product tour** that mirrors the deck, with
branded on-screen captions per step: intake & integrations → the worklist (three lanes) → a brief glimpse
of the live coding agent → grounded & cited result → confidence & rule checks → audit packet → control
tower (queues, SLA, assignment) → CDI co-pilot → closed-loop learning → the admin functions
(configuration, knowledge-graph builder, reference data, change log) → role-based access (the app reshapes
per role) → outcomes dashboard. The SSE agent console is shown only as a short glimpse. Runtime ≈ 2 min.
