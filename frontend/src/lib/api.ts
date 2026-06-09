import type { ExplainResult, HealthStatus, ModelInfo, PredictionResult } from "@/types";
import {
  mapApiToPredictionResult,
  type ApiPredictPayload,
} from "@/lib/prediction-utils";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:5000";

/** Browser requests go through Next.js proxy (/api → Flask) to avoid CORS. */
const API_BASE = typeof window !== "undefined" ? "/api" : API_URL;

async function postPredict(file: File): Promise<ApiPredictPayload> {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const msg = await res.text();
      throw new Error(`Server error ${res.status}: ${msg}`);
    }

    const result = (await res.json()) as ApiPredictPayload;
    console.log("✓ Prediction:", result);
    return result;
  } catch (err) {
    console.error("✗ Fetch failed:", err);
    throw err;
  }
}

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(`Server error ${res.status}: ${msg}`);
  }
  return res.json();
}

export async function checkHealth(): Promise<HealthStatus> {
  return apiGet<HealthStatus>("/health");
}

export async function getClasses(): Promise<string[]> {
  const data = await apiGet<{ classes: string[] }>("/classes");
  return data.classes;
}

export async function getModelInfo(): Promise<ModelInfo> {
  return apiGet<ModelInfo>("/model-info");
}

export async function predictImage(file: File): Promise<PredictionResult> {
  const data = await postPredict(file);
  return mapApiToPredictionResult(data);
}

export async function explainImage(file: File): Promise<ExplainResult> {
  const data = await postPredict(file);
  const result = mapApiToPredictionResult(data);
  return {
    ...result,
    heatmap: data.heatmap ?? null,
    heatmap_error: data.heatmap_error ?? null,
  };
}

export function isApiAvailable(): boolean {
  return Boolean(API_BASE);
}
