"""
Template for rendering property cards.
"""

import json
from pathlib import Path
from PIL import Image
from ..renderer.primitives import (
    create_card_base,
    draw_rounded_rectangle,
    draw_text,
    get_font,
)
from ..renderer.elements import draw_value_badge, draw_property_rent_row
from ..models import PropertyCard


def load_design_tokens():
    """Load design tokens from JSON file."""
    tokens_path = Path(__file__).parent.parent.parent / "design_tokens.json"
    with open(tokens_path) as f:
        return json.load(f)


def render_property_card(card: PropertyCard) -> Image.Image:
    """
    Render a property card.

    Args:
        card: PropertyCard instance

    Returns:
        Rendered card image
    """
    tokens = load_design_tokens()
    global_config = tokens["global"]
    property_config = tokens["card_types"]["property"]

    # Get color for property set
    color_map = global_config["colors"]["property_sets"]
    header_color = color_map.get(card.color, "#228B22")

    # Create card base
    width = global_config["card"]["width"]
    height = global_config["card"]["height"]
    corner_radius = global_config["card"]["corner_radius"]
    bg_color = property_config["colors"]["background"]

    img, draw = create_card_base(width, height, bg_color, corner_radius)

    # Draw header bar with property name
    header_height = property_config["layout"]["header_bar"]["height"]
    header_padding = property_config["layout"]["header_bar"]["padding"]

    draw_rounded_rectangle(
        draw,
        (header_padding, header_padding, width - header_padding, header_height),
        radius=10,
        fill=header_color,
        outline="#000000",
        width=2,
    )

    # Draw property name in header
    header_font = get_font("Arial", size=18, bold=True)
    property_text = card.property_name or card.title
    text_y = header_padding + header_height // 2
    draw_text(
        draw, property_text.upper(), (width // 2, text_y), header_font, anchor="mm"
    )

    # Draw "RENT" label
    rent_label_y = property_config["layout"]["rent_section"]["start_y"] - 30
    rent_label_font = get_font("Arial", size=24, bold=True)
    draw_text(draw, "RENT", (width // 2, rent_label_y), rent_label_font, anchor="mm")

    # Draw rent table
    rent_start_y = property_config["layout"]["rent_section"]["start_y"]
    row_height = property_config["layout"]["rent_section"]["row_height"]

    label_font = get_font("Arial", size=12)
    label_y = rent_start_y - 20
    draw_text(
        draw,
        "(No. of properties\nowned in set)",
        (width // 2, label_y),
        label_font,
        anchor="mm",
    )

    for i, (num_props, rent_value) in enumerate(card.rent_values):
        y_pos = rent_start_y + i * row_height
        draw_property_rent_row(
            draw,
            y_pos,
            num_props,
            rent_value,
            icon_color=header_color,
            x_start=30,
            row_width=width - 60,
        )

    # Draw value badge
    badge_config = global_config["value_badge"]
    badge_pos = badge_config["position"]["top_left"]
    if card.value:
        draw_value_badge(
            draw,
            card.value,
            (badge_pos["x"], badge_pos["y"]),
            diameter=badge_config["diameter"],
        )

    # Draw footer text
    footer_font = get_font("Arial", size=10)
    footer_y = property_config["layout"]["footer_text"]["y"]
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
