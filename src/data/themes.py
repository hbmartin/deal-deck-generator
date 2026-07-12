"""Theme resolution: locate a theme's card data and build its merged tokens.

A theme is a directory under ``themes/`` holding a ``cards.yaml`` (required) and
an optional ``tokens.json`` overlay. The overlay is deep-merged onto the shared
base ``design_tokens.json`` at load time, so a theme only lists the values it
changes (typically the property palette). The ``classic`` theme has no overlay,
so it resolves to the base tokens unchanged.
"""

import json
from functools import cache
from pathlib import Path

from ..tokens import TOKENS_PATH, Tokens

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
THEMES_DIR = PROJECT_ROOT / "themes"
DEFAULT_THEME = "classic"
# Shared card-list fragments a theme can pull in via `include:` live here. The
# directory has no cards.yaml, so it is not a theme.
FRAGMENTS_DIR = THEMES_DIR / "_shared"


def available_themes() -> list[str]:
    """Sorted names of theme directories that contain a cards.yaml."""
    if not THEMES_DIR.is_dir():
        return []
    return sorted(p.name for p in THEMES_DIR.iterdir() if (p / "cards.yaml").is_file())


def available_fragments() -> list[str]:
    """Sorted names of shared card-list fragments in themes/_shared/*.yaml."""
    if not FRAGMENTS_DIR.is_dir():
        return []
    return sorted(p.stem for p in FRAGMENTS_DIR.glob("*.yaml"))


def _validate_fragment_name(name: str) -> None:
    """Reject include names that are not a registered shared fragment."""
    fragments = available_fragments()
    if name not in fragments:
        message = f"unknown fragment {name!r}; available: {', '.join(fragments)}"
        raise ValueError(message)


def fragment_cards_path(name: str) -> Path:
    """Path to a shared fragment's yaml, validating that it is registered.

    Like theme names, the allow-list check (exact membership of the discovered
    fragment stems) is what blocks absolute paths and ``..`` traversal.
    """
    _validate_fragment_name(name)
    return FRAGMENTS_DIR / f"{name}.yaml"


def _validate_theme_name(name: str) -> None:
    """Reject names that do not exactly identify a registered theme."""
    themes = available_themes()
    if name not in themes:
        message = f"unknown theme {name!r}; available: {', '.join(themes)}"
        raise ValueError(message)


def theme_cards_path(name: str) -> Path:
    """Path to a theme's cards.yaml, validating the theme exists."""
    _validate_theme_name(name)
    return THEMES_DIR / name / "cards.yaml"


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Recursively merge overlay onto base. Nested dicts merge; scalars and
    lists in the overlay replace the base value. Returns a new dict.
    """
    merged = dict(base)
    for key, value in overlay.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


@cache
def load_theme_tokens(name: str = DEFAULT_THEME) -> Tokens:
    """Load the base tokens and deep-merge the theme's optional overlay."""
    _validate_theme_name(name)
    with TOKENS_PATH.open(encoding="utf-8") as f:
        base = json.load(f)
    overlay_path = THEMES_DIR / name / "tokens.json"
    if overlay_path.is_file():
        with overlay_path.open(encoding="utf-8") as f:
            base = _deep_merge(base, json.load(f))
    return Tokens(raw=base)
