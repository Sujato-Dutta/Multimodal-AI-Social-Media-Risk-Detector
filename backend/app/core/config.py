"""
Application configuration — centralized settings management.
"""

from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List, Optional


class Settings(BaseSettings):
    APP_NAME: str = "Multimodal AI Social Media Risk Detector"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://localhost:3000",
    ]

    EXTRA_ALLOWED_ORIGINS: str = ""

    MAX_IMAGE_SIZE_MB: int = 10
    MAX_IMAGE_DIMENSION: int = 224
    SUPPORTED_IMAGE_FORMATS: List[str] = ["image/jpeg", "image/png", "image/webp"]

    CLIP_MODEL_NAME: str = "ViT-B/32"
    INFERENCE_DEVICE: str = "cpu"

    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @model_validator(mode="after")
    def merge_extra_origins(self):
        if self.EXTRA_ALLOWED_ORIGINS:
            for origin in self.EXTRA_ALLOWED_ORIGINS.split(","):
                origin = origin.strip()
                if origin and origin not in self.ALLOWED_ORIGINS:
                    self.ALLOWED_ORIGINS.append(origin)
        return self

    @property
    def max_image_size_bytes(self) -> int:
        return self.MAX_IMAGE_SIZE_MB * 1024 * 1024


settings = Settings()
