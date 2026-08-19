"use client";

import React from "react";
import { Check, X, ArrowUpRight, ShieldAlert, Award, DollarSign, Briefcase } from "lucide-react";

interface ProgramItem {
  id: string;
  name: string;
  college: string;
  tier: string;
  fee_lakhs: number;
  placement_rate_pct: number;
  median_salary_lpa: number;
  ai_risk_pct: number;
  payback_years: number;
  npv_20yr_lakhs: number;
}

interface CollegeCompareTableProps {
  programs: ProgramItem[];
}

export default function CollegeCompareTable({ programs }: CollegeCompareTableProps) {
  if (!programs || programs.length === 0) {
    return (
      <div className="p-8 text-center bg-slate-900/60 border border-slate-800 rounded-2xl text-slate-400">
        No colleges selected for comparison. Add programs to compare ROI.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/90 backdrop-blur-md shadow-2xl">
      <table className="w-full text-left border-collapse min-w-[650px]">
        <thead>
          <tr className="border-b border-slate-800 bg-slate-950/80">
            <th className="p-4 text-xs font-bold text-slate-400 uppercase tracking-wider w-1/4">Metric</th>
            {programs.map((p) => (
              <th key={p.id} className="p-4 text-sm font-bold text-white border-l border-slate-800/80">
                <div className="text-indigo-400 text-xs font-semibold">{p.college}</div>
                <div className="text-base text-white font-extrabold">{p.name}</div>
                <span className="inline-block mt-1 text-[10px] px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                  Tier {p.tier}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/80 text-sm">
          {/* Total Cost / Fee */}
          <tr>
            <td className="p-4 font-semibold text-slate-300 flex items-center gap-1.5">
              <DollarSign className="w-4 h-4 text-amber-400" /> Total Degree Fee
            </td>
            {programs.map((p) => (
              <td key={p.id} className="p-4 border-l border-slate-800/80 text-white font-bold">
                ₹{p.fee_lakhs} Lakhs
              </td>
            ))}
          </tr>

          {/* Placement Rate */}
          <tr>
            <td className="p-4 font-semibold text-slate-300 flex items-center gap-1.5">
              <Briefcase className="w-4 h-4 text-emerald-400" /> Placement Consistency
            </td>
            {programs.map((p) => (
              <td key={p.id} className="p-4 border-l border-slate-800/80 text-emerald-400 font-bold">
                {p.placement_rate_pct}%
              </td>
            ))}
          </tr>

          {/* Median Starting Salary */}
          <tr>
            <td className="p-4 font-semibold text-slate-300 flex items-center gap-1.5">
              <Award className="w-4 h-4 text-indigo-400" /> Median Year-1 Salary
            </td>
            {programs.map((p) => (
              <td key={p.id} className="p-4 border-l border-slate-800/80 text-indigo-300 font-bold">
                ₹{p.median_salary_lpa} LPA
              </td>
            ))}
          </tr>

          {/* Payback Horizon */}
          <tr>
            <td className="p-4 font-semibold text-slate-300">Net Payback Horizon</td>
            {programs.map((p) => (
              <td key={p.id} className="p-4 border-l border-slate-800/80 text-slate-200">
                {p.payback_years} Years
              </td>
            ))}
          </tr>

          {/* 20-Year NPV */}
          <tr className="bg-emerald-500/5">
            <td className="p-4 font-bold text-emerald-400">20-Year Net Present Value (NPV)</td>
            {programs.map((p) => (
              <td key={p.id} className="p-4 border-l border-slate-800/80 text-emerald-400 font-extrabold text-base">
                ₹{p.npv_20yr_lakhs} Lakhs
              </td>
            ))}
          </tr>

          {/* AI Automation Exposure */}
          <tr>
            <td className="p-4 font-semibold text-slate-300 flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-red-400" /> AI Automation Risk
            </td>
            {programs.map((p) => (
              <td key={p.id} className="p-4 border-l border-slate-800/80">
                <span className={`font-bold ${p.ai_risk_pct > 30 ? "text-amber-400" : "text-emerald-400"}`}>
                  {p.ai_risk_pct}%
                </span>
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
