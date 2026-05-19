"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Sparkles } from "lucide-react";
import { Sidebar } from "@/components/sidebar";
import { SearchBar } from "@/components/search-bar";
import { SelectedFilmPanel } from "@/components/selected-film-panel";
import { SimilarFilmsPanel } from "@/components/similar-films-panel";
import { EmptyState } from "@/components/empty-state";
import { BackboneSwitcher } from "@/components/backbone-switcher";
import { Footer } from "@/components/footer";
import { ErrorFallback } from "@/components/error-fallback";
import { api, type BackboneId } from "@/lib/api";

export default function HomePage() {
  const params = useSearchParams();
  const router = useRouter();
  const filmIdParam = params.get("film");
  const filmId = filmIdParam && /^\d+$/.test(filmIdParam) ? Number(filmIdParam) : null;
  const backbone = ((params.get("backbone") ?? "ae_z32") as BackboneId);

  const {
    data: film,
    isLoading: filmLoading,
    isError: filmIsError,
    error: filmError,
    refetch: refetchFilm,
  } = useQuery({
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

          <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-muted-foreground py-2 border-b border-border tabular-nums">
            <span>329,044 films</span><span aria-hidden="true">·</span>
            <span>3 backbones</span><span aria-hidden="true">·</span>
            <span>32-dim latent</span><span aria-hidden="true">·</span>
            <span>cosine over L2-normalized</span>
          </div>

          {/* Content area */}
          {filmId === null ? (
            <>
              <section className="bg-card border border-border rounded-lg p-5">
                <div className="flex items-start gap-3">
                  <Sparkles className="w-5 h-5 text-primary mt-0.5 shrink-0" aria-hidden="true" />
                  <div className="flex-1">
                    <h2 className="text-base font-semibold text-foreground mb-1.5">How retrieval works</h2>
                    <p className="text-sm text-muted-foreground leading-relaxed mb-3">
                      Every film is encoded as a 32-dim multimodal embedding learned jointly over seven feature
                      blocks (numerical metadata, genre, language, decade, prior-awards, text overview, director
                      profile). Pick any film and we return its top-10 nearest neighbors by{" "}
                      <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">cosine similarity</code>{" "}
                      over the full 329,044-film index. The same query against the three backbones (z=32, z=64, z=128)
                      produces visibly different rankings — see the U-curve finding on{" "}
                      <a className="text-primary underline underline-offset-2 hover:text-primary/80" href="/about">About</a>.
                    </p>
                    <div className="flex flex-wrap gap-1.5 text-[10px] text-muted-foreground tabular-nums">
                      <span className="px-2 py-0.5 rounded bg-muted">7 feature blocks</span>
                      <span className="px-2 py-0.5 rounded bg-muted">cosine top-10</span>
                      <span className="px-2 py-0.5 rounded bg-muted">329,044-film index</span>
                      <span className="px-2 py-0.5 rounded bg-muted">live distribution heatmap</span>
                    </div>
                  </div>
                </div>
              </section>
              <EmptyState onPickExample={(id) => setFilm(id)} />
            </>
          ) : (
            <div className="flex gap-5 flex-1 items-start">
              {/* Selected Film panel — ~58% */}
              <div className="flex-[58] min-w-0">
                {filmIsError ? (
                  <ErrorFallback
                    title="Couldn't load film details"
                    error={filmError}
                    onRetry={() => refetchFilm()}
                  />
                ) : (
                  <SelectedFilmPanel
                    film={film ?? null}
                    loading={filmLoading}
                    backbone={backbone}
                  />
                )}
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
