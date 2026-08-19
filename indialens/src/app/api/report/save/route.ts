import { NextRequest, NextResponse } from 'next/server';
import { reportStore, SavedReport } from '../../../../lib/report-store';

const API_BASE = process.env.API_BASE_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const token = body.token || Math.random().toString(36).substring(2, 18);
    const createdAt = new Date().toISOString();
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();

    const savedRecord: SavedReport = {
      token,
      created_at: createdAt,
      expires_at: expiresAt,
      student_input: body.profile_parsed || body.student_input || {},
      results: body,
      _source: 'mock',
    };

    reportStore.set(token, savedRecord);

    // Also attempt backend save if API available
    try {
      await fetch(`${API_BASE}/api/v1/analyze/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(2000),
      });
    } catch {
      // Backend unavailable, fallback to local store
    }

    return NextResponse.json({ status: 'ok', token, expires_at: expiresAt });
  } catch (err) {
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}

