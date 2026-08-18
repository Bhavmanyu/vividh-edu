"use client";

export const dynamic = "force-dynamic";

import { useState, useMemo, useCallback } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  createColumnHelper,
  type SortingState,
} from "@tanstack/react-table";
import Link from "next/link";
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Download,
  Filter,
  Search,
  X,
  Info,
  RefreshCw,
} from "lucide-react";
import { ScoreRing } from "@/components/ScoreRing";
import { DataFreshnessBadge } from "@/components/DataFreshnessBadge";
import { formatInr, UNIQUE_FIELDS, UNIQUE_STATES, UNIQUE_TIERS } from "../../lib/mock-data";
import type { CollegeDegreeRecord } from "../../lib/mock-data";
import { useColleges } from "@/hooks/useData";


const FIELD_LABELS: Record<string, string> = {
  "engineering-cs": "Engineering — CS",
  "engineering-non-cs": "Engineering — Non-CS",
  medicine: "Medicine",
  management: "Management",
  commerce: "Commerce",
  design: "Design",
  law: "Law",
};

const AI_RISK_COLORS: Record<string, string> = {
  Low: "#22C55E",
  Medium: "#F59E0B",
  High: "#F97316",
  "Very High": "#EF4444",
};

const columnHelper = createColumnHelper<CollegeDegreeRecord>();

