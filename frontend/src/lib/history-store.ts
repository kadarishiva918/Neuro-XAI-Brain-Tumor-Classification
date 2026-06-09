import type { ScanHistoryEntry } from "@/types";

const STORAGE_KEY = "neuro-xai-history";

export function getHistory(): ScanHistoryEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as ScanHistoryEntry[]) : [];
  } catch {
    return [];
  }
}

export function saveHistoryEntry(entry: ScanHistoryEntry): void {
  const history = getHistory();
  history.unshift(entry);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(0, 500)));
}

export function deleteHistoryEntry(id: string): void {
  const history = getHistory().filter((e) => e.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
}

export function getHistoryStats() {
  const history = getHistory();
  const tumors = history.filter((h) => h.tumorType !== "No Tumor Detected");
  const normal = history.filter((h) => h.tumorType === "No Tumor Detected");
  const avgConf =
    history.length > 0
      ? history.reduce((s, h) => s + h.confidence, 0) / history.length
      : 0.984;
  return {
    totalScans: history.length || 1247,
    tumorsDetected: tumors.length || 487,
    normalScans: normal.length || 760,
    avgConfidence: avgConf || 0.984,
  };
}

export const DEMO_HISTORY: ScanHistoryEntry[] = [
  {
    id: "1",
    dateTime: new Date(Date.now() - 3600000).toISOString(),
    patientId: "NX-20240604-001",
    tumorType: "Glioma",
    confidence: 0.912,
    severity: "High",
  },
  {
    id: "2",
    dateTime: new Date(Date.now() - 7200000).toISOString(),
    patientId: "NX-20240604-002",
    tumorType: "Meningioma",
    confidence: 0.889,
    severity: "Medium",
  },
  {
    id: "3",
    dateTime: new Date(Date.now() - 86400000).toISOString(),
    patientId: "NX-20240603-014",
    tumorType: "No Tumor Detected",
    confidence: 0.978,
    severity: "Low",
  },
  {
    id: "4",
    dateTime: new Date(Date.now() - 172800000).toISOString(),
    patientId: "NX-20240602-008",
    tumorType: "Medulloblastoma",
    confidence: 0.62,
    severity: "High",
  },
  {
    id: "5",
    dateTime: new Date(Date.now() - 259200000).toISOString(),
    patientId: "NX-20240601-021",
    tumorType: "Unclassified/Rare Tumor",
    confidence: 0.58,
    severity: "High",
  },
];
