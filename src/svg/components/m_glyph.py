"""The Monopoly money glyph: an M with a double horizontal strikethrough,
followed by an amount digit and a small trailing M, e.g. (M)3m.

The struck M is pure vector geometry (no font dependence). Digits and the
small trailing M use the condensed heavy face so they match card titles.
"""

from ...svg import core
from ...tokens import Tokens
from ...text.measure import get_measurer

# Struck-M design box: 100 units tall, GLYPH_W wide, drawn around origin top-left.
# The letter is drawn upright, then slanted with a skew; SLANT is how far the
# top edge shifts right (100 * tan(SLANT_DEG)), keeping the baseline anchored.
GLYPH_W = 88
SLANT_DEG = 12
SLANT = 21.3
GLYPH_ADV = GLYPH_W + SLANT  # advance width of the slanted glyph
_BAR = 8.5  # height of each strike bar
_BAR_OVERHANG = 14  # strikes protrude equally past the letter on both sides

DEF_ID = "m-glyph"


def ensure_glyph(doc: core.SVGDocument) -> str:
    """Register the unit struck-M (100 units tall) in <defs>."""
    if doc.has_def(DEF_ID):
        return DEF_ID
    w = GLYPH_W
    # Filled M outline: stems 17 wide, middle vertex dips to ~70.
    letter = core.path(
        f"M 0 100 L 0 0 L 20 0 L {w / 2} 50 L {w - 20} 0 L {w} 0 L {w} 100 "
        f"L {w - 17} 100 L {w - 17} 25 L {w / 2 + 7} 72 L {w / 2 - 7} 72 "
        f"L 17 25 L 17 100 Z",
        fill="currentColor",
    )
    strikes = [
        core.rect(
            None,
            x=-_BAR_OVERHANG,
            y=y - _BAR / 2,
            width=w + 2 * _BAR_OVERHANG,
            height=_BAR,
            fill="currentColor",
        )
        for y in (38, 60)
    ]
    # Oblique lean: top shifts right, baseline stays put. The strikes skew
    # with the letter so their overhang tracks the slanted stems.
    slanted = core.g(
        letter,
        *strikes,
        transform=f"{core.translate(SLANT, 0)} skewX({-SLANT_DEG})",
    )
    doc.add_def(DEF_ID, core.g(slanted))
    return DEF_ID


def money_amount(
    doc: core.SVGDocument,
    tokens: Tokens,
    value: int,
    size: float,
    color: str = "#000000",
    small_m: bool = True,
):
    """Build the amount group anchored at (0, 0) = left edge, baseline.

    Returns (group_element, total_width).
    """
    ensure_glyph(doc)
    font = tokens.font("condensed_heavy")
    measurer = get_measurer(font.measure_path)

    digits = str(value)
    digit_w = measurer.advance(digits, size)
    small_size = size * 0.44
    small_w = measurer.advance("M", small_size) if small_m else 0.0

    glyph_h = size * 0.82  # the struck M runs slightly shorter than the digits
    glyph_w = GLYPH_ADV / 100 * glyph_h
    gap = size * 0.09

    children = [
        core.use(
            DEF_ID,
            transform=f"{core.translate(0, -glyph_h)} scale({core.fmt(glyph_h / 100)})",
        ),
        core.el(
            "text",
            x=glyph_w + gap,
            y=0,
            text=digits,
            font_family=font.stack,
            font_weight=font.weight,
            font_size=size,
            fill=color,
        ),
    ]
    total = glyph_w + gap + digit_w
    if small_m:
        children.append(
            core.el(
                "text",
                x=total + gap,
                y=0,
                text="M",
                font_family=font.stack,
                font_weight=font.weight,
                font_size=small_size,
                fill=color,
            )
        )
        total += gap + small_w

    group = core.g(*children, color=color)
    return group, total
