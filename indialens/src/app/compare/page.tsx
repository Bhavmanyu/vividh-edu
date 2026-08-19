import React from "react";
import CollegeCompareTable from "@/components/CollegeCompareTable";
import { Scale, Plus, Sparkles, Layers } from "lucide-react";

export const metadata = {
  title: "Compare Colleges & Degrees | IndiaLens",
  description: "Compare up to 4 Indian college programs side-by-side on 20-Year NPV, placement consistency, fees, and AI risk exposure.",
};

const SAMPLE_PROGRAMS = [
  {
    id: "iit-bombay-cs",
    name: "B.Tech Computer Science",
    college: "IIT Bombay",
    tier: "1",
    fee_lakhs: 10.5,
    placement_rate_pct: 94.2,
    median_salary_lpa: 21.5,
    ai_risk_pct: 18.4,
    payback_years: 2.1,
    npv_20yr_lakhs: 142.0,
  },
  {
    id: "bits-pilani-cs",
    name: "B.E. Computer Science",
    college: "BITS Pilani",
    tier: "1",
    fee_lakhs: 24.0,
    placement_rate_pct: 91.5,
    median_salary_lpa: 19.2,
    ai_risk_pct: 19.8,
    payback_years: 3.8,
    npv_20yr_lakhs: 118.5,
  },
  {
    id: "iiit-hyderabad-cs",
    name: "B.Tech CSE",
    college: "IIIT Hyderabad",
    tier: "1",
    fee_lakhs: 16.0,
    placement_rate_pct: 98.0,
    median_salary_lpa: 26.0,
    ai_risk_pct: 16.2,
    payback_years: 2.3,
    npv_20yr_lakhs: 165.0,
  },
  {
    id: "nit-trichy-cs",
    name: "B.Tech Computer Science",
    college: "NIT Trichy",
    tier: "1",
    fee_lakhs: 6.8,
    placement_rate_pct: 88.0,
    median_salary_lpa: 14.5,
    ai_risk_pct: 22.0,
    payback_years: 2.4,
    npv_20yr_lakhs: 96.0,
  },
];

export default function ComparePage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-2">
              <Scale className="w-3.5 h-3.5" />
              Side-by-Side ROI Benchmark Matrix
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Compare Colleges & Programs
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Evaluate Net Present Value, payback horizons, fee structures, and AI risk vectors across top institutes.
            </p>
          </div>

          <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl flex items-center gap-2 shadow-lg transition-all">
            <Plus className="w-4 h-4" /> Add Program to Compare
          </button>
        </div>

        {/* Compare Matrix Table */}
        <CollegeCompareTable programs={SAMPLE_PROGRAMS} />

        {/* Insights Callout */}
        <div className="p-6 rounded-2xl bg-indigo-950/30 border border-indigo-500/20 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="space-y-1 text-center md:text-left">
            <h3 className="text-base font-bold text-white flex items-center justify-center md:justify-start gap-2">
              <Sparkles className="w-4 h-4 text-emerald-400" /> Need AI Guidance on these selections?
            </h3>
            <p className="text-xs text-slate-300">
              Our Gemini Flash AI Advisor can evaluate your personal budget against these 4 programs.
            </p>
          </div>
          <a
            href="/advisor"
            className="px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-emerald-400 text-slate-950 font-bold text-xs rounded-xl hover:opacity-90 transition-all shrink-0"
          >
            Consult AI Advisor
          </a>
        </div>
      </div>
    </main>
  );
}
