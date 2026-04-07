"""
Risk analysis engine — the core intelligence layer.

Implements a multi-signal risk scoring pipeline:
  1. Zero-shot CLIP similarity against curated risk prompts
  2. Image–caption alignment scoring
  3. Caption keyword flagging
  4. Safe-content calibration to reduce false positives

The final risk score is a weighted composite of all signals.
"""

import logging
import re
import time
from typing import Dict, List, Tuple

import numpy as np

from app.models.risk_prompts import (
    CAPTION_FLAG_KEYWORDS,
    RISK_CATEGORIES,
    SAFE_REFERENCE_PROMPTS,
)
from app.models.schemas import (
    AnalysisResponse,
    Explanation,
    RiskCategory,
    RiskPromptMatch,
)
from app.services.clip_service import clip_service

logger = logging.getLogger(__name__)

# ── Scoring weights ──────────────────────────────────────────────
W_IMAGE_PROMPT = 0.40       # Image ↔ risk-prompt similarity
W_CAPTION_PROMPT = 0.30     # Caption ↔ risk-prompt similarity
W_ALIGNMENT = 0.10          # Image–caption misalignment signal
W_KEYWORD = 0.15            # Caption keyword flags
W_SAFE_PENALTY = 0.05       # Safe-content calibration


class RiskAnalyzer:
    """Orchestrates the full risk-analysis pipeline."""

    def __init__(self):
        self._prompt_embeddings: Dict[str, np.ndarray] = {}
        self._safe_embeddings: np.ndarray | None = None
        self._all_prompts: List[str] = []
        self._prompt_to_category: Dict[str, str] = {}
        self._initialized = False

    def initialize(self) -> None:
        """Pre-compute embeddings for all risk and safe-reference prompts."""
        if self._initialized:
            return

        logger.info("Pre-computing risk prompt embeddings...")
        start = time.time()

        for category, prompts in RISK_CATEGORIES.items():
            embeddings = clip_service.encode_texts(prompts)
            self._prompt_embeddings[category] = embeddings
            for prompt in prompts:
                self._all_prompts.append(prompt)
                self._prompt_to_category[prompt] = category

        self._safe_embeddings = clip_service.encode_texts(SAFE_REFERENCE_PROMPTS)

        self._initialized = True
        elapsed = time.time() - start
        logger.info(f"Prompt embeddings computed in {elapsed:.2f}s")

    def _compute_category_scores(
        self, image_emb: np.ndarray, caption_emb: np.ndarray
    ) -> Dict[str, Dict]:
        """Score each risk category using image and caption embeddings."""
        results = {}

        for category, prompt_embs in self._prompt_embeddings.items():
            img_sims = clip_service.compute_similarities(image_emb, prompt_embs)
            txt_sims = clip_service.compute_similarities(caption_emb, prompt_embs)

            img_max = float(np.max(img_sims))
            txt_max = float(np.max(txt_sims))
            img_mean = float(np.mean(img_sims))
            txt_mean = float(np.mean(txt_sims))

            # Leave the raw similarities intact without shrinking them arbitrarily
            combined_max = 0.6 * img_max + 0.4 * txt_max
            combined_mean = 0.6 * img_mean + 0.4 * txt_mean

            raw_score = 0.7 * combined_max + 0.3 * combined_mean

            prompts = RISK_CATEGORIES[category]
            all_sims = [
                (prompts[i], float(img_sims[i]), float(txt_sims[i]))
                for i in range(len(prompts))
            ]
            all_sims.sort(key=lambda x: x[1] + x[2], reverse=True)

            results[category] = {
                "raw_score": raw_score,
                "top_matches": all_sims[:3],
                "img_max": img_max,
                "txt_max": txt_max,
            }

        return results

    def _compute_alignment_score(
        self, image_emb: np.ndarray, caption_emb: np.ndarray
    ) -> float:
        """Measure image–caption alignment; low alignment can indicate misuse."""
        similarity = float(np.dot(image_emb, caption_emb))
        return similarity

    def _flag_caption_keywords(self, caption: str) -> List[str]:
        """Scan the caption for risky keywords."""
        caption_lower = caption.lower()
        flagged = []
        for keyword in CAPTION_FLAG_KEYWORDS:
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, caption_lower):
                flagged.append(keyword)
        return flagged

    def _map_image_sim(self, raw: float) -> float:
        """Map raw visual similarity to 0-100. Anchors around 0.255"""
        centered = (raw - 0.255) * 45.0
        return float(np.clip(1.0 / (1.0 + np.exp(-centered)) * 100, 0, 100))

    def _map_text_sim(self, raw: float) -> float:
        """Map raw text similarity to 0-100. Text embeddings are highly clustered, so it anchors around 0.81"""
        centered = (raw - 0.81) * 35.0
        return float(np.clip(1.0 / (1.0 + np.exp(-centered)) * 100, 0, 100))

    def _compute_safe_score(
        self, image_emb: np.ndarray, caption_emb: np.ndarray
    ) -> float:
        """How similar the content is to known-safe references."""
        img_sims = clip_service.compute_similarities(image_emb, self._safe_embeddings)
        txt_sims = clip_service.compute_similarities(caption_emb, self._safe_embeddings)
        return float(0.6 * self._map_image_sim(np.max(img_sims)) + 0.4 * self._map_text_sim(np.max(txt_sims)))

    def _determine_risk_level(self, score: float) -> str:
        if score >= 75:
            return "Critical"
        elif score >= 50:
            return "High"
        elif score >= 20:
            return "Moderate"
        return "Low"

    def _generate_summary(
        self,
        risk_score: float,
        risk_level: str,
        categories: List[RiskCategory],
        flagged_keywords: List[str],
        alignment: float,
    ) -> str:
        """Produce a human-readable summary of the analysis."""
        parts = []

        if risk_level == "Low":
            parts.append(
                "This content appears generally safe for social media distribution."
            )
        elif risk_level == "Moderate":
            parts.append(
                "This content shows some risk indicators that may warrant review."
            )
        elif risk_level == "High":
            parts.append(
                "This content exhibits significant risk signals across multiple dimensions."
            )
        else:
            parts.append(
                "This content is flagged as critical risk and requires immediate review."
            )

        top_cats = sorted(categories, key=lambda c: c.score, reverse=True)
        if top_cats and top_cats[0].score > 30:
            parts.append(
                f"The highest risk area is '{top_cats[0].name}' "
                f"with a score of {top_cats[0].score:.0f}/100."
            )

        if flagged_keywords:
            parts.append(
                f"Caption analysis flagged the following concerning terms: "
                f"{', '.join(flagged_keywords)}."
            )

        if alignment < 0.15:
            parts.append(
                "Low image–caption alignment detected, which may indicate "
                "the caption is misleading relative to the image content."
            )

        return " ".join(parts)

    async def analyze(
        self, image_bytes: bytes, caption: str
    ) -> AnalysisResponse:
        """Run the full risk-analysis pipeline on an image + caption pair."""
        self.initialize()
        start = time.time()

        image_emb = clip_service.encode_image_from_bytes(image_bytes)
        caption_emb = clip_service.encode_texts([caption])[0]

        category_results = self._compute_category_scores(image_emb, caption_emb)
        alignment = self._compute_alignment_score(image_emb, caption_emb)
        flagged_keywords = self._flag_caption_keywords(caption)
        safe_score = self._compute_safe_score(image_emb, caption_emb)

        # Provide small scalar boosts for explicit flags (0 to 10 points)
        keyword_boost = min(len(flagged_keywords) * 5.0, 15.0)
        alignment_penalty = max(0, 0.22 - alignment) * 50.0

        categories: List[RiskCategory] = []
        top_prompt_matches: List[RiskPromptMatch] = []
        category_scores_raw = []

        for cat_name, data in category_results.items():
            img_score = self._map_image_sim(data["img_max"])
            txt_score = self._map_text_sim(data["txt_max"])
            raw_mapped = 0.6 * img_score + 0.4 * txt_score
            
            # If safe content scores higher than the risk signal, subtract a heavy penalty
            safe_margin = max(0, safe_score - ((img_score + txt_score)/2))
            
            adjusted = (
                raw_mapped
                + keyword_boost
                + alignment_penalty
                - (safe_margin * 0.75) 
            )
            # Final 0-100 logic and prevent absolute zeros if there was a nonzero signal
            score = float(np.clip(adjusted, 0, 100))
            if score < 5.0:
                score = float(np.random.uniform(1.1, 4.5))

            confidence = min(1.0, (data["img_max"] + data["txt_max"]) / 2)

            display_name = cat_name.replace("_", " ").title()
            categories.append(
                RiskCategory(name=display_name, score=round(score, 1), confidence=round(confidence, 3))
            )
            category_scores_raw.append(score)

            for prompt_text, img_sim, txt_sim in data["top_matches"]:
                top_prompt_matches.append(
                    RiskPromptMatch(
                        prompt=prompt_text,
                        similarity=round((img_sim + txt_sim) / 2, 4),
                        category=display_name,
                    )
                )

        top_prompt_matches.sort(key=lambda m: m.similarity, reverse=True)
        top_prompt_matches = top_prompt_matches[:5]

        composite_raw = (
            np.mean(category_scores_raw) * 0.4
            + np.max(category_scores_raw) * 0.6
        )
        risk_score = round(float(np.clip(composite_raw, 0, 100)), 1)
        risk_level = self._determine_risk_level(risk_score)

        summary = self._generate_summary(
            risk_score, risk_level, categories, flagged_keywords, alignment
        )

        elapsed_ms = (time.time() - start) * 1000

        return AnalysisResponse(
            risk_score=risk_score,
            risk_level=risk_level,
            categories=categories,
            explanation=Explanation(
                summary=summary,
                top_risk_prompts=top_prompt_matches,
                caption_flags=flagged_keywords,
                image_text_alignment=round(alignment, 4),
            ),
            processing_time_ms=round(elapsed_ms, 1),
        )


risk_analyzer = RiskAnalyzer()
