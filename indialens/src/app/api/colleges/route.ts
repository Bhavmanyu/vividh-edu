import { NextResponse } from "next/server";
import { MOCK_DATA, formatInr } from "@/lib/mock-data";

const FASTAPI_BASE = process.env.FASTAPI_URL ?? "http://localhost:8000";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  const params = new URLSearchParams({
    page:     searchParams.get("page")     ?? "1",
    per_page: searchParams.get("per_page") ?? "50",
    ...(searchParams.get("field")    ? { field:    searchParams.get("field")!    } : {}),
    ...(searchParams.get("tier")     ? { tier:     searchParams.get("tier")!     } : {}),
    ...(searchParams.get("state")    ? { state:    searchParams.get("state")!    } : {}),
    ...(searchParams.get("search")   ? { search:   searchParams.get("search")!   } : {}),
    ...(searchParams.get("sort_by")  ? { sort_by:  searchParams.get("sort_by")!  } : {}),
    ...(searchParams.get("sort_dir") ? { sort_dir: searchParams.get("sort_dir")! } : {}),
  });

  // Try FastAPI
  try {
    const resp = await fetch(`${FASTAPI_BASE}/api/colleges?${params}`, {
      next: { revalidate: 300 }, // 5-min server cache
    } as RequestInit);
    if (resp.ok) {
      const data = await resp.json();
      if (data.data?.length > 0) return NextResponse.json({ ...data, _source: "database" });
    }
  } catch { /* fall through */ }

  // ── Mock fallback ──────────────────────────────────────────────
  let filtered = [...MOCK_DATA];
  const field  = searchParams.get("field");
  const tier   = searchParams.get("tier");
  const state  = searchParams.get("state");
  const search = searchParams.get("search")?.toLowerCase();
  const sortBy = searchParams.get("sort_by") ?? "compositeScore";
  const sortDir = searchParams.get("sort_dir") ?? "desc";

  if (field)  filtered = filtered.filter((r) => r.degree.field === field);
  if (tier)   filtered = filtered.filter((r) => String(r.college.tier) === tier);
  if (state)  filtered = filtered.filter((r) => r.college.state === state);
  if (search) filtered = filtered.filter((r) =>
    r.college.name.toLowerCase().includes(search) ||
    r.degree.name.toLowerCase().includes(search)
  );

  filtered.sort((a, b) => {
    const getVal = (r: typeof a) => {
      if (sortBy === "compositeScore")  return r.roi.compositeScore;
      if (sortBy === "financialRoiPct") return r.roi.financialRoiPct;
      if (sortBy === "riskScore")       return r.roi.riskScore;
      if (sortBy === "year1Salary")     return r.salary.year1.p50;
      return r.roi.compositeScore;
    };
    return sortDir === "asc" ? getVal(a) - getVal(b) : getVal(b) - getVal(a);
  });

  const page    = parseInt(searchParams.get("page") ?? "1");
  const perPage = parseInt(searchParams.get("per_page") ?? "50");
  const start   = (page - 1) * perPage;
  const paged   = filtered.slice(start, start + perPage);

  return NextResponse.json({
    data: paged,
    total: filtered.length,
    page,
    per_page: perPage,
    model_version: "v1.0-seed",
    generated_at: new Date().toISOString(),
    _source: "mock",
  });
}
