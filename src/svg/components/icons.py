"""Flat vector icons drawn in unit design boxes.

Every factory returns a group whose contents live in a box of the given
height with (0, 0) at the icon's top-left; callers translate/scale.
Shapes are simplified silhouettes matched to the reference photos.
"""

import math

from ...svg import core


def train(height: float, color: str = "#FFFFFF") -> core.ET.Element:
    """Steam locomotive silhouette, facing left. Width ~= 1.5 * height."""
    h = height
    w = 1.5 * h
    body = core.path(
        # cab | boiler | front stack — one silhouette path
        f"M {w * 0.98} {h * 0.78} "
        f"L {w * 0.98} {h * 0.22} L {w * 0.72} {h * 0.22} "
        f"L {w * 0.72} {h * 0.40} L {w * 0.30} {h * 0.40} "
        f"L {w * 0.30} {h * 0.30} L {w * 0.38} {h * 0.30} L {w * 0.38} {h * 0.06} "
        f"L {w * 0.24} {h * 0.06} L {w * 0.24} {h * 0.30} "
        f"L {w * 0.06} {h * 0.30} L {w * 0.02} {h * 0.46} "
        f"L {w * 0.02} {h * 0.78} Z",
        fill=color,
    )
    wheels = [
        core.circle(w * 0.16, h * 0.82, h * 0.13, fill=color),
        core.circle(w * 0.42, h * 0.82, h * 0.13, fill=color),
        core.circle(w * 0.68, h * 0.82, h * 0.13, fill=color),
        core.circle(w * 0.88, h * 0.82, h * 0.13, fill=color),
    ]
    return core.g(body, *wheels)


def faucet(height: float, color: str = "#000000") -> core.ET.Element:
    """Water tap with a drip. Width ~= 1.1 * height."""
    h = height
    w = 1.1 * h
    body = core.path(
        f"M {w * 0.10} {h * 0.34} "
        f"L {w * 0.42} {h * 0.34} L {w * 0.42} {h * 0.24} "
        f"L {w * 0.30} {h * 0.20} L {w * 0.30} {h * 0.10} "
        f"L {w * 0.62} {h * 0.10} L {w * 0.62} {h * 0.20} "
        f"L {w * 0.50} {h * 0.24} L {w * 0.50} {h * 0.34} "
        f"L {w * 0.78} {h * 0.34} "
        f"Q {w * 0.94} {h * 0.34} {w * 0.94} {h * 0.52} "
        f"L {w * 0.94} {h * 0.60} L {w * 0.80} {h * 0.60} L {w * 0.80} {h * 0.54} "
        f"Q {w * 0.80} {h * 0.46} {w * 0.70} {h * 0.46} "
        f"L {w * 0.10} {h * 0.46} Z",
        fill=color,
    )
    drip = core.path(
        f"M {w * 0.87} {h * 0.72} "
        f"Q {w * 0.94} {h * 0.84} {w * 0.87} {h * 0.90} "
        f"Q {w * 0.80} {h * 0.84} {w * 0.87} {h * 0.72} Z",
        fill=color,
    )
    return core.g(body, drip)


def bulb(
    height: float, color: str = "#000000", glow: str = "#F5D227"
) -> core.ET.Element:
    """Light bulb with rays. Width ~= 0.9 * height."""
    h = height
    w = 0.9 * h
    cx = w / 2
    globe_r = h * 0.30
    globe_cy = h * 0.34
    parts = [
        core.circle(
            cx, globe_cy, globe_r, fill=glow, stroke=color, stroke_width=h * 0.045
        ),
        # base
        core.rect(
            None,
            x=cx - globe_r * 0.5,
            y=globe_cy + globe_r * 0.85,
            width=globe_r,
            height=h * 0.22,
            rx=h * 0.03,
            fill=color,
        ),
    ]
    # rays
    for ang in (-150, -120, -90, -60, -30):
        a = math.radians(ang)
        x1 = cx + math.cos(a) * globe_r * 1.25
        y1 = globe_cy + math.sin(a) * globe_r * 1.25
        x2 = cx + math.cos(a) * globe_r * 1.65
        y2 = globe_cy + math.sin(a) * globe_r * 1.65
        parts.append(
            core.line(
                x1,
                y1,
                x2,
                y2,
                stroke=color,
                stroke_width=h * 0.05,
                stroke_linecap="round",
            )
        )
    return core.g(*parts)


def route(height: float, color: str = "#000000") -> core.ET.Element:
    """Winding route with endpoint markers. Width ~= 1.15 * height."""
    h = height
    w = 1.15 * h
    path = core.path(
        f"M {w * 0.18} {h * 0.82} "
        f"C {w * 0.72} {h * 0.80} {w * 0.28} {h * 0.42} {w * 0.78} {h * 0.18}",
        fill="none",
        stroke=color,
        stroke_width=h * 0.09,
        stroke_linecap="round",
    )
    return core.g(
        path,
        core.circle(w * 0.18, h * 0.82, h * 0.12, fill=color),
        core.circle(w * 0.78, h * 0.18, h * 0.12, fill=color),
    )


def agave(height: float, color: str = "#000000") -> core.ET.Element:
    """Compact fan of pointed agave leaves. Width ~= height."""
    h = height
    w = h
    leaves = []
    for angle, scale in ((-46, 0.76), (-24, 0.92), (0, 1.0), (24, 0.92), (46, 0.76)):
        length = h * 0.72 * scale
        width = h * 0.15 * scale
        leaves.append(
            core.path(
                f"M 0 0 C {-width} {-length * 0.32} "
                f"{-width * 0.6} {-length * 0.7} 0 {-length} "
                f"C {width * 0.6} {-length * 0.7} "
                f"{width} {-length * 0.32} 0 0 Z",
                fill=color,
                transform=f"{core.translate(w / 2, h * 0.9)} {core.rotate(angle)}",
            )
        )
    return core.g(*leaves)


