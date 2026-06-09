import type { DisplayLabel, Severity, TumorClass } from "@/types";
import { ALL_TUMOR_TYPES } from "@/types";

export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ");
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

/** Severity mapping per clinical specification */
export function getSeverity(label: DisplayLabel): Severity {
  const map: Record<string, Severity> = {
    Glioma: "High",
    Medulloblastoma: "High",
    "Primary CNS Lymphoma": "High",
    "Metastatic (Secondary) Tumor": "High",
    Meningioma: "Medium",
    Ependymoma: "Medium",
    "Unclassified/Rare Tumor": "High",
    "Pituitary Adenoma": "Low-Medium",
    "Acoustic Neuroma (Schwannoma)": "Low",
    "No Tumor": "Low",
    "No Tumor Detected": "Low",
  };
  return map[label] ?? "Medium";
}

export function isTumorLabel(label: DisplayLabel): boolean {
  return label !== "No Tumor Detected" && label !== "Unclassified/Rare Tumor"
    ? true
    : label === "Unclassified/Rare Tumor";
}

export function getTumorBadgeClass(label: DisplayLabel): string {
  const map: Record<string, string> = {
    Glioma: "badge-glioma",
    Meningioma: "badge-meningioma",
    "Pituitary Adenoma": "badge-pituitary",
    Medulloblastoma: "badge-glioma",
    Ependymoma: "badge-meningioma",
    "Acoustic Neuroma (Schwannoma)": "badge-normal",
    "Primary CNS Lymphoma": "badge-glioma",
    "Metastatic (Secondary) Tumor": "badge-glioma",
    "Unclassified/Rare Tumor": "badge-meningioma",
    "No Tumor Detected": "badge-normal",
  };
  return map[label] ?? "badge-meningioma";
}

export function generatePatientId(): string {
  const d = new Date();
  const date = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, "0")}${String(d.getDate()).padStart(2, "0")}`;
  const seq = String(Math.floor(Math.random() * 999) + 1).padStart(3, "0");
  return `NX-${date}-${seq}`;
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Result indicator dot colors */
export const RESULT_DOT_COLORS: Record<string, string> = {
  Glioma: "#ef4444",
  Meningioma: "#f97316",
  "Pituitary Adenoma": "#eab308",
  "No Tumor": "#22c55e",
  "No Tumor Detected": "#22c55e",
  "Unclassified/Rare Tumor": "#eab308",
};

export function getResultDotColor(label: string): string {
  return RESULT_DOT_COLORS[label] ?? "#ef4444";
}

export function isNoTumorLabel(label: string): boolean {
  return label === "No Tumor" || label === "No Tumor Detected";
}

export const TUMOR_COLORS: Record<TumorClass, string> = {
  Glioma: "#FF4D6D",
  Meningioma: "#F97316",
  "Pituitary Adenoma": "#EAB308",
  Medulloblastoma: "#DC2626",
  Ependymoma: "#A855F7",
  "Acoustic Neuroma (Schwannoma)": "#06B6D4",
  "Primary CNS Lymphoma": "#EC4899",
  "Metastatic (Secondary) Tumor": "#8B5CF6",
};

export function emptyProbabilities(): Record<TumorClass, number> {
  return Object.fromEntries(ALL_TUMOR_TYPES.map((t) => [t, 0])) as Record<TumorClass, number>;
}

export const DEMO_WEEKLY_SCANS = [
  { day: "Mon", scans: 42, tumors: 18 },
  { day: "Tue", scans: 38, tumors: 15 },
  { day: "Wed", scans: 55, tumors: 22 },
  { day: "Thu", scans: 47, tumors: 19 },
  { day: "Fri", scans: 61, tumors: 28 },
  { day: "Sat", scans: 28, tumors: 9 },
  { day: "Sun", scans: 22, tumors: 7 },
];

export const DEMO_TUMOR_DIST = ALL_TUMOR_TYPES.map((name, i) => ({
  name,
  value: [22, 18, 14, 12, 10, 9, 8, 7][i],
  color: TUMOR_COLORS[name],
}));

export const DEMO_CONFIDENCE_TREND = [
  { date: "May 29", confidence: 96.2 },
  { date: "May 30", confidence: 97.1 },
  { date: "May 31", confidence: 95.8 },
  { date: "Jun 1", confidence: 98.0 },
  { date: "Jun 2", confidence: 97.4 },
  { date: "Jun 3", confidence: 98.2 },
  { date: "Jun 4", confidence: 98.4 },
];
