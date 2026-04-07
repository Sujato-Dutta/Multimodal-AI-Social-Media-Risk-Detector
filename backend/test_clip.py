import asyncio
import sys
import json
from app.services.risk_analyzer import risk_analyzer

async def main():
    with open(r"F:\Multimodal AI Social Media Risk Detector\test_assets\safe_watch.png", "rb") as f:
        img_bytes = f.read()
    
    caption = "Just launched our new aesthetic lineup! Get yours at 20% off this weekend! ✨"
    
    print("Running analysis...")
    risk_analyzer.initialize()
    
    import app.services.risk_analyzer as ra
    
    # Store old calc locally and wrap it
    original_calc = ra.risk_analyzer._compute_category_scores
    def wrapped_calc(img, txt):
        res = original_calc(img, txt)
        print("BRAND RISK METRICS -> img_max:", res['brand_risk']['img_max'], "txt_max:", res['brand_risk']['txt_max'], "raw:", res['brand_risk']['raw_score'])
        return res
    ra.risk_analyzer._compute_category_scores = wrapped_calc
    
    res = await ra.risk_analyzer.analyze(img_bytes, caption)
    
    print("\nFINAL RESULT:")
    print(res.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())
