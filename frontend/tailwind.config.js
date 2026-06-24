/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg:      "#0f172a",
        card:    "#1e293b",
        border:  "#334155",
        accent:  "#6366f1",
        "accent-hover": "#4f46e5",
        muted:   "#94a3b8",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
