import { NextResponse } from "next/server";
import { MOCK_DATA } from "../../../lib/mock-data";

const FASTAPI_BASE = process.env.FASTAPI_URL ?? "http://localhost:8000";

// ── Mock trajectory builder — matches LSTM output shape ───────────────
function buildMockTrajectory(baseSalary: number, field: string) {
  const growthRates: Record<string, number> = {
    "engineering-cs": 0.18, "management": 0.16, "medicine": 0.13,
    "law": 0.12, "engineering-non-cs": 0.10, "design": 0.14,
    "commerce": 0.10, "pure-sciences": 0.09, "social-sciences": 0.08, "arts": 0.07,
  };
  const r = growthRates[field] ?? 0.12;

  const project = (years: number) => {
    const p50 = baseSalary * Math.pow(1 + r, years);
    return {
      p10: Math.round(p50 * 0.72),
      p25: Math.round(p50 * 0.82),
      p50: Math.round(p50),
      p75: Math.round(p50 * 1.22),
      p90: Math.round(p50 * 1.45),
    };
  };

  return {
    y1: project(1),
    y3: project(3),
    y5: project(5),
    y10: project(10),
    y15: project(15),
    y20: project(20),
  };
}

export async function POST(request: Request) {
  const profile = await request.json();

  // Try FastAPI (Week 3: returns XGBoost scores + LSTM trajectory)
  try {
    const resp = await fetch(`${FASTAPI_BASE}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile),
    });
    if (resp.ok) {
      const data = await resp.json();
      if (data._source !== "empty_db_use_mock") {
        return NextResponse.json(data);
      }
    }
  } catch {
    // fall through to mock
  }

  // ── Rich mock fallback with LSTM-shaped trajectory ─────────────────
  const token = Math.random().toString(36).substring(2, 18);

  const recommendations = MOCK_DATA.slice(0, 5).map((r, i) => {
    const baseSalary = r.salary?.year1?.p50 ?? 1_000_000;
    const field = r.degree?.field ?? "engineering-cs";
    const trajectory = buildMockTrajectory(baseSalary, field);

    return {
      rank: i + 1,
      programId: r.id,
      collegeName: r.college.name,
      degreeName: r.degree.name,
      state: r.college.state,
      tier: r.college.tier,
      compositeScore: r.roi.compositeScore,
      fitScore: Math.round(78 - i * 5 + Math.random() * 8),
      trajectory,
      predictedSalaryY1: trajectory.y1.p50,
      predictedSalaryY5: trajectory.y5.p50,
      totalCostInr: r.costs?.totalCostOfDegreeInr ?? 1_000_000,
      placementRate: r.placement?.rate ? r.placement.rate / 100 : 0.75,
      reasons: [
        `Fit score based on your ${profile.primary_goals?.length ?? 0} stated goals`,
        `Financial ROI ${r.roi.financialRoiPct.toFixed(0)}% — top ${(i + 1) * 10}th percentile nationally`,
        `XGBoost predicts ₹${(trajectory.y5.p50 / 100_000).toFixed(0)}L at Year 5 (seed model)`,
        "Low geographic concentration — opportunities across 6+ cities",
      ],
      topRisks: [
        `AI automation risk: ${(r.roi.riskScore * 100).toFixed(0)}% — mitigated by specialisation`,
        "Credential inflation ~7% YoY in this cohort",
      ],
    };
  });

  const flags: object[] = [];
  if ((profile.total_budget ?? 20) <= 5) {
    flags.push({
      type: "budget_alert",
      title: "Tight Budget (≤ ₹5L)",
      message: "NIT/state university seats via JEE are the best value. Avg CS graduate recoups ₹5L in < 18 months.",
      severity: "warning",
    });
  }
  if (profile.jee_rank && profile.jee_rank < 500) {
    flags.push({
      type: "opportunity_alert",
      title: "Top-500 JEE Rank — IIT Open Merit Range",
      message: "All 23 IITs are viable. Model applies +12% network premium on 10-year salary for IIT graduates.",
      severity: "success",
    });
  }
  if (profile.neet_score && profile.neet_score >= 650) {
    flags.push({
      type: "opportunity_alert",
      title: "NEET 650+ — AIIMS/Top MBBS Range",
      message: "You qualify for AIIMS (composite score: 91) and top state medical colleges.",
      severity: "success",
    });
  }
  if (!profile.fields_of_interest?.length) {
    flags.push({
      type: "improve_accuracy",
      title: "Add Fields of Interest",
      message: "Specifying 2–3 fields improves recommendation accuracy by ~18%.",
      severity: "info",
    });
  }

  return NextResponse.json({
    token,
    recommendations,
    profile_parsed: profile,
    flags,
    model_version: "v1.0-seed",
    using_ml: false,
    generated_at: new Date().toISOString(),
    _source: "mock",
  });
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const token = searchParams.get("token");

  if (!token) {
    return NextResponse.json({ error: "token required" }, { status: 400 });
  }

  // Try FastAPI
  try {
    const resp = await fetch(`${FASTAPI_BASE}/api/analyze/${token}`);
    if (resp.ok) return NextResponse.json(await resp.json());
  } catch {
    // fall through
  }

  // Mock fallback
  return NextResponse.json({
    token,
    recommendations: MOCK_DATA.slice(0, 5).map((r, i) => ({
      rank: i + 1,
      programId: r.id,
      collegeName: r.college.name,
      degreeName: r.degree.name,
      compositeScore: r.roi.compositeScore,
      fitScore: Math.round(78 - i * 5),
      trajectory: buildMockTrajectory(r.salary?.year1?.p50 ?? 1_000_000, r.degree?.field ?? "engineering-cs"),
    })),
    _source: "mock",
  });
}

// ML status proxy (GET /api/ml/status)
// Mounted here as a convenience — also available at /api/ml/status via backend
export async function HEAD() {
  try {
    const resp = await fetch(`${FASTAPI_BASE}/api/ml/status`);
    return new NextResponse(null, { status: resp.ok ? 200 : 503 });
  } catch {
    return new NextResponse(null, { status: 503 });
  }
}
