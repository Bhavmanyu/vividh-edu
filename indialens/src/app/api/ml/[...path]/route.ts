import { NextResponse } from "next/server";

const FASTAPI_BASE = process.env.FASTAPI_URL ?? "http://localhost:8000";

/** Proxy all /api/ml/* requests to FastAPI */
export async function GET(
  _request: Request,
  { params }: { params: { path: string[] } }
) {
  const subpath = (params.path ?? []).join("/");
  const targetUrl = `${FASTAPI_BASE}/api/ml/${subpath}`;

  try {
    const resp = await fetch(targetUrl);
    const data = await resp.json();
    return NextResponse.json(data, { status: resp.status });
  } catch {
    return NextResponse.json({ error: "ML service unavailable" }, { status: 503 });
  }
}

export async function POST(
  request: Request,
  { params }: { params: { path: string[] } }
) {
  const subpath = (params.path ?? []).join("/");
  const targetUrl = `${FASTAPI_BASE}/api/ml/${subpath}`;

  const apiKey = request.headers.get("x-api-key") ?? "";

  try {
    const body = await request.text();
    const resp = await fetch(targetUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": apiKey,
      },
      body: body || undefined,
    });
    const data = await resp.json();
    return NextResponse.json(data, { status: resp.status });
  } catch {
    return NextResponse.json({ error: "ML service unavailable" }, { status: 503 });
  }
}
