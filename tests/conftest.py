import os
import shutil
from pathlib import Path

import pytest

from src.data.loader import load_deck

from src.goldens import detect_env, fonts_mode_for

from src.render.pipeline import render_deck

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def deck():
    return load_deck()


@pytest.fixture(scope="session")
def golden_env() -> str:
    return os.environ.get("GOLDEN_ENV") or detect_env()


@pytest.fixture(scope="session")
# pyrefly: ignore [bad-return]
def rendered_previews(deck, golden_env, tmp_path_factory) -> Path:
    """Render every unique design at preview size once per test session."""
    out = tmp_path_factory.mktemp("render")
    render_deck(deck, out, fonts_mode=fonts_mode_for(golden_env), previews=True)
    yield out / "preview"
    shutil.rmtree(out, ignore_errors=True)
