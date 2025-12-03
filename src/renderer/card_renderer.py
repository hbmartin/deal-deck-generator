"""
Main card rendering engine.
Dispatches to appropriate template based on card type.
"""

from PIL import Image
from pathlib import Path
from ..models import Card


def render_card(card: Card, output_path: str | Path | None = None) -> Image.Image:
    """
    Render a card to an image.

    Args:
        card: Card instance to render
        output_path: Optional path to save rendered image

    Returns:
        Rendered PIL Image

    Raises:
        ValueError: If card type is not supported
    """
    if card.card_type == "property":
        from ..templates.property_template import render_property_card

        img = render_property_card(card)

    elif card.card_type == "action":
        from ..templates.action_template import render_action_card

        img = render_action_card(card)

    elif card.card_type == "money":
        from ..templates.money_template import render_money_card

        img = render_money_card(card)

    elif card.card_type == "rent":
        # TODO: Implement rent card template
        raise NotImplementedError("Rent card rendering not yet implemented")

    elif card.card_type == "wildcard":
        # TODO: Implement wildcard template
        raise NotImplementedError("Wildcard card rendering not yet implemented")

    else:
        raise ValueError(f"Unknown card type: {card.card_type}")

    # Save if output path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)

    return img
