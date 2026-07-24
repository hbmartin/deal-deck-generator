"""Theme-aware card-back configuration and SVG structure."""

import xml.etree.ElementTree as ET

import pytest

from src.data.loader import load_deck
from src.data.themes import load_theme_tokens, theme_cards_path
from src.models.deck import CardBackConfig, Deck, DeckConfig
from src.svg.card_back import build_card_back

THEME_TITLES = {
    "arizona": "ARIZONA DEAL",
    "classic": "DEAL",
    "chicago": "WINDY CITY DEAL",
    "oaxaca": "OAXACA DEAL",
}


def _elements_with_role(root: ET.Element, role: str) -> list[ET.Element]:
    return [element for element in root.iter() if element.get("data-role") == role]


def test_card_back_config_normalizes_and_rejects_blank_titles():
    assert CardBackConfig(title="  WINDY   CITY DEAL ").title == "WINDY CITY DEAL"
    with pytest.raises(ValueError, match="must not be blank"):
        CardBackConfig(title=" \n ")


def test_loader_defaults_card_back_title_for_older_theme_files(tmp_path):
    cards_path = tmp_path / "cards.yaml"
    cards_path.write_text("deck: {}\n", encoding="utf-8")

    assert load_deck(cards_path).config.card_back.title == "DEAL"


@pytest.mark.parametrize(("theme", "title"), THEME_TITLES.items())
def test_builtin_theme_card_back_titles(theme, title):
    deck = load_deck(theme_cards_path(theme))

    assert deck.config.card_back.title == title


@pytest.mark.parametrize("theme", THEME_TITLES)
def test_card_back_tokens_reference_ten_unique_property_colors(theme):
    tokens = load_theme_tokens(theme)
    style = tokens.card_back

    assert len(style.accent_order) == 10
    assert len(set(style.accent_order)) == 10
    assert tokens.property_color(style.background_property)["fill"].startswith("#")
    assert all(tokens.property_color(color) for color in style.accent_order)


@pytest.mark.parametrize("theme", THEME_TITLES)
def test_card_back_svg_is_valid_deterministic_and_rotationally_balanced(theme):
    deck = load_deck(theme_cards_path(theme))
    tokens = load_theme_tokens(theme)
    first = build_card_back(deck, tokens).to_bytes()
    second = build_card_back(deck, tokens).to_bytes()
    root = ET.fromstring(first)  # noqa: S314 - parses trusted generated SVG

    assert first == second
    assert len(first) < 300_000
    assert root.get("viewBox") == "0 0 732 1101"

    ids = [element.get("id") for element in root.iter() if element.get("id")]
    assert len(ids) == len(set(ids))

    upright = _elements_with_role(root, "card-back-title")
    opposite = _elements_with_role(root, "card-back-title-opposite")
    assert [element.text for element in upright] == [deck.config.card_back.title]
    assert [element.text for element in opposite] == [deck.config.card_back.title]
    assert upright[0].get("transform") is None
    assert opposite[0].get("transform") == "rotate(180 366 550.5)"

    ring = _elements_with_role(root, "card-back-accent-ring")[0]
    segments = [child for child in ring if child.tag.endswith("path")]
    fills = [segment.get("fill") for segment in segments]
    assert len(fills) == 20
    assert fills[:10] == fills[10:]


def test_theme_card_backs_resolve_distinct_art_and_ornaments():
    rendered = {
        theme: build_card_back(
            load_deck(theme_cards_path(theme)),
            load_theme_tokens(theme),
        ).to_bytes()
        for theme in THEME_TITLES
    }

    assert len(set(rendered.values())) == len(THEME_TITLES)
    assert b"guilloche-wave-card-back" in rendered["classic"]
    assert b"guilloche-wave-card-back" in rendered["chicago"]
    assert b"mitla-step-motif-card-back" in rendered["oaxaca"]
    assert b"agave-medallion-leaf-card-back" in rendered["oaxaca"]
    assert b"desert-dune-motif-card-back" in rendered["arizona"]
    assert b"band-corner-saguaro-card-back" in rendered["arizona"]
    assert b"sunburst-medallion-ray-card-back" in rendered["arizona"]


def test_card_back_rejects_title_that_cannot_fit():
    deck = Deck(
        cards=[],
        config=DeckConfig(card_back=CardBackConfig(title="W" * 200)),
    )

    with pytest.raises(ValueError, match="cannot fit"):
        build_card_back(deck)
