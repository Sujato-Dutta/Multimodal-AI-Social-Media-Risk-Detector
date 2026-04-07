"use client";

import styles from "./ExplanationPanel.module.css";

export default function ExplanationPanel({ explanation, processingTime }) {
  if (!explanation) return null;

  return (
    <div className={styles.container} id="explanation-panel">
      {/* Summary */}
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>
          <span className={styles.sectionIcon}>🔍</span>
          Analysis Summary
        </h3>
        <p className={styles.summary}>{explanation.summary}</p>
      </div>

      {/* Top Risk Prompts */}
      {explanation.top_risk_prompts?.length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>
            <span className={styles.sectionIcon}>🎯</span>
            Matched Risk Signals
          </h3>
          <div className={styles.promptList}>
            {explanation.top_risk_prompts.map((match, i) => (
              <div key={i} className={styles.promptItem}>
                <div className={styles.promptHeader}>
                  <span className={styles.promptCategory}>{match.category}</span>
                  <span className={styles.promptSim}>
                    {(match.similarity * 100).toFixed(1)}%
                  </span>
                </div>
                <p className={styles.promptText}>{match.prompt}</p>
                <div className={styles.simBar}>
                  <div
                    className={styles.simFill}
                    style={{ width: `${match.similarity * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Caption Flags */}
      {explanation.caption_flags?.length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>
            <span className={styles.sectionIcon}>🚩</span>
            Flagged Keywords
          </h3>
          <div className={styles.flagsContainer}>
            {explanation.caption_flags.map((flag, i) => (
              <span key={i} className={styles.flag}>
                {flag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Image-Text Alignment */}
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>
          <span className={styles.sectionIcon}>🔗</span>
          Image–Caption Alignment
        </h3>
        <div className={styles.alignmentRow}>
          <div className={styles.alignmentBar}>
            <div
              className={styles.alignmentFill}
              style={{
                width: `${Math.max(0, explanation.image_text_alignment * 100)}%`,
              }}
            />
          </div>
          <span className={styles.alignmentValue}>
            {(explanation.image_text_alignment * 100).toFixed(1)}%
          </span>
        </div>
        <p className={styles.alignmentHint}>
          {explanation.image_text_alignment >= 0.25
            ? "Image and caption are well-aligned."
            : explanation.image_text_alignment >= 0.15
            ? "Moderate alignment — the caption partially describes the image."
            : "Low alignment — the caption may not accurately describe the image."}
        </p>
      </div>

      {/* Processing Time */}
      <div className={styles.footer}>
        <span className={styles.footerText}>
          Processed in {processingTime.toFixed(0)}ms
        </span>
      </div>
    </div>
  );
}
