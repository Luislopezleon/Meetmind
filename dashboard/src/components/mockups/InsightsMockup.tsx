"use client";

import { motion } from "framer-motion";

const INSIGHTS = [
  { type: "Action Item", icon: "✓", color: "green", text: "María entrega el diseño de la landing", meta: "@María · viernes" },
  { type: "Decision", icon: "◆", color: "blue", text: "Usar Stripe como plan B si no hay respuesta del backend", meta: "impact: medium" },
  { type: "Risk", icon: "▲", color: "amber", text: "API de pagos sin confirmar del equipo backend", meta: "severity: high" },
];

const COLOR_MAP: Record<string, string> = {
  green: "text-green-400 bg-green-400/10 border-green-400/20",
  blue: "text-blue-400 bg-blue-400/10 border-blue-400/20",
  amber: "text-amber-400 bg-amber-400/10 border-amber-400/20",
};

export function InsightsMockup() {
  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[#0a0a0a] overflow-hidden shadow-2xl">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border)] bg-[#0d0d0d]">
        <span className="text-[11px] text-[var(--text-muted)]">AI Insights</span>
        <span className="ml-auto text-[10px] text-[var(--text-muted)] bg-[#161616] px-2 py-0.5 rounded-full">
          Gemini 3.5
        </span>
      </div>

      <div className="p-5 space-y-3">
        {INSIGHTS.map((insight, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -12 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.25, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="p-3.5 rounded-xl bg-[#111111] border border-[var(--border)]"
          >
            <div className="flex items-center gap-2 mb-2">
              <span className={`w-5 h-5 rounded-md flex items-center justify-center text-[10px] border ${COLOR_MAP[insight.color]}`}>
                {insight.icon}
              </span>
              <span className={`text-[10px] font-medium uppercase tracking-wide ${COLOR_MAP[insight.color].split(" ")[0]}`}>
                {insight.type}
              </span>
            </div>
            <p className="text-sm text-[var(--text)] leading-snug">{insight.text}</p>
            <p className="text-[11px] text-[var(--text-muted)] mt-1.5">{insight.meta}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
