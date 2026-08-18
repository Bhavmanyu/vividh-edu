/**
 * useColleges — Fetches paginated/filtered programs list
 * Drives the /index ROI table.
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import type { CollegeDegreeRecord } from "@/lib/mock-data";

export interface CollegesQuery {
  page?: number;
  per_page?: number;
  field?: string;
  tier?: string;
  state?: string;
  search?: string;
  sort_by?: string;
  sort_dir?: "asc" | "desc";
}

export interface CollegesResponse {
  data: CollegeDegreeRecord[];
  total: number;
  page: number;
  per_page: number;
  model_version: string;
  generated_at: string;
  _source: "database" | "mock";
}

export function useColleges(query: CollegesQuery = {}) {
  const [response, setResponse] = useState<CollegesResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch_ = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    const params = new URLSearchParams();
    if (query.page)      params.set("page",     String(query.page));
    if (query.per_page)  params.set("per_page", String(query.per_page));
    if (query.field)     params.set("field",    query.field);
    if (query.tier)      params.set("tier",     query.tier);
    if (query.state)     params.set("state",    query.state);
    if (query.search)    params.set("search",   query.search);
    if (query.sort_by)   params.set("sort_by",  query.sort_by);
    if (query.sort_dir)  params.set("sort_dir", query.sort_dir);

    try {
      const resp = await fetch(`/api/colleges?${params.toString()}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data: CollegesResponse = await resp.json();
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setIsLoading(false);
    }
  }, [
    query.page, query.per_page, query.field, query.tier,
    query.state, query.search, query.sort_by, query.sort_dir,
  ]);

  useEffect(() => { fetch_(); }, [fetch_]);

  return { response, isLoading, error, refetch: fetch_ };
}

/**
 * useCollege — Fetches a single program detail by ID.
 * Drives the /college/[id] detail page.
 */
export function useCollege(id: string) {
  const [data, setData] = useState<CollegeDegreeRecord | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    fetch(`/api/colleges/${id}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d) => { if (!cancelled) setData(d); })
      .catch((e) => { if (!cancelled) setError(e.message); })
      .finally(() => { if (!cancelled) setIsLoading(false); });

    return () => { cancelled = true; };
  }, [id]);

  return { data, isLoading, error };
}

/**
 * usePlatformStats — Live stats for landing page and StatsBar.
 * Falls back to computed mock stats if API unavailable.
 */
export interface PlatformStats {
  programs_indexed: number;
  data_points_collected: number;
  median_roi_pct: number;
  last_updated: string | null;
  model_version: string;
  _source: "database" | "mock";
}

export function usePlatformStats() {
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/colleges/stats")
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((d) => { if (!cancelled) setStats(d); })
      .catch(() => {
        if (!cancelled) setStats({
          programs_indexed: 15,
          data_points_collected: 4_280,
          median_roi_pct: 187,
          last_updated: null,
          model_version: "v1.0-seed",
          _source: "mock",
        });
      })
      .finally(() => { if (!cancelled) setIsLoading(false); });

    return () => { cancelled = true; };
  }, []);

  return { stats, isLoading };
}

/**
 * useAdminQueue — Anomaly queue and scrape run history for /admin page.
 */
export interface Anomaly {
  id: string;
  program_id: string;
  college_name: string;
  degree_name: string;
  field_name: string;
  prior_value: string | null;
  new_value: string;
  delta_pct: number;
  status: "pending" | "accepted" | "rejected";
  created_at: string;
}

export interface ScrapeRun {
  id: string;
  source_name: string;
  started_at: string;
  completed_at: string | null;
  status: string;
  records_scraped: number;
  records_updated: number;
  records_flagged: number;
  error_message: string | null;
}

export function useAdminQueue(apiKey: string) {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [scrapeRuns, setScrapeRuns] = useState<ScrapeRun[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const headers = { "X-API-KEY": apiKey };

  const fetchAll = useCallback(async () => {
    if (!apiKey) return;
    setIsLoading(true);
    try {
      const [aq, sr] = await Promise.all([
        fetch("/api/admin/anomalies", { headers }).then((r) => r.json()),
        fetch("/api/admin/scrape-runs", { headers }).then((r) => r.json()),
      ]);
      setAnomalies(aq.anomalies ?? []);
      setScrapeRuns(sr.runs ?? []);
    } catch (e) {
      setError("Failed to load admin data. Check API key.");
    } finally {
      setIsLoading(false);
    }
  }, [apiKey]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const reviewAnomaly = async (id: string, action: "accept" | "reject", notes?: string) => {
    await fetch(`/api/admin/anomalies/${id}`, {
      method: "POST",
      headers: { ...headers, "Content-Type": "application/json" },
      body: JSON.stringify({ action, notes }),
    });
    fetchAll(); // refresh queue
  };

  const triggerScrape = async (source: string) => {
    await fetch(`/api/admin/scrape/${source}`, { method: "POST", headers });
    setTimeout(fetchAll, 2000);
  };

  const triggerRetrain = async () => {
    await fetch("/api/ml/retrain", { method: "POST", headers });
  };

  return {
    anomalies, scrapeRuns, isLoading, error,
    reviewAnomaly, triggerScrape, triggerRetrain, refresh: fetchAll,
  };
}


export interface SavedReport {
  token: string;
  created_at: string;
  expires_at: string;
  student_input: any; 
  results: any;       
  _source: 'database' | 'not_found';
}

export function useReport(token: string) {
  const [data, setData] = useState<SavedReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    fetch(`/api/report/${token}`)
      .then((r) => {
        if (!r.ok) {
          if (r.status === 404) return null;
          throw new Error(`HTTP ${r.status}`);
        }
        return r.json();
      })
      .then((d) => { if (!cancelled) setData(d); })
      .catch((e) => { if (!cancelled) setError(e.message); })
      .finally(() => { if (!cancelled) setIsLoading(false); });

    return () => { cancelled = true; };
  }, [token]);

  return { data, isLoading, error };
}
