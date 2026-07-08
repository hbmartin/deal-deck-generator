"""Fanned-card icon used in rent tables: (n-1) colored cards fanned behind
a white front card that carries a colored top stripe and the count digit.
"""

from ...svg import core
from ...text.measure import get_measurer
from ...tokens import Tokens

# Front card design box
CARD_W = 46
CARD_H = 62
CORNER = 7
OUTLINE = 3


def _stripe(fill: str) -> core.ET.Element:
    """Colored band across a mini card's top, inset for the outline."""
    return core.path(
        f"M {OUTLINE / 2} {CARD_H * 0.30} L {OUTLINE / 2} {CORNER} "
        f"Q {OUTLINE / 2} {OUTLINE / 2} {CORNER} {OUTLINE / 2} "
        f"L {CARD_W - CORNER} {OUTLINE / 2} "
        f"Q {CARD_W - OUTLINE / 2} {OUTLINE / 2} {CARD_W - OUTLINE / 2} {CORNER} "
        f"L {CARD_W - OUTLINE / 2} {CARD_H * 0.30} Z",
        fill=fill,
    )


def _mini_card(fill: str) -> core.ET.Element:
    return core.rect(
        None,
        x=0,
        y=0,
        width=CARD_W,
        height=CARD_H,
        rx=CORNER,
        fill=fill,
        stroke="#000000",
        stroke_width=OUTLINE,
    )


def fan_icon(
    doc: core.SVGDocument,
    tokens: Tokens,
    count: int,
    color_key: str,
    scale: float = 1.0,
) -> core.ET.Element:
    """Group anchored so the FRONT card's top-left is at (0, 0)."""
    fill = tokens.property_color(color_key)["fill"]
    font = tokens.font("condensed_heavy")
    measurer = get_measurer(font.measure_path)

    parts = []
    # Back cards are striped like the front tile and fan out to the left,
    # pivoting near the front card's bottom-right corner (as photographed).
    for i in range(count - 1, 0, -1):
        back = core.g(_mini_card("#FFFFFF"), _stripe(fill))
        back.set("transform", core.rotate(-15 * i, CARD_W * 0.9, CARD_H * 1.05))
        parts.append(back)

    parts.append(_mini_card("#FFFFFF"))
    parts.append(_stripe(fill))
    size = CARD_H * 0.52
    digit = str(count)
    parts.append(
        core.el(
            "text",
            x=CARD_W / 2,
            y=CARD_H * 0.30
            + (CARD_H * 0.70 + size * measurer.metrics.cap_height) / 2
            - size * 0.1,
            text=digit,
            font_family=font.stack,
            font_weight=font.weight,
            font_size=size,
            text_anchor="middle",
            fill="#000000",
        )
    )
    group = core.g(*parts)
    if scale != 1.0:
        group.set("transform", f"scale({core.fmt(scale)})")
    return group
