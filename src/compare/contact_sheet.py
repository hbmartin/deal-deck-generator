"""Contact sheets pairing rendered previews with reference photos.

The photos are angled stacks, so pairing is strictly side-by-side visual
reference — no registration or diffing. Filenames below match the files in
"Card Images/" exactly, including the two 'railraod' typos.
"""

from pathlib import Path

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PHOTO_DIR = PROJECT_ROOT / "Card Images"

# design_id (or design_id prefix) -> reference photo filename
PHOTO_MAP = {
    "brown": "brown-property-card.png",
    "light_blue": "light-blue-property-card.png",
    "pink": "pink-property-card.png",
    "orange": "orange-property-card.png",
    "red": "red-property-card.png",
    "yellow": "yellow-property-card.png",
    "green": "green-property-card.png",
    "dark_blue": "dark-blue-property-card.png",
    "railroad": "railroad-property-card.png",
    "utility": "utility-property-card.png",
    "deal-breaker": "deal-breaker-action-card.png",
    "just-say-no": "just-say-no-action-card.png",
    "sly-deal": "sly-deal-action-card.png",
    "forced-deal": "force-deal-action-card.png",
    "debt-collector": "debt-collector-action-card.png",
    "its-my-birthday": "it's-my-birthday-action-card.png",
    "pass-go": "pass-go-action-card.png",
    "house": "house-action-card.png",
    "hotel": "hotel-action-card.png",
    "double-the-rent": "double-the-rent-action-card.png",
    "rent-pink-orange": "orange-and-pink-rent-card.png",
    "rent-railroad-utility": "railroad-and-utility-rent-card.png",
    "rent-green-dark_blue": "blue-and-green-rent-card.png",
    "rent-brown-light_blue": "brown-and-light-blue-rent-card.png",
    "rent-red-yellow": "red-and-yellow-rent-card.png",
    "rent-wild": "all-color-wild-rent-card.png",
    "wildcard-pink-orange": "orange-and-pink-wildcard-card.png",
    "wildcard-light_blue-brown": "light-blue-and-brown-wildcard-card.png",
    "wildcard-light_blue-railroad": "railraod-and-light-blue-wildcard-card.png",
    "wildcard-dark_blue-green": "dark-blue-and-green-wildcard-card.png",
    "wildcard-railroad-green": "railraod-and-green-wildcard-card.png",
    "wildcard-red-yellow": "red-and-yellow-wildcard-card.png",
    "wildcard-railroad-utility": "railroad-and-utility-wildcard-card.png",
    "wildcard-multicolor": "multicolor-wildcard-card.png",
    "money-1m": "$1M-money-card.png",
    "money-2m": "$2M-money-card.png",
    "money-3m": "$3M-money-card.png",
    "money-4m": "$4M-money-card.png",
    "money-5m": "$5M-money-card.png",
    "money-10m": "$10M-money-card.png",
}

TYPE_PREFIXES = {
    "property": (
        "brown",
        "light_blue",
        "pink",
        "orange",
        "red",
        "yellow",
        "green",
        "dark_blue",
        "railroad-0",
        "utility-0",
    ),
    "action": (
        "deal-breaker",
        "just-say-no",
        "sly-deal",
        "forced-deal",
        "debt-collector",
        "its-my-birthday",
        "pass-go",
        "house",
        "hotel",
        "double-the-rent",
    ),
    "rent": ("rent-",),
    "wildcard": ("wildcard-",),
    "money": ("money-",),
}

CELL_H = 455
PAD = 14
LABEL_H = 26


def photo_for(design_id: str) -> Path | None:
    if design_id in PHOTO_MAP:
        return PHOTO_DIR / PHOTO_MAP[design_id]
    for prefix, fname in PHOTO_MAP.items():
        if design_id.startswith(prefix):
            return PHOTO_DIR / fname
    return None


def _fit_height(img: Image.Image, h: int) -> Image.Image:
    w = round(img.width * h / img.height)
    return img.resize((w, h), Image.Resampling.LANCZOS)


def build_contact_sheets(
    preview_dir: Path,
    compare_dir: Path,
    types: list[str] | None = None,
) -> list[Path]:
    compare_dir.mkdir(parents=True, exist_ok=True)
    sheets = []
    for card_type, prefixes in TYPE_PREFIXES.items():
        if types and card_type not in types:
            continue
        previews = sorted(
            p
            for p in preview_dir.glob("*.png")
            if any(p.stem.startswith(pfx) for pfx in prefixes)
        )
        if not previews:
            continue
        rows = []
        for pv in previews:
            render = _fit_height(Image.open(pv).convert("RGB"), CELL_H)
            photo_path = photo_for(pv.stem)
            if photo_path and photo_path.exists():
                photo = _fit_height(Image.open(photo_path).convert("RGB"), CELL_H)
            else:
                photo = Image.new("RGB", (300, CELL_H), "#888888")
            rows.append((pv.stem, render, photo))

        chunk_size = 6
        chunks = [rows[i : i + chunk_size] for i in range(0, len(rows), chunk_size)]
        for ci, chunk in enumerate(chunks):
            width = max(r[1].width + r[2].width for r in chunk) + 3 * PAD
            height = sum(CELL_H + LABEL_H + PAD for _ in chunk) + PAD
            sheet = Image.new("RGB", (width, height), "#2A2A2A")
            draw = ImageDraw.Draw(sheet)
            y = PAD
            for stem, render, photo in chunk:
                draw.text((PAD, y + 4), stem, fill="#FFFFFF")
                y += LABEL_H
                sheet.paste(render, (PAD, y))
                sheet.paste(photo, (render.width + 2 * PAD, y))
                y += CELL_H + PAD

            suffix = f"-{ci + 1}" if len(chunks) > 1 else ""
            out = compare_dir / f"compare-{card_type}{suffix}.png"
            sheet.save(out)
            sheets.append(out)
    return sheets
