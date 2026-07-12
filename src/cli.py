"""Command-line interface: render / compare / goldens / smoke."""

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

from . import goldens
from .compare import contact_sheet
from .data.loader import load_deck
from .data.themes import (
    DEFAULT_THEME,
    available_themes,
    load_theme_tokens,
    theme_cards_path,
)
from .geometry import BLEED
from .raster import base as raster_base
from .raster import fontsetup
from .render.pipeline import render_deck
from .svg.cards import base as card_base

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = PROJECT_ROOT / "output"
CARD_TYPES = ["property", "action", "rent", "wildcard", "money"]


def _add_render_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--theme",
        default=DEFAULT_THEME,
        help=f"deck theme under themes/ (default: {DEFAULT_THEME})",
    )
    p.add_argument(
        "--list-themes", action="store_true", help="list available themes and exit"
    )
    p.add_argument("--type", choices=CARD_TYPES, action="append", dest="types")
    p.add_argument("--card", action="append", dest="cards", help="design id filter")
    p.add_argument("--renderer", choices=["rsvg", "inkscape"], default="rsvg")
    p.add_argument("--fonts", choices=["system", "bundled"], default="system")
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output dir (default: output/<theme>)",
    )
    p.add_argument("--no-previews", action="store_true", help="skip preview-size PNGs")


def cmd_render(args: argparse.Namespace | SimpleNamespace) -> int:
    if args.list_themes:
        print("\n".join(available_themes()))
        return 0
    try:
        cards_path = theme_cards_path(args.theme)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2

    deck = load_deck(cards_path)
    tokens = load_theme_tokens(args.theme)
    out = args.out or (DEFAULT_OUT / args.theme)
    manifest = render_deck(
        deck,
        out,
        types=args.types,
        card_ids=args.cards,
        renderer=args.renderer,
        fonts_mode=args.fonts,
        previews=not args.no_previews,
        tokens=tokens,
    )
    n = len(manifest["cards"])
    print(f"rendered {n} designs ({manifest['total_physical_cards']} physical cards)")
    print(f"output: {out}")
    return 0


def cmd_smoke(args: argparse.Namespace | SimpleNamespace) -> int:
    """Render a blank chrome-only card through both rasterizers."""
    out = args.out / "smoke"
    out.mkdir(parents=True, exist_ok=True)
    doc = card_base.blank_card()
    svg_path = out / "blank.svg"
    svg_path.write_bytes(doc.to_bytes())
    fontconfig = fontsetup.write_fonts_conf(out, args.fonts)
    for name, required in [("rsvg", True), ("inkscape", False)]:
        png = out / f"blank-{name}.png"
        try:
            raster_base.get_rasterizer(name).rasterize(
                svg_path, png, int(BLEED.w), int(BLEED.h), fontconfig
            )
            print(f"ok: {png}")
        except Exception as e:  # noqa: BLE001 - smoke reports all failures
            if required:
                print(f"FAIL {name}: {e}")
                return 1
            print(f"warn: optional rasterizer {name} unavailable: {e}")
    return 0


def cmd_compare(args: argparse.Namespace | SimpleNamespace) -> int:
    sheets = contact_sheet.build_contact_sheets(
        preview_dir=args.out / "preview",
        compare_dir=args.out / "compare",
        types=args.types,
    )
    for s in sheets:
        print(f"sheet: {s}")
    return 0


def cmd_goldens(args: argparse.Namespace | SimpleNamespace) -> int:
    if not args.update:
        print("nothing to do (use --update)", file=sys.stderr)
        return 2
    env = goldens.update_goldens(env=args.env, renderer=args.renderer)
    print(f"updated goldens for env {env!r}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="deal-deck")
    sub = parser.add_subparsers(dest="command", required=True)

    p_render = sub.add_parser("render", help="render SVGs + PNGs")
    _add_render_args(p_render)
    p_render.set_defaults(fn=cmd_render)

    p_smoke = sub.add_parser("smoke", help="render a blank card via both rasterizers")
    p_smoke.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p_smoke.add_argument("--fonts", choices=["system", "bundled"], default="system")
    p_smoke.set_defaults(fn=cmd_smoke)

    p_cmp = sub.add_parser("compare", help="contact sheets: render vs reference photo")
    p_cmp.add_argument("--type", choices=CARD_TYPES, action="append", dest="types")
    p_cmp.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p_cmp.set_defaults(fn=cmd_compare)

    p_gold = sub.add_parser("goldens", help="manage golden images")
    p_gold.add_argument("--update", action="store_true")
    p_gold.add_argument("--env", choices=["mac", "ci"], default=None)
    p_gold.add_argument("--renderer", choices=["rsvg", "inkscape"], default="rsvg")
    p_gold.set_defaults(fn=cmd_goldens)

    args = parser.parse_args(argv)
    return args.fn(args)
