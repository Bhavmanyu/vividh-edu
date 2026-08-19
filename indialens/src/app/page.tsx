import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRight,
  BarChart2,
  Brain,
  Shield,
  TrendingUp,
  Database,
  Cpu,
  ChevronRight,
  CheckCircle,
  ExternalLink,
} from "lucide-react";
import { ScoreRing } from "@/components/ScoreRing";
import { CollegeCard } from "@/components/CollegeCard";
import { MOCK_DATA, PLATFORM_STATS, formatInr } from "../lib/mock-data";

export const metadata: Metadata = {
  title: "IndiaLens — Know the real return on your degree",
  description:
    "India's first quantitative education ROI platform. Updated weekly. Peer-reviewed methodology. Free for students.",
};

const TOP_THREE = [MOCK_DATA[0], MOCK_DATA[8], MOCK_DATA[9]]; // IIT Bombay CSE, AIIMS MBBS, IIM MBA

const HOW_IT_WORKS = [
  {
    step: "01",
    title: "We scrape",
    desc: "12 data sources scraped every week — NIRF, AmbitionBox, Naukri, PLFS, World Bank ICP, Reddit, and more.",
    icon: <Database size={20} />,
  },
  {
    step: "02",
    title: "We score",
    desc: "A 6-component ROI formula weighs financial return, risk, optionality, mobility, satisfaction, and social capital.",
    icon: <Cpu size={20} />,
  },
  {
    step: "03",
    title: "You decide",
    desc: "Every score has a source. Every prediction shows uncertainty. No black boxes — ever.",
    icon: <Brain size={20} />,
  },
];

const SAMPLE_COMPARISON = MOCK_DATA.slice(0, 3);

