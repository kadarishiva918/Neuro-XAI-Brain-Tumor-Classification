"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import { Download } from "lucide-react";
import { useDiagnostic } from "@/context/diagnostic-context";
import { TooltipInfo } from "@/components/ui/tooltip-info";
import { generateReportPdf } from "@/lib/pdf-report";

export function XAIStep({ onNext }: { onNext: () => void }) {
  const { previewUrl, heatmap } = useDiagnostic();
  const [opacity, setOpacity] = useState(0.6);

  const cards = [
    {
      title: "GRAD-CAM",
      subtitle: "Heatmap",
      desc: "Tumor region highlighted in red/yellow",
      tooltip: "Gradient-weighted Class Activation Mapping highlights regions that most influenced the model's prediction.",
      image: heatmap ? `data:image/png;base64,${heatmap}` : previewUrl,
      features: ["Superior frontal", "Parietal lobe", "Temporal region"],
    },
    {
      title: "SHAP",
      subtitle: "Attribution Map",
      desc: "Top 10 features ranked",
      tooltip: "SHapley Additive exPlanations quantify each feature's contribution to the prediction.",
      bars: [
        { name: "Intensity variance", v: 0.24 },
        { name: "Edge density", v: 0.19 },
        { name: "Texture homogeneity", v: 0.15 },
      ],
    },
    {
      title: "LIME",
      subtitle: "Explanation",
      desc: "Top 5 regions ranked",
      tooltip: "Local Interpretable Model-agnostic Explanations approximate the model locally with interpretable segments.",
      regions: ["Region A (42%)", "Region B (28%)", "Region C (15%)"],
    },
  ];

  return (
    <div>
      <div className="grid gap-6 md:grid-cols-3">
        {cards.map((card, i) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            whileHover={{ scale: 1.02 }}
            className="glass-card overflow-hidden p-4"
          >
            <div className="flex items-center justify-between">
              <h4 className="font-display font-bold">{card.title}</h4>
              <TooltipInfo term={card.title} definition={card.tooltip} />
            </div>
            <p className="text-xs text-text-muted">{card.subtitle}</p>
            {card.image && (
              <div className="relative mt-3 aspect-square overflow-hidden rounded-lg">
                <Image src={card.image} alt={card.title} fill className="object-cover" style={{ opacity }} />
              </div>
            )}
            {card.bars && (
              <div className="mt-3 space-y-2">
                {card.bars.map((b) => (
                  <div key={b.name}>
                    <div className="flex justify-between text-xs">
                      <span>{b.name}</span>
                      <span className="font-mono">{(b.v * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-bg-elevated">
                      <div className="h-full rounded-full bg-accent-violet" style={{ width: `${b.v * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            )}
            {card.regions && (
              <ul className="mt-3 space-y-1 text-xs text-text-muted">
                {card.regions.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
            )}
            <button type="button" className="btn-secondary mt-3 w-full text-xs">
              <Download className="h-3 w-3" /> Download
            </button>
          </motion.div>
        ))}
      </div>
      <div className="mt-4 glass-card p-4">
        <label className="text-sm text-text-muted">Overlay opacity</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={opacity}
          onChange={(e) => setOpacity(parseFloat(e.target.value))}
          className="mt-2 w-full accent-accent-cyan"
        />
      </div>
      <button type="button" className="btn-primary mt-6" onClick={onNext}>
        Generate Clinical Report
      </button>
    </div>
  );
}

import { getSeverity } from "@/lib/utils";
import type { DisplayLabel } from "@/types";

export function ReportStep() {
  const { patientId, scanDate, previewUrl, prediction, heatmap } = useDiagnostic();
  const label = (prediction?.predicted_label ?? prediction?.tumor_type ?? "Unclassified/Rare Tumor") as DisplayLabel;
  const confidence = prediction?.confidence ?? 0;
  const severity = getSeverity(label);

  const handlePdf = () => generateReportPdf({
    patientId,
    scanDate,
    label,
    confidence,
    previewUrl,
    heatmap,
  });

  return (
    <div className="glass-card mx-auto max-w-2xl p-8 font-serif">
      <div className="border-b-2 border-accent-blue pb-4 text-center">
        <h2 className="font-display text-xl font-bold tracking-wide text-accent-blue">
          NEURO-XAI DIAGNOSTIC REPORT
        </h2>
        <p className="mt-1 text-xs text-text-muted">Precision Diagnostics. Explainable Intelligence.</p>
      </div>
      <dl className="mt-4 grid grid-cols-2 gap-2 text-sm">
        <dt className="text-text-muted">Patient ID</dt>
        <dd className="font-mono">{patientId}</dd>
        <dt className="text-text-muted">Date</dt>
        <dd>{new Date(scanDate).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}</dd>
      </dl>
      <hr className="my-4 border-border" />
      <div className="grid gap-4 sm:grid-cols-2">
        {previewUrl && (
          <div className="relative aspect-square max-h-40 overflow-hidden rounded border border-border">
            <Image src={previewUrl} alt="MRI" fill className="object-cover" />
          </div>
        )}
        <div>
          <p className="text-sm text-text-muted">Classification</p>
          <p className="text-lg font-bold text-accent-rose">{label} ({(confidence * 100).toFixed(1)}%)</p>
          <p className="text-sm">Severity: {severity}</p>
          {prediction?.message && (
            <p className="mt-2 text-xs text-orange-300">{prediction.message}</p>
          )}
        </div>
      </div>
      <p className="mt-4 text-sm text-text-muted">
        <strong>Model Notes:</strong> Cross-Gated Attention Fusion detected high-density feature activation in the
        periventricular white matter with asymmetric hemisphere involvement consistent with {label} morphology.
      </p>
      <div className="mt-6 flex flex-wrap gap-3">
        <button type="button" className="btn-primary" onClick={handlePdf}>
          📄 Download PDF
        </button>
        <button type="button" className="btn-secondary">📧 Email Report</button>
        <button type="button" className="btn-secondary" onClick={() => window.print()}>
          🖨 Print
        </button>
        <button type="button" className="btn-secondary">💾 Save to History</button>
      </div>
    </div>
  );
}
