import { Sidebar } from "@/components/sidebar";

export default function AboutPage() {
  return (
    <div className="flex min-h-screen bg-[#f8f9fb]">
      <Sidebar />
      <main className="flex-1 ml-[220px] p-8 max-w-3xl">
        <h1 className="text-2xl font-semibold mb-4">About CineEmbed</h1>

        <section className="prose prose-sm">
          <p>
            CineEmbed is a multimodal movie recommender built for SENG 474
            (Deep Learning, TED University, Spring 2026) by Baran Dinçoğuz,
            Arda Arvas, and Kaan Kaya. The model encodes each of 329,044
            films into a 32-dimensional latent space using a multi-modal
            autoencoder over seven feature blocks (numerical metadata,
            genre one-hot, language one-hot, decade scalar, prior-awards,
            text overview embedding, and director profile).
          </p>

          <h2>Two methodological findings</h2>

          <h3>NMI ≠ retrieval quality</h3>
          <p>
            The MVP champion model, <code>dec_z64_k21</code>, won on the
            NMI clustering metric (geo_NMI = 0.323) but collapsed under
            cosine retrieval: every pair of films inside a cluster sat at
            cosine ≈ 1.000 (angular collapse), so top-5 retrieval degenerated
            into a random tie-break. We adopted <code>genre@5</code> — the
            mean fraction of top-5 nearest neighbours sharing a film&rsquo;s
            primary genre — as the demo-relevant metric, and switched the
            demo backbone to <code>ae_z64</code>. See journal/07.
          </p>

          <h3>Information-bottleneck sweet spot at z=32</h3>
          <p>
            Round 2 swept latent dimension across z &isin; &#123;32, 64, 128&#125;
            with the recipe held constant. Counter-intuitively the smallest
            variant won on both <code>genre@5</code> (0.723 vs 0.715 vs
            0.722) and <code>gNMI</code> (0.334 vs 0.328 vs 0.273) — a
            U-curve. The over-parameterised z=128 variant produced
            near-dead latent dimensions and a narrowing pair-cosine
            distribution. We interpret z=32 as the information-bottleneck
            sweet spot for this task. See journal/12.
          </p>

          <h2>How to read the gallery</h2>
          <p>
            The <a href="/gallery">Gallery</a> page renders five well-known
            queries (Inception, Spirited Away, Shawshank, Pulp Fiction, Toy
            Story) against the three backbones side-by-side. The same
            query produces visibly different top-5 neighbours per backbone
            — the strongest demonstration of the project&rsquo;s findings.
          </p>

          <p className="text-xs text-gray-500 mt-8">
            Source repo: github.com/barandincoguz/CineEmbed- · branch
            feature/wandb-integration · spec
            docs/superpowers/specs/2026-05-18-frontend-backend-integration-design.md
          </p>
        </section>
      </main>
    </div>
  );
}
