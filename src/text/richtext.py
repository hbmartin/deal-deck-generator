"""Rich text: description strings with inline {nM} money-glyph tokens.

parse() splits a string into word-level items; each item is either a plain
word or an inline money amount. Layout wraps items greedily and emits
centered lines mixing <text> runs with vector glyph groups.

rich_lines() optionally shrinks the type size to keep a block within a
vertical budget (`max_h`); with no budget it renders at the given size, so
existing callers are byte-for-byte unchanged.
"""

import re
from dataclasses import dataclass

from ..svg import core
from ..svg.components.m_glyph import GLYPH_ADV, money_amount
from ..tokens import Tokens
from .measure import TextMeasurer, get_measurer

_TOKEN = re.compile(r"\{(\d+)M\}")


@dataclass(frozen=True)
class Word:
    text: str


@dataclass(frozen=True)
class Money:
    value: int
    prefix: str = ""  # punctuation hugging the glyph, e.g. "(" or "."
    suffix: str = ""


def parse(text: str) -> list[Word | Money]:
    """Split on whitespace; a token containing {nM} becomes a Money item with
    any surrounding punctuation kept attached (no space inserted).
    """
    items: list[Word | Money] = []
    for tok in text.split():
        m = _TOKEN.search(tok)
        if m:
            items.append(
                Money(int(m.group(1)), prefix=tok[: m.start()], suffix=tok[m.end() :])
            )
        else:
            items.append(Word(tok))
    return items


def _money_width(measurer: TextMeasurer, value: int, size: float) -> float:
    glyph_w = GLYPH_ADV / 100 * (size * 0.82)
    digit_w = measurer.advance(str(value), size)
    small_w = measurer.advance("M", size * 0.44)
    return glyph_w + size * 0.09 * 2 + digit_w + small_w


def _item_width(
    item: Word | Money,
    size: float,
    measurer: TextMeasurer,
    heavy: TextMeasurer,
) -> float:
    if isinstance(item, Word):
        return measurer.advance(item.text, size)
    w = _money_width(heavy, item.value, size)
    if item.prefix:
        w += measurer.advance(item.prefix, size)
    if item.suffix:
        w += measurer.advance(item.suffix, size)
    return w


def _wrap_items(
    items: list[Word | Money],
    size: float,
    max_w: float,
    measurer: TextMeasurer,
    heavy: TextMeasurer,
) -> list[list[Word | Money]]:
    """Greedy word wrap of rich-text items at a given size."""
    lines: list[list[Word | Money]] = []
    current: list[Word | Money] = []
    current_w = 0.0
    space_w = measurer.advance(" ", size)
    for item in items:
        w = _item_width(item, size, measurer, heavy)
        add_w = w if not current else w + space_w
        if current and current_w + add_w > max_w:
            lines.append(current)
            current, current_w = [item], w
        else:
            current.append(item)
            current_w += add_w
    if current:
        lines.append(current)
    return lines


def measure_rich_height(  # noqa: PLR0913
    tokens: Tokens,
    text: str,
    size: float,
    max_w: float,
    font_role: str = "body",
    line_height: float = 1.3,
) -> float:
    """Vertical space a rich-text block would occupy at `size` (no emission)."""
    measurer = get_measurer(tokens.font(font_role).measure_path)
    heavy = get_measurer(tokens.font("condensed_heavy").measure_path)
    lines = _wrap_items(parse(text), size, max_w, measurer, heavy)
    return len(lines) * size * line_height


def rich_lines(  # noqa: C901, PLR0913
    doc: core.SVGDocument,
    tokens: Tokens,
    text: str,
    cx: float,
    y: float,
    size: float,
    max_w: float,
    font_role: str = "body",
    line_height: float = 1.3,
    color: str = "#000000",
    max_h: float | None = None,
    min_size: float | None = None,
) -> tuple[core.ET.Element, float]:
    """Wrap and emit centered rich-text lines starting at baseline `y`.

    When `max_h` is given, the type size steps down (toward `min_size`) until
    the block fits that height, clamping at `min_size` if it still overflows.
    Without `max_h` the text renders at `size` unchanged.

    Returns (group, next_baseline_y).
    """
    font = tokens.font(font_role)
    measurer = get_measurer(font.measure_path)
    heavy_measurer = get_measurer(tokens.font("condensed_heavy").measure_path)

    items = parse(text)
    if min_size is None:
        min_size = size
    while True:
        lines = _wrap_items(items, size, max_w, measurer, heavy_measurer)
        if max_h is None or size <= min_size:
            break
        if len(lines) * size * line_height <= max_h:
            break
        size -= 1

    space_w = measurer.advance(" ", size)

    parts = []
    baseline = y
    for line in lines:
        widths = [_item_width(i, size, measurer, heavy_measurer) for i in line]
        total = sum(widths) + space_w * (len(line) - 1)
        x = cx - total / 2
        run: list[str] = []
        run_x = x
        for item, w in zip(line, widths, strict=True):
            if isinstance(item, Word):
                run.append(item.text)
                x += w + space_w
            else:
                if run:
                    parts.append(
                        core.el(
                            "text",
                            x=run_x,
                            y=baseline,
                            text=" ".join(run),
                            font_family=font.stack,
                            font_weight=font.weight,
                            font_size=size,
                            fill=color,
                        )
                    )
                    run = []
                if item.prefix:
                    parts.append(
                        core.el(
                            "text",
                            x=x,
                            y=baseline,
                            text=item.prefix,
                            font_family=font.stack,
                            font_weight=font.weight,
                            font_size=size,
                            fill=color,
                        )
                    )
                    x += measurer.advance(item.prefix, size)
                amount, aw = money_amount(doc, tokens, item.value, size)
                amount.set("transform", core.translate(x, baseline))
                parts.append(amount)
                x += aw
                if item.suffix:
                    parts.append(
                        core.el(
                            "text",
                            x=x,
                            y=baseline,
                            text=item.suffix,
                            font_family=font.stack,
                            font_weight=font.weight,
                            font_size=size,
                            fill=color,
                        )
                    )
                    x += measurer.advance(item.suffix, size)
                x += space_w
                run_x = x
        if run:
            parts.append(
                core.el(
                    "text",
                    x=run_x,
                    y=baseline,
                    text=" ".join(run),
                    font_family=font.stack,
                    font_weight=font.weight,
                    font_size=size,
                    fill=color,
                )
            )
        baseline += size * line_height
    return core.g(*parts), baseline
