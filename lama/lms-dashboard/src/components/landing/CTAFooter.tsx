"use client";

import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import MagneticButton from "./MagneticButton";

export default function CTAFooter() {
  return (
    <footer className="bg-ink text-paper">
      <div className="mx-auto max-w-6xl px-6 py-32 text-center">
        <motion.h2
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-balance font-display text-4xl md:text-6xl"
        >
          Stop tracking uniforms
          <br />
          <span className="italic text-brass-light">by memory.</span>
        </motion.h2>
        <div className="mt-10 flex justify-center">
          <MagneticButton href="/Sign-in">Sign in to UDMS</MagneticButton>
        </div>
      </div>

      <div className="border-t border-paper/10">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-8 text-xs text-paper/50 sm:flex-row">
          <div className="flex items-center gap-2">
            <Image src="/logo.png" alt="UDMS" width={18} height={18} />
            <span>UDMS — Uniform Distribution Management System</span>
          </div>
          <Link href="/Sign-in" className="hover:text-paper">
            Sign in
          </Link>
        </div>
      </div>
    </footer>
  );
}
