import { NextResponse } from "next/server";

const FASTAPI_BASE = process.env.FASTAPI_URL ?? "http://localhost:8000";

/** Proxy all /api/admin/* to FastAPI admin router */
export async function GET(
  request: Request,
  { params }: { params: { path: string[] } }
) {
  const subpath = (params.path ?? []).join("/");
  const apiKey  = request.headers.get("x-api-key") ?? "";

  try {
    const resp = await fetch(`${FASTAPI_BASE}/api/admin/${subpath}`, {
      headers: { "X-API-KEY": apiKey },
    });
    const data = await resp.json();
    return NextResponse.json(data, { status: resp.status });
  } catch {
    return NextResponse.json({ error: "Admin service unavailable" }, { status: 503 });
  }
}

export async function POST(
  request: Request,
  { params }: { params: { path: string[] } }
) {
  const subpath = (params.path ?? []).join("/");
  const apiKey  = request.headers.get("x-api-key") ?? "";

  try {
    const body = await request.text();
    const resp = await fetch(`${FASTAPI_BASE}/api/admin/${subpath}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-KEY": apiKey },
      body: body || undefined,
    });
    const data = await resp.json();
    return NextResponse.json(data, { status: resp.status });
  } catch {
    return NextResponse.json({ error: "Admin service unavailable" }, { status: 503 });
  }
}
