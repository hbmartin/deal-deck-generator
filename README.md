# Business Deal Card Generator

A Python card-rendering engine that reproduces Business Deal-style card layouts using Pillow. This project generates card images from YAML definitions, supporting property cards, action cards, rent cards, wildcard cards, and money cards.

## Features

- **Card Types Supported:**
  - Property cards (with color-coded headers and rent tables)
  - Action cards (with decorative borders and centered text)
  - Rent cards (with color circles and descriptions)
  - Wildcard property cards (with color stripe headers)
  - Money cards (with large denomination displays)

- **Design System:**
  - JSON-based design tokens for easy customization
  - Consistent typography and spacing
  - Color-coded property sets
  - Modular template system

## Installation

This project uses `uv` for dependency management. Make sure you have `uv` installed:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install dependencies:

```bash
uv sync
```

## Usage

### Rendering Cards

Render all cards from the YAML definition file:

```bash
uv run python render_deck.py
```

Render specific card types:

```bash
uv run python render_deck.py --types property action
```

Render to a specific output directory:

```bash
uv run python render_deck.py --output output/my_deck
```

Render in WebP format:

```bash
uv run python render_deck.py --format webp
```

### Command-Line Options

- `--cards`, `-c`: Path to cards YAML file (default: `cards.yaml`)
- `--output`, `-o`: Output directory for rendered cards (default: `output/deck`)
- `--types`, `-t`: Card types to render: `property`, `action`, `money`, `rent`, `wildcard`, or `all` (default: `all`)
- `--format`, `-f`: Output image format: `png` or `webp` (default: `png`)

### Card Definitions

Cards are defined in `cards.yaml`. Each card type has its own section:

```yaml
property_cards:
  - id: brown-01
    name: "Mediterranean Avenue"
    color: brown
    value: 1
    set_size: 2
    rent_values: [[1, 1], [2, 2]]
    quantity: 2

action_cards:
  - id: deal-breaker
    name: "Deal Breaker"
    value: 5
    description: "Steal a complete set of properties..."
    quantity: 2
```

See `cards.yaml` for complete examples of all card types.

## Project Structure

```
.
├── src/
│   ├── models/          # Card data models
│   │   └── card.py      # Card dataclasses
│   ├── renderer/        # Rendering engine
│   │   ├── card_renderer.py  # Main renderer dispatcher
│   │   ├── primitives.py     # Low-level drawing primitives
│   │   └── elements.py       # High-level card elements
│   └── templates/       # Card type templates
│       ├── property_template.py
│       ├── action_template.py
│       ├── money_template.py
│       ├── rent_template.py
│       └── wildcard_template.py
├── Card Images/         # Reference card images
├── cards.yaml           # Card definitions
├── design_tokens.json  # Design system tokens
├── render_deck.py       # CLI entry point
└── analyze_cards.py     # Card image analysis tool
```

## Customization

### Design Tokens

Modify `design_tokens.json` to customize:

- Card dimensions and corner radius
- Color palettes for property sets
- Typography (fonts, sizes, weights)
- Spacing and padding values
- Layout parameters for each card type

### Adding New Card Types

1. Create a new template in `src/templates/`
2. Add the card model in `src/models/card.py`
3. Update `src/renderer/card_renderer.py` to dispatch to your template
4. Add card definitions to `cards.yaml`

## Development

### Code Formatting

Format code with Black:

```bash
uv run black .
```

### Linting

Check code with Ruff:

```bash
uv run ruff check .
```

### Analysis

Analyze card images to extract design tokens:

```bash
uv run python analyze_cards.py
```

This generates `analysis_results.json` with extracted dimensions, colors, and layout information.

## Card Specifications

### Property Cards
- Color-coded header bar
- Property name
- Rent table with property icons
- Value badge (top-left)

### Action Cards
- Decorative chain-link border
- "ACTION CARD" title bar
- Large circular title area
- Description text
- Value badges (top-left and bottom-right)

### Rent Cards
- Decorative chain-link border
- "RENT" title bar
- Concentric color circles (2-color) or "ALL COLORS" text (wild)
- Description text
- Value badges (top-left and bottom-right)

### Wildcard Cards
- Color stripe header (2 colors or 10 colors for multicolor)
- "PROPERTY WILD CARD" title
- Large "WILD" text
- Description text
- Value badge (top-left)

### Money Cards
- Decorative chain-link border
- Large denomination circle
- Value badges (top-left and bottom-right)

## License

This project is for educational and personal use. Card designs are inspired by Business Deal card game mechanics.

## Acknowledgments

- Card design analysis based on reference images
- Built with Pillow (PIL) for image rendering
- Uses `uv` for fast Python package management

