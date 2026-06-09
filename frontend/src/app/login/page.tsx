"use client";

import { useState } from "react";
import { Brain } from "lucide-react";
import { SPECIALIZATIONS, useAuth } from "@/context/auth-context";
import type { Specialization } from "@/context/auth-context";

export default function LoginPage() {
  const { login, isReady } = useAuth();
  const [name, setName] = useState("");
  const [specialization, setSpecialization] = useState<Specialization>("Neuroradiology");
  const [hospital, setHospital] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    login({
      name: name.trim(),
      specialization,
      hospital: hospital.trim(),
    });
  };

  if (!isReady) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#050b1a] text-[#e8f0ff]">
        <p className="text-text-muted">Loading...</p>
      </div>
    );
  }

  return (
    <div className="gradient-mesh grid-overlay flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-md glass-card p-8">
        <div className="mb-6 flex flex-col items-center text-center">
          <Brain className="h-12 w-12 text-accent-cyan" />
          <h1 className="mt-3 font-display text-2xl font-bold">Neuro-XAI</h1>
          <p className="mt-1 text-sm text-text-muted">
            Precision Diagnostics · Explainable Intelligence
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm text-text-muted">Full Name *</label>
            <input
              className="input-field mt-1"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Dr. Arjun Mehta"
              required
            />
          </div>

          <div>
            <label className="text-sm text-text-muted">Specialization *</label>
            <select
              className="input-field mt-1"
              value={specialization}
              onChange={(e) => setSpecialization(e.target.value as Specialization)}
            >
              {SPECIALIZATIONS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm text-text-muted">Hospital / Institution</label>
            <input
              className="input-field mt-1"
              value={hospital}
              onChange={(e) => setHospital(e.target.value)}
              placeholder="Optional"
            />
          </div>

          <button type="submit" className="btn-primary w-full">
            Sign In
          </button>
        </form>

        <p className="mt-4 text-center text-xs text-text-muted">
          No password required — demo clinical access
        </p>
      </div>
    </div>
  );
}
