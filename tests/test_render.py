"""End-to-end raster checks on one design per card type."""

from PIL import Image

from src.geometry import BLEED

from src.raster.base import get_rasterizer

from src.raster.fontsetup import write_fonts_conf

from src.svg.cards import build_card

SAMPLE_DESIGNS = [
    "red-01",
    "railroad-04",
    "pass-go",
    "rent-wild",
    "wildcard-pink-orange",
    "money-10m",
]


def test_print_png_dimensions(deck, tmp_path):
    fontconfig = write_fonts_conf(tmp_path, "bundled")
    rast = get_rasterizer("rsvg")
    by_id = {c.metadata["design_id"]: c for c in deck.unique_designs()}
    for design_id in SAMPLE_DESIGNS:
        card = by_id[design_id]
        svg = tmp_path / f"{design_id}.svg"
        svg.write_bytes(build_card(card, deck).to_bytes())
        png = tmp_path / f"{design_id}.png"
        rast.rasterize(svg, png, int(BLEED.w), int(BLEED.h), fontconfig)
        with Image.open(png) as img:
            assert img.size == (732, 1101), design_id
