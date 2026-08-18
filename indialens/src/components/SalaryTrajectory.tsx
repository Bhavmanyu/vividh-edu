"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from "recharts";

interface TrajectoryData {
  year: number;
  conservative: number;
  base: number;
  optimistic: number;
}

interface SalaryTrajectoryProps {
  data?: TrajectoryData[];
  salaryByYear?: {
    year1: { p25: number; p50: number; p75: number };
    year5: { p25: number; p50: number; p75: number };
    year10: { p25: number; p50: number; p75: number };
    year20: { p25: number; p50: number; p75: number };
  };
}

function formatSalary(value: number): string {
  if (value >= 10000000) return `₹${(value / 10000000).toFixed(1)}Cr`;
  if (value >= 100000) return `₹${(value / 100000).toFixed(1)}L`;
  return `₹${(value / 1000).toFixed(0)}K`;
}

const CustomTooltip = ({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: number;
}) => {
  if (!active || !payload?.length) return null;
  return (
    <div
      style={{
        background: "#13131A",
        border: "1px solid #1E1E2E",
        borderRadius: 8,
        padding: "12px 16px",
        boxShadow: "0 8px 24px rgba(0,0,0,0.4)",
      }}
    >
      <p
        style={{
          color: "#8B8BA7",
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          marginBottom: 8,
        }}
      >
        Year {label}
      </p>
      {payload.map((entry) => (
        <div
          key={entry.name}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            marginBottom: 4,
          }}
        >
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: entry.color,
              display: "inline-block",
            }}
          />
          <span style={{ color: "#8B8BA7", fontSize: 12, minWidth: 90 }}>
            {entry.name}
          </span>
          <span
            style={{
              color: "#F0F0F5",
              fontSize: 13,
              fontWeight: 600,
              fontFamily: "JetBrains Mono, monospace",
            }}
          >
            {formatSalary(entry.value)}
          </span>
        </div>
      ))}
    </div>
  );
};

export function SalaryTrajectory({ data, salaryByYear }: SalaryTrajectoryProps) {
  // Build chart data from salaryByYear if data not provided directly
  const chartData: TrajectoryData[] =
    data ||
    (salaryByYear
      ? [
          { year: 0, conservative: 0, base: 0, optimistic: 0 },
          {
            year: 1,
            conservative: salaryByYear.year1.p25,
            base: salaryByYear.year1.p50,
            optimistic: salaryByYear.year1.p75,
          },
          {
            year: 5,
            conservative: salaryByYear.year5.p25,
            base: salaryByYear.year5.p50,
            optimistic: salaryByYear.year5.p75,
          },
          {
            year: 10,
            conservative: salaryByYear.year10.p25,
            base: salaryByYear.year10.p50,
            optimistic: salaryByYear.year10.p75,
          },
          {
            year: 20,
            conservative: salaryByYear.year20.p25,
            base: salaryByYear.year20.p50,
            optimistic: salaryByYear.year20.p75,
          },
        ]
      : []);

  return (
    <div style={{ width: "100%", height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 8, right: 16, left: 8, bottom: 8 }}
        >
          <defs>
            <linearGradient id="optimisticGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#22C55E" />
              <stop offset="100%" stopColor="#84CC16" />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="2 6"
            stroke="#1E1E2E"
            vertical={false}
          />
          <XAxis
            dataKey="year"
            tick={{ fill: "#4A4A6A", fontSize: 11, fontFamily: "JetBrains Mono" }}
            tickLine={false}
            axisLine={false}
            label={{
              value: "Year",
              position: "insideBottomRight",
              fill: "#4A4A6A",
              fontSize: 11,
              offset: -4,
            }}
          />
          <YAxis
            tickFormatter={formatSalary}
            tick={{ fill: "#4A4A6A", fontSize: 11, fontFamily: "JetBrains Mono" }}
            tickLine={false}
            axisLine={false}
            width={64}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{
              paddingTop: 12,
              fontSize: 12,
              color: "#8B8BA7",
            }}
          />
          {/* Area between conservative and optimistic */}
          <Line
            type="monotone"
            dataKey="optimistic"
            name="Optimistic"
            stroke="#22C55E"
            strokeWidth={2}
            dot={{ fill: "#22C55E", strokeWidth: 0, r: 3 }}
            activeDot={{ r: 5, strokeWidth: 0 }}
            strokeDasharray="6 3"
          />
          <Line
            type="monotone"
            dataKey="base"
            name="Base Case"
            stroke="#4F6EF7"
            strokeWidth={2.5}
            dot={{ fill: "#4F6EF7", strokeWidth: 0, r: 3 }}
            activeDot={{ r: 5, strokeWidth: 0 }}
          />
          <Line
            type="monotone"
            dataKey="conservative"
            name="Conservative"
            stroke="#F59E0B"
            strokeWidth={2}
            dot={{ fill: "#F59E0B", strokeWidth: 0, r: 3 }}
            activeDot={{ r: 5, strokeWidth: 0 }}
            strokeDasharray="4 4"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
