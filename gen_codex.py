import math
import svgwrite

WIDTH, HEIGHT = 732, 1101


def guilloche_rosette_path(cx, cy, R, r, m, steps=720):
    """
    Simple guilloche / rosette curve:
        radius(theta) = R + r * sin(m * theta)
    """
    pts = []
    for i in range(steps + 1):
        t = 2 * math.pi * i / steps
        rad = R + r * math.sin(m * t)
        x = cx + rad * math.cos(t)
        y = cy + rad * math.sin(t)
        pts.append((x, y))

    d = [f"M {pts[0][0]:.3f},{pts[0][1]:.3f}"]
    for (x, y) in pts[1:]:
        d.append(f"L {x:.3f},{y:.3f}")
    d.append("Z")
    return " ".join(d)


def add_guilloche_background_pattern(dwg, pattern_id="guilloche_bg"):
    """
    Guilloche-like tiled background: two overlapping rosettes.
    """
    size = 80
    pat = dwg.pattern(
        id=pattern_id,
        size=(size, size),
        patternUnits="userSpaceOnUse",
    )

    # First rosette – larger, smoother
    d1 = guilloche_rosette_path(size / 2, size / 2, R=26, r=6, m=8)
    pat.add(
        dwg.path(
            d=d1,
            fill="none",
            stroke="#6e4a70",
            stroke_width=0.7,
            opacity=0.6,
        )
    )

    # Second rosette – smaller, finer detail
    d2 = guilloche_rosette_path(size / 2, size / 2, R=18, r=4, m=13)
    pat.add(
        dwg.path(
            d=d2,
            fill="none",
            stroke="#5d3b5f",
            stroke_width=0.5,
            opacity=0.45,
        )
    )

    dwg.defs.add(pat)


def scallops_horizontal(x0, x1, y, pitch, radius, upward):
    """
    Build a Q-curve scalloped path along a horizontal side.
    """
    if x1 < x0:
        x0, x1 = x1, x0

    length = x1 - x0
    n = int(length / pitch)
    if n <= 0:
        return ""

    d = []
    for i in range(n):
        xs = x0 + i * pitch
        xe = xs + pitch
        xm = (xs + xe) / 2.0
        cy = y - radius if upward else y + radius
        if i == 0:
            d.append(f"M {xs:.3f},{y:.3f}")
        d.append(f"Q {xm:.3f},{cy:.3f} {xe:.3f},{y:.3f}")
    return " ".join(d)


def scallops_vertical(y0, y1, x, pitch, radius, leftward):
    """
    Build a Q-curve scalloped path along a vertical side.
    """
    if y1 < y0:
        y0, y1 = y1, y0

    length = y1 - y0
    n = int(length / pitch)
    if n <= 0:
        return ""

    d = []
    for i in range(n):
        ys = y0 + i * pitch
        ye = ys + pitch
        ym = (ys + ye) / 2.0
        cx = x - radius if leftward else x + radius
        if i == 0:
            d.append(f"M {x:.3f},{ys:.3f}")
        d.append(f"Q {cx:.3f},{ym:.3f} {x:.3f},{ye:.3f}")
    return " ".join(d)


def draw_guilloche_frame(dwg, x, y, w, h, line_color="#000000"):
    """
    Guilloche-like inner frame: scallops on all four sides + inner rect.
    """
    group = dwg.g(stroke=line_color, fill="none")

    pitch = 14.0
    radius = 4.5

    # Top (arches inward)
    top_d = scallops_horizontal(x, x + w, y, pitch, radius, upward=False)
    group.add(
        dwg.path(
            d=top_d,
            stroke_width=1.4,
        )
    )

    # Bottom (mirror of top)
    bottom_d = scallops_horizontal(x + w, x, y + h, pitch, radius, upward=True)
    group.add(
        dwg.path(
            d=bottom_d,
            stroke_width=1.4,
        )
    )

    # Left side (arches inward)
    left_d = scallops_vertical(y + h, y, x, pitch, radius, leftward=False)
    group.add(
        dwg.path(
            d=left_d,
            stroke_width=1.4,
        )
    )

    # Right side (mirror)
    right_d = scallops_vertical(y, y + h, x + w, pitch, radius, leftward=True)
    group.add(
        dwg.path(
            d=right_d,
            stroke_width=1.4,
        )
    )

    # Simple inner rectangle just inside the scallops
    inner_offset = 8.0
    group.add(
        dwg.rect(
            insert=(x + inner_offset, y + inner_offset),
            size=(w - 2 * inner_offset, h - 2 * inner_offset),
            stroke_width=1.1,
        )
    )

    dwg.add(group)


