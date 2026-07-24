"""Load design_tokens.json into typed, frozen structures.

Renderers read all tunable design values (colors, type sizes, fonts) from
here so visual adjustments happen in design_tokens.json, not in code.
"""

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Literal

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOKENS_PATH = PROJECT_ROOT / "design_tokens.json"
FONTS_DIR = PROJECT_ROOT / "src" / "assets" / "fonts"


@dataclass(frozen=True)
class FontRole:
    stack: str
    measure_file: str
    weight: str

    @property
    def measure_path(self) -> Path:
        return FONTS_DIR / self.measure_file


type FieldPattern = Literal["wave", "mitla_step", "desert_dune"]
type BorderCorner = Literal["rosette", "agave", "saguaro"]
type MoneyMedallion = Literal["epitrochoid", "agave", "sunburst"]


@dataclass(frozen=True)
class OrnamentStyle:
    field_pattern: FieldPattern
    border_corner: BorderCorner
    money_medallion: MoneyMedallion


@dataclass(frozen=True)
class CardBackStyle:
    background_property: str
    accent_order: tuple[str, ...]


@dataclass(frozen=True)
class Tokens:
    raw: dict

    @property
    def preview_size(self) -> tuple[int, int]:
        p = self.raw["print"]["preview"]
        return (p["w"], p["h"])

    @property
    def corner_radius(self) -> float:
        return self.raw["print"]["corner_radius"]

    def font(self, role: str) -> FontRole:
        f = self.raw["fonts"][role]
        return FontRole(f["stack"], f["measure_file"], f["weight"])

    @property
    def ornament(self) -> OrnamentStyle:
        ornament = self.raw["ornament"]
        return OrnamentStyle(
            field_pattern=ornament["field_pattern"],
            border_corner=ornament["border_corner"],
            money_medallion=ornament["money_medallion"],
        )

    @property
    def card_back(self) -> CardBackStyle:
        card_back = self.raw["card_back"]
        return CardBackStyle(
            background_property=card_back["background_property"],
            accent_order=tuple(card_back["accent_order"]),
        )

    def property_color(self, color: str) -> dict:
        return self.raw["palette"]["property"][color]

    def value_tint(self, value: int) -> dict:
        return self.raw["palette"]["value_tints"][str(value)]

    def chrome(self, key: str) -> str:
        return self.raw["palette"]["chrome"][key]

    def size(self, key: str) -> float:
        return self.raw["type_scale"][key]


@cache
def load_tokens(path: Path = TOKENS_PATH) -> Tokens:
    with path.open() as f:
        return Tokens(raw=json.load(f))


def mix_hex(a: str, b: str, t: float) -> str:
    """Linear mix of two #RRGGBB colors; t=0 -> a, t=1 -> b."""
    av = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    bv = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    mixed = [round(x + (y - x) * t) for x, y in zip(av, bv, strict=True)]
    return "#" + "".join(f"{v:02X}" for v in mixed)
