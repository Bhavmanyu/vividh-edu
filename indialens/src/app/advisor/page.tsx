import React from "react";
import AIAdvisorWidget from "@/components/AIAdvisorWidget";
import { Sparkles, Bot, Shield, TrendingUp, HelpCircle } from "lucide-react";

export const metadata = {
  title: "AI Career & ROI Advisor | IndiaLens",
  description: "Consult IndiaLens AI powered by Google Gemini 1.5 Flash for personalized career counseling, budget optimization, and ROI strategies.",
};

export default function AdvisorPage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            Powered by Google Gemini 1.5 Flash
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-indigo-300">
            IndiaLens AI Career & ROI Advisor
          </h1>
          <p className="text-slate-400 text-sm max-w-2xl mx-auto">
            Get instant quantitative guidance on college selection, loan payback horizons, AI automation exposure, and geographic career mobility.
          </p>
        </div>

        {/* AI Advisor Core Widget */}
        <AIAdvisorWidget className="shadow-2xl border-slate-800" />

        {/* Informational Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
              <TrendingUp className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-bold text-white">NPV & IRR Financial Modeling</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Calculates 20-year net earnings minus tuition, hostel, and high-school baseline opportunity cost at an 8% discount rate.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold">
              <Shield className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-bold text-white">10-Year AI Automation Exposure</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Evaluates degree vulnerabilities using Oxford O*NET automation tasks calibrated for Indian engineering and management roles.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center font-bold">
              <Bot className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-bold text-white">Psychometrics & Student Experience</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Synthesizes student reviews into Cronbach&apos;s $\alpha$ internal consistency scores ($\ge 0.78$) across faculty, WLB, and infrastructure.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
