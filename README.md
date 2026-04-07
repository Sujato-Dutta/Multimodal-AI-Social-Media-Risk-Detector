# 🛡️ Multimodal AI Social Media Risk Detector

> A production-grade, multimodal AI content moderation system that analyzes social media posts (image + caption) for brand risk, offensive content, and misinformation — using zero-shot classification.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)](https://nextjs.org)
[![CLIP](https://img.shields.io/badge/OpenAI-CLIP-412991?logo=openai&logoColor=white)](https://github.com/openai/CLIP)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Problem Statement

Social media platforms process **billions of posts daily**, each potentially containing harmful, misleading, or brand-unsafe content. Traditional moderation relies on:

- **Manual review** — expensive, slow, and doesn't scale
- **Keyword filters** — trivially bypassed, high false-positive rate
- **Single-modality models** — analyze text OR images, missing cross-modal context

The core challenge: **A harmless image paired with a malicious caption (or vice versa) creates risk that no single-modality system can detect.** A photo of a kitchen knife is safe. Paired with a threatening caption, it isn't. This requires understanding the *relationship* between visual and textual content.

This project solves that by using **multimodal AI** to jointly analyze image and text, producing explainable risk assessments across three critical categories: **Brand Risk**, **Offensive Content**, and **Misinformation**.

---

## 🧠 Why Multimodal AI

### The Case for CLIP

| Approach | Training Data Needed | Inference Cost | Adaptability | Cross-Modal? |
|---|---|---|---|---|
| Custom CNN + LSTM | ~100K labeled samples | High (GPU) | Retrain for new categories | ❌ |
| Fine-tuned BERT + ResNet | ~50K labeled samples | High (GPU) | Retrain for new categories | ❌ |
| **CLIP Zero-Shot** | **0 samples** | **Low (CPU)** | **Edit prompts** | **✅** |

**CLIP (Contrastive Language-Image Pretraining)** was trained on 400M image-text pairs from the internet. It learns a shared embedding space where images and text can be directly compared. This enables:

1. **Zero-shot classification** — No task-specific training data required. Define risk categories as text prompts and compute similarity.
2. **Cross-modal understanding** — Detect when an image and caption tell conflicting stories (a key misinformation signal).
3. **CPU-friendly inference** — The ViT-B/32 variant runs efficiently on CPU, making it deployable on free-tier infrastructure.
4. **Instant extensibility** — Add new risk categories by writing new prompts. No retraining, no new data.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Next.js)                         │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │  Image    │  │   Caption    │  │     Results Dashboard     │  │
│  │  Upload   │  │   Input      │  │  Score │ Tags │ Explain   │  │
│  └────┬─────┘  └──────┬───────┘  └───────────────────────────┘  │
│       └───────┬────────┘                        ▲                │
└───────────────┼─────────────────────────────────┼────────────────┘
                │ POST /api/v1/analyze            │ JSON Response
                ▼                                 │
┌───────────────┼─────────────────────────────────┼────────────────┐
│               │         BACKEND (FastAPI)       │                │
│  ┌────────────▼──────────────────────────────┐  │                │
│  │           Input Validation                │  │                │
│  │  • Format check  • Size limit  • Sanitize │  │                │
│  └────────────┬──────────────────────────────┘  │                │
│               ▼                                 │                │
│  ┌────────────────────────────────────────────┐ │                │
│  │         CLIP Encoding Layer                │ │                │
│  │  ┌─────────────┐    ┌──────────────────┐   │ │                │
│  │  │ Image       │    │ Text             │   │ │                │
│  │  │ Encoder     │    │ Encoder          │   │ │                │
│  │  │ (ViT-B/32)  │    │ (Transformer)    │   │ │                │
│  │  └──────┬──────┘    └────────┬─────────┘   │ │                │
│  │         │ 512-d              │ 512-d        │ │                │
│  └─────────┼────────────────────┼─────────────┘ │                │
│            ▼                    ▼                │                │
│  ┌─────────────────────────────────────────────┐ │                │
│  │          Risk Analysis Engine               │ │                │
│  │                                             │ │                │
│  │  1. Similarity vs Risk Prompts (30 prompts) │ │                │
│  │  2. Image–Caption Alignment Score           │ │                │
│  │  3. Caption Keyword Flagging               │ │                │
│  │  4. Safe-Content Calibration               │ │                │
│  │  5. Sigmoid Normalization → 0–100          │ │                │
│  └──────────────────────┬──────────────────────┘ │                │
│                         ▼                        │                │
│  ┌──────────────────────────────────────────────┐│                │
│  │         Explainability Layer                 ││                │
│  │  • Top matched prompts + scores             ││                │
│  │  • Flagged keywords                         │├────────────────┘
│  │  • Alignment interpretation                 ││
│  │  • Human-readable summary                   ││
│  └──────────────────────────────────────────────┘│
└──────────────────────────────────────────────────┘
```

### Pipeline Flow

1. **Input Layer** — Image file + caption text received via multipart form
2. **Preprocessing** — Image resized to 224×224, normalized via CLIP's transform; caption cleaned and truncated
3. **Multimodal Encoding** — CLIP produces 512-dimensional embeddings for both modalities
4. **Feature Extraction** — Cosine similarity computed against 30 risk prompts (10 per category) and 8 safe-reference prompts
5. **Multi-Signal Scoring** — Weighted combination of image–prompt similarity, caption–prompt similarity, alignment score, keyword flags, and safe-content penalty
6. **Normalization** — Raw scores passed through sigmoid scaling to produce 0–100 risk scores
7. **Explanation Generation** — Top-matching prompts, flagged keywords, and alignment interpretation assembled into a human-readable report

---

## 🔑 Design Decisions

### Why CLIP ViT-B/32?

- **ViT-B/32** is the smallest CLIP variant (~340MB). It provides strong zero-shot performance while fitting comfortably in memory-constrained environments.
- Larger variants (ViT-L/14) offer marginal accuracy gains but 4× the memory footprint — not justified for this use case.

### Why Zero-Shot Over Fine-Tuning?

- **No labeled dataset** is required. Risk categories evolve constantly (new misinformation trends, new offensive content patterns). With zero-shot, updating detection is as simple as editing prompt strings.
- Fine-tuning requires curated datasets, GPU training, and risks catastrophic forgetting of CLIP's general capabilities.

### Why a Lightweight Classifier Isn't Needed (Yet)

The zero-shot similarity approach already produces well-calibrated risk signals. A classifier head (logistic regression / MLP) would add marginal benefit but introduce:
- A training data dependency
- A model artifact to version and deploy
- Risk of overfitting to a narrow distribution

The current sigmoid-normalized scoring achieves strong separation between safe and risky content without any trained classifier.

---

## 📊 Risk Scoring Formula

The risk score is computed through a multi-signal pipeline:

### Modality-Aware Normalization

Because CLIP text embeddings are much more densely clustered than image embeddings, raw cosine similarities cannot be combined directly. We map them to `0-100` scores using independent sigmoid curves centered around their respective baselines:

```python
img_score = sigmoid( (max(image_sims) - 0.255) × 45.0 ) × 100
txt_score = sigmoid( (max(caption_sims) - 0.81) × 35.0 ) × 100

raw_mapped = 0.6 × img_score + 0.4 × txt_score
```

### Adjustments

```python
safe_margin = max(0, safe_score - mean(img_score, txt_score))

adjusted = raw_mapped
         + keyword_boost         # (0 to +15 based on flagged keywords)
         + alignment_penalty     # (0 to +50 for severe image-text conflict)
         - (safe_margin × 0.75)  # Huge penalty if perfectly matches safe references
```

### Composite Risk Score

```python
score      = clip(adjusted, 0, 100)
final_risk = 0.4 × mean(category_scores) + 0.6 × max(category_scores)
```

**Rationale:** The composite formula weights the *worst* category more heavily (0.6) because a post that is extremely offensive but otherwise safe should still be flagged. The mean provides a baseline that captures multi-category risk.

---

## 🎨 Prompt Engineering Strategy

### Risk Prompts

Each category uses 10 carefully engineered prompts designed to:

1. **Cover the semantic space** — Each prompt targets a distinct sub-type of risk within its category
2. **Use CLIP-friendly language** — Prompts are phrased as image/content descriptions that align with CLIP's training distribution
3. **Avoid ambiguity** — Each prompt is specific enough to minimize false positives on benign content

Example for `brand_risk`:
```
"a controversial political statement or protest"
"content that could embarrass a corporation"
"a social media post that could cause a PR crisis"
"content depicting unsafe or reckless behavior"
```

### Safe Reference Prompts

8 positive-reference prompts establish a "safe baseline":
```
"a wholesome family-friendly social media post"
"a beautiful landscape or nature photograph"
"a professional corporate announcement"
```

These serve as **calibration anchors** — high similarity to safe references reduces the risk score, suppressing false positives on benign content.

### Why This Works

CLIP's embedding space captures semantic relationships, not just keywords. The prompt "a social media post that could cause a PR crisis" activates when CLIP detects visual or textual signals associated with controversy, scandal, or inappropriate content — even for scenarios the model has never explicitly seen.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **ML Model** | OpenAI CLIP ViT-B/32 | Multimodal embeddings |
| **Backend** | FastAPI + Uvicorn | REST API server |
| **Frontend** | Next.js 15 (App Router) | User interface |
| **Validation** | Pydantic v2 | Request/response schemas |
| **Image Processing** | Pillow + torchvision | Preprocessing pipeline |
| **Deployment** | Render (backend) + Vercel (frontend) | Cloud hosting |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/multimodal-ai-risk-detector.git
cd multimodal-ai-risk-detector
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 10000 --workers 1
```

The API will be available at `http://localhost:10000`. Interactive docs at `http://localhost:10000/docs`.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local

# Start development server
npm run dev
```

The UI will be available at `http://localhost:3000`.

### 4. Warm Up the Model

Before first use, warm up the CLIP model:

```bash
curl -X POST http://localhost:10000/api/v1/warmup
```

### 5. Test the API

```bash
curl -X POST http://localhost:10000/api/v1/analyze \
  -F "image=@test_image.jpg" \
  -F "caption=Check out this amazing product!"
```

---

## 📡 API Reference

### `GET /api/v1/health`

Health check and readiness probe.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true
}
```

### `POST /api/v1/warmup`

Pre-loads the CLIP model and computes risk prompt embeddings.

### `POST /api/v1/analyze`

Analyze an image + caption pair for social media risk.

**Request:** `multipart/form-data`
| Field | Type | Required | Description |
|---|---|---|---|
| `image` | File | Yes | JPEG, PNG, or WebP image (max 10MB) |
| `caption` | String | No | Post caption / accompanying text |

**Response:**
```json
{
  "risk_score": 67.3,
  "risk_level": "High",
  "categories": [
    {
      "name": "Offensive Content",
      "score": 72.1,
      "confidence": 0.341
    },
    {
      "name": "Brand Risk",
      "score": 58.4,
      "confidence": 0.298
    },
    {
      "name": "Misinformation",
      "score": 45.2,
      "confidence": 0.267
    }
  ],
  "explanation": {
    "summary": "This content exhibits significant risk signals...",
    "top_risk_prompts": [
      {
        "prompt": "graphic violence or gore in an image",
        "similarity": 0.3241,
        "category": "Offensive Content"
      }
    ],
    "caption_flags": ["violent", "attack"],
    "image_text_alignment": 0.1823
  },
  "processing_time_ms": 1247.3
}
```

---

## 🧪 Evaluation

### Synthetic Dataset Strategy

The evaluation script generates synthetic test samples spanning four risk levels with controlled captions:

- **Low risk:** Nature photos, pet content, recipes, celebrations
- **High risk:** Clickbait, medical misinformation, sensationalized content
- **Critical risk:** Hate speech, violent threats, dehumanizing language

### Running Evaluation

```bash
cd eval

# Ensure the backend is running, then:
python evaluate.py --api-url http://localhost:10000

# Save results to JSON
python evaluate.py --api-url http://localhost:10000 --output results.json
```

### Metrics

| Metric | Description |
|---|---|
| **Exact Accuracy** | Predicted risk level matches expected level |
| **±1 Tolerance Accuracy** | Predicted level is within one step of expected |
| **Precision** | Of all flagged-risky content, how much was actually risky |
| **Recall** | Of all actually risky content, how much was flagged |
| **F1-Score** | Harmonic mean of precision and recall |

---

## 🚢 Deployment

### Backend → Render

1. Push the `backend/` directory to a GitHub repository
2. Create a new **Web Service** on [Render](https://render.com)
3. Connect your repository
4. Configure:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 10000 --workers 1`
5. Add environment variable:
   - `EXTRA_ALLOWED_ORIGINS` = your Vercel frontend URL

### Frontend → Vercel

1. Push the `frontend/` directory to a GitHub repository
2. Import the project on [Vercel](https://vercel.com)
3. Configure:
   - **Root Directory:** `frontend`
   - **Framework:** Next.js
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = your Render backend URL

---

## ⚠️ Failure Case Analysis

### Known Failure Modes

1. **Subtle sarcasm/irony** — CLIP interprets content literally. A sarcastic caption praising something terrible may not be flagged.

2. **Cultural context** — Gestures and symbols that are offensive in one culture but benign in another may produce false positives/negatives.

3. **Text-in-images** — CLIP has limited OCR capability. Offensive text embedded in an image may not be detected.

4. **Novel misinformation** — Zero-shot detection relies on similarity to known patterns. Completely novel misinformation formats may evade detection.

5. **Adversarial inputs** — Subtle image perturbations designed to fool CLIP can shift similarity scores.

### Mitigation Strategies

- **Multi-signal fusion** — No single signal dominates; the system combines image similarity, text similarity, alignment, and keywords.
- **Safe-reference calibration** — Reduces false positives on benign content.
- **Conservative thresholds** — The sigmoid normalization centers at 0.18 similarity, meaning content needs meaningfully elevated similarity to cross risk thresholds.

---
## 📁 Project Structure

```
multimodal-ai-social-media-risk-detector/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py          # API endpoint handlers
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py          # Centralized settings
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── risk_prompts.py    # Risk prompt definitions
│   │   │   └── schemas.py         # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── clip_service.py    # CLIP model management
│   │   │   └── risk_analyzer.py   # Risk scoring engine
│   │   ├── __init__.py
│   │   └── main.py                # FastAPI application entry
│   ├── Dockerfile
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── globals.css            # Design system & theme
│   │   ├── layout.js              # Root layout with SEO
│   │   ├── page.js                # Main application page
│   │   └── page.module.css        # Page-specific styles
│   ├── components/
│   │   ├── CategoryTags.js        # Risk category cards
│   │   ├── ExplanationPanel.js    # Detailed explanation view
│   │   ├── ImageUploader.js       # Drag-and-drop image upload
│   │   ├── LoadingSpinner.js      # Analysis loading state
│   │   └── RiskScore.js           # Risk score progress bar
│   ├── utils/
│   │   └── api.js                 # Backend API client
│   ├── .env.example
│   └── package.json
├── eval/
│   └── evaluate.py                # Evaluation script with metrics
├── .gitignore
└── README.md
```

---

## 👤 Author

**[Sujato Dutta]** — [LinkedIn](https://www.linkedin.com/in/sujato-dutta/)

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
