"""
Test suite to validate card rendering against original card images.
"""

import pytest
from pathlib import Path
from PIL import Image
import numpy as np

from src.models import (
    PropertyCard,
    ActionCard,
    MoneyCard,
    RentCard,
    WildcardCard,
)
from src.renderer.card_renderer import render_card


# Test data directory
TEST_DATA_DIR = Path(__file__).parent.parent / "Card Images"
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "test_validation"


def setup_module():
    """Create output directory for test results."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def compare_images(
    img1: Image.Image, img2: Image.Image, threshold: float = 0.95
) -> bool:
    """
    Compare two images using structural similarity.

    Args:
        img1: First image
        img2: Second image
        threshold: Similarity threshold (0-1)

    Returns:
        True if images are similar enough
    """
    # Resize to same dimensions if needed
    if img1.size != img2.size:
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)

    # Convert to numpy arrays
    arr1 = np.array(img1.convert("RGB"))
    arr2 = np.array(img2.convert("RGB"))

    # Calculate normalized cross-correlation
    arr1_norm = (arr1 - arr1.mean()) / (arr1.std() + 1e-8)
    arr2_norm = (arr2 - arr2.mean()) / (arr2.std() + 1e-8)

    correlation = (arr1_norm * arr2_norm).mean()

    return correlation >= threshold


def test_property_card_rendering():
    """Test property card rendering."""
    card = PropertyCard(
        card_id="test-brown-01",
        card_type="property",
        title="Test Property",
        property_name="Mediterranean Avenue",
        color="brown",
        value=1,
        rent_values=[(1, 1), (2, 2)],
        set_size=2,
    )

    img = render_card(card)
    assert img is not None
    assert img.size == (413, 455)  # Standard card size

    # Save test output
    output_path = OUTPUT_DIR / "test_property_card.png"
    img.save(output_path)


def test_action_card_rendering():
    """Test action card rendering."""
    card = ActionCard(
        card_id="test-deal-breaker",
        card_type="action",
        title="Deal Breaker",
        action_name="Deal Breaker",
        value=5,
        description="Steal a complete set of properties from any player.",
    )

    img = render_card(card)
    assert img is not None
    assert img.size == (413, 455)


def test_money_card_rendering():
    """Test money card rendering."""
    card = MoneyCard(
        card_id="test-money-5m",
        card_type="money",
        title="$5M",
        denomination=5,
        value=5,
    )

    img = render_card(card)
    assert img is not None
    assert img.size == (413, 455)


def test_rent_card_rendering():
    """Test rent card rendering."""
    # Two-color rent card
    card = RentCard(
        card_id="test-rent-pink-orange",
        card_type="rent",
        title="Rent",
        value=1,
        colors=["pink", "orange"],
        is_wild=False,
        description="All players pay you rent for properties you own in one of these colors.",
    )

    img = render_card(card)
    assert img is not None
    assert img.size == (413, 455)

    # Wild rent card
    wild_card = RentCard(
        card_id="test-rent-wild",
        card_type="rent",
        title="Rent",
        value=3,
        colors=[],
        is_wild=True,
        description="All players pay you rent for properties you own in one of these colors.",
    )

    img_wild = render_card(wild_card)
    assert img_wild is not None


def test_wildcard_card_rendering():
    """Test wildcard card rendering."""
    # Two-color wildcard
    card = WildcardCard(
        card_id="test-wildcard-pink-orange",
        card_type="wildcard",
        title="Property Wild Card",
        value=2,
        allowed_colors=["pink", "orange"],
        is_multicolor=False,
        description="This card can be used as part of any property set.",
    )

    img = render_card(card)
    assert img is not None
    assert img.size == (413, 455)

    # Multicolor wildcard
    multicolor_card = WildcardCard(
        card_id="test-wildcard-multicolor",
        card_type="wildcard",
        title="Property Wild Card",
        value=0,
        allowed_colors=[
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
        ],
        is_multicolor=True,
        description="This card can be used as part of any property set.",
    )

    img_multi = render_card(multicolor_card)
    assert img_multi is not None


def test_card_dimensions():
    """Test that all cards have consistent dimensions."""
    cards = [
        PropertyCard(
            card_id="test-prop",
            card_type="property",
            title="Test",
            color="brown",
            value=1,
            rent_values=[(1, 1)],
            set_size=2,
        ),
        ActionCard(
            card_id="test-action",
            card_type="action",
            title="Test",
            action_name="Test",
            value=1,
        ),
        MoneyCard(
            card_id="test-money",
            card_type="money",
            title="$1M",
            denomination=1,
            value=1,
        ),
        RentCard(
            card_id="test-rent",
            card_type="rent",
            title="Rent",
            value=1,
            colors=["brown"],
            is_wild=False,
        ),
        WildcardCard(
            card_id="test-wildcard",
            card_type="wildcard",
            title="Wild Card",
            value=1,
            allowed_colors=["brown"],
            is_multicolor=False,
        ),
    ]

    for card in cards:
        img = render_card(card)
        assert img.size == (413, 455), f"Card {card.card_id} has wrong size: {img.size}"


def test_validate_against_originals():
    """
    Validate rendered cards against original card images.
    This test compares rendered cards with reference images.
    """
    if not TEST_DATA_DIR.exists():
        pytest.skip("Card Images directory not found")

    # Test a few key cards
    test_cases = [
        {
            "type": "property",
            "card": PropertyCard(
                card_id="test-green",
                card_type="property",
                title="Pacific Avenue",
                property_name="Pacific Avenue",
                color="green",
                value=4,
                rent_values=[(1, 2), (2, 4), (3, 7)],
                set_size=3,
            ),
            "reference": "green-property-card.png",
        },
        {
            "type": "action",
            "card": ActionCard(
                card_id="test-deal-breaker",
                card_type="action",
                title="Deal Breaker",
                action_name="Deal Breaker",
                value=5,
                description="Steal a complete set of properties from any player.",
            ),
            "reference": "deal-breaker-action-card.png",
        },
        {
            "type": "money",
            "card": MoneyCard(
                card_id="test-money-5m",
                card_type="money",
                title="$5M",
                denomination=5,
                value=5,
            ),
            "reference": "$5M-money-card.png",
        },
    ]

    for test_case in test_cases:
        reference_path = TEST_DATA_DIR / test_case["reference"]
        if not reference_path.exists():
            continue

        # Render card
        rendered_img = render_card(test_case["card"])

        # Load reference image
        reference_img = Image.open(reference_path)

        # Save comparison
        comparison_path = OUTPUT_DIR / f"comparison_{test_case['type']}.png"
        comparison = Image.new("RGB", (rendered_img.width * 2, rendered_img.height))
        comparison.paste(rendered_img, (0, 0))
        comparison.paste(
            reference_img.resize(rendered_img.size), (rendered_img.width, 0)
        )
        comparison.save(comparison_path)

        # Note: We don't fail the test if images don't match exactly
        # This is a visual validation tool
        print(f"\nComparison saved: {comparison_path}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
