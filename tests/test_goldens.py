"""Golden-image regression: rendered previews vs the accepted set for this
environment (tests/goldens/mac or tests/goldens/ci).

Thresholds absorb antialiasing drift across cairo/harfbuzz point releases
while catching real layout/color changes.
"""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

GOLDENS_DIR = Path(__file__).parent / "goldens"

MEAN_ABS_TOLERANCE = 1.5
OUTLIER_VALUE = 24
OUTLIER_FRACTION = 0.005


def _load(path: Path) -> np.ndarray:
    with Image.open(path) as img:
        return np.asarray(img.convert("RGB"), dtype=np.int16)


def test_previews_match_goldens(golden_env, rendered_previews):
    golden_dir = GOLDENS_DIR / golden_env
    if not golden_dir.exists():
        pytest.skip(
            f"no golden set for env {golden_env!r}; run: "
            f"python main.py goldens --update --env {golden_env}"
        )

    goldens = sorted(golden_dir.glob("*.png"))
    assert goldens, f"golden dir {golden_dir} is empty"

    failures = []
    for golden in goldens:
        rendered = rendered_previews / golden.name
        assert rendered.exists(), f"missing rendered preview {golden.name}"
        a, b = _load(golden), _load(rendered)
        if a.shape != b.shape:
            failures.append(f"{golden.name}: shape {a.shape} != {b.shape}")
            continue
        diff = np.abs(a - b)
        mean_abs = float(diff.mean())
        outliers = float((diff.max(axis=2) > OUTLIER_VALUE).mean())
        if mean_abs > MEAN_ABS_TOLERANCE or outliers > OUTLIER_FRACTION:
            failures.append(
                f"{golden.name}: mean_abs={mean_abs:.2f} outliers={outliers:.3%}"
            )
    assert not failures, "golden mismatches:\n" + "\n".join(failures)
