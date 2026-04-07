"""
Risk prompt definitions — the core of the zero-shot detection strategy.

Each category contains semantically rich prompts that CLIP compares against
both the image and caption embeddings. The prompts are engineered to cover
a broad spectrum of risk signals within each category.
"""

from typing import Dict, List

RISK_CATEGORIES: Dict[str, List[str]] = {
    "offensive_content": [
        "a photo containing hate speech or slurs",
        "an image with offensive or vulgar gestures",
        "explicit or sexually suggestive content",
        "nudity or partial nudity in a social media post",
        "racist or discriminatory imagery",
        "a photo mocking a person's disability or appearance",
        "content that promotes substance abuse",
        "graphic violence or gore in an image",
        "bullying or cyberbullying content",
        "a post with profane or abusive language",
    ],
    "brand_risk": [
        "a controversial political statement or protest",
        "a product associated with negative publicity",
        "content that could embarrass a corporation",
        "an image showing illegal activity or lawbreaking",
        "content unsuitable for advertising placement",
        "a scene involving weapons or dangerous objects",
        "a social media post that could cause a PR crisis",
        "inappropriate use of a logo or brand identity",
        "content depicting unsafe or reckless behavior",
        "imagery associated with scandal or controversy",
    ],
    "misinformation": [
        "a manipulated or doctored photograph",
        "misleading medical or health advice",
        "a fake news headline or fabricated story",
        "a conspiracy theory being promoted as fact",
        "out-of-context photo used to deceive viewers",
        "misleading statistics or infographic",
        "a deepfake or AI-generated face",
        "false claim about a public figure",
        "disinformation campaign content",
        "clickbait or sensationalized content designed to mislead",
    ],
}

SAFE_REFERENCE_PROMPTS: List[str] = [
    "a wholesome family-friendly social media post",
    "a beautiful landscape or nature photograph",
    "a professional corporate announcement",
    "a friendly group photo of people smiling",
    "an educational and informative infographic",
    "a positive product review or recommendation",
    "a celebration or festive gathering",
    "an inspirational motivational quote",
]

CAPTION_FLAG_KEYWORDS: List[str] = [
    "kill", "hate", "die", "attack", "bomb", "threat",
    "fake", "hoax", "scam", "fraud", "conspiracy",
    "nude", "explicit", "nsfw", "xxx",
    "drugs", "cocaine", "meth",
    "racist", "sexist", "slur",
    "weapon", "gun", "knife",
    "blood", "gore", "violent",
    "propaganda", "manipulation",
]
