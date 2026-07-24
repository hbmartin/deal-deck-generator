"""Money card: tinted guilloché field, ornate band, central denomination."""

from ...geometry import CUT, Box
from ...models import MoneyCard
from ...models.deck import Deck
from ...tokens import Tokens, mix_hex
from .. import core
from ..components.badge import value_badge
from ..components.border_band import border_band
from ..components.guilloche import (
    agave_medallion,
    rosette,
    sunburst_medallion,
    texture_field,
)
from ..components.m_glyph import money_amount
from . import register
from .base import card_body, footer, new_document

FIELD_INSET = 9
FIELD_RADIUS = 26

CIRCLE_CX = 366
CIRCLE_CY = 540
CIRCLE_R = 200
CIRCLE_RING = 7

BADGE_POS = (132, 132)  # disc kept fully inside the safe area; bottom-right is the twin


@register("money")
def build_money(card: MoneyCard, deck: Deck, tokens: Tokens) -> core.SVGDocument:
    tint = tokens.value_tint(card.denomination)
    field_color = tint["field"]
    line_color = tint["line"]
    dark = mix_hex(line_color, "#000000", 0.55)

    doc = new_document()
    doc.add(card_body(tokens))

    field = CUT.inset(FIELD_INSET)
    doc.add(rect_field(field, field_color))

    # The active theme selects the field texture and medallion treatment.
    doc.add(
        texture_field(
            doc,
            field,
            stroke=line_color,
            style=tokens.ornament.field_pattern,
        )
    )
    match tokens.ornament.money_medallion:
        case "epitrochoid":
            doc.add(
                rosette(
                    CIRCLE_CX,
                    CIRCLE_CY,
                    CIRCLE_R * 1.32,
                    stroke=line_color,
                    variant=0,
                )
            )
            doc.add(
                rosette(
                    CIRCLE_CX,
                    CIRCLE_CY,
                    CIRCLE_R * 0.82,
                    stroke=line_color,
                    variant=1,
                )
            )
        case "agave":
            doc.add(
                agave_medallion(
                    doc,
                    CIRCLE_CX,
                    CIRCLE_CY,
                    CIRCLE_R * 1.34,
                    stroke=line_color,
                )
            )
        case "sunburst":
            doc.add(
                sunburst_medallion(
                    doc,
                    CIRCLE_CX,
                    CIRCLE_CY,
                    CIRCLE_R * 1.34,
                    stroke=line_color,
                )
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
    doc.add(
        border_band(
            doc,
            field.inset(40),
            stroke=dark,
            corner_style=tokens.ornament.border_corner,
        )
    )
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
