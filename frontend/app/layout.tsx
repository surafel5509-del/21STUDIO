import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "21STUDIO AI Agent",
  description: "Multi-provider AI Agent by 21STUDIO",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
