"use client";

import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";

const portals = [
  {
    href: "/admin",
    icon: "/setting.png",
    role: "Admin",
    body: "Manage stock, approve requests, and see distribution across every class.",
  },
  {
    href: "/teacher",
    icon: "/teacher.png",
    role: "Teacher",
    body: "Request uniforms for a class and track what's still outstanding.",
  },
  {
    href: "/parent",
    icon: "/parent.png",
    role: "Parent",
    body: "Confirm sizing and delivery for your child without a paper form.",
  },
  {
    href: "/student",
    icon: "/student.png",
    role: "Student",
    body: "See your own uniform record — what's issued, and what's next.",
  },
];

export default function Portals() {
  return (
    <section id="portals" className="bg-navy py-32">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-16 max-w-xl">
          <p className="mb-4 text-xs uppercase tracking-[0.3em] text-brass-light">
            One system, four vantage points
          </p>
          <h2 className="text-balance font-display text-4xl text-paper md:text-5xl">
            Everyone sees exactly what they need.
          </h2>
        </div>

        <div className="grid grid-cols-1 gap-px overflow-hidden rounded-2xl bg-paper/10 sm:grid-cols-2 lg:grid-cols-4">
          {portals.map((p, i) => (
            <motion.div
              key={p.role}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-10% 0px" }}
              transition={{ duration: 0.5, delay: i * 0.06 }}
            >
              <Link
                href={p.href}
                data-cursor-hover
                className="group flex h-full flex-col justify-between bg-navy p-8 transition-colors hover:bg-navy-deep"
              >
                <div>
                  <div className="mb-6 flex h-11 w-11 items-center justify-center rounded-full bg-paper/10 transition-transform duration-300 group-hover:-translate-y-1 group-hover:rotate-6">
                    <Image
                      src={p.icon}
                      alt=""
                      width={20}
                      height={20}
                      className="opacity-80 invert"
                    />
                  </div>
                  <h3 className="font-display text-xl text-paper">
                    {p.role}
                  </h3>
                  <p className="mt-2 text-sm text-paper/60">{p.body}</p>
                </div>
                <span className="mt-8 inline-flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-brass-light">
                  Enter
                  <span className="transition-transform duration-300 group-hover:translate-x-1">
                    →
                  </span>
                </span>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
