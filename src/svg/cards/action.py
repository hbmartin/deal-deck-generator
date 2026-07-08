"""Action card: tinted chassis, ACTION CARD header, title circle, description."""

from ...models import ActionCard
from ...tokens import load_tokens
from .. import core
from ..components.badge import value_badge
from ..components.circle_title import circle_title
from ...text.richtext import rich_lines
from . import register
from .base import card_body, footer, new_document
from .chassis import tinted_chassis

HEADER_BASELINE = 262
CIRCLE_CX = 366
CIRCLE_CY = 520
CIRCLE_R = 195
DESC_TOP = 778
BADGE_POS = (108, 114)  # centered on the border band's corner square


def action_chassis_content(doc, tokens, card, tint, title_icon=None):
    """Header + circle + description + badges shared by action/rent cards."""
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
            doc, tokens, CIRCLE_CX, CIRCLE_CY, CIRCLE_R, card.title, icon=title_icon
        )
    )

    baseline = DESC_TOP
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
        card.value,
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
        card.value,
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


# pyrefly: ignore [bad-argument-type]
@register("action")
def build_action(card: ActionCard, deck) -> core.SVGDocument:
    tokens = load_tokens()
    # pyrefly: ignore [bad-argument-type]
    tint = tokens.value_tint(card.value)

    doc = new_document()
    doc.add(card_body(tokens))
    tinted_chassis(doc, tokens, tint)
    action_chassis_content(doc, tokens, card, tint, title_icon=card.icon)

    f = footer(deck, tokens)
    if f is not None:
        doc.add(f)
    return doc
