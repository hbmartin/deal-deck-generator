"""Rent-card bullseye: colored outer band (two halves or ten segments),
heavy black ring, white center with RENT.
"""

import math

from ...svg import core
from ...text.measure import get_measurer
from ...tokens import Tokens
from .icons import bulb, train

BAND_T = 60  # colored band thickness
RING_T = 22  # black ring thickness
GAP_DEG = 2.2  # white separator between wild segments

# Segment order around the wild ring, clockwise from 12 o'clock.
WILD_ORDER = [
    "yellow",
    "green",
    "dark_blue",
    "railroad",
    "utility",
    "brown",
    "light_blue",
    "pink",
    "orange",
    "red",
]


def _annulus_segment(  # noqa: PLR0913
    cx: float,
    cy: float,
    r_out: float,
    r_in: float,
    a0: float,
    a1: float,
) -> str:
    """Segment path between angles a0..a1 (degrees, 0 = 12 o'clock, cw)."""

    def pt(r: float, a: float) -> str:
        rad = math.radians(a - 90)
        return f"{core.fmt(cx + r * math.cos(rad))} {core.fmt(cy + r * math.sin(rad))}"

    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (
        f"M {pt(r_out, a0)} "
        f"A {core.fmt(r_out)} {core.fmt(r_out)} 0 {large} 1 {pt(r_out, a1)} "
        f"L {pt(r_in, a1)} "
        f"A {core.fmt(r_in)} {core.fmt(r_in)} 0 {large} 0 {pt(r_in, a0)} Z"
    )


def bullseye(  # noqa: PLR0913
    tokens: Tokens,
    cx: float,
    cy: float,
    r: float,
    colors: list[str],
    *,
    is_wild: bool = False,
) -> core.ET.Element:
    """colors: two property color keys, or empty with is_wild=True."""
    band_in = r - BAND_T
    center_r = band_in - RING_T

    parts = [core.circle(cx, cy, r, fill="#FFFFFF")]

    if is_wild:
        step = 360 / len(WILD_ORDER)
        for i, key in enumerate(WILD_ORDER):
            fill = tokens.property_color(key)["fill"]
            a0 = i * step + GAP_DEG / 2
            a1 = (i + 1) * step - GAP_DEG / 2
            parts.append(
                core.path(_annulus_segment(cx, cy, r, band_in, a0, a1), fill=fill)
            )
    else:
        first, second = colors
        if "railroad" in colors or "utility" in colors:
            # split left/right, icons embedded at the sides
            halves = [(180.0, 360.0, first), (0.0, 180.0, second)]
        else:
            halves = [(270.0, 450.0, first), (90.0, 270.0, second)]
        for a0, a1, key in halves:
            fill = tokens.property_color(key)["fill"]
            parts.append(
                core.path(_annulus_segment(cx, cy, r, band_in, a0, a1), fill=fill)
            )
        # thin outline around the colored band
        parts.append(
            core.circle(cx, cy, r, fill="none", stroke="#000000", stroke_width=3)
        )

        if "railroad" in colors or "utility" in colors:
            band_mid = r - BAND_T / 2
            for key, side in ((first, -1), (second, 1)):
                icon_h = BAND_T * 0.72
                if key == "railroad":
                    icon = train(icon_h, "#FFFFFF")
                    icon_w = icon_h * 1.5
                elif key == "utility":
                    icon = bulb(icon_h)
                    icon_w = icon_h * 0.9
                else:
                    continue
                icon.set(
                    "transform",
                    core.translate(cx + side * band_mid - icon_w / 2, cy - icon_h / 2),
                )
                parts.append(icon)

    # heavy black ring + white center
    parts.append(
        core.circle(
            cx,
            cy,
            band_in - RING_T / 2,
            fill="none",
            stroke="#000000",
            stroke_width=RING_T,
        )
    )
    parts.append(core.circle(cx, cy, center_r, fill="#FFFFFF"))

    font = tokens.font("condensed_heavy")
    measurer = get_measurer(font.measure_path)
    size = tokens.size("circle_title") * 0.98
    parts.append(
        core.el(
            "text",
            x=cx,
            y=cy + size * measurer.metrics.cap_height / 2,
            text="RENT",
            font_family=font.stack,
            font_weight=font.weight,
            font_size=size,
            text_anchor="middle",
            fill="#000000",
            letter_spacing=1,
        )
    )
    return core.g(*parts)
