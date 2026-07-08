"""Money card: tinted guilloché field, ornate band, central denomination."""

from ...geometry import CUT, Box
from ...models import MoneyCard
from ...tokens import load_tokens, mix_hex
from .. import core
from ..components.badge import value_badge
from ..components.border_band import border_band
from ..components.guilloche import rosette, wave_field
from ..components.m_glyph import money_amount
from . import register
from .base import card_body, footer, new_document

FIELD_INSET = 9
FIELD_RADIUS = 26

CIRCLE_CX = 366
CIRCLE_CY = 540
CIRCLE_R = 200
CIRCLE_RING = 7

BADGE_POS = (108, 114)  # centered on the band corner; bottom-right is the twin


@register("money")
def build_money(card: MoneyCard, deck) -> core.SVGDocument:
    tokens = load_tokens()
    tint = tokens.value_tint(card.denomination)
    field_color = tint["field"]
    line_color = tint["line"]
    dark = mix_hex(line_color, "#000000", 0.55)

    doc = new_document()
    doc.add(card_body(tokens))

    field = CUT.inset(FIELD_INSET)
    doc.add(rect_field(field, field_color))

    # Engraved texture: woven wave mesh across the field plus a rosette
    # medallion behind the central circle.
    doc.add(wave_field(doc, field, stroke=line_color))
    doc.add(
        rosette(CIRCLE_CX, CIRCLE_CY, CIRCLE_R * 1.32, stroke=line_color, variant=0)
    )
    doc.add(
        rosette(CIRCLE_CX, CIRCLE_CY, CIRCLE_R * 0.82, stroke=line_color, variant=1)
    )

    # Chrome: outer pinstripe, motif band, inner double rule.
    doc.add(
        core.rect(
            field.inset(10),
            fill="none",
            stroke=dark,
            stroke_width=2.5,
            rx=FIELD_RADIUS - 8,
        )
    )
    doc.add(border_band(doc, field.inset(40), stroke=dark))
    doc.add(core.rect(field.inset(64), fill="none", stroke=dark, stroke_width=2.5))
    doc.add(core.rect(field.inset(71), fill="none", stroke=dark, stroke_width=1.5))

    # Central circle: solid field color (the engraving stops at the ring).
    doc.add(
        core.circle(
            CIRCLE_CX,
            CIRCLE_CY,
            CIRCLE_R,
            fill=field_color,
            stroke="#000000",
            stroke_width=CIRCLE_RING,
        )
    )
    # Central amount reads horizontally, sized to fit the circle.
    digit_size = 200.0
    amount, width = money_amount(doc, tokens, card.denomination, digit_size)
    max_w = CIRCLE_R * 2 * 0.86
    if width > max_w:
        digit_size *= max_w / width
        amount, width = money_amount(doc, tokens, card.denomination, digit_size)
    amount.set(
        "transform",
        core.translate(CIRCLE_CX - width / 2, CIRCLE_CY + digit_size * 0.36),
    )
    doc.add(amount)

    # Corner badges: solid field color, black ring, horizontal amount.
    badge = value_badge(
        doc,
        tokens,
        card.denomination,
        ring_color="#000000",
        fill=field_color,
    )
    badge.set("transform", core.translate(*BADGE_POS))
    doc.add(badge)
    badge2 = value_badge(
        doc,
        tokens,
        card.denomination,
        ring_color="#000000",
        fill=field_color,
    )
    badge2.set(
        "transform",
        f"{core.translate(732 - BADGE_POS[0], 1101 - BADGE_POS[1])} {core.rotate(180)}",
    )
    doc.add(badge2)

    f = footer(deck, tokens)
    if f is not None:
        doc.add(f)
    return doc


def rect_field(box: Box, fill: str) -> core.ET.Element:
    return core.rect(box, rx=FIELD_RADIUS, ry=FIELD_RADIUS, fill=fill)
