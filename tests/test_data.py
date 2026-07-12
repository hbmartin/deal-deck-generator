"""Deck data invariants: counts, names, and wildcard rent derivation.

Composition is asserted per theme via EXPECTED: the base themes are the standard
106-card deck, while chicago also pulls in the 38-card expansion set (see
``include: [expansion]`` in themes/chicago/cards.yaml). The rent-derivation and
quantity self-consistency invariants hold for *every* theme. The name-specific
assertions are true only for the classic Atlantic-City deck and use the classic
``deck`` fixture.
"""

from collections import Counter

import pytest

from src.data.loader import load_deck
from src.data.themes import available_themes, theme_cards_path

# Base 106-card composition, shared by every pure-reskin theme.
_BASE_PER_TYPE = {"property": 28, "action": 34, "rent": 13, "wildcard": 11, "money": 20}
_BASE = {"total": 106, "designs": 58, "per_type": _BASE_PER_TYPE}

EXPECTED = {
    "classic": _BASE,
    # chicago = base + expansion (29 designs / 38 physical, all action cards).
    "chicago": {
        "total": 144,
        "designs": 87,
        "per_type": {**_BASE_PER_TYPE, "action": 34 + 38},
    },
}


@pytest.fixture(params=available_themes())
def named_deck(request):
    """(theme_name, loaded deck) for each available theme (parametrized)."""
    return request.param, load_deck(theme_cards_path(request.param))


def test_expected_covers_every_theme():
    # Adding a theme must add its expected composition here, on purpose.
    assert set(EXPECTED) == set(available_themes())


def test_total_card_count(named_deck):
    name, deck = named_deck
    assert len(deck.cards) == EXPECTED[name]["total"]


def test_per_type_counts(named_deck):
    name, deck = named_deck
    counts = Counter(c.card_type for c in deck.cards)
    assert counts == EXPECTED[name]["per_type"]


def test_unique_design_count(named_deck):
    name, deck = named_deck
    assert len(deck.unique_designs()) == EXPECTED[name]["designs"]


def test_wildcard_halves_derive_from_property_tables(named_deck):
    _name, deck = named_deck
    props = {c.color: c for c in deck.by_type("property")}
    for card in deck.by_type("wildcard"):
        if card.is_multicolor:
            assert "halves" not in card.metadata
            continue
        halves = card.metadata["halves"]
        assert [h["color"] for h in halves] == card.allowed_colors
        for half in halves:
            prop = props[half["color"]]
            assert half["set_size"] == prop.set_size
            assert half["rent_values"] == prop.rent_values


def test_design_quantities_sum_to_deck(named_deck):
    _name, deck = named_deck
    total = sum(
        deck.quantity_of(c.metadata["design_id"]) for c in deck.unique_designs()
    )
    assert total == len(deck.cards)


# --- classic-only name assertions ---


def test_railroads_and_utilities_are_named(deck):
    names = {c.title for c in deck.by_type("property")}
    assert {
        "Reading Railroad",
        "Pennsylvania Railroad",
        "B. & O. Railroad",
        "Short Line",
        "Electric Company",
        "Water Works",
    } <= names


def test_brown_set_is_mediterranean_and_baltic(deck):
    browns = [c for c in deck.by_type("property") if c.color == "brown"]
    assert sorted(c.title for c in browns) == ["Baltic Avenue", "Mediterranean Avenue"]
