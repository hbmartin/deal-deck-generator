"""The money glyph: an M with a double horizontal strikethrough,
followed by an amount digit and a small trailing M, e.g. (M)3m.

The struck M is pure vector geometry (no font dependence). Digits and the
small trailing M use the condensed heavy face so they match card titles.
"""

from ...svg import core
from ...tokens import Tokens
from ...text.measure import get_measurer

# Struck-M design box: 100 units tall, GLYPH_W wide, drawn around origin top-left.
GLYPH_W = 88
GLYPH_ADV = GLYPH_W  # advance width
_BAR = 8.5  # height of each strike bar
_BAR_OVERHANG = 14  # strikes protrude equally past the letter on both sides

DEF_ID = "m-glyph"


def ensure_glyph(doc: core.SVGDocument) -> str:
    """Register the unit struck-M (100 units tall) in <defs>.

    The letter is a zigzag M — four angled strokes /\\/\\ with flat apex
    tops — not vertical stems, matching the printed glyph.
    """
    if doc.has_def(DEF_ID):
        return DEF_ID
    # Single closed contour, clockwise from the bottom-left outer corner.
    letter = core.path(
        "M 0 100 "
        "L 19 0 L 35 0 "  # left leg up to apex 1
        "L 44 55 "  # notch down between the apexes
        "L 53 0 L 69 0 "  # up to apex 2
        "L 88 100 L 71 100 "  # right leg down to the foot
        "L 56 16 "  # inner edge up under apex 2
        "L 44 84 "  # middle vertex bottom
        "L 32 16 "  # inner edge up under apex 1
        "L 17 100 Z",
        fill="currentColor",
    )
    strikes = [
        core.rect(
            None,
            x=-_BAR_OVERHANG,
            y=y - _BAR / 2,
            width=GLYPH_W + 2 * _BAR_OVERHANG,
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
