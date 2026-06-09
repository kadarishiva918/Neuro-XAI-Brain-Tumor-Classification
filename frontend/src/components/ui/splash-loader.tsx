"use client";

import { NeuroLogo } from "@/components/ui/logo";

/** Centered app splash — logo capped at 120px */
export function SplashLoader() {
  return (
    <div
      className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[#0a0f1e]"
      role="status"
      aria-label="Loading Neuro-XAI"
    >
      <div className="flex max-w-[120px] flex-col items-center">
        <NeuroLogo size="lg" showTagline={false} />
      </div>
      <p className="mt-4 text-sm font-semibold tracking-wide text-white">Neuro-XAI</p>
      <p className="mt-1 text-[10px] uppercase tracking-widest text-[#6b7fa3]">
        Precision Diagnostics
      </p>
      <div className="mt-6 h-8 w-8 animate-spin rounded-full border-2 border-[#4cc9f0]/30 border-t-[#00d4ff]" />
      <p className="mt-3 text-xs text-[#6b7fa3]">Loading clinical workspace…</p>
    </div>
  );
}
