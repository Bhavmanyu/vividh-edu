/**
 * useModelStatus — Fetches ML model health and data freshness
 * Used in the footer, methodology page, and admin panel.
 */
"use client";

import { useState, useEffect } from "react";

export interface ModelStatus {
  champion: {
    version_tag: string;
    trained_at?: string;
    training_records?: number;
    validation_mae?: number;
    validation_r2?: number;
    changelog?: string;
  } | null;
  programs_indexed: number;
  last_data_update: string | null;
  model_health: "healthy" | "seed_mode" | "no_model" | "unavailable";
}

interface UseModelStatusReturn {
  status: ModelStatus | null;
  isLoading: boolean;
  refetch: () => void;
}

const SEED_STATUS: ModelStatus = {
  champion: { version_tag: "v1.0-seed", training_records: 15 },
  programs_indexed: 15,
  last_data_update: null,
  model_health: "seed_mode",
};

export function useModelStatus(): UseModelStatusReturn {
  const [status, setStatus] = useState<ModelStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;

    const fetch_ = async () => {
      setIsLoading(true);
      try {
        const resp = await fetch("/api/ml/status", {
          next: { revalidate: 60 },
        } as RequestInit);

        if (!resp.ok) throw new Error("not ok");
        const data: ModelStatus = await resp.json();
        if (!cancelled) setStatus(data);
      } catch {
        // Fallback to FastAPI health endpoint
        try {
          const resp2 = await fetch("http://localhost:8000/api/health").catch(() => null);
          if (resp2 && resp2.ok) {
            const health = await resp2.json();
            if (!cancelled) {
              setStatus({
                ...SEED_STATUS,
                champion: { version_tag: health.model_version || "v1.0-seed" },
                model_health: health.ml_status === "ready" ? "healthy" : "seed_mode",
              });
            }
          } else {
            if (!cancelled) setStatus(SEED_STATUS);
          }
        } catch {
          if (!cancelled) setStatus(SEED_STATUS);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    fetch_();
    return () => { cancelled = true; };
  }, [tick]);

  return {
    status,
    isLoading,
    refetch: () => setTick((t) => t + 1),
  };
}
