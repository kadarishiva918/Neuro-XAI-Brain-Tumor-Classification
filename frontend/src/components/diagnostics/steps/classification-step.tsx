"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Download, RefreshCw } from "lucide-react";
import { useDiagnostic } from "@/context/diagnostic-context";
import { useAuth } from "@/context/auth-context";
import { getSeverity, getResultDotColor, isNoTumorLabel, TUMOR_COLORS, emptyProbabilities } from "@/lib/utils";
import {
  formatConfidencePercent,
  getProbabilityPercent,
  normalizeProbabilities,
} from "@/lib/prediction-utils";
import { downloadReport } from "@/lib/report-download";
import { ALL_TUMOR_TYPES } from "@/types";
import { TooltipInfo } from "@/components/ui/tooltip-info";

const PROBABILITY_ROWS = [...ALL_TUMOR_TYPES, "No Tumor"] as const;

export function ClassificationStep({ onNext }: { onNext: () => void }) {
  const { prediction, patientId, scanDate, resetSession } = useDiagnostic();
  const { user } = useAuth();

  const rawProbs = prediction?.probabilities
    ? normalizeProbabilities(prediction.probabilities as Record<string, number>)
    : emptyProbabilities();

  const label =
    prediction?.predicted_label ??
    prediction?.tumor_type ??
    "Unclassified/Rare Tumor";
  const confidenceFrac = prediction?.confidence ?? 0;
  const severity =
    prediction?.severity ??
    getSeverity(label);
  const isRare = label === "Unclassified/Rare Tumor";
  const isNormal = isNoTumorLabel(String(label));
  const dotColor = getResultDotColor(String(label));
  const lowConfidence = prediction?.message?.includes("Low confidence");

  const handleScanAgain = () => {
    resetSession();
  };

  const handleDownload = () => {
    if (!prediction) return;
    downloadReport(prediction, patientId, scanDate, user?.name);
  };

  return (
    <motion.div
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="mx-auto max-w-xl glass-card p-8 text-center"
    >
      <h3 className="text-sm font-semibold uppercase tracking-widest text-text-muted">
        Classification Result
      </h3>
      <hr className="my-4 border-border" />

      <div className="flex items-center justify-center gap-3">
        <span
          className="inline-block h-3 w-3 shrink-0 rounded-full"
          style={{ backgroundColor: dotColor }}
          aria-hidden
        />
        <motion.p
          initial={{ scale: 1.2 }}
          animate={{ scale: 1 }}
          className={`font-display text-2xl font-bold ${
            isNormal
              ? "text-[#22c55e]"
              : isRare || lowConfidence
              ? "text-[#eab308]"
              : "text-accent-rose"
          }`}
        >
          {String(label).toUpperCase()}
          {!isNormal && !isRare ? " DETECTED" : ""}
        </motion.p>
      </div>

      <p className="mt-2 font-mono text-accent-cyan">
        Confidence: {formatConfidencePercent(confidenceFrac)}
      </p>
      {prediction?.message && (
        <p className="mt-3 rounded-lg border border-orange-500/30 bg-orange-500/10 p-3 text-sm text-orange-200">
          {prediction.message}
        </p>
      )}
      {prediction?.original_prediction && (
        <p className="mt-2 text-xs text-text-muted">
          Model suggestion: {prediction.original_prediction}
          {prediction.original_confidence != null &&
            ` (${formatConfidencePercent(prediction.original_confidence)})`}
        </p>
      )}
      <span
        className={`mt-2 inline-block rounded-full px-3 py-1 text-xs font-bold ${
          severity === "High"
            ? "bg-accent-rose/20 text-accent-rose"
            : severity === "Medium"
            ? "bg-orange-500/20 text-orange-400"
            : severity === "Low-Medium"
            ? "bg-yellow-500/20 text-yellow-400"
            : "bg-[#22c55e]/20 text-[#22c55e]"
        }`}
      >
        Severity: {severity}
      </span>

      <div className="relative mx-auto my-6 h-28 w-28">
        <svg viewBox="0 0 100 100" className="-rotate-90">
          <circle cx="50" cy="50" r="42" fill="none" stroke="#111D3A" strokeWidth="8" />
          <motion.circle
            cx="50"
            cy="50"
            r="42"
            fill="none"
            stroke={isNormal ? "#22c55e" : "#4CC9F0"}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={264}
            initial={{ strokeDashoffset: 264 }}
            animate={{
              strokeDashoffset: 264 - 264 * Math.min(1, Math.max(0, confidenceFrac)),
            }}
            transition={{ duration: 1.2, ease: "easeOut" }}
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center font-mono text-lg font-bold">
          {Math.round(Math.min(100, Math.max(0, confidenceFrac * 100)))}%
        </span>
      </div>

      <p className="mb-3 text-left text-sm text-text-muted">
        Probability Distribution (trained + extended classes)
      </p>
      <div className="max-h-64 space-y-2 overflow-y-auto text-left">
        {PROBABILITY_ROWS.map((cls) => {
          const pct = getProbabilityPercent(rawProbs, cls);
          const barColor =
            cls === "No Tumor"
              ? "#22c55e"
              : TUMOR_COLORS[cls as keyof typeof TUMOR_COLORS] ?? "#4CC9F0";
          return (
            <div key={cls}>
              <div className="mb-1 flex justify-between text-xs">
                <span className="truncate pr-2">{cls}</span>
                <span className="font-mono shrink-0">{pct.toFixed(1)}%</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-bg-elevated">
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: barColor }}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(100, pct)}%` }}
                  transition={{ type: "spring", stiffness: 80, damping: 15 }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 flex flex-wrap justify-center gap-3">
        <button
          type="button"
          className="btn-primary inline-flex items-center gap-2 bg-gradient-to-r from-accent-cyan to-accent-blue"
          onClick={handleScanAgain}
        >
          <RefreshCw className="h-4 w-4" />
          Scan New Image
        </button>
        <button
          type="button"
          className="btn-secondary inline-flex items-center gap-2"
          onClick={handleDownload}
          disabled={!prediction}
        >
          <Download className="h-4 w-4" />
          Download Report
        </button>
        <button type="button" className="btn-secondary" onClick={onNext}>
          View Explainability
        </button>
        <Link href="/explainability/grad-cam" className="btn-secondary">
          Deep Dive XAI
        </Link>
      </div>
      <p className="mt-4 text-xs text-text-muted">
        Cross-Gated Attention Fusion
        <TooltipInfo
          term="Cross-Gated Attention"
          definition="Fuses local detail and global context feature paths through learnable gating mechanisms for improved tumor localization."
        />
      </p>
    </motion.div>
  );
}
