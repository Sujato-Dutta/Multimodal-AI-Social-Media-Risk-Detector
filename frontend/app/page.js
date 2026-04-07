"use client";

import { useState, useCallback } from "react";
import styles from "./page.module.css";
import ImageUploader from "../components/ImageUploader";
import RiskScore from "../components/RiskScore";
import CategoryTags from "../components/CategoryTags";
import ExplanationPanel from "../components/ExplanationPanel";
import LoadingSpinner from "../components/LoadingSpinner";
import { analyzeContent } from "../utils/api";

export default function Home() {
  const [imageFile, setImageFile] = useState(null);
  const [caption, setCaption] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const canAnalyze = imageFile && !loading;

  const handleAnalyze = useCallback(async () => {
    if (!imageFile) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeContent(imageFile, caption);
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [imageFile, caption]);

  const handleReset = () => {
    setImageFile(null);
    setCaption("");
    setResult(null);
    setError(null);
  };

  return (
    <main className={styles.main}>
      {loading && <LoadingSpinner />}

      {/* Header */}
      <header className={styles.header}>
        <div className={styles.badgeContainer}>
          <div className={styles.badgeGlow}></div>
          <div className={styles.badge}>
            <span className={styles.badgeDot}></span>
            AI Moderation Engine
          </div>
        </div>

        <div className={styles.titleWrapper}>
          <div className={styles.logoMark}>
            <svg className={styles.logoIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          </div>
          <h1 className={styles.title}>
            Multimodal AI <span className={styles.riskAccent}>Risk</span> Detector
          </h1>
        </div>

        <p className={styles.subtitle}>
          Content Analysis for Social Media.
        </p>
      </header>

      <div className={styles.layout}>
        {/* Input panel */}
        <section className={styles.inputPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle}>Input</h2>
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label} htmlFor="image-uploader">
              Image
            </label>
            <ImageUploader
              onFileSelect={setImageFile}
              disabled={loading}
            />
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label} htmlFor="caption-input">
              Caption
            </label>
            <textarea
              id="caption-input"
              className={styles.textarea}
              placeholder="Enter the post caption or accompanying text..."
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              disabled={loading}
              rows={4}
              maxLength={1000}
            />
            <span className={styles.charCount}>
              {caption.length}/1000
            </span>
          </div>

          {error && (
            <div className={styles.error} id="error-message">
              <span className={styles.errorIcon}>✕</span>
              {error}
            </div>
          )}

          <div className={styles.actions}>
            <button
              className={styles.analyzeBtn}
              onClick={handleAnalyze}
              disabled={!canAnalyze}
              id="analyze-btn"
            >
              {loading ? (
                "Analyzing..."
              ) : (
                <>
                  <span className={styles.btnIcon}>⚡</span>
                  Analyze Content
                </>
              )}
            </button>

            {result && (
              <button
                className={styles.resetBtn}
                onClick={handleReset}
                id="reset-btn"
              >
                Reset
              </button>
            )}
          </div>
        </section>

        {/* Results panel */}
        <section className={styles.resultsPanel}>
          {!result && !loading && (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
              </div>
              <h3 className={styles.emptyTitle}>Ready to Analyze</h3>
              <p className={styles.emptyText}>
                Upload an image and provide a caption to begin risk analysis
              </p>
            </div>
          )}

          {result && (
            <div className={styles.results}>
              <div className={styles.panelHeader}>
                <h2 className={styles.panelTitle}>Results</h2>
              </div>

              <RiskScore
                score={result.risk_score}
                level={result.risk_level}
              />

              <CategoryTags categories={result.categories} />

              <ExplanationPanel
                explanation={result.explanation}
                processingTime={result.processing_time_ms}
              />
            </div>
          )}
        </section>
      </div>

      {/* Footer */}
      <footer className={styles.footer}>
        <p>
          Powered by CLIP ViT-B/32 · Zero-Shot Multimodal Classification
        </p>
        <p className={styles.watermark}>
          Made by Sujato Dutta
        </p>
      </footer>
    </main>
  );
}
