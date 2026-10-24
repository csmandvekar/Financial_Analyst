import React from "react";
import Link from "next/link";
import { Activity, Cpu, Database, ExternalLink, ShieldCheck } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 dark:border-slate-800/80 bg-white/50 dark:bg-slate-950/50 py-8 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-500 dark:text-slate-400">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-cyan-500" />
          <span>Financial Intelligence Platform &bull; Multi-Agent Distributed DAG</span>
        </div>

        <div className="flex items-center gap-6">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-cyan-500 transition-colors"
          >
            <Database className="w-3.5 h-3.5" />
            FastAPI Swagger
            <ExternalLink className="w-3 h-3 ml-0.5 opacity-60" />
          </a>
          <a
            href="http://localhost:8000/metrics"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-cyan-500 transition-colors"
          >
            <Activity className="w-3.5 h-3.5" />
            Prometheus Metrics
            <ExternalLink className="w-3 h-3 ml-0.5 opacity-60" />
          </a>
          <a
            href="http://localhost:3000"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-cyan-500 transition-colors"
          >
            <Cpu className="w-3.5 h-3.5" />
            Grafana Dashboards
            <ExternalLink className="w-3 h-3 ml-0.5 opacity-60" />
          </a>
        </div>
      </div>
    </footer>
  );
}
