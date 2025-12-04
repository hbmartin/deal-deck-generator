"""
Shared utilities for card templates.
"""

import json
import functools
from pathlib import Path
from ..renderer.primitives import get_font as _get_font


def get_assets_dir() -> Path | None:
    """Get assets directory path if it exists."""
    assets_dir = Path(__file__).parent.parent.parent / "src" / "assets"
    return assets_dir if assets_dir.exists() else None


@functools.lru_cache(maxsize=1)
def load_design_tokens() -> dict:
    """
    Load design tokens from JSON file with caching.

    The result is cached using functools.lru_cache to avoid reading
    and parsing the JSON file multiple times during batch operations.

    Returns:
        Dictionary containing design tokens

    Note:
        The cache is cleared automatically if the function is called
        with different arguments (though it takes no arguments, so
        the cache persists for the lifetime of the Python process).
    """
    tokens_path = Path(__file__).parent.parent.parent / "design_tokens.json"
    with open(tokens_path) as f:
        return json.load(f)


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
