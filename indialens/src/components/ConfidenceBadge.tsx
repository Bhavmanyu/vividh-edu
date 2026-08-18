"use client";

import { Info } from "lucide-react";
import { useState } from "react";

type ConfidenceLevel = "High" | "Medium" | "Low";

const CONFIG: Record<ConfidenceLevel, { color: string; bg: string; border: string; desc: string }> = {
  High: {
    color: "#22C55E",
    bg: "rgba(34, 197, 94, 0.1)",
    border: "rgba(34, 197, 94, 0.2)",
    desc: "High confidence: Based on ≥3 verified data sources, updated within 30 days. CI width < 15 points.",
  },
  Medium: {
    color: "#F59E0B",
    bg: "rgba(245, 158, 11, 0.1)",
    border: "rgba(245, 158, 11, 0.2)",
    desc: "Medium confidence: Based on 1–2 sources or data older than 30 days. CI width 15–25 points.",
  },
  Low: {
    color: "#EF4444",
    bg: "rgba(239, 68, 68, 0.1)",
    border: "rgba(239, 68, 68, 0.2)",
    desc: "Low confidence: Limited data, imputed values, or CI width > 25 points. Interpret with caution.",
  },
};

interface ConfidenceBadgeProps {
  level: ConfidenceLevel;
  ciLow?: number;
  ciHigh?: number;
}

export function ConfidenceBadge({ level, ciLow, ciHigh }: ConfidenceBadgeProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const cfg = CONFIG[level];

  return (
    <div className="relative inline-flex">
      <button
        type="button"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onFocus={() => setShowTooltip(true)}
        onBlur={() => setShowTooltip(false)}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 4,
          padding: "2px 8px",
          borderRadius: 999,
          background: cfg.bg,
          border: `1px solid ${cfg.border}`,
          color: cfg.color,
          fontSize: 10,
          fontWeight: 700,
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          cursor: "help",
        }}
      >
        {level}
        <Info size={9} />
      </button>
      {showTooltip && (
        <div
          style={{
            position: "absolute",
            bottom: "calc(100% + 8px)",
            left: "50%",
            transform: "translateX(-50%)",
            width: 240,
            background: "#13131A",
            border: "1px solid #1E1E2E",
            borderRadius: 8,
            padding: "10px 12px",
            fontSize: 12,
            color: "#8B8BA7",
            lineHeight: 1.5,
            boxShadow: "0 8px 24px rgba(0,0,0,0.5)",
            zIndex: 50,
            pointerEvents: "none",
          }}
        >
          <p>{cfg.desc}</p>
          {ciLow !== undefined && ciHigh !== undefined && (
            <p
              className="mt-1.5 font-mono"
              style={{ color: "#F0F0F5", fontSize: 11 }}
            >
              CI: {ciLow}–{ciHigh} (±{Math.round((ciHigh - ciLow) / 2)} pts)
            </p>
          )}
          {/* Arrow */}
          <div
            style={{
              position: "absolute",
              bottom: -5,
              left: "50%",
              transform: "translateX(-50%)",
              width: 8,
              height: 8,
              background: "#1E1E2E",
              rotate: "45deg",
            }}
          />
        </div>
      )}
    </div>
  );
}
