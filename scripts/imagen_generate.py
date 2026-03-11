"""
Gemini Imagen (Nano Banana) — AI Image Generation for Ad Creatives
Uses Google Gemini API's native image generation to create business lending ad images.

Requirements:
    pip install google-genai Pillow python-dotenv

NOTE: The package is `google-genai` (NOT the deprecated `google-generativeai`).

Usage:
    from scripts.imagen_generate import generate_ad_image, generate_ad_variants

    # Generate single ad
    result = generate_ad_image(
        prompt="Professional business lending ad...",
        size="1080x1080",
        output_path="media/exports/campaign1/feed_v1.png"
    )

    # Generate A/B test variants
    results = generate_ad_variants(
        base_prompt="Business term loan ad...",
        variants=3,
        size="1080x1080",
        campaign_name="q1_business_loans"
    )
"""

import os
import re
import base64
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

# Load credentials
load_dotenv(Path(__file__).parent.parent / ".env.agents")

# Model priority: best text rendering first, then fast, then legacy
MODELS = [
    "gemini-2.5-flash-image",      # Nano Banana — fast, production-ready
    "gemini-2.0-flash-exp",         # Legacy experimental fallback
]


REGISTRY_PATH = Path(__file__).parent.parent / "media" / "ASSET_REGISTRY.md"

# Matches a registry table row: | 001 | ... |
_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|")


def register_asset(
    file_path: str,
    campaign_name: str,
    creative_type: str,
    angle: str,
    size: str,
    model: str,
) -> str:
    """
    Append a new DRAFT entry to media/ASSET_REGISTRY.md.

    Args:
        file_path: Path to the saved image file (relative to project root preferred)
        campaign_name: Campaign identifier, e.g. 'consolidation_q2_2026'
        creative_type: e.g. 'Static Image'
        angle: Creative angle / concept description
        size: Pixel dimensions string, e.g. '1080x1080'
        model: Gemini model name used to generate the image

    Returns:
        Zero-padded asset ID string, e.g. '004'
    """
    registry_text = REGISTRY_PATH.read_text(encoding="utf-8") if REGISTRY_PATH.exists() else ""

    # Determine next ID by finding the highest existing numeric ID in the table
    existing_ids = [int(m.group(1)) for m in _ROW_RE.finditer(registry_text)]
    next_id = (max(existing_ids) + 1) if existing_ids else 1
    asset_id = str(next_id).zfill(3)

    # Normalise file path to forward slashes relative to project root
    project_root = REGISTRY_PATH.parent.parent
    try:
        relative_path = Path(file_path).resolve().relative_to(project_root.resolve())
        display_path = str(relative_path).replace("\\", "/")
    except ValueError:
        display_path = str(file_path).replace("\\", "/")

    created = date.today().isoformat()
    new_row = (
        f"| {asset_id} | {display_path} | {campaign_name} | {creative_type} "
        f"| {angle} | {size} | {model} | DRAFT | {created} | — |"
    )

    # Insert the new row directly before the Status Legend section so the table
    # stays contiguous and the legend always appears below it.
    legend_marker = "\n## Status Legend"
    if legend_marker in registry_text:
        updated_text = registry_text.replace(legend_marker, f"\n{new_row}{legend_marker}")
    else:
        # Fallback: append to end of file
        updated_text = registry_text.rstrip("\n") + f"\n{new_row}\n"

    REGISTRY_PATH.write_text(updated_text, encoding="utf-8")
    return asset_id


def get_client():
    """Initialize Gemini API client using google-genai SDK."""
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in .env.agents. "
            "Get one from https://aistudio.google.com/apikey"
        )

    return genai.Client(api_key=api_key)


def _size_to_aspect_ratio(size):
    """Convert pixel dimensions string to Gemini aspect ratio."""
    width, height = map(int, size.split("x"))
    ratio = width / height

    # Map to closest supported aspect ratio
    ratios = [
        (1.0, "1:1"),
        (1.778, "16:9"),
        (0.5625, "9:16"),
        (0.8, "4:5"),
        (1.25, "5:4"),
        (0.75, "3:4"),
        (1.333, "4:3"),
        (0.667, "2:3"),
        (1.5, "3:2"),
    ]

    closest = min(ratios, key=lambda r: abs(r[0] - ratio))
    return closest[1]


def _size_to_resolution(size):
    """Pick appropriate resolution tier based on pixel dimensions."""
    width, height = map(int, size.split("x"))
    max_dim = max(width, height)
    if max_dim <= 512:
        return "0.5K"
    elif max_dim <= 1080:
        return "1K"
    elif max_dim <= 2048:
        return "2K"
    else:
        return "4K"


