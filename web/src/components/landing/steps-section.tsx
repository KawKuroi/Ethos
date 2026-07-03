import { Fragment } from "react";

import { STEPS } from "./data";
import styles from "./landing.module.css";

export function StepsSection() {
  return (
    <section className={`eth-reveal ${styles.stepsSection}`}>
      <div className={styles.stepsHead}>
        <h2 className={styles.h2} style={{ margin: 0 }}>
          Cómo se usa
        </h2>
        <span className={styles.stepsNote}>
          Tres pasos · abajo lo ves en detalle
        </span>
      </div>
      <div className={styles.stepsRow}>
        {STEPS.map((step) => (
          <Fragment key={step.n}>
            <div className={styles.stepCard}>
              <div className={styles.stepHead}>
                <span className={styles.stepNum}>{step.n}</span>
                <div className={styles.stepTitle}>{step.title}</div>
              </div>
              <p className={styles.stepBody}>{step.body}</p>
            </div>
            {step.arrow && <span className={styles.stepArrow}>{step.arrow}</span>}
          </Fragment>
        ))}
      </div>
    </section>
  );
}
