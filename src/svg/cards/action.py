"""Action card: tinted chassis, ACTION CARD header, title circle, description."""

from ...models import ActionCard, Card
from ...models.deck import Deck
from ...text.richtext import measure_rich_height, rich_lines
from ...tokens import Tokens
from .. import core
from ..components.badge import value_badge
from ..components.circle_title import circle_title
from . import register
from .base import card_body, footer, new_document
from .chassis import tinted_chassis

HEADER_BASELINE = 262
CIRCLE_CX = 366
CIRCLE_CY = 520
CIRCLE_R = 195
DESC_TOP = 778
DESC_BOTTOM = 985  # keep rules text clear of the footer and bottom badge
BADGE_POS = (132, 132)  # disc kept fully inside the safe area (corner 66 + radius)


def action_chassis_content(
    doc: core.SVGDocument,
    tokens: Tokens,
    card: Card,
    tint: dict[str, str],
    title_icon: str | None = None,
) -> None:
    """Header + circle + description + badges shared by action/rent cards."""
    value = card.require_value()
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
        circle_title(
            tokens, CIRCLE_CX, CIRCLE_CY, CIRCLE_R, card.title, icon=title_icon
        )
    )

    baseline = DESC_TOP
    if card.description:
        # Reserve vertical room for the fine print, then shrink the description
        # (only if needed) so the whole block clears the footer. Base-game cards
        # are short and never shrink, so their output is unchanged.
        reserve = sum(
            measure_rich_height(tokens, line, tokens.size("body_small"), 400) + 2
            for line in card.fine_print
        )
        desc_max_h = max(DESC_BOTTOM - DESC_TOP - reserve, 60)
        block, baseline = rich_lines(
            doc,
            tokens,
            card.description,
            cx=366,
            y=baseline,
            size=tokens.size("body"),
            max_w=372,
            max_h=desc_max_h,
            min_size=20,
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
        value,
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
        value,
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


@register("action")
def build_action(card: ActionCard, deck: Deck, tokens: Tokens) -> core.SVGDocument:
    value = card.require_value()
    tint = tokens.value_tint(value)

    doc = new_document()
    doc.add(card_body(tokens))
    tinted_chassis(doc, tokens, tint)
    action_chassis_content(doc, tokens, card, tint, title_icon=card.icon)

    f = footer(deck, tokens)
    if f is not None:
        doc.add(f)
    return doc
