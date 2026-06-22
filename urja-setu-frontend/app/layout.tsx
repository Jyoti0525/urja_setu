import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "URJA-SETU — Energy Supply Chain Resilience",
  description:
    "AI-driven early-warning and decision-support for India's energy supply chain. ET AI Hackathon 2.0.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
