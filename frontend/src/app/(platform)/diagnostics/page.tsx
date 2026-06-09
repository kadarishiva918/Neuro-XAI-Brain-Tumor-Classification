"use client";

import { useCallback, useState } from "react";
import toast from "react-hot-toast";
import { PageTransition } from "@/components/layout/page-transition";
import { StepIndicator } from "@/components/diagnostics/step-indicator";
import { UploadStep } from "@/components/diagnostics/steps/upload-step";
import {
  PreprocessStep,
  FeatureExtractionStep,
  FusionStep,
} from "@/components/diagnostics/steps/pipeline-steps";
import { ClassificationStep } from "@/components/diagnostics/steps/classification-step";
import { XAIStep, ReportStep } from "@/components/diagnostics/steps/xai-report-steps";
import { useDiagnostic } from "@/context/diagnostic-context";
import { API_URL, predictImage } from "@/lib/api";
import { saveHistoryEntry } from "@/lib/history-store";
import { formatConfidencePercent } from "@/lib/prediction-utils";
import { getSeverity } from "@/lib/utils";
import type { DisplayLabel } from "@/types";

export default function DiagnosticsPage() {
  const {
    currentStep,
    setCurrentStep,
    file,
    setPrediction,
    setHeatmap,
    patientId,
    resetSession,
  } = useDiagnostic();
  const [, setAnalyzing] = useState(false);

  const runAnalysis = useCallback(async () => {
    if (!file) return;
    setAnalyzing(true);
    try {
      const result = await predictImage(file);
      setPrediction(result);
      setHeatmap(null);
      const label = result.predicted_label ?? result.tumor_type ?? "Unknown";
      toast.success(
        `Analysis complete — ${label} (${formatConfidencePercent(result.confidence)})`
      );
      saveHistoryEntry({
        id: crypto.randomUUID(),
        dateTime: new Date().toISOString(),
        patientId,
        tumorType: label as DisplayLabel,
        confidence: result.confidence,
        severity: getSeverity(label as DisplayLabel),
        heatmap: undefined,
        probabilities: result.probabilities,
      });
      setCurrentStep(2);
    } catch (err) {
      console.error(err);
      const message = err instanceof Error ? err.message : "Unknown error";
      toast.error(`Analysis failed — ${message}`);
      console.error(`Check Flask API at ${API_URL} (proxied via /api)`);
      setCurrentStep(1);
    } finally {
      setAnalyzing(false);
    }
  }, [file, setPrediction, setHeatmap, setCurrentStep, patientId]);

  const goToClassify = useCallback(() => {
    setCurrentStep(5);
  }, [setCurrentStep]);

  return (
    <PageTransition>
      <header className="mb-6 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-bold">MRI Diagnostics</h1>
          <p className="text-text-muted">7-step clinical analysis pipeline</p>
        </div>
        {currentStep > 1 && (
          <button
            type="button"
            onClick={resetSession}
            className="text-sm font-medium text-accent-cyan hover:text-accent-blue"
          >
            ← New Scan
          </button>
        )}
      </header>

      <StepIndicator current={currentStep} />

      {currentStep === 1 && (
        <UploadStep onNext={() => runAnalysis()} />
      )}
      {currentStep === 2 && (
        <PreprocessStep onComplete={() => setCurrentStep(3)} />
      )}
      {currentStep === 3 && (
        <FeatureExtractionStep onComplete={() => setCurrentStep(4)} />
      )}
      {currentStep === 4 && (
        <FusionStep onComplete={goToClassify} />
      )}
      {currentStep === 5 && (
        <ClassificationStep onNext={() => setCurrentStep(6)} />
      )}
      {currentStep === 6 && (
        <XAIStep onNext={() => setCurrentStep(7)} />
      )}
      {currentStep === 7 && <ReportStep />}
    </PageTransition>
  );
}
