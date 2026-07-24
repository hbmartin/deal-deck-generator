"""Deterministic, theme-aware card-back SVG composition."""

import math

from ..geometry import CUT
from ..models.deck import Deck
from ..text.measure import get_measurer
from ..tokens import Tokens, load_tokens, mix_hex
from . import core
from .cards.base import card_body, new_document
from .components.border_band import border_band
from .components.guilloche import (
    agave_medallion,
    rosette,
    sunburst_medallion,
    texture_field,
)

FIELD_INSET = 9
FIELD_RADIUS = 26
CX = 366
CY = 550.5
ORNAMENT_RADIUS = 230
ACCENT_OUTER_RADIUS = 218
ACCENT_INNER_RADIUS = 190
INNER_DISC_RADIUS = 190
TITLE_MAX_WIDTH = 300
TITLE_MIN_SIZE = 28
TITLE_BASELINE_OFFSET = 28
ACCENT_GAP_DEGREES = 1.4


def _annulus_segment(  # noqa: PLR0913
    cx: float,
    cy: float,
    outer_radius: float,
    inner_radius: float,
    start_angle: float,
    end_angle: float,
) -> str:
    """Return one clockwise annulus segment, with zero degrees at 12 o'clock."""

    def point(radius: float, angle: float) -> str:
        radians = math.radians(angle - 90)
        x = cx + radius * math.cos(radians)
        y = cy + radius * math.sin(radians)
        return f"{core.fmt(x)} {core.fmt(y)}"

    large_arc = 1 if (end_angle - start_angle) % 360 > 180 else 0
    return (
        f"M {point(outer_radius, start_angle)} "
        f"A {core.fmt(outer_radius)} {core.fmt(outer_radius)} "
        f"0 {large_arc} 1 {point(outer_radius, end_angle)} "
        f"L {point(inner_radius, end_angle)} "
        f"A {core.fmt(inner_radius)} {core.fmt(inner_radius)} "
        f"0 {large_arc} 0 {point(inner_radius, start_angle)} Z"
    )


def _resolved_background(tokens: Tokens) -> dict[str, str]:
    style = tokens.card_back
    if len(style.accent_order) != 10 or len(set(style.accent_order)) != 10:
        raise ValueError("card-back accent_order must contain 10 unique colors")
    try:
        background = tokens.property_color(style.background_property)
        for color in style.accent_order:
            tokens.property_color(color)
    except KeyError as error:
        message = f"unknown card-back property color: {error.args[0]}"
        raise ValueError(message) from error
    return background


def _accent_ring(tokens: Tokens, gap_fill: str) -> core.ET.Element:
    """Draw all ten theme colors twice so opposite segments always match."""
    colors = tokens.card_back.accent_order * 2
    step = 360 / len(colors)
    parts = [core.circle(CX, CY, ACCENT_OUTER_RADIUS, fill=gap_fill)]
    for index, color in enumerate(colors):
        start = index * step + ACCENT_GAP_DEGREES / 2
        end = (index + 1) * step - ACCENT_GAP_DEGREES / 2
        parts.append(
            core.path(
                _annulus_segment(
                    CX,
                    CY,
                    ACCENT_OUTER_RADIUS,
                    ACCENT_INNER_RADIUS,
                    start,
                    end,
                ),
                fill=tokens.property_color(color)["fill"],
            )
        )
    return core.g(*parts, data_role="card-back-accent-ring")


def _fit_title(tokens: Tokens, title: str) -> float:
    font = tokens.font("condensed_heavy")
    measurer = get_measurer(font.measure_path)
    configured_size = tokens.size("card_back_title")
    configured_width = measurer.advance(title, configured_size)
    size = min(configured_size, configured_size * TITLE_MAX_WIDTH / configured_width)
    if size < TITLE_MIN_SIZE:
        raise ValueError(
            f"card-back title {title!r} cannot fit within {TITLE_MAX_WIDTH}px"
        )
    return size


def _title_pair(tokens: Tokens, title: str, ink: str) -> core.ET.Element:
    font = tokens.font("condensed_heavy")
    size = _fit_title(tokens, title)
    baseline = CY - TITLE_BASELINE_OFFSET
    attributes = {
        "x": CX,
        "y": baseline,
        "text": title,
        "font_family": font.stack,
        "font_weight": font.weight,
        "font_size": size,
        "text_anchor": "middle",
        "fill": ink,
        "letter_spacing": 1,
    }
    upright = core.el("text", **attributes, data_role="card-back-title")
    opposite = core.el(
        "text",
        **attributes,
        data_role="card-back-title-opposite",
        transform=core.rotate(180, CX, CY),
    )
    return core.g(upright, opposite)


def build_card_back(deck: Deck, tokens: Tokens | None = None) -> core.SVGDocument:
    """Build the common card back for a deck using its resolved theme tokens."""
    tokens = tokens or load_tokens()
    background = _resolved_background(tokens)
    field_color = background["fill"]
    ink = background["text"]
    line_color = mix_hex(field_color, ink, 0.62)
    inner_fill = mix_hex(field_color, ink, 0.08)

    doc = new_document(bleed_fill=field_color)
    doc.add(card_body(tokens, fill=field_color))

    field = CUT.inset(FIELD_INSET)
    doc.add(
        core.rect(
            field,
            rx=FIELD_RADIUS,
            ry=FIELD_RADIUS,
            fill=field_color,
        )
    )
    doc.add(
        texture_field(
            doc,
            field,
            stroke=line_color,
            style=tokens.ornament.field_pattern,
            key="card-back",
        )
    )

    doc.add(
        core.rect(
            field.inset(10),
            fill="none",
            stroke=ink,
            stroke_width=2.5,
            rx=FIELD_RADIUS - 8,
        )
    )
    doc.add(
        border_band(
            doc,
            field.inset(40),
            stroke=ink,
            key="card-back",
            corner_style=tokens.ornament.border_corner,
        )
    )
    doc.add(core.rect(field.inset(64), fill="none", stroke=ink, stroke_width=2.5))
    doc.add(core.rect(field.inset(71), fill="none", stroke=ink, stroke_width=1.5))

    match tokens.ornament.money_medallion:
        case "epitrochoid":
            doc.add(
                rosette(
                    CX,
                    CY,
                    ORNAMENT_RADIUS,
                    stroke=line_color,
                    stroke_width=1.1,
                )
            )
        case "agave":
            doc.add(
                agave_medallion(
                    doc,
                    CX,
                    CY,
                    ORNAMENT_RADIUS,
                    stroke=line_color,
                    key="card-back",
                )
            )
        case "sunburst":
            doc.add(
                sunburst_medallion(
                    doc,
                    CX,
                    CY,
                    ORNAMENT_RADIUS,
                    stroke=line_color,
                    key="card-back",
                )
            )

    doc.add(
        core.circle(
            CX,
            CY,
            ORNAMENT_RADIUS,
            fill="none",
            stroke=line_color,
            stroke_width=2,
        )
    )
    doc.add(_accent_ring(tokens, ink))
    doc.add(
        core.circle(
            CX,
            CY,
            INNER_DISC_RADIUS,
            fill=inner_fill,
            stroke=ink,
            stroke_width=4,
        )
    )
    doc.add(
        core.line(
            CX - 118,
            CY,
            CX + 118,
            CY,
            stroke=ink,
            stroke_width=2,
            data_role="card-back-title-divider",
        )
    )
    doc.add(_title_pair(tokens, deck.config.card_back.title, ink))
    return doc
