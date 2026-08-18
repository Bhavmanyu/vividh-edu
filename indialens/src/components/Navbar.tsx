"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart2, Search, Zap, BookOpen, Shield, Menu, X } from "lucide-react";
import { useState, useEffect } from "react";

const NAV_LINKS = [
  { href: "/index", label: "ROI Index", icon: <BarChart2 size={14} /> },
  { href: "/analyze", label: "Analyze My ROI", icon: <Search size={14} /> },
  { href: "/methodology", label: "Methodology", icon: <BookOpen size={14} /> },
];

export function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handler);
    return () => window.removeEventListener("scroll", handler);
  }, []);

  return (
    <nav
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        background: scrolled
          ? "rgba(10,10,15,0.95)"
          : "rgba(10,10,15,0.6)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        borderBottom: "1px solid",
        borderColor: scrolled ? "#1E1E2E" : "transparent",
        transition: "all 0.3s ease",
      }}
    >
      <div className="container-xl">
        <div className="flex items-center justify-between" style={{ height: 60 }}>
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2" style={{ textDecoration: "none" }}>
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
              style={{ fontSize: 18, color: "#F0F0F5", letterSpacing: "-0.02em" }}
            >
              India<span style={{ color: "#4F6EF7" }}>Lens</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map((link) => {
              const active = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    padding: "6px 14px",
                    borderRadius: 6,
                    fontSize: 13,
                    fontWeight: active ? 600 : 500,
                    color: active ? "#F0F0F5" : "#8B8BA7",
                    background: active ? "rgba(79,110,247,0.1)" : "transparent",
                    textDecoration: "none",
                    transition: "all 0.15s",
                  }}
                  onMouseEnter={(e) => {
                    if (!active) {
                      (e.currentTarget as HTMLElement).style.color = "#F0F0F5";
                      (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.04)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!active) {
                      (e.currentTarget as HTMLElement).style.color = "#8B8BA7";
                      (e.currentTarget as HTMLElement).style.background = "transparent";
                    }
                  }}
                >
                  {link.icon}
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* CTA + Admin */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              href="/admin"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 5,
                fontSize: 12,
                color: "#4A4A6A",
                textDecoration: "none",
                transition: "color 0.15s",
              }}
              onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.color = "#8B8BA7")}
              onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.color = "#4A4A6A")}
            >
              <Shield size={12} />
              Admin
            </Link>
            <Link href="/analyze" className="btn-primary" style={{ padding: "8px 18px", fontSize: 13 }}>
              Find My ROI
            </Link>
          </div>

          {/* Mobile menu toggle */}
          <button
            className="md:hidden"
            onClick={() => setMobileOpen((v) => !v)}
            style={{
              background: "none",
              border: "none",
              color: "#8B8BA7",
              cursor: "pointer",
              padding: 4,
            }}
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div
          style={{
            borderTop: "1px solid #1E1E2E",
            background: "rgba(10,10,15,0.98)",
            padding: "16px 24px",
          }}
        >
          <div className="flex flex-col gap-2">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "10px 12px",
                  borderRadius: 6,
                  fontSize: 14,
                  color: pathname === link.href ? "#F0F0F5" : "#8B8BA7",
                  background: pathname === link.href ? "rgba(79,110,247,0.1)" : "transparent",
                  textDecoration: "none",
                }}
              >
                {link.icon}
                {link.label}
              </Link>
            ))}
            <Link
              href="/analyze"
              onClick={() => setMobileOpen(false)}
              className="btn-primary mt-2 justify-center"
              style={{ fontSize: 14 }}
            >
              Find My ROI
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
