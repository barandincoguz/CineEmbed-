"use client";

import dynamic from "next/dynamic";
import { FilmPoster } from "./film-poster";
import type { BackboneId, Film } from "@/lib/api";

const CosineHeatmap = dynamic(
  () => import("./cosine-heatmap").then((m) => m.CosineHeatmap),
  { ssr: false, loading: () => <div className="mt-6 h-44 bg-gray-50 rounded animate-pulse" /> }
);

interface Props {
  film: Film | null;
  loading: boolean;
  backbone: BackboneId;
}

export function SelectedFilmPanel({ film, loading, backbone }: Props) {
  if (loading || !film) {
    return (
      <div className="border border-border rounded-lg p-6 bg-card animate-pulse">
        <div className="h-64 bg-gray-100 rounded mb-4" />
        <div className="h-6 bg-gray-100 rounded w-2/3 mb-2" />
        <div className="h-4 bg-gray-100 rounded w-1/2" />
      </div>
    );
  }

  // STYLISTIC_DICT fallback: when style empty but plot has entries, render
  // a single "Keywords" list (no fake split) per spec §5.5.
  const showSplit = film.style.length > 0;
  const flatKeywords = !showSplit ? film.plot : [];

  return (
    <article className="border border-border rounded-lg p-6 bg-card">
      <div className="flex gap-6 mb-4">
        <FilmPoster film={film} size="md" />
        <div className="flex-1">
          <h2 className="text-2xl font-semibold">{film.title}</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {film.year ?? "—"} · {film.director}
            {film.duration ? ` · ${Math.round(film.duration)} min` : ""}
            {film.country ? ` · ${film.country}` : ""}
          </p>
          {film.tagline && (
            <p className="italic text-sm text-gray-600 mt-2">&ldquo;{film.tagline}&rdquo;</p>
          )}
          <div className="mt-3 flex flex-wrap gap-1">
            {film.genres.slice(0, 5).map((g) => (
              <span key={g} className="px-2 py-0.5 text-xs bg-purple-50 text-purple-800 rounded">{g}</span>
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            ★ {film.rating.toFixed(1)} ({film.votes.toLocaleString()} votes) ·
            Cluster #{film.cluster} · {film.time} · backbone {backbone}
          </p>
        </div>
      </div>
      {film.overview && (
        <p className="text-sm text-gray-700 leading-relaxed">{film.overview}</p>
      )}
      {showSplit && (
        <>
          {film.style.length > 0 && (
            <ChipList title="Style" chips={film.style} variant="indigo" />
          )}
          {film.plot.length > 0 && (
            <ChipList title="Plot" chips={film.plot} variant="rose" />
          )}
        </>
      )}
      {!showSplit && flatKeywords.length > 0 && (
        <ChipList title="Keywords" chips={flatKeywords} variant="slate" />
      )}
      <CosineHeatmap filmId={film.id} backbone={backbone} />
    </article>
  );
}

function ChipList({ title, chips, variant }: { title: string; chips: string[]; variant: "indigo" | "rose" | "slate" }) {
  const colors = {
    indigo: "bg-indigo-50 text-indigo-700",
    rose: "bg-rose-50 text-rose-700",
    slate: "bg-slate-100 text-slate-700",
  };
  return (
    <div className="mt-4">
      <p className="text-xs font-medium text-muted-foreground mb-1">{title}</p>
      <div className="flex flex-wrap gap-1">
        {chips.map((c) => (
          <span key={c} className={`px-2 py-0.5 text-xs rounded ${colors[variant]}`}>{c}</span>
        ))}
      </div>
    </div>
  );
}
