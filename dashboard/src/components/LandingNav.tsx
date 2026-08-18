"use client";

import Link from "next/link";
import { motion } from "framer-motion";

export function LandingNav() {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="fixed top-0 left-0 right-0 z-50 border-b border-[var(--border)] bg-black/70 backdrop-blur-xl"
    >
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-white flex items-center justify-center">
            <span className="text-black text-[10px] font-black">M</span>
          </div>
          <span className="text-sm font-semibold tracking-tight">MeetMind</span>
        </Link>

        <nav className="hidden md:flex items-center gap-8 text-sm text-[var(--text-muted)]">
          <a href="#product" className="hover:text-[var(--text)] transition-colors duration-200">Product</a>
          <a href="#how-it-works" className="hover:text-[var(--text)] transition-colors duration-200">How it works</a>
          <a href="#pricing" className="hover:text-[var(--text)] transition-colors duration-200">Pricing</a>
        </nav>

        <div className="flex items-center gap-3">
          <Link href="/login" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text)] transition-colors duration-200 px-3 py-1.5">
            Sign in
          </Link>
          <Link href="/login" className="btn-primary text-sm">
            Sign up
          </Link>
        </div>
      </div>
    </motion.header>
  );
}
