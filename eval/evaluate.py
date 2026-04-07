"""
Evaluation script for the Multimodal AI Social Media Risk Detector.

Generates a synthetic test dataset, runs predictions through the API,
and computes Accuracy, Precision, Recall, and F1-score.

Usage:
    python evaluate.py --api-url http://localhost:10000
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import List, Tuple

import requests
from PIL import Image
import numpy as np
from io import BytesIO


@dataclass
class TestSample:
    caption: str
    expected_risk: str  # "low", "moderate", "high", "critical"
    description: str


SYNTHETIC_DATASET: List[TestSample] = [
    TestSample(
        caption="Beautiful sunset over the mountains, feeling grateful 🌅",
        expected_risk="low",
        description="Safe nature content",
    ),
    TestSample(
        caption="Just adopted this cute puppy! Welcome home buddy! 🐶",
        expected_risk="low",
        description="Safe pet content",
    ),
    TestSample(
        caption="Great team meeting today, excited about the product launch!",
        expected_risk="low",
        description="Safe corporate content",
    ),
    TestSample(
        caption="This politician is secretly plotting to destroy the country, share before they delete this!",
        expected_risk="high",
        description="Misinformation / conspiracy",
    ),
    TestSample(
        caption="EXPOSED: The real truth they don't want you to know! This is a massive cover-up!",
        expected_risk="high",
        description="Clickbait misinformation",
    ),
    TestSample(
        caption="Kill all people who disagree with me, they deserve to die",
        expected_risk="critical",
        description="Violent hate speech",
    ),
    TestSample(
        caption="This brand is terrible and their CEO should be attacked for what they've done",
        expected_risk="high",
        description="Brand risk with violent language",
    ),
    TestSample(
        caption="Check out my new recipe for homemade pasta! 🍝",
        expected_risk="low",
        description="Safe food content",
    ),
    TestSample(
        caption="BREAKING: Exposed leaked photos show the scandal of the decade!!",
        expected_risk="high",
        description="Sensationalized clickbait",
    ),
    TestSample(
        caption="This miracle drug cures everything, doctors hate this trick!",
        expected_risk="high",
        description="Medical misinformation",
    ),
    TestSample(
        caption="Had a wonderful birthday celebration with family 🎂",
        expected_risk="low",
        description="Safe celebration content",
    ),
    TestSample(
        caption="These people are subhuman and need to be dealt with. Share if you agree.",
        expected_risk="critical",
        description="Dehumanizing hate speech",
    ),
]


def generate_test_image(width: int = 224, height: int = 224, seed: int = 42) -> bytes:
    """Generate a simple synthetic test image."""
    rng = np.random.RandomState(seed)
    pixels = rng.randint(0, 255, (height, width, 3), dtype=np.uint8)
    img = Image.fromarray(pixels)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def risk_level_to_numeric(level: str) -> int:
    mapping = {"low": 0, "moderate": 1, "high": 2, "critical": 3}
    return mapping.get(level.lower(), -1)


def run_evaluation(api_url: str) -> dict:
    """Run all test samples against the API and compute metrics."""
    analyze_url = f"{api_url}/api/v1/analyze"

    print(f"\n{'═' * 60}")
    print(f"  Evaluation — {len(SYNTHETIC_DATASET)} test samples")
    print(f"  API: {analyze_url}")
    print(f"{'═' * 60}\n")

    y_true = []
    y_pred = []
    results = []

    for i, sample in enumerate(SYNTHETIC_DATASET):
        img_bytes = generate_test_image(seed=i)
        files = {"image": ("test.png", img_bytes, "image/png")}
        data = {"caption": sample.caption}

        try:
            start = time.time()
            resp = requests.post(analyze_url, files=files, data=data, timeout=30)
            elapsed = time.time() - start

            if resp.status_code != 200:
                print(f"  [{i+1:02d}] ✗ HTTP {resp.status_code} — {sample.description}")
                continue

            result = resp.json()
            predicted = result["risk_level"].lower()
            expected = sample.expected_risk

            y_true.append(risk_level_to_numeric(expected))
            y_pred.append(risk_level_to_numeric(predicted))

            match = "✓" if predicted == expected else "✗"
            print(
                f"  [{i+1:02d}] {match}  expected={expected:<10s} "
                f"predicted={predicted:<10s} score={result['risk_score']:5.1f}  "
                f"({elapsed:.1f}s) — {sample.description}"
            )

            results.append({
                "caption": sample.caption,
                "expected": expected,
                "predicted": predicted,
                "risk_score": result["risk_score"],
                "time_s": round(elapsed, 2),
            })

        except requests.exceptions.RequestException as e:
            print(f"  [{i+1:02d}] ✗ Request failed: {e}")

    if not y_true:
        print("\nNo successful predictions. Cannot compute metrics.")
        return {}

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    accuracy = float(np.mean(y_true == y_pred))

    binary_true = (y_true >= 2).astype(int)
    binary_pred = (y_pred >= 2).astype(int)

    tp = int(np.sum((binary_pred == 1) & (binary_true == 1)))
    fp = int(np.sum((binary_pred == 1) & (binary_true == 0)))
    fn = int(np.sum((binary_pred == 0) & (binary_true == 1)))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    tolerance_acc = float(np.mean(np.abs(y_true - y_pred) <= 1))

    print(f"\n{'─' * 60}")
    print(f"  METRICS")
    print(f"{'─' * 60}")
    print(f"  Exact Accuracy     : {accuracy:.1%}")
    print(f"  ±1 Tolerance Acc   : {tolerance_acc:.1%}")
    print(f"  Precision (risky)  : {precision:.1%}")
    print(f"  Recall (risky)     : {recall:.1%}")
    print(f"  F1-Score (risky)   : {f1:.1%}")
    print(f"{'─' * 60}\n")

    return {
        "accuracy": round(accuracy, 4),
        "tolerance_accuracy": round(tolerance_acc, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "samples": len(y_true),
        "results": results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the risk detector API")
    parser.add_argument("--api-url", default="http://localhost:10000", help="Base API URL")
    parser.add_argument("--output", default=None, help="Save results to JSON file")
    args = parser.parse_args()

    metrics = run_evaluation(args.api_url)

    if args.output and metrics:
        with open(args.output, "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"  Results saved to {args.output}")
