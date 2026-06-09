import { jsPDF } from "jspdf";
import type { PredictionResult } from "@/types";
import { formatConfidencePercent } from "@/lib/prediction-utils";

export function downloadReport(
  prediction: PredictionResult,
  patientId: string,
  scanDate: string,
  clinicianName?: string
) {
  const doc = new jsPDF();
  const label = prediction.predicted_label ?? prediction.tumor_type ?? "Unknown";
  const confidence = formatConfidencePercent(prediction.confidence);

  doc.setFontSize(18);
  doc.text("Neuro-XAI Clinical Report", 14, 20);
  doc.setFontSize(11);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 28);
  if (clinicianName) doc.text(`Clinician: ${clinicianName}`, 14, 35);

  doc.setFontSize(13);
  doc.text("Patient Information", 14, 48);
  doc.setFontSize(11);
  doc.text(`Patient ID: ${patientId}`, 14, 56);
  doc.text(`Scan Date: ${scanDate}`, 14, 63);

  doc.setFontSize(13);
  doc.text("Classification Result", 14, 78);
  doc.setFontSize(11);
  doc.text(`Diagnosis: ${label}`, 14, 86);
  doc.text(`Confidence: ${confidence}`, 14, 93);
  doc.text(`Severity: ${prediction.severity ?? "N/A"}`, 14, 100);

  doc.setFontSize(13);
  doc.text("Probability Distribution", 14, 115);
  let y = 123;
  const probs = prediction.probabilities as Record<string, number>;
  for (const [key, val] of Object.entries(probs)) {
    if (val > 0 || key === "No Tumor") {
      doc.text(`${key}: ${val.toFixed(1)}%`, 14, y);
      y += 7;
      if (y > 270) break;
    }
  }

  doc.setFontSize(9);
  doc.text(
    "Disclaimer: AI-assisted analysis for research support only. Not a substitute for clinical judgment.",
    14,
    285
  );

  doc.save(`Neuro-XAI-Report-${patientId}.pdf`);
}
