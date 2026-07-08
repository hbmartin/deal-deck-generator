"""Text measurement using fontTools metrics from the bundled fonts.

Measurement ALWAYS uses the bundled fallback fonts, even when the final
render resolves to system Gill Sans: line-break and centering decisions
must be identical on every machine so the emitted SVG bytes are stable.
Layout boxes carry slack to absorb the (small) metric differences.
"""

from dataclasses import dataclass
from functools import cache
from pathlib import Path

from fontTools.ttLib import TTFont


@dataclass(frozen=True)
class FontMetrics:
    ascent: float  # fraction of em, positive up from baseline
    descent: float  # fraction of em, positive down from baseline
    cap_height: float  # fraction of em


class TextMeasurer:
    def __init__(self, font_path: Path):
        self.font_path = font_path
        self._font = TTFont(str(font_path))
        self._upem = self._font["head"].unitsPerEm
        self._cmap = self._font.getBestCmap()
        self._hmtx = self._font["hmtx"]
        self._kern = None
        if "kern" in self._font:
            try:
                self._kern = self._font["kern"].kernTables[0].kernTable
            except AttributeError, IndexError:
                self._kern = None

    def _glyph(self, ch: str) -> str:
        return self._cmap.get(ord(ch), ".notdef")

    def advance(self, text: str, size: float, letter_spacing: float = 0.0) -> float:
        """Width of a text run at the given px size (letter_spacing in px)."""
        units = 0
        prev = None
        for ch in text:
            name = self._glyph(ch)
            units += self._hmtx[name][0]
            if self._kern and prev is not None:
                units += self._kern.get((prev, name), 0)
            prev = name
        width = units * size / self._upem
        if letter_spacing and len(text) > 1:
            width += letter_spacing * (len(text) - 1)
        return width

    @property
    def metrics(self) -> FontMetrics:
        hhea = self._font["hhea"]
        try:
            cap = self._font["OS/2"].sCapHeight
        except KeyError, AttributeError:
            cap = hhea.ascent * 0.7
        return FontMetrics(
            ascent=hhea.ascent / self._upem,
            descent=abs(hhea.descent) / self._upem,
            cap_height=cap / self._upem,
        )


@cache
def get_measurer(font_path: Path) -> TextMeasurer:
    return TextMeasurer(font_path)
