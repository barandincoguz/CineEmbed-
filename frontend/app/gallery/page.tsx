import { Sidebar } from "@/components/sidebar";
import { GallerySchema } from "@/lib/api-types";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

async function fetchGallery() {
  const res = await fetch(`${BASE}/api/gallery`, { next: { revalidate: 3600 } });
  const json = await res.json();
  return GallerySchema.parse(json);
}

export default async function GalleryPage() {
  const gallery = await fetchGallery();
  const backbones = ["ae_z32", "ae_z64", "ae_z128"] as const;

  return (
    <div className="flex min-h-screen bg-[#f8f9fb]">
      <Sidebar />
      <main className="flex-1 ml-[220px] p-8">
        <h1 className="text-2xl font-semibold mb-2">Eyeball gallery</h1>
        <p className="text-sm text-gray-600 mb-6">
          Five well-known queries × three backbones. The same query produces
          visibly different top-5 neighbours per backbone — the strongest
          demonstration of the project&rsquo;s z-sweep finding (see{" "}
          <a className="text-purple-700 underline" href="/about">About</a>).
        </p>
        <div className="space-y-8">
          {gallery.queries.map((q) => (
            <section key={q}>
              <h2 className="text-lg font-medium mb-3">{q}</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {backbones.map((bb) => {
                  const cell = gallery.matrix[q][bb];
                  return (
                    <div key={bb} className="border border-[#e5e4ec] rounded-lg p-3 bg-white">
                      <p className="text-xs font-medium text-purple-700 mb-2">{bb}</p>
                      <p className="text-sm font-medium mb-2">{cell.query.title} ({cell.query.year ?? "—"})</p>
                      <ol className="text-xs space-y-1">
                        {cell.neighbors.map((n, i) => (
                          <li key={n.id} className="flex justify-between">
                            <span>#{i + 1} {n.title}</span>
                            <span className="text-gray-500">{n.cosine.toFixed(3)}</span>
                          </li>
                        ))}
                      </ol>
                    </div>
                  );
                })}
              </div>
            </section>
          ))}
        </div>
      </main>
    </div>
  );
}
