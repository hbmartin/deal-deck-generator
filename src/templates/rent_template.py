"""
Template for rendering rent cards.
"""

import json
from pathlib import Path
from PIL import Image
from ..renderer.primitives import (
    create_card_base,
    draw_text,
    draw_multiline_text,
    draw_circle,
    draw_pie_slice,
)
from ..renderer.elements import draw_value_badge, draw_decorative_border
from ..models import RentCard
from .utils import get_template_font


def load_design_tokens():
    """Load design tokens from JSON file."""
    tokens_path = Path(__file__).parent.parent.parent / "design_tokens.json"
    with open(tokens_path) as f:
        return json.load(f)


def render_rent_card(card: RentCard) -> Image.Image:
    """
    Render a rent card.

    Args:
        card: RentCard instance

    Returns:
        Rendered card image
    """
    tokens = load_design_tokens()
    global_config = tokens["global"]
    rent_config = tokens["card_types"]["rent"]

    # Create card base
    width = global_config["card"]["width"]
    height = global_config["card"]["height"]
    corner_radius = global_config["card"]["corner_radius"]
    bg_color = rent_config["colors"]["background"]

    img, draw = create_card_base(width, height, bg_color, corner_radius)

    # Draw decorative border
    draw_decorative_border(img, draw, border_width=15, pattern="chain_link")

    # Draw "RENT" title bar
    title_y = rent_config["layout"]["title_bar"]["y"]
    title_font = get_template_font("Arial", size=20, bold=True)
    draw_text(draw, "RENT", (width // 2, title_y), title_font, anchor="mm")

    # Get color map
    color_map = global_config["colors"]["property_sets"]

    # Draw color circles
    circle_config = rent_config["layout"]["color_circles"]
    circle_center_y = circle_config["center_y"]
    outer_radius = circle_config["outer_diameter"] // 2
    inner_radius = circle_config["inner_diameter"] // 2

    if card.is_wild:
        # Wild rent: draw all colors as segmented pie slices
        all_colors_list = [
            "brown",
            "light_blue",
            "pink",
            "orange",
            "red",
            "yellow",
            "green",
            "dark_blue",
            "railroad",
            "utility",
        ]
        all_colors = [color_map.get(c, "#228B22") for c in all_colors_list]
        num_colors = len(all_colors)
        segment_angle = 360.0 / num_colors

        # Draw outer circle border first
        draw_circle(
            draw,
            (width // 2, circle_center_y),
            outer_radius,
            fill=None,
            outline="#000000",
            width=4,
        )

        # Draw each color segment
        for i, color in enumerate(all_colors):
            start_angle = i * segment_angle
            end_angle = (i + 1) * segment_angle

            # Draw pie slice
            draw_pie_slice(
                draw,
                (width // 2, circle_center_y),
                outer_radius,
                start_angle,
                end_angle,
                fill=color,
                outline="#000000",
                width=2,
            )

        # Draw inner white circle with text
        draw_circle(
            draw,
            (width // 2, circle_center_y),
            inner_radius,
            fill="#FFFFFF",
            outline="#000000",
            width=3,
        )

        # Draw "ALL" text in center
        all_font = get_template_font("Arial", size=42, bold=True)
        draw_text(
            draw,
            "ALL",
            (width // 2, circle_center_y - 15),
            all_font,
            anchor="mm",
        )

        colors_font = get_template_font("Arial", size=20, bold=True)
        draw_text(
            draw,
            "COLORS",
            (width // 2, circle_center_y + 15),
            colors_font,
            anchor="mm",
        )
    else:
        # Two-color rent: draw concentric circles
        if len(card.colors) >= 2:
            color1 = color_map.get(card.colors[0], "#228B22")
            color2 = color_map.get(card.colors[1], "#FF1493")

            # Draw outer circle (first color)
            draw_circle(
                draw,
                (width // 2, circle_center_y),
                outer_radius,
                fill=color1,
                outline="#000000",
                width=4,
            )

            # Draw inner circle (second color)
            draw_circle(
                draw,
                (width // 2, circle_center_y),
                inner_radius,
                fill=color2,
                outline="#000000",
                width=3,
            )
        elif len(card.colors) == 1:
            # Single color (fallback)
            color = color_map.get(card.colors[0], "#228B22")
            draw_circle(
                draw,
                (width // 2, circle_center_y),
                outer_radius,
                fill=color,
                outline="#000000",
                width=4,
            )

    # Draw description
    if card.description:
        desc_config = rent_config["layout"]["description_area"]
        desc_font = get_template_font("Arial", size=12)
        desc_x = (width - desc_config["width"]) // 2
        desc_y = desc_config["start_y"]

        draw_multiline_text(
            draw,
            card.description,
            (desc_x, desc_y),
            desc_font,
            max_width=desc_config["width"],
            align="center",
        )

    # Draw value badges (top-left and bottom-right)
    badge_config = global_config["value_badge"]
    if card.value:
        # Top-left badge
        tl_pos = badge_config["position"]["top_left"]
        draw_value_badge(
            draw,
            card.value,
            (tl_pos["x"], tl_pos["y"]),
            diameter=badge_config["diameter"],
        )

        # Bottom-right badge
        br_pos = badge_config["position"]["bottom_right"]
        br_x = width + br_pos["x"]
        br_y = height + br_pos["y"]
        draw_value_badge(
            draw, card.value, (br_x, br_y), diameter=badge_config["diameter"]
        )

    # Draw footer text
    footer_font = get_template_font("Arial", size=10)
    footer_y = 430
    footer_text = "© 1935, 2008 HASBRO"
    draw_text(
        draw,
        footer_text,
        (width // 2, footer_y),
        footer_font,
        color="#505050",
        anchor="mm",
    )

    return img
