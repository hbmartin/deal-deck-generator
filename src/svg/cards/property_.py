"""Property card: color header, rent table, corner badge."""

from ...geometry import Box
from ...models import PropertyCard
from ...models.deck import Deck
from ...tokens import Tokens
from .. import core
from ..components.badge import value_badge
from ..components.header_bar import property_header
from ..components.rent_table import caption_and_rent_label, rent_rows
from . import register
from .base import card_body, footer, new_document, thin_frame


@register("property")
def build_property(card: PropertyCard, deck: Deck, tokens: Tokens) -> core.SVGDocument:
    value = card.require_value()
    doc = new_document()
    doc.add(card_body(tokens, fill=tokens.chrome("property_body")))
    doc.add(thin_frame())

    # Positions below are derived from measurements of the reference photos,
    # expressed in full-bleed pixel coordinates.
    header_box = Box(115, 146, 502, 140)
    doc.add(
        property_header(
            tokens,
            header_box,
            card.title,
            card.color,
            card.header_icon,
            explicit_lines=card.name_lines,
            badge_clear_x=138 + 62 + 12,  # badge center x + radius + gap
        )
    )

    # Four-row tables (railroads) start higher to fit inside the frame.
    tall = len(card.rent_values) >= 4
    caption_box = Box(140, 365 if tall else 410, 490, 90)
    doc.add(caption_and_rent_label(tokens, caption_box))

    rows_box = Box(140, 491 if tall else 562, 490, 0)  # rows_box.y = first row mid
    doc.add(
        rent_rows(doc, tokens, rows_box, card.rent_values, card.color, card.set_size)
    )

    # Badge nests into the frame corner, overlapping frame and header edge.
    badge = value_badge(
        doc,
        tokens,
        value,
        tokens.chrome("badge_ring_property"),
        fill=tokens.chrome("property_body"),
    )
    badge.set("transform", core.translate(132, 132))
    doc.add(badge)

    f = footer(deck, tokens)
    if f is not None:
        doc.add(f)
    return doc
