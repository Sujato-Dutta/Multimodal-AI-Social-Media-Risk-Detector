"""
API route handlers for the Risk Detector service.
"""

import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.models.schemas import AnalysisResponse, HealthResponse
from app.services.clip_service import clip_service
from app.services.risk_analyzer import risk_analyzer

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health and readiness probe."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        model_loaded=clip_service.is_loaded,
    )


@router.post("/warmup")
async def warmup():
    """Pre-load the model and prompt embeddings to eliminate cold-start latency."""
    clip_service.load_model()
    risk_analyzer.initialize()
    return {"status": "warm", "model": settings.CLIP_MODEL_NAME}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(
    image: UploadFile = File(..., description="Image file to analyze"),
    caption: str = Form("", description="Caption or text associated with the image"),
):
    """
    Analyze an image + caption pair for social media risk.

    Returns a composite risk score, per-category breakdown, and
    human-readable explanation with matched risk prompts.
    """

    if image.content_type not in settings.SUPPORTED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format '{image.content_type}'. "
                   f"Accepted: {', '.join(settings.SUPPORTED_IMAGE_FORMATS)}",
        )

    image_bytes = await image.read()

    if len(image_bytes) > settings.max_image_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Image exceeds maximum size of {settings.MAX_IMAGE_SIZE_MB}MB.",
        )

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image file.")

    if not caption.strip():
        caption = "a social media post with an image"

    try:
        result = await risk_analyzer.analyze(image_bytes, caption.strip())
        logger.info(
            f"Analysis complete — risk_score={result.risk_score} "
            f"risk_level={result.risk_level} time={result.processing_time_ms:.0f}ms"
        )
        return result

    except Exception as e:
        logger.exception("Analysis pipeline error")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during content analysis. Please try again.",
        )
