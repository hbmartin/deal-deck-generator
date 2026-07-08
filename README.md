# Deal Deck Generator

Data-driven card deck generator that reproduces the 2008-era Monopoly Deal
card designs as print-ready files: **cards.yaml → Python → SVG → PNG**.

Every one of the deck's 106 cards (58 unique designs) is generated as a
resolution-independent SVG in print coordinates and rasterized to a PNG that
matches the MakePlayingCards.com **US Game Deck** spec — 2.44" × 3.67" full
bleed at 300 DPI (732 × 1101 px), cut line 2.2" × 3.43", with all critical
content inside the safe area. Reference photos of the physical cards live in
`Card Images/` and drive the visual-fidelity work (layout metrics, palettes,
the guilloché engraving, the double-struck Ⓜ money glyph).

## Requirements

- Python ≥ 3.14 and [uv](https://docs.astral.sh/uv/)
- `rsvg-convert` (librsvg) — `brew install librsvg` / `apt install librsvg2-bin`
- Optional: Inkscape as an alternative rasterizer (`--renderer inkscape`)

```bash
uv sync --dev
```

## Usage

```bash
# Render everything: output/svg, output/png (732x1101 print), output/preview
uv run python main.py render

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

`output/manifest.json` records every design with its physical-card quantity —
use it when uploading to MakePlayingCards (one image per design, set the
quantity on the site; the deck totals 106 cards).

## How it works

| Stage | Where | What |
|---|---|---|
| Data | `cards.yaml`, `src/data/loader.py` | All 106 cards, transcribed verbatim from the reference photos. Two-color wildcards derive their rent tables from the property definitions at load time — one source of truth. `{nM}` tokens in descriptions mark inline money glyphs. |
| Design tokens | `design_tokens.json`, `src/tokens.py` | Print geometry, the ten property colors, per-value tints (money **and** action/rent cards share one `value_tints` table, as the real deck does), type scale, fonts. Tune colors/sizes here, not in code. |
| SVG build | `src/svg/` | ElementTree-based builders. `svg/components/` holds the shared pieces: Ⓜ glyph, corner badges, header bars, fanned-card icons, dotted leaders, rent tables, title circles, color rings, procedural guilloché + ornate border band, icons, Mr. Monopoly. `svg/cards/` composes them per card type. |
| Guilloché | `src/svg/components/guilloche.py` | Deterministic engraved-line work: interleaved sine-wave mesh fields (one path per family in `<defs>`, stamped with `<use>`) and superposed epitrochoid rosette medallions. No randomness — renders are byte-stable. |
| Raster | `src/raster/` | Pluggable rasterizers (rsvg default, Inkscape optional) driven through fontconfig. On macOS `PANGOCAIRO_BACKEND=fc` is forced so the bundled fonts are honored. |

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

- Data invariants (106 cards, per-type counts, railroad/utility names,
  wildcard rent derivation), SVG structure (parse validity, viewBox, size
  budget, deterministic output), and raster dimensions.
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
Pyrefly, tests, renders the full deck with bundled fonts, and uploads the PNGs
+ manifest as an artifact.
