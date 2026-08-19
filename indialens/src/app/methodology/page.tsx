import type { Metadata } from "next";
import Link from "next/link";
import { BookOpen, ExternalLink, Shield, AlertTriangle, CheckCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Methodology",
  description:
    "Full technical documentation of how IndiaLens calculates composite ROI scores, salary trajectories, and risk indicators.",
};

const SOURCES = [
  {
    name: "NIRF (National Institutional Ranking Framework)",
    url: "https://nirfindia.org",
    fields: ["Placement rate", "Median salary", "Student/faculty ratio", "Infrastructure"],
    cadence: "Annual report + weekly PDF scrape",
    confidence: "High",
  },
  {
    name: "AmbitionBox",
    url: "https://ambitionbox.com",
    fields: ["Reported salaries by experience level", "Company ratings", "Work-life balance scores"],
    cadence: "Weekly scrape via API",
    confidence: "Medium",
  },
  {
    name: "Naukri.com Job Postings",
    url: "https://naukri.com",
    fields: ["Job demand by role and city", "Salary ranges in job descriptions"],
    cadence: "Weekly scrape",
    confidence: "Medium",
  },
  {
    name: "PLFS (Periodic Labour Force Survey) — MoSPI",
    url: "https://mospi.gov.in",
    fields: ["Employment rates by qualification", "Earnings distribution by education"],
    cadence: "Quarterly release",
    confidence: "High",
  },
  {
    name: "World Bank ICP (International Comparison Program)",
    url: "https://worldbank.org/icp",
    fields: ["India-US PPP conversion factors (for USD comparisons)"],
    cadence: "Quarterly",
    confidence: "High",
  },
  {
    name: "Oxford O*NET Crosswalk",
    url: "https://oxfordmartin.ox.ac.uk",
    fields: ["Automation probability by occupation (extended to Indian job types)"],
    cadence: "Annual",
    confidence: "Medium",
  },
  {
    name: "Reddit India (PRAW)",
    url: "https://reddit.com",
    fields: ["Anecdotal salary data from r/india, r/cscareerquestions_india, r/CAstudents"],
    cadence: "Weekly NLP extraction",
    confidence: "Low",
  },
];

const FORMULA_COMPONENTS = [
  {
    name: "Financial ROI (NPV & IRR)",
    weight: 35,
    formula: "NPV(20-Yr Earnings − Total Degree Cost, r=6%) / Total Degree Cost",
    inputs: [
      "Net Present Value (NPV) computed over a 20-year career horizon",
      "Internal Rate of Return (IRR) comparing college degree vs. baseline high-school labor",
      "Net Payback Horizon (Years to recover total tuition + living + opportunity cost)",
      "World Bank ICP annual PPP conversion factors for global mobility benchmarking",
    ],
    note: "Opportunity cost includes baseline earnings of non-degree entrants from MoSPI PLFS 2023-24 quarterly reports. Discount rate r=6% mirrors India's long-term RBI benchmark repo + risk premium.",
  },
  {
    name: "Risk-Adjusted Stability",
    weight: 20,
    formula: "1 − (w₁×AI_automation + w₂×salary_volatility + w₃×cyclicality + w₄×credential_inflation)",
    inputs: [
      "AI automation exposure index calibrated via Oxford O*NET extended for Indian job roles",
      "Empirical salary variance across 5-year and 10-year experience brackets",
      "Macroeconomic recession sensitivity (CMIE & MoSPI sector volatility index)",
    ],
    note: "Composite risk score evaluates 8 distinct vulnerability vectors. Weights are optimized on 5-year longitudinal salary stability data.",
  },
  {
    name: "Upside Optionality",
    weight: 15,
    formula: "P90 / P50 10-Year Salary Ratio & Convexity Score",
    inputs: [
      "90th percentile salary ceiling at Year 10",
      "50th percentile median salary at Year 10",
      "Entrepreneurship & founding exit rate derived from crunchbase / alumni data",
    ],
    note: "Measures career trajectory tail risk and upside potential. High optionality rewards degrees providing non-linear ceiling opportunities.",
  },
  {
    name: "Mobility & Market Breadth",
    weight: 15,
    formula: "f(global_visa_eligibility, remote_compatibility, tier1_city_demand_breadth)",
    inputs: [
      "International placement & H-1B / Tech Visa success rate",
      "Remote-first & hybrid work compatibility index by domain",
      "City breadth score across top 12 Indian tech & financial hubs",
    ],
    note: "Evaluates whether the degree locks a graduate into regional/specific employers or opens global mobility.",
  },
  {
    name: "Survey Psychometrics & Student Experience",
    weight: 10,
    formula: "Likert-weighted Cronbach's α Index (WLB, Mentorship, Infrastructure)",
    inputs: [
      "Verified alumni sentiment analysis across campus life and work-life balance",
      "Faculty accessibility and mentorship quality rating",
      "Hostel, lab, and digital infrastructure adequacy index",
    ],
    note: "Survey data undergoes psychometric validation (Cronbach's alpha ≥ 0.78) to ensure internal consistency and eliminate response bias.",
  },
  {
    name: "Social Capital & Alumni Network",
    weight: 5,
    formula: "log(LinkedIn_VP_Director_Density + 1) × College_Tier_Multiplier",
    inputs: [
      "Alumni leadership ratio (CXO, VP, Founder percentage at 10+ years)",
      "Peer network density across Fortune 500 and Top Indian Unicorns",
    ],
    note: "Quantifies the structural leverage provided by the institution's alumni ecosystem.",
  },
];

