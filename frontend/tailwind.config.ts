import type { Config } from "tailwindcss";

// Design tokens — cf. doc 03-Wireframes.md §2
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: ["class", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        bg:        "var(--bg)",
        "bg-e1":   "var(--bg-elev-1)",
        "bg-e2":   "var(--bg-elev-2)",
        "bg-e3":   "var(--bg-elev-3)",
        "bg-pinned": "var(--bg-pinned)",
        border:    "var(--border)",
        "border-strong": "var(--border-strong)",
        text:      "var(--text)",
        "text-muted": "var(--text-muted)",
        "text-dim":   "var(--text-dim)",
        "text-ghost": "var(--text-ghost)",
        accent:    "var(--accent)",
        "accent-soft": "var(--accent-soft)",
        "bubble-in":  "var(--bubble-in)",
        "bubble-out": "var(--bubble-out)",
      },
      fontFamily: {
        sys: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Text"', '"Segoe UI"', "Roboto", "sans-serif"],
      },
      transitionTimingFunction: {
        ios: "cubic-bezier(0.32, 0.72, 0, 1)",
      },
      transitionDuration: {
        micro: "150ms",
        std:   "280ms",
      },
    },
  },
  plugins: [],
} satisfies Config;
