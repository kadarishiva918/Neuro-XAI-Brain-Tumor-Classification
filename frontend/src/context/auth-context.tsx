"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useRouter, usePathname } from "next/navigation";

export const SPECIALIZATIONS = [
  "Neuroradiology",
  "Neurosurgery",
  "Oncology",
  "General Radiology",
  "Research",
] as const;

export type Specialization = (typeof SPECIALIZATIONS)[number];

export interface UserProfile {
  name: string;
  specialization: Specialization;
  hospital: string;
  initials: string;
}

const STORAGE_KEY = "neuro-xai-user";

export function getInitials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .map((word) => word[0]?.toUpperCase() ?? "")
    .join("");
}

function loadUser(): UserProfile | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as UserProfile;
  } catch {
    return null;
  }
}

interface AuthContextValue {
  user: UserProfile | null;
  login: (profile: Omit<UserProfile, "initials">) => void;
  logout: () => void;
  isReady: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isReady, setIsReady] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    setUser(loadUser());
    setIsReady(true);
  }, []);

  useEffect(() => {
    if (!isReady) return;
    const isLoginPage = pathname === "/login";
    if (!user && !isLoginPage) {
      router.replace("/login");
    } else if (user && isLoginPage) {
      router.replace("/");
    }
  }, [user, isReady, pathname, router]);

  const login = useCallback(
    (profile: Omit<UserProfile, "initials">) => {
      const full: UserProfile = {
        ...profile,
        initials: getInitials(profile.name),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(full));
      setUser(full);
      router.push("/");
    },
    [router]
  );

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
    router.push("/login");
  }, [router]);

  const value = useMemo(
    () => ({ user, login, logout, isReady }),
    [user, login, logout, isReady]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
