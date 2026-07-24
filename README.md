# Deal Deck Generator

Data-driven card deck generator that produces card designs as print-ready files: **cards.yaml → Python → SVG → PNG**.

Decks are **themeable**: each theme under `themes/<name>/` supplies its own card
names and an optional color-palette overlay, all sharing the same game structure
and rendering engine. The default `classic` deck ships alongside `arizona`
(statewide places + desert ornaments), `chicago` (Chicago landmarks + civic
palette), and `oaxaca` (Oaxaca City + Valles Centrales, natural-dye palette,
and custom ornaments). See [Themes](#themes).

The base deck's 58 unique designs—and 87 when a theme includes the shared
expansion—are generated as resolution-independent SVGs in print coordinates
and rasterized to PNGs that match the MakePlayingCards.com
**US Game Deck** spec — 2.44" × 3.67" full bleed at 300 DPI (732 × 1101 px),
cut line 2.2" × 3.43", with all critical content inside the safe area. Each
render also creates one uniquely named PNG per physical card, ready for bulk
upload, plus one theme-aware common card back. Reference photos of the physical
cards live in `Card Images/` and drive the visual-fidelity work (layout metrics,
palettes, the guilloché engraving, the double-struck Ⓜ money glyph).

## Requirements

- Python ≥ 3.14 and [uv](https://docs.astral.sh/uv/)
- `rsvg-convert` (librsvg) — `brew install librsvg` / `apt install librsvg2-bin`
- Optional: Inkscape as an alternative rasterizer (`--renderer inkscape`)

```bash
uv sync --dev
```

## Usage

```bash
# Render the default (classic) deck into output/classic/{svg,png,preview}
uv run python main.py render

# Render a different theme (output goes to output/<theme>/ by default)
uv run python main.py render --theme chicago
uv run python main.py render --theme oaxaca
uv run python main.py render --theme arizona
uv run python main.py render --list-themes

# Filter by type or design id
uv run python main.py render --type property --type money
uv run python main.py render --card money-10m --card red-01

# Side-by-side contact sheets against the reference photos
uv run python main.py compare

# Rasterizer / font selection
uv run python main.py render --renderer inkscape --fonts bundled

# Sanity check the toolchain (blank card through the rasterizers)
uv run python main.py smoke
```

`output/<theme>/png/` contains one print PNG per unique front design plus
`card-back.png`; matching SVG and optional preview files are written as
`svg/card-back.svg` and `preview/card-back.png`. The back is always generated,
including filtered renders, and is recorded separately under `card_back` in
`manifest.json`.
`output/<theme>/upload/` expands those designs by quantity into a flat,
slot-ordered set of physical-card files, such as `029-deal-breaker-1.png` and
`030-deal-breaker-2.png`. Select the entire `upload/` folder for bulk upload to
MakePlayingCards. `manifest.json` records both the design quantities and the
ordered mapping for every upload file; the classic deck totals 106 files.

## Themes

A theme is a directory under `themes/` holding a `cards.yaml` (required) and an
optional `tokens.json` overlay:

```
themes/
  classic/cards.yaml     # the default deck (== base design_tokens.json palette)
  arizona/
    cards.yaml           # statewide places + shared expansion, 144 cards
    tokens.json          # copper/sunset palette + dune/saguaro/sunburst ornaments
  chicago/
    cards.yaml           # Chicago property names + "WINDY CITY DEAL" footer
    tokens.json          # palette overlay: Chicago property colors
  oaxaca/
    cards.yaml           # Oaxaca City + Valles Centrales, 106-card base deck
    tokens.json          # full palette + Mitla/agave ornament profile
```

- `cards.yaml` follows the same schema for every theme. Each theme's base cards
  are **pure reskins**: identical card ids, values, set sizes, rent tables, and
  quantities—only property `name`s, header icons, and deck presentation text
  change. Themes may also include registered shared fragments such as
  `expansion`; the base cards remain structurally interchangeable and wildcard
  rent tables stay derived from one source of truth.
- `deck.card_back.title` supplies the common back's centered branding. It is
  rendered in opposing orientations so the back has no preferred direction;
  older theme files that omit it default to `DEAL`.

  ```yaml
  deck:
    footer_text: "WINDY CITY DEAL"
    card_back:
      title: "WINDY CITY DEAL"
  ```

- `tokens.json` is a small **overlay** deep-merged onto the base
  `design_tokens.json` at load time. A theme can override property colors,
  value tints, and the `ornament` choices for field pattern, border corners,
  and money medallions. `classic` has no overlay, so it resolves to the base
  tokens unchanged.
- Base `card_back` tokens select a background property color and the ten-color
  accent order. Because they reference the resolved property palette, the same
  back layout automatically follows every theme's colors and ornaments.
- Property `header_icon` supports `train`, `bulb`, `faucet`, `route`, `agave`,
  `jicara`, and `river`. Wildcard headers derive every distinct icon used by
  their corresponding property set.

To add a theme, copy `themes/classic/cards.yaml`, rename the properties, and
(optionally) add a `tokens.json` overlay. It shows up in `--list-themes`
automatically. Resolution lives in `src/data/themes.py`
(`theme_cards_path`, `load_theme_tokens`).

## How it works

| Stage | Where | What |
|---|---|---|
| Data | `themes/<name>/cards.yaml`, `src/data/loader.py`, `src/data/themes.py` | All 106 cards per theme, transcribed verbatim from the reference photos (classic). Two-color wildcards derive their rent tables from the property definitions at load time — one source of truth. `{nM}` tokens in descriptions mark inline money glyphs; `deck.card_back.title` brands the common back. |
| Design tokens | `design_tokens.json` (base) + `themes/<name>/tokens.json` (overlay), `src/tokens.py` | Print geometry, the ten property colors, per-value tints (money **and** action/rent cards share one `value_tints` table), ornament profile, type scale, and fonts. Tune shared values in the base; theme-specific choices go in overlays. |
| SVG build | `src/svg/` | ElementTree-based builders. `svg/components/` holds the shared pieces: Ⓜ glyph, corner badges, header bars, fanned-card icons, dotted leaders, rent tables, title circles, color rings, procedural guilloché + ornate border band, icons, Mr. Money. `svg/cards/` composes the fronts; `svg/card_back.py` builds the deterministic common back. |
| Ornament | `src/svg/components/guilloche.py`, `src/svg/components/border_band.py` | Deterministic SVG textures and ornaments selected by theme tokens: classic wave/rosette engraving, Oaxaca stepped-stone/agave forms, or Arizona dune/saguaro/sunburst forms. Reusable paths live in `<defs>` and are stamped with `<use>`; no randomness is used. |
| Raster | `src/raster/`, `src/render/pipeline.py` | Pluggable rasterizers (rsvg default, Inkscape optional) driven through fontconfig. Each unique front and the common back are rasterized once; only fronts are copied by quantity into the slot-ordered `upload/` directory. On macOS `PANGOCAIRO_BACKEND=fc` is forced so the bundled fonts are honored. |

### Fonts

The SVGs use hybrid stacks: system **Gill Sans** is preferred when present
(macOS), with bundled free fallbacks committed under `src/assets/fonts/`
(Gillius ADF No2 for body text, Oswald for condensed headings; licenses
alongside). Text is measured with the bundled fonts on every machine so line
breaks are identical everywhere; only rasterization differs. `--fonts bundled`
forces the fallback-only look (what CI renders).

## Tests & golden images

```bash
uv run pytest
```

- Data invariants (theme-specific card counts, per-type counts, wildcard rent
  derivation) run across **every** theme; theme-specific names, pure-reskin
  structure, palettes, and ornament checks live in `tests/test_themes.py`. Plus SVG
  structure (parse validity, viewBox, size budget, deterministic output) and
  raster dimensions. Card-back tests cover theme configuration, palette
  references, deterministic structure, rotational pairing, manifest isolation,
  print dimensions, and DPI metadata.
- **Golden regression**: rendered previews are compared against the accepted
  set for the current environment — `tests/goldens/mac` (Gill Sans, generated
  locally) or `tests/goldens/ci` (bundled fonts, generated on Linux). After
  intentionally changing a design:

  ```bash
  uv run python main.py goldens --update            # current env
  uv run python main.py goldens --update --env ci   # bundled-font set
  ```

  The ci set should be produced on Linux (grab the `rendered-deck` artifact
  from a CI run and commit its previews) — the golden test skips with a
  notice when the set for its environment is absent.

CI (GitHub Actions) checks Ruff formatting, lints with Ruff, type-checks with
Pyrefly, tests, renders the full deck with bundled fonts, and uploads the design
PNGs, quantity-expanded upload files, previews, and manifest as an artifact.
