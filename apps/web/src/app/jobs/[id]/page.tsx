"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  Activity,
  ArrowRight,
  CheckCircle2,
  Clock,
  Cpu,
  FileCheck2,
  Layers,
  Loader2,
  Sparkles,
} from "lucide-react";
import { JobStatusStepper } from "@/components/jobs/JobStatusStepper";
import { getJobStatus } from "@/lib/api";

export default function JobStatusPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params?.id as string;

  const [jobData, setJobData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    let isMounted = true;
    const fetchStatus = async () => {
      try {
        const data = await getJobStatus(jobId);
        if (isMounted) {
          setJobData(data);
          setLoading(false);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || "Failed to load job status");
          setLoading(false);
        }
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [jobId]);

  const isComplete = jobData?.status === "completed" || jobData?.status === "degraded";

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-black tracking-tight text-slate-900 dark:text-white">
              Analysis Job: {jobData?.ticker || "Processing"}
            </span>
            {isComplete ? (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Ready
              </span>
            ) : (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-cyan-500/10 text-cyan-500 border border-cyan-500/20 flex items-center gap-1 animate-pulse">
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> In Progress
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 font-mono mt-1">Job ID: {jobId}</p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href={`/jobs/${jobId}/trace`}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 transition-colors flex items-center gap-1.5"
          >
            <Activity className="w-3.5 h-3.5 text-cyan-500" />
            Live Trace Spans
          </Link>

          {isComplete && (
            <Link
              href={`/reports/${jobId}`}
              className="px-5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md shadow-cyan-500/20 hover:scale-[1.02] transition-all flex items-center gap-1.5"
            >
              <FileCheck2 className="w-3.5 h-3.5" />
              View Full Report
              <ArrowRight className="w-3.5 h-3.5 ml-0.5" />
            </Link>
          )}
        </div>
      </div>

      {error ? (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-500 text-xs font-medium">
          {error}
        </div>
      ) : (
        <div className="space-y-6">
          {/* Stepper Card */}
          <div className="p-6 md:p-8 rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-6">
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">
                LangGraph State Machine Pipeline
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Deterministic DAG progression across 5 parallel collectors, quantitative risk, and narrative synthesis
              </p>
            </div>

            <JobStatusStepper
              status={jobData?.status || "running"}
              currentStageIndex={isComplete ? 6 : 4}
            />
          </div>
        </div>
      )}
    </div>
  );
}
