"""Theme system: overlay token merge, Chicago pure-reskin, and render smoke."""

import xml.etree.ElementTree as ET

import pytest

from src.data.loader import load_deck
from src.data.themes import (
    available_themes,
    load_theme_tokens,
    theme_cards_path,
)
from src.svg.cards import build_card
from src.tokens import load_tokens

PROPERTY_COLORS = [
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
]


def _design_signature(deck) -> dict[str, tuple]:
    """Structural fingerprint of a deck, ignoring names/text/colors."""
    return {
        c.metadata["design_id"]: (
            c.card_type,
            c.value,
            deck.quantity_of(c.metadata["design_id"]),
        )
        for c in deck.unique_designs()
    }


def test_classic_and_chicago_registered():
    assert {"classic", "chicago"} <= set(available_themes())


def test_chicago_is_pure_reskin_of_classic():
    """Same ids, types, values, and quantities as classic — only labels differ."""
    classic = load_deck(theme_cards_path("classic"))
    chicago = load_deck(theme_cards_path("chicago"))
    assert _design_signature(chicago) == _design_signature(classic)


def test_chicago_has_new_property_names():
    chicago = load_deck(theme_cards_path("chicago"))
    names = {c.title for c in chicago.by_type("property")}
    assert "Willis Tower" in names
    assert "Mediterranean Avenue" not in names


def test_chicago_footer_branding():
    chicago = load_deck(theme_cards_path("chicago"))
    assert chicago.config.footer_text == "WINDY CITY DEAL"


def test_overlay_merges_onto_base():
    base = load_tokens()
    chicago = load_theme_tokens("chicago")
    # Overlay changed the palette...
    assert chicago.property_color("dark_blue") != base.property_color("dark_blue")
    # ...but inherited base geometry, fonts, and type scale untouched.
    assert chicago.corner_radius == base.corner_radius
    assert chicago.font("body").stack == base.font("body").stack
    assert chicago.size("badge_value") == base.size("badge_value")
    # ...and every property color is still present and well-formed.
    for color in PROPERTY_COLORS:
        entry = chicago.property_color(color)
        assert set(entry) == {"fill", "text"}
        assert entry["fill"].startswith("#")


def test_classic_tokens_equal_base():
    """classic has no overlay, so it resolves to the base tokens unchanged."""
    assert load_theme_tokens("classic").raw == load_tokens().raw


@pytest.mark.parametrize("theme", ["classic", "chicago"])
def test_every_design_builds_valid_svg(theme):
    deck = load_deck(theme_cards_path(theme))
    tokens = load_theme_tokens(theme)
    for card in deck.unique_designs():
        data = build_card(card, deck, tokens).to_bytes()
        # Parses as XML and is a non-trivial SVG document.
        root = ET.fromstring(data)
        assert root.tag.endswith("svg")
