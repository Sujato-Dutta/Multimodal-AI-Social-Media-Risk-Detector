"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class RiskCategory(BaseModel):
    name: str = Field(..., description="Risk category name")
    score: float = Field(..., ge=0.0, le=100.0, description="Category risk score (0–100)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level")


class RiskPromptMatch(BaseModel):
    prompt: str = Field(..., description="The risk prompt that matched")
    similarity: float = Field(..., description="Cosine similarity score")
    category: str = Field(..., description="Parent risk category")


class Explanation(BaseModel):
    summary: str = Field(..., description="Human-readable risk summary")
    top_risk_prompts: List[RiskPromptMatch] = Field(
        default_factory=list,
        description="Top matching risk prompts with similarity scores"
    )
    caption_flags: List[str] = Field(
        default_factory=list,
        description="Flagged keywords found in the caption"
    )
    image_text_alignment: float = Field(
        0.0,
        description="Cosine similarity between image and caption embeddings"
    )


class AnalysisResponse(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Overall risk score (0–100)")
    risk_level: str = Field(..., description="Risk level: Low, Moderate, High, Critical")
    categories: List[RiskCategory] = Field(
        default_factory=list,
        description="Breakdown by risk category"
    )
    explanation: Explanation = Field(..., description="Detailed explanation of risk assessment")
    processing_time_ms: float = Field(..., description="Total inference time in milliseconds")


class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    status: str
    version: str
    model_loaded: bool
