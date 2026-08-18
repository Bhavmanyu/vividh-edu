"use client";

interface RiskItem {
  label: string;
  value: number; // 0–1
  description?: string;
}

interface RiskGridProps {
  items: RiskItem[];
  dots?: number; // total dots per indicator (default 5)
}

function getColor(value: number): string {
  if (value <= 0.2) return "#22C55E";
  if (value <= 0.4) return "#84CC16";
  if (value <= 0.6) return "#F59E0B";
  if (value <= 0.8) return "#F97316";
  return "#EF4444";
}

function getRiskLevel(value: number): string {
  if (value <= 0.2) return "Very Low";
  if (value <= 0.4) return "Low";
  if (value <= 0.6) return "Medium";
  if (value <= 0.8) return "High";
  return "Very High";
}

export function RiskGrid({ items, dots = 5 }: RiskGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {items.map((item) => {
        const filled = Math.round(item.value * dots);
        const color = getColor(item.value);
        return (
          <div
            key={item.label}
            className="glass-card p-4 group"
            title={item.description}
          >
            <div className="flex items-start justify-between mb-2">
              <span
                className="text-xs font-semibold uppercase tracking-wider"
                style={{ color: "#8B8BA7", letterSpacing: "0.06em" }}
              >
                {item.label}
              </span>
              <span
                className="text-xs font-bold"
                style={{ color }}
              >
                {getRiskLevel(item.value)}
              </span>
            </div>
            <div className="flex items-center gap-1.5 mt-2">
              {Array.from({ length: dots }).map((_, i) => (
                <span
                  key={i}
                  style={{
                    display: "inline-block",
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: i < filled ? color : "#1E1E2E",
                    transition: `background 0.2s ease ${i * 0.05}s`,
                    boxShadow: i < filled ? `0 0 4px ${color}60` : "none",
                  }}
                />
              ))}
              <span className="ml-2 text-xs font-mono" style={{ color: "#4A4A6A" }}>
                {Math.round(item.value * 100)}%
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
