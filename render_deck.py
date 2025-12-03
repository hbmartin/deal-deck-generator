#!/usr/bin/env python3
"""
CLI tool to render card deck from YAML definitions.
"""

import argparse
import yaml
from pathlib import Path
from src.models import PropertyCard, ActionCard, MoneyCard, RentCard, WildcardCard
from src.renderer.card_renderer import render_card


def load_card_definitions(yaml_path: Path) -> dict:
    """Load card definitions from YAML file."""
    with open(yaml_path) as f:
        return yaml.safe_load(f)


def create_property_card_instances(prop_defs: list) -> list:
    """Create PropertyCard instances from YAML definitions."""
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


def create_action_card_instances(action_defs: list) -> list:
    """Create ActionCard instances from YAML definitions."""
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


def create_money_card_instances(money_defs: list) -> list:
    """Create MoneyCard instances from YAML definitions."""
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


def create_rent_card_instances(rent_defs: list) -> list:
    """Create RentCard instances from YAML definitions."""
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


def create_wildcard_instances(wildcard_defs: list) -> list:
    """Create WildcardCard instances from YAML definitions."""
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


def main():
    parser = argparse.ArgumentParser(
        description="Render card deck from YAML definitions"
    )
    parser.add_argument(
        "--cards",
        "-c",
        type=str,
        default="cards.yaml",
        help="Path to cards YAML file (default: cards.yaml)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="output/deck",
        help="Output directory for rendered cards (default: output/deck)",
    )
    parser.add_argument(
        "--types",
        "-t",
        nargs="+",
        choices=["property", "action", "money", "rent", "wildcard", "all"],
        default=["all"],
        help="Card types to render (default: all)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["png", "webp"],
        default="png",
        help="Output image format (default: png)",
    )

    args = parser.parse_args()

    # Load card definitions
    yaml_path = Path(args.cards)
    if not yaml_path.exists():
        print(f"Error: Card definitions file not found: {yaml_path}")
        return

    print(f"Loading card definitions from {yaml_path}...")
    card_defs = load_card_definitions(yaml_path)

    # Determine which card types to render
    types_to_render = set(args.types)
    if "all" in types_to_render:
        types_to_render = {"property", "action", "money", "rent", "wildcard"}

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Track statistics
    stats = {"property": 0, "action": 0, "money": 0, "rent": 0, "wildcard": 0}

    # Render property cards
    if "property" in types_to_render:
        print("\nRendering property cards...")
        property_cards = create_property_card_instances(card_defs["property_cards"])
        for card in property_cards:
            output_path = output_dir / f"{card.card_id}.{args.format}"
            render_card(card, output_path)
            stats["property"] += 1
        print(f"  ✓ Rendered {stats['property']} property cards")

    # Render action cards
    if "action" in types_to_render:
        print("\nRendering action cards...")
        action_cards = create_action_card_instances(card_defs["action_cards"])
        for card in action_cards:
            output_path = output_dir / f"{card.card_id}.{args.format}"
            render_card(card, output_path)
            stats["action"] += 1
        print(f"  ✓ Rendered {stats['action']} action cards")

    # Render money cards
    if "money" in types_to_render:
        print("\nRendering money cards...")
        money_cards = create_money_card_instances(card_defs["money_cards"])
        for card in money_cards:
            output_path = output_dir / f"{card.card_id}.{args.format}"
            render_card(card, output_path)
            stats["money"] += 1
        print(f"  ✓ Rendered {stats['money']} money cards")

    # Render rent cards
    if "rent" in types_to_render:
        print("\nRendering rent cards...")
        rent_cards = create_rent_card_instances(card_defs["rent_cards"])
        for card in rent_cards:
            output_path = output_dir / f"{card.card_id}.{args.format}"
            render_card(card, output_path)
            stats["rent"] += 1
        print(f"  ✓ Rendered {stats['rent']} rent cards")

    # Render wildcard cards
    if "wildcard" in types_to_render:
        print("\nRendering wildcard cards...")
        wildcard_cards = create_wildcard_instances(card_defs["wildcard_cards"])
        for card in wildcard_cards:
            output_path = output_dir / f"{card.card_id}.{args.format}"
            render_card(card, output_path)
            stats["wildcard"] += 1
        print(f"  ✓ Rendered {stats['wildcard']} wildcard cards")

    # Print summary
    total = sum(stats.values())
    print(f"\n{'='*50}")
    print(f"✅ Successfully rendered {total} cards")
    print(f"   Property: {stats['property']}")
    print(f"   Action: {stats['action']}")
    print(f"   Money: {stats['money']}")
    print(f"   Rent: {stats['rent']}")
    print(f"   Wildcard: {stats['wildcard']}")
    print(f"\nOutput directory: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
