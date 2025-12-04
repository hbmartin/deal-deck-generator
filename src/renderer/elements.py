"""
Higher-level rendering functions for common card elements.
"""

from PIL import Image, ImageDraw
from .primitives import (
    draw_circle,
    draw_text,
    get_font,
    hex_to_rgb,
)


def draw_value_badge(
    draw: ImageDraw.ImageDraw,
    value: int,
    position: tuple[int, int],
    diameter: int = 50,
    bg_color: str = "#FFFFFF",
    border_color: str = "#000000",
    border_width: int = 3,
    text_color: str = "#000000",
):
    """
    Draw a circular value badge.

    Args:
        draw: ImageDraw object
        value: Value to display (in millions)
        position: Center position as (x, y)
        diameter: Badge diameter
        bg_color: Background color
        border_color: Border color
        border_width: Border width
        text_color: Text color
    """
    radius = diameter // 2

    # Draw outer circle (border)
    draw_circle(
        draw, position, radius, fill=bg_color, outline=border_color, width=border_width
    )

    # Draw value text with money symbol
    font = get_font("Arial", size=diameter // 3, bold=True)
    value_text = f"${value}M"
    draw_text(draw, value_text, position, font, color=text_color, anchor="mm")


def draw_decorative_border(
    img: Image.Image,
    draw: ImageDraw.ImageDraw,
    border_width: int = 15,
    border_color: str = "#505050",
    pattern: str = "chain_link",
):
    """
    Draw a decorative border around the card.

    Args:
        img: Card image
        draw: ImageDraw object
        border_width: Border width in pixels
        border_color: Border color
        pattern: Pattern type ('chain_link', 'solid', 'double')
    """
    width, height = img.size
    margin = 10

    if border_color.startswith("#"):
        border_color = hex_to_rgb(border_color)

    if pattern == "chain_link":
        # Draw a simple dashed/segmented border
        segment_length = 15
        gap = 5

        # Top and bottom borders
        for x in range(margin, width - margin, segment_length + gap):
            x_end = min(x + segment_length, width - margin)
            draw.line([(x, margin), (x_end, margin)], fill=border_color, width=3)
            draw.line(
                [(x, height - margin), (x_end, height - margin)],
                fill=border_color,
                width=3,
            )

        # Left and right borders
        for y in range(margin, height - margin, segment_length + gap):
            y_end = min(y + segment_length, height - margin)
            draw.line([(margin, y), (margin, y_end)], fill=border_color, width=3)
            draw.line(
                [(width - margin, y), (width - margin, y_end)],
                fill=border_color,
                width=3,
            )

    elif pattern == "double":
        # Draw double line border
        draw.rectangle(
            [(margin, margin), (width - margin, height - margin)],
            outline=border_color,
            width=2,
        )
        draw.rectangle(
            [(margin + 5, margin + 5), (width - margin - 5, height - margin - 5)],
            outline=border_color,
            width=2,
        )

    else:  # solid
        draw.rectangle(
            [(margin, margin), (width - margin, height - margin)],
            outline=border_color,
            width=border_width,
        )


def draw_property_rent_row(
    draw: ImageDraw.ImageDraw,
    y: int,
    num_properties: int,
    rent_value: int,
    icon_color: str = "#228B22",
    x_start: int = 50,
    row_width: int = 300,
):
    """
    Draw a single rent table row with property icon and value.

    Args:
        draw: ImageDraw object
        y: Y position of row
        num_properties: Number of properties in set
        rent_value: Rent amount
        icon_color: Color for property icon
        x_start: Starting X position
        row_width: Total width of row
    """
    # Draw property icon (simplified house shape)
    icon_size = 40
    icon_x = x_start + 20

    if icon_color.startswith("#"):
        icon_color = hex_to_rgb(icon_color)

    # Draw simple house icon (square + triangle roof)
    house_y = y - icon_size // 2
    draw.rectangle(
        [
            (icon_x, house_y + icon_size // 3),
            (icon_x + icon_size, house_y + icon_size),
        ],
        fill=icon_color,
        outline="#000000",
        width=2,
    )

    # Triangle roof
    draw.polygon(
        [
            (icon_x, house_y + icon_size // 3),
            (icon_x + icon_size // 2, house_y),
            (icon_x + icon_size, house_y + icon_size // 3),
        ],
        fill=icon_color,
        outline="#000000",
    )

    # Draw number badge
    badge_radius = 18
    badge_x = icon_x + icon_size // 2
    badge_y = y
    draw_circle(
        draw,
        (badge_x, badge_y),
        badge_radius,
        fill="#FFFFFF",
        outline="#000000",
        width=2,
    )

    font = get_font("Arial", size=16, bold=True)
    draw_text(draw, str(num_properties), (badge_x, badge_y), font, anchor="mm")

    # Draw dotted line
    dots_start_x = icon_x + icon_size + 20
    dots_end_x = x_start + row_width - 80
    dot_spacing = 10

    for x in range(dots_start_x, dots_end_x, dot_spacing):
        draw.ellipse([(x, y - 2), (x + 3, y + 1)], fill="#505050")

    # Draw rent value
    rent_font = get_font("Arial", size=18, bold=True)
    rent_text = f"${rent_value}M"
    rent_x = x_start + row_width - 50
    draw_text(draw, rent_text, (rent_x, y), rent_font, anchor="rm")


def draw_color_stripes(
    draw: ImageDraw.ImageDraw,
    colors: list[str],
    y: int,
    height: int,
    x_start: int = 30,
    x_end: int = 383,
):
    """
    Draw horizontal color stripes (for wildcard headers).

    Args:
        draw: ImageDraw object
        colors: List of hex color codes
        y: Top Y position
        height: Stripe height
        x_start: Starting X position
        x_end: Ending X position
    """
    if not colors:
        return

    stripe_width = (x_end - x_start) // len(colors)

    for i, color in enumerate(colors):
        x1 = x_start + i * stripe_width
        x2 = x1 + stripe_width

        if color.startswith("#"):
            color = hex_to_rgb(color)

        draw.rectangle([(x1, y), (x2, y + height)], fill=color, outline=None)

    # Draw border around all stripes
    draw.rectangle([(x_start, y), (x_end, y + height)], outline="#000000", width=2)