export default function MethodologyPage() {
  return (
    <div style={{ padding: "40px 0 80px" }}>
      <div className="container-lg" style={{ maxWidth: 800 }}>
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-2 mb-3">
            <Shield size={16} style={{ color: "#4F6EF7" }} />
            <p
              className="text-xs font-semibold uppercase tracking-wider"
              style={{ color: "#4F6EF7", letterSpacing: "0.1em" }}
            >
              Methodological Transparency
            </p>
          </div>
          <h1
            className="font-display font-bold mb-4"
            style={{ fontSize: 36, color: "#F0F0F5", letterSpacing: "-0.025em" }}
          >
            How IndiaLens Calculates ROI
          </h1>
          <p style={{ fontSize: 16, color: "#8B8BA7", lineHeight: 1.8, maxWidth: 640 }}>
            Every composite score, salary trajectory, and risk indicator is derived
            from this methodology. The formula is public, the weights are auditable,
            and the uncertainty is always shown.
          </p>
          <div
            style={{
              marginTop: 16,
              padding: "12px 16px",
              background: "rgba(79,110,247,0.06)",
              borderLeft: "3px solid #4F6EF7",
              borderRadius: "0 8px 8px 0",
            }}
          >
            <p style={{ fontSize: 13, color: "#8B8BA7" }}>
              <strong style={{ color: "#F0F0F5" }}>Cite this document:</strong> IndiaLens Research (2025).
              &ldquo;IndiaLens Degree ROI Index Methodology v1.0-seed.&rdquo; Available at:
              indialens.in/methodology
            </p>
          </div>
        </div>

        {/* Quick summary */}
        <section className="mb-12">
          <h2
            className="font-display font-bold mb-4"
            style={{ fontSize: 24, color: "#F0F0F5", letterSpacing: "-0.015em" }}
          >
            Composite Score Formula (v1.0-seed)
          </h2>

          <div className="glass-card p-6 mb-6">
            <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 14, color: "#4F6EF7", lineHeight: 1.8 }}>
              Score = 0.35 × FinancialROI
              <br />
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ 0.20 × RiskAdjustedStability
              <br />
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ 0.15 × UpsideOptionality
              <br />
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ 0.15 × MobilityPremium
              <br />
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ 0.10 × SatisfactionScore
              <br />
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ 0.05 × SocialCapitalScore
            </p>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {FORMULA_COMPONENTS.map((comp) => (
              <div key={comp.name} className="glass-card p-6">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3
                      className="font-display font-semibold"
                      style={{ fontSize: 17, color: "#F0F0F5" }}
                    >
                      {comp.name}
                    </h3>
                    <span
                      className="font-mono font-bold text-sm"
                      style={{ color: "#4F6EF7" }}
                    >
                      {comp.weight}% weight
                    </span>
                  </div>
                </div>

                <div
                  className="p-3 rounded-md mb-4"
                  style={{
                    background: "rgba(79,110,247,0.06)",
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 12,
                    color: "#7B96FF",
                  }}
                >
                  {comp.formula}
                </div>

                <div className="mb-3">
                  <p style={{ fontSize: 11, color: "#4A4A6A", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                    Inputs
                  </p>
                  {comp.inputs.map((input) => (
                    <div key={input} className="flex items-start gap-2 mb-1.5">
                      <CheckCircle size={11} style={{ color: "#22C55E", marginTop: 3, flexShrink: 0 }} />
                      <span style={{ fontSize: 13, color: "#8B8BA7" }}>{input}</span>
                    </div>
                  ))}
                </div>

                <div
                  className="flex items-start gap-2"
                  style={{ borderTop: "1px solid #1E1E2E", paddingTop: 12 }}
                >
                  <AlertTriangle size={11} style={{ color: "#F59E0B", marginTop: 3, flexShrink: 0 }} />
                  <p style={{ fontSize: 12, color: "#4A4A6A", lineHeight: 1.6 }}>
                    <strong style={{ color: "#8B8BA7" }}>Note:</strong> {comp.note}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Data sources */}
        <section className="mb-12">
          <h2
            className="font-display font-bold mb-6"
            style={{ fontSize: 24, color: "#F0F0F5", letterSpacing: "-0.015em" }}
          >
            Data Sources
          </h2>
          <div className="space-y-3">
            {SOURCES.map((src) => (
              <div key={src.name} className="glass-card p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <a
                        href={src.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          fontSize: 15,
                          fontWeight: 600,
                          color: "#F0F0F5",
                          textDecoration: "none",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: 4,
                        }}
                      >
                        {src.name}
                        <ExternalLink size={11} style={{ color: "#4A4A6A" }} />
                      </a>
                    </div>
                    <p style={{ fontSize: 11, color: "#4A4A6A", marginBottom: 8 }}>
                      {src.cadence}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {src.fields.map((f) => (
                        <span
                          key={f}
                          style={{
                            padding: "2px 8px",
                            borderRadius: 999,
                            fontSize: 11,
                            background: "#1E1E2E",
                            color: "#8B8BA7",
                            border: "1px solid #2A2A3E",
                          }}
                        >
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                  <span
                    style={{
                      padding: "2px 10px",
                      borderRadius: 999,
                      fontSize: 10,
                      fontWeight: 700,
                      background:
                        src.confidence === "High"
                          ? "rgba(34,197,94,0.1)"
                          : src.confidence === "Medium"
                          ? "rgba(245,158,11,0.1)"
                          : "rgba(239,68,68,0.1)",
                      border: `1px solid ${
                        src.confidence === "High"
                          ? "rgba(34,197,94,0.2)"
                          : src.confidence === "Medium"
                          ? "rgba(245,158,11,0.2)"
                          : "rgba(239,68,68,0.2)"
                      }`,
                      color:
                        src.confidence === "High"
                          ? "#22C55E"
                          : src.confidence === "Medium"
                          ? "#F59E0B"
                          : "#EF4444",
                      whiteSpace: "nowrap",
                      flexShrink: 0,
                    }}
                  >
                    {src.confidence}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Uncertainty section */}
        <section className="mb-12">
          <h2
            className="font-display font-bold mb-4"
            style={{ fontSize: 24, color: "#F0F0F5", letterSpacing: "-0.015em" }}
          >
            How We Handle Uncertainty
          </h2>
          <div className="space-y-4">
            {[
              {
                q: "Why do salary predictions show ranges, not single numbers?",
                a: "Because single-number salary predictions are epistemically dishonest. Any prediction at a 20-year horizon has massive uncertainty from macroeconomic changes, personal performance, and industry disruption. We always display p25–p75 confidence intervals.",
              },
              {
                q: "What is a Confidence Interval (CI) score?",
                a: "Each composite score also has a CI, expressed as two numbers (e.g., 71–89 for a score of 82). The CI reflects the range of scores we'd assign given our data uncertainty. A score with a CI width > 25 gets a 'Low Confidence' badge.",
              },
              {
                q: "How do we handle missing data?",
                a: "We impute missing values using within-tier, within-field averages, then apply a confidence penalty proportional to the imputation fraction. Imputed fields are always disclosed in the data provenance panel.",
              },
              {
                q: "What's the model version and how often does it retrain?",
                a: "v1.0-seed is a seed model trained on 15 hand-verified programs. Production plan: weekly retraining triggered by scraper runs + anomaly queue resolution. Full model version history will be published.",
              },
            ].map((item) => (
              <div key={item.q} className="glass-card p-5">
                <h3 style={{ fontSize: 14, fontWeight: 600, color: "#F0F0F5", marginBottom: 8 }}>
                  {item.q}
                </h3>
                <p style={{ fontSize: 13, color: "#8B8BA7", lineHeight: 1.7 }}>{item.a}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Feedback CTA */}
        <div
          className="glass-card p-6 text-center"
          style={{ borderColor: "rgba(79,110,247,0.3)" }}
        >
          <BookOpen size={20} style={{ color: "#4F6EF7", margin: "0 auto 12px" }} />
          <h3 className="font-display font-semibold mb-2" style={{ fontSize: 18, color: "#F0F0F5" }}>
            Found an error? Help us improve.
          </h3>
          <p style={{ fontSize: 13, color: "#8B8BA7", marginBottom: 20 }}>
            If you&apos;re an educator, researcher, or placement officer with better data,
            please submit a correction. Your institution will be credited.
          </p>
          <Link href="/admin" className="btn-primary">
            <Shield size={14} />
            Submit a Data Correction
          </Link>
        </div>
      </div>
    </div>
  );
}
