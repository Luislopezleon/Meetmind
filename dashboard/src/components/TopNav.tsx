"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Meetings" },
  { href: "/settings", label: "Settings" },
];

export function TopNav() {
  const pathname = usePathname();

  return (
    <header className="w-full border-b border-[var(--border)] bg-[var(--bg-primary)]/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[var(--accent)] to-blue-600 flex items-center justify-center transition-shadow duration-300 group-hover:shadow-lg group-hover:shadow-blue-500/25">
            <span className="text-white text-xs font-bold">M</span>
          </div>
          <span className="text-sm font-semibold text-[var(--text-primary)]">MeetMind</span>
        </Link>

        {/* Nav links */}
        <nav className="flex items-center gap-1">
          {LINKS.map((link) => {
            const isActive = link.href === "/" ? pathname === "/" || pathname.startsWith("/meetings") : pathname.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-1.5 rounded-lg text-sm transition-all duration-200 ${
                  isActive
                    ? "text-[var(--text-primary)] bg-[var(--bg-tertiary)]"
                    : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
