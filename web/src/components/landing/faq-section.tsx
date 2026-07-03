import { FAQS } from "./data";
import styles from "./landing.module.css";

export function FaqSection() {
  return (
    <section className={`eth-reveal ${styles.faqSection}`}>
      <h2 className={styles.faqTitle}>Preguntas frecuentes</h2>
      <div className={styles.faqGrid}>
        {FAQS.map((faq) => (
          <div key={faq.q} className={styles.faqItem}>
            <div className={styles.faqQ}>{faq.q}</div>
            <p className={styles.faqA}>{faq.a}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
