"use client";

import { useState, useRef, useCallback } from "react";
import styles from "./ImageUploader.module.css";

export default function ImageUploader({ onFileSelect, disabled }) {
  const [preview, setPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState("");
  const inputRef = useRef(null);

  const handleFile = useCallback(
    (file) => {
      if (!file) return;

      const validTypes = ["image/jpeg", "image/png", "image/webp"];
      if (!validTypes.includes(file.type)) {
        alert("Please upload a JPEG, PNG, or WebP image.");
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        alert("Image must be under 10 MB.");
        return;
      }

      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
      onFileSelect(file);
    },
    [onFileSelect]
  );

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleInputChange = (e) => {
    handleFile(e.target.files[0]);
  };

  const clearImage = (e) => {
    e.stopPropagation();
    setPreview(null);
    setFileName("");
    onFileSelect(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div
      className={`${styles.dropzone} ${isDragging ? styles.dragging : ""} ${
        preview ? styles.hasPreview : ""
      } ${disabled ? styles.disabled : ""}`}
      onClick={() => !disabled && inputRef.current?.click()}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      id="image-uploader"
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleInputChange}
        className={styles.hiddenInput}
        disabled={disabled}
        id="image-file-input"
      />

      {preview ? (
        <div className={styles.previewContainer}>
          <img src={preview} alt="Upload preview" className={styles.preview} />
          <div className={styles.previewOverlay}>
            <span className={styles.fileName}>{fileName}</span>
            <button
              className={styles.clearBtn}
              onClick={clearImage}
              id="clear-image-btn"
            >
              ✕
            </button>
          </div>
        </div>
      ) : (
        <div className={styles.placeholder}>
          <div className={styles.uploadIcon}>
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
          <p className={styles.uploadText}>
            Drop an image here or <span className={styles.browse}>browse</span>
          </p>
          <p className={styles.uploadHint}>JPEG, PNG, or WebP · Max 10 MB</p>
        </div>
      )}
    </div>
  );
}
