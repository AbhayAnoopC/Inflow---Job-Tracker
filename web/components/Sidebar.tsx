"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Overview" },
  { href: "/postings", label: "Postings" },
  { href: "/skills", label: "Skills" },
  { href: "/companies", label: "Companies" },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="fixed inset-y-0 left-0 flex w-[220px] flex-col bg-sidebar">
      <div className="flex items-center gap-2 px-5 pb-6 pt-7">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M20 4C10 4 4 9.5 4 16c0 1.4.3 2.7.8 3.8C6.3 14.5 10 11 15 9c-3.4 2.4-6 5.6-7.3 10.6 1 .3 2 .4 3.3.4 6.6 0 9-6 9-16Z"
            fill="#4a9b6f"
          />
        </svg>
        <span className="text-[16px] font-semibold text-white">BC Co-op Tracker</span>
      </div>
      <nav className="flex flex-col gap-0.5 px-2">
        {NAV.map(({ href, label }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              aria-current={active ? "page" : undefined}
              className={`rounded-md border-l-[3px] px-[17px] py-2.5 text-[14px] transition-colors ${
                active
                  ? "border-sidebar-accent bg-white/10 text-sidebar-active"
                  : "border-transparent text-sidebar-text hover:bg-white/5 hover:text-sidebar-active"
              }`}
            >
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
