"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  TrendingUp,
  Shield,
  Globe,
  Star,
  Users,
  AlertTriangle,
  Database,
  ChevronRight,
} from "lucide-react";
import { ScoreRing } from "@/components/ScoreRing";
import { ROIBreakdown } from "@/components/ROIBreakdown";
import { RiskGrid } from "@/components/RiskGrid";
import { SalaryTrajectory } from "@/components/SalaryTrajectory";
import { DataFreshnessBadge } from "@/components/DataFreshnessBadge";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { CollegeCard } from "@/components/CollegeCard";
import JobMarketCard from "@/components/JobMarketCard";
import EcosystemBadge from "@/components/EcosystemBadge";
import PsychometricsRadar from "@/components/PsychometricsRadar";
import AIAdvisorWidget from "@/components/AIAdvisorWidget";
import { MOCK_DATA, formatInr } from "../../../lib/mock-data";
import { useCollege } from "@/hooks/useData";

export default function CollegeDetailPage() {
  const params = useParams();
  const id = params?.id as string;

  const { data: record, isLoading, error } = useCollege(id);

  if (isLoading) {
    return (
      <div style={{ padding: "120px 24px", textAlign: "center" }}>
        <p style={{ color: "#8B8BA7" }}>Loading program details…</p>
      </div>
    );
  }

  if (!record) {
    return (
      <div style={{ padding: "80px 24px", textAlign: "center" }}>
        <p style={{ color: "#8B8BA7" }}>{error || "Program not found."}</p>
        <Link href="/explore" className="btn-primary mt-4 inline-flex">
          Back to Index
        </Link>
      </div>
    );
  }

  const jsonLd = record ? {
    "@context": "https://schema.org",
    "@type": "EducationalOrganization",
    "name": `${record.college.name} — ${record.degree.name}`,
    "description": `ROI score ${record.roi.compositeScore}/100. Median salary ₹${((record.salary?.year1?.p50 ?? 0) / 100000).toFixed(1)}L at graduation.`,
    "url": `https://indialens.in/college/${id}`,
    "offers": {
      "@type": "Offer",
      "price": `${record.costs?.totalCostOfDegreeInr ?? 0}`,
      "priceCurrency": "INR"
    }
  } : null;


  const similar = MOCK_DATA.filter(
    (r) => r.id !== record.id && r.degree.field === record.degree.field
  ).slice(0, 3);

  const { college, degree, roi, salary, placement, risk, costs, meta } = record;

  const riskItems = [
    { label: "AI Automation Risk", value: risk.aiAutomationProbability, description: "Probability occupation is automated in 10 years (Oxford O*NET crosswalk)" },
    { label: "Salary Volatility", value: risk.salaryVolatility, description: "Std deviation of salary distribution (AmbitionBox data)" },
    { label: "Industry Cyclicality", value: risk.industryCyclicality, description: "Sensitivity to economic cycles (RBI KLEMS data)" },
    { label: "Credential Inflation", value: risk.credentialInflation, description: "Graduate supply growing faster than job demand" },
    { label: "Geographic Concentration", value: risk.geographicConcentration, description: "Jobs concentrated in 1–2 cities" },
    { label: "Regulatory Risk", value: risk.regulatoryRisk, description: "Government policy can cap income (e.g. public sector pay bands)" },
    { label: "Physical Health Risk", value: risk.physicalHealthRisk, description: "Occupational health hazards" },
    { label: "Work-Life Quality", value: 1 - risk.workLifeQuality, description: "Burnout risk (higher = worse WLB)" },
  ];

  const ciWidth = roi.confidenceIntervalHigh - roi.confidenceIntervalLow;
  const confidenceLevel = ciWidth < 10 ? "High" : ciWidth < 20 ? "Medium" : "Low";

  return (
    <div style={{ padding: "40px 0 80px" }}>
      {jsonLd && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      )}
      <div className="container-lg">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 mb-8">
          <Link
            href="/explore"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              fontSize: 13,
              color: "#8B8BA7",
              textDecoration: "none",
            }}
          >
            <ArrowLeft size={14} />
            ROI Index
          </Link>
          <ChevronRight size={12} style={{ color: "#4A4A6A" }} />
          <span style={{ fontSize: 13, color: "#4A4A6A" }}>{college.shortName}</span>
          <ChevronRight size={12} style={{ color: "#4A4A6A" }} />
          <span style={{ fontSize: 13, color: "#F0F0F5" }}>{degree.shortName}</span>
        </div>

        {/* Header */}
        <div className="glass-card p-8 mb-6">
          <div className="flex flex-col md:flex-row items-start gap-8">
            <ScoreRing score={roi.compositeScore} size={120} strokeWidth={8} />
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-3">
                <span className="badge badge-blue">
                  {college.type} · Tier {college.tier}
                </span>
                <span className="badge badge-gold">
                  NIRF #{college.nirfRank}
                </span>
                <ConfidenceBadge
                  level={confidenceLevel as "High" | "Medium" | "Low"}
                  ciLow={roi.confidenceIntervalLow}
                  ciHigh={roi.confidenceIntervalHigh}
                />
                <DataFreshnessBadge days={meta.dataFreshnessDays} />
              </div>
              <h1
                className="font-display font-bold mb-1"
                style={{ fontSize: 28, color: "#F0F0F5", letterSpacing: "-0.025em" }}
              >
                {college.name}
              </h1>
              <h2
                style={{ fontSize: 18, color: "#8B8BA7", fontWeight: 500, marginBottom: 20 }}
              >
                {degree.name}
              </h2>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {[
                  {
                    icon: <TrendingUp size={14} />,
                    label: "Financial ROI",
                    value: `${roi.financialRoiPct.toLocaleString()}%`,
                    color: "#4F6EF7",
                  },
                  {
                    icon: <Shield size={14} />,
                    label: "Risk Score",
                    value: `${Math.round(roi.riskScore * 100)}/100`,
                    color: roi.riskScore < 0.3 ? "#22C55E" : roi.riskScore < 0.5 ? "#F59E0B" : "#EF4444",
                  },
                  {
                    icon: <Users size={14} />,
                    label: "Placement Rate",
                    value: `${placement.rate}%`,
                    color: "#22C55E",
                  },
                  {
                    icon: <Star size={14} />,
                    label: "Median Salary Y1",
                    value: formatInr(salary.year1.p50),
                    color: "#F7C94F",
                  },
                ].map((stat) => (
                  <div key={stat.label}>
                    <div
                      className="flex items-center gap-1.5 mb-1"
                      style={{ color: "#4A4A6A" }}
                    >
                      {stat.icon}
                      <span style={{ fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>
                        {stat.label}
                      </span>
                    </div>
                    <span
                      className="font-mono font-bold"
                      style={{ fontSize: 18, color: stat.color }}
                    >
                      {stat.value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: ROI Breakdown + Salary trajectory */}
          <div className="lg:col-span-2 space-y-6">
            {/* Salary Trajectory */}
            <div className="glass-card p-6">
              <h3
                className="font-display font-semibold mb-1"
                style={{ fontSize: 18, color: "#F0F0F5" }}
              >
                Salary Trajectory
              </h3>
              <p style={{ fontSize: 12, color: "#8B8BA7", marginBottom: 20 }}>
                Conservative (p25) / Base Case (p50) / Optimistic (p75) · Confidence Interval: {roi.confidenceIntervalLow}–{roi.confidenceIntervalHigh}
              </p>
              <SalaryTrajectory salaryByYear={salary} />
              <div
                className="grid grid-cols-4 gap-4 mt-4 pt-4"
                style={{ borderTop: "1px solid #1E1E2E" }}
              >
                {[
                  { year: "Year 1", data: salary.year1 },
                  { year: "Year 5", data: salary.year5 },
                  { year: "Year 10", data: salary.year10 },
                  { year: "Year 20", data: salary.year20 },
                ].map((s) => (
                  <div key={s.year}>
                    <p style={{ fontSize: 10, color: "#4A4A6A", marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                      {s.year}
                    </p>
                    <p className="font-mono font-bold" style={{ fontSize: 13, color: "#F0F0F5" }}>
                      {formatInr(s.data.p50)}
                    </p>
                    <p style={{ fontSize: 10, color: "#4A4A6A" }}>
                      {formatInr(s.data.p25)}–{formatInr(s.data.p75)}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* ROI Breakdown */}
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3
                  className="font-display font-semibold"
                  style={{ fontSize: 18, color: "#F0F0F5" }}
                >
                  ROI Formula Breakdown
                </h3>
                <Link
                  href="/methodology"
                  style={{ fontSize: 12, color: "#4F6EF7", textDecoration: "none" }}
                >
                  Methodology →
                </Link>
              </div>
              <ROIBreakdown
                financialRoi={roi.financialRoiPct}
                riskScore={roi.riskScore}
                optionalityScore={roi.optionalityScore}
                mobilityScore={roi.mobilityScore}
                satisfactionScore={roi.satisfactionScore}
                networkScore={roi.networkScore}
              />
            </div>

            {/* Cost breakdown */}
            <div className="glass-card p-6">
              <h3
                className="font-display font-semibold mb-4"
                style={{ fontSize: 18, color: "#F0F0F5" }}
              >
                Total Cost of Degree
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: "Tuition (total)", value: costs.totalTuitionInr },
                  { label: "Hostel & Living", value: costs.hostelLivingInr },
                  { label: "Exam Prep (JEE etc)", value: costs.examPrepCostsInr },
                  { label: "Opportunity Cost", value: costs.opportunityCostInr },
                ].map((item) => (
                  <div key={item.label}>
                    <p style={{ fontSize: 11, color: "#4A4A6A", marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                      {item.label}
                    </p>
                    <p className="font-mono font-bold" style={{ fontSize: 15, color: "#F0F0F5" }}>
                      {formatInr(item.value)}
                    </p>
                  </div>
                ))}
              </div>
              <div
                style={{ borderTop: "1px solid #1E1E2E", paddingTop: 12, marginTop: 12 }}
              >
                <div className="flex justify-between items-center">
                  <span style={{ fontSize: 13, color: "#8B8BA7" }}>Total Cost of Degree</span>
                  <span className="font-mono font-bold" style={{ fontSize: 18, color: "#EF4444" }}>
                    {formatInr(costs.totalCostOfDegreeInr)}
                  </span>
                </div>
                <p style={{ fontSize: 11, color: "#4A4A6A", marginTop: 4 }}>
                  Includes opportunity cost — what you'd earn if you'd taken a job after 12th (avg PLFS data)
                </p>
              </div>
            </div>

            {/* City Job Market Demand Telemetry */}
            <JobMarketCard initialField={degree.field} initialCity="bengaluru" />

            {/* Student Experience Psychometrics Radar */}
            <PsychometricsRadar />

            {/* GitHub & Wikidata Ecosystem Badge */}
            <EcosystemBadge universityName={college.name} />

            {/* AI Advisor Floating Consultation Widget */}
            <AIAdvisorWidget
              initialBudget={Math.round((costs?.totalCostOfDegreeInr || 1000000) / 100000)}
              initialField={degree.field}
            />
          </div>

          {/* Right: Risk grid + raw data + similar */}
          <div className="space-y-6">
            {/* Risk grid */}
            <div className="glass-card p-6">
              <h3
                className="font-display font-semibold mb-4"
                style={{ fontSize: 18, color: "#F0F0F5" }}
              >
                Risk Dashboard
              </h3>
              <RiskGrid items={riskItems} />
            </div>

            {/* Data provenance */}
            <div className="glass-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <Database size={14} style={{ color: "#4A4A6A" }} />
                <h3
                  className="font-display font-semibold"
                  style={{ fontSize: 16, color: "#F0F0F5" }}
                >
                  Data Sources
                </h3>
              </div>
              {[
                { source: "NIRF 2024", fields: "Placement %, fees, student count", updated: `${meta.dataFreshnessDays}d ago` },
                { source: "AmbitionBox", fields: "Salary by experience, satisfaction", updated: `${meta.dataFreshnessDays + 2}d ago` },
                { source: "Oxford O*NET", fields: "Automation probability", updated: "Annually" },
                { source: "World Bank ICP", fields: "PPP conversion factors", updated: "Quarterly" },
              ].map((src) => (
                <div
                  key={src.source}
                  style={{
                    paddingBottom: 10,
                    marginBottom: 10,
                    borderBottom: "1px solid #1E1E2E",
                  }}
                >
                  <div className="flex justify-between items-start">
                    <p style={{ fontSize: 12, fontWeight: 600, color: "#F0F0F5" }}>
                      {src.source}
                    </p>
                    <span style={{ fontSize: 10, color: "#4A4A6A" }}>{src.updated}</span>
                  </div>
                  <p style={{ fontSize: 11, color: "#4A4A6A", marginTop: 2 }}>
                    {src.fields}
                  </p>
                </div>
              ))}
              <p style={{ fontSize: 10, color: "#4A4A6A" }}>
                Model version: {meta.scrapeSource.split("+")[0].trim()}
              </p>
            </div>
          </div>
        </div>

        {/* Similar programs */}
        {similar.length > 0 && (
          <div className="mt-8">
            <h2
              className="font-display font-semibold mb-4"
              style={{ fontSize: 22, color: "#F0F0F5" }}
            >
              Similar Programs
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {similar.map((r) => (
                <CollegeCard key={r.id} record={r} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
