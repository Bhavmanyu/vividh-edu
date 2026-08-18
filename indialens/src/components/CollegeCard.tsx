"use client";

import Link from "next/link";
import { ScoreRing } from "./ScoreRing";
import { DataFreshnessBadge } from "./DataFreshnessBadge";
import { formatInr } from "../lib/mock-data";
import type { CollegeDegreeRecord } from "../lib/mock-data";
import { TrendingUp, AlertTriangle, Users } from "lucide-react";

interface CollegeCardProps {
  record: CollegeDegreeRecord;
  rank?: number;
  compact?: boolean;
}

const TIER_LABELS: Record<number, string> = { 1: "Tier 1", 2: "Tier 2", 3: "Tier 3" };
const AI_RISK_CLASS: Record<string, string> = {
  Low: "badge-green",
  Medium: "badge-yellow",
  High: "badge-red",
  "Very High": "badge-red",
};

export function CollegeCard({ record, rank, compact = false }: CollegeCardProps) {
  const { college, degree, roi, salary, placement, meta } = record;

  return (
    <Link href={`/college/${record.id}`} className="block group">
      <div
        className="glass-card p-5 transition-all duration-200 hover:border-[#4F6EF7]/40"
        style={{
          borderRadius: 8,
          transition: "transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease",
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.transform = "translateY(-2px)";
          (e.currentTarget as HTMLElement).style.boxShadow =
            "0 0 0 1px rgba(79,110,247,0.3), 0 12px 32px rgba(0,0,0,0.5)";
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.transform = "translateY(0)";
          (e.currentTarget as HTMLElement).style.boxShadow = "";
        }}
      >
        <div className="flex items-start gap-4">
          {/* Score Ring */}
          <ScoreRing score={roi.compositeScore} size={72} strokeWidth={5} />

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-1">
              <div>
                {rank && (
                  <span
                    className="text-xs font-mono font-bold"
                    style={{ color: "#4F6EF7" }}
                  >
                    #{rank}
                  </span>
                )}{" "}
                <span
                  className="text-xs font-semibold uppercase tracking-wider"
                  style={{ color: "#8B8BA7" }}
                >
                  {college.shortName}
                </span>
              </div>
              <DataFreshnessBadge days={meta.dataFreshnessDays} />
            </div>

            <h3
              className="font-display font-semibold leading-tight truncate"
              style={{ fontSize: 15, color: "#F0F0F5" }}
            >
              {degree.shortName}
            </h3>

            <div className="flex flex-wrap items-center gap-2 mt-2">
              <span className={`badge ${AI_RISK_CLASS[meta.aiRiskLabel]}`}>
                AI Risk: {meta.aiRiskLabel}
              </span>
              <span className="badge badge-blue">{TIER_LABELS[college.tier]}</span>
              <span
                className="text-xs"
                style={{ color: "#4A4A6A" }}
              >
                {college.city}
              </span>
            </div>
          </div>
        </div>

        {!compact && (
          <div
            className="grid grid-cols-3 gap-3 mt-4 pt-4"
            style={{ borderTop: "1px solid #1E1E2E" }}
          >
            <StatBlock
              icon={<TrendingUp size={12} />}
              label="Median Y1"
              value={formatInr(salary.year1.p50)}
            />
            <StatBlock
              icon={<TrendingUp size={12} />}
              label="Median Y10"
              value={formatInr(salary.year10.p50)}
            />
            <StatBlock
              icon={<Users size={12} />}
              label="Placement"
              value={`${placement.rate}%`}
            />
          </div>
        )}

        {/* Confidence bar */}
        <div className="mt-3 flex items-center gap-2">
          <div
            style={{
              flex: 1,
              height: 3,
              background: "#1E1E2E",
              borderRadius: 2,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${roi.compositeScore}%`,
                height: "100%",
                background: "linear-gradient(90deg, #4F6EF7, #8BA4FF)",
                borderRadius: 2,
              }}
            />
          </div>
          <span
            className="text-xs font-mono whitespace-nowrap"
            style={{ color: "#4A4A6A" }}
          >
            CI: {roi.confidenceIntervalLow}–{roi.confidenceIntervalHigh}
          </span>
        </div>
      </div>
    </Link>
  );
}

function StatBlock({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div>
      <div
        className="flex items-center gap-1 mb-0.5"
        style={{ color: "#4A4A6A" }}
      >
        {icon}
        <span className="text-xs" style={{ fontSize: 10, letterSpacing: "0.06em", textTransform: "uppercase" }}>
          {label}
        </span>
      </div>
      <span
        className="font-mono font-bold text-sm"
        style={{ color: "#F0F0F5" }}
      >
        {value}
      </span>
    </div>
  );
}
