import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f5f3ff",
          100: "#ede9fe",
          200: "#ddd6fe",
          300: "#c4b5fd",
          400: "#a78bfa",
          500: "#7c5cfc",
          600: "#6a4aee",
          700: "#5b3dd4",
          800: "#4c33b0",
          900: "#3d2a8a",
        },
      },
    },
  },
  plugins: [],
};

export default config;
