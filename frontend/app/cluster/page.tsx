"use client";

import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { Sidebar } from "@/components/sidebar";
import { BackboneSwitcher } from "@/components/backbone-switcher";
import { ClusterCard } from "@/components/cluster-card";
import { Footer } from "@/components/footer";
import { ErrorFallback } from "@/components/error-fallback";
import { api, type BackboneId } from "@/lib/api";

export default function ClustersPage() {
  const params = useSearchParams();
  const backbone = ((params.get("backbone") ?? "ae_z32") as BackboneId);
  const { data: clusters = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ["clusters", backbone],
    queryFn: ({ signal }) => api.getClusters(backbone, { signal }),
  });

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-[220px] p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold tracking-tight mb-6">Clusters (k=21)</h1>
          <BackboneSwitcher />
        </div>
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="border border-border rounded-lg p-4 bg-card animate-pulse h-48" />
            ))}
          </div>
        ) : isError ? (
          <ErrorFallback title="Couldn't load clusters" error={error} onRetry={() => refetch()} />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {clusters.map((c) => (
              <ClusterCard key={c.id} cluster={c} backbone={backbone} />
            ))}
          </div>
        )}
        <Footer />
      </main>
    </div>
  );
}
