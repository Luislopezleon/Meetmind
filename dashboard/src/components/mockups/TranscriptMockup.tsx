"use client";

import { useEffect, useState } from "react";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";

const LINES = [
  { speaker: "Luis", text: "Necesitamos cerrar el diseño de la landing esta semana." },
  { speaker: "María", text: "Yo me encargo, lo tengo listo para el viernes." },
  { speaker: "Carlos", text: "Me preocupa la API de pagos, no está confirmada aún." },
];

export function TranscriptMockup() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });
  const [visibleLines, setVisibleLines] = useState(0);

  useEffect(() => {
    if (!inView) return;
    const timers = LINES.map((_, i) =>
      setTimeout(() => setVisibleLines((v) => Math.max(v, i + 1)), i * 900)
    );
    return () => timers.forEach(clearTimeout);
  }, [inView]);

  return (
    <div ref={ref} className="rounded-2xl border border-[var(--border)] bg-[#0a0a0a] overflow-hidden shadow-2xl">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border)] bg-[#0d0d0d]">
        <span className="text-[11px] text-[var(--text-muted)]">Live Transcript</span>
        <div className="flex items-center gap-1.5 ml-auto">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
          <span className="text-[10px] text-green-400">Recording</span>
        </div>
      </div>

      <div className="p-6 space-y-4 min-h-[220px]">
        {LINES.slice(0, visibleLines).map((line, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <p className="text-xs font-medium text-blue-400 mb-1">{line.speaker}</p>
            <TypedLine text={line.text} active={i === visibleLines - 1} />
          </motion.div>
        ))}
        {visibleLines < LINES.length && visibleLines > 0 && (
          <div className="flex gap-1 pt-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--text-muted)] animate-bounce [animation-delay:-0.3s]" />
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--text-muted)] animate-bounce [animation-delay:-0.15s]" />
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--text-muted)] animate-bounce" />
          </div>
        )}
      </div>
    </div>
  );
}

function TypedLine({ text, active }: { text: string; active: boolean }) {
  const [displayed, setDisplayed] = useState(active ? "" : text);

  useEffect(() => {
    if (!active) {
      setDisplayed(text);
      return;
    }
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) clearInterval(interval);
    }, 20);
    return () => clearInterval(interval);
  }, [active, text]);

  return <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{displayed}</p>;
}
