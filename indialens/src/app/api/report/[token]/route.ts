import { NextRequest, NextResponse } from 'next/server';

const API_BASE = process.env.API_BASE_URL || 'http://localhost:8000';

export async function GET(request: NextRequest, { params }: { params: { token: string } }) {
  const { token } = params;
  try {
    const res = await fetch(`${API_BASE}/api/v1/analyze/report/${token}`);
    if (!res.ok) {
      if (res.status === 404) {
        return NextResponse.json({ _source: 'not_found' }, { status: 404 });
      }
      return NextResponse.json({ error: 'Failed to fetch report' }, { status: res.status });
    }
    const data = await res.json();
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
