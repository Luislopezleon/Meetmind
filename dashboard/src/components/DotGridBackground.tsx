"use client";

import { useEffect, useRef } from "react";

/**
 * Animated 3D-ish network of dots that continuously drifts and
 * reacts subtly to mouse position. Inspired by network/particle
 * hero backgrounds (Prime UI style).
 */
export function DotGridBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef({ x: -9999, y: -9999 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = 0;
    let height = 0;
    let animationId: number;

    interface Dot {
      x: number;
      y: number;
      z: number; // depth, affects size/opacity
      vx: number;
      vy: number;
    }

    let dots: Dot[] = [];

    const resize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    const init = () => {
      dots = [];
      const spacing = 46;
      const cols = Math.ceil(width / spacing) + 2;
      const rows = Math.ceil(height / spacing) + 2;

      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          dots.push({
            x: i * spacing + (Math.random() - 0.5) * 10,
            y: j * spacing + (Math.random() - 0.5) * 10,
            z: Math.random(),
            vx: (Math.random() - 0.5) * 0.15,
            vy: (Math.random() - 0.5) * 0.15,
          });
        }
      }
    };

    let t = 0;

    const animate = () => {
      t += 0.003;
      ctx.clearRect(0, 0, width, height);

      const mx = mouseRef.current.x;
      const my = mouseRef.current.y;

      for (const d of dots) {
        // Gentle organic drift (wave motion)
        d.x += d.vx + Math.sin(t + d.y * 0.01) * 0.15;
        d.y += d.vy + Math.cos(t + d.x * 0.01) * 0.15;

        // Wrap around edges
        if (d.x < -20) d.x = width + 20;
        if (d.x > width + 20) d.x = -20;
        if (d.y < -20) d.y = height + 20;
        if (d.y > height + 20) d.y = -20;

        // Distance to mouse for subtle glow boost
        const dx = mx - d.x;
        const dy = my - d.y;
        const distSq = dx * dx + dy * dy;
        const mouseBoost = distSq < 40000 ? (1 - distSq / 40000) * 0.5 : 0;

        const size = 0.8 + d.z * 1.2;
        const opacity = 0.08 + d.z * 0.12 + mouseBoost;

        ctx.beginPath();
        ctx.arc(d.x, d.y, size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
        ctx.fill();
      }

      // Draw connecting lines between nearby dots (sparse, for network feel)
      ctx.lineWidth = 0.5;
      for (let i = 0; i < dots.length; i++) {
        const a = dots[i];
        // only check a handful of neighbors ahead for perf
        for (let j = i + 1; j < Math.min(i + 8, dots.length); j++) {
          const b = dots[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 55) {
            const opacity = (1 - dist / 55) * 0.05;
            ctx.strokeStyle = `rgba(255, 255, 255, ${opacity})`;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
      }

      animationId = requestAnimationFrame(animate);
    };

    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY };
    };
    const handleResize = () => {
      resize();
      init();
    };

    resize();
    init();
    animate();

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{
        maskImage: "radial-gradient(ellipse 80% 60% at 50% 0%, black 40%, transparent 90%)",
        WebkitMaskImage: "radial-gradient(ellipse 80% 60% at 50% 0%, black 40%, transparent 90%)",
      }}
    />
  );
}
