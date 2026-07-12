"""Property card header bar: color band + centered name + optional icons."""

from ...geometry import Box
from ...svg import core
from ...text.measure import get_measurer
from ...tokens import Tokens
from .icons import bulb, faucet, train

HEADER_STROKE = 4


def split_name(name: str, explicit: list[str] | None = None) -> list[str]:
    """Match the printed cards: the last word drops to its own line
    ("KENTUCKY / AVENUE", "B. & O. / RAILROAD"); one-word names stay single.
    Cards typeset differently on the real deck pass explicit lines.
    """
    if explicit:
        return [ln.upper() for ln in explicit]
    words = name.upper().split()
    if len(words) < 2:
        return words
    return [" ".join(words[:-1]), words[-1]]


def property_header(  # noqa: C901, PLR0913
    tokens: Tokens,
    box: Box,
    name: str,
    color_key: str,
    header_icon: str | None = None,
    explicit_lines: list[str] | None = None,
    badge_clear_x: float | None = None,
) -> core.ET.Element:
    colors = tokens.property_color(color_key)
    font = tokens.font("condensed")
    measurer = get_measurer(font.measure_path)

    parts = [
        core.rect(
            box,
            fill=colors["fill"],
            stroke="#000000",
            stroke_width=HEADER_STROKE,
        )
    ]

    icon_zone = 0.0
    if header_icon:
        icon_h = box.h * 0.42
        if header_icon == "train":
            left, right = train(icon_h, colors["text"]), train(icon_h, colors["text"])
            icon_w = icon_h * 1.5
        elif header_icon == "faucet":
            left, right = faucet(icon_h, colors["text"]), faucet(icon_h, colors["text"])
            icon_w = icon_h * 1.1
        else:
            left, right = bulb(icon_h), bulb(icon_h)
            icon_w = icon_h * 0.9
        icon_inset = box.h * 0.22
        icon_zone = icon_inset + icon_w + 16
        icon_y = box.cy - icon_h / 2
        left.set("transform", core.translate(box.x + icon_inset, icon_y))
        if header_icon == "train":
            # mirror the right-side locomotive so the pair faces outward
            right.set(
                "transform",
                f"{core.translate(box.x2 - icon_inset, icon_y)} scale(-1 1)",
            )
        else:
            right.set(
                "transform",
                core.translate(box.x2 - icon_inset - icon_w, icon_y),
            )
        parts += [left, right]

    lines = split_name(name, explicit_lines)
    base_size = tokens.size("property_name")
    max_w = box.w - 2 * max(icon_zone, box.h * 0.28)
    line_height = 1.08
    m = measurer.metrics

    right_edge = box.x2 - box.h * 0.22
    sizes = []
    for ln in lines:
        adv = measurer.advance(ln, base_size, letter_spacing=0.5)
        fitted = base_size if adv <= max_w else base_size * max_w / adv
        if badge_clear_x is not None:
            # If the centered line would slide under the badge, it must fit
            # the narrower zone right of the badge instead.
            if (
                box.cx - measurer.advance(ln, fitted, letter_spacing=0.5) / 2
                < badge_clear_x
            ):
                zone_w = right_edge - badge_clear_x - 6
                if adv > zone_w:
                    fitted = min(fitted, base_size * zone_w / adv)
        sizes.append(fitted)
    size = min(sizes)

    block_h = (len(lines) - 1) * size * line_height + size * m.cap_height
    first_baseline = box.cy - block_h / 2 + size * m.cap_height
    for i, ln in enumerate(lines):
        # A long line whose left edge would slide under the corner badge is
        # centered in the space right of the badge instead (as printed).
        x = box.cx
        adv = measurer.advance(ln, size, letter_spacing=0.5)
        if badge_clear_x is not None and box.cx - adv / 2 < badge_clear_x:
            x = (badge_clear_x + right_edge) / 2
        parts.append(
            core.el(
                "text",
                x=x,
                y=first_baseline + i * size * line_height,
                text=ln,
                font_family=font.stack,
                font_weight=font.weight,
                font_size=size,
                text_anchor="middle",
                fill=colors["text"],
                letter_spacing=0.5,
            )
        )
    return core.g(*parts)
