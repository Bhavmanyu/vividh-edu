"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import {
  User, TrendingUp, AlertTriangle, Gem, BookOpen,
  LayoutGrid, ArrowRight, Download, Share2, Info,
  ChevronDown, ChevronUp, ArrowLeft, Lightbulb,
} from "lucide-react";
import { ScoreRing } from "@/components/ScoreRing";
import { RiskGrid } from "@/components/RiskGrid";
import { SalaryTrajectory } from "@/components/SalaryTrajectory";
import { ReportSection } from "@/components/ReportSection";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { MOCK_DATA, formatInr } from "../../../lib/mock-data";
import { useState } from "react";
import { useReport } from "@/hooks/useData";

// Sample report data (in production, fetched by token from API)
const SAMPLE_REPORT = {
  profileSummary: {
    parsed: {
      stream: "Science PCM",
      academicStrength: "High (12th: 91%)",
      budget: "₹25L total",
      goalPrimary: "High Salary + Prestige",
      riskAppetite: "Moderate (6/10)",
      wlbPriority: "4/10",
      location: "Open to anywhere in India",
      flags: [
        {
          type: "contradiction",
          msg: "You ranked Work-Life Balance at 4/10 but also selected Investment Banking as an interest — these are in direct conflict. IB associates routinely work 80–100 hours/week.",
        },
      ],
    },
  },
  recommendations: MOCK_DATA.slice(0, 5).map((r, i) => ({
    rank: i + 1,
    ...r,
    fitScore: 95 - i * 8,
    reasons: [
      `Strong alignment with your Science PCM background and stated goal of high salary`,
      `Financial ROI of ${r.roi.financialRoiPct.toLocaleString()}% exceeds your budget of ₹25L by ${Math.round(r.roi.financialRoiPct / 100)}×`,
      `${r.college.state} location is within your relocation preference`,
    ],
    topRisks: [
      `AI automation risk at ${Math.round(r.risk.aiAutomationProbability * 100)}% — mitigated by early specialization`,
      `Credential inflation growing at ${Math.round(r.risk.credentialInflation * 10)}% YoY in this field`,
    ],
  })),
  hiddenGem: {
    ...MOCK_DATA[3], // IIIT Hyderabad CSE
    gemReason: "IIIT Hyderabad has 34% less competition than IITs for research roles, and alumni data shows 22% higher LinkedIn seniority index at the 10-year mark than expected for its rank. Your strong Math background is a better fit for its dual-degree research track than standard B.Tech programs.",
    modelConfidence: 68,
  },
  roadmap: {
    college: MOCK_DATA[0],
    years: [
      {
        year: "Year 1",
        focus: "Foundation",
        skills: ["Data Structures & Algorithms", "Linear Algebra", "Python fundamentals", "One open source contribution"],
        milestone: "Join at least 1 research lab or competitive programming club",
      },
      {
        year: "Year 2",
        focus: "Technical depth",
        skills: ["Machine Learning basics", "Database systems", "Web development fundamentals", "1 internship (target: ₹30K+/mo stipend)"],
        milestone: "Complete a Kaggle competition or contribute to an ML paper",
      },
      {
        year: "Year 3",
        focus: "Specialization + Network",
        skills: ["Cloud (AWS/GCP)", "System design", "Domain specialization (AI/Systems/Security)", "2nd internship (target: ₹60K+/mo)"],
        milestone: "Pre-placement offer or research publication",
      },
      {
        year: "Year 4",
        focus: "Placement + Launch",
        skills: ["Interview prep (DSA + system design)", "MBA/MS GRE prep (if targeting)", "Personal brand (GitHub/LinkedIn/blog)"],
        milestone: "₹15–25L CTC placement or FAANG interview",
      },
    ],
  },
  pathNotTaken: {
    title: "Product Management at a tech startup",
    description: "Your combination of technical aptitude (92% PCM), high-agency personality (took charge in Q1), and dislike of purely solo work strongly signals Product Management. A CS degree + 3 years SWE experience + MBA path typically yields ₹40–80L by age 30 — comparable to the IIT CSE base case trajectory but with significantly better work-life balance.",
    roiComparison: {
      recommended: 94,
      alternative: 78,
      note: "Lower composite ROI but 40% better WLB score",
    },
  },
};

