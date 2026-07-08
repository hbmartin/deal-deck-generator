"""The Monopoly money glyph: an M with a double horizontal strikethrough,
followed by an amount digit and a small trailing M, e.g. (M)3m.

The struck M is pure vector geometry (no font dependence). Digits and the
small trailing M use the condensed heavy face so they match card titles.
"""

from ...svg import core
from ...tokens import Tokens
from ...text.measure import get_measurer

# Struck-M design box: 100 units tall, GLYPH_W wide, drawn around origin top-left.
GLYPH_W = 88
_BAR = 8.5  # height of each strike bar
_BAR_OVERHANG_L = 14  # strikes protrude past the letter on the left...
_BAR_OVERHANG_R = 5  # ...and slightly on the right

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
            x=-_BAR_OVERHANG_L,
            y=y - _BAR / 2,
            width=w + _BAR_OVERHANG_L + _BAR_OVERHANG_R,
            height=_BAR,
            fill="currentColor",
        )
        for y in (38, 60)
    ]
    doc.add_def(DEF_ID, core.g(letter, *strikes))
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
    glyph_w = GLYPH_W / 100 * glyph_h
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
