import { NextResponse } from "next/server";
import { PLATFORM_STATS } from "@/lib/mock-data";

export async function GET() {
  return NextResponse.json({
    status: "success",
    lastRun: {
      startedAt: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
      completedAt: new Date(Date.now() - 2.7 * 60 * 60 * 1000).toISOString(),
      recordsScraped: 12847,
      recordsUpdated: 342,
      recordsFlagged: 7,
      sources: ["NIRF", "AmbitionBox", "Naukri", "PLFS", "WorldBank"],
    },
    nextRunAt: new Date(
      Date.now() + (7 - ((Date.now() / (1000 * 60 * 60 * 24)) % 7)) * 24 * 60 * 60 * 1000
    ).toISOString(),
    stats: PLATFORM_STATS,
  });
}
