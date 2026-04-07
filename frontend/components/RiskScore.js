"use client";

import styles from "./RiskScore.module.css";

const RISK_COLORS = {
  Low: "#22c55e",
  Moderate: "#eab308",
  High: "#f97316",
  Critical: "#ef4444",
};

export default function RiskScore({ score, level }) {
  const color = RISK_COLORS[level] || RISK_COLORS.Low;

  return (
    <div className={styles.container} id="risk-score-display">
      <div className={styles.header}>
        <h3 className={styles.title}>Risk Assessment</h3>
        <span
          className={styles.badge}
          style={{
            background: `${color}15`,
            color: color,
            borderColor: `${color}40`,
          }}
          id="risk-level-badge"
        >
          {level}
        </span>
      </div>

      <div className={styles.scoreRow}>
        <span className={styles.scoreValue} style={{ color }}>
          {Math.round(score)}
        </span>
        <span className={styles.scoreMax}>/100</span>
      </div>

      <div className={styles.barTrack}>
        <div
          className={styles.barFill}
          style={{
            width: `${score}%`,
            background: `linear-gradient(90deg, ${color}99, ${color})`,
            boxShadow: `0 0 12px ${color}60`,
          }}
        />
        {/* Threshold markers */}
        <div className={styles.marker} style={{ left: "25%" }} title="Moderate" />
        <div className={styles.marker} style={{ left: "50%" }} title="High" />
        <div className={styles.marker} style={{ left: "75%" }} title="Critical" />
      </div>

      <div className={styles.labels}>
        <span>Safe</span>
        <span>Moderate</span>
        <span>High</span>
        <span>Critical</span>
      </div>
    </div>
  );
}
