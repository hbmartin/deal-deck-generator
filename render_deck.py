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

    # Configuration mapping for card types
    CARD_TYPE_CONFIG = {
        "property": ("property_cards", create_property_card_instances),
        "action": ("action_cards", create_action_card_instances),
        "money": ("money_cards", create_money_card_instances),
        "rent": ("rent_cards", create_rent_card_instances),
        "wildcard": ("wildcard_cards", create_wildcard_instances),
    }

    # Render cards using configuration mapping
    for card_type, (yaml_key, creator_func) in CARD_TYPE_CONFIG.items():
        if card_type in types_to_render:
            print(f"\nRendering {card_type} cards...")
            cards = creator_func(card_defs[yaml_key])
            for card in cards:
                output_path = output_dir / f"{card.card_id}.{args.format}"
                render_card(card, output_path)
                stats[card_type] += 1
            print(f"  ✓ Rendered {stats[card_type]} {card_type} cards")

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
