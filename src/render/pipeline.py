"""Render pipeline: card models -> SVG files -> print + preview PNGs."""

import json
import shutil
from pathlib import Path
from typing import NotRequired, TypedDict

from ..geometry import BLEED
from ..models import Card
from ..models.deck import Deck
from ..raster.base import get_rasterizer, stamp_png_dpi
from ..raster.fontsetup import write_fonts_conf
from ..svg.card_back import build_card_back
from ..svg.cards import build_card
from ..tokens import Tokens, load_tokens


class CardManifestEntry(TypedDict):
    type: str
    title: str
    quantity: int
    svg: str
    png: str
    preview: NotRequired[str]


class UploadManifestEntry(TypedDict):
    slot: int
    card_id: str
    design_id: str
    png: str


class CardBackManifestEntry(TypedDict):
    title: str
    svg: str
    png: str
    preview: NotRequired[str]


class RenderManifest(TypedDict):
    renderer: str
    fonts: str
    card_back: CardBackManifestEntry
    cards: dict[str, CardManifestEntry]
    upload_files: list[UploadManifestEntry]
    total_physical_cards: int


def design_id_of(card: Card) -> str:
    return card.metadata.get("design_id", card.card_id)


def _upload_filename(card: Card, *, slot: int, total: int) -> str:
    slot_width = max(3, len(str(total)))
    return f"{slot:0{slot_width}d}-{card.card_id}.png"


def _write_upload_files(
    deck: Deck,
    *,
    design_pngs: dict[str, Path],
    out_dir: Path,
) -> list[UploadManifestEntry]:
    """Create one real, uniquely named PNG per selected physical card."""
    upload_dir = out_dir / "upload"
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
    upload_dir.mkdir(parents=True)

    physical_cards = [card for card in deck.cards if design_id_of(card) in design_pngs]
    entries: list[UploadManifestEntry] = []
    for slot, card in enumerate(physical_cards, start=1):
        design_id = design_id_of(card)
        upload_path = upload_dir / _upload_filename(
            card,
            slot=slot,
            total=len(physical_cards),
        )
        shutil.copyfile(src=design_pngs[design_id], dst=upload_path)
        entries.append(
            {
                "slot": slot,
                "card_id": card.card_id,
                "design_id": design_id,
                "png": str(upload_path.relative_to(out_dir)),
            }
        )
    return entries


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
) -> RenderManifest:
    """Render unique designs and quantity-expanded upload files."""
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

    card_entries: dict[str, CardManifestEntry] = {}
    design_pngs: dict[str, Path] = {}
    for card in designs:
        design_id = design_id_of(card)
        doc = build_card(card, deck, tokens)
        svg_path = svg_dir / f"{design_id}.svg"
        svg_path.write_bytes(doc.to_bytes())
        png_path = png_dir / f"{design_id}.png"
        rast.rasterize(svg_path, png_path, int(BLEED.w), int(BLEED.h), fontconfig)
        stamp_png_dpi(png_path)  # print files must declare 300 DPI for MPC
        design_pngs[design_id] = png_path
        entry: CardManifestEntry = {
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
        card_entries[design_id] = entry

    card_back_doc = build_card_back(deck, tokens)
    card_back_svg = svg_dir / "card-back.svg"
    card_back_svg.write_bytes(card_back_doc.to_bytes())
    card_back_png = png_dir / "card-back.png"
    rast.rasterize(
        card_back_svg,
        card_back_png,
        int(BLEED.w),
        int(BLEED.h),
        fontconfig,
    )
    stamp_png_dpi(card_back_png)
    card_back_entry: CardBackManifestEntry = {
        "title": deck.config.card_back.title,
        "svg": str(card_back_svg.relative_to(out_dir)),
        "png": str(card_back_png.relative_to(out_dir)),
    }
    if previews:
        card_back_preview = preview_dir / "card-back.png"
        rast.rasterize(card_back_svg, card_back_preview, pw, ph, fontconfig)
        card_back_entry["preview"] = str(card_back_preview.relative_to(out_dir))

    upload_files = _write_upload_files(
        deck,
        design_pngs=design_pngs,
        out_dir=out_dir,
    )
    manifest: RenderManifest = {
        "renderer": rast.name,
        "fonts": fonts_mode,
        "card_back": card_back_entry,
        "cards": card_entries,
        "upload_files": upload_files,
        "total_physical_cards": len(upload_files),
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    return manifest
