"use client";

import { Clock } from "lucide-react";

interface DataFreshnessBadgeProps {
  days: number;
  showIcon?: boolean;
}

export function DataFreshnessBadge({ days, showIcon = true }: DataFreshnessBadgeProps) {
  let color: string;
  let bg: string;
  let border: string;
  let label: string;

  if (days <= 7) {
    color = "#22C55E";
    bg = "rgba(34, 197, 94, 0.1)";
    border = "rgba(34, 197, 94, 0.2)";
    label = days === 0 ? "Today" : `${days}d ago`;
  } else if (days <= 30) {
    color = "#F59E0B";
    bg = "rgba(245, 158, 11, 0.1)";
    border = "rgba(245, 158, 11, 0.2)";
    label = `${days}d ago`;
  } else {
    color = "#EF4444";
    bg = "rgba(239, 68, 68, 0.1)";
    border = "rgba(239, 68, 68, 0.2)";
    label = days >= 365 ? `${Math.floor(days / 30)}mo ago` : `${days}d ago`;
  }

  return (
    <span
      title={`Data last updated ${days} days ago${days > 30 ? " — consider reviewing" : ""}`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
        padding: "2px 8px",
        borderRadius: 999,
        background: bg,
        border: `1px solid ${border}`,
        color,
        fontSize: 10,
        fontWeight: 600,
        letterSpacing: "0.04em",
        whiteSpace: "nowrap",
        cursor: "default",
      }}
    >
      {showIcon && <Clock size={9} />}
      {label}
    </span>
  );
}
