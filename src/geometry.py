"""Print-space geometry for the MakePlayingCards US Game Deck spec.

All coordinates are in pixels at 300 DPI on the full-bleed canvas:
bleed 732x1101 (2.44" x 3.67"), cut 660x1029 (2.2" x 3.43"),
safe 600x969 (2.0" x 3.23").
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float

    @property
    def x2(self) -> float:
        return self.x + self.w

    @property
    def y2(self) -> float:
        return self.y + self.h

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    def inset(self, dx: float, dy: float | None = None) -> "Box":
        """Shrink the box by dx on left/right and dy (default dx) on top/bottom."""
        if dy is None:
            dy = dx
        return Box(self.x + dx, self.y + dy, self.w - 2 * dx, self.h - 2 * dy)


BLEED = Box(0, 0, 732, 1101)
CUT = Box(36, 36, 660, 1029)
SAFE = Box(66, 66, 600, 969)

DPI = 300
