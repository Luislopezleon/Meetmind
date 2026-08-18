"use client";

import { motion } from "framer-motion";

/**
 * Splits text into words and reveals them left-to-right with a
 * staggered fade+slide animation triggered on scroll into view.
 */
export function RevealText({
  text,
  className = "",
  delay = 0,
  el: El = "span",
}: {
  text: string;
  className?: string;
  delay?: number;
  el?: "span" | "h1" | "h2" | "h3" | "p";
}) {
  const words = text.split(" ");

  return (
    <El className={className}>
      {words.map((word, i) => (
        <span key={i} className="inline-block overflow-hidden pb-1 mr-[0.25em]">
          <motion.span
            className="inline-block"
            initial={{ y: "110%", opacity: 0 }}
            whileInView={{ y: "0%", opacity: 1 }}
            viewport={{ once: true }}
            transition={{
              duration: 0.6,
              delay: delay + i * 0.045,
              ease: [0.16, 1, 0.3, 1],
            }}
          >
            {word}
          </motion.span>
        </span>
      ))}
    </El>
  );
}
