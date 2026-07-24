"""Theme system: token overlays, pure reskins, ornaments, and render smoke."""

import xml.etree.ElementTree as ET

import pytest

from src.data.loader import load_deck
from src.data.themes import (
    THEMES_DIR,
    available_fragments,
    available_themes,
    fragment_cards_path,
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


def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first: str, second: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(first), _relative_luminance(second)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


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


def test_builtin_themes_registered():
    assert {"arizona", "classic", "chicago", "oaxaca"} <= set(available_themes())


def test_chicago_base_is_pure_reskin_of_classic():
    """Chicago's BASE cards match classic exactly (ids, types, values, quantities);
    only the property labels and the added expansion set differ.
    """
    classic = load_deck(theme_cards_path("classic"))
    chicago = load_deck(theme_cards_path("chicago"))
    chicago_base = {
        k: v for k, v in _design_signature(chicago).items() if not k.startswith("exp-")
    }
    assert chicago_base == _design_signature(classic)


def test_arizona_base_is_pure_reskin_of_classic():
    classic = load_deck(theme_cards_path("classic"))
    arizona = load_deck(theme_cards_path("arizona"))
    arizona_base = {
        key: value
        for key, value in _design_signature(arizona).items()
        if not key.startswith("exp-")
    }

    assert arizona_base == _design_signature(classic)


def test_oaxaca_is_pure_reskin_of_classic():
    classic = load_deck(theme_cards_path("classic"))
    oaxaca = load_deck(theme_cards_path("oaxaca"))

    assert _design_signature(oaxaca) == _design_signature(classic)
    assert len(oaxaca.cards) == 106
    assert len(oaxaca.unique_designs()) == 58
    assert not any(
        card.metadata["design_id"].startswith("exp-")
        for card in oaxaca.unique_designs()
    )


def test_chicago_includes_expansion():
    """Chicago pulls in the 29 expansion action designs; classic does not."""
    classic = load_deck(theme_cards_path("classic"))
    chicago = load_deck(theme_cards_path("chicago"))
    exp = [
        c
        for c in chicago.unique_designs()
        if c.metadata["design_id"].startswith("exp-")
    ]
    assert len(exp) == 29
    assert all(c.card_type == "action" for c in exp)
    assert {c.value for c in exp} == {3, 4, 5}
    # a doubled design keeps its count; classic stays expansion-free
    assert chicago.quantity_of("exp-gold-digger") == 2
    assert not any(
        c.metadata["design_id"].startswith("exp-") for c in classic.unique_designs()
    )


def test_arizona_includes_expansion():
    arizona = load_deck(theme_cards_path("arizona"))
    expansion = [
        card
        for card in arizona.unique_designs()
        if card.metadata["design_id"].startswith("exp-")
    ]

    assert len(expansion) == 29
    assert all(card.card_type == "action" for card in expansion)
    assert len(arizona.unique_designs()) == 87
    assert len(arizona.cards) == 144


def test_include_merges_shared_fragment():
    """The `include:` directive merges a registered fragment's cards into a deck."""
    assert "expansion" in available_fragments()
    ids = {
        c.metadata["design_id"]
        for c in load_deck(theme_cards_path("chicago")).unique_designs()
    }
    assert "exp-gold-digger" in ids  # defined only in themes/_shared/expansion.yaml


@pytest.mark.parametrize(
    "name",
    ["missing", "expansion/../expansion", str(THEMES_DIR / "_shared" / "expansion")],
)
def test_fragment_loaders_reject_unregistered_names(name):
    with pytest.raises(ValueError, match="unknown fragment"):
        fragment_cards_path(name)


def test_chicago_has_new_property_names():
    chicago = load_deck(theme_cards_path("chicago"))
    names = {c.title for c in chicago.by_type("property")}
    assert "Willis Tower" in names
    assert "Mediterranean Avenue" not in names


def test_chicago_footer_branding():
    chicago = load_deck(theme_cards_path("chicago"))
    assert chicago.config.footer_text == "WINDY CITY DEAL"


def test_oaxaca_property_names_and_footer():
    oaxaca = load_deck(theme_cards_path("oaxaca"))
    expected = {
        "La Noria",
        "Carmen Alto",
        "Jalatlaco",
        "Xochimilco",
        "El Llano",
        "Zócalo",
        "Mercado Benito Juárez",
        "Mercado 20 de Noviembre",
        "Mercado de Artesanías",
        "Museo Textil de Oaxaca",
        "Jardín Etnobotánico",
        "Andador Macedonio Alcalá",
        "Teatro Macedonio Alcalá",
        "Auditorio Guelaguetza",
        "Santa María del Tule",
        "Tlacolula de Matamoros",
        "Cuilápam de Guerrero",
        "Centro Histórico",
        "Mitla",
        "Hierve el Agua",
        "Templo de Santo Domingo",
        "Monte Albán",
        "Santa María Atzompa",
        "San Bartolo Coyotepec",
        "San Martín Tilcajete",
        "Teotitlán del Valle",
        "Mezcal",
        "Tejate",
    }

    assert {card.title for card in oaxaca.by_type("property")} == expected
    assert oaxaca.config.footer_text == "OAXACA DEAL"


def test_arizona_property_names_and_branding():
    arizona = load_deck(theme_cards_path("arizona"))
    expected = {
        "Bisbee",
        "Jerome",
        "Tempe Town Lake",
        "Lake Havasu",
        "Lake Powell",
        "Roosevelt Row",
        "Old Town Scottsdale",
        "Barrio Viejo",
        "Papago Park",
        "Saguaro National Park",
        "Organ Pipe Cactus National Monument",
        "Sedona",
        "Antelope Canyon",
        "Canyon de Chelly National Monument",
        "Petrified Forest National Park",
        "Meteor Crater",
        "Chiricahua National Monument",
        "Mount Lemmon",
        "Mogollon Rim",
        "Humphreys Peak",
        "Monument Valley Navajo Tribal Park",
        "Grand Canyon National Park",
        "Oatman",
        "Kingman",
        "Seligman",
        "Winslow",
        "Colorado River",
        "Salt River",
    }

    assert {card.title for card in arizona.by_type("property")} == expected
    assert arizona.config.footer_text == "ARIZONA DEAL"
    assert arizona.config.card_back.title == "ARIZONA DEAL"


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


def test_oaxaca_palette_tints_and_ornaments():
    oaxaca = load_theme_tokens("oaxaca")
    expected_property = {
        "brown": {"fill": "#7A4335", "text": "#FFFFFF"},
        "light_blue": {"fill": "#83BED3", "text": "#000000"},
        "pink": {"fill": "#B73772", "text": "#FFFFFF"},
        "orange": {"fill": "#E77722", "text": "#000000"},
        "red": {"fill": "#A6322D", "text": "#FFFFFF"},
        "yellow": {"fill": "#E6BF43", "text": "#000000"},
        "green": {"fill": "#4F7C50", "text": "#FFFFFF"},
        "dark_blue": {"fill": "#264B72", "text": "#FFFFFF"},
        "railroad": {"fill": "#24201E", "text": "#FFFFFF"},
        "utility": {"fill": "#AAB7A2", "text": "#000000"},
    }
    expected_tints = {
        1: {"field": "#F7EDC5", "line": "#BFAE74"},
        2: {"field": "#F2CBB5", "line": "#B77A5A"},
        3: {"field": "#D7E4C4", "line": "#899B69"},
        4: {"field": "#C4D8E8", "line": "#768EA8"},
        5: {"field": "#D5B1C2", "line": "#936179"},
        10: {"field": "#E5B54A", "line": "#A77924"},
    }

    assert {
        color: oaxaca.property_color(color) for color in PROPERTY_COLORS
    } == expected_property
    assert {
        value: oaxaca.value_tint(value) for value in expected_tints
    } == expected_tints
    assert oaxaca.ornament.field_pattern == "mitla_step"
    assert oaxaca.ornament.border_corner == "agave"
    assert oaxaca.ornament.money_medallion == "agave"


def test_arizona_palette_tints_chrome_and_ornaments():
    arizona = load_theme_tokens("arizona")
    expected_property = {
        "brown": {"fill": "#8B4A32", "text": "#FFFFFF"},
        "light_blue": {"fill": "#4CB7C5", "text": "#000000"},
        "pink": {"fill": "#B82974", "text": "#FFFFFF"},
        "orange": {"fill": "#B9501C", "text": "#FFFFFF"},
        "red": {"fill": "#9E2F32", "text": "#FFFFFF"},
        "yellow": {"fill": "#E3B23C", "text": "#000000"},
        "green": {"fill": "#2F6B45", "text": "#FFFFFF"},
        "dark_blue": {"fill": "#214A73", "text": "#FFFFFF"},
        "railroad": {"fill": "#2A2724", "text": "#FFFFFF"},
        "utility": {"fill": "#D5C6A1", "text": "#000000"},
    }
    expected_tints = {
        1: {"field": "#F7E8C6", "line": "#B99A68"},
        2: {"field": "#F5C2A4", "line": "#B66B49"},
        3: {"field": "#DDE5C6", "line": "#879667"},
        4: {"field": "#C7E5E5", "line": "#6E9FA5"},
        5: {"field": "#D8B6C9", "line": "#96647D"},
        10: {"field": "#D9A441", "line": "#9D6E22"},
    }

    assert {
        color: arizona.property_color(color) for color in PROPERTY_COLORS
    } == expected_property
    assert {
        value: arizona.value_tint(value) for value in expected_tints
    } == expected_tints
    assert arizona.chrome("property_body") == "#F3E9D7"
    assert arizona.ornament.field_pattern == "desert_dune"
    assert arizona.ornament.border_corner == "saguaro"
    assert arizona.ornament.money_medallion == "sunburst"


def test_oaxaca_property_headers_meet_normal_text_contrast():
    oaxaca = load_theme_tokens("oaxaca")

    for color in PROPERTY_COLORS:
        entry = oaxaca.property_color(color)
        assert _contrast_ratio(entry["fill"], entry["text"]) >= 4.5


def test_arizona_property_headers_meet_normal_text_contrast():
    arizona = load_theme_tokens("arizona")

    for color in PROPERTY_COLORS:
        entry = arizona.property_color(color)
        assert _contrast_ratio(entry["fill"], entry["text"]) >= 4.5


def test_classic_and_chicago_keep_default_ornaments():
    for theme in ("classic", "chicago"):
        ornament = load_theme_tokens(theme).ornament
        assert ornament.field_pattern == "wave"
        assert ornament.border_corner == "rosette"
        assert ornament.money_medallion == "epitrochoid"


def test_oaxaca_svg_selects_mitla_and_agave_ornaments():
    oaxaca_deck = load_deck(theme_cards_path("oaxaca"))
    oaxaca_tokens = load_theme_tokens("oaxaca")
    classic_deck = load_deck(theme_cards_path("classic"))
    classic_tokens = load_theme_tokens("classic")

    oaxaca_action = next(
        card
        for card in oaxaca_deck.unique_designs()
        if card.metadata["design_id"] == "pass-go"
    )
    oaxaca_money = next(
        card
        for card in oaxaca_deck.unique_designs()
        if card.metadata["design_id"] == "money-5m"
    )
    classic_action = next(
        card
        for card in classic_deck.unique_designs()
        if card.metadata["design_id"] == "pass-go"
    )

    action_svg = build_card(oaxaca_action, oaxaca_deck, oaxaca_tokens).to_bytes()
    money_svg = build_card(oaxaca_money, oaxaca_deck, oaxaca_tokens).to_bytes()
    classic_svg = build_card(classic_action, classic_deck, classic_tokens).to_bytes()

    assert b"mitla-step-motif-field" in action_svg
    assert b"band-corner-agave-band" in action_svg
    assert b"agave-medallion-leaf-medallion" in money_svg
    assert b"mitla-step" not in classic_svg
    assert b"band-corner-agave" not in classic_svg


def test_arizona_svg_selects_desert_ornaments():
    arizona_deck = load_deck(theme_cards_path("arizona"))
    arizona_tokens = load_theme_tokens("arizona")
    classic_deck = load_deck(theme_cards_path("classic"))
    classic_tokens = load_theme_tokens("classic")

    arizona_action = next(
        card
        for card in arizona_deck.unique_designs()
        if card.metadata["design_id"] == "pass-go"
    )
    arizona_money = next(
        card
        for card in arizona_deck.unique_designs()
        if card.metadata["design_id"] == "money-5m"
    )
    classic_action = next(
        card
        for card in classic_deck.unique_designs()
        if card.metadata["design_id"] == "pass-go"
    )

    action_svg = build_card(arizona_action, arizona_deck, arizona_tokens).to_bytes()
    money_svg = build_card(arizona_money, arizona_deck, arizona_tokens).to_bytes()
    classic_svg = build_card(classic_action, classic_deck, classic_tokens).to_bytes()

    assert b"desert-dune-motif-field" in action_svg
    assert b"band-corner-saguaro-band" in action_svg
    assert b"sunburst-medallion-ray-medallion" in money_svg
    assert b"desert-dune" not in classic_svg
    assert b"band-corner-saguaro" not in classic_svg
    assert b"sunburst-medallion" not in classic_svg


def test_oaxaca_wildcard_derives_all_set_icons():
    oaxaca = load_deck(theme_cards_path("oaxaca"))
    wildcard = next(
        card
        for card in oaxaca.by_type("wildcard")
        if card.metadata["design_id"] == "wildcard-railroad-utility"
    )
    halves = wildcard.metadata["halves"]

    assert halves[0]["header_icons"] == ["agave", "jicara"]
    assert halves[1]["header_icons"] == ["route"]


def test_arizona_wildcard_derives_route_and_river_icons():
    arizona = load_deck(theme_cards_path("arizona"))
    wildcard = next(
        card
        for card in arizona.by_type("wildcard")
        if card.metadata["design_id"] == "wildcard-railroad-utility"
    )
    halves = wildcard.metadata["halves"]

    assert halves[0]["header_icons"] == ["river"]
    assert halves[1]["header_icons"] == ["route"]


def test_classic_tokens_equal_base():
    """Classic has no overlay, so it resolves to the base tokens unchanged."""
    assert load_theme_tokens("classic").raw == load_tokens().raw


@pytest.mark.parametrize(
    "theme",
    ["missing", "classic/../classic", str(THEMES_DIR / "classic")],
)
def test_theme_loaders_reject_unregistered_names(theme):
    with pytest.raises(ValueError, match="unknown theme"):
        theme_cards_path(theme)
    with pytest.raises(ValueError, match="unknown theme"):
        load_theme_tokens(theme)


@pytest.mark.parametrize("theme", available_themes())
def test_every_design_builds_valid_svg(theme):
    deck = load_deck(theme_cards_path(theme))
    tokens = load_theme_tokens(theme)
    for card in deck.unique_designs():
        data = build_card(card, deck, tokens).to_bytes()
        # Parses as XML and is a non-trivial SVG document.
        root = ET.fromstring(data)  # noqa: S314 - parses trusted generated SVG
        assert root.tag.endswith("svg")