export default function LandingPage() {
  return (
    <div>
      {/* ── HERO ─────────────────────────────────────────────────────── */}
      <section className="hero-gradient" style={{ padding: "80px 0 64px" }}>
        <div className="container-lg">
          <div style={{ maxWidth: 760 }}>
            {/* Eyebrow */}
            <div
              className="flex items-center gap-2 mb-6 animate-fade-in"
              style={{ opacity: 0, animationFillMode: "forwards" }}
            >
              <span className="badge badge-blue">
                <span className="pulse-dot" style={{ width: 5, height: 5 }} />
                BETA
              </span>
              <span
                className="text-xs font-mono"
                style={{ color: "#4A4A6A" }}
              >
                v1.0 · {PLATFORM_STATS.collegesTracked} colleges indexed
              </span>
            </div>

            {/* Headline */}
            <h1
              className="font-display animate-slide-up stagger-1"
              style={{
                fontSize: "clamp(2.8rem, 6vw, 5rem)",
                fontWeight: 700,
                lineHeight: 1.05,
                letterSpacing: "-0.03em",
                color: "#F0F0F5",
                opacity: 0,
                animationFillMode: "forwards",
                marginBottom: 24,
              }}
            >
              Know the{" "}
              <span className="gradient-text-blue">real return</span>
              <br />
              on your degree.
            </h1>

            <p
              className="animate-slide-up stagger-2"
              style={{
                fontSize: "clamp(1rem, 2vw, 1.2rem)",
                color: "#8B8BA7",
                lineHeight: 1.7,
                maxWidth: 560,
                opacity: 0,
                animationFillMode: "forwards",
                marginBottom: 36,
              }}
            >
              India&apos;s first quantitative education intelligence platform.
              ROI scores, salary trajectories, and AI automation risk for every
              major college × degree combination.{" "}
              <span style={{ color: "#F0F0F5" }}>Data verified and updated continuously.</span>
            </p>

            {/* CTAs */}
            <div
              className="flex flex-wrap items-center gap-3 animate-slide-up stagger-3"
              style={{ opacity: 0, animationFillMode: "forwards" }}
            >
              <Link href="/analyze" className="btn-primary" style={{ fontSize: 15, padding: "13px 28px" }}>
                Find your ROI
                <ArrowRight size={16} />
              </Link>
              <Link href="/explore" className="btn-secondary" style={{ fontSize: 15, padding: "12px 24px" }}>
                <BarChart2 size={14} />
                Browse the Index
              </Link>
            </div>

            {/* Social proof */}
            <div
              className="flex flex-wrap items-center gap-6 mt-10 pt-8 animate-fade-in stagger-4"
              style={{
                borderTop: "1px solid #1E1E2E",
                opacity: 0,
                animationFillMode: "forwards",
              }}
            >
              {[
                { value: "55", label: "Colleges indexed" },
                { value: "73", label: "Programs tracked" },
                { value: "6", label: "ROI components" },
                { value: "Free", label: "Always" },
              ].map((stat) => (
                <div key={stat.label}>
                  <div
                    className="font-display font-bold"
                    style={{ fontSize: 22, color: "#F0F0F5", letterSpacing: "-0.02em" }}
                  >
                    {stat.value}
                  </div>
                  <div style={{ fontSize: 12, color: "#4A4A6A" }}>{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── ROI TEASER (3 sample cards) ───────────────────────────── */}
      <section style={{ padding: "64px 0" }}>
        <div className="container-lg">
          <div className="flex items-end justify-between mb-8">
            <div>
              <p
                className="text-xs font-semibold uppercase tracking-wider mb-2"
                style={{ color: "#4F6EF7", letterSpacing: "0.1em" }}
              >
                Sample from the Index
              </p>
              <h2
                className="font-display"
                style={{ fontSize: 28, fontWeight: 700, color: "#F0F0F5", letterSpacing: "-0.02em" }}
              >
                Not all degrees are equal
              </h2>
            </div>
            <Link
              href="/explore"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                fontSize: 13,
                color: "#4F6EF7",
                textDecoration: "none",
                fontWeight: 600,
              }}
            >
              Browse the Index
              <ChevronRight size={14} />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {SAMPLE_COMPARISON.map((record, i) => (
              <div
                key={record.id}
                className="animate-slide-up"
                style={{
                  opacity: 0,
                  animationDelay: `${i * 0.1}s`,
                  animationFillMode: "forwards",
                }}
              >
                <CollegeCard record={record} rank={i + 1} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── THREE PRODUCTS ────────────────────────────────────────── */}
      <section
        style={{
          padding: "64px 0",
          background: "rgba(19,19,26,0.5)",
          borderTop: "1px solid #1E1E2E",
          borderBottom: "1px solid #1E1E2E",
        }}
      >
        <div className="container-lg">
          <div className="text-center mb-12">
            <p
              className="text-xs font-semibold uppercase tracking-wider mb-2"
              style={{ color: "#F7C94F", letterSpacing: "0.1em" }}
            >
              Three products in one
            </p>
            <h2
              className="font-display"
              style={{ fontSize: 32, fontWeight: 700, color: "#F0F0F5", letterSpacing: "-0.02em" }}
            >
              Built for the full lifecycle
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: <BarChart2 size={22} />,
                color: "#4F6EF7",
                title: "Degree ROI Index",
                desc: "A public, weekly-updated index ranking every major Indian degree × college by composite ROI. Searchable, filterable, exportable. Designed to be cited by journalists and researchers.",
                href: "/index",
                cta: "Browse the Index",
              },
              {
                icon: <Brain size={22} />,
                color: "#22C55E",
                title: "Student ROI Engine",
                desc: "Enter your academic profile, budget, and goals. Receive a ranked list of college-degree combinations with 20-year salary trajectories, risk scores, and a personalized coursework roadmap.",
                href: "/analyze",
                cta: "Analyze my profile",
              },
              {
                icon: <TrendingUp size={22} />,
                color: "#F7C94F",
                title: "AI Displacement Tracker",
                desc: "Track AI-driven job market shifts and district-level opportunity across India. Automation probability by occupation, with weekly trend signals from job postings and Reddit NLP.",
                href: "#",
                cta: "Coming soon",
                disabled: true,
              },
            ].map((product) => (
              <div key={product.title} className="glass-card p-6">
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: 10,
                    background: `${product.color}15`,
                    border: `1px solid ${product.color}25`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: product.color,
                    marginBottom: 16,
                  }}
                >
                  {product.icon}
                </div>
                <h3
                  className="font-display font-semibold mb-3"
                  style={{ fontSize: 18, color: "#F0F0F5", letterSpacing: "-0.01em" }}
                >
                  {product.title}
                </h3>
                <p
                  style={{ fontSize: 14, color: "#8B8BA7", lineHeight: 1.7, marginBottom: 20 }}
                >
                  {product.desc}
                </p>
                {product.disabled ? (
                  <span className="badge badge-gold">{product.cta}</span>
                ) : (
                  <Link
                    href={product.href}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 6,
                      fontSize: 13,
                      fontWeight: 600,
                      color: product.color,
                      textDecoration: "none",
                    }}
                  >
                    {product.cta}
                    <ArrowRight size={13} />
                  </Link>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ──────────────────────────────────────────── */}
      <section style={{ padding: "80px 0" }}>
        <div className="container-lg">
          <div className="text-center mb-12">
            <p
              className="text-xs font-semibold uppercase tracking-wider mb-2"
              style={{ color: "#8B8BA7", letterSpacing: "0.1em" }}
            >
              The pipeline
            </p>
            <h2
              className="font-display"
              style={{ fontSize: 32, fontWeight: 700, color: "#F0F0F5", letterSpacing: "-0.02em" }}
            >
              How IndiaLens works
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {HOW_IT_WORKS.map((step, i) => (
              <div key={step.step} className="relative">
                {i < HOW_IT_WORKS.length - 1 && (
                  <div
                    className="hidden md:block absolute top-8 left-full w-full"
                    style={{
                      height: 1,
                      background: "linear-gradient(90deg, #4F6EF7, transparent)",
                      width: "calc(100% - 48px)",
                      marginLeft: 24,
                    }}
                  />
                )}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    marginBottom: 16,
                  }}
                >
                  <div
                    style={{
                      width: 40,
                      height: 40,
                      borderRadius: 10,
                      background: "rgba(79,110,247,0.1)",
                      border: "1px solid rgba(79,110,247,0.2)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "#4F6EF7",
                    }}
                  >
                    {step.icon}
                  </div>
                  <span
                    className="font-mono font-bold"
                    style={{ fontSize: 12, color: "#4A4A6A" }}
                  >
                    {step.step}
                  </span>
                </div>
                <h3
                  className="font-display font-semibold mb-3"
                  style={{ fontSize: 20, color: "#F0F0F5" }}
                >
                  {step.title}
                </h3>
                <p style={{ fontSize: 14, color: "#8B8BA7", lineHeight: 1.7 }}>
                  {step.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── METHODOLOGY TRUST BLOCK ──────────────────────────────── */}
      <section
        style={{
          padding: "64px 0",
          background: "rgba(79,110,247,0.04)",
          borderTop: "1px solid rgba(79,110,247,0.12)",
          borderBottom: "1px solid rgba(79,110,247,0.12)",
        }}
      >
        <div className="container-lg">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Shield size={16} style={{ color: "#4F6EF7" }} />
                <p
                  className="text-xs font-semibold uppercase tracking-wider"
                  style={{ color: "#4F6EF7", letterSpacing: "0.1em" }}
                >
                  Methodological Transparency
                </p>
              </div>
              <h2
                className="font-display font-bold mb-4"
                style={{ fontSize: 28, color: "#F0F0F5", letterSpacing: "-0.02em" }}
              >
                Our formula is fully public.
                <br />
                Peer reviewed. Open to challenge.
              </h2>
              <p style={{ color: "#8B8BA7", fontSize: 14, lineHeight: 1.8, marginBottom: 24 }}>
                Every composite score decomposes into six weighted components.
                Every salary prediction shows a confidence interval, not just a
                number. Every data point links back to its source.
              </p>
              <div className="flex flex-col gap-3">
                {[
                  "6-component ROI formula with public weights",
                  "All predictions show p25–p75 ranges",
                  "Weekly scrape timestamps on every data point",
                  "Educator feedback loop corrects model errors",
                  "Model version history publicly accessible",
                ].map((item) => (
                  <div key={item} className="flex items-start gap-3">
                    <CheckCircle
                      size={14}
                      style={{ color: "#22C55E", marginTop: 3, flexShrink: 0 }}
                    />
                    <span style={{ fontSize: 14, color: "#8B8BA7" }}>{item}</span>
                  </div>
                ))}
              </div>
              <Link
                href="/methodology"
                className="btn-secondary mt-6 inline-flex"
                style={{ fontSize: 13 }}
              >
                <ExternalLink size={13} />
                Read the methodology
              </Link>
            </div>

            {/* Formula preview */}
            <div className="glass-card p-6">
              <p
                className="text-xs font-semibold uppercase tracking-wider mb-4"
                style={{ color: "#4A4A6A", letterSpacing: "0.08em" }}
              >
                Master Formula
              </p>
              {[
                { label: "PPP-Adjusted Financial ROI", weight: "35%", color: "#4F6EF7" },
                { label: "Risk-Adjusted Stability", weight: "20%", color: "#22C55E" },
                { label: "Upside Optionality", weight: "15%", color: "#F7C94F" },
                { label: "Mobility Premium", weight: "15%", color: "#A78BFA" },
                { label: "Satisfaction & Wellbeing", weight: "10%", color: "#F97316" },
                { label: "Social Capital & Network", weight: "5%", color: "#EC4899" },
              ].map((component) => (
                <div key={component.label} className="flex items-center gap-3 mb-3">
                  <div
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background: component.color,
                      flexShrink: 0,
                    }}
                  />
                  <span style={{ fontSize: 13, color: "#8B8BA7", flex: 1 }}>
                    {component.label}
                  </span>
                  <span
                    className="font-mono font-bold text-sm"
                    style={{ color: component.color }}
                  >
                    {component.weight}
                  </span>
                </div>
              ))}
              <div
                style={{
                  borderTop: "1px solid #1E1E2E",
                  paddingTop: 12,
                  marginTop: 8,
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span style={{ fontSize: 12, color: "#4A4A6A" }}>
                  Composite Score (0–100)
                </span>
                <span
                  className="font-mono font-bold"
                  style={{ color: "#F0F0F5", fontSize: 16 }}
                >
                  = Σ weights
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ─────────────────────────────────────────────────────── */}
      <section style={{ padding: "80px 0", textAlign: "center" }}>
        <div className="container-lg" style={{ maxWidth: 600, margin: "0 auto" }}>
          <h2
            className="font-display font-bold mb-4"
            style={{ fontSize: 36, color: "#F0F0F5", letterSpacing: "-0.03em" }}
          >
            Your degree decision.
            <br />
            <span className="gradient-text-blue">Make it quantitatively.</span>
          </h2>
          <p
            style={{
              fontSize: 16,
              color: "#8B8BA7",
              lineHeight: 1.7,
              marginBottom: 36,
            }}
          >
            8 questions. 3 minutes. A personalized ROI report with 20-year
            salary trajectories for your specific profile.
          </p>
          <Link
            href="/analyze"
            className="btn-primary"
            style={{ fontSize: 16, padding: "14px 36px" }}
          >
            Start your analysis
            <ArrowRight size={16} />
          </Link>
          <p
            style={{
              fontSize: 12,
              color: "#4A4A6A",
              marginTop: 16,
            }}
          >
            Free. No account required. No dark patterns.
          </p>
        </div>
      </section>
    </div>
  );
}
