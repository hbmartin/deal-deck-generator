"""
Shared utilities for card templates.
"""

from pathlib import Path
from ..renderer.primitives import get_font as _get_font


def get_assets_dir() -> Path | None:
    """Get assets directory path if it exists."""
    assets_dir = Path(__file__).parent.parent.parent / "src" / "assets"
    return assets_dir if assets_dir.exists() else None


def get_template_font(font_name: str = "Arial", size: int = 14, bold: bool = False):
    """
    Get a font with assets directory support.

    Args:
        font_name: Font family name or filename
        size: Font size in points
        bold: Whether to use bold variant

    Returns:
        ImageFont object
    """
    assets_dir = get_assets_dir()
    return _get_font(font_name, size, bold, assets_dir)