def generate_ad_image(
    prompt,
    output_path,
    size="1080x1080",
    style="professional",
    campaign_name: str = "",
    creative_type: str = "Static Image",
    angle: str = "",
):
    """
    Generate a single ad image using Gemini native image generation.

    Args:
        prompt: Detailed text description of the ad image to generate
        output_path: Where to save the generated image
        size: Image dimensions (1080x1080, 1080x1920, 1200x628)
        style: Image style hint (professional, modern, bold)
        campaign_name: Optional — passed to register_asset() when provided
        creative_type: Asset type label for the registry (default 'Static Image')
        angle: Creative angle / concept description for the registry

    Returns:
        dict with path, size, model, status, and asset_id (when registered)
    """
    from google.genai import types

    def _success(path: str, model: str) -> dict:
        """Build a success result dict and register the asset when campaign_name is set."""
        result: dict = {"path": path, "size": size, "model": model, "status": "SUCCESS"}
        if campaign_name:
            asset_id = register_asset(
                file_path=path,
                campaign_name=campaign_name,
                creative_type=creative_type,
                angle=angle or Path(path).stem,
                size=size,
                model=model,
            )
            result["asset_id"] = asset_id
        return result

    client = get_client()
    aspect_ratio = _size_to_aspect_ratio(size)
    resolution = _size_to_resolution(size)

    # Enhance prompt with quality modifiers
    enhanced_prompt = (
        f"{prompt}\n\n"
        f"Style: {style}, high resolution, clean design, "
        f"professional financial services advertisement, "
        f"suitable for social media advertising."
    )

    # Try each model in priority order
    for model_name in MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=enhanced_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=resolution,
                    ),
                ),
            )

            # Save generated image
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data is not None:
                    image_data = part.inline_data.data
                    # Decode if base64 string
                    if isinstance(image_data, str):
                        image_data = base64.b64decode(image_data)

                    with open(output_path, "wb") as f:
                        f.write(image_data)

                    return _success(str(output_path), model_name)

        except Exception:
            continue

    # All models failed — try Imagen standalone as final fallback
    try:
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=enhanced_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/png",
            ),
        )

        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        response.generated_images[0].image.save(output_path)
        return _success(str(output_path), "imagen-3.0-generate-002")
    except Exception as e:
        return {"path": None, "error": f"All models failed. Last: {e}", "status": "FAILED"}


def generate_ad_variants(base_prompt, campaign_name, variants=3, size="1080x1080"):
    """
    Generate multiple ad variants for A/B testing.

    Args:
        base_prompt: Base prompt for the ad
        campaign_name: Campaign identifier for file naming
        variants: Number of variants to generate (default 3)
        size: Image dimensions

    Returns:
        list of result dicts
    """
    results = []
    output_dir = Path(__file__).parent.parent / "media" / "exports" / campaign_name

    for i in range(1, variants + 1):
        output_path = output_dir / f"ad_v{i}_{size.replace('x', '_')}.png"

        variant_prompt = f"{base_prompt}\nVariant {i} of {variants} — create a unique visual arrangement."

        result = generate_ad_image(
            prompt=variant_prompt,
            output_path=str(output_path),
            size=size,
        )
        result["variant"] = i
        results.append(result)

    return results


def generate_consolidation_ad(
    headline="STOP THE DAILY DRAIN",
    before_daily="$2,100/day across 4 funders",
    after_daily="$850/day — one partner",
    savings="Save $1,250/day",
    cta="See If You Qualify",
    company_name="SunBiz Funding",
    bg_color="navy blue (#001F54)",
    size="1080x1080",
    campaign_name="consolidation",
    style="before_after",
):
    """
    Generate an MCA consolidation ad image for SunBiz Funding.

    Args:
        headline: Main ad headline
        before_daily: Before consolidation daily payment text
        after_daily: After consolidation daily payment text
        savings: Savings amount text
        cta: Call to action text
        company_name: Company name for branding
        bg_color: Background color theme
        size: Image dimensions
        campaign_name: For file naming
        style: 'before_after', 'roadmap', or 'payment_table'

    Returns:
        result dict with file path
    """
    if style == "roadmap":
        prompt = f"""Professional financial services advertisement with {bg_color} background.
Bold white headline: "{headline}".
Four connected steps shown as a horizontal roadmap:
Phase 1: "Consolidate" — Phase 2: "Buy Out Positions" — Phase 3: "One Funder" — Phase 4: "Line of Credit"
Subtext: "We don't stack — we build a plan."
Company name "{company_name}" prominently displayed.
Orange CTA button: "{cta}".
Clean, modern, analytical financial advisory design.
Professional, trustworthy, data-driven aesthetic."""
    elif style == "payment_table":
        prompt = f"""Clean professional financial ad with {bg_color} background.
Bold headline: "OVERLEVERAGED? SEE THE DIFFERENCE."
Comparison table:
Row 1 (red tint): "Current: 4 positions — {before_daily} — Cash flow: Choked"
Row 2 (green tint): "After SunBiz: 1 position — {after_daily} — Cash flow: Healthy"
Large text: "Monthly savings: $37,500 back in your business"
Green checkmark on the "After" row.
"{company_name}" branding.
Orange button: "{cta}".
Professional, data-driven, analytical style."""
    else:  # before_after (default)
        prompt = f"""Professional MCA consolidation advertisement with {bg_color} background.
Bold white headline: "{headline}".
Clean infographic comparing:
LEFT section (red/orange, labeled "BEFORE"): "{before_daily}"
RIGHT section (green, labeled "AFTER"): "{after_daily}"
Large text showing savings: "{savings}"
Company name "{company_name}" with logo top-right.
Orange CTA button at bottom: "{cta}".
Small disclaimer: "Terms vary based on business qualifications."
Clean, analytical, professional financial advisory design.
No cheesy stock photos. Modern infographic style."""

    output_dir = Path(__file__).parent.parent / "media" / "exports" / campaign_name
    output_path = output_dir / f"consolidation_{style}_{size.replace('x', '_')}.png"

    angle_labels = {
        "before_after": "Consolidation - Before/After",
        "roadmap": "Consolidation - Roadmap",
        "payment_table": "Consolidation - Payment Table",
    }

    return generate_ad_image(
        prompt=prompt,
        output_path=str(output_path),
        size=size,
        campaign_name=campaign_name,
        creative_type="Static Image",
        angle=angle_labels.get(style, f"Consolidation - {style}"),
    )


