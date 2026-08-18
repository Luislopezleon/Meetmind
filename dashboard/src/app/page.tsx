"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { LandingNav } from "@/components/LandingNav";
import { DotGridBackground } from "@/components/DotGridBackground";
import { RevealText } from "@/components/RevealText";
import { MeetMockup } from "@/components/mockups/MeetMockup";
import { TranscriptMockup } from "@/components/mockups/TranscriptMockup";
import { InsightsMockup } from "@/components/mockups/InsightsMockup";

export default function LandingPage() {
  return (
    <>
      <DotGridBackground />
      <LandingNav />

      <main className="relative z-10">
        {/* HERO */}
        <section className="max-w-5xl mx-auto px-6 pt-36 pb-32 text-center">
          <RevealText
            el="h1"
            text="Every meeting, understood."
            className="text-5xl md:text-6xl font-bold tracking-tight leading-[1.1]"
          />
          <RevealText
            el="h1"
            text="Automatically."
            delay={0.3}
            className="text-5xl md:text-6xl font-bold tracking-tight leading-[1.1] text-[var(--text-muted)]"
          />

          <motion.p
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="text-lg text-[var(--text-secondary)] max-w-xl mx-auto mt-6"
          >
            MeetMind sends an AI bot to your meetings. It transcribes, detects action items,
            decisions, and risks — then hands you a clean summary. No note-taking required.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.8, duration: 0.5 }}
            className="flex items-center justify-center gap-4 mt-10"
          >
            <Link href="/login" className="btn-primary">Get started free</Link>
            <a href="#product" className="btn-secondary">See how it works</a>
          </motion.div>
        </section>

        {/* PRODUCT SHOWCASE */}
        <section id="product" className="max-w-6xl mx-auto px-6 py-24 space-y-40">
          <ShowcaseRow
            eyebrow="01 · Join"
            title="It joins the call for you."
            description="Paste any Google Meet, Zoom, or Teams link. Our bot joins silently, records, and starts transcribing — no plugins, no setup on your end."
          >
            <MeetMockup />
          </ShowcaseRow>

          <ShowcaseRow
            eyebrow="02 · Transcribe"
            title="Every word, captured live."
            description="Real-time transcription with speaker identification streams straight to your dashboard as the conversation happens."
            reverse
          >
            <TranscriptMockup />
          </ShowcaseRow>

          <ShowcaseRow
            eyebrow="03 · Understand"
            title="AI extracts what matters."
            description="A LangGraph agent reads the transcript and pulls out action items, decisions, and risks — each with an assignee, confidence score, and context."
          >
            <InsightsMockup />
          </ShowcaseRow>
        </section>

        {/* HOW IT WORKS */}
        <section id="how-it-works" className="max-w-4xl mx-auto px-6 py-24">
          <div className="text-center mb-16">
            <RevealText el="h2" text="From meeting to insight in four steps." className="text-3xl font-bold tracking-tight" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { n: "01", t: "Send the link", d: "Paste your meeting URL into MeetMind." },
              { n: "02", t: "Bot joins", d: "Our AI bot connects and starts recording." },
              { n: "03", t: "AI analyzes", d: "LangGraph + Gemini extract insights in real time." },
              { n: "04", t: "Review & act", d: "Get a live dashboard and executive summary." },
            ].map((step, i) => (
              <motion.div
                key={step.n}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
                className="card p-5"
              >
                <span className="text-xs text-[var(--text-muted)] font-mono">{step.n}</span>
                <h3 className="text-sm font-medium mt-3 mb-1.5">{step.t}</h3>
                <p className="text-xs text-[var(--text-muted)] leading-relaxed">{step.d}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="max-w-3xl mx-auto px-6 py-32 text-center">
          <RevealText el="h2" text="Stop taking notes. Start acting on them." className="text-4xl font-bold tracking-tight mb-6" />
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
          >
            <Link href="/login" className="btn-primary text-base px-8 py-3">Get started free</Link>
          </motion.div>
        </section>

        {/* TECH MARQUEE */}
        <section className="py-16 overflow-hidden border-t border-[var(--border)]">
          <div className="relative">
            <div className="flex animate-marquee gap-16 items-center">
              {[...Array(2)].map((_, set) => (
                <div key={set} className="flex gap-16 items-center shrink-0">
                  {[
                    { name: "FastAPI", svg: "⚡" },
                    { name: "LangGraph", svg: "◇" },
                    { name: "Google Gemini", svg: "✦" },
                    { name: "Recall.ai", svg: "●" },
                    { name: "PostgreSQL", svg: "◆" },
                    { name: "Redis", svg: "◈" },
                    { name: "Next.js", svg: "▲" },
                    { name: "Docker", svg: "◉" },
                    { name: "WebSockets", svg: "⟐" },
                    { name: "TypeScript", svg: "◊" },
                  ].map((tech) => (
                    <div key={tech.name} className="flex items-center gap-2 opacity-30 hover:opacity-60 transition-opacity duration-300">
                      <span className="text-sm">{tech.svg}</span>
                      <span className="text-xs font-medium text-[var(--text-muted)] whitespace-nowrap">{tech.name}</span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FOOTER */}
        <footer className="border-t border-[var(--border)] py-8">
          <div className="max-w-6xl mx-auto px-6 flex items-center justify-between text-xs text-[var(--text-muted)]">
            <span>© 2026 MeetMind</span>
            <span>Built with FastAPI, LangGraph &amp; Next.js</span>
          </div>
        </footer>
      </main>
    </>
  );
}

function ShowcaseRow({
  eyebrow,
  title,
  description,
  children,
  reverse,
}: {
  eyebrow: string;
  title: string;
  description: string;
  children: React.ReactNode;
  reverse?: boolean;
}) {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 gap-12 items-center ${reverse ? "md:[direction:rtl]" : ""}`}>
      <div style={{ direction: "ltr" }}>
        <motion.span
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-xs text-[var(--text-muted)] font-mono uppercase tracking-wider"
        >
          {eyebrow}
        </motion.span>
        <RevealText el="h2" text={title} className="text-3xl font-bold tracking-tight mt-3 mb-4" />
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-[var(--text-secondary)] leading-relaxed"
        >
          {description}
        </motion.p>
      </div>
      <motion.div
        style={{ direction: "ltr" }}
        initial={{ opacity: 0, scale: 0.96 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      >
        {children}
      </motion.div>
    </div>
  );
}
