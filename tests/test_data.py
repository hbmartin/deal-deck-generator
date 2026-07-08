"""Deck data invariants: counts, names, and wildcard rent derivation."""

from collections import Counter


def test_total_card_count(deck):
    assert len(deck.cards) == 106


def test_per_type_counts(deck):
    counts = Counter(c.card_type for c in deck.cards)
    assert counts == {
        "property": 28,
        "action": 34,
        "rent": 13,
        "wildcard": 11,
        "money": 20,
    }


def test_unique_design_count(deck):
    assert len(deck.unique_designs()) == 58


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


def test_wildcard_halves_derive_from_property_tables(deck):
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


def test_design_quantities_sum_to_deck(deck):
    total = sum(
        deck.quantity_of(c.metadata["design_id"]) for c in deck.unique_designs()
    )
    assert total == 106
