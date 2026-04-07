"use client";

import styles from "./LoadingSpinner.module.css";

export default function LoadingSpinner({ message = "Analyzing content..." }) {
  return (
    <div className={styles.overlay} id="loading-spinner">
      <div className={styles.card}>
        <div className={styles.spinnerWrapper}>
          <div className={styles.ring}></div>
          <div className={styles.ring}></div>
          <div className={styles.core}></div>
        </div>
        <p className={styles.message}>{message}</p>
        <div className={styles.steps}>
          <span className={styles.step}>Encoding image</span>
          <span className={styles.stepDot}>→</span>
          <span className={styles.step}>Processing text</span>
          <span className={styles.stepDot}>→</span>
          <span className={styles.step}>Computing risk</span>
        </div>
      </div>
    </div>
  );
}
