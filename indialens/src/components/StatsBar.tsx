"use client";

import { Activity } from "lucide-react";
import { usePlatformStats } from "@/hooks/useData";

export function StatsBar() {
  const { stats, isLoading } = usePlatformStats();

  const programsIndexed   = stats?.programs_indexed      ?? 15;
  const dataPoints        = stats?.data_points_collected ?? 4280;
  const medianRoi         = stats?.median_roi_pct        ?? 187;
  const lastUpdated       = stats?.last_updated;
  const isLive            = stats?._source === "database";

  const lastUpdatedLabel = (() => {
    if (!lastUpdated) return null;
    const diffH = Math.round((Date.now() - new Date(lastUpdated).getTime()) / 3_600_000);
    if (diffH < 1)  return "< 1h ago";
    if (diffH < 24) return `${diffH}h ago`;
    return `${Math.round(diffH / 24)}d ago`;
  })();

  return (
    <div
      style={{
        background: "rgba(30,30,46,0.4)",
        borderBottom: "1px solid #1E1E2E",
        padding: "8px 0",
        backdropFilter: "blur(8px)",
      }}
    >
      <div className="container-xl">
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 8,
          }}
        >
          <div className="flex items-center gap-1.5" style={{ color: "#4A4A6A" }}>
            <Activity size={11} />
            <span style={{ fontSize: 11, letterSpacing: "0.02em" }}>
              <span className="font-mono font-semibold" style={{ color: "#8B8BA7" }}>
                {isLoading ? "—" : programsIndexed.toLocaleString()}
              </span>{" "}
              programs indexed ·{" "}
              <span className="font-mono font-semibold" style={{ color: "#8B8BA7" }}>
                {isLoading ? "—" : dataPoints >= 1_000_000
                  ? `${(dataPoints / 1_000_000).toFixed(2)}M`
                  : dataPoints.toLocaleString()}
              </span>{" "}
              data points ·{" "}
              <span className="font-mono font-semibold" style={{ color: "#8B8BA7" }}>
                {isLoading ? "—" : `${medianRoi}`}
              </span>{" "}
              median ROI score
              {/* Live / seed indicator */}
              {!isLoading && (
                <span
                  style={{
                    marginLeft: 8,
                    fontSize: 9,
                    fontWeight: 700,
                    padding: "1px 6px",
                    borderRadius: 99,
                    background: isLive ? "rgba(34,197,94,0.1)" : "rgba(245,158,11,0.1)",
                    color: isLive ? "#22C55E" : "#F59E0B",
                    border: `1px solid ${isLive ? "rgba(34,197,94,0.25)" : "rgba(245,158,11,0.25)"}`,
                    letterSpacing: "0.06em",
                  }}
                >
                  {isLive ? "LIVE" : "SEED"}
                </span>
              )}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="pulse-dot" />
            <span style={{ color: "#22C55E", fontSize: 11, fontWeight: 600 }}>
              {lastUpdatedLabel ? `Last updated ${lastUpdatedLabel}` : "Live pipeline active"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
