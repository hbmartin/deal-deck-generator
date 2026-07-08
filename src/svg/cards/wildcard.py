"""Property wildcards.

Two-color: 180-degree rotationally symmetric halves. Each row band holds up
to two entries: the top color's fan/leader/value reading left-to-right on
the right, and the bottom color's rotated twin on the left. Rent tables are
derived from the property definitions at load time.

Multicolor: color stripe bars, title, Mr. Monopoly, description.
"""

from ...geometry import Box
from ...models import WildcardCard
from ...text.measure import get_measurer
from ...text.richtext import rich_lines
from ...tokens import load_tokens
from .. import core
from ..components import fan_icon as fan_mod
from ..components.badge import value_badge
from ..components.character import mr_monopoly
from ..components.fan_icon import fan_icon
from ..components.icons import bulb, faucet, train
from ..components.m_glyph import money_amount
from ..components.rent_table import DOT, DOT_GAP
from . import register
from .base import card_body, footer, frame_box, new_document, thin_frame

CX, CY = 366, 550.5

HEADER_BOX = Box(115, 132, 502, 190)
BADGE_POS = (138, 120)  # nested into the frame corner

FAN_SCALE = 0.82
BAND_PITCH = 96
ENTRY_FAN_X = 384  # front tile left edge (upright frame)
ENTRY_VALUE_X2 = 634  # value right edge
VALUE_SIZE = 42

STRIPE_COLORS = [
    "brown",
    "light_blue",
    "pink",
    "orange",
    "red",
    "yellow",
    "green",
    "dark_blue",
    "railroad",
    "utility",
]


def _leader(x1, x2, y):
    return core.line(
        x1,
        y,
        x2,
        y,
        stroke="#000000",
        stroke_width=DOT * 0.9,
        stroke_linecap="round",
        stroke_dasharray=f"0.1 {DOT_GAP * 0.9}",
    )


def _wildcard_header(doc, tokens, half: dict) -> core.ET.Element:
    colors = tokens.property_color(half["color"])
    box = HEADER_BOX
    font_small = tokens.font("body_bold")
    font_big = tokens.font("condensed_heavy")
    caption_font = tokens.font("body")

    parts = [core.rect(box, fill=colors["fill"], stroke="#000000", stroke_width=4)]
    text = colors["text"]
    parts.append(
        core.el(
            "text",
            x=box.cx,
            y=box.y + 52,
            text="PROPERTY",
            font_family=font_small.stack,
            font_weight=font_small.weight,
            font_size=34,
            text_anchor="middle",
            fill=text,
            letter_spacing=2,
        )
    )
    parts.append(
        core.el(
            "text",
            x=box.cx,
            y=box.y + 128,
            text="WILD CARD",
            font_family=font_big.stack,
            font_weight=font_big.weight,
            font_size=74,
            text_anchor="middle",
            fill=text,
            letter_spacing=1,
        )
    )
    parts.append(
        core.el(
            "text",
            x=box.cx,
            y=box.y + 168,
            text="(Use card either way up.)",
            font_family=caption_font.stack,
            font_size=26,
            text_anchor="middle",
            fill=text,
        )
    )

    icon = half.get("header_icon")
    if icon == "train":
        el = train(44, text)
        el.set("transform", core.translate(box.x + 24, box.y + 18))
        parts.append(el)
    elif icon in ("bulb", "faucet"):
        b = bulb(40)
        b.set("transform", core.translate(box.x2 - 60, box.y + 14))
        f = faucet(38, text)
        f.set("transform", core.translate(box.x2 - 66, box.y + 118))
        parts.append(b)
        parts.append(f)
    return core.g(*parts)


def _half_group(doc, tokens, half: dict, band_mids: list[float]) -> core.ET.Element:
    """One half in upright coordinates; caller rotates the second half."""
    measurer = get_measurer(tokens.font("body_bold").measure_path)
    parts = [_wildcard_header(doc, tokens, half)]

    rent_font = tokens.font("body")
    parts.append(
        core.el(
            "text",
            x=ENTRY_VALUE_X2,
            y=band_mids[0] - 74,
            text="RENT",
            font_family=rent_font.stack,
            font_size=tokens.size("rent_label") * 0.92,
            text_anchor="end",
            fill="#000000",
            letter_spacing=5,
        )
    )

    icon_h = fan_mod.CARD_H * FAN_SCALE
    icon_w = fan_mod.CARD_W * FAN_SCALE
    set_size = half["set_size"]
    for (n, rent), mid in zip(half["rent_values"], band_mids):
        icon = fan_icon(doc, tokens, n, half["color"])
        icon.set(
            "transform",
            f"{core.translate(ENTRY_FAN_X, mid - icon_h * 0.52)} "
            f"scale({core.fmt(FAN_SCALE)})",
        )
        parts.append(icon)

        amount, amount_w = money_amount(doc, tokens, rent, VALUE_SIZE)
        amount_x = ENTRY_VALUE_X2 - amount_w
        amount.set("transform", core.translate(amount_x, mid + VALUE_SIZE * 0.36))
        parts.append(amount)

        x1 = ENTRY_FAN_X + icon_w + 12
        x2 = amount_x - 12
        if n == set_size:
            label = "FULL SET"
            label_size = 24
            label_w = measurer.advance(label, label_size, letter_spacing=1)
            label_x = x2 - label_w - 16
            parts.append(_leader(x1, label_x - 8, mid))
            parts.append(
                core.el(
                    "text",
                    x=label_x,
                    y=mid + label_size * 0.36,
                    text=label,
                    font_family=tokens.font("body_bold").stack,
                    font_weight=tokens.font("body_bold").weight,
                    font_size=label_size,
                    fill="#000000",
                    letter_spacing=1,
                )
            )
        else:
            parts.append(_leader(x1, x2, mid))
    return core.g(*parts)


