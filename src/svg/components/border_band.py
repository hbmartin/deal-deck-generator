"""Ornate rectangular border band: a diamond-chain motif tiled along each
edge with theme-selected corner ornaments, flanked by thin rules.

Explicit <use> tiling (not <pattern>): each edge gets an integer tile count
with a tiny justified stretch, sides are rotated 90 degrees, and corners
are their own motif — matching the printed cards.
"""

from ...geometry import Box
from ...svg import core
from ...tokens import BorderCorner

UNIT = 26.0  # motif design size (square)


def _motif(stroke: str) -> core.ET.Element:
    """One chain unit drawn in a UNIT x UNIT box centered at origin."""
    u = UNIT
    h = u / 2
    diamond = core.path(
        f"M 0 {-h * 0.72} L {h * 0.72} 0 L 0 {h * 0.72} L {-h * 0.72} 0 Z",
        fill="none",
        stroke=stroke,
        stroke_width=1.6,
    )
    dot = core.circle(0, 0, u * 0.09, fill=stroke)
    links = core.g(
        core.line(-h, -h * 0.5, -h * 0.28, 0, stroke=stroke, stroke_width=1.2),
        core.line(-h, h * 0.5, -h * 0.28, 0, stroke=stroke, stroke_width=1.2),
        core.line(h * 0.28, 0, h, -h * 0.5, stroke=stroke, stroke_width=1.2),
        core.line(h * 0.28, 0, h, h * 0.5, stroke=stroke, stroke_width=1.2),
    )
    return core.g(diamond, dot, links)


def _corner(stroke: str) -> core.ET.Element:
    """Corner square rosette centered at origin."""
    u = UNIT
    h = u / 2
    return core.g(
        core.rect(
            None,
            x=-h,
            y=-h,
            width=u,
            height=u,
            fill="none",
            stroke=stroke,
            stroke_width=1.6,
        ),
        core.path(
            f"M 0 {-h * 0.62} L {h * 0.62} 0 L 0 {h * 0.62} L {-h * 0.62} 0 Z",
            fill="none",
            stroke=stroke,
            stroke_width=1.4,
        ),
        core.circle(0, 0, u * 0.12, fill=stroke),
    )


def _agave_corner(stroke: str) -> core.ET.Element:
    """Four small pointed leaves forming a compact agave corner tile."""
    leaves = [
        core.path(
            "M 0 0 C -2 -3 -3 -7 0 -10 C 3 -7 2 -3 0 0 Z",
            fill="none",
            stroke=stroke,
            stroke_width=1.35,
            transform=core.rotate(angle),
        )
        for angle in (0, 90, 180, 270)
    ]
    return core.g(*leaves, core.circle(0, 0, 2.1, fill=stroke))


def _saguaro_corner(stroke: str) -> core.ET.Element:
    """Compact saguaro silhouette centered in the corner tile."""
    return core.g(
        core.path(
            "M 0 11 V -11",
            fill="none",
            stroke=stroke,
            stroke_width=2.4,
            stroke_linecap="round",
        ),
        core.path(
            "M 0 2 H -5 V -4 C -5 -6 -7 -6 -7 -4 V -1",
            fill="none",
            stroke=stroke,
            stroke_width=2.1,
            stroke_linecap="round",
            stroke_linejoin="round",
        ),
        core.path(
            "M 0 -1 H 5 V -7 C 5 -9 7 -9 7 -7 V -5",
            fill="none",
            stroke=stroke,
            stroke_width=2.1,
            stroke_linecap="round",
            stroke_linejoin="round",
        ),
        core.line(-6, 11, 6, 11, stroke=stroke, stroke_width=1.3),
    )


def _corner_for_style(stroke: str, style: BorderCorner) -> core.ET.Element:
    """Build the configured corner ornament."""
    match style:
        case "rosette":
            return _corner(stroke)
        case "agave":
            return _agave_corner(stroke)
        case "saguaro":
            return _saguaro_corner(stroke)


def border_band(
    doc: core.SVGDocument,
    band_center: Box,
    stroke: str,
    key: str = "band",
    corner_style: BorderCorner = "rosette",
) -> core.ET.Element:
    """Band ring whose centerline is the rectangle `band_center` (motifs only;
    the flanking pinstripe rules are composed by the card builders).
    """
    motif_id = f"band-motif-{key}"
    corner_id = (
        f"band-corner-{key}"
        if corner_style == "rosette"
        else f"band-corner-{corner_style}-{key}"
    )
    if not doc.has_def(motif_id):
        doc.add_def(motif_id, _motif(stroke))
    if not doc.has_def(corner_id):
        doc.add_def(corner_id, _corner_for_style(stroke, corner_style))

    parts = []
    x1, y1, x2, y2 = band_center.x, band_center.y, band_center.x2, band_center.y2

    # Horizontal edges (between corner squares)
    for (y,) in ((y1,), (y2,)):
        run = (x2 - x1) - UNIT  # leave room for corner squares
        n = max(1, round(run / UNIT))
        scale = run / (n * UNIT)
        for i in range(n):
            cx = x1 + UNIT / 2 + (i + 0.5) * UNIT * scale
            parts.append(
                core.use(
                    motif_id,
                    transform=f"{core.translate(cx, y)} scale({core.fmt(scale)} 1)",
                )
            )
    # Vertical edges
    for x in (x1, x2):
        run = (y2 - y1) - UNIT
        n = max(1, round(run / UNIT))
        scale = run / (n * UNIT)
        for i in range(n):
            cy = y1 + UNIT / 2 + (i + 0.5) * UNIT * scale
            parts.append(
                core.use(
                    motif_id,
                    transform=f"{core.translate(x, cy)} {core.rotate(90)} "
                    f"scale({core.fmt(scale)} 1)",
                )
            )
    # Corners
    for cx, cy in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
        parts.append(core.use(corner_id, transform=core.translate(cx, cy)))

    return core.g(*parts)
