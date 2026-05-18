"use client";

import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { Sidebar } from "@/components/sidebar";
import { BackboneSwitcher } from "@/components/backbone-switcher";
import { ClusterCard } from "@/components/cluster-card";
import { api, type BackboneId } from "@/lib/api";

export default function ClustersPage() {
  const params = useSearchParams();
  const backbone = ((params.get("backbone") ?? "ae_z32") as BackboneId);
  const { data: clusters = [], isLoading } = useQuery({
    queryKey: ["clusters", backbone],
    queryFn: ({ signal }) => api.getClusters(backbone, { signal }),
  });

  return (
    <div className="flex min-h-screen bg-[#f8f9fb]">
      <Sidebar />
      <main className="flex-1 ml-[220px] p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold">Clusters (k=21)</h1>
          <BackboneSwitcher />
        </div>
        {isLoading ? (
          <p className="text-gray-500">Loading clusters…</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {clusters.map((c) => (
              <ClusterCard key={c.id} cluster={c} backbone={backbone} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