def jicara(height: float, color: str = "#000000") -> core.ET.Element:
    """Shallow jícara drinking bowl. Width ~= 1.1 * height."""
    h = height
    w = 1.1 * h
    return core.g(
        core.path(
            f"M {w * 0.08} {h * 0.36} Q {w * 0.5} {h * 0.98} {w * 0.92} {h * 0.36} Z",
            fill="none",
            stroke=color,
            stroke_width=h * 0.07,
            stroke_linejoin="round",
        ),
        core.line(
            w * 0.08,
            h * 0.36,
            w * 0.92,
            h * 0.36,
            stroke=color,
            stroke_width=h * 0.07,
            stroke_linecap="round",
        ),
        core.circle(w * 0.36, h * 0.26, h * 0.055, fill=color),
        core.circle(w * 0.53, h * 0.20, h * 0.045, fill=color),
        core.circle(w * 0.68, h * 0.27, h * 0.05, fill=color),
    )


def header_icon(
    name: str,
    height: float,
    color: str,
) -> tuple[core.ET.Element, float]:
    """Build a property-header icon and report its design width."""
    match name:
        case "train":
            return train(height, color), height * 1.5
        case "faucet":
            return faucet(height, color), height * 1.1
        case "bulb":
            return bulb(height), height * 0.9
        case "route":
            return route(height, color), height * 1.15
        case "agave":
            return agave(height, color), height
        case "jicara":
            return jicara(height, color), height * 1.1
        case _:
            msg = f"unsupported property header icon {name!r}"
            raise ValueError(msg)


def house(height: float, color: str = "#1E9247") -> core.ET.Element:
    """House piece, flat front view. Width ~= 1.25 * height."""
    h = height
    w = 1.25 * h
    return core.g(
        core.path(
            f"M {w * 0.06} {h * 0.44} L {w * 0.5} {h * 0.04} L {w * 0.94} {h * 0.44} Z",
            fill=color,
        ),
        core.rect(
            None, x=w * 0.14, y=h * 0.44, width=w * 0.72, height=h * 0.52, fill=color
        ),
    )


def hotel(height: float, color: str = "#C0272D") -> core.ET.Element:
    """Hotel piece: wider, with an entrance block."""
    h = height
    w = 1.45 * h
    return core.g(
        core.path(
            f"M {w * 0.04} {h * 0.36} L {w * 0.5} {h * 0.02} L {w * 0.96} {h * 0.36} Z",
            fill=color,
        ),
        core.rect(
            None, x=w * 0.10, y=h * 0.36, width=w * 0.80, height=h * 0.60, fill=color
        ),
    )


def cake(height: float) -> core.ET.Element:
    """Birthday cake with three candles."""
    h = height
    w = 1.15 * h
    ink = "#000000"
    parts = [
        # plate
        core.el(
            "ellipse",
            cx=w / 2,
            cy=h * 0.94,
            rx=w * 0.48,
            ry=h * 0.06,
            fill="none",
            stroke=ink,
            stroke_width=h * 0.035,
        ),
        # cake body
        core.rect(
            None,
            x=w * 0.16,
            y=h * 0.55,
            width=w * 0.68,
            height=h * 0.36,
            fill="#FFFFFF",
            stroke=ink,
            stroke_width=h * 0.035,
        ),
        # icing wave
        core.path(
            f"M {w * 0.16} {h * 0.62} "
            f"Q {w * 0.24} {h * 0.72} {w * 0.32} {h * 0.62} "
            f"Q {w * 0.40} {h * 0.72} {w * 0.48} {h * 0.62} "
            f"Q {w * 0.56} {h * 0.72} {w * 0.64} {h * 0.62} "
            f"Q {w * 0.72} {h * 0.72} {w * 0.80} {h * 0.62} "
            f"L {w * 0.84} {h * 0.62} L {w * 0.84} {h * 0.55} "
            f"L {w * 0.16} {h * 0.55} Z",
            fill=ink,
        ),
    ]
    for fx in (0.32, 0.5, 0.68):
        x = w * fx
        parts.append(
            core.rect(
                None,
                x=x - w * 0.015,
                y=h * 0.30,
                width=w * 0.03,
                height=h * 0.25,
                fill=ink,
            )
        )
        parts.append(
            core.path(
                f"M {x} {h * 0.12} Q {x + w * 0.05} {h * 0.22} {x} {h * 0.28} "
                f"Q {x - w * 0.05} {h * 0.22} {x} {h * 0.12} Z",
                fill=ink,
            )
        )
    return core.g(*parts)


def go_arrow(height: float, color: str = "#C0272D") -> core.ET.Element:
    """Draw the left-pointing Pass Go arrow, about 2.6 times wider than tall."""
    h = height
    w = 2.6 * h
    return core.g(
        core.path(
            f"M {w * 0.30} {h * 0.02} L {w * 0.02} {h * 0.5} L {w * 0.30} {h * 0.98} "
            f"L {w * 0.30} {h * 0.70} L {w * 0.98} {h * 0.70} L {w * 0.98} {h * 0.30} "
            f"L {w * 0.30} {h * 0.30} Z",
            fill=color,
            stroke="#000000",
            stroke_width=h * 0.05,
        )
    )


ICONS = {
    "train": train,
    "faucet": faucet,
    "bulb": bulb,
    "house": house,
    "hotel": hotel,
    "cake": cake,
    "go_arrow": go_arrow,
}
