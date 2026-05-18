"use client";

import { useQuery } from "@tanstack/react-query";
import { api, type BackboneId, type Neighbor } from "@/lib/api";

interface Props {
  filmId: number;
  backbone: BackboneId;
  onSelectFilm: (id: number) => void;
}

function cosineColor(c: number): string {
  if (c >= 0.95) return "bg-green-100 text-green-800";
  if (c >= 0.8) return "bg-blue-100 text-blue-800";
  return "bg-slate-100 text-slate-700";
}

export function SimilarFilmsPanel({ filmId, backbone, onSelectFilm }: Props) {
  const { data: neighbors = [], isLoading } = useQuery({
    queryKey: ["similar", filmId, backbone],
    queryFn: ({ signal }) => api.getSimilar(filmId, backbone, 10, { signal }),
  });

  if (isLoading) {
    return (
      <div className="border border-[#e5e4ec] rounded-lg p-4 bg-white animate-pulse">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-10 bg-gray-100 rounded mb-2" />
        ))}
      </div>
    );
  }

  if (neighbors.length === 0) {
    return <div className="border border-[#e5e4ec] rounded-lg p-4 bg-white text-sm text-gray-500">No similar films found.</div>;
  }

  return (
    <aside className="border border-[#e5e4ec] rounded-lg p-4 bg-white">
      <h3 className="text-sm font-medium text-gray-700 mb-3">Similar films (backbone {backbone})</h3>
      <ol className="space-y-2">
        {neighbors.map((n: Neighbor, i: number) => (
          <li key={n.id}>
            <button
              type="button"
              onClick={() => onSelectFilm(n.id)}
              className="w-full flex items-start gap-3 px-2 py-2 rounded hover:bg-purple-50 text-left"
            >
              <span className="text-xs text-gray-400 w-6">#{i + 1}</span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{n.title}</div>
                <div className="text-xs text-gray-500 truncate">
                  {n.year ?? "—"} · {n.director}
                </div>
                <div className="flex flex-wrap gap-1 mt-1">
                  {n.genres.slice(0, 2).map((g) => (
                    <span key={g} className="text-[10px] px-1.5 py-0.5 bg-gray-100 rounded">{g}</span>
                  ))}
                </div>
              </div>
              <span
                className={`text-xs px-1.5 py-0.5 rounded ${cosineColor(n.cosine)}`}
                aria-label={`cosine ${n.cosine.toFixed(3)}`}
              >
                {n.cosine.toFixed(2)}
              </span>
            </button>
          </li>
        ))}
      </ol>
    </aside>
  );
}
