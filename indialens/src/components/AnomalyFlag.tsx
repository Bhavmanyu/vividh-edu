"use client";

import { AlertTriangle, Clock, CheckCircle, XCircle } from "lucide-react";

interface AnomalyFlagProps {
  field: string;
  priorValue: string | number;
  newValue: string | number;
  deltaPct: number;
  status: "pending" | "accepted" | "rejected";
  onAccept?: () => void;
  onReject?: () => void;
}

const STATUS_CONFIG = {
  pending: {
    color: "#F59E0B",
    icon: <Clock size={12} />,
    label: "Pending Review",
  },
  accepted: {
    color: "#22C55E",
    icon: <CheckCircle size={12} />,
    label: "Accepted",
  },
  rejected: {
    color: "#EF4444",
    icon: <XCircle size={12} />,
    label: "Rejected",
  },
};

export function AnomalyFlag({
  field,
  priorValue,
  newValue,
  deltaPct,
  status,
  onAccept,
  onReject,
}: AnomalyFlagProps) {
  const cfg = STATUS_CONFIG[status];
  const isLarge = Math.abs(deltaPct) > 40;

  return (
    <div
      style={{
        border: `1px solid ${isLarge ? "rgba(239,68,68,0.3)" : "rgba(245,158,11,0.3)"}`,
        borderRadius: 8,
        background: isLarge ? "rgba(239,68,68,0.05)" : "rgba(245,158,11,0.05)",
        padding: "12px 16px",
      }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-2">
          <AlertTriangle
            size={14}
            style={{
              color: isLarge ? "#EF4444" : "#F59E0B",
              marginTop: 2,
              flexShrink: 0,
            }}
          />
          <div>
            <p
              className="font-semibold text-sm"
              style={{ color: "#F0F0F5" }}
            >
              {field}
            </p>
            <div className="flex items-center gap-3 mt-1">
              <span
                className="font-mono text-xs"
                style={{ color: "#8B8BA7" }}
              >
                {priorValue}
              </span>
              <span style={{ color: "#4A4A6A", fontSize: 10 }}>→</span>
              <span
                className="font-mono text-xs font-bold"
                style={{ color: "#F0F0F5" }}
              >
                {newValue}
              </span>
              <span
                className="text-xs font-mono font-bold"
                style={{ color: isLarge ? "#EF4444" : "#F59E0B" }}
              >
                {deltaPct > 0 ? "+" : ""}{deltaPct.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 4,
              padding: "2px 8px",
              borderRadius: 999,
              background: `${cfg.color}15`,
              border: `1px solid ${cfg.color}30`,
              color: cfg.color,
              fontSize: 10,
              fontWeight: 600,
            }}
          >
            {cfg.icon}
            {cfg.label}
          </span>

          {status === "pending" && (
            <div className="flex gap-1">
              <button
                onClick={onAccept}
                className="btn-secondary"
                style={{ padding: "4px 10px", fontSize: 11, borderRadius: 4 }}
              >
                Accept
              </button>
              <button
                onClick={onReject}
                style={{
                  padding: "4px 10px",
                  fontSize: 11,
                  borderRadius: 4,
                  background: "rgba(239,68,68,0.1)",
                  border: "1px solid rgba(239,68,68,0.2)",
                  color: "#EF4444",
                  cursor: "pointer",
                }}
              >
                Reject
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
