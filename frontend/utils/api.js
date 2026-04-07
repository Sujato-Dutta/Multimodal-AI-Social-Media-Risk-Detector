/**
 * API client for the Risk Detector backend.
 */

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:10000";

/**
 * Analyze an image + caption for social media risk.
 * @param {File} imageFile
 * @param {string} caption
 * @returns {Promise<object>} AnalysisResponse
 */
export async function analyzeContent(imageFile, caption) {
  const formData = new FormData();
  formData.append("image", imageFile);
  formData.append("caption", caption);

  const res = await fetch(`${API_BASE}/api/v1/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Analysis failed (HTTP ${res.status})`);
  }

  return res.json();
}

/**
 * Check backend health.
 * @returns {Promise<object>}
 */
export async function checkHealth() {
  const res = await fetch(`${API_BASE}/api/v1/health`);
  return res.json();
}

/**
 * Warm up the model.
 * @returns {Promise<object>}
 */
export async function warmupModel() {
  const res = await fetch(`${API_BASE}/api/v1/warmup`, { method: "POST" });
  return res.json();
}
