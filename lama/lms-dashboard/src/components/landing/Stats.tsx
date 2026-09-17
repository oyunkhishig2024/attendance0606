"use client";

import { motion } from "framer-motion";

const stats = [
  { value: "1", label: "record per student, reused for every order" },
  { value: "4", label: "roles — admin, teacher, parent, student — one source of truth" },
  { value: "0", label: "spreadsheets to reconcile at delivery" },
];

export default function Stats() {
  return (
    <section className="border-y border-ink/10 bg-paper py-20">
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-12 px-6 sm:grid-cols-3">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: i * 0.08 }}
          >
            <p className="font-display text-6xl text-navy">{s.value}</p>
            <p className="mt-3 max-w-[22ch] text-sm text-ink/60">{s.label}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
