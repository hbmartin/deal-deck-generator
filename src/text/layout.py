"""Line breaking and block placement for SVG <text> emission.

SVG 1.1 <text> has no wrapping, so lines are broken here with real font
metrics and emitted as one <text> element per line with explicit x/y.
"""

from dataclasses import dataclass

from ..geometry import Box
from .measure import TextMeasurer


class TextOverflowError(Exception):
    """Raised when text cannot fit its layout box even at min_size."""


@dataclass(frozen=True)
class PlacedLine:
    text: str
    x: float
    y: float  # baseline
    size: float


def wrap_line(
    measurer: TextMeasurer, text: str, size: float, max_w: float
) -> list[str]:
    """Greedy word wrap of a single logical line."""
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if measurer.advance(candidate, size) <= max_w:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def layout_block(
    measurer: TextMeasurer,
    text: str,
    box: Box,
    size: float,
    min_size: float | None = None,
    line_height: float = 1.25,
    halign: str = "center",
    valign: str = "middle",
) -> list[PlacedLine]:
    """Wrap `text` (honoring explicit newlines) into `box`.

    If the block overflows vertically or a single word overflows horizontally,
    the size steps down by 1px toward min_size; below that TextOverflowError.
    """
    if min_size is None:
        min_size = size

    current = size
    while True:
        lines: list[str] = []
        fits = True
        for logical in text.split("\n"):
            wrapped = wrap_line(measurer, logical, current, box.w)
            for ln in wrapped:
                if measurer.advance(ln, current) > box.w:
                    fits = False
            lines.extend(wrapped)
        block_h = (len(lines) - 1) * current * line_height + current
        if block_h > box.h:
            fits = False
        if fits:
            break
        if current <= min_size:
            raise TextOverflowError(
                f"text does not fit in {box.w:.0f}x{box.h:.0f} at >= {min_size}px: "
                f"{text[:60]!r}"
            )
        current -= 1

    m = measurer.metrics
    # Vertical placement uses cap-height centering for optical balance.
    advance = current * line_height
    first_cap_top_to_last_baseline = (len(lines) - 1) * advance + current * m.cap_height
    if valign == "top":
        first_baseline = box.y + current * m.cap_height
    elif valign == "bottom":
        first_baseline = box.y2 - (len(lines) - 1) * advance - current * m.descent
    else:
        first_baseline = (
            box.y
            + (box.h - first_cap_top_to_last_baseline) / 2
            + (current * m.cap_height)
        )

    placed = []
    for i, ln in enumerate(lines):
        if halign == "left":
            x = box.x
        elif halign == "right":
            x = box.x2
        else:
            x = box.cx
        placed.append(PlacedLine(ln, x, first_baseline + i * advance, current))
    return placed
