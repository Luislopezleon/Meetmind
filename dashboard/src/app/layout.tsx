import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MeetMind — Meeting intelligence, automated",
  description: "AI-powered meeting assistant that transcribes, extracts action items, decisions, and risks in real time.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