def generate_growth_ad(
    headline="SMART CAPITAL FOR GROWING BUSINESSES",
    cta="See Your Options",
    company_name="SunBiz Funding",
    size="1080x1080",
    campaign_name="growth_capital",
):
    """Generate a growth capital / A-paper ad for clean merchants."""
    prompt = f"""Professional business funding advertisement with clean white/light gray background.
Navy blue headline: "{headline}".
Image of a confident business owner in their modern workspace.
Blue accent cards showing: "Fast Decisions" | "No Bank Delays" | "No Equity Required"
Subtext: "Revenue $40K+/month? You qualify for our best terms."
"{company_name}" branding with logo.
Orange CTA button: "{cta}".
Modern, clean, professional financial advisory design."""

    output_dir = Path(__file__).parent.parent / "media" / "exports" / campaign_name
    output_path = output_dir / f"growth_ad_{size.replace('x', '_')}.png"

    return generate_ad_image(
        prompt=prompt,
        output_path=str(output_path),
        size=size,
        campaign_name=campaign_name,
        creative_type="Static Image",
        angle="Growth Capital",
    )


def generate_all_sizes(prompt, campaign_name):
    """Generate an ad in all standard platform sizes."""
    sizes = {
        "meta_feed_square": "1080x1080",       # 1:1
        "meta_feed_portrait": "1080x1350",      # 4:5
        "meta_stories": "1080x1920",            # 9:16
        "google_display": "1200x628",           # ~16:9
    }

    results = {}
    for name, size in sizes.items():
        output_dir = Path(__file__).parent.parent / "media" / "exports" / campaign_name
        output_path = output_dir / f"{name}.png"
        results[name] = generate_ad_image(
            prompt=prompt, output_path=str(output_path), size=size
        )

    return results


if __name__ == "__main__":
    print("SunBiz Funding — Gemini Imagen Ad Generator")
    print("=" * 50)
    print()
    print("SDK: google-genai (pip install google-genai)")
    print("Models: gemini-2.5-flash-image (primary), imagen-3.0-generate-002 (fallback)")
    print()
    print("Usage examples:")
    print()
    print("  # Generate a consolidation ad (before/after)")
    print("  from scripts.imagen_generate import generate_consolidation_ad")
    print("  result = generate_consolidation_ad(")
    print('      headline="STOP THE DAILY DRAIN",')
    print('      before_daily="$2,100/day across 4 funders",')
    print('      after_daily="$850/day — one partner",')
    print('      savings="Save $1,250/day",')
    print('      style="before_after",  # or "roadmap" or "payment_table"')
    print("  )")
    print()
    print("  # Generate a growth capital ad")
    print("  from scripts.imagen_generate import generate_growth_ad")
    print('  result = generate_growth_ad(headline="SMART CAPITAL FOR GROWING BUSINESSES")')
    print()
    print("  # Generate A/B test variants")
    print("  from scripts.imagen_generate import generate_ad_variants")
    print('  results = generate_ad_variants("MCA consolidation prompt...", "campaign1", variants=3)')
    print()
    print("  # Generate all platform sizes")
    print("  from scripts.imagen_generate import generate_all_sizes")
    print('  results = generate_all_sizes("MCA ad prompt...", "campaign1")')
