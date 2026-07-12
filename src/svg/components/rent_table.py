"""Property-card rent table: caption, RENT label, and icon/leader/value rows."""

from ...geometry import Box
from ...svg import core
from ...text.measure import get_measurer
from ...tokens import Tokens
from . import fan_icon as fan_mod
from .fan_icon import fan_icon
from .m_glyph import money_amount

ROW_PITCH = 140
ICON_SCALE = 1.15
DOT = 4.0  # leader dot diameter (stroke width, round caps)
DOT_GAP = 13.5


def caption_and_rent_label(tokens: Tokens, box: Box) -> core.ET.Element:
    """'(No. of properties owned in set)' at left, big RENT at right."""
    body = tokens.font("body")
    heavy = tokens.font("body")
    caption_size = tokens.size("caption")
    rent_size = tokens.size("rent_label")
    parts = []
    for i, line in enumerate(["(No. of properties", "owned in set)"]):
        parts.append(
            core.el(
                "text",
                x=box.x + box.w * 0.24,
                y=box.y + caption_size * (1.05 + i * 1.25),
                text=line,
                font_family=body.stack,
                font_size=caption_size,
                text_anchor="middle",
                fill="#000000",
            )
        )
    parts.append(
        core.el(
            "text",
            x=box.x2,
            y=box.y + rent_size * 0.95,
            text="RENT",
            font_family=heavy.stack,
            font_size=rent_size,
            text_anchor="end",
            fill="#000000",
            letter_spacing=6,
        )
    )
    return core.g(*parts)


def _leader(x1: float, x2: float, y: float) -> core.ET.Element:
    return core.line(
        x1,
        y,
        x2,
        y,
        stroke="#000000",
        stroke_width=DOT,
        stroke_linecap="round",
        stroke_dasharray=f"0.1 {DOT_GAP}",
    )


def rent_rows(  # noqa: PLR0913
    doc: core.SVGDocument,
    tokens: Tokens,
    box: Box,
    rent_values: list[tuple[int, int]],
    color_key: str,
    set_size: int,
) -> core.ET.Element:
    """Rows anchored at box.y; box.w spans icon column through value column."""
    value_size = tokens.size("rent_value")
    body = tokens.font("body_bold")
    measurer = get_measurer(body.measure_path)

    icon_w = fan_mod.CARD_W * ICON_SCALE
    icon_h = fan_mod.CARD_H * ICON_SCALE
    rows = []
    for i, (n, rent) in enumerate(rent_values):
        mid_y = box.y + i * ROW_PITCH
        row_top = mid_y - icon_h * 0.52
        # Fanned cards extend to the left of the front tile; anchor the tile
        # in a fixed column so digits align vertically.
        icon_x = box.x + box.w * 0.18
        icon = fan_icon(tokens, n, color_key)
        icon.set(
            "transform",
            f"{core.translate(icon_x, row_top)} scale({core.fmt(ICON_SCALE)})",
        )
        rows.append(icon)

        amount, amount_w = money_amount(doc, tokens, rent, value_size)
        amount_x = box.x2 - amount_w
        amount.set("transform", core.translate(amount_x, mid_y + value_size * 0.36))
        rows.append(amount)

        leader_x1 = icon_x + icon_w + 14
        leader_x2 = amount_x - 14
        if n == set_size:
            # ..FULL SET.. sits in the leader adjacent to the rent value
            label = "FULL SET"
            label_size = tokens.size("caption") * 1.15
            label_w = measurer.advance(label, label_size, letter_spacing=1)
            label_x = leader_x2 - label_w - 22
            rows.append(_leader(leader_x1, label_x - 10, mid_y))
            rows.append(
                core.el(
                    "text",
                    x=label_x,
                    y=mid_y + label_size * 0.36,
                    text=label,
                    font_family=body.stack,
                    font_weight=body.weight,
                    font_size=label_size,
                    fill="#000000",
                    letter_spacing=1,
                )
            )
            rows.append(_leader(label_x + label_w + 8, leader_x2, mid_y))
        else:
            rows.append(_leader(leader_x1, leader_x2, mid_y))
    return core.g(*rows)
