"""Thin SVG-building helpers over xml.etree.ElementTree.

Conventions:
- Attribute names: python underscores become hyphens (stroke_width -> stroke-width);
  a trailing underscore is stripped (class_ -> class).
- Numbers are formatted to at most 2 decimal places for stable, compact output.
- Documents are fixed to the full-bleed canvas viewBox ("0 0 732 1101").
"""

import xml.etree.ElementTree as ET

from ..geometry import BLEED

SVG_NS = "http://www.w3.org/2000/svg"


def fmt(v) -> str:
    """Format attribute values: floats trimmed to 2 decimals, no trailing zeros."""
    if isinstance(v, float):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return str(v)


def el(tag: str, *children: ET.Element, text: str | None = None, **attrs) -> ET.Element:
    e = ET.Element(tag)
    for k, v in attrs.items():
        if v is None:
            continue
        name = k.rstrip("_").replace("_", "-")
        e.set(name, fmt(v))
    if text is not None:
        e.text = text
    for c in children:
        e.append(c)
    return e


def g(*children: ET.Element, **attrs) -> ET.Element:
    return el("g", *children, **attrs)


def rect(box=None, **attrs) -> ET.Element:
    if box is not None:
        attrs = {"x": box.x, "y": box.y, "width": box.w, "height": box.h, **attrs}
    return el("rect", **attrs)


def circle(cx, cy, r, **attrs) -> ET.Element:
    return el("circle", cx=cx, cy=cy, r=r, **attrs)


def line(x1, y1, x2, y2, **attrs) -> ET.Element:
    return el("line", x1=x1, y1=y1, x2=x2, y2=y2, **attrs)


def path(d: str, **attrs) -> ET.Element:
    return el("path", d=d, **attrs)


def text_el(x, y, content: str, **attrs) -> ET.Element:
    return el("text", x=x, y=y, text=content, **attrs)


def use(href: str, **attrs) -> ET.Element:
    return el("use", href=f"#{href}", **attrs)


def translate(x, y) -> str:
    return f"translate({fmt(x)} {fmt(y)})"


def rotate(deg, cx=None, cy=None) -> str:
    if cx is None:
        return f"rotate({fmt(deg)})"
    return f"rotate({fmt(deg)} {fmt(cx)} {fmt(cy)})"


class SVGDocument:
    """A full-bleed card document with a managed <defs> section."""

    def __init__(self):
        self.root = el(
            "svg",
            xmlns=SVG_NS,
            viewBox=f"0 0 {int(BLEED.w)} {int(BLEED.h)}",
            width=int(BLEED.w),
            height=int(BLEED.h),
        )
        self._defs = el("defs")
        self.root.append(self._defs)
        self._def_ids: set[str] = set()

    def add_def(self, def_id: str, element: ET.Element) -> str:
        """Register a definition once; repeated ids are ignored."""
        if def_id not in self._def_ids:
            element.set("id", def_id)
            self._defs.append(element)
            self._def_ids.add(def_id)
        return def_id

    def has_def(self, def_id: str) -> bool:
        return def_id in self._def_ids

    def add(self, element: ET.Element) -> None:
        self.root.append(element)

    def to_bytes(self) -> bytes:
        return ET.tostring(self.root, encoding="utf-8", xml_declaration=True)