def _band_mids(count: int, total_bands: int) -> list[float]:
    offset = max(0, (total_bands - count) // 2)
    first = CY - (total_bands - 1) / 2 * BAND_PITCH
    return [first + (offset + j) * BAND_PITCH for j in range(count)]


def _build_two_color(card: WildcardCard, deck) -> core.SVGDocument:
    tokens = load_tokens()
    doc = new_document()
    doc.add(card_body(tokens, fill=tokens.chrome("property_body")))
    doc.add(thin_frame())

    top, bottom = card.metadata["halves"]
    bands = max(len(top["rent_values"]), len(bottom["rent_values"]))

    doc.add(_half_group(doc, tokens, top, _band_mids(len(top["rent_values"]), bands)))

    bottom_group = _half_group(
        doc, tokens, bottom, _band_mids(len(bottom["rent_values"]), bands)
    )
    bottom_group.set("transform", core.rotate(180, CX, CY))
    doc.add(bottom_group)

    ring = tokens.chrome("badge_ring_property")
    body = tokens.chrome("property_body")
    # pyrefly: ignore [bad-argument-type]
    badge = value_badge(doc, tokens, card.value, ring_color=ring, fill=body)
    badge.set("transform", core.translate(*BADGE_POS))
    doc.add(badge)
    # pyrefly: ignore [bad-argument-type]
    badge2 = value_badge(doc, tokens, card.value, ring_color=ring, fill=body)
    badge2.set(
        "transform",
        f"{core.translate(732 - BADGE_POS[0], 1101 - BADGE_POS[1])} {core.rotate(180)}",
    )
    doc.add(badge2)
    return doc


def _stripe_bar(tokens, y: float) -> core.ET.Element:
    box = frame_box()
    x = box.x + 18
    w = box.w - 36
    seg = w / len(STRIPE_COLORS)
    parts = []
    for i, key in enumerate(STRIPE_COLORS):
        parts.append(
            core.rect(
                None,
                x=x + i * seg + 2,
                y=y,
                width=seg - 4,
                height=44,
                fill=tokens.property_color(key)["fill"],
            )
        )
    return core.g(*parts)


def _build_multicolor(card: WildcardCard, deck) -> core.SVGDocument:
    tokens = load_tokens()
    doc = new_document()
    doc.add(card_body(tokens, fill=tokens.chrome("property_body")))
    doc.add(thin_frame())

    font = tokens.font("condensed_heavy")
    doc.add(_stripe_bar(tokens, 140))
    doc.add(
        core.el(
            "text",
            x=CX,
            y=262,
            text="PROPERTY WILD CARD",
            font_family=font.stack,
            font_weight=font.weight,
            font_size=56,
            text_anchor="middle",
            fill="#000000",
        )
    )
    doc.add(_stripe_bar(tokens, 292))

    figure = mr_monopoly(420)
    figure.set("transform", core.translate(CX - 0.78 * 420 / 2, 380))
    doc.add(figure)

    baseline = 880
    if card.description:
        block, baseline = rich_lines(
            doc,
            tokens,
            card.description,
            cx=CX,
            y=baseline,
            size=tokens.size("body"),
            max_w=430,
        )
        doc.add(block)

    doc.add(_stripe_bar(tokens, 968))
    return doc


# pyrefly: ignore [bad-argument-type]
@register("wildcard")
def build_wildcard(card: WildcardCard, deck) -> core.SVGDocument:
    if card.is_multicolor:
        doc = _build_multicolor(card, deck)
    else:
        doc = _build_two_color(card, deck)
    tokens = load_tokens()
    f = footer(deck, tokens)
    if f is not None:
        doc.add(f)
    return doc
