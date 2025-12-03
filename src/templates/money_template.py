"""
Template for rendering money cards.
"""

import json
from pathlib import Path
from PIL import Image
from ..renderer.primitives import create_card_base, draw_text, get_font
from ..renderer.elements import draw_value_badge, draw_decorative_border, draw_circle
from ..models import MoneyCard


def load_design_tokens():
    """Load design tokens from JSON file."""
    tokens_path = Path(__file__).parent.parent.parent / "design_tokens.json"
    with open(tokens_path) as f:
        return json.load(f)


def render_money_card(card: MoneyCard) -> Image.Image:
    """
    Render a money card.

    Args:
        card: MoneyCard instance

    Returns:
        Rendered card image
    """
    tokens = load_design_tokens()
    global_config = tokens["global"]
    money_config = tokens["card_types"]["money"]

    # Create card base
    width = global_config["card"]["width"]
    height = global_config["card"]["height"]
    corner_radius = global_config["card"]["corner_radius"]
    bg_color = money_config["colors"]["background"]

    img, draw = create_card_base(width, height, bg_color, corner_radius)

    # Draw decorative border
    draw_decorative_border(img, draw, border_width=15, pattern="chain_link")

    # Draw large denomination circle
    circle_config = money_config["layout"]["denomination_circle"]
    circle_center_y = circle_config["center_y"]
    circle_radius = circle_config["diameter"] // 2

    draw_circle(
        draw,
        (width // 2, circle_center_y),
        circle_radius,
        fill=money_config["colors"]["circle_bg"],
        outline="#000000",
        width=circle_config["border_width"],
    )

    # Draw denomination text
    denom_font = get_font("Arial", size=60, bold=True)
    denom_text = f"${card.denomination}M"
    draw_text(draw, denom_text, (width // 2, circle_center_y), denom_font, anchor="mm")

    # Draw value badges (top-left and bottom-right)
    badge_config = global_config["value_badge"]

    # Top-left badge
    tl_pos = badge_config["position"]["top_left"]
    draw_value_badge(
        draw,
        card.denomination,
        (tl_pos["x"], tl_pos["y"]),
        diameter=badge_config["diameter"],
    )

    # Bottom-right badge
    br_pos = badge_config["position"]["bottom_right"]
    br_x = width + br_pos["x"]
    br_y = height + br_pos["y"]
    draw_value_badge(
        draw, card.denomination, (br_x, br_y), diameter=badge_config["diameter"]
    )

    # Draw footer text
    footer_font = get_font("Arial", size=10)
    footer_y = money_config["layout"]["footer_text"]["y"]
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
