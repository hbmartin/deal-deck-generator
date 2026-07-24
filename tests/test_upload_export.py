"""Quantity-expanded upload export behavior."""

from pathlib import Path

import pytest

from src.data.loader import load_deck
from src.data.themes import theme_cards_path
from src.render import pipeline


class StubDocument:
    def to_bytes(self) -> bytes:
        return b"<svg />"


class StubRasterizer:
    name = "stub"

    def rasterize(self, svg_path: Path, png_path: Path, *_args) -> None:
        png_path.write_bytes(svg_path.stem.encode())


@pytest.fixture
def fast_render(monkeypatch):
    monkeypatch.setattr(pipeline, "build_card", lambda *_args: StubDocument())
    monkeypatch.setattr(pipeline, "get_rasterizer", lambda _name: StubRasterizer())
    monkeypatch.setattr(
        pipeline,
        "write_fonts_conf",
        lambda out_dir, _fonts_mode: out_dir / "fonts.conf",
    )
    monkeypatch.setattr(pipeline, "stamp_png_dpi", lambda _path: None)
    return pipeline.render_deck


@pytest.mark.parametrize(
    ("theme", "expected_count"),
    [("arizona", 144), ("classic", 106), ("chicago", 144)],
)
def test_full_theme_upload_counts(theme, expected_count, fast_render, tmp_path):
    deck = load_deck(theme_cards_path(theme))
    out_dir = tmp_path / theme

    manifest = fast_render(deck, out_dir, previews=False)
    upload_paths = sorted((out_dir / "upload").glob("*.png"))

    assert len(upload_paths) == expected_count
    assert len(manifest["upload_files"]) == expected_count
    assert manifest["total_physical_cards"] == expected_count
    assert all(path.is_file() and not path.is_symlink() for path in upload_paths)


def test_card_back_outputs_and_manifest_are_separate_from_uploads(
    deck,
    fast_render,
    tmp_path,
):
    manifest = fast_render(
        deck,
        tmp_path,
        card_ids=["pass-go"],
        previews=True,
    )

    assert manifest["card_back"] == {
        "title": "DEAL",
        "svg": "svg/card-back.svg",
        "png": "png/card-back.png",
        "preview": "preview/card-back.png",
    }
    assert (tmp_path / "svg/card-back.svg").is_file()
    assert (tmp_path / "png/card-back.png").read_bytes() == b"card-back"
    assert (tmp_path / "preview/card-back.png").read_bytes() == b"card-back"
    assert not any("card-back" in path.name for path in (tmp_path / "upload").iterdir())


def test_no_previews_omits_card_back_preview(deck, fast_render, tmp_path):
    manifest = fast_render(deck, tmp_path, card_ids=["pass-go"], previews=False)

    assert "preview" not in manifest["card_back"]
    assert not (tmp_path / "preview/card-back.png").exists()


def test_classic_upload_names_and_manifest_follow_deck_order(fast_render, tmp_path):
    deck = load_deck(theme_cards_path("classic"))

    manifest = fast_render(deck, tmp_path, previews=False)
    upload_paths = sorted((tmp_path / "upload").glob("*.png"))

    assert upload_paths[0].name == "001-brown-01.png"
    assert upload_paths[28].name == "029-deal-breaker-1.png"
    assert upload_paths[29].name == "030-deal-breaker-2.png"
    assert manifest["upload_files"][28] == {
        "slot": 29,
        "card_id": "deal-breaker-1",
        "design_id": "deal-breaker",
        "png": "upload/029-deal-breaker-1.png",
    }
    assert (
        upload_paths[28].read_bytes()
        == (tmp_path / "png/deal-breaker.png").read_bytes()
    )


def test_filtered_export_restarts_slots_and_removes_stale_files(
    fast_render,
    tmp_path,
):
    deck = load_deck(theme_cards_path("classic"))

    first_manifest = fast_render(
        deck,
        tmp_path,
        card_ids=["pass-go"],
        previews=False,
    )
    assert len(first_manifest["upload_files"]) == 10
    assert (tmp_path / "upload/010-pass-go-10.png").is_file()

    second_manifest = fast_render(
        deck,
        tmp_path,
        card_ids=["money-5m", "money-10m"],
        previews=False,
    )
    upload_names = sorted(path.name for path in (tmp_path / "upload").glob("*.png"))

    assert upload_names == [
        "001-money-10m.png",
        "002-money-5m-1.png",
        "003-money-5m-2.png",
    ]
    assert [entry["design_id"] for entry in second_manifest["upload_files"]] == [
        "money-10m",
        "money-5m",
        "money-5m",
    ]
    assert not (tmp_path / "upload/010-pass-go-10.png").exists()


def test_type_filter_exports_only_matching_physical_cards(fast_render, tmp_path):
    deck = load_deck(theme_cards_path("classic"))

    manifest = fast_render(deck, tmp_path, types=["money"], previews=False)

    assert manifest["total_physical_cards"] == 20
    assert manifest["upload_files"][0]["png"] == "upload/001-money-10m.png"
    assert {entry["design_id"] for entry in manifest["upload_files"]} == {
        "money-10m",
        "money-5m",
        "money-4m",
        "money-3m",
        "money-2m",
        "money-1m",
    }


def test_upload_slot_width_expands_beyond_three_digits(deck):
    assert (
        pipeline._upload_filename(  # noqa: SLF001 - verifies filename contract
            deck.cards[0], slot=1, total=1_000
        )
        == "0001-brown-01.png"
    )
