"use client";

interface ROIComponent {
  label: string;
  value: number; // 0–100 (the score for this component)
  weight: number; // 0–1 (formula weight)
  color: string;
}

interface ROIBreakdownProps {
  financialRoi: number;
  riskScore: number;
  optionalityScore: number;
  mobilityScore: number;
  satisfactionScore: number;
  networkScore: number;
}

export function ROIBreakdown({
  financialRoi,
  riskScore,
  optionalityScore,
  mobilityScore,
  satisfactionScore,
  networkScore,
}: ROIBreakdownProps) {
  const components: ROIComponent[] = [
    {
      label: "Financial ROI",
      value: Math.min(100, Math.round(financialRoi / 50)),
      weight: 0.35,
      color: "#4F6EF7",
    },
    {
      label: "Risk-Adjusted",
      value: Math.round((1 - riskScore) * 100),
      weight: 0.2,
      color: "#22C55E",
    },
    {
      label: "Optionality",
      value: Math.round(optionalityScore * 100),
      weight: 0.15,
      color: "#F7C94F",
    },
    {
      label: "Mobility",
      value: Math.round(mobilityScore * 100),
      weight: 0.15,
      color: "#A78BFA",
    },
    {
      label: "Satisfaction",
      value: Math.round(satisfactionScore * 100),
      weight: 0.1,
      color: "#F97316",
    },
    {
      label: "Network",
      value: Math.round(networkScore * 100),
      weight: 0.05,
      color: "#EC4899",
    },
  ];

  const totalWeighted = components.reduce(
    (sum, c) => sum + c.value * c.weight,
    0
  );

  return (
    <div className="space-y-3">
      {components.map((comp) => {
        const contribution = Math.round(comp.value * comp.weight);
        return (
          <div key={comp.label}>
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <span
                  style={{
                    display: "inline-block",
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: comp.color,
                  }}
                />
                <span
                  className="text-xs font-semibold"
                  style={{ color: "#8B8BA7" }}
                >
                  {comp.label}
                </span>
                <span
                  className="text-xs font-mono"
                  style={{ color: "#4A4A6A" }}
                >
                  ×{comp.weight}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span
                  className="text-xs font-mono"
                  style={{ color: "#8B8BA7" }}
                >
                  {comp.value}/100
                </span>
                <span
                  className="text-xs font-mono font-bold"
                  style={{ color: comp.color, minWidth: 32, textAlign: "right" }}
                >
                  +{contribution}
                </span>
              </div>
            </div>
            <div
              style={{
                height: 6,
                background: "#1E1E2E",
                borderRadius: 3,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${comp.value}%`,
                  background: comp.color,
                  borderRadius: 3,
                  transition: "width 1s cubic-bezier(0.4, 0, 0.2, 1)",
                  boxShadow: `0 0 8px ${comp.color}40`,
                }}
              />
            </div>
          </div>
        );
      })}
      <div
        style={{
          borderTop: "1px solid #1E1E2E",
          paddingTop: 12,
          marginTop: 8,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span
          className="text-xs font-semibold uppercase tracking-wider"
          style={{ color: "#4A4A6A" }}
        >
          Composite Score
        </span>
        <span
          className="font-mono font-bold text-lg"
          style={{ color: "#F0F0F5" }}
        >
          {Math.round(totalWeighted)}/100
        </span>
      </div>
    </div>
  );
}