function downloadCSV(data: CollegeDegreeRecord[]) {
  const rows = [
    [
      "College",
      "Degree",
      "State",
      "Tier",
      "Composite Score",
      "Financial ROI %",
      "AI Risk",
      "Placement Rate",
      "Median Salary Y1 (INR)",
      "Median Salary Y10 (INR)",
      "Last Updated (days ago)",
    ],
    ...data.map((r) => [
      r.college.shortName,
      r.degree.shortName,
      r.college.state,
      r.college.tier,
      r.roi.compositeScore,
      r.roi.financialRoiPct,
      r.meta.aiRiskLabel,
      r.placement.rate,
      r.salary.year1.p50,
      r.salary.year10.p50,
      r.meta.dataFreshnessDays,
    ]),
  ];
  const csv = rows.map((r) => r.join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `indialens-roi-index-${new Date().toISOString().split("T")[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function ROIIndexPage() {
  const [sorting, setSorting] = useState<SortingState>([
    { id: "compositeScore", desc: true },
  ]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [fieldFilter, setFieldFilter] = useState("");
  const [stateFilter, setStateFilter] = useState("");
  const [tierFilter, setTierFilter] = useState("");
  const [aiRiskFilter, setAiRiskFilter] = useState("");
  const [showMethodology, setShowMethodology] = useState(false);

  // Live data — FastAPI first, mock fallback automatically
  const { response, isLoading, error, refetch } = useColleges({
    field:    fieldFilter  || undefined,
    state:    stateFilter  || undefined,
    tier:     tierFilter   || undefined,
    search:   globalFilter || undefined,
    per_page: 100,
  });

  const allData: CollegeDegreeRecord[] = response?.data ?? [];
  const isLive = response?._source === "database";

  const filteredData = useMemo(() => {
    return allData.filter((r) => {
      if (aiRiskFilter && r.meta.aiRiskLabel !== aiRiskFilter) return false;
      return true;
    });
  }, [allData, aiRiskFilter]);


  const columns = useMemo(
    () => [
      columnHelper.accessor("roi.compositeScore", {
        id: "compositeScore",
        header: "Score",
        cell: ({ getValue }) => (
          <ScoreRing score={getValue()} size={48} strokeWidth={4} showLabel={false} animate={false} />
        ),
        size: 64,
      }),
      columnHelper.display({
        id: "college",
        header: "College & Degree",
        cell: ({ row }) => {
          const r = row.original;
          return (
            <Link
              href={`/college/${r.id}`}
              style={{ textDecoration: "none" }}
            >
              <div>
                <p
                  style={{
                    fontWeight: 600,
                    fontSize: 13,
                    color: "#F0F0F5",
                    letterSpacing: "-0.01em",
                  }}
                >
                  {r.college.shortName}
                </p>
                <p style={{ fontSize: 12, color: "#8B8BA7", marginTop: 2 }}>
                  {r.degree.shortName}
                </p>
              </div>
            </Link>
          );
        },
      }),
      columnHelper.display({
        id: "location",
        header: "State",
        cell: ({ row }) => (
          <span style={{ fontSize: 12, color: "#8B8BA7" }}>
            {row.original.college.state}
          </span>
        ),
      }),
      columnHelper.display({
        id: "tier",
        header: "Tier",
        cell: ({ row }) => (
          <span
            className="badge badge-blue"
            style={{ fontSize: 10 }}
          >
            T{row.original.college.tier}
          </span>
        ),
      }),
      columnHelper.accessor("roi.financialRoiPct", {
        id: "financialRoi",
        header: "Financial ROI",
        cell: ({ getValue }) => (
          <span className="font-mono font-bold text-sm" style={{ color: "#4F6EF7" }}>
            {getValue().toLocaleString()}%
          </span>
        ),
      }),
      columnHelper.display({
        id: "aiRisk",
        header: "AI Risk",
        cell: ({ row }) => {
          const label = row.original.meta.aiRiskLabel;
          return (
            <span
              style={{
                color: AI_RISK_COLORS[label],
                fontSize: 12,
                fontWeight: 600,
              }}
            >
              {label}
            </span>
          );
        },
      }),
      columnHelper.accessor("placement.rate", {
        id: "placementRate",
        header: "Placement %",
        cell: ({ getValue }) => (
          <div className="flex items-center gap-2">
            <div
              style={{
                width: 36,
                height: 4,
                background: "#1E1E2E",
                borderRadius: 2,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${getValue()}%`,
                  height: "100%",
                  background: "#22C55E",
                  borderRadius: 2,
                }}
              />
            </div>
            <span className="font-mono text-xs" style={{ color: "#8B8BA7" }}>
              {getValue()}%
            </span>
          </div>
        ),
      }),
      columnHelper.display({
        id: "salaryY1",
        header: "Salary Y1",
        cell: ({ row }) => (
          <span className="font-mono text-sm" style={{ color: "#F0F0F5" }}>
            {formatInr(row.original.salary.year1.p50)}
          </span>
        ),
      }),
      columnHelper.display({
        id: "salaryY10",
        header: "Salary Y10",
        cell: ({ row }) => (
          <span className="font-mono text-sm" style={{ color: "#22C55E" }}>
            {formatInr(row.original.salary.year10.p50)}
          </span>
        ),
      }),
      columnHelper.display({
        id: "freshness",
        header: "Updated",
        cell: ({ row }) => (
          <DataFreshnessBadge days={row.original.meta.dataFreshnessDays} />
        ),
      }),
    ],
    []
  );

  const table = useReactTable({
    data: filteredData,
    columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  const hasFilters = fieldFilter || stateFilter || tierFilter || aiRiskFilter || globalFilter;

  return (
    <div style={{ padding: "40px 0 80px" }}>
      <div className="container-xl">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <p
                className="text-xs font-semibold uppercase tracking-wider"
                style={{ color: "#4F6EF7", letterSpacing: "0.1em" }}
              >
                Public Index
              </p>
              {/* Live / Mock badge */}
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  padding: "2px 8px",
                  borderRadius: 99,
                  background: isLive ? "rgba(34,197,94,0.12)" : "rgba(245,158,11,0.12)",
                  color: isLive ? "#22C55E" : "#F59E0B",
                  border: `1px solid ${isLive ? "rgba(34,197,94,0.3)" : "rgba(245,158,11,0.3)"}`,
                  letterSpacing: "0.08em",
                }}
              >
                {isLoading ? "LOADING…" : isLive ? "● LIVE DB" : "● SEED DATA"}
              </span>
            </div>
            <h1
              className="font-display font-bold"
              style={{ fontSize: 32, color: "#F0F0F5", letterSpacing: "-0.02em", marginBottom: 8 }}
            >
              Degree ROI Index
            </h1>
            <p style={{ fontSize: 14, color: "#8B8BA7" }}>
              {isLoading ? "Loading programs…" : `${filteredData.length} programs`}
              {" "}· Sorted by composite ROI score ·{" "}
              <button
                onClick={() => setShowMethodology((v) => !v)}
                style={{
                  color: "#4F6EF7",
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  fontSize: 14,
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                  padding: 0,

                }}
              >
                <Info size={12} />
                How is this scored?
              </button>
            </p>
          </div>
          <button
            onClick={() => downloadCSV(filteredData)}
            className="btn-secondary"
            style={{ fontSize: 13 }}
          >
            <Download size={14} />
            Export CSV
          </button>
        </div>

        {/* Methodology sidebar (collapsible) */}
        {showMethodology && (
          <div
            className="glass-card p-6 mb-6 animate-slide-up"
            style={{ borderLeft: "3px solid #4F6EF7", borderRadius: "0 8px 8px 0" }}
          >
            <div className="flex items-start justify-between">
              <div>
                <h3
                  className="font-display font-semibold mb-2"
                  style={{ fontSize: 16, color: "#F0F0F5" }}
                >
                  How composite scores are calculated
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-3">
                  {[
                    { label: "PPP-Adjusted Financial ROI", w: "35%" },
                    { label: "Risk-Adjusted Stability", w: "20%" },
                    { label: "Upside Optionality", w: "15%" },
                    { label: "Mobility Premium", w: "15%" },
                    { label: "Satisfaction & Wellbeing", w: "10%" },
                    { label: "Social Capital", w: "5%" },
                  ].map((c) => (
                    <div key={c.label} style={{ fontSize: 12 }}>
                      <span style={{ color: "#8B8BA7" }}>{c.label}</span>
                      <span
                        className="font-mono font-bold ml-2"
                        style={{ color: "#4F6EF7" }}
                      >
                        {c.w}
                      </span>
                    </div>
                  ))}
                </div>
                <Link
                  href="/methodology"
                  style={{ fontSize: 12, color: "#4F6EF7", textDecoration: "none", marginTop: 8, display: "inline-block" }}
                >
                  Full methodology →
                </Link>
              </div>
              <button
                onClick={() => setShowMethodology(false)}
                style={{ background: "none", border: "none", color: "#4A4A6A", cursor: "pointer" }}
              >
                <X size={16} />
              </button>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="glass-card p-4 mb-4">
          <div className="flex flex-wrap items-center gap-3">
            {/* Search */}
            <div
              style={{
                position: "relative",
                flex: "1",
                minWidth: 200,
              }}
            >
              <Search
                size={14}
                style={{
                  position: "absolute",
                  left: 12,
                  top: "50%",
                  transform: "translateY(-50%)",
                  color: "#4A4A6A",
                  pointerEvents: "none",
                }}
              />
              <input
                value={globalFilter}
                onChange={(e) => setGlobalFilter(e.target.value)}
                placeholder="Search colleges or degrees..."
                className="form-input"
                style={{ paddingLeft: 36 }}
              />
            </div>

            {/* Field filter */}
            <select
              value={fieldFilter}
              onChange={(e) => setFieldFilter(e.target.value)}
              className="form-input form-select"
              style={{ maxWidth: 180, background: "#0A0A0F" }}
            >
              <option value="">All Fields</option>
              {UNIQUE_FIELDS.map((f) => (
                <option key={f} value={f} style={{ background: "#13131A" }}>
                  {FIELD_LABELS[f] || f}
                </option>
              ))}
            </select>

            {/* State filter */}
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="form-input form-select"
              style={{ maxWidth: 160, background: "#0A0A0F" }}
            >
              <option value="">All States</option>
              {UNIQUE_STATES.map((s) => (
                <option key={s} value={s} style={{ background: "#13131A" }}>
                  {s}
                </option>
              ))}
            </select>

            {/* Tier filter */}
            <select
              value={tierFilter}
              onChange={(e) => setTierFilter(e.target.value)}
              className="form-input form-select"
              style={{ maxWidth: 120, background: "#0A0A0F" }}
            >
              <option value="">All Tiers</option>
              {UNIQUE_TIERS.map((t) => (
                <option key={t} value={t} style={{ background: "#13131A" }}>
                  Tier {t}
                </option>
              ))}
            </select>

            {/* AI Risk filter */}
            <select
              value={aiRiskFilter}
              onChange={(e) => setAiRiskFilter(e.target.value)}
              className="form-input form-select"
              style={{ maxWidth: 140, background: "#0A0A0F" }}
            >
              <option value="">All AI Risk</option>
              {["Low", "Medium", "High", "Very High"].map((l) => (
                <option key={l} value={l} style={{ background: "#13131A" }}>
                  {l}
                </option>
              ))}
            </select>

            {/* Clear */}
            {hasFilters && (
              <button
                onClick={() => {
                  setFieldFilter("");
                  setStateFilter("");
                  setTierFilter("");
                  setAiRiskFilter("");
                  setGlobalFilter("");
                }}
                className="btn-secondary"
                style={{ fontSize: 12, padding: "8px 12px" }}
              >
                <X size={12} />
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Table */}
        <div className="glass-card overflow-hidden">
          <div style={{ overflowX: "auto" }}>
            <table className="data-table" style={{ minWidth: 900 }}>
              <thead>
                {table.getHeaderGroups().map((hg) => (
                  <tr key={hg.id}>
                    {hg.headers.map((header) => (
                      <th
                        key={header.id}
                        onClick={header.column.getToggleSortingHandler()}
                        style={{ cursor: header.column.getCanSort() ? "pointer" : "default" }}
                      >
                        <div className="flex items-center gap-1">
                          {flexRender(header.column.columnDef.header, header.getContext())}
                          {header.column.getCanSort() && (
                            <span style={{ color: "#4A4A6A" }}>
                              {header.column.getIsSorted() === "asc" ? (
                                <ArrowUp size={10} />
                              ) : header.column.getIsSorted() === "desc" ? (
                                <ArrowDown size={10} />
                              ) : (
                                <ArrowUpDown size={10} />
                              )}
                            </span>
                          )}
                        </div>
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row) => (
                  <tr key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id}>
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Empty state */}
          {table.getRowModel().rows.length === 0 && (
            <div
              style={{
                textAlign: "center",
                padding: "48px 24px",
                color: "#4A4A6A",
              }}
            >
              <Filter size={24} style={{ margin: "0 auto 12px" }} />
              <p style={{ fontWeight: 600, marginBottom: 4 }}>No programs match your filters</p>
              <p style={{ fontSize: 13 }}>Try removing some filters</p>
            </div>
          )}
        </div>

        {/* Footer note */}
        <p
          className="text-xs font-mono mt-4"
          style={{ color: "#4A4A6A", textAlign: "center" }}
        >
          Showing {table.getRowModel().rows.length} of {allData.length} programs ·
          Composite scores calculated per IndiaLens v1 methodology ·{" "}
          <Link href="/methodology" style={{ color: "#4F6EF7", textDecoration: "none" }}>
            See formula
          </Link>
        </p>
      </div>
    </div>
  );
}
