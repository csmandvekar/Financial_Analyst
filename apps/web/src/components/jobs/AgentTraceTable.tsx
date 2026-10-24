"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock,
  Code,
  Hash,
  XCircle,
} from "lucide-react";
import { AgentRunData } from "@/lib/api";
import { formatDate } from "@/lib/utils";

interface AgentTraceTableProps {
  agentRuns: AgentRunData[];
  ticker: string;
  jobId: string;
}

export function AgentTraceTable({ agentRuns, ticker, jobId }: AgentTraceTableProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const totalDuration = agentRuns.reduce((acc, r) => acc + (r.duration_ms || 0), 0);

  return (
    <div className="space-y-4">
      {/* Overview Metric Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Target Asset</div>
          <div className="text-base font-bold text-slate-900 dark:text-white mt-0.5">{ticker}</div>
        </div>
        <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Agents Executed</div>
          <div className="text-base font-bold text-slate-900 dark:text-white mt-0.5">{agentRuns.length} Spans</div>
        </div>
        <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Cumulative Latency</div>
          <div className="text-base font-bold text-slate-900 dark:text-white mt-0.5">
            {(totalDuration / 1000).toFixed(2)}s
          </div>
        </div>
        <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Distributed Trace ID</div>
          <div className="text-xs font-mono text-cyan-500 mt-1 truncate" title={jobId}>
            {jobId.slice(0, 16)}...
          </div>
        </div>
      </div>

      {/* Table Container */}
      <div className="overflow-hidden rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 dark:bg-slate-950/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 uppercase font-semibold">
              <tr>
                <th className="px-4 py-3.5">Agent Name</th>
                <th className="px-4 py-3.5">Version</th>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-4 py-3.5">Duration</th>
                <th className="px-4 py-3.5">Started At</th>
                <th className="px-4 py-3.5 text-right">Provenance Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
              {agentRuns.map((run) => {
                const isExpanded = expandedId === run.id;
                const isSuccess = run.status === "success";
                const isDegraded = run.status === "degraded";

                return (
                  <React.Fragment key={run.id || run.agent_name}>
                    <tr
                      onClick={() => setExpandedId(isExpanded ? null : run.id)}
                      className="hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors"
                    >
                      <td className="px-4 py-3.5 font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <span className="p-1 rounded bg-slate-100 dark:bg-slate-800 text-slate-500">
                          <Code className="w-3.5 h-3.5" />
                        </span>
                        {run.agent_name}
                      </td>
                      <td className="px-4 py-3.5 text-slate-500 font-mono">v{run.agent_version}</td>
                      <td className="px-4 py-3.5">
                        {isSuccess ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                            <CheckCircle2 className="w-3 h-3" /> SUCCESS
                          </span>
                        ) : isDegraded ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/10 text-amber-500 border border-amber-500/20">
                            <AlertTriangle className="w-3 h-3" /> DEGRADED
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-500/10 text-rose-500 border border-rose-500/20">
                            <XCircle className="w-3 h-3" /> FAILED
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3.5 font-mono text-slate-700 dark:text-slate-300">
                        {run.duration_ms ? `${run.duration_ms.toFixed(1)}ms` : "< 1ms"}
                      </td>
                      <td className="px-4 py-3.5 text-slate-500">{formatDate(run.started_at)}</td>
                      <td className="px-4 py-3.5 text-right font-mono text-slate-400">
                        <span className="flex items-center justify-end gap-1">
                          <Hash className="w-3 h-3 opacity-60" />
                          {run.input_hash || "n/a"}
                          {isExpanded ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />}
                        </span>
                      </td>
                    </tr>

                    {isExpanded && (
                      <tr className="bg-slate-50/70 dark:bg-slate-950/40">
                        <td colSpan={6} className="px-6 py-4 space-y-2 text-xs">
                          <div className="font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-2">
                            <Clock className="w-4 h-4 text-cyan-500" />
                            Execution Timeline: Finished at {formatDate(run.finished_at)}
                          </div>
                          {run.error && (
                            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 font-mono text-[11px]">
                              {run.error}
                            </div>
                          )}
                          <div className="text-[11px] text-slate-500">
                            OpenTelemetry Span: <code className="text-cyan-500 font-mono">agent.{run.agent_name}</code> (Service: <code className="text-slate-400">financial-intel-platform</code>)
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
