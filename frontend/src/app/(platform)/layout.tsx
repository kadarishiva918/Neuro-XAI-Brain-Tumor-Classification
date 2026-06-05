import { AppShell } from "@/components/layout/app-shell";
import { DiagnosticProvider } from "@/context/diagnostic-context";

export default function PlatformLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <DiagnosticProvider>
      <AppShell>{children}</AppShell>
    </DiagnosticProvider>
  );
}
