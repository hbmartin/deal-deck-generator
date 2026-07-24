"""Shared tinted chassis for the action-family cards (action/rent/money):
tinted field, theme-selected texture, outer pinstripe, ornate band, inner rules.
"""

from ...geometry import CUT, Box
from ...svg import core
from ...tokens import Tokens, mix_hex
from ..components.border_band import border_band
from ..components.guilloche import texture_field

FIELD_INSET = 9
FIELD_RADIUS = 26


def field_box() -> Box:
    return CUT.inset(FIELD_INSET)


def content_box() -> Box:
    """Area inside the inner double rule."""
    return field_box().inset(78)


def tinted_chassis(
    doc: core.SVGDocument,
    tokens: Tokens,
    tint: dict[str, str],
    texture_extras: list[core.ET.Element] | None = None,
) -> None:
    """Add field, texture, and chrome layers to the document in order.

    texture_extras render above the wave field but below the chrome
    (used for rosette medallions).
    """
    field = field_box()
    dark = mix_hex(tint["line"], "#000000", 0.55)

    doc.add(core.rect(field, rx=FIELD_RADIUS, ry=FIELD_RADIUS, fill=tint["field"]))
    doc.add(
        texture_field(
            doc,
            field,
            stroke=tint["line"],
            style=tokens.ornament.field_pattern,
        )
    )
    for extra in texture_extras or []:
        doc.add(extra)

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
