"""
Save the SunBiz Funding logo to media/brand/sunbiz_logo.png

Usage:
    1. Place the logo image in this directory as 'logo_source.png'
    2. Run: python scripts/save_logo.py

    OR copy manually:
    cp /path/to/sunbiz_logo.png media/brand/sunbiz_logo.png

The logo compositing system in imagen_generate.py expects:
    media/brand/sunbiz_logo.png (PNG with transparency)

For best results:
    - Use PNG format with transparent background
    - Minimum 500x500px resolution
    - Logo should have alpha channel (transparent background)
"""

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
LOGO_DEST = PROJECT_ROOT / "media" / "brand" / "sunbiz_logo.png"


def save_logo(source_path: str):
    """Copy logo from source to the expected brand directory."""
    source = Path(source_path)
    if not source.exists():
        print(f"ERROR: Source file not found: {source}")
        sys.exit(1)

    LOGO_DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(source), str(LOGO_DEST))
    print(f"Logo saved to: {LOGO_DEST}")
    print(f"Size: {LOGO_DEST.stat().st_size:,} bytes")
    print("Logo compositing is now active for all generated ads.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/save_logo.py <path_to_logo.png>")
        print()
        print("Or copy manually:")
        print(f"  cp /path/to/logo.png {LOGO_DEST}")
    else:
        save_logo(sys.argv[1])
