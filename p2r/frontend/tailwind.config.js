/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Shared Nous RCM Framework palette (same tokens as ACE — one platform).
        brand: {
          50: "#fff4ed", 100: "#ffe6d5", 300: "#ffb088",
          500: "#f26722", 600: "#e2520f", 700: "#bb3e0f",
        },
        ace: {
          50: "#eef2ff", 100: "#e0e7ff", 400: "#818cf8",
          500: "#6366f1", 600: "#4f46e5", 700: "#4338ca", 900: "#1e1b4b",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(16,24,40,.06), 0 1px 3px rgba(16,24,40,.1)",
      },
    },
  },
  plugins: [],
};
