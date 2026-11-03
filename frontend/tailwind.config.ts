import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101820",
        paper: "#F4F5F2",
        muted: "#737B80",
        line: "#E2E5E1",
        signal: "#C7F36B"
      }
    }
  },
  plugins: []
};

export default config;
