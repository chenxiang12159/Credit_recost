"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "首页" },
  { href: "/xhs", label: "小红书" },
  { href: "/submit", label: "提交" },
  { href: "/about", label: "关于" },
];

export default function Header() {
  const pathname = usePathname();

  return (
    <header className="bg-primary-700 text-white shadow-lg">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 text-xl font-bold">
          <span className="text-2xl">🏦</span>
          <span>银行活动聚合平台</span>
        </Link>
        <nav className="flex gap-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === item.href
                  ? "bg-primary-800 text-white"
                  : "text-primary-100 hover:bg-primary-600 hover:text-white"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
