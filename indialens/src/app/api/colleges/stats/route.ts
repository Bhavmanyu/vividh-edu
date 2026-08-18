import { NextResponse } from "next/server";
import { MOCK_DATA } from "@/lib/mock-data";

const FASTAPI_BASE = process.env.FASTAPI_URL ?? "http://localhost:8000";

/** GET /api/colleges/stats — live platform stats for landing page + StatsBar */
export async function GET() {
  // Try FastAPI
  try {
    const [countResp, dpResp, roiResp] = await Promise.all([
      fetch(`${FASTAPI_BASE}/api/colleges?page=1&per_page=1`),
      fetch(`${FASTAPI_BASE}/api/ml/status`),
      fetch(`${FASTAPI_BASE}/api/colleges?page=1&per_page=100`),
    ]);

    let programs_indexed = 15;
    let last_updated = null as string | null;
    let model_version = "v1.0-seed";
    let median_roi = 187;

    if (countResp.ok) {
      const d = await countResp.json();
      programs_indexed = d.total ?? 15;
    }

    if (dpResp.ok) {
      const d = await dpResp.json();
      last_updated = d.last_data_update;
      model_version = d.champion?.version_tag ?? "v1.0-seed";
    }

    if (roiResp.ok) {
      const d = await roiResp.json();
      const rois = (d.data ?? []).map((r: { roi?: { compositeScore?: number } }) => r.roi?.compositeScore ?? 0).filter(Boolean);
      if (rois.length > 0) {
        rois.sort((a: number, b: number) => a - b);
        median_roi = rois[Math.floor(rois.length / 2)];
      }
    }

    return NextResponse.json({
      programs_indexed,
      data_points_collected: programs_indexed * 285,  // avg data points per program
      median_roi_pct: median_roi,
      last_updated,
      model_version,
      _source: "database",
    });

  } catch { /* fall through */ }

  // Mock stats
  const rois = MOCK_DATA.map((r) => r.roi.compositeScore).sort((a, b) => a - b);
  const medianRoi = rois[Math.floor(rois.length / 2)];

  return NextResponse.json({
    programs_indexed: MOCK_DATA.length,
    data_points_collected: MOCK_DATA.length * 285,
    median_roi_pct: medianRoi,
    last_updated: null,
    model_version: "v1.0-seed",
    _source: "mock",
  });
}
