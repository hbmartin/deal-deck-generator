"""Procedural guilloché engraving: sine-wave mesh fields and trochoid rosettes.

Everything here is deterministic pure geometry — no randomness — so repeated
renders produce byte-identical SVGs (required for golden-image stability).
"""

import math

from ...geometry import Box
from ...svg import core


def _wave_path(width: float, wavelength: float, amplitude: float, phase: float) -> str:
    """One horizontal sine stroke sampled as a polyline path (y around 0)."""
    step = wavelength / 16
    pts = []
    x = 0.0
    while x <= width + step / 2:
        y = amplitude * math.sin(2 * math.pi * x / wavelength + phase)
        pts.append(f"{core.fmt(x)} {core.fmt(y)}")
        x += step
    return "M " + " L ".join(pts)


def wave_field(
    doc: core.SVGDocument,
    clip_box: Box,
    stroke: str,
    spacing: float = 7.5,
    wavelength: float = 92.0,
    amplitude: float = 3.8,
    stroke_width: float = 0.8,
    key: str = "field",
) -> core.ET.Element:
    """Two interleaved families of sine strokes -> woven engraving texture.

    One wave path per family lives in <defs>; rows are stamped with <use>.
    """
    clip_id = f"guilloche-clip-{key}"
    if not doc.has_def(clip_id):
        doc.add_def(
            clip_id,
            core.el("clipPath", core.rect(clip_box)),
        )
    for fam, phase in (("a", 0.0), ("b", math.pi)):
        wave_id = f"guilloche-wave-{key}-{fam}"
        if not doc.has_def(wave_id):
            doc.add_def(
                wave_id,
                core.path(
                    _wave_path(clip_box.w + wavelength, wavelength, amplitude, phase),
                    fill="none",
                    stroke=stroke,
                    stroke_width=stroke_width,
                ),
            )

    rows = []
    n = int(clip_box.h / spacing) + 2
    for k in range(n):
        y = clip_box.y + k * spacing
        rows.append(core.use(f"guilloche-wave-{key}-a", x=clip_box.x, y=y))
        rows.append(
            core.use(f"guilloche-wave-{key}-b", x=clip_box.x, y=y + spacing / 2)
        )
    return core.g(*rows, clip_path=f"url(#{clip_id})")


def _epitrochoid_path(
    cx: float, cy: float, R: float, r: float, d: float, turns: int, samples: int = 720
) -> str:
    """Closed epitrochoid; with R/r = p/q in lowest terms it closes after q turns."""
    pts = []
    k = (R + r) / r
    for i in range(samples + 1):
        t = 2 * math.pi * turns * i / samples
        x = (R + r) * math.cos(t) - d * math.cos(k * t)
        y = (R + r) * math.sin(t) - d * math.sin(k * t)
        pts.append(f"{core.fmt(cx + x)} {core.fmt(cy + y)}")
    return "M " + " L ".join(pts) + " Z"


def rosette(
    cx: float,
    cy: float,
    radius: float,
    stroke: str,
    stroke_width: float = 0.85,
    variant: int = 0,
) -> core.ET.Element:
    """Superposed epitrochoid rings — the engraved medallion look.

    `radius` is the approximate outer radius; co-prime ratio pairs per
    variant give visually distinct medallions.
    """
    params = [
        [(11, 4, 0.42), (13, 5, 0.30), (17, 6, 0.22)],
        [(9, 4, 0.5), (12, 5, 0.26), (15, 7, 0.2)],
    ][variant % 2]
    paths = []
    for i, (big, small, df) in enumerate(params):
        # Scale so the curve's maximum extent ~= radius, with successive
        # curves stepping inward to build a dense concentric medallion.
        shrink = 1.0 - 0.18 * i
        unit = radius * shrink / (big / small + 1 + df * 2.2)
        R, r = unit * big / small, unit
        d = unit * df * 2.2
        paths.append(
            core.path(
                _epitrochoid_path(cx, cy, R, r, d, turns=small, samples=720),
                fill="none",
                stroke=stroke,
                stroke_width=stroke_width,
            )
        )
    return core.g(*paths)
