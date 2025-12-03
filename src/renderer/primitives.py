"""
Low-level drawing primitives using Pillow.
Provides utilities for rendering card elements.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 6:
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    elif len(hex_color) == 8:  # With alpha
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    else:
        raise ValueError(f"Invalid hex color: {hex_color}")


def hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    """Convert hex color string to RGBA tuple."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 6:
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        return (*rgb, 255)
    elif len(hex_color) == 8:
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4, 6))
    else:
        raise ValueError(f"Invalid hex color: {hex_color}")


def draw_rounded_rectangle(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    radius: int,
    fill: str | None = None,
    outline: str | None = None,
    width: int = 1,
):
    """
    Draw a rounded rectangle.

    Args:
        draw: ImageDraw object
        xy: Bounding box as (x1, y1, x2, y2)
        radius: Corner radius in pixels
        fill: Fill color (hex or RGB)
        outline: Outline color (hex or RGB)
        width: Outline width
    """
    x1, y1, x2, y2 = xy

    # Convert hex colors to RGB if needed
    if fill and isinstance(fill, str) and fill.startswith("#"):
        fill = hex_to_rgb(fill)
    if outline and isinstance(outline, str) and outline.startswith("#"):
        outline = hex_to_rgb(outline)

    # Draw rounded rectangle
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_circle(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    radius: int,
    fill: str | None = None,
    outline: str | None = None,
    width: int = 1,
):
    """
    Draw a circle.

    Args:
        draw: ImageDraw object
        center: Center point as (x, y)
        radius: Circle radius
        fill: Fill color
        outline: Outline color
        width: Outline width
    """
    cx, cy = center
    bbox = (cx - radius, cy - radius, cx + radius, cy + radius)

    if fill and isinstance(fill, str) and fill.startswith("#"):
        fill = hex_to_rgb(fill)
    if outline and isinstance(outline, str) and outline.startswith("#"):
        outline = hex_to_rgb(outline)

    draw.ellipse(bbox, fill=fill, outline=outline, width=width)


def get_font(font_name: str = "Arial", size: int = 14, bold: bool = False):
    """
    Load a font. Falls back to default if not found.

    Args:
        font_name: Font family name
        size: Font size in points
        bold: Whether to use bold variant

    Returns:
        ImageFont object
    """
    try:
        # Try to load system font
        if bold and "bold" not in font_name.lower():
            font_name = f"{font_name} Bold"

        # Common macOS font paths
        font_paths = [
            f"/System/Library/Fonts/{font_name}.ttf",
            f"/System/Library/Fonts/{font_name}.ttc",
            f"/Library/Fonts/{font_name}.ttf",
            f"/Library/Fonts/{font_name}.ttc",
        ]

        for path in font_paths:
            if Path(path).exists():
                return ImageFont.truetype(path, size)

        # Try loading by name (Pillow will search system)
        return ImageFont.truetype(font_name, size)

    except Exception:
        # Fall back to default font
        return ImageFont.load_default()


def draw_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    position: tuple[int, int],
    font: ImageFont.ImageFont,
    color: str = "#000000",
    anchor: str = "lt",
    align: str = "left",
):
    """
    Draw text at a position.

    Args:
        draw: ImageDraw object
        text: Text to draw
        position: Position as (x, y)
        font: Font object
        color: Text color
        anchor: Anchor point (e.g., 'lt' = left-top, 'mm' = middle-middle)
        align: Text alignment for multiline text
    """
    if color.startswith("#"):
        color = hex_to_rgb(color)

    draw.text(position, text, font=font, fill=color, anchor=anchor, align=align)


def draw_multiline_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    position: tuple[int, int],
    font: ImageFont.ImageFont,
    color: str = "#000000",
    max_width: int = 300,
    line_spacing: float = 1.2,
    align: str = "left",
):
    """
    Draw text with automatic line wrapping.

    Args:
        draw: ImageDraw object
        text: Text to draw
        position: Top-left position as (x, y)
        font: Font object
        color: Text color
        max_width: Maximum width in pixels before wrapping
        line_spacing: Line height multiplier
        align: Text alignment
    """
    if color.startswith("#"):
        color = hex_to_rgb(color)

    # Estimate characters per line (rough approximation)
    avg_char_width = font.getbbox("M")[2]
    chars_per_line = max(10, max_width // avg_char_width)

    # Wrap text
    lines = []
    for paragraph in text.split("\n"):
        if paragraph.strip():
            lines.extend(textwrap.wrap(paragraph, width=chars_per_line))
        else:
            lines.append("")

    # Calculate line height
    line_height = int(font.size * line_spacing)

    # Draw each line
    x, y = position
    for line in lines:
        if align == "center":
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            line_x = x + (max_width - text_width) // 2
        elif align == "right":
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            line_x = x + max_width - text_width
        else:
            line_x = x

        draw.text((line_x, y), line, font=font, fill=color)
        y += line_height


def create_card_base(
    width: int, height: int, bg_color: str = "#FFFFFF", corner_radius: int = 20
) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """
    Create a blank card canvas with rounded corners.

    Args:
        width: Card width in pixels
        height: Card height in pixels
        bg_color: Background color
        corner_radius: Corner radius

    Returns:
        Tuple of (Image, ImageDraw) objects
    """
    # Create image with alpha channel for rounded corners
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle background
    draw_rounded_rectangle(
        draw, (0, 0, width, height), radius=corner_radius, fill=bg_color
    )

    return img, draw


def paste_image(
    base: Image.Image, overlay: Image.Image, position: tuple[int, int], mask=None
):
    """
    Paste one image onto another.

    Args:
        base: Base image
        overlay: Image to paste
        position: Position as (x, y)
        mask: Optional mask for transparency
    """
    if overlay.mode == "RGBA":
        base.paste(overlay, position, overlay)
    else:
        base.paste(overlay, position, mask)
