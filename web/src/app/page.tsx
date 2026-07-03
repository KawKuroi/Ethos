import { CATS } from "@/components/landing/data";
import { FaqSection } from "@/components/landing/faq-section";
import { LandingFooter } from "@/components/landing/footer";
import { Gallery } from "@/components/landing/gallery";
import { LandingHeader } from "@/components/landing/header";
import { Hero } from "@/components/landing/hero";
import styles from "@/components/landing/landing.module.css";
import { McpSection } from "@/components/landing/mcp-section";
import { StepsSection } from "@/components/landing/steps-section";
import { Suggestions } from "@/components/landing/suggestions";
import { Walkthrough } from "@/components/landing/walkthrough";

// Landing pública, traducida del prototipo (docs/design.md §4).
export default function Home() {
  return (
    <div className={styles.container}>
      <LandingHeader />
      <main>
        <Hero />
        <McpSection />
        <StepsSection />

        {/* Categorías: walkthrough de Juegos + galería del catálogo */}
        <section id="categorias" className={`eth-reveal ${styles.catSection}`}>
          <div className={styles.walkHead}>
            <div className={styles.walkIntro}>
              <h2 className={styles.h2} style={{ marginBottom: 8 }}>
                Una categoría, de tu app hasta tu IA
              </h2>
              <p className={styles.walkIntroText}>
                Seguimos{" "}
                <strong className={styles.walkIntroStrong}>Juegos</strong> de
                principio a fin: qué entra, cómo Ethos lo ordena, cómo queda en
                tu perfil y cómo lo usa tu IA. Las otras{" "}
                {CATS.length - 1} categorías hacen lo mismo.
              </p>
            </div>
            <div className={styles.exampleChip}>
              <span className={styles.exampleInitial}>J</span>
              <div>
                <div className={styles.exampleLabel}>Ejemplo</div>
                <div className={styles.exampleName}>Juegos</div>
              </div>
            </div>
          </div>
          <Walkthrough />
          <Gallery />
        </section>

        <FaqSection />
        <Suggestions />
      </main>
      <LandingFooter />
    </div>
  );
}
