"use client";

import { useQuery } from "@tanstack/react-query";
import { useSearchParams, useRouter } from "next/navigation";
import { use } from "react";
import { Sidebar } from "@/components/sidebar";
import { BackboneSwitcher } from "@/components/backbone-switcher";
import { FilmPoster } from "@/components/film-poster";
import { Footer } from "@/components/footer";
import { api, type BackboneId } from "@/lib/api";

export default function ClusterDetailPage({ params: pa }: { params: Promise<{ k: string }> }) {
  const { k } = use(pa);
  const kInt = Number(k);
  const params = useSearchParams();
  const router = useRouter();
  const backbone = ((params.get("backbone") ?? "ae_z32") as BackboneId);

  const { data, isLoading } = useQuery({
    queryKey: ["cluster", kInt, backbone],
    queryFn: ({ signal }) => api.getCluster(kInt, backbone, 50, { signal }),
    enabled: !isNaN(kInt) && kInt >= 0 && kInt <= 20,
  });

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-[220px] p-8">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-semibold tracking-tight mb-6">{data?.name ?? `Cluster #${k}`}</h1>
          <BackboneSwitcher />
        </div>
        {data && (
          <p className="text-sm text-muted-foreground mb-6">
            {data.size.toLocaleString()} films · top genres:&nbsp;
            {data.topGenres.map((g) => `${g.genre} ${(g.pct * 100).toFixed(0)}%`).join(", ")}
            &nbsp;· decade {data.modalDecade}&nbsp;· showing {data.films.length} of {data.total}
          </p>
        )}
        {isLoading && <p className="text-muted-foreground">Loading…</p>}
        {data && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {data.films.map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => router.push(`/?film=${f.id}&backbone=${backbone}`)}
                className="text-left"
              >
                <FilmPoster film={f} size="sm" />
                <p className="text-xs mt-1 truncate">{f.title}</p>
                <p className="text-[10px] text-muted-foreground">{f.year ?? "—"}</p>
              </button>
            ))}
          </div>
        )}
        <Footer />
      </main>
    </div>
  );
}
