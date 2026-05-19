"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Sidebar } from "@/components/sidebar";
import { SearchBar } from "@/components/search-bar";
import { SelectedFilmPanel } from "@/components/selected-film-panel";
import { SimilarFilmsPanel } from "@/components/similar-films-panel";
import { EmptyState } from "@/components/empty-state";
import { BackboneSwitcher } from "@/components/backbone-switcher";
import { Footer } from "@/components/footer";
import { api, type BackboneId } from "@/lib/api";

export default function HomePage() {
  const params = useSearchParams();
  const router = useRouter();
  const filmIdParam = params.get("film");
  const filmId = filmIdParam && /^\d+$/.test(filmIdParam) ? Number(filmIdParam) : null;
  const backbone = ((params.get("backbone") ?? "ae_z32") as BackboneId);

  const { data: film, isLoading: filmLoading } = useQuery({
    queryKey: ["film", filmId, backbone],
    queryFn: ({ signal }) => api.getFilm(filmId!, backbone, { signal }),
    enabled: filmId !== null,
  });

  const setFilm = (id: number | null) => {
    const next = new URLSearchParams(params.toString());
    if (id === null) next.delete("film");
    else next.set("film", String(id));
    router.replace(`?${next.toString()}`, { scroll: false });
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <main className="flex-1 flex flex-col min-h-screen" style={{ marginLeft: 220 }}>
        <div className="flex flex-col flex-1 px-6 pt-6 pb-6 gap-5 max-w-[1200px] w-full mx-auto">
          {/* Backbone switcher */}
          <div className="flex justify-end">
            <BackboneSwitcher />
          </div>

          {/* Search bar */}
          <SearchBar backbone={backbone} onSelectFilm={(id) => setFilm(id)} />

          {/* Content area */}
          {filmId === null ? (
            <EmptyState onPickExample={(id) => setFilm(id)} />
          ) : (
            <div className="flex gap-5 flex-1 items-start">
              {/* Selected Film panel — ~58% */}
              <div className="flex-[58] min-w-0">
                <SelectedFilmPanel
                  film={film ?? null}
                  loading={filmLoading}
                  backbone={backbone}
                />
              </div>

              {/* Similar Films panel — ~42% */}
              <div className="flex-[42] min-w-0 self-stretch">
                <SimilarFilmsPanel
                  filmId={filmId}
                  backbone={backbone}
                  onSelectFilm={(id) => setFilm(id)}
                />
              </div>
            </div>
          )}
        </div>

        <Footer />
      </main>
    </div>
  );
}
