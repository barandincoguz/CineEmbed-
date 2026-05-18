"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Film, Layers, GalleryHorizontal, Info } from "lucide-react";

const NAV = [
  { href: "/", label: "Home", icon: Film },
  { href: "/cluster", label: "Clusters", icon: Layers },
  { href: "/gallery", label: "Gallery", icon: GalleryHorizontal },
  { href: "/about", label: "About", icon: Info },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <nav
      aria-label="Primary navigation"
      className="fixed left-0 top-0 bottom-0 w-[220px] bg-white border-r border-[#e5e4ec] p-4"
    >
      <h1 className="font-semibold mb-6 text-purple-700">CineEmbed</h1>
      <ul className="space-y-1">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== "/" && pathname.startsWith(href));
          return (
            <li key={href}>
              <Link
                href={href}
                className={`flex items-center gap-2 px-2 py-1.5 rounded text-sm ${
                  active ? "bg-purple-50 text-purple-800" : "text-gray-700 hover:bg-gray-50"
                }`}
              >
                <Icon className="w-4 h-4" aria-hidden="true" />
                {label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
