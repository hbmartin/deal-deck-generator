"""
Data loading module for parsing YAML card definitions and creating card objects.

This module handles:
- Loading YAML card definition files
- Parsing card definitions
- Creating card model instances from definitions
- Handling quantity multipliers
"""

import yaml
from pathlib import Path
from typing import Literal

from ..models import (
    PropertyCard,
    ActionCard,
    MoneyCard,
    RentCard,
    WildcardCard,
    Card,
)


def load_card_definitions(yaml_path: Path | str) -> dict:
    """
    Load card definitions from a YAML file.

    Args:
        yaml_path: Path to the YAML file containing card definitions

    Returns:
        Dictionary containing card definitions organized by type

    Raises:
        FileNotFoundError: If the YAML file doesn't exist
        yaml.YAMLError: If the YAML file is invalid
    """
    yaml_path = Path(yaml_path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"Card definitions file not found: {yaml_path}")

    with open(yaml_path) as f:
        return yaml.safe_load(f)


def create_property_card_instances(prop_defs: list[dict]) -> list[PropertyCard]:
    """
    Create PropertyCard instances from YAML definitions.

    Args:
        prop_defs: List of property card definition dictionaries

    Returns:
        List of PropertyCard instances

    Example:
        >>> defs = [{"id": "brown-01", "name": "Mediterranean Avenue", ...}]
        >>> cards = create_property_card_instances(defs)
    """
    cards = []
    for prop_def in prop_defs:
        quantity = prop_def.get("quantity", 1)
        for i in range(quantity):
            card_id = f"{prop_def['id']}-{i+1}" if quantity > 1 else prop_def["id"]
            card = PropertyCard(
                card_id=card_id,
                card_type="property",
                title=prop_def["name"],
                property_name=prop_def["name"],
                color=prop_def["color"],
                value=prop_def["value"],
                rent_values=[tuple(rv) for rv in prop_def["rent_values"]],
                set_size=prop_def["set_size"],
            )
            cards.append(card)
    return cards


def create_action_card_instances(action_defs: list[dict]) -> list[ActionCard]:
    """
    Create ActionCard instances from YAML definitions.

    Args:
        action_defs: List of action card definition dictionaries

    Returns:
        List of ActionCard instances
    """
    cards = []
    for action_def in action_defs:
        quantity = action_def.get("quantity", 1)
        for i in range(quantity):
            card_id = f"{action_def['id']}-{i+1}" if quantity > 1 else action_def["id"]
            card = ActionCard(
                card_id=card_id,
                card_type="action",
                title=action_def["name"],
                action_name=action_def["name"],
                value=action_def["value"],
                description=action_def.get("description", ""),
            )
            cards.append(card)
    return cards


def create_money_card_instances(money_defs: list[dict]) -> list[MoneyCard]:
    """
    Create MoneyCard instances from YAML definitions.

    Args:
        money_defs: List of money card definition dictionaries

    Returns:
        List of MoneyCard instances
    """
    cards = []
    for money_def in money_defs:
        denom = money_def["denomination"]
        quantity = money_def.get("quantity", 1)
        for i in range(quantity):
            card_id = f"money-{denom}m-{i+1}" if quantity > 1 else f"money-{denom}m"
            card = MoneyCard(
                card_id=card_id,
                card_type="money",
                title=f"${denom}M",
                denomination=denom,
                value=denom,
            )
            cards.append(card)
    return cards


def create_rent_card_instances(rent_defs: list[dict]) -> list[RentCard]:
    """
    Create RentCard instances from YAML definitions.

    Args:
        rent_defs: List of rent card definition dictionaries

    Returns:
        List of RentCard instances
    """
    cards = []
    for rent_def in rent_defs:
        quantity = rent_def.get("quantity", 1)
        for i in range(quantity):
            card_id = f"{rent_def['id']}-{i+1}" if quantity > 1 else rent_def["id"]
            card = RentCard(
                card_id=card_id,
                card_type="rent",
                title=rent_def["name"],
                value=rent_def["value"],
                description=rent_def.get("description", ""),
                colors=rent_def.get("colors", []),
                is_wild=rent_def.get("is_wild", False),
            )
            cards.append(card)
    return cards


def create_wildcard_instances(wildcard_defs: list[dict]) -> list[WildcardCard]:
    """
    Create WildcardCard instances from YAML definitions.

    Args:
        wildcard_defs: List of wildcard card definition dictionaries

    Returns:
        List of WildcardCard instances
    """
    cards = []
    for wildcard_def in wildcard_defs:
        quantity = wildcard_def.get("quantity", 1)
        for i in range(quantity):
            card_id = (
                f"{wildcard_def['id']}-{i+1}" if quantity > 1 else wildcard_def["id"]
            )
            card = WildcardCard(
                card_id=card_id,
                card_type="wildcard",
                title=wildcard_def["name"],
                value=wildcard_def.get("value", 0),
                description=wildcard_def.get("description", ""),
                allowed_colors=wildcard_def.get("allowed_colors", []),
                is_multicolor=wildcard_def.get("is_multicolor", False),
            )
            cards.append(card)
    return cards


def create_card_instances(
    card_defs: dict,
    card_type: Literal["property", "action", "money", "rent", "wildcard"] | None = None,
) -> list[Card]:
    """
    Create card instances from card definitions dictionary.

    This is a convenience function that creates all card types or a specific type.

    Args:
        card_defs: Dictionary containing card definitions (from load_card_definitions)
        card_type: Optional card type to filter. If None, creates all card types.

    Returns:
        List of Card instances

    Example:
        >>> defs = load_card_definitions("cards.yaml")
        >>> all_cards = create_card_instances(defs)
        >>> property_cards = create_card_instances(defs, card_type="property")
    """
    all_cards = []

    if card_type is None or card_type == "property":
        if "property_cards" in card_defs:
            all_cards.extend(
                create_property_card_instances(card_defs["property_cards"])
            )

    if card_type is None or card_type == "action":
        if "action_cards" in card_defs:
            all_cards.extend(create_action_card_instances(card_defs["action_cards"]))

    if card_type is None or card_type == "money":
        if "money_cards" in card_defs:
            all_cards.extend(create_money_card_instances(card_defs["money_cards"]))

    if card_type is None or card_type == "rent":
        if "rent_cards" in card_defs:
            all_cards.extend(create_rent_card_instances(card_defs["rent_cards"]))

    if card_type is None or card_type == "wildcard":
        if "wildcard_cards" in card_defs:
            all_cards.extend(create_wildcard_instances(card_defs["wildcard_cards"]))

    return all_cards
