import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "21STUDIO — Intelligent Workspace",
  description: "A modern multi-provider AI workspace powered by Mistral, Groq, and Cerebras.",
  applicationName: "21STUDIO",
  keywords: ["AI", "agent", "21STUDIO", "Mistral", "Groq", "Cerebras"],
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#07070a",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
