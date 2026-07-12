"""Shared card chrome: bleed, body, frames, footer.

Layer order (bottom to top) for every card:
  1. bleed rect (fills the full 732x1101 canvas so the print bleeds cleanly)
  2. card body: rounded rect at the cut line
  3. per-family background (guilloche field / panel)
  4. per-family chrome (thin frame or ornate band)
  5. content
  6. corner badges
  7. footer
"""

import xml.etree.ElementTree as ET

from ...geometry import BLEED, CUT, SAFE, Box
from ...models.deck import Deck
from ...tokens import Tokens, load_tokens
from ..core import SVGDocument, el, rect

# The thin black frame on property/wildcard cards sits just inside the safe area.
FRAME_INSET = 10  # from safe-area edge
FRAME_STROKE = 3
FRAME_RADIUS = 14


def new_document(bleed_fill: str = "#FFFFFF") -> SVGDocument:
    doc = SVGDocument()
    doc.add(rect(BLEED, fill=bleed_fill))
    return doc


def card_body(tokens: Tokens, fill: str = "#FFFFFF") -> ET.Element:
    """Draw a rounded rectangle at the cut line."""
    return rect(CUT, rx=tokens.corner_radius, ry=tokens.corner_radius, fill=fill)


def frame_box() -> Box:
    return SAFE.inset(FRAME_INSET)


def thin_frame(stroke: str = "#000000") -> ET.Element:
    """Draw the thin rounded-rectangle rule used on property and wildcard cards."""
    return rect(
        frame_box(),
        rx=FRAME_RADIUS,
        ry=FRAME_RADIUS,
        fill="none",
        stroke=stroke,
        stroke_width=FRAME_STROKE,
    )


def footer(deck: Deck | None, tokens: Tokens) -> ET.Element | None:
    """Footer text zone above the bottom frame edge; empty text -> no element."""
    text = getattr(getattr(deck, "config", None), "footer_text", "") or ""
    if not text:
        return None
    fb = frame_box()
    font = tokens.font("body")
    return el(
        "text",
        x=fb.cx,
        y=fb.y2 - 14,
        text=text,
        font_family=font.stack,
        font_size=tokens.size("footer"),
        text_anchor="middle",
        fill="#000000",
    )


def blank_card(deck: Deck | None = None) -> SVGDocument:
    """Chrome-only card used by the M0 smoke test and as a layout reference."""
    tokens = load_tokens()
    doc = new_document()
    doc.add(card_body(tokens))
    doc.add(thin_frame())
    f = footer(deck, tokens) if deck is not None else None
    if f is not None:
        doc.add(f)
    return doc
