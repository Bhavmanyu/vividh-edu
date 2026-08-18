"use client";

import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import type { ReactNode } from "react";

interface ReportSectionProps {
  icon: ReactNode;
  title: string;
  subtitle?: string;
  children: ReactNode;
  defaultOpen?: boolean;
  badge?: ReactNode;
}

export function ReportSection({
  icon,
  title,
  subtitle,
  children,
  defaultOpen = true,
  badge,
}: ReportSectionProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="glass-card overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between gap-4 p-6"
        style={{
          background: "transparent",
          border: "none",
          cursor: "pointer",
          textAlign: "left",
          borderBottom: open ? "1px solid #1E1E2E" : "none",
          transition: "border-color 0.2s",
        }}
      >
        <div className="flex items-center gap-3">
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 8,
              background: "rgba(79,110,247,0.12)",
              border: "1px solid rgba(79,110,247,0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#4F6EF7",
              flexShrink: 0,
            }}
          >
            {icon}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3
                className="font-display font-semibold"
                style={{ fontSize: 16, color: "#F0F0F5" }}
              >
                {title}
              </h3>
              {badge}
            </div>
            {subtitle && (
              <p style={{ fontSize: 12, color: "#8B8BA7", marginTop: 2 }}>
                {subtitle}
              </p>
            )}
          </div>
        </div>
        <div style={{ color: "#4A4A6A", flexShrink: 0 }}>
          {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </button>

      {open && (
        <div className="p-6">
          {children}
        </div>
      )}
    </div>
  );
}
