"""SVG structural invariants: parse validity, viewBox, id uniqueness, size."""

import xml.etree.ElementTree as ET

import pytest

# pyrefly: ignore [missing-import]
from src.svg.cards import build_card

SIZE_BUDGET = 300_000  # bytes; guards against runaway guilloché output


@pytest.fixture(scope="module")
def built_svgs(deck):
    return {
        c.metadata["design_id"]: build_card(c, deck).to_bytes()
        for c in deck.unique_designs()
    }


def test_every_design_builds(built_svgs):
    assert len(built_svgs) == 58


def test_svgs_parse_with_viewbox(built_svgs):
    for design_id, data in built_svgs.items():
        root = ET.fromstring(data)
        assert root.get("viewBox") == "0 0 732 1101", design_id


def test_size_budget(built_svgs):
    for design_id, data in built_svgs.items():
        assert len(data) < SIZE_BUDGET, f"{design_id} is {len(data)} bytes"


def test_def_ids_unique(built_svgs):
    for design_id, data in built_svgs.items():
        root = ET.fromstring(data)
        ids = [el.get("id") for el in root.iter() if el.get("id")]
        assert len(ids) == len(set(ids)), design_id


def test_deterministic_output(deck):
    card = deck.unique_designs()[0]
    assert build_card(card, deck).to_bytes() == build_card(card, deck).to_bytes()
