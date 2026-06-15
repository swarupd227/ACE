import StreamConsole from "./StreamConsole";
import { useRole } from "../role";
import type { EvalReport } from "../types";

// Thin wrapper around the generic StreamConsole for the eval run.
export default function EvalConsole({ onClose, onDone }: { onClose: () => void; onDone: (r: EvalReport) => void }) {
  const { role } = useRole();
  const actor = role.toLowerCase().replace(/\s+/g, "_");
  return (
    <StreamConsole
      path={`/eval/run/stream?actor=${encodeURIComponent(actor)}`}
      title="Evaluation run"
      onClose={onClose}
      onDone={(ev) => onDone(ev.report)}
    />
  );
}
