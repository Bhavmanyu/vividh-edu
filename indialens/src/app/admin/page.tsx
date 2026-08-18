"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Shield, BarChart2, AlertTriangle, MessageSquare,
  RefreshCw, History, Database, CheckCircle, Lock, XCircle, Brain,
} from "lucide-react";
import { AnomalyFlag } from "@/components/AnomalyFlag";
import { FeedbackForm } from "@/components/FeedbackForm";
import { useAdminQueue } from "@/hooks/useData";
import { useModelStatus } from "@/hooks/useModelStatus";


// Auth gate — captures API key
function LoginGate({ onLogin }: { onLogin: (key: string) => void }) {
  const [key, setKey] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!key.trim()) { setError("API key required"); return; }
    // Quick validation against admin endpoint
    const resp = await fetch("/api/admin/health", {
      headers: { "X-API-KEY": key },
    }).catch(() => null);
    if (resp && resp.status === 401) {
      setError("Invalid API key"); return;
    }
    onLogin(key.trim());
  };

  return (
    <div
      style={{
        minHeight: "80vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 24,
      }}
    >
      <div className="glass-card p-8" style={{ width: "100%", maxWidth: 400 }}>
        <div className="flex items-center gap-3 mb-6">
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 8,
              background: "rgba(79,110,247,0.12)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#4F6EF7",
            }}
          >
            <Lock size={18} />
          </div>
          <div>
            <h1 className="font-display font-bold" style={{ fontSize: 20, color: "#F0F0F5" }}>
              Admin Panel
            </h1>
            <p style={{ fontSize: 12, color: "#4A4A6A" }}>Educator & Researcher Access</p>
          </div>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="form-label">Admin API Key</label>
            <input
              type="password"
              className="form-input"
              placeholder="Enter X-API-KEY…"
              value={key}
              onChange={(e) => { setKey(e.target.value); setError(""); }}
              autoFocus
            />
            {error && <p style={{ fontSize: 12, color: "#EF4444", marginTop: 4 }}>{error}</p>}
            <p style={{ fontSize: 11, color: "#4A4A6A", marginTop: 6 }}>
              Set via <code style={{ color: "#8B8BA7" }}>API_KEY_ADMIN</code> in backend .env
            </p>
          </div>
          <button type="submit" className="btn-primary w-full justify-center">
            <Shield size={14} />
            Access Admin Panel
          </button>
        </form>

        <p style={{ fontSize: 11, color: "#4A4A6A", textAlign: "center", marginTop: 16 }}>
          Access restricted to verified educators, researchers, and platform administrators.
        </p>
      </div>
    </div>
  );
}

const SAMPLE_ANOMALIES = [
  {
    id: "a1",
    collegeName: "VIT Vellore — B.Tech CSE",
    field: "placement_rate_pct",
    priorValue: "75%",
    newValue: "89%",
    deltaPct: 18.7,
    status: "pending" as const,
  },
  {
    id: "a2",
    collegeName: "IIT Bombay — B.Tech Mechanical",
    field: "median_salary_inr",
    priorValue: "₹11.0L",
    newValue: "₹15.4L",
    deltaPct: 40.0,
    status: "pending" as const,
  },
  {
    id: "a3",
    collegeName: "SRM Chennai — B.Tech CSE",
    field: "placement_rate_pct",
    priorValue: "68%",
    newValue: "51%",
    deltaPct: -25.0,
    status: "accepted" as const,
  },
];

const MODEL_VERSIONS = [
  {
    version: "v1.0-seed",
    trainedAt: "2026-08-05",
    trigger: "Initial seed — 15 college-degree combinations",
    isLive: true,
    metrics: { mse: 2.4, r2: 0.87 },
  },
  {
    version: "v0.9-beta",
    trainedAt: "2026-07-01",
    trigger: "Beta test with 8 colleges",
    isLive: false,
    metrics: { mse: 3.1, r2: 0.81 },
  },
];

type AdminTab = "dashboard" | "anomalies" | "feedback" | "scrapes" | "models";

