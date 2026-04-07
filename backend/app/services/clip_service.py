"""
CLIP model service — handles model lifecycle and embedding generation.

Encapsulates all interactions with the CLIP model behind a clean interface.
The model is loaded lazily on first use to optimize cold-start behavior.
"""

import logging
import time
from io import BytesIO
from typing import List, Optional, Tuple

import clip
import numpy as np
import torch
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)


class CLIPService:
    """Manages the CLIP model and provides embedding generation."""

    def __init__(self):
        self._model = None
        self._preprocess = None
        self._device = settings.INFERENCE_DEVICE
        self._model_name = settings.CLIP_MODEL_NAME
        self._is_loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def load_model(self) -> None:
        """Load the CLIP model into memory."""
        if self._is_loaded:
            return

        logger.info(f"Loading CLIP model '{self._model_name}' on {self._device}...")
        start = time.time()

        self._model, self._preprocess = clip.load(
            self._model_name,
            device=self._device,
            jit=False,
        )
        self._model.eval()
        self._is_loaded = True

        elapsed = time.time() - start
        logger.info(f"CLIP model loaded in {elapsed:.2f}s")

    def _ensure_loaded(self) -> None:
        if not self._is_loaded:
            self.load_model()

    def preprocess_image(self, image_bytes: bytes) -> torch.Tensor:
        """Convert raw image bytes to a preprocessed tensor."""
        self._ensure_loaded()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")

        max_dim = settings.MAX_IMAGE_DIMENSION
        if max(image.size) > max_dim:
            image.thumbnail((max_dim, max_dim), Image.LANCZOS)

        tensor = self._preprocess(image).unsqueeze(0).to(self._device)
        return tensor

    @torch.no_grad()
    def encode_image(self, image_tensor: torch.Tensor) -> np.ndarray:
        """Generate a normalized embedding for a preprocessed image tensor."""
        self._ensure_loaded()
        features = self._model.encode_image(image_tensor)
        features = features / features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy().flatten()

    @torch.no_grad()
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """Generate normalized embeddings for a list of text strings."""
        self._ensure_loaded()
        tokens = clip.tokenize(texts, truncate=True).to(self._device)
        features = self._model.encode_text(tokens)
        features = features / features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy()

    def compute_similarities(
        self, embedding: np.ndarray, reference_embeddings: np.ndarray
    ) -> np.ndarray:
        """Compute cosine similarities between one embedding and many references."""
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        norms = np.linalg.norm(reference_embeddings, axis=1, keepdims=True) + 1e-8
        reference_embeddings = reference_embeddings / norms
        return reference_embeddings @ embedding

    def encode_image_from_bytes(self, image_bytes: bytes) -> np.ndarray:
        """End-to-end: raw bytes → normalized embedding."""
        tensor = self.preprocess_image(image_bytes)
        return self.encode_image(tensor)


clip_service = CLIPService()
