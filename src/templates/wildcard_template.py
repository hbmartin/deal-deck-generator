"""
Template for rendering wildcard property cards.
"""

import json
from pathlib import Path
from PIL import Image
from ..renderer.primitives import (
    create_card_base,
    draw_text,
    draw_multiline_text,
)
from ..renderer.elements import draw_value_badge, draw_color_stripes
from ..models import WildcardCard
from .utils import get_template_font


def load_design_tokens():
    """Load design tokens from JSON file."""
    tokens_path = Path(__file__).parent.parent.parent / "design_tokens.json"
    with open(tokens_path) as f:
        return json.load(f)


def render_wildcard_card(card: WildcardCard) -> Image.Image:
    """
    Render a wildcard property card.

    Args:
        card: WildcardCard instance

    Returns:
        Rendered card image
    """
    tokens = load_design_tokens()
    global_config = tokens["global"]
    wildcard_config = tokens["card_types"]["wildcard"]

    # Create card base
    width = global_config["card"]["width"]
    height = global_config["card"]["height"]
    corner_radius = global_config["card"]["corner_radius"]
    bg_color = wildcard_config["colors"]["background"]

    img, draw = create_card_base(width, height, bg_color, corner_radius)

    # Get color map
    color_map = global_config["colors"]["property_sets"]

    # Draw color stripe header
    stripe_config = wildcard_config["layout"]["color_stripe_header"]
    stripe_y = stripe_config["y"]
    stripe_height = stripe_config["height"]

    if card.is_multicolor:
        # Multicolor wildcard: draw all 10 colors
        all_colors = [
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
        stripe_colors = [color_map.get(c, "#228B22") for c in all_colors]
    else:
        # Two-color wildcard: draw the two allowed colors
        stripe_colors = [color_map.get(c, "#228B22") for c in card.allowed_colors[:2]]

    draw_color_stripes(
        draw,
        stripe_colors,
        stripe_y,
        stripe_height,
        x_start=30,
        x_end=width - 30,
    )

    # Draw "PROPERTY WILD CARD" title
    title_y = wildcard_config["layout"]["title_bar"]["y"]
    title_font = get_template_font("Arial", size=16, bold=True)
    title_text = card.title.upper() if card.title else "PROPERTY WILD CARD"
    draw_text(draw, title_text, (width // 2, title_y), title_font, anchor="mm")

    # Draw character/icon area (simplified as text for now)
    char_config = wildcard_config["layout"]["character_area"]
    char_y = char_config["center_y"]

    # Draw "WILD" text in large font
    wild_font = get_template_font("Arial", size=64, bold=True)
    draw_text(
        draw,
        "WILD",
        (width // 2, char_y),
        wild_font,
        color="#505050",
        anchor="mm",
    )

    # Draw description
    if card.description:
        desc_config = wildcard_config["layout"]["description_area"]
        desc_font = get_template_font("Arial", size=11)
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

    # Draw value badge (top-left only for wildcards)
    badge_config = global_config["value_badge"]
    if card.value:
        tl_pos = badge_config["position"]["top_left"]
        draw_value_badge(
            draw,
            card.value,
            (tl_pos["x"], tl_pos["y"]),
            diameter=badge_config["diameter"],
        )

    # Draw footer text
    footer_font = get_template_font("Arial", size=10)
    footer_y = wildcard_config["layout"]["footer_text"]["y"]
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
