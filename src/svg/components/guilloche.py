"""Procedural field textures and medallions selected by theme tokens.

Everything here is deterministic pure geometry — no randomness — so repeated
renders produce byte-identical SVGs (required for golden-image stability).
"""

import math

from ...geometry import Box
from ...svg import core
from ...tokens import FieldPattern


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


def wave_field(  # noqa: PLR0913
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


def mitla_step_field(
    doc: core.SVGDocument,
    clip_box: Box,
    stroke: str,
    stroke_width: float = 0.9,
    key: str = "field",
) -> core.ET.Element:
    """Tile an original stepped-stone rhythm across a clipped field."""
    clip_id = f"mitla-step-clip-{key}"
    if not doc.has_def(clip_id):
        doc.add_def(
            clip_id,
            core.el("clipPath", core.rect(clip_box)),
        )

    motif_id = f"mitla-step-motif-{key}"
    motif_w = 64.0
    motif_h = 36.0
    if not doc.has_def(motif_id):
        upper = core.path(
            "M 0 30 H 12 V 24 H 24 V 18 H 36 V 12 H 48 V 6 H 64",
            fill="none",
            stroke=stroke,
            stroke_width=stroke_width,
        )
        lower = core.path(
            "M 0 6 H 16 V 12 H 28 V 18 H 40 V 24 H 52 V 30 H 64",
            fill="none",
            stroke=stroke,
            stroke_width=stroke_width,
        )
        doc.add_def(motif_id, core.g(upper, lower))

    tiles = []
    row_count = math.ceil(clip_box.h / motif_h) + 1
    column_count = math.ceil(clip_box.w / motif_w) + 2
    for row in range(row_count):
        offset = motif_w / 2 if row % 2 else 0.0
        y = clip_box.y + row * motif_h
        for column in range(-1, column_count):
            x = clip_box.x + column * motif_w + offset
            tiles.append(core.use(motif_id, x=x, y=y))
    return core.g(*tiles, clip_path=f"url(#{clip_id})", opacity=0.72)


def texture_field(
    doc: core.SVGDocument,
    clip_box: Box,
    stroke: str,
    style: FieldPattern,
    key: str = "field",
) -> core.ET.Element:
    """Build the field texture selected by the active theme tokens."""
    match style:
        case "wave":
            return wave_field(doc, clip_box, stroke=stroke, key=key)
        case "mitla_step":
            return mitla_step_field(doc, clip_box, stroke=stroke, key=key)


def _epitrochoid_path(  # noqa: PLR0913
    cx: float,
    cy: float,
    outer_radius: float,
    rolling_radius: float,
    offset: float,
    turns: int,
    samples: int = 720,
) -> str:
    """Draw a closed epitrochoid that closes after the requested turns."""
    pts = []
    k = (outer_radius + rolling_radius) / rolling_radius
    for i in range(samples + 1):
        t = 2 * math.pi * turns * i / samples
        x = (outer_radius + rolling_radius) * math.cos(t) - offset * math.cos(k * t)
        y = (outer_radius + rolling_radius) * math.sin(t) - offset * math.sin(k * t)
        pts.append(f"{core.fmt(cx + x)} {core.fmt(cy + y)}")
    return "M " + " L ".join(pts) + " Z"


def rosette(  # noqa: PLR0913
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
        outer_radius, rolling_radius = unit * big / small, unit
        offset = unit * df * 2.2
        paths.append(
            core.path(
                _epitrochoid_path(
                    cx,
                    cy,
                    outer_radius,
                    rolling_radius,
                    offset,
                    turns=small,
                    samples=720,
                ),
                fill="none",
                stroke=stroke,
                stroke_width=stroke_width,
            )
        )
    return core.g(*paths)


def _agave_leaf(length: float, width: float, stroke: str) -> core.ET.Element:
    """One pointed agave leaf rooted at the local origin."""
    return core.path(
        f"M 0 0 C {-width * 0.62} {-length * 0.28} "
        f"{-width * 0.42} {-length * 0.68} 0 {-length} "
        f"C {width * 0.42} {-length * 0.68} {width * 0.62} {-length * 0.28} 0 0 Z",
        fill="none",
        stroke=stroke,
        stroke_width=0.9,
    )


def agave_medallion(  # noqa: PLR0913
    doc: core.SVGDocument,
    cx: float,
    cy: float,
    radius: float,
    stroke: str,
    key: str = "medallion",
) -> core.ET.Element:
    """Concentric radial agave leaves used behind the money-card disc."""
    leaf_id = f"agave-medallion-leaf-{key}"
    if not doc.has_def(leaf_id):
        doc.add_def(
            leaf_id,
            _agave_leaf(length=radius, width=radius * 0.24, stroke=stroke),
        )

    leaves = []
    for index in range(16):
        angle = index * 22.5
        leaves.append(
            core.use(
                leaf_id,
                transform=f"{core.translate(cx, cy)} {core.rotate(angle)}",
            )
        )
        leaves.append(
            core.use(
                leaf_id,
                transform=(
                    f"{core.translate(cx, cy)} {core.rotate(angle + 11.25)} scale(0.64)"
                ),
            )
        )
    return core.g(*leaves, opacity=0.78)
