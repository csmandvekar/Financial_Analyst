"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Activity,
  ArrowLeft,
  CheckCircle2,
  Cpu,
  FileText,
  Layers,
  Loader2,
} from "lucide-react";
import { AgentTraceTable } from "@/components/jobs/AgentTraceTable";
import { getJobTrace, JobTraceResponse } from "@/lib/api";

export default function JobTracePage() {
  const params = useParams();
  const jobId = params?.id as string;

  const [traceData, setTraceData] = useState<JobTraceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    getJobTrace(jobId)
      .then((data) => {
        setTraceData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load trace records");
        setLoading(false);
      });
  }, [jobId]);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center justify-between">
        <Link
          href={`/jobs/${jobId}`}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 dark:text-slate-400 hover:text-cyan-500 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Job Status
        </Link>

        <Link
          href={`/reports/${jobId}`}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:underline"
        >
          <FileText className="w-3.5 h-3.5" />
          View Report Document &rarr;
        </Link>
      </div>

      {/* Header */}
      <div className="space-y-2 border-b border-slate-200 dark:border-slate-800 pb-6">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-500 dark:text-cyan-400 border border-cyan-500/20">
          <Activity className="w-3.5 h-3.5" />
          Distributed Agent Execution Trace
        </div>
        <h1 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white">
          Agent Execution Spans & Provenance Audit
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Inspect individual agent timings, inputs, versions, and degraded fallback states recorded in PostgreSQL & OpenTelemetry.
        </p>
      </div>

      {loading ? (
        <div className="p-16 flex flex-col items-center justify-center space-y-3 text-slate-400">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
          <p className="text-sm font-medium">Fetching distributed trace logs...</p>
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-500 text-xs font-medium">
          {error}
        </div>
      ) : traceData ? (
        <AgentTraceTable
          agentRuns={traceData.agent_runs || []}
          ticker={traceData.ticker}
          jobId={traceData.job_id}
        />
      ) : null}
    </div>
  );
}
