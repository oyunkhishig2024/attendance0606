"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { motion } from "framer-motion";

const MotionLink = motion.create(Link);

type MagneticButtonProps = {
  href: string;
  children: React.ReactNode;
  variant?: "solid" | "ghost";
};

export default function MagneticButton({
  href,
  children,
  variant = "solid",
}: MagneticButtonProps) {
  const ref = useRef<HTMLAnchorElement>(null);
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  const handleMove = (e: React.MouseEvent<HTMLAnchorElement>) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    setOffset({ x: x * 0.3, y: y * 0.3 });
  };

  const reset = () => setOffset({ x: 0, y: 0 });

  const base =
    "relative inline-flex items-center justify-center gap-2 rounded-full px-7 py-3 text-sm tracking-wide transition-colors";
  const styles =
    variant === "solid"
      ? `${base} bg-navy text-paper hover:bg-navy-deep`
      : `${base} border border-ink/20 text-ink hover:border-ink/40`;

  return (
    <MotionLink
      ref={ref}
      href={href}
      onMouseMove={handleMove}
      onMouseLeave={reset}
      animate={{ x: offset.x, y: offset.y }}
      transition={{ type: "spring", stiffness: 200, damping: 15, mass: 0.4 }}
      className={styles}
    >
      {children}
    </MotionLink>
  );
}
