import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: "hsl(var(--card))",
        "card-foreground": "hsl(var(--card-foreground))",
        popover: "hsl(var(--popover))",
        "popover-foreground": "hsl(var(--popover-foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        bullish: {
          DEFAULT: "#10b981",
          light: "#34d399",
          dark: "#059669",
          bg: "rgba(16, 185, 129, 0.12)",
        },
        bearish: {
          DEFAULT: "#f43f5e",
          light: "#fb7185",
          dark: "#e11d48",
          bg: "rgba(244, 63, 94, 0.12)",
        },
        neutral: {
          DEFAULT: "#8b5cf6",
          light: "#a78bfa",
          dark: "#7c3aed",
          bg: "rgba(139, 92, 246, 0.12)",
        },
        cyan: {
          DEFAULT: "#06b6d4",
          glow: "rgba(6, 182, 212, 0.25)",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      animation: {
        pulse_fast: "pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        glow: "glow 2s ease-in-out infinite alternate",
      },
    },
  },
  plugins: [],
};

export default config;
