#!/usr/bin/env python3
"""
CLI tool to render card deck from YAML definitions.
"""

import argparse
from pathlib import Path
from src.data import (
    load_card_definitions,
    create_property_card_instances,
    create_action_card_instances,
    create_money_card_instances,
    create_rent_card_instances,
    create_wildcard_instances,
)
from src.renderer.card_renderer import render_card


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
    try:
        print(f"Loading card definitions from {yaml_path}...")
        card_defs = load_card_definitions(yaml_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    except Exception as e:
        print(f"Error loading card definitions: {e}")
        return

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
