"use client";

import { useRef } from "react";
import {
  motion,
  useMotionValue,
  useScroll,
  useSpring,
  useTransform,
} from "framer-motion";
import MagneticButton from "./MagneticButton";

export default function Hero() {
  const sectionRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end start"],
  });
  const gridY = useTransform(scrollYProgress, [0, 1], [0, 80]);
  const contentOpacity = useTransform(scrollYProgress, [0, 0.8], [1, 0]);
  const contentY = useTransform(scrollYProgress, [0, 1], [0, 60]);

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [10, -10]), {
    stiffness: 150,
    damping: 20,
  });
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-10, 10]), {
    stiffness: 150,
    damping: 20,
  });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    mouseX.set((e.clientX - rect.left) / rect.width - 0.5);
    mouseY.set((e.clientY - rect.top) / rect.height - 0.5);
  };
  const resetTilt = () => {
    mouseX.set(0);
    mouseY.set(0);
  };

  return (
    <section
      ref={sectionRef}
      className="relative flex min-h-screen items-center overflow-hidden bg-paper"
    >
      <motion.div
        style={{ y: gridY }}
        className="bg-grid-fabric absolute inset-0 text-ink"
        aria-hidden
      />
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-paper via-transparent to-paper" />

      <motion.div
        style={{ opacity: contentOpacity, y: contentY }}
        className="relative mx-auto grid max-w-6xl grid-cols-1 items-center gap-16 px-6 py-32 md:grid-cols-2"
      >
        <div>
          <p className="mb-6 text-xs uppercase tracking-[0.3em] text-brass">
            Uniform Distribution Management System
          </p>
          <h1 className="text-balance font-display text-5xl leading-[1.05] text-ink md:text-6xl">
            Every uniform,
            <br />
            <span className="italic text-navy">accounted for.</span>
          </h1>
          <p className="mt-6 max-w-md text-balance text-lg text-ink/70">
            UDMS turns uniform sizing, ordering, and delivery into a single
            tracked record — from the first measurement to the last
            confirmed delivery.
          </p>
          <div className="mt-10 flex flex-wrap items-center gap-4">
            <MagneticButton href="/Sign-in">Sign in to UDMS</MagneticButton>
            <MagneticButton href="#pipeline" variant="ghost">
              See how it works
            </MagneticButton>
          </div>
        </div>

        <div
          onMouseMove={handleMouseMove}
          onMouseLeave={resetTilt}
          className="perspective-1200 hidden justify-self-center md:flex"
        >
          <motion.div
            style={{ rotateX, rotateY }}
            className="relative flex h-80 w-60 flex-col justify-between rounded-2xl border border-ink/10 bg-navy p-6 text-paper shadow-[0_30px_60px_-15px_rgba(14,23,48,0.45)]"
          >
            <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-paper/60">
              <span>Fit Tag</span>
              <span>№ 04812</span>
            </div>
            <div>
              <p className="font-display text-3xl italic text-brass-light">
                Delivered
              </p>
              <p className="mt-2 text-sm text-paper/70">
                Grade 6 · Size M · Set 2 of 2
              </p>
            </div>
            <div
              className="h-px w-full bg-stitch-line text-paper/30"
              aria-hidden
            />
          </motion.div>
        </div>
      </motion.div>
    </section>
  );
}
