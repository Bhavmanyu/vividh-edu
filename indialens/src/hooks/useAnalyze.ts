/**
 * useAnalyze — React hook for the Student ROI Engine
 *
 * Wraps the POST /api/analyze and GET /api/analyze/{token} endpoints.
 * Handles loading states, error boundaries, and caching.
 */
"use client";

import { useState, useCallback } from "react";

export interface StudentProfilePayload {
  tenth_pct?: number;
  twelfth_pct?: number;
  twelfth_stream?: string;
  jee_rank?: number;
  neet_score?: number;
  backlog?: string;
  family_income?: string;
  total_budget: number;
  loan_willingness?: string;
  home_state?: string;
  relocation_india?: string;
  relocation_abroad?: string;
  primary_goals: string[];
  risk_appetite: number;
  wlb_priority: number;
  fields_of_interest?: string[];
  sports_level?: string;
  coding_level?: string;
  entrepreneurship_level?: string;
}

export interface TrajectoryBand {
  p10?: number;
  p25: number;
  p50: number;
  p75: number;
  p90: number;
}

export interface Recommendation {
  rank: number;
  programId: string;
  collegeName: string;
  degreeName: string;
  state: string;
  tier?: string;
  compositeScore?: number;
  fitScore: number;
  trajectory: Record<string, TrajectoryBand>;
  predictedSalaryY1?: number;
  predictedSalaryY5?: number;
  totalCostInr?: number;
  placementRate?: number;
  reasons: string[];
  topRisks?: string[];
}

export interface AnalyzeFlag {
  type: string;
  title: string;
  message: string;
  severity: "info" | "warning" | "success" | "error";
}

export interface AnalyzeResult {
  token: string;
  recommendations: Recommendation[];
  profile_parsed: StudentProfilePayload;
  flags: AnalyzeFlag[];
  model_version: string;
  using_ml: boolean;
  generated_at: string;
  _source: string;
}

interface UseAnalyzeReturn {
  result: AnalyzeResult | null;
  isLoading: boolean;
  error: string | null;
  submit: (profile: StudentProfilePayload) => Promise<AnalyzeResult | null>;
  fetchReport: (token: string) => Promise<AnalyzeResult | null>;
  reset: () => void;
}

export function useAnalyze(): UseAnalyzeReturn {
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = useCallback(async (profile: StudentProfilePayload) => {
    setIsLoading(true);
    setError(null);

    try {
      const resp = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });

      if (!resp.ok) {
        const errData = await resp.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error: ${resp.status}`);
      }

      const data: AnalyzeResult = await resp.json();
      setResult(data);

      // Persist token for sharing / direct URL
      if (data.token && typeof window !== "undefined") {
        sessionStorage.setItem("indialens_report_token", data.token);
      }

      return data;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setError(msg);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchReport = useCallback(async (token: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const resp = await fetch(`/api/analyze?token=${token}`);
      if (!resp.ok) {
        throw new Error(`Report not found: ${resp.status}`);
      }
      const data: AnalyzeResult = await resp.json();
      setResult(data);
      return data;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setError(msg);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { result, isLoading, error, submit, fetchReport, reset };
}
