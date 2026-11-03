import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FINN — Investment Intelligence",
  description: "A focused intelligence layer for public-markets investors.",
  applicationName: "FINN",
  appleWebApp: { capable: true, statusBarStyle: "black-translucent", title: "FINN" }
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#10151b"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
