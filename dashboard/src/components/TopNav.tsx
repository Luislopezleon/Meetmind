"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function TopNav() {
  const pathname = usePathname();

  const isSettings = pathname.startsWith("/app/settings");

  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-[var(--border)] bg-black/80 backdrop-blur-xl">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-white flex items-center justify-center">
            <span className="text-black text-[10px] font-black">M</span>
          </div>
          <span className="text-sm font-semibold tracking-tight">MeetMind</span>
        </Link>

        <nav className="flex items-center gap-8">
          <Link
            href="/app"
            className={`text-sm transition-colors duration-200 ${
              !isSettings ? "text-[var(--text)]" : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
            }`}
          >
            Meetings
          </Link>
          <Link
            href="/app/settings"
            className={`text-sm transition-colors duration-200 ${
              isSettings ? "text-[var(--text)]" : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
            }`}
          >
            Settings
          </Link>
        </nav>
      </div>
    </header>
  );
}
