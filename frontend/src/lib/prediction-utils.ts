import { ALL_TUMOR_TYPES } from "@/types";
import type { DisplayLabel, PredictionResult, TumorClass } from "@/types";

/** API may return confidence as 0–100 or 0–1 */
export function toPercent(value: number | undefined | null): number {
  if (value == null || Number.isNaN(value)) return 0;
  if (value <= 1 && value >= 0) return value * 100;
  return value;
}

export function toFraction(value: number | undefined | null): number {
  if (value == null || Number.isNaN(value)) return 0;
  if (value > 1) return value / 100;
  return value;
}

export type ProbabilityMap = Record<string, number>;

/** Normalize API probabilities object to percentages for display */
export function normalizeProbabilities(
  raw: ProbabilityMap | undefined
): Record<TumorClass, number> & { "No Tumor"?: number } {
  const out = Object.fromEntries(ALL_TUMOR_TYPES.map((k) => [k, 0])) as Record<
    TumorClass,
    number
  > & { "No Tumor"?: number };

  if (!raw) return out;

  const alias: Record<string, string> = {
    "Metastatic Tumor": "Metastatic (Secondary) Tumor",
    "Acoustic Neuroma": "Acoustic Neuroma (Schwannoma)",
    Pituitary: "Pituitary Adenoma",
  };

  for (const [key, val] of Object.entries(raw)) {
    const target = (alias[key] ?? key) as keyof typeof out;
    if (target in out || target === "No Tumor") {
      out[target as TumorClass] = toPercent(val);
    }
    if (key === "No Tumor") {
      out["No Tumor"] = toPercent(val);
    }
  }

  return out;
}

export interface ApiPredictPayload {
  predicted_class?: number;
  predicted_label?: string;
  tumor_type?: string;
  confidence?: number;
  confidence_fraction?: number;
  severity?: string;
  message?: string;
  probabilities?: ProbabilityMap;
  probabilities_fraction?: ProbabilityMap;
  heatmap?: string | null;
  heatmap_error?: string | null;
  filename?: string;
  model_loaded?: boolean;
  low_confidence_warning?: boolean;
  unclassified?: boolean;
  original_prediction?: string;
  original_confidence?: number;
}

/** Map Flask JSON → PredictionResult for UI state */
export function mapApiToPredictionResult(data: ApiPredictPayload): PredictionResult {
  const probabilities = normalizeProbabilities(data.probabilities);
  const confidence = toPercent(
    data.confidence ?? data.confidence_fraction
  );

  const label = (data.tumor_type ??
    data.predicted_label ??
    "Unclassified/Rare Tumor") as DisplayLabel;

  return {
    filename: data.filename,
    predicted_class: data.predicted_class ?? 0,
    predicted_label: label,
    tumor_type: label,
    confidence: confidence / 100,
    severity: (data.severity as PredictionResult["severity"]) ?? undefined,
    message: data.message,
    original_prediction: data.original_prediction,
    original_confidence: data.original_confidence
      ? toPercent(data.original_confidence) / 100
      : undefined,
    probabilities: probabilities as Record<TumorClass, number>,
    model_loaded: data.model_loaded,
  };
}

export function formatConfidencePercent(confidenceFraction: number): string {
  return `${toPercent(confidenceFraction).toFixed(1)}%`;
}

export function getProbabilityPercent(
  probs: Record<string, number> | undefined,
  key: string
): number {
  if (!probs) return 0;
  const val = probs[key];
  return toPercent(val);
}