def make_card_svg(filename="monopoly_like_card.svg"):
    dwg = svgwrite.Drawing(filename, size=(WIDTH, HEIGHT))

    min_dim = min(WIDTH, HEIGHT)

    # Colors tuned to approximate the photo
    card_bg = "#f3e3db"      # off-white card stock
    purple = "#846183"       # main field color
    line_color = "#000000"

    # Base card background
    dwg.add(dwg.rect(insert=(0, 0), size=(WIDTH, HEIGHT), fill=card_bg))

    # Geometry margins (relative to min dimension to keep proportions)
    outer_margin = 0.03 * min_dim       # outer black frame
    purple_margin = 0.07 * min_dim      # main purple field inset
    frame_margin = 0.12 * min_dim       # guilloche frame inset

    # Outer black border
    dwg.add(
        dwg.rect(
            insert=(outer_margin, outer_margin),
            size=(WIDTH - 2 * outer_margin, HEIGHT - 2 * outer_margin),
            fill="none",
            stroke=line_color,
            stroke_width=4.0,
        )
    )

    # Main purple field
    dwg.add(
        dwg.rect(
            insert=(purple_margin, purple_margin),
            size=(WIDTH - 2 * purple_margin, HEIGHT - 2 * purple_margin),
            fill=purple,
            stroke="none",
        )
    )

    # Guilloche background pattern (defs + patterned rect)
    add_guilloche_background_pattern(dwg, "guilloche_bg")

    inner_rect_x = frame_margin
    inner_rect_y = frame_margin
    inner_rect_w = WIDTH - 2 * frame_margin
    inner_rect_h = HEIGHT - 2 * frame_margin

    dwg.add(
        dwg.rect(
            insert=(inner_rect_x, inner_rect_y),
            size=(inner_rect_w, inner_rect_h),
            fill="url(#guilloche_bg)",
            stroke="none",
        )
    )

    # Guilloche-style frame around that inner area
    draw_guilloche_frame(
        dwg,
        inner_rect_x,
        inner_rect_y,
        inner_rect_w,
        inner_rect_h,
        line_color=line_color,
    )

    # Central double-bordered circle
    cx, cy = WIDTH / 2.0, HEIGHT / 2.0
    outer_r = 0.26 * min_dim
    inner_r = outer_r - 10.0

    # Outer circle line
    dwg.add(
        dwg.circle(
            center=(cx, cy),
            r=outer_r,
            fill="none",
            stroke=line_color,
            stroke_width=5.0,
        )
    )

    # Inner circle, filled with purple to mask the guilloche texture
    dwg.add(
        dwg.circle(
            center=(cx, cy),
            r=inner_r,
            fill=purple,
            stroke=line_color,
            stroke_width=2.5,
        )
    )

    # Corner circles (top-right & bottom-left), double-bordered, no text
    corner_outer_r = 0.085 * min_dim
    corner_inner_r = corner_outer_r - 8.0

    bl_cx = purple_margin + corner_outer_r
    bl_cy = HEIGHT - purple_margin - corner_outer_r
    tr_cx = WIDTH - purple_margin - corner_outer_r
    tr_cy = purple_margin + corner_outer_r

    for (cx_c, cy_c) in [(bl_cx, bl_cy), (tr_cx, tr_cy)]:
        # Outer ring
        dwg.add(
            dwg.circle(
                center=(cx_c, cy_c),
                r=corner_outer_r,
                fill=purple,
                stroke=line_color,
                stroke_width=4.0,
            )
        )
        # Inner ring
        dwg.add(
            dwg.circle(
                center=(cx_c, cy_c),
                r=corner_inner_r,
                fill=purple,
                stroke=line_color,
                stroke_width=2.0,
            )
        )

    dwg.save()
    print(f"Saved {filename}")


if __name__ == "__main__":
    make_card_svg()
