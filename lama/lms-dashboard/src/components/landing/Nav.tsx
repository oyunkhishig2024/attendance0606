"use client";

import Image from "next/image";
import Link from "next/link";
import { motion, useScroll, useTransform } from "framer-motion";

export default function Nav() {
  const { scrollY } = useScroll();
  const background = useTransform(
    scrollY,
    [0, 120],
    ["rgba(245, 240, 230, 0)", "rgba(245, 240, 230, 0.9)"]
  );
  const borderOpacity = useTransform(scrollY, [0, 120], [0, 1]);

  return (
    <motion.header
      style={{ backgroundColor: background }}
      className="fixed inset-x-0 top-0 z-40 backdrop-blur-sm"
    >
      <motion.div
        style={{ opacity: borderOpacity }}
        className="absolute inset-x-0 bottom-0 h-px bg-ink/10"
      />
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Link href="/" className="flex items-center gap-3">
          <Image src="/logo.png" alt="UDMS" width={28} height={28} />
          <span className="flex flex-col leading-none">
            <span className="font-display text-lg tracking-tight text-ink">
              UDMS
            </span>
            <span className="text-[10px] uppercase tracking-[0.2em] text-ink/50">
              Хувцас хангамж
            </span>
          </span>
        </Link>
        <div className="hidden items-center gap-8 text-sm text-ink/70 md:flex">
          <a href="#pipeline" className="hover:text-ink">
            How it works
          </a>
          <a href="#portals" className="hover:text-ink">
            Portals
          </a>
          <Link
            href="/Sign-in"
            className="rounded-full border border-ink/20 px-5 py-2 text-ink hover:border-ink/40"
          >
            Sign in
          </Link>
        </div>
      </nav>
    </motion.header>
  );
}
