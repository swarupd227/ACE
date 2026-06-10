const f = require("ffmpeg-static");
const { execFileSync } = require("child_process");
const fs = require("fs"), path = require("path");
function findWebm(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { const r = findWebm(p); if (r) return r; }
    else if (e.name.endsWith(".webm")) return p;
  }
  return null;
}
const webm = findWebm("recordings");
execFileSync(f, ["-y","-ss","0.3","-i",webm,"-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart","../deck/ACE_demo.mp4"], {stdio:"pipe"});
for (const t of ["0.0","0.5","1.0","2.0","4.0","5.5"]) {
  execFileSync(f, ["-y","-ss",t,"-i","../deck/ACE_demo.mp4","-vframes","1","frames/open-"+t+".png"], {stdio:"pipe"});
}
console.log("converted", webm);
