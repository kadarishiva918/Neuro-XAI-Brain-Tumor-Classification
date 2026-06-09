"use client";

import { motion } from "framer-motion";

interface NeuroLogoProps {
  collapsed?: boolean;
  size?: "sm" | "md" | "lg";
  showTagline?: boolean;
}

const sizes = {
  sm: { box: 32, svg: 32 },
  md: { box: 40, svg: 40 },
  lg: { box: 96, svg: 96 },
};

export function NeuroLogo({
  collapsed = false,
  size = "md",
  showTagline = true,
}: NeuroLogoProps) {
  const dim = sizes[size];

  return (
    <div className="flex items-center gap-3">
      <motion.div
        className="relative flex shrink-0 items-center justify-center"
        style={{ width: dim.box, height: dim.box, maxWidth: 120, maxHeight: 120 }}
        animate={{ scale: [1, 1.05, 1] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
      >
        <svg
          viewBox="0 0 48 48"
          width={dim.svg}
          height={dim.svg}
          className="block"
          style={{ width: dim.svg, height: dim.svg, maxWidth: "100%", maxHeight: "100%" }}
          aria-hidden
        >
          <defs>
            <linearGradient id="brainGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4CC9F0" />
              <stop offset="100%" stopColor="#7B61FF" />
            </linearGradient>
          </defs>
          <motion.circle
            cx="24"
            cy="24"
            r="20"
            fill="none"
            stroke="url(#brainGrad)"
            strokeWidth="1.5"
            opacity="0.4"
            animate={{ r: [18, 22, 18], opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <path
            d="M24 8c-6 0-10 4-10 10 0 2 1 4 2 5-2 1-4 3-4 6 0 4 3 7 7 9 1-3 4-5 7-5 3 0 6 2 7 5 4-2 7-5 7-9 0-3-2-5-4-6 1-1 2-3 2-5 0-6-4-10-10-10z"
            fill="url(#brainGrad)"
            opacity="0.9"
          />
          <motion.path
            d="M18 20 Q24 24 30 20"
            fill="none"
            stroke="#00D4FF"
            strokeWidth="1.5"
            strokeLinecap="round"
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
          <motion.path
            d="M16 28 Q24 32 32 28"
            fill="none"
            stroke="#4CC9F0"
            strokeWidth="1"
            strokeLinecap="round"
            animate={{ opacity: [0.3, 0.9, 0.3] }}
            transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
          />
        </svg>
      </motion.div>
      {!collapsed && showTagline && size !== "lg" && (
        <div className="min-w-0">
          <p className="font-display text-lg font-bold tracking-tight text-text-primary">
            Neuro-XAI
          </p>
          <p className="truncate text-[10px] font-medium uppercase tracking-widest text-text-muted">
            Precision Diagnostics
          </p>
        </div>
      )}
    </div>
  );
}
