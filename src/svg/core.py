"""Thin SVG-building helpers over xml.etree.ElementTree.

Conventions:
- Attribute names: python underscores become hyphens (stroke_width -> stroke-width);
  a trailing underscore is stripped (class_ -> class).
- Numbers are formatted to at most 2 decimal places for stable, compact output.
- Documents are fixed to the full-bleed canvas viewBox ("0 0 732 1101").
"""

import xml.etree.ElementTree as ET

from ..geometry import BLEED, Box

SVG_NS = "http://www.w3.org/2000/svg"


type Number = int | float


def fmt(v: object) -> str:
    """Format attribute values: floats trimmed to 2 decimals, no trailing zeros."""
    if isinstance(v, float):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return str(v)


def _element(
    tag: str,
    children: tuple[ET.Element, ...],
    text: str | None,
    attrs: dict[str, object],
) -> ET.Element:
    element = ET.Element(tag)
    for key, value in attrs.items():
        if value is None:
            continue
        name = key.rstrip("_").replace("_", "-")
        element.set(name, fmt(value))
    if text is not None:
        element.text = text
    element.extend(children)
    return element


def el(
    tag: str,
    *children: ET.Element,
    text: str | None = None,
    **attrs: object,
) -> ET.Element:
    return _element(tag, children, text, attrs)


def g(*children: ET.Element, **attrs: object) -> ET.Element:
    return _element("g", children, None, attrs)


def rect(box: Box | None = None, **attrs: object) -> ET.Element:
    if box is not None:
        attrs = {"x": box.x, "y": box.y, "width": box.w, "height": box.h, **attrs}
    return _element("rect", (), None, attrs)


def circle(cx: Number, cy: Number, r: Number, **attrs: object) -> ET.Element:
    return _element("circle", (), None, {"cx": cx, "cy": cy, "r": r, **attrs})


def line(
    x1: Number,
    y1: Number,
    x2: Number,
    y2: Number,
    **attrs: object,
) -> ET.Element:
    return _element(
        "line",
        (),
        None,
        {"x1": x1, "y1": y1, "x2": x2, "y2": y2, **attrs},
    )


def path(d: str, **attrs: object) -> ET.Element:
    return _element("path", (), None, {"d": d, **attrs})


def text_el(x: Number, y: Number, content: str, **attrs: object) -> ET.Element:
    return _element("text", (), content, {"x": x, "y": y, **attrs})


def use(href: str, **attrs: object) -> ET.Element:
    return _element("use", (), None, {"href": f"#{href}", **attrs})


def translate(x: Number, y: Number) -> str:
    return f"translate({fmt(x)} {fmt(y)})"


def rotate(
    deg: Number,
    cx: Number | None = None,
    cy: Number | None = None,
) -> str:
    if cx is None:
        return f"rotate({fmt(deg)})"
    return f"rotate({fmt(deg)} {fmt(cx)} {fmt(cy)})"


class SVGDocument:
    """A full-bleed card document with a managed <defs> section."""

    def __init__(self) -> None:
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
