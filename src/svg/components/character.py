"""Simplified vector Mr. Money for the multicolor wildcard.

A stylized flat-color redraw of the pose in the reference photo: top hat,
mustache, tailcoat, one arm extended pointing at an open palm.
Drawn in a unit box of the given height, (0, 0) = top-left; width ~0.78 h.
"""

from ...svg import core

SKIN = "#F6C99F"
INK = "#1A1A1A"
WHITE = "#FFFFFF"


def mr_money(height: float) -> core.ET.Element:
    h = height
    w = 0.78 * h
    cx = w * 0.46  # figure center line

    parts = []

    # --- legs & shoes ---
    for side in (-1, 1):
        x = cx + side * w * 0.10
        parts.append(
            core.rect(
                None,
                x=x - w * 0.055,
                y=h * 0.72,
                width=w * 0.11,
                height=h * 0.20,
                fill=INK,
            )
        )
        parts.append(
            core.el(
                "ellipse",
                cx=x + side * w * 0.045,
                cy=h * 0.945,
                rx=w * 0.115,
                ry=h * 0.032,
                fill=INK,
            )
        )

    # --- tailcoat body ---
    parts.append(
        core.path(
            f"M {cx - w * 0.20} {h * 0.40} "
            f"Q {cx - w * 0.26} {h * 0.58} {cx - w * 0.18} {h * 0.74} "
            f"L {cx + w * 0.18} {h * 0.74} "
            f"Q {cx + w * 0.26} {h * 0.58} {cx + w * 0.20} {h * 0.40} "
            f"Q {cx} {h * 0.35} {cx - w * 0.20} {h * 0.40} Z",
            fill=INK,
        )
    )
    # shirt wedge + bowtie
    parts.append(
        core.path(
            f"M {cx - w * 0.075} {h * 0.40} L {cx + w * 0.075} {h * 0.40} "
            f"L {cx} {h * 0.56} Z",
            fill=WHITE,
        )
    )
    parts.append(
        core.path(
            f"M {cx - w * 0.07} {h * 0.395} L {cx - w * 0.02} {h * 0.42} "
            f"L {cx - w * 0.02} {h * 0.44} L {cx - w * 0.07} {h * 0.465} Z "
            f"M {cx + w * 0.07} {h * 0.395} L {cx + w * 0.02} {h * 0.42} "
            f"L {cx + w * 0.02} {h * 0.44} L {cx + w * 0.07} {h * 0.465} Z",
            fill=INK,
        )
    )

    # --- pointing arm (his right, viewer left) folded across, open palm ---
    parts.append(
        core.path(
            f"M {cx - w * 0.19} {h * 0.44} "
            f"Q {cx - w * 0.34} {h * 0.50} {cx - w * 0.30} {h * 0.585} "
            f"L {cx - w * 0.215} {h * 0.585} "
            f"Q {cx - w * 0.245} {h * 0.52} {cx - w * 0.13} {h * 0.485} Z",
            fill=INK,
        )
    )
    # open palm (skin)
    parts.append(
        core.el(
            "ellipse",
            cx=cx - w * 0.265,
            cy=h * 0.615,
            rx=w * 0.075,
            ry=h * 0.038,
            fill=SKIN,
        )
    )
    # --- other arm pointing down toward the palm ---
    parts.append(
        core.path(
            f"M {cx + w * 0.19} {h * 0.44} "
            f"Q {cx + w * 0.30} {h * 0.50} {cx + w * 0.16} {h * 0.575} "
            f"L {cx + w * 0.02} {h * 0.60} "
            f"L {cx - w * 0.02} {h * 0.565} "
            f"Q {cx + w * 0.16} {h * 0.52} {cx + w * 0.13} {h * 0.475} Z",
            fill=INK,
        )
    )
    # pointing hand
    parts.append(
        core.el(
            "ellipse",
            cx=cx - w * 0.05,
            cy=h * 0.585,
            rx=w * 0.055,
            ry=h * 0.028,
            fill=SKIN,
        )
    )

    # --- head ---
    parts.append(core.circle(cx, h * 0.295, w * 0.155, fill=SKIN))
    # ears
    parts.extend(
        core.circle(cx + side * w * 0.15, h * 0.30, w * 0.035, fill=SKIN)
        for side in (-1, 1)
    )
    # mustache: two white lobes
    parts.extend(
        core.el(
            "ellipse",
            cx=cx + side * w * 0.075,
            cy=h * 0.345,
            rx=w * 0.085,
            ry=h * 0.026,
            fill=WHITE,
            transform=core.rotate(side * 12, cx + side * w * 0.075, h * 0.345),
        )
        for side in (-1, 1)
    )
    # eyes + nose
    parts.extend(
        core.circle(cx + side * w * 0.05, h * 0.275, w * 0.012, fill=INK)
        for side in (-1, 1)
    )
    parts.append(core.circle(cx, h * 0.31, w * 0.022, fill="#E8A87C"))

    # --- top hat ---
    parts.append(
        core.el("ellipse", cx=cx, cy=h * 0.175, rx=w * 0.21, ry=h * 0.022, fill=INK)
    )
    parts.append(
        core.rect(
            None,
            x=cx - w * 0.145,
            y=h * 0.03,
            width=w * 0.29,
            height=h * 0.145,
            fill=INK,
        )
    )
    parts.append(
        core.el("ellipse", cx=cx, cy=h * 0.03, rx=w * 0.145, ry=h * 0.016, fill=INK)
    )

    return core.g(*parts)
