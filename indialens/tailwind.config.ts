import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // IndiaLens Design System
        bg: "#0A0A0F",
        surface: "#13131A",
        border: "#1E1E2E",
        primary: {
          DEFAULT: "#4F6EF7",
          hover: "#6B85F9",
          muted: "#1a2460",
        },
        secondary: {
          DEFAULT: "#F7C94F",
          muted: "#4a3a0f",
        },
        success: "#22C55E",
        warning: "#F59E0B",
        danger: "#EF4444",
        text: {
          primary: "#F0F0F5",
          secondary: "#8B8BA7",
          muted: "#4A4A6A",
        },
      },
      fontFamily: {
        display: ["Clash Display", "Plus Jakarta Sans", "sans-serif"],
        body: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      fontSize: {
        "display-xl": ["clamp(3rem, 6vw, 5rem)", { lineHeight: "1.05", letterSpacing: "-0.03em" }],
        "display-lg": ["clamp(2rem, 4vw, 3.5rem)", { lineHeight: "1.1", letterSpacing: "-0.025em" }],
        "display-md": ["clamp(1.5rem, 3vw, 2.5rem)", { lineHeight: "1.2", letterSpacing: "-0.02em" }],
      },
      spacing: {
        "4": "4px",
        "8": "8px",
        "12": "12px",
        "16": "16px",
        "24": "24px",
        "32": "32px",
        "48": "48px",
        "64": "64px",
        "96": "96px",
      },
      borderRadius: {
        card: "8px",
        input: "4px",
        tag: "999px",
        table: "0px",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-hero": "radial-gradient(ellipse 80% 50% at 50% -20%, #1a2460 0%, transparent 100%)",
        "gradient-card": "linear-gradient(135deg, #13131A 0%, #0d0d14 100%)",
        "noise": "url('/noise.svg')",
      },
      animation: {
        "fade-in": "fadeIn 0.4s ease forwards",
        "slide-up": "slideUp 0.5s ease forwards",
        "pulse-dot": "pulseDot 2s ease-in-out infinite",
        "number-roll": "numberRoll 0.8s ease forwards",
        "ring-fill": "ringFill 1.2s ease forwards",
      },
      keyframes: {
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        slideUp: {
          from: { opacity: "0", transform: "translateY(20px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        pulseDot: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.4" },
        },
        numberRoll: {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        ringFill: {
          from: { "stroke-dashoffset": "339" },
          to: { "stroke-dashoffset": "var(--ring-offset)" },
        },
      },
      boxShadow: {
        card: "0 0 0 1px #1E1E2E, 0 4px 20px rgba(0,0,0,0.4)",
        glow: "0 0 30px rgba(79, 110, 247, 0.2)",
        "glow-gold": "0 0 30px rgba(247, 201, 79, 0.15)",
        "inner-glow": "inset 0 1px 0 rgba(255,255,255,0.05)",
      },
    },
  },
  plugins: [],
};
export default config;
