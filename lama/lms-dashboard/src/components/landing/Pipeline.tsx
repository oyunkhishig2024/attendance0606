"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

const steps = [
  {
    label: "01 · Measure",
    title: "Every size, recorded once.",
    body: "A student's measurements are captured a single time and reused for every future order — no re-measuring, no guesswork.",
  },
  {
    label: "02 · Request",
    title: "Orders start from the roster.",
    body: "Admins and teachers request uniforms directly against class rosters, so nothing is ordered for a student who already has it.",
  },
  {
    label: "03 · Fulfill",
    title: "Stock is matched, not guessed.",
    body: "Requests are matched against available stock and queued for delivery, with shortages flagged before they become a problem.",
  },
  {
    label: "04 · Confirm",
    title: "Delivery closes the loop.",
    body: "Parents and students confirm receipt in the same system — turning a delivery into a record, not an assumption.",
  },
];

export default function Pipeline() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start 0.8", "end 0.4"],
  });
  const lineScale = useTransform(scrollYProgress, [0, 1], [0, 1]);

  return (
    <section id="pipeline" ref={ref} className="relative bg-paper py-32">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-20 max-w-xl">
          <p className="mb-4 text-xs uppercase tracking-[0.3em] text-brass">
            How it works
          </p>
          <h2 className="text-balance font-display text-4xl text-ink md:text-5xl">
            One record, from order to wear.
          </h2>
        </div>

        <div className="relative grid grid-cols-1 gap-x-12 gap-y-16 md:grid-cols-[2px_1fr] md:gap-y-24">
          <div className="relative hidden md:block">
            <div className="absolute inset-y-0 left-0 w-px bg-ink/10" />
            <motion.div
              style={{ scaleY: lineScale }}
              className="absolute inset-y-0 left-0 w-px origin-top bg-brass"
            />
          </div>

          <div className="flex flex-col gap-16 md:col-start-2 md:gap-24">
            {steps.map((step, i) => (
              <motion.div
                key={step.label}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-15% 0px -15% 0px" }}
                transition={{ duration: 0.6, ease: "easeOut", delay: i * 0.05 }}
                className="grid grid-cols-1 gap-4 md:grid-cols-[140px_1fr]"
              >
                <span className="font-display text-sm uppercase tracking-[0.15em] text-ink/40">
                  {step.label}
                </span>
                <div>
                  <h3 className="font-display text-2xl text-ink md:text-3xl">
                    {step.title}
                  </h3>
                  <p className="mt-3 max-w-md text-ink/70">{step.body}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
