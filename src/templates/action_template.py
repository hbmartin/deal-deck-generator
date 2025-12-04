"""
Template for rendering action cards.
"""

import json
from pathlib import Path
from PIL import Image
from ..renderer.primitives import (
    create_card_base,
    draw_text,
    draw_multiline_text,
)
from ..renderer.elements import draw_value_badge, draw_decorative_border, draw_circle
from ..models import ActionCard
from .utils import get_template_font


def load_design_tokens():
    """Load design tokens from JSON file."""
    tokens_path = Path(__file__).parent.parent.parent / "design_tokens.json"
    with open(tokens_path) as f:
        return json.load(f)


def render_action_card(card: ActionCard) -> Image.Image:
    """
    Render an action card.

    Args:
        card: ActionCard instance

    Returns:
        Rendered card image
    """
    tokens = load_design_tokens()
    global_config = tokens["global"]
    action_config = tokens["card_types"]["action"]

    # Create card base
    width = global_config["card"]["width"]
    height = global_config["card"]["height"]
    corner_radius = global_config["card"]["corner_radius"]
    bg_color = action_config["colors"]["background"]

    img, draw = create_card_base(width, height, bg_color, corner_radius)

    # Draw decorative border
    draw_decorative_border(img, draw, border_width=15, pattern="chain_link")

    # Draw "ACTION CARD" title bar
    title_y = action_config["layout"]["title_bar"]["y"]
    title_font = get_template_font("Arial", size=16, bold=True)
    draw_text(draw, "ACTION CARD", (width // 2, title_y), title_font, anchor="mm")

    # Draw title circle with action name
    circle_config = action_config["layout"]["title_circle"]
    circle_center_y = circle_config["center_y"]
    circle_radius = circle_config["diameter"] // 2

    draw_circle(
        draw,
        (width // 2, circle_center_y),
        circle_radius,
        fill=action_config["colors"]["circle_bg"],
        outline="#000000",
        width=circle_config["border_width"],
    )

    # Draw action name in circle
    action_font = get_template_font("Arial", size=28, bold=True)
    action_text = card.action_name or card.title

    # Split long titles into multiple lines
    if len(action_text) > 12:
        words = action_text.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        draw_text(
            draw,
            line1.upper(),
            (width // 2, circle_center_y - 20),
            action_font,
            anchor="mm",
        )
        draw_text(
            draw,
            line2.upper(),
            (width // 2, circle_center_y + 20),
            action_font,
            anchor="mm",
        )
    else:
        draw_text(
            draw,
            action_text.upper(),
            (width // 2, circle_center_y),
            action_font,
            anchor="mm",
        )

    # Draw description
    if card.description:
        desc_config = action_config["layout"]["description_area"]
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
    footer_y = action_config["layout"]["footer_text"]["y"]
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
