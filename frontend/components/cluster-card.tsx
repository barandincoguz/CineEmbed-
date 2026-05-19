"use client";

import Link from "next/link";
import { FilmPoster } from "./film-poster";
import type { Cluster } from "@/lib/api";

export function ClusterCard({ cluster, backbone }: { cluster: Cluster; backbone: string }) {
  return (
    <Link
      href={`/cluster/${cluster.id}?backbone=${backbone}`}
      className="block border border-border rounded-lg p-4 bg-card hover:border-purple-300 transition"
    >
      <h3 className="font-medium text-sm">{cluster.name}</h3>
      <p className="text-xs text-muted-foreground mt-1">{cluster.size.toLocaleString()} films</p>
      <div className="flex flex-wrap gap-1 mt-2">
        {cluster.topGenres.slice(0, 3).map((g) => (
          <span key={g.genre} className="text-[10px] px-1.5 py-0.5 bg-purple-50 text-purple-700 rounded">
            {g.genre} {(g.pct * 100).toFixed(0)}%
          </span>
        ))}
      </div>
      <div className="flex gap-1 mt-3">
        {cluster.previewFilms.slice(0, 4).map((f) => (
          <FilmPoster key={f.id} film={f} size="sm" />
        ))}
      </div>
    </Link>
  );
}
