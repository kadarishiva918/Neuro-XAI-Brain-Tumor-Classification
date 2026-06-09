import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import { AppProviders } from "@/providers/app-providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["600", "700", "800"],
  variable: "--font-jakarta",
});
const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-jetbrains",
});

export const metadata: Metadata = {
  title: "Neuro-XAI | Precision Diagnostics. Explainable Intelligence.",
  description:
    "Clinical-grade brain tumor classification platform with Cross-Gated Multi-Path Attention Fusion and explainable AI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`dark ${inter.variable} ${jakarta.variable} ${jetbrains.variable}`}
    >
      <body className="min-h-screen bg-[#050b1a] text-[#e8f0ff] antialiased font-sans">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
