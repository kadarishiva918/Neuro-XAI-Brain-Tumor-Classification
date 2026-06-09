"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Microscope,
  Eye,
  BarChart3,
  FileText,
  History,
  Settings,
  ChevronDown,
  GraduationCap,
  Layers,
  Sparkles,
} from "lucide-react";
import { useState } from "react";
import { LogOut } from "lucide-react";
import { useTheme } from "next-themes";
import { NeuroLogo } from "@/components/ui/logo";
import { useAuth } from "@/context/auth-context";
import { cn } from "@/lib/utils";

type NavItem =
  | { href: string; label: string; icon: React.ComponentType<{ className?: string }> }
  | {
      label: string;
      icon: React.ComponentType<{ className?: string }>;
      children: { href: string; label: string; icon: React.ComponentType<{ className?: string }> }[];
    };

const navItems: NavItem[] = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/diagnostics", label: "MRI Diagnostics", icon: Microscope },
  {
    label: "Explainability",
    icon: Eye,
    children: [
      { href: "/explainability/grad-cam", label: "Grad-CAM Heatmaps", icon: GraduationCap },
      { href: "/explainability/shap", label: "SHAP Attribution", icon: Layers },
      { href: "/explainability/lime", label: "LIME Explanations", icon: Sparkles },
    ],
  },
  { href: "/analytics", label: "Model Analytics", icon: BarChart3 },
  { href: "/report", label: "Clinical Report", icon: FileText },
  { href: "/history", label: "History Logs", icon: History },
];

interface SidebarProps {
  mobileOpen: boolean;
  onMobileClose: () => void;
}

export function Sidebar({ mobileOpen, onMobileClose }: SidebarProps) {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const [xaiOpen, setXaiOpen] = useState(pathname.startsWith("/explainability"));

  const isActive = (href: string) =>
    href === "/" ? pathname === "/" : pathname.startsWith(href);

  const NavLink = ({
    href,
    label,
    icon: Icon,
    nested = false,
  }: {
    href: string;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    nested?: boolean;
  }) => {
    const active = isActive(href);
    return (
      <Link
        href={href}
        onClick={onMobileClose}
        className={cn(
          "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
          nested && "pl-9 text-xs",
          active
            ? "neon-border-active text-[#e8f0ff]"
            : "text-[#6b7fa3] hover:bg-[rgba(76,201,240,0.08)] hover:text-[#e8f0ff]"
        )}
      >
        <Icon
          className={cn(
            "h-4 w-4 shrink-0 transition-all",
            active ? "text-[#00d4ff]" : "group-hover:text-[#4cc9f0]"
          )}
        />
        <span className="truncate">{label}</span>
      </Link>
    );
  };

  const sidebarContent = (
    <>
      <div className="border-b border-[rgba(76,201,240,0.12)] px-4 py-5">
        <Link href="/" className="block" onClick={onMobileClose}>
          <NeuroLogo />
        </Link>
        <p className="mt-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-[#6b7fa3]">
          Precision Diagnostics
        </p>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {navItems.map((item) => {
          if ("children" in item && item.children) {
            const open = xaiOpen || item.children.some((c) => isActive(c.href));
            return (
              <div key={item.label}>
                <button
                  type="button"
                  onClick={() => setXaiOpen(!xaiOpen)}
                  className={cn(
                    "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
                    "text-[#6b7fa3] hover:bg-[rgba(76,201,240,0.08)] hover:text-[#e8f0ff]",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4cc9f0]",
                    open && "text-[#e8f0ff]"
                  )}
                >
                  <item.icon className="h-4 w-4 shrink-0" />
                  <span className="flex-1 text-left">{item.label}</span>
                  <ChevronDown
                    className={cn("h-4 w-4 transition-transform", open && "rotate-180")}
                  />
                </button>
                <AnimatePresence>
                  {open && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="ml-5 mt-1 space-y-0.5 border-l border-[rgba(76,201,240,0.12)] pl-2">
                        {item.children.map((child) => (
                          <NavLink
                            key={child.href}
                            href={child.href}
                            label={child.label}
                            icon={child.icon}
                            nested
                          />
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          }
          if (!("href" in item)) return null;
          return (
            <NavLink
              key={item.href}
              href={item.href}
              label={item.label}
              icon={item.icon}
            />
          );
        })}
      </nav>

      <div className="space-y-1 border-t border-[rgba(76,201,240,0.12)] px-3 py-4">
        {user && (
          <div className="mb-3 flex items-center gap-3 rounded-lg bg-[rgba(76,201,240,0.06)] px-3 py-2.5">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#4cc9f0] to-[#7b61ff] text-xs font-bold text-[#050b1a]">
              {user.initials}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-[#e8f0ff]">{user.name}</p>
              <p className="truncate text-xs text-[#6b7fa3]">{user.specialization}</p>
            </div>
            <button
              type="button"
              onClick={logout}
              className="shrink-0 rounded p-1.5 text-[#6b7fa3] hover:bg-[rgba(255,77,109,0.15)] hover:text-[#ff4d6d]"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        )}
        <NavLink href="/settings" label="Settings" icon={Settings} />
        <button
          type="button"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-[#6b7fa3] transition-all hover:bg-[rgba(76,201,240,0.08)] hover:text-[#e8f0ff] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4cc9f0]"
        >
          <span className="text-base">{theme === "dark" ? "🌙" : "☀️"}</span>
          <span>{theme === "dark" ? "Dark Mode" : "Light Mode"}</span>
        </button>
      </div>
    </>
  );

  const sidebarClass =
    "sidebar-shell fixed top-0 z-40 flex h-screen w-[260px] flex-col bg-[#0d1117]";

  return (
    <>
      <aside className={cn(sidebarClass, "hidden lg:flex")}>{sidebarContent}</aside>

      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
              onClick={onMobileClose}
            />
            <motion.aside
              initial={{ x: -260 }}
              animate={{ x: 0 }}
              exit={{ x: -260 }}
              className={cn(sidebarClass, "lg:hidden")}
            >
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      <aside className="fixed bottom-0 left-0 right-0 z-30 flex h-14 items-center justify-around border-t border-[rgba(76,201,240,0.12)] bg-[#0d1117] lg:hidden">
        {navItems.slice(0, 5).map((item) => {
          const href = "href" in item ? item.href : "/explainability/grad-cam";
          const Icon = item.icon;
          const active = isActive(href);
          return (
            <Link
              key={item.label}
              href={href}
              className={cn(
                "flex flex-col items-center p-2 text-[10px]",
                active ? "text-[#00d4ff]" : "text-[#6b7fa3]"
              )}
            >
              <Icon className="h-5 w-5" />
            </Link>
          );
        })}
      </aside>
    </>
  );
}