export default function AdminPage() {
  const [authed, setAuthed]       = useState(false);
  const [apiKey, setApiKey]       = useState("");
  const [activeTab, setActiveTab] = useState<AdminTab>("dashboard");

  const {
    anomalies, scrapeRuns, isLoading: queueLoading, error: queueError,
    reviewAnomaly, triggerScrape, triggerRetrain, refresh,
  } = useAdminQueue(apiKey);

  const { status: modelStatus } = useModelStatus();

  if (!authed) {
    return <LoginGate onLogin={(key) => { setApiKey(key); setAuthed(true); }} />;
  }


  const TABS: { id: AdminTab; label: string; icon: React.ReactNode; badge?: number }[] = [
    { id: "dashboard", label: "Dashboard", icon: <BarChart2 size={14} /> },
    {
      id: "anomalies",
      label: "Anomaly Queue",
      icon: <AlertTriangle size={14} />,
      badge: anomalies.filter((a) => a.status === "pending").length,
    },
    { id: "feedback", label: "Educator Feedback", icon: <MessageSquare size={14} /> },
    { id: "scrapes", label: "Scrape History", icon: <Database size={14} /> },
    { id: "models", label: "Model Versions", icon: <History size={14} /> },
  ];

  return (
    <div style={{ padding: "40px 0 80px" }}>
      <div className="container-xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Shield size={16} style={{ color: "#4F6EF7" }} />
              <h1
                className="font-display font-bold"
                style={{ fontSize: 24, color: "#F0F0F5" }}
              >
                Admin Panel
              </h1>
            </div>
            <p style={{ fontSize: 13, color: "#8B8BA7" }}>
              Model v1.0-seed · Last scrape: 3 hours ago · 7 anomalies pending
            </p>
          </div>
          <button
            className="btn-primary"
            style={{ background: "#22C55E", fontSize: 13 }}
          >
            <RefreshCw size={13} />
            Force Retrain
          </button>
        </div>

        {/* Tabs */}
        <div
          className="flex gap-1 mb-8 overflow-x-auto"
          style={{ borderBottom: "1px solid #1E1E2E", paddingBottom: 0 }}
        >
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                padding: "10px 16px",
                background: "none",
                border: "none",
                borderBottom: `2px solid ${activeTab === tab.id ? "#4F6EF7" : "transparent"}`,
                color: activeTab === tab.id ? "#4F6EF7" : "#8B8BA7",
                fontSize: 13,
                fontWeight: activeTab === tab.id ? 600 : 500,
                cursor: "pointer",
                whiteSpace: "nowrap",
                marginBottom: -1,
                transition: "all 0.15s",
              }}
            >
              {tab.icon}
              {tab.label}
              {tab.badge ? (
                <span
                  style={{
                    background: "#EF4444",
                    color: "white",
                    borderRadius: 999,
                    fontSize: 10,
                    fontWeight: 700,
                    padding: "1px 6px",
                  }}
                >
                  {tab.badge}
                </span>
              ) : null}
            </button>
          ))}
        </div>

        {/* Dashboard */}
        {activeTab === "dashboard" && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "Model Version", value: "v1.0-seed", color: "#4F6EF7" },
                { label: "Pending Anomalies", value: "7", color: "#F59E0B" },
                { label: "Feedback Items", value: "12", color: "#22C55E" },
                { label: "Last Scrape", value: "3h ago", color: "#8B8BA7" },
              ].map((stat) => (
                <div key={stat.label} className="glass-card p-5">
                  <p style={{ fontSize: 11, color: "#4A4A6A", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                    {stat.label}
                  </p>
                  <p className="font-mono font-bold" style={{ fontSize: 20, color: stat.color }}>
                    {stat.value}
                  </p>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="glass-card p-6">
                <h3 className="font-display font-semibold mb-4" style={{ fontSize: 16, color: "#F0F0F5" }}>
                  Recent Scrape Runs
                </h3>
                {[
                  { source: "NIRF PDF", status: "success", records: 847, time: "3h ago" },
                  { source: "AmbitionBox", status: "success", records: 12041, time: "3h ago" },
                  { source: "Naukri.com", status: "partial", records: 8234, time: "3h ago" },
                  { source: "Reddit (PRAW)", status: "success", records: 2891, time: "4h ago" },
                ].map((run) => (
                  <div
                    key={run.source}
                    className="flex items-center justify-between py-2"
                    style={{ borderBottom: "1px solid #1E1E2E" }}
                  >
                    <div className="flex items-center gap-2">
                      <span
                        style={{
                          width: 6,
                          height: 6,
                          borderRadius: "50%",
                          background: run.status === "success" ? "#22C55E" : "#F59E0B",
                          display: "inline-block",
                        }}
                      />
                      <span style={{ fontSize: 13, color: "#F0F0F5" }}>{run.source}</span>
                    </div>
                    <div className="text-right">
                      <span className="font-mono text-xs" style={{ color: "#8B8BA7" }}>
                        {run.records.toLocaleString()} records
                      </span>
                      <span style={{ fontSize: 11, color: "#4A4A6A", marginLeft: 8 }}>
                        {run.time}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="glass-card p-6">
                <h3 className="font-display font-semibold mb-4" style={{ fontSize: 16, color: "#F0F0F5" }}>
                  Model Performance
                </h3>
                <div className="space-y-3">
                  {[
                    { metric: "ROI Predictor MSE", value: "2.4", trend: "↓ improved" },
                    { metric: "Placement Rate RMSE", value: "4.1%", trend: "stable" },
                    { metric: "Salary Pred. MAPE", value: "8.2%", trend: "↑ worsened" },
                    { metric: "College Matcher Recall@5", value: "0.87", trend: "↓ improved" },
                  ].map((m) => (
                    <div key={m.metric} className="flex items-center justify-between">
                      <span style={{ fontSize: 13, color: "#8B8BA7" }}>{m.metric}</span>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold" style={{ fontSize: 14, color: "#F0F0F5" }}>
                          {m.value}
                        </span>
                        <span
                          style={{
                            fontSize: 10,
                            color: m.trend.includes("improved") ? "#22C55E" : m.trend.includes("worsened") ? "#EF4444" : "#8B8BA7",
                          }}
                        >
                          {m.trend}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Anomaly Queue */}
        {activeTab === "anomalies" && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display font-semibold" style={{ fontSize: 20, color: "#F0F0F5" }}>
                Anomaly Review Queue
              </h2>
              <p style={{ fontSize: 13, color: "#8B8BA7" }}>
                {anomalies.filter((a) => a.status === "pending").length} pending review
              </p>
            </div>
            <p style={{ fontSize: 13, color: "#8B8BA7", marginBottom: 16 }}>
              Data points flagged by the pipeline with &gt;40% delta from prior week scrape.
              Human review required before these values update the model.
            </p>
            <div className="space-y-3">
              {anomalies.map((anomaly) => (
                <div key={anomaly.id}>
                  <p style={{ fontSize: 12, color: "#4A4A6A", marginBottom: 6 }}>
                    {anomaly.college_name || "Program"} ({anomaly.degree_name || "Degree"})
                  </p>
                  <AnomalyFlag
                    field={anomaly.field_name || "Scraped Metric"}
                    priorValue={anomaly.prior_value ?? "N/A"}
                    newValue={anomaly.new_value}
                    deltaPct={anomaly.delta_pct}
                    status={anomaly.status}
                    onAccept={() => reviewAnomaly(anomaly.id, "accept")}
                    onReject={() => reviewAnomaly(anomaly.id, "reject")}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Educator Feedback */}
        {activeTab === "feedback" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <h2 className="font-display font-semibold mb-2" style={{ fontSize: 20, color: "#F0F0F5" }}>
                Submit a Data Correction
              </h2>
              <p style={{ fontSize: 13, color: "#8B8BA7", marginBottom: 20 }}>
                Corrections are reviewed, source-verified, and used as training signal corrections
                at the next retraining cycle. Claude adjudicates conflicts between model outputs and
                educator corrections based on evidence quality.
              </p>
              <FeedbackForm />
            </div>
            <div>
              <h3 className="font-display font-semibold mb-4" style={{ fontSize: 18, color: "#F0F0F5" }}>
                Recent Corrections
              </h3>
              {[
                {
                  id: "f1",
                  college: "AIIMS Delhi — MBBS",
                  field: "median_salary_inr",
                  status: "accepted",
                  submitter: "Dr. R. Mehta (AIIMS)",
                  submittedAt: "2 days ago",
                },
                {
                  id: "f2",
                  college: "NID Ahmedabad — B.Des",
                  field: "placement_rate_pct",
                  status: "pending",
                  submitter: "Prof. A. Sharma (NID)",
                  submittedAt: "5 days ago",
                },
              ].map((item) => (
                <div key={item.id} className="glass-card p-4 mb-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <p style={{ fontSize: 13, fontWeight: 600, color: "#F0F0F5" }}>
                        {item.college}
                      </p>
                      <p style={{ fontSize: 12, color: "#8B8BA7" }}>
                        Field: <span className="font-mono">{item.field}</span>
                      </p>
                      <p style={{ fontSize: 11, color: "#4A4A6A", marginTop: 4 }}>
                        By {item.submitter} · {item.submittedAt}
                      </p>
                    </div>
                    <span
                      className={`badge ${item.status === "accepted" ? "badge-green" : "badge-yellow"}`}
                    >
                      {item.status === "accepted" ? <CheckCircle size={9} /> : null}
                      {item.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Scrape History */}
        {activeTab === "scrapes" && (
          <div>
            <h2 className="font-display font-semibold mb-4" style={{ fontSize: 20, color: "#F0F0F5" }}>
              Scrape Run History
            </h2>
            <div className="glass-card overflow-hidden">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Source</th>
                    <th>Started</th>
                    <th>Duration</th>
                    <th>Records</th>
                    <th>Updated</th>
                    <th>Flagged</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { source: "NIRF PDF", started: "2026-08-05 02:00", dur: "18m", scraped: 847, updated: 23, flagged: 2, status: "success" },
                    { source: "AmbitionBox", started: "2026-08-05 02:18", dur: "41m", scraped: 12041, updated: 312, flagged: 5, status: "success" },
                    { source: "Naukri.com", started: "2026-08-05 02:59", dur: "22m", scraped: 8234, updated: 891, flagged: 0, status: "partial" },
                    { source: "World Bank ICP", started: "2026-08-05 03:21", dur: "2m", scraped: 180, updated: 4, flagged: 0, status: "success" },
                    { source: "Reddit PRAW", started: "2026-08-05 03:23", dur: "15m", scraped: 2891, updated: 2891, flagged: 0, status: "success" },
                  ].map((run, i) => (
                    <tr key={i}>
                      <td>
                        <span style={{ fontWeight: 600, fontSize: 13, color: "#F0F0F5" }}>{run.source}</span>
                      </td>
                      <td>
                        <span className="font-mono text-xs" style={{ color: "#8B8BA7" }}>{run.started}</span>
                      </td>
                      <td>
                        <span className="font-mono text-xs" style={{ color: "#8B8BA7" }}>{run.dur}</span>
                      </td>
                      <td>
                        <span className="font-mono text-sm" style={{ color: "#F0F0F5" }}>{run.scraped.toLocaleString()}</span>
                      </td>
                      <td>
                        <span className="font-mono text-sm" style={{ color: "#22C55E" }}>{run.updated}</span>
                      </td>
                      <td>
                        <span className="font-mono text-sm" style={{ color: run.flagged > 0 ? "#F59E0B" : "#4A4A6A" }}>
                          {run.flagged}
                        </span>
                      </td>
                      <td>
                        <span
                          className={`badge ${run.status === "success" ? "badge-green" : "badge-yellow"}`}
                          style={{ fontSize: 10 }}
                        >
                          {run.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Model Versions */}
        {activeTab === "models" && (
          <div>
            <h2 className="font-display font-semibold mb-4" style={{ fontSize: 20, color: "#F0F0F5" }}>
              Model Version History
            </h2>
            <div className="space-y-4">
              {MODEL_VERSIONS.map((v) => (
                <div
                  key={v.version}
                  className="glass-card p-6"
                  style={{
                    borderLeft: v.isLive ? "3px solid #22C55E" : "3px solid #1E1E2E",
                  }}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-mono font-bold" style={{ fontSize: 18, color: "#F0F0F5" }}>
                          {v.version}
                        </span>
                        {v.isLive && <span className="badge badge-green">LIVE</span>}
                      </div>
                      <p style={{ fontSize: 13, color: "#8B8BA7" }}>
                        Trained: {v.trainedAt}
                      </p>
                      <p style={{ fontSize: 13, color: "#4A4A6A", marginTop: 4 }}>
                        Trigger: {v.trigger}
                      </p>
                    </div>
                    <div className="text-right">
                      <p style={{ fontSize: 11, color: "#4A4A6A" }}>Performance metrics</p>
                      <p className="font-mono text-sm mt-1" style={{ color: "#8B8BA7" }}>
                        MSE: {v.metrics.mse} · R²: {v.metrics.r2}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
