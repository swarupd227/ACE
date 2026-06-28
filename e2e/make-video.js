// Transcode the newest Playwright recording (.webm) to a shareable mp4.
// The bottom caption bar is already part of the recorded page, so nothing is overlaid here.
const ff = require("ffmpeg-static");
const { execFileSync } = require("child_process");
const fs = require("fs"), path = require("path");

function newestWebm(dir) {
  let best = null;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { const r = newestWebm(p); if (r && (!best || r.t > best.t)) best = r; }
    else if (e.name.endsWith(".webm")) { const t = fs.statSync(p).mtimeMs; if (!best || t > best.t) best = { p, t }; }
  }
  return best;
}

const src = newestWebm("recordings");
if (!src) { console.error("no .webm found under recordings/ — run the spec first"); process.exit(1); }

const out = path.join("..", "deck", "ACE_studio_demo.mp4");
execFileSync(ff, ["-y", "-ss", "0.3", "-i", src.p,
  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], { stdio: "pipe" });

// report duration (ffmpeg prints metadata to stderr)
let dur = "?";
try {
  execFileSync(ff, ["-i", out], { stdio: "pipe" });
} catch (e) {
  const m = String(e.stderr || "").match(/Duration:\s*(\d+):(\d+):(\d+\.\d+)/);
  if (m) dur = `${m[1]}:${m[2]}:${m[3]}`;
}
console.log(`source : ${src.p}`);
console.log(`output : ${path.resolve(out)}`);
console.log(`length : ${dur}`);
