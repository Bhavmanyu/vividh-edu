import { NextResponse } from "next/server";
import { MOCK_DATA } from "@/lib/mock-data";

const FASTAPI_BASE = process.env.FASTAPI_URL ?? "http://localhost:8000";

export async function GET(_req: Request, { params }: { params: { id: string } }) {
  const { id } = params;

  // Try FastAPI
  try {
    const resp = await fetch(`${FASTAPI_BASE}/api/colleges/${id}`, {
      next: { revalidate: 600 },
    } as RequestInit);
    if (resp.ok) {
      const data = await resp.json();
      return NextResponse.json({ ...data, _source: "database" });
    }
  } catch { /* fall through */ }

  // Mock fallback
  const record = MOCK_DATA.find((r) => r.id === id) ?? MOCK_DATA[0];
  return NextResponse.json({ ...record, _source: "mock" });
}
