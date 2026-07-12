"""Render pipeline: card models -> SVG files -> print + preview PNGs."""

import json
from pathlib import Path

from ..geometry import BLEED
from ..models import Card
from ..models.deck import Deck
from ..raster.base import get_rasterizer, stamp_png_dpi
from ..raster.fontsetup import write_fonts_conf
from ..svg.cards import build_card
from ..tokens import Tokens, load_tokens


def design_id_of(card: Card) -> str:
    return card.metadata.get("design_id", card.card_id)


def render_deck(  # noqa: PLR0913
    deck: Deck,
    out_dir: Path,
    *,
    types: list[str] | None = None,
    card_ids: list[str] | None = None,
    renderer: str = "rsvg",
    fonts_mode: str = "system",
    previews: bool = True,
    tokens: Tokens | None = None,
) -> dict:
    """Render unique designs; returns the manifest dict."""
    tokens = tokens or load_tokens()
    svg_dir = out_dir / "svg"
    png_dir = out_dir / "png"
    preview_dir = out_dir / "preview"
    for d in (svg_dir, png_dir, preview_dir):
        d.mkdir(parents=True, exist_ok=True)

    fontconfig = write_fonts_conf(out_dir, fonts_mode)
    rast = get_rasterizer(renderer)
    pw, ph = tokens.preview_size

    designs = deck.unique_designs()
    if types:
        designs = [c for c in designs if c.card_type in types]
    if card_ids:
        designs = [c for c in designs if design_id_of(c) in card_ids]

    manifest = {"renderer": rast.name, "fonts": fonts_mode, "cards": {}}
    for card in designs:
        design_id = design_id_of(card)
        doc = build_card(card, deck, tokens)
        svg_path = svg_dir / f"{design_id}.svg"
        svg_path.write_bytes(doc.to_bytes())
        png_path = png_dir / f"{design_id}.png"
        rast.rasterize(svg_path, png_path, int(BLEED.w), int(BLEED.h), fontconfig)
        stamp_png_dpi(png_path)  # print files must declare 300 DPI for MPC
        entry = {
            "type": card.card_type,
            "title": card.title,
            "quantity": deck.quantity_of(design_id),
            "svg": str(svg_path.relative_to(out_dir)),
            "png": str(png_path.relative_to(out_dir)),
        }
        if previews:
            pv_path = preview_dir / f"{design_id}.png"
            rast.rasterize(svg_path, pv_path, pw, ph, fontconfig)
            entry["preview"] = str(pv_path.relative_to(out_dir))
        manifest["cards"][design_id] = entry

    # pyrefly: ignore [bad-assignment]
    manifest["total_physical_cards"] = sum(
        e["quantity"] for e in manifest["cards"].values()
    )
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest
