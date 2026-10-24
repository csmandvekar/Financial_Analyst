import React from "react";
import { AlertTriangle, CheckCircle2, ExternalLink, Link2, ShieldAlert } from "lucide-react";

interface EvidenceSourceListProps {
  citations: string[];
  degradedSources: string[];
}

export function EvidenceSourceList({ citations, degradedSources }: EvidenceSourceListProps) {
  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 md:p-8 space-y-6 shadow-sm">
      <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100 dark:border-slate-800/80 pb-4">
        <Link2 className="w-4 h-4 text-cyan-500" />
        Upstream Evidence Citations & Source Reliability
      </div>

      {/* Degraded Sources Warning Banner */}
      {degradedSources && degradedSources.length > 0 && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-600 dark:text-amber-400 space-y-1">
          <div className="flex items-center gap-2 font-bold text-xs">
            <AlertTriangle className="w-4 h-4" />
            Degraded Data Source Notice
          </div>
          <p className="text-xs">
            The following data sources were temporarily unavailable or returned degraded payloads during this run:{" "}
            <span className="font-bold underline">{degradedSources.join(", ")}</span>. Pipeline gracefully completed using fallback heuristic weights.
          </p>
        </div>
      )}

      {/* Citations List */}
      {citations && citations.length > 0 ? (
        <div className="space-y-2.5">
          {citations.map((citation, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40 text-xs text-slate-700 dark:text-slate-300 flex items-start gap-3"
            >
              <span className="w-5 h-5 rounded-full bg-cyan-500/10 text-cyan-500 font-bold flex items-center justify-center text-[10px] shrink-0 mt-0.5">
                {idx + 1}
              </span>
              <div className="flex-1 break-words">{citation}</div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs text-slate-400 italic">No external article citations recorded for this run.</p>
      )}
    </div>
  );
}
