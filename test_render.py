"""
Test script to render sample cards.
"""

from pathlib import Path
from src.models import PropertyCard, ActionCard, MoneyCard
from src.renderer.card_renderer import render_card


def main():
    """Render a few sample cards to test the rendering engine."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    print("Rendering sample cards...\n")

    # Test property card
    print("1. Rendering Green Property Card...")
    green_property = PropertyCard(
        card_id="green-01",
        card_type="property",
        title="North Carolina Avenue",
        property_name="North Carolina Avenue",
        color="green",
        value=4,
        rent_values=[(1, 2), (2, 4), (3, 7)],
        set_size=3,
    )
    render_card(green_property, output_dir / "test_green_property.png")
    print("   ✓ Saved to output/test_green_property.png")

    # Test action card
    print("\n2. Rendering Deal Breaker Action Card...")
    deal_breaker = ActionCard(
        card_id="action-deal-breaker",
        card_type="action",
        title="Deal Breaker",
        action_name="Deal Breaker",
        value=5,
        description="Steal a complete set of properties from any player. (Includes any buildings.) Play into center to use.",
    )
    render_card(deal_breaker, output_dir / "test_deal_breaker.png")
    print("   ✓ Saved to output/test_deal_breaker.png")

    # Test money card
    print("\n3. Rendering $5M Money Card...")
    five_million = MoneyCard(
        card_id="money-5m",
        card_type="money",
        title="$5M",
        denomination=5,
        value=5,
    )
    render_card(five_million, output_dir / "test_5m_money.png")
    print("   ✓ Saved to output/test_5m_money.png")

    # Test another property color
    print("\n4. Rendering Dark Blue Property Card...")
    dark_blue_property = PropertyCard(
        card_id="dark-blue-01",
        card_type="property",
        title="Boardwalk",
        property_name="Boardwalk",
        color="dark_blue",
        value=4,
        rent_values=[(1, 3), (2, 8)],
        set_size=2,
    )
    render_card(dark_blue_property, output_dir / "test_dark_blue_property.png")
    print("   ✓ Saved to output/test_dark_blue_property.png")

    print("\n✅ All test cards rendered successfully!")
    print(f"Check the '{output_dir}' directory to see the results.")


if __name__ == "__main__":
    main()
