import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {
    colors: { navy: "#0A1628", accent: "#1E6FD9", surface: "#F5F7FA", border: "#E2E8F0" },
    fontFamily: { sans: ["Inter", "sans-serif"], mono: ["JetBrains Mono", "monospace"] },
    borderRadius: { DEFAULT: "4px", sm: "4px", md: "4px", lg: "4px" }
  } },
  plugins: []
} satisfies Config;