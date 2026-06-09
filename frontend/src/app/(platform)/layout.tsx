"use client";

import { AppShell } from "@/components/layout/app-shell";
import { DiagnosticProvider } from "@/context/diagnostic-context";
import { useAuth } from "@/context/auth-context";

export default function PlatformLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isReady } = useAuth();

  if (!isReady || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#050b1a] text-[#e8f0ff]">
        <p className="text-text-muted">Loading...</p>
      </div>
    );
  }

  return (
    <DiagnosticProvider>
      <AppShell>{children}</AppShell>
    </DiagnosticProvider>
  );
}
