import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "FINN — Indian Stock Market Investment Intelligence",
    short_name: "FINN",
    description: "Mobile-first investment intelligence for Indian stock markets (NSE & BSE) with audit-grade primary evidence citations.",
    start_url: "/",
    display: "standalone",
    orientation: "portrait",
    background_color: "#090e12",
    theme_color: "#090e12",
    categories: ["finance", "business", "productivity"],
    icons: [
      {
        src: "/icon.svg",
        sizes: "any",
        type: "image/svg+xml",
        purpose: "any"
      }
    ]
  };
}
