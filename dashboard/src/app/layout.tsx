import type { Metadata } from "next";
import "./globals.css";
import { TopNav } from "@/components/TopNav";
import { AnimatedBackground } from "@/components/AnimatedBackground";

export const metadata: Metadata = {
  title: "MeetMind",
  description: "AI-powered meeting intelligence",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="noise-bg">
        <AnimatedBackground />
        <div className="relative z-10 min-h-screen flex flex-col">
          <TopNav />
          <main className="flex-1 w-full max-w-5xl mx-auto px-6 py-10">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
