"""Golden image management.

Two golden sets exist because rendering is font-environment dependent:
- mac: system Gill Sans (the pixels that actually get printed locally)
- ci:  bundled fallback fonts only (deterministic on Linux runners)
"""

import platform
import shutil
from pathlib import Path

from .data.loader import load_deck
from .render.pipeline import render_deck

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GOLDENS_DIR = PROJECT_ROOT / "tests" / "goldens"
BUILD_DIR = PROJECT_ROOT / "output" / ".goldens-build"

_GILL_SANS = Path("/System/Library/Fonts/Supplemental/GillSans.ttc")


def detect_env() -> str:
    if platform.system() == "Darwin" and _GILL_SANS.exists():
        return "mac"
    return "ci"


def fonts_mode_for(env: str) -> str:
    return "system" if env == "mac" else "bundled"


def update_goldens(env: str | None = None, renderer: str = "rsvg") -> str:
    env = env or detect_env()
    deck = load_deck()
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    render_deck(
        deck,
        BUILD_DIR,
        renderer=renderer,
        fonts_mode=fonts_mode_for(env),
        previews=True,
    )
    target = GOLDENS_DIR / env
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for png in sorted((BUILD_DIR / "preview").glob("*.png")):
        shutil.copy2(png, target / png.name)
    return env
