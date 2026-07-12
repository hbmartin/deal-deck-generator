"""Tests for reference-photo lookup and contact-sheet composition."""

from PIL import Image

from src.compare import contact_sheet


def test_photo_for_supports_exact_prefix_and_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(contact_sheet, "PHOTO_DIR", tmp_path)

    assert contact_sheet.photo_for("money-1m") == tmp_path / "$1M-money-card.png"
    assert contact_sheet.photo_for("brown-99") == tmp_path / "brown-property-card.png"
    assert contact_sheet.photo_for("unmapped") is None


def test_fit_height_preserves_aspect_ratio():
    image = Image.new("RGB", (20, 10), "red")

    resized = contact_sheet._fit_height(image, 25)  # noqa: SLF001

    assert resized.size == (50, 25)


def test_build_contact_sheets_chunks_rows_and_uses_photo_fallback(
    monkeypatch,
    tmp_path,
):
    preview_dir = tmp_path / "preview"
    photo_dir = tmp_path / "photos"
    compare_dir = tmp_path / "compare"
    preview_dir.mkdir()
    photo_dir.mkdir()
    monkeypatch.setattr(contact_sheet, "PHOTO_DIR", photo_dir)

    for value in range(1, 8):
        Image.new("RGB", (20 + value, 40), "blue").save(
            preview_dir / f"money-{value}m.png"
        )
    Image.new("RGB", (30, 20), "green").save(photo_dir / "$1M-money-card.png")

    sheets = contact_sheet.build_contact_sheets(
        preview_dir=preview_dir,
        compare_dir=compare_dir,
        types=["money"],
    )

    assert sheets == [
        compare_dir / "compare-money-1.png",
        compare_dir / "compare-money-2.png",
    ]
    for sheet_path in sheets:
        with Image.open(sheet_path) as sheet:
            assert sheet.width > 600
            assert sheet.height > contact_sheet.CELL_H
