"""Action-card center circle: white disc, heavy ring, title text and/or icon."""

from ...svg import core
from ...text.measure import get_measurer
from ...tokens import Tokens
from .icons import cake, go_arrow, hotel, house

RING_W = 8

# icon -> (vertical arrangement, icon height, width/height ratio)
_ICON_SPECS = {
    "house": ("above", 120, 1.25),
    "hotel": ("above", 120, 1.45),
    "cake": ("below", 110, 1.15),
    "go_arrow": ("below", 92, 2.6),
}

_ICON_FACTORIES = {
    "house": house,
    "hotel": hotel,
    "cake": cake,
    "go_arrow": go_arrow,
}


def _title_lines(title: str) -> list[str]:
    """Split circle titles as printed: two balanced lines when multi-word."""
    words = title.upper().split()
    if len(words) < 2:
        return words
    if len(words) == 2:
        return [words[0], words[1]]
    # 3+ words: break before the last two words ("IT'S MY / BIRTHDAY" is the
    # exception handled by balance: minimize width difference).
    _, lines = min(
        (
            (abs(len(first) - len(second)), [first, second])
            for i in range(1, len(words))
            if (first := " ".join(words[:i])) and (second := " ".join(words[i:]))
        ),
        key=lambda candidate: candidate[0],
    )
    return lines


def circle_title(  # noqa: PLR0913
    tokens: Tokens,
    cx: float,
    cy: float,
    r: float,
    title: str,
    icon: str | None = None,
) -> core.ET.Element:
    font = tokens.font("condensed_heavy")
    measurer = get_measurer(font.measure_path)
    base_size = tokens.size("circle_title")

    lines = _title_lines(title)
    max_w = r * 1.62
    sizes = []
    for ln in lines:
        adv = measurer.advance(ln, base_size)
        sizes.append(base_size if adv <= max_w else base_size * max_w / adv)
    size = min(sizes)
    m = measurer.metrics
    line_adv = size * 1.06
    text_h = (len(lines) - 1) * line_adv + size * m.cap_height

    parts = [
        core.circle(cx, cy, r, fill="#FFFFFF"),
        core.circle(cx, cy, r, fill="none", stroke="#000000", stroke_width=RING_W),
    ]

    icon_el = None
    icon_h = 0.0
    gap = 0.0
    arrangement = None
    ratio = 0.0
    if icon:
        arrangement, icon_h, ratio = _ICON_SPECS[icon]
        icon_el = _ICON_FACTORIES[icon](icon_h)
        gap = size * 0.28
    total_h = text_h + (icon_h + gap if icon else 0)
    top = cy - total_h / 2

    if icon_el is not None and arrangement == "above":
        icon_w = icon_h * ratio
        icon_el.set("transform", core.translate(cx - icon_w / 2, top))
        parts.append(icon_el)
        first_baseline = top + icon_h + gap + size * m.cap_height
    else:
        first_baseline = top + size * m.cap_height

    for i, ln in enumerate(lines):
        parts.append(
            core.el(
                "text",
                x=cx,
                y=first_baseline + i * line_adv,
                text=ln,
                font_family=font.stack,
                font_weight=font.weight,
                font_size=size,
                text_anchor="middle",
                fill="#000000",
                letter_spacing=0.5,
            )
        )

    if icon_el is not None and arrangement == "below":
        icon_w = icon_h * ratio
        icon_y = first_baseline + (len(lines) - 1) * line_adv + gap
        icon_el.set("transform", core.translate(cx - icon_w / 2, icon_y))
        parts.append(icon_el)

    return core.g(*parts)
