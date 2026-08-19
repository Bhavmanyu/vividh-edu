"use client";

import Link from "next/link";
import { Zap, ExternalLink } from "lucide-react";
import { PLATFORM_STATS } from "../lib/mock-data";

export function Footer() {
  return (
    <footer
      style={{
        borderTop: "1px solid #1E1E2E",
        background: "#0A0A0F",
        padding: "48px 0 32px",
        marginTop: 96,
      }}
    >
      <div className="container-xl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 6,
                  background: "linear-gradient(135deg, #4F6EF7, #8BA4FF)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Zap size={14} fill="white" color="white" />
              </div>
              <span
                className="font-display font-bold"
                style={{ fontSize: 18, color: "#F0F0F5" }}
              >
                India<span style={{ color: "#4F6EF7" }}>Lens</span>
              </span>
            </div>
            <p style={{ color: "#8B8BA7", fontSize: 14, lineHeight: 1.7, maxWidth: 320 }}>
              India&apos;s first quantitative education and career intelligence
              platform. Every score has a source. Every prediction has an
              uncertainty range.
            </p>
            <p
              className="mt-4 text-xs font-mono"
              style={{ color: "#4A4A6A" }}
            >
              {PLATFORM_STATS.collegesTracked} colleges · {PLATFORM_STATS.programsIndexed} programs indexed · Verified data
            </p>
          </div>

          {/* Platform */}
          <div>
            <p
              className="text-xs font-semibold uppercase tracking-wider mb-4"
              style={{ color: "#4A4A6A", letterSpacing: "0.08em" }}
            >
              Platform
            </p>
            <div className="flex flex-col gap-2">
              {[
                { href: "/explore", label: "ROI Index" },
                { href: "/analyze", label: "Student Engine" },
                { href: "/methodology", label: "Methodology" },
                { href: "/admin", label: "Educator Portal" },
              ].map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  style={{
                    color: "#8B8BA7",
                    fontSize: 13,
                    textDecoration: "none",
                    transition: "color 0.15s",
                  }}
                  onMouseEnter={(e) =>
                    ((e.currentTarget as HTMLElement).style.color = "#F0F0F5")
                  }
                  onMouseLeave={(e) =>
                    ((e.currentTarget as HTMLElement).style.color = "#8B8BA7")
                  }
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>

          {/* Data sources */}
          <div>
            <p
              className="text-xs font-semibold uppercase tracking-wider mb-4"
              style={{ color: "#4A4A6A", letterSpacing: "0.08em" }}
            >
              Data Sources
            </p>
            <div className="flex flex-col gap-2">
              {["NIRF", "AmbitionBox", "PLFS / MoSPI", "World Bank ICP", "CMIE", "Reddit API"].map(
                (src) => (
                  <span key={src} style={{ color: "#8B8BA7", fontSize: 13 }}>
                    {src}
                  </span>
                )
              )}
            </div>
          </div>
        </div>

        <div
          style={{
            borderTop: "1px solid #1E1E2E",
            paddingTop: 24,
            display: "flex",
            flexDirection: "row",
            flexWrap: "wrap",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 12,
          }}
        >
          <div className="flex flex-wrap items-center gap-4">
            <span style={{ color: "#4A4A6A", fontSize: 12 }}>
              © 2025 IndiaLens. Open methodology, public index.
            </span>
            <Link
              href="/methodology"
              style={{
                color: "#4A4A6A",
                fontSize: 12,
                textDecoration: "none",
                display: "flex",
                alignItems: "center",
                gap: 4,
              }}
            >
              <ExternalLink size={10} />
              Cite this index
            </Link>
          </div>
          <div className="flex items-center gap-3">
            <span
              className="text-xs font-mono"
              style={{ color: "#4A4A6A" }}
            >
              Model v1.0-seed
            </span>
            <div className="flex items-center gap-1.5">
              <span className="pulse-dot" />
              <span style={{ color: "#22C55E", fontSize: 11, fontWeight: 600 }}>
                Live
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
