"use client";

import { motion } from "framer-motion";

const PARTICIPANTS = [
  { name: "Luis", color: "from-blue-500 to-blue-700" },
  { name: "María", color: "from-pink-500 to-pink-700" },
  { name: "Carlos", color: "from-amber-500 to-amber-700" },
];

export function MeetMockup() {
  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[#0a0a0a] overflow-hidden shadow-2xl">
      {/* Fake browser chrome */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border)] bg-[#0d0d0d]">
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-[#333]" />
          <div className="w-2.5 h-2.5 rounded-full bg-[#333]" />
          <div className="w-2.5 h-2.5 rounded-full bg-[#333]" />
        </div>
        <div className="flex-1 flex justify-center">
          <div className="text-[11px] text-[var(--text-muted)] bg-[#161616] px-3 py-1 rounded-full">
            meet.google.com/abc-defg-hij
          </div>
        </div>
      </div>

      {/* Meet grid */}
      <div className="p-6 bg-gradient-to-b from-[#0a0a0a] to-[#050505]">
        <div className="grid grid-cols-2 gap-3">
          {PARTICIPANTS.map((p, i) => (
            <motion.div
              key={p.name}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15, duration: 0.5 }}
              className="relative aspect-video rounded-xl bg-[#141414] border border-[var(--border)] flex items-center justify-center overflow-hidden"
            >
              <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${p.color} flex items-center justify-center text-sm font-medium text-white`}>
                {p.name.charAt(0)}
              </div>
              <span className="absolute bottom-2 left-2 text-[10px] text-white/70 bg-black/40 px-2 py-0.5 rounded-full">
                {p.name}
              </span>
            </motion.div>
          ))}

          {/* Bot tile — highlighted */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.45, duration: 0.5 }}
            className="relative aspect-video rounded-xl bg-[#0f1520] border border-blue-500/40 flex items-center justify-center overflow-hidden"
            style={{ boxShadow: "0 0 30px rgba(59,130,246,0.15)" }}
          >
            <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center">
              <span className="text-black text-xs font-black">M</span>
            </div>
            <span className="absolute bottom-2 left-2 text-[10px] text-white/80 bg-black/40 px-2 py-0.5 rounded-full">
              MeetMind Bot
            </span>
            <span className="absolute top-2 right-2 flex items-center gap-1 text-[9px] text-red-400 bg-black/50 px-2 py-0.5 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
              REC
            </span>
          </motion.div>
        </div>

        {/* Fake toolbar */}
        <div className="flex items-center justify-center gap-3 mt-6">
          {["mic", "cam", "leave"].map((icon) => (
            <div
              key={icon}
              className={`w-9 h-9 rounded-full flex items-center justify-center ${
                icon === "leave" ? "bg-red-500/90" : "bg-[#1a1a1a] border border-[var(--border)]"
              }`}
            >
              <div className="w-3 h-3 rounded-full bg-white/60" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