export default function ReportPage() {
  const params = useParams();
  const token = params?.token as string;
  const [expandedRec, setExpandedRec] = useState<number | null>(0);
  const { data, isLoading, error } = useReport(token);
  const [shareCopied, setShareCopied] = useState(false);

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setShareCopied(true);
    setTimeout(() => setShareCopied(false), 2000);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-400 font-mono text-sm">Loading your personalized report...</p>
      </div>
    );
  }

  if (error || !data || data._source === 'not_found') {
    return (
      <div className="container-lg py-16 text-center">
        <AlertTriangle size={48} className="mx-auto text-red-500 mb-4" />
        <h1 className="text-2xl font-bold mb-2">Report Not Found</h1>
        <p className="text-gray-400 mb-6">This report does not exist or has expired.</p>
        <Link href="/analyze" className="btn-primary">Create New Report</Link>
      </div>
    );
  }

  // Map backend structure to frontend structure expected by the template
  // If backend is already close to reportData, we use it directly, else fallback to reportData for structure mapping (since it is a mock)
  const reportData = (data.results || SAMPLE_REPORT) as typeof SAMPLE_REPORT;
  const expiresAt = data.expires_at ? new Date(data.expires_at) : new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
  const daysLeft = Math.ceil((expiresAt.getTime() - Date.now()) / (1000 * 60 * 60 * 24));


  const { profileSummary, recommendations, hiddenGem, roadmap, pathNotTaken } = reportData;

  
  const reportHeader = (
    <div className="glass-card mb-8 p-4 flex flex-wrap gap-4 items-center justify-between" style={{ borderLeft: "4px solid #4F6EF7" }}>
      <div className="flex items-center gap-3">
        <Info size={18} style={{ color: "#4F6EF7" }} />
        <span style={{ fontSize: 14, color: "#F0F0F5" }}>
          This report expires in {daysLeft} days.
        </span>
      </div>
      <div className="flex gap-3">
        <button onClick={handleShare} className="btn-secondary" style={{ padding: "8px 16px", fontSize: 13 }}>
          <Share2 size={16} />
          {shareCopied ? "Copied!" : "Share Link"}
        </button>
        <button onClick={() => alert('PDF export coming soon')} className="btn-secondary" style={{ padding: "8px 16px", fontSize: 13 }}>
          <Download size={16} />
          Download PDF
        </button>
      </div>
    </div>
  );

  return (
    <div style={{ padding: "40px 0 80px" }}>
        {reportHeader}

      <div className="container-lg" style={{ maxWidth: 820 }}>
        {/* Header */}
        <div className="flex flex-col md:flex-row items-start justify-between gap-4 mb-8">
          <div>
            <Link
              href="/analyze"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                fontSize: 13,
                color: "#8B8BA7",
                textDecoration: "none",
                marginBottom: 8,
              }}
            >
              <ArrowLeft size={14} />
              New analysis
            </Link>
            <h1
              className="font-display font-bold"
              style={{ fontSize: 28, color: "#F0F0F5", letterSpacing: "-0.02em" }}
            >
              Your ROI Report
            </h1>
            <p style={{ fontSize: 13, color: "#8B8BA7", marginTop: 4 }}>
              Token: <span className="font-mono" style={{ color: "#4A4A6A" }}>{token}</span> ·{" "}
              Shareable at{" "}
              <span className="font-mono" style={{ color: "#4F6EF7" }}>
                indialens.in/report/{token}
              </span>
            </p>
          </div>
          <div className="flex gap-2">
            <button className="btn-secondary" style={{ fontSize: 13 }}>
              <Share2 size={13} />
              Share
            </button>
            <button className="btn-secondary" style={{ fontSize: 13 }}>
              <Download size={13} />
              PDF
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {/* 1 — Profile Summary */}
          <ReportSection icon={<User size={16} />} title="Your Profile Summary" subtitle="What the model understood about you">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
              {Object.entries(profileSummary.parsed)
                .filter(([k]) => k !== "flags")
                .map(([key, value]) => (
                  <div key={key} className="glass-card p-3">
                    <p style={{ fontSize: 10, color: "#4A4A6A", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>
                      {key.replace(/_/g, " ")}
                    </p>
                    <p style={{ fontSize: 13, color: "#F0F0F5", fontWeight: 600 }}>{String(value)}</p>
                  </div>
                ))}
            </div>
            {profileSummary.parsed.flags.map((flag, i) => (
              <div
                key={i}
                style={{
                  padding: "12px 16px",
                  borderRadius: 8,
                  background: "rgba(245,158,11,0.08)",
                  border: "1px solid rgba(245,158,11,0.25)",
                  display: "flex",
                  gap: 10,
                }}
              >
                <AlertTriangle size={14} style={{ color: "#F59E0B", flexShrink: 0, marginTop: 2 }} />
                <p style={{ fontSize: 13, color: "#8B8BA7", lineHeight: 1.6 }}>{flag.msg}</p>
              </div>
            ))}
          </ReportSection>

          {/* 2 — Top 5 Recommendations */}
          <ReportSection
            icon={<TrendingUp size={16} />}
            title="Top 5 Recommendations"
            subtitle="Ranked by predicted personal ROI for your specific profile"
          >
            <div className="space-y-3">
              {recommendations.map((rec, i) => (
                <div key={rec.id} className="glass-card overflow-hidden">
                  <button
                    type="button"
                    onClick={() => setExpandedRec(expandedRec === i ? null : i)}
                    className="w-full p-5"
                    style={{
                      background: "transparent",
                      border: "none",
                      cursor: "pointer",
                      textAlign: "left",
                    }}
                  >
                    <div className="flex items-center gap-4">
                      <div
                        className="font-mono font-bold"
                        style={{ fontSize: 24, color: "#4A4A6A", minWidth: 32 }}
                      >
                        #{rec.rank}
                      </div>
                      <ScoreRing score={rec.roi.compositeScore} size={56} strokeWidth={4} showLabel={false} animate={false} />
                      <div className="flex-1 text-left">
                        <p style={{ fontWeight: 700, fontSize: 15, color: "#F0F0F5", letterSpacing: "-0.01em" }}>
                          {rec.college.shortName} — {rec.degree.shortName}
                        </p>
                        <p style={{ fontSize: 12, color: "#8B8BA7", marginTop: 2 }}>
                          {rec.college.city} · {rec.college.type} · {rec.college.state}
                        </p>
                      </div>
                      <div className="text-right flex flex-col items-end gap-2">
                        <span
                          className="font-mono font-bold text-lg"
                          style={{ color: "#22C55E" }}
                        >
                          {rec.fitScore}% fit
                        </span>
                        <ConfidenceBadge
                          level="High"
                          ciLow={rec.roi.confidenceIntervalLow}
                          ciHigh={rec.roi.confidenceIntervalHigh}
                        />
                      </div>
                      <div style={{ color: "#4A4A6A" }}>
                        {expandedRec === i ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </div>
                    </div>
                  </button>

                  {expandedRec === i && (
                    <div style={{ padding: "0 20px 20px", borderTop: "1px solid #1E1E2E" }}>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 mb-4">
                        {[
                          { label: "Year 1 (base)", value: formatInr(rec.salary.year1.p50) },
                          { label: "Year 5 (base)", value: formatInr(rec.salary.year5.p50) },
                          { label: "Year 10 (base)", value: formatInr(rec.salary.year10.p50) },
                          { label: "Year 20 (base)", value: formatInr(rec.salary.year20.p50) },
                        ].map((s) => (
                          <div key={s.label}>
                            <p style={{ fontSize: 10, color: "#4A4A6A", marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                              {s.label}
                            </p>
                            <p className="font-mono font-bold" style={{ fontSize: 15, color: "#F0F0F5" }}>
                              {s.value}
                            </p>
                          </div>
                        ))}
                      </div>
                      <SalaryTrajectory salaryByYear={rec.salary} />
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                        <div>
                          <p style={{ fontSize: 11, fontWeight: 700, color: "#22C55E", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                            Why it fits you
                          </p>
                          {rec.reasons.map((r, ri) => (
                            <div key={ri} className="flex items-start gap-2 mb-2">
                              <span style={{ color: "#22C55E", marginTop: 4, flexShrink: 0 }}>·</span>
                              <p style={{ fontSize: 13, color: "#8B8BA7", lineHeight: 1.6 }}>{r}</p>
                            </div>
                          ))}
                        </div>
                        <div>
                          <p style={{ fontSize: 11, fontWeight: 700, color: "#EF4444", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                            Top risks for you
                          </p>
                          {rec.topRisks.map((r, ri) => (
                            <div key={ri} className="flex items-start gap-2 mb-2">
                              <AlertTriangle size={12} style={{ color: "#EF4444", marginTop: 3, flexShrink: 0 }} />
                              <p style={{ fontSize: 13, color: "#8B8BA7", lineHeight: 1.6 }}>{r}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                      <Link
                        href={`/college/${rec.id}`}
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: 6,
                          fontSize: 13,
                          color: "#4F6EF7",
                          textDecoration: "none",
                          marginTop: 16,
                          fontWeight: 600,
                        }}
                      >
                        Full program analysis <ArrowRight size={13} />
                      </Link>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </ReportSection>

          {/* 3 — Hidden Gem */}
          <ReportSection
            icon={<Gem size={16} />}
            title="Hidden Gem Pick"
            subtitle="Lower certainty, but strong signal for your specific profile"
            badge={
              <span className="badge badge-gold" style={{ fontSize: 10 }}>
                Model confidence: {hiddenGem.modelConfidence}%
              </span>
            }
          >
            <div className="flex items-start gap-4">
              <ScoreRing score={hiddenGem.roi.compositeScore} size={72} strokeWidth={5} />
              <div className="flex-1">
                <h3 className="font-display font-semibold" style={{ fontSize: 18, color: "#F0F0F5" }}>
                  {hiddenGem.college.shortName} — {hiddenGem.degree.shortName}
                </h3>
                <p style={{ fontSize: 13, color: "#8B8BA7", marginTop: 8, lineHeight: 1.7 }}>
                  {hiddenGem.gemReason}
                </p>
                <div className="flex items-center gap-3 mt-4">
                  <span className="badge badge-gold">Model confidence: {hiddenGem.modelConfidence}%</span>
                  <Link href={`/college/${hiddenGem.id}`} style={{ fontSize: 13, color: "#4F6EF7", textDecoration: "none" }}>
                    Full analysis →
                  </Link>
                </div>
              </div>
            </div>
          </ReportSection>

          {/* 4 — Coursework Roadmap */}
          <ReportSection
            icon={<BookOpen size={16} />}
            title="Coursework Roadmap"
            subtitle={`Year-by-year skill stack for ${roadmap.college.college.shortName} ${roadmap.college.degree.shortName}`}
            defaultOpen={false}
          >
            <div className="space-y-4">
              {roadmap.years.map((yr, i) => (
                <div
                  key={yr.year}
                  style={{
                    display: "flex",
                    gap: 16,
                    paddingBottom: i < roadmap.years.length - 1 ? 16 : 0,
                    borderBottom: i < roadmap.years.length - 1 ? "1px solid #1E1E2E" : "none",
                  }}
                >
                  <div style={{ flexShrink: 0, textAlign: "center" }}>
                    <div
                      style={{
                        width: 36,
                        height: 36,
                        borderRadius: "50%",
                        background: "rgba(79,110,247,0.12)",
                        border: "1px solid rgba(79,110,247,0.2)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "#4F6EF7",
                        fontSize: 11,
                        fontWeight: 700,
                      }}
                    >
                      Y{i + 1}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F0F5" }}>{yr.year}</p>
                      <span className="badge badge-blue" style={{ fontSize: 9 }}>{yr.focus}</span>
                    </div>
                    <div className="flex flex-wrap gap-2 mb-3">
                      {yr.skills.map((skill) => (
                        <span
                          key={skill}
                          style={{
                            padding: "3px 10px",
                            borderRadius: 999,
                            fontSize: 11,
                            background: "#1E1E2E",
                            color: "#8B8BA7",
                            border: "1px solid #2A2A3E",
                          }}
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                    <p style={{ fontSize: 12, color: "#4F6EF7" }}>🎯 {yr.milestone}</p>
                  </div>
                </div>
              ))}
            </div>
          </ReportSection>

          {/* 5 — Risk Dashboard */}
          <ReportSection
            icon={<LayoutGrid size={16} />}
            title="Risk Dashboard"
            subtitle="Your personalized risk profile for the top recommendation"
            defaultOpen={false}
          >
            <RiskGrid
              items={[
                { label: "AI Automation Risk", value: 0.32, description: "32% probability of automation in 10 years" },
                { label: "Credential Inflation", value: 0.15, description: "CS grads growing at 8% YoY vs 12% job growth" },
                { label: "Burnout Risk", value: 0.55, description: "Based on your WLB priority (4/10) + field avg" },
                { label: "Geographic Concentration", value: 0.2, description: "CSE jobs available in 15+ Indian cities" },
                { label: "Financial Downside Risk", value: 0.18, description: "P25 salary still covers loan repayment" },
                { label: "Industry Cyclicality", value: 0.35, description: "Tech sector recessions ~every 8 years" },
              ]}
            />
          </ReportSection>

          {/* 6 — Path Not Taken */}
          <ReportSection
            icon={<Lightbulb size={16} />}
            title="The Path Not Taken"
            subtitle="One alternative you likely haven't considered"
            defaultOpen={false}
          >
            <div>
              <h3 className="font-display font-semibold mb-3" style={{ fontSize: 18, color: "#F7C94F" }}>
                {pathNotTaken.title}
              </h3>
              <p style={{ fontSize: 14, color: "#8B8BA7", lineHeight: 1.7, marginBottom: 16 }}>
                {pathNotTaken.description}
              </p>
              <div className="flex items-center gap-6">
                <div>
                  <p style={{ fontSize: 11, color: "#4A4A6A", marginBottom: 4 }}>Recommended path</p>
                  <div className="flex items-center gap-2">
                    <ScoreRing score={pathNotTaken.roiComparison.recommended} size={48} strokeWidth={4} showLabel={false} animate={false} />
                    <span className="font-mono font-bold" style={{ fontSize: 16, color: "#F0F0F5" }}>
                      {pathNotTaken.roiComparison.recommended}/100
                    </span>
                  </div>
                </div>
                <ArrowRight size={20} style={{ color: "#4A4A6A" }} />
                <div>
                  <p style={{ fontSize: 11, color: "#4A4A6A", marginBottom: 4 }}>Alternative path</p>
                  <div className="flex items-center gap-2">
                    <ScoreRing score={pathNotTaken.roiComparison.alternative} size={48} strokeWidth={4} showLabel={false} animate={false} />
                    <span className="font-mono font-bold" style={{ fontSize: 16, color: "#F0F0F5" }}>
                      {pathNotTaken.roiComparison.alternative}/100
                    </span>
                  </div>
                </div>
                <p style={{ fontSize: 12, color: "#8B8BA7", fontStyle: "italic" }}>
                  {pathNotTaken.roiComparison.note}
                </p>
              </div>
            </div>
          </ReportSection>

          {/* 7 — Data transparency */}
          <div
            className="glass-card p-4"
            style={{ borderLeft: "3px solid #1E1E2E" }}
          >
            <div className="flex items-start gap-2">
              <Info size={13} style={{ color: "#4A4A6A", marginTop: 2, flexShrink: 0 }} />
              <p style={{ fontSize: 12, color: "#4A4A6A", lineHeight: 1.6 }}>
                This report used data last updated{" "}
                <span style={{ color: "#8B8BA7" }}>3 hours ago</span> · Model version{" "}
                <span className="font-mono" style={{ color: "#8B8BA7" }}>v1.0-seed</span> ·
                Confidence:{" "}
                <span style={{ color: "#22C55E" }}>High</span> · 847 colleges in our database ·
                15 programs indexed for your field ·{" "}
                <Link href="/methodology" style={{ color: "#4F6EF7", textDecoration: "none" }}>
                  Full methodology →
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
