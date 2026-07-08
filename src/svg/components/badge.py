"""Corner value badge: solid circle matching the card background + ring +
money amount."""

from ...svg import core
from ...tokens import Tokens
from .m_glyph import money_amount

BADGE_R = 62
RING_W = 5


def value_badge(
    doc: core.SVGDocument,
    tokens: Tokens,
    value: int,
    ring_color: str,
    fill: str | None = "#FFFFFF",
    rotate_content: float = 0.0,
    keyline: str | None = None,
) -> core.ET.Element:
    """Badge group centered at (0, 0); caller translates into place.

    fill should be the card's background color behind the badge so the disc
    reads as un-textured background (None leaves the circle unfilled).
    rotate_content rotates the amount inside the circle (action-family
    badges read vertically on the printed cards). keyline adds the thin
    circle hugging the outside of the ring (black around the red rings).
    """
    amount_size = tokens.size("badge_value")
    amount, width = money_amount(doc, tokens, value, amount_size)
    # The amount fills most of the badge; wide amounts (10) shrink to fit.
    max_w = (BADGE_R - RING_W) * 2 * 0.84
    if width > max_w:
        amount_size *= max_w / width
        amount, width = money_amount(doc, tokens, value, amount_size)

    # Center the amount optically: baseline sits just below circle center.
    transform = ""
    if rotate_content:
        transform = f"{core.rotate(rotate_content)} "
    transform += core.translate(-width / 2, amount_size * 0.36)
    amount.set("transform", transform)

    parts = []
    if fill is not None:
        parts.append(core.circle(0, 0, BADGE_R, fill=fill))
    parts.append(
        core.circle(
            0,
            0,
            BADGE_R - RING_W / 2,
            fill="none",
            stroke=ring_color,
            stroke_width=RING_W,
        )
    )
    if keyline is not None:
        keyline_w = 2.5
        parts.append(
            core.circle(
                0,
                0,
                BADGE_R + keyline_w / 2,
                fill="none",
                stroke=keyline,
                stroke_width=keyline_w,
            )
        )
    parts.append(amount)
    return core.g(*parts)
