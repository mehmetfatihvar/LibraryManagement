"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "/books/new", label: "Add Book" },
  { href: "/members", label: "Members" },
  { href: "/borrowings", label: "Circulation" },
  { href: "/enrich", label: "Enrich ISBN" },
  { href: "/reports", label: "Reports" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-500/20 text-lg font-bold text-sky-400">
            X
          </div>
          <div>
            <p className="text-sm font-semibold text-white">XML Library</p>
            <p className="text-xs text-slate-400">Management System</p>
          </div>
        </Link>
        <nav className="flex items-center gap-1">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  active
                    ? "bg-sky-500/20 text-sky-300"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
