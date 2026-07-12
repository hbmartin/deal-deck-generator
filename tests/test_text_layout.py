"""Unit tests for deterministic text wrapping and placement."""

import pytest

from src.geometry import Box
from src.svg import core
from src.text.layout import TextOverflowError, layout_block, wrap_line
from src.text.measure import FontMetrics
from src.text.richtext import measure_rich_height, rich_lines
from src.tokens import load_tokens


class FixedWidthMeasurer:
    """Measure every character as one em to make placement assertions exact."""

    metrics = FontMetrics(ascent=0.8, descent=0.2, cap_height=0.7)

    def advance(self, text: str, size: float) -> float:
        return len(text) * size


@pytest.fixture
def measurer() -> FixedWidthMeasurer:
    return FixedWidthMeasurer()


def test_wrap_line_handles_empty_and_greedy_wrapping(measurer):
    assert wrap_line(measurer, "   ", size=1, max_w=10) == []
    assert wrap_line(measurer, "one two three", size=1, max_w=7) == [
        "one two",
        "three",
    ]


def test_layout_block_shrinks_and_centers_explicit_lines(measurer):
    lines = layout_block(
        measurer,
        "aa\nbb",
        Box(x=0, y=10, w=40, h=20),
        size=10,
        min_size=7,
    )

    assert [line.text for line in lines] == ["aa", "bb"]
    assert [line.size for line in lines] == [8, 8]
    assert [line.x for line in lines] == [20, 20]
    assert [line.y for line in lines] == pytest.approx([17.8, 27.8])


def test_layout_block_supports_top_left_alignment(measurer):
    [line] = layout_block(
        measurer,
        "top",
        Box(x=2, y=3, w=100, h=30),
        size=10,
        halign="left",
        valign="top",
    )

    assert (line.x, line.y) == pytest.approx((2, 10))


def test_layout_block_supports_bottom_right_alignment(measurer):
    lines = layout_block(
        measurer,
        "one\ntwo",
        Box(x=2, y=3, w=100, h=30),
        size=10,
        halign="right",
        valign="bottom",
    )

    assert [line.x for line in lines] == [102, 102]
    assert [line.y for line in lines] == pytest.approx([18.5, 31])


def test_layout_block_raises_when_minimum_size_cannot_fit(measurer):
    with pytest.raises(TextOverflowError, match=r"4x20 at >= 1px"):
        layout_block(
            measurer,
            "longword",
            Box(x=0, y=0, w=4, h=20),
            size=2,
            min_size=1,
        )


# --- rich_lines glyph-aware auto-fit (uses real bundled-font metrics) ---


def _text_font_sizes(group) -> list[float]:
    return [
        float(t.get("font-size"))
        for t in group.iter()
        if t.tag.endswith("text") and t.get("font-size") is not None
    ]


def test_rich_lines_without_max_h_keeps_requested_size():
    tokens = load_tokens()
    group, _ = rich_lines(
        core.SVGDocument(),
        tokens,
        "one two three four five",
        cx=366,
        y=778,
        size=32,
        max_w=372,
    )
    assert set(_text_font_sizes(group)) == {32.0}


def test_rich_lines_shrinks_to_fit_max_h():
    tokens = load_tokens()
    long_text = " ".join(["word"] * 40)
    natural = measure_rich_height(tokens, long_text, 32, 372)

    group, baseline = rich_lines(
        core.SVGDocument(),
        tokens,
        long_text,
        cx=366,
        y=778,
        size=32,
        max_w=372,
        max_h=natural / 2,
        min_size=12,
    )
    sizes = _text_font_sizes(group)
    assert sizes
    assert max(sizes) < 32  # shrank below the requested size
    assert (baseline - 778) <= natural / 2 + 1e-6  # block fits the budget


def test_rich_lines_clamps_at_min_size_without_raising():
    tokens = load_tokens()
    group, _ = rich_lines(
        core.SVGDocument(),
        tokens,
        " ".join(["word"] * 60),
        cx=366,
        y=778,
        size=32,
        max_w=372,
        max_h=1.0,  # impossible budget -> clamp at min_size, never raise
        min_size=14,
    )
    assert min(_text_font_sizes(group)) == 14.0
