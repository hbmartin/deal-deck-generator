"""Unit tests for deterministic text wrapping and placement."""

import pytest

from src.geometry import Box
from src.text.layout import TextOverflowError, layout_block, wrap_line
from src.text.measure import FontMetrics


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
