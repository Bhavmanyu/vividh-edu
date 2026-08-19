"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart2, Search, Zap, BookOpen, Shield, Menu, X, Sparkles, Scale, Compass } from "lucide-react";
import { useState, useEffect } from "react";

const NAV_LINKS = [
  { href: "/explore", label: "Explore Colleges", icon: <Compass size={14} /> },
  { href: "/analyze", label: "Calculate ROI", icon: <Search size={14} /> },
  { href: "/advisor", label: "AI Advisor", icon: <Sparkles size={14} className="text-emerald-400" /> },
  { href: "/compare", label: "Compare", icon: <Scale size={14} /> },
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
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-slate-950/90 backdrop-blur-xl border-b border-white/[0.08] shadow-2xl py-2.5"
          : "bg-slate-950/40 backdrop-blur-md border-b border-white/[0.04] py-3.5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-11">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 via-indigo-600 to-emerald-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-all">
              <Zap size={16} className="text-slate-950 fill-slate-950" />
            </div>
            <span className="font-extrabold text-lg text-white tracking-tight">
              India<span className="text-indigo-400">Lens</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1.5 bg-slate-900/60 p-1 rounded-xl border border-white/[0.06]">
            {NAV_LINKS.map((link) => {
              const active = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    active
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                      : "text-slate-400 hover:text-white hover:bg-white/[0.04]"
                  }`}
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
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors font-medium px-2 py-1"
            >
              <Shield size={13} className="text-slate-500" />
              Admin Portal
            </Link>
            <Link
              href="/analyze"
              className="px-4 py-2 text-xs font-bold text-slate-950 bg-gradient-to-r from-emerald-400 to-teal-300 hover:opacity-90 rounded-xl shadow-lg shadow-emerald-500/10 transition-all"
            >
              Find My ROI
            </Link>
          </div>

          {/* Mobile menu toggle */}
          <button
            className="md:hidden p-2 text-slate-400 hover:text-white"
            onClick={() => setMobileOpen((v) => !v)}
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden bg-slate-950/95 backdrop-blur-2xl border-b border-slate-800 px-6 py-4 space-y-2 mt-2">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setMobileOpen(false)}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-semibold ${
                pathname === link.href ? "bg-indigo-600 text-white" : "text-slate-300 hover:bg-slate-900"
              }`}
            >
              {link.icon}
              {link.label}
            </Link>
          ))}
          <Link
            href="/analyze"
            onClick={() => setMobileOpen(false)}
            className="w-full mt-3 py-2.5 text-center text-xs font-bold text-slate-950 bg-emerald-400 rounded-xl block"
          >
            Find My ROI
          </Link>
        </div>
      )}
    </nav>
  );
}
