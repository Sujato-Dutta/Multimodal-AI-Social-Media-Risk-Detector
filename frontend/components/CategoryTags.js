"use client";

import styles from "./CategoryTags.module.css";

const CATEGORY_ICONS = {
  "Offensive Content": "⚠",
  "Brand Risk": "🏢",
  "Misinformation": "📰",
};

const RISK_COLORS = {
  low: "#22c55e",
  moderate: "#eab308",
  high: "#f97316",
  critical: "#ef4444",
};

function getLevel(score) {
  if (score >= 75) return "critical";
  if (score >= 50) return "high";
  if (score >= 25) return "moderate";
  return "low";
}

export default function CategoryTags({ categories }) {
  if (!categories || categories.length === 0) return null;

  const sorted = [...categories].sort((a, b) => b.score - a.score);

  return (
    <div className={styles.container} id="category-tags">
      <h3 className={styles.title}>Risk Categories</h3>
      <div className={styles.grid}>
        {sorted.map((cat) => {
          const level = getLevel(cat.score);
          const color = RISK_COLORS[level];
          const icon = CATEGORY_ICONS[cat.name] || "📋";

          return (
            <div
              key={cat.name}
              className={styles.card}
              style={{ borderColor: `${color}30` }}
            >
              <div className={styles.cardHeader}>
                <span className={styles.icon}>{icon}</span>
                <span className={styles.catName}>{cat.name}</span>
              </div>

              <div className={styles.scoreSection}>
                <span className={styles.catScore} style={{ color }}>
                  {Math.round(cat.score)}
                </span>
                <span className={styles.catMax}>/100</span>
              </div>

              <div className={styles.miniBar}>
                <div
                  className={styles.miniFill}
                  style={{
                    width: `${cat.score}%`,
                    background: color,
                    boxShadow: `0 0 8px ${color}50`,
                  }}
                />
              </div>

              <div className={styles.confidence}>
                Confidence: {(cat.confidence * 100).toFixed(0)}%
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
