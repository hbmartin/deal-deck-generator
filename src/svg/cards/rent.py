"""Rent card: action chassis with a color bullseye instead of a title circle."""

from ...models import RentCard
from ...text.richtext import rich_lines
from ...tokens import load_tokens
from .. import core
from ..components.badge import value_badge
from ..components.color_ring import bullseye
from . import register
from .action import BADGE_POS, CIRCLE_CX, CIRCLE_CY, CIRCLE_R, HEADER_BASELINE
from .base import card_body, footer, new_document
from .chassis import tinted_chassis


# pyrefly: ignore [bad-argument-type]
@register("rent")
def build_rent(card: RentCard, deck) -> core.SVGDocument:
    tokens = load_tokens()
    # pyrefly: ignore [bad-argument-type]
    tint = tokens.value_tint(card.value)

    doc = new_document()
    doc.add(card_body(tokens))
    tinted_chassis(doc, tokens, tint)

    header_font = tokens.font("body_bold")
    doc.add(
        core.el(
            "text",
            x=366,
            y=HEADER_BASELINE,
            text="ACTION CARD",
            font_family=header_font.stack,
            font_weight=header_font.weight,
            font_size=tokens.size("action_header"),
            text_anchor="middle",
            fill="#000000",
            letter_spacing=2,
        )
    )

    doc.add(
        bullseye(
            doc,
            tokens,
            CIRCLE_CX,
            CIRCLE_CY,
            CIRCLE_R,
            colors=card.colors,
            is_wild=card.is_wild,
        )
    )

    baseline = 778
    if card.description:
        block, baseline = rich_lines(
            doc,
            tokens,
            card.description,
            cx=366,
            y=baseline,
            size=tokens.size("body"),
            max_w=372,
        )
        doc.add(block)
    for line in card.fine_print:
        block, baseline = rich_lines(
            doc,
            tokens,
            line,
            cx=366,
            y=baseline + 2,
            size=tokens.size("body_small"),
            max_w=400,
        )
        doc.add(block)

    ring = tokens.chrome("badge_ring_action")
    badge = value_badge(
        doc,
        tokens,
        card.value,  # pyrefly: ignore [bad-argument-type]
        ring_color=ring,
        fill=tint["field"],
        rotate_content=90,
        keyline="#000000",
    )
    badge.set("transform", core.translate(*BADGE_POS))
    doc.add(badge)
    badge2 = value_badge(
        doc,
        tokens,
        card.value,  # pyrefly: ignore [bad-argument-type]
        ring_color=ring,
        fill=tint["field"],
        rotate_content=90,
        keyline="#000000",
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
