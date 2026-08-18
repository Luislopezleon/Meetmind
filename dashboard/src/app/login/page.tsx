"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { DotGridBackground } from "@/components/DotGridBackground";

export default function LoginPage() {
  return (
    <>
      <DotGridBackground />
      <div className="relative z-10 min-h-screen flex items-center justify-center px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="w-full max-w-md"
        >
          {/* Dev banner */}
          <div className="mb-8 p-4 rounded-xl border border-amber-500/20 bg-amber-500/5 text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <span className="text-xs font-medium text-amber-400 uppercase tracking-wider">In Development</span>
            </div>
            <p className="text-sm text-[var(--text-secondary)]">
              MeetMind is currently in active development. Authentication is not available yet.
            </p>
          </div>

          {/* Card */}
          <div className="card p-8 text-center">
            {/* Logo */}
            <div className="flex justify-center mb-6">
              <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center">
                <span className="text-black text-sm font-black">M</span>
              </div>
            </div>

            <h1 className="text-xl font-semibold tracking-tight mb-2">Welcome to MeetMind</h1>
            <p className="text-sm text-[var(--text-muted)] mb-8">
              Sign in and sign up will be available once we launch.<br />
              For now, you can explore the demo dashboard below.
            </p>

            {/* Disabled auth buttons */}
            <div className="space-y-3 mb-6">
              <button disabled className="w-full py-2.5 rounded-xl bg-[var(--bg-elevated)] border border-[var(--border)] text-sm text-[var(--text-muted)] cursor-not-allowed flex items-center justify-center gap-2">
                <svg className="w-4 h-4" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
                Continue with Google
              </button>
              <button disabled className="w-full py-2.5 rounded-xl bg-[var(--bg-elevated)] border border-[var(--border)] text-sm text-[var(--text-muted)] cursor-not-allowed">
                Continue with email
              </button>
            </div>

            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-[var(--border)]" /></div>
              <div className="relative flex justify-center"><span className="px-3 bg-[var(--bg-card)] text-xs text-[var(--text-muted)]">or</span></div>
            </div>

            {/* Demo button */}
            <Link
              href="/app"
              className="btn-primary w-full block text-center"
            >
              Try the demo →
            </Link>

            <p className="text-[11px] text-[var(--text-muted)] mt-4">
              The demo contains real AI-analyzed meeting data.
            </p>
          </div>

          {/* Back link */}
          <div className="text-center mt-6">
            <Link href="/" className="text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors">
              ← Back to homepage
            </Link>
          </div>
        </motion.div>
      </div>
    </>
  );
}
