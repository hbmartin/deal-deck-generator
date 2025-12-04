# Business Deal Card Generator

A Python-based card rendering engine that generates high-quality card images from YAML definitions. This tool reproduces Business Deal-style card layouts using Pillow, supporting all major card types with a flexible, customizable design system.

## 🎯 Overview

This project allows you to:
- **Define cards** in simple YAML format
- **Render card images** programmatically with consistent styling
- **Customize designs** through JSON design tokens
- **Generate complete decks** with a single command
- **Extend functionality** with custom templates and assets

Perfect for game designers, developers, or anyone needing to generate card game assets programmatically.

## ✨ Features

### Supported Card Types

- **Property Cards** - Color-coded headers with rent tables
- **Action Cards** - Decorative borders with centered text and descriptions
- **Rent Cards** - Color circles (2-color or wild 10-color segmented)
- **Wildcard Cards** - Multi-color stripe headers for flexible property sets
- **Money Cards** - Large denomination displays with decorative borders

### Key Capabilities

- 🎨 **Design System** - JSON-based design tokens for easy customization
- 🔤 **Custom Fonts** - Support for custom fonts from assets directory
- 🧪 **Test Suite** - Comprehensive validation and comparison tests
- 📐 **Consistent Layouts** - Standardized dimensions and spacing
- 🎯 **Modular Architecture** - Easy to extend with new card types
- 🚀 **Fast Rendering** - Efficient Pillow-based image generation

## 📋 Requirements

- Python 3.14 or higher
- `uv` package manager (recommended) or pip

## 🚀 Quick Start

### Installation

1. **Install `uv`** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone or download this repository**

3. **Install dependencies**:
   ```bash
   uv sync
   ```

### Basic Usage

**Render all cards:**
```bash
uv run python render_deck.py
```

**Render specific card types:**
```bash
uv run python render_deck.py --types property action
```

**Custom output directory:**
```bash
uv run python render_deck.py --output my_cards
```

**Export as WebP:**
```bash
uv run python render_deck.py --format webp
```

## 📖 Detailed Usage

### Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--cards` | `-c` | Path to cards YAML file | `cards.yaml` |
| `--output` | `-o` | Output directory | `output/deck` |
| `--types` | `-t` | Card types to render | `all` |
| `--format` | `-f` | Image format (png/webp) | `png` |

**Card Types:** `property`, `action`, `money`, `rent`, `wildcard`, or `all`

### Examples

**Render only property and money cards:**
```bash
uv run python render_deck.py --types property money
```

**Render to a specific directory with WebP format:**
```bash
uv run python render_deck.py --output cards/webp --format webp
```

**Use a custom card definition file:**
```bash
uv run python render_deck.py --cards my_cards.yaml --output my_output
```

## 📝 Card Definitions

Cards are defined in YAML format. Here are examples for each card type:

### Property Card

```yaml
property_cards:
  - id: brown-01
    name: "Mediterranean Avenue"
    color: brown
    value: 1
    set_size: 2
    rent_values: [[1, 1], [2, 2]]
    quantity: 2
```

**Fields:**
- `id`: Unique identifier
- `name`: Property name
- `color`: Property set color (brown, light_blue, pink, orange, red, yellow, green, dark_blue, railroad, utility)
- `value`: Card value in millions
- `set_size`: Number of properties in the complete set
- `rent_values`: List of `[num_properties, rent_amount]` pairs
- `quantity`: How many copies to generate

### Action Card

```yaml
action_cards:
  - id: deal-breaker
    name: "Deal Breaker"
    value: 5
    description: "Steal a complete set of properties from any player. (Includes any buildings.) Play into center to use."
    quantity: 2
```

### Money Card

```yaml
money_cards:
  - denomination: 5
    quantity: 2
```

### Rent Card

```yaml
rent_cards:
  # Two-color rent card
  - id: rent-pink-orange
    name: "Rent"
    colors: [pink, orange]
    value: 1
    is_wild: false
    description: "All players pay you rent for properties you own in one of these colors."
    quantity: 2
    
  # Wild rent card (all colors)
  - id: rent-wild
    name: "Rent"
    colors: []
    value: 3
    is_wild: true
    description: "All players pay you rent for properties you own in one of these colors."
    quantity: 3
```

### Wildcard Card

```yaml
wildcard_cards:
  # Two-color wildcard
  - id: wildcard-pink-orange
    name: "Property Wild Card"
    allowed_colors: [pink, orange]
    is_multicolor: false
    value: 2
    description: "This card can be used as part of any property set."
    quantity: 2
    
  # Multicolor wildcard (all 10 colors)
  - id: wildcard-multicolor
    name: "Property Wild Card"
    allowed_colors: [brown, light_blue, pink, orange, red, yellow, green, dark_blue, railroad, utility]
    is_multicolor: true
    value: 0
    description: "This card can be used as part of any property set."
    quantity: 2
```

See `cards.yaml` for the complete deck definition (106 cards total).

## 🎨 Customization

### Design Tokens

Modify `design_tokens.json` to customize the visual appearance:

**Card Dimensions:**
```json
{
  "global": {
    "card": {
      "width": 413,
      "height": 455,
      "corner_radius": 20,
      "border_width": 3
    }
  }
}
```

**Colors:**
```json
{
  "global": {
    "colors": {
      "property_sets": {
        "brown": "#8B4513",
        "light_blue": "#ADD8E6",
        "pink": "#FF1493",
        ...
      }
    }
  }
}
```

**Typography:**
```json
{
  "global": {
    "typography": {
      "font_family_primary": "Arial",
      "sizes": {
        "title_large": 28,
        "body": 14
      }
    }
  }
}
```

### Custom Fonts

1. Create the fonts directory:
   ```bash
   mkdir -p src/assets/fonts
   ```

2. Place your font files:
   ```
   src/assets/fonts/
     ├── MyCustomFont.ttf
     ├── MyCustomFont-Bold.ttf
     └── ...
   ```

3. Update `design_tokens.json` to use your font:
   ```json
   {
     "global": {
       "typography": {
         "font_family_primary": "MyCustomFont"
       }
     }
   }
   ```

The renderer automatically checks `src/assets/fonts/` before falling back to system fonts.

### Custom Icons

Icons support is planned. Place icons in `src/assets/icons/`:
```
src/assets/icons/
  ├── house.png
  ├── hotel.png
  └── ...
```

## 🏗️ Project Structure

```
deal-deck-generator/
├── src/
│   ├── models/              # Card data models (dataclasses)
│   │   └── card.py
│   ├── renderer/            # Rendering engine
│   │   ├── card_renderer.py # Main dispatcher
│   │   ├── primitives.py    # Low-level drawing functions
│   │   └── elements.py      # High-level card elements
│   ├── templates/           # Card type templates
│   │   ├── property_template.py
│   │   ├── action_template.py
│   │   ├── money_template.py
│   │   ├── rent_template.py
│   │   ├── wildcard_template.py
│   │   └── utils.py        # Shared template utilities
│   └── assets/              # Custom assets (fonts, icons)
│       ├── fonts/
│       └── icons/
├── tests/                   # Test suite
│   └── test_card_rendering.py
├── Card Images/             # Reference card images
├── cards.yaml               # Card definitions
├── design_tokens.json       # Design system configuration
├── render_deck.py           # CLI entry point
├── analyze_cards.py         # Image analysis tool
└── README.md                # This file
```

## 🧪 Development

### Running Tests

**Run all tests:**
```bash
uv run pytest tests/ -v
```

**Run specific test:**
```bash
uv run pytest tests/test_card_rendering.py::test_property_card_rendering -v
```

**Test coverage:**
- Rendering validation for all card types
- Dimension consistency checks
- Visual comparison with original images

### Code Quality

**Format code:**
```bash
uv run black .
```

**Lint code:**
```bash
uv run ruff check .
```

**Format and lint together:**
```bash
uv run black . && uv run ruff check .
```

### Analyzing Card Images

Extract design tokens from reference images:

```bash
uv run python analyze_cards.py
```

This generates `analysis_results.json` with:
- Card dimensions
- Color palettes
- Layout structure
- Typography estimates

## 📐 Card Specifications

### Standard Card Size
- **Dimensions:** 413 × 455 pixels
- **Aspect Ratio:** ~0.908 (portrait)
- **Corner Radius:** 20 pixels
- **Format:** PNG or WebP

### Card Type Details

#### Property Cards
- Color-coded header bar (property set color)
- Property name in header
- "RENT" label
- Rent table with property icons
- Value badge (top-left corner)
- Footer text

#### Action Cards
- Decorative chain-link border
- "ACTION CARD" title bar
- Large circular title area with action name
- Description text (wrapped)
- Value badges (top-left and bottom-right)
- Footer text

#### Rent Cards
- Decorative chain-link border
- "RENT" title bar
- **Two-color:** Concentric circles (outer + inner)
- **Wild:** Segmented circle with all 10 property colors
- Description text
- Value badges (top-left and bottom-right)
- Footer text

#### Wildcard Cards
- Color stripe header (2 or 10 colors)
- "PROPERTY WILD CARD" title
- Large "WILD" text display
- Description text
- Value badge (top-left)
- Footer text

#### Money Cards
- Decorative chain-link border
- Large denomination circle
- Denomination text ($XM format)
- Value badges (top-left and bottom-right)
- Footer text

## 🔧 Extending the Project

### Adding a New Card Type

1. **Create the model** in `src/models/card.py`:
   ```python
   @dataclass
   class CustomCard(Card):
       custom_field: str = ""
       
       def __post_init__(self):
           super().__post_init__()
           self.card_type = "custom"
   ```

2. **Create the template** in `src/templates/custom_template.py`:
   ```python
   def render_custom_card(card: CustomCard) -> Image.Image:
       # Your rendering logic here
       ...
   ```

3. **Update the renderer** in `src/renderer/card_renderer.py`:
   ```python
   elif card.card_type == "custom":
       from ..templates.custom_template import render_custom_card
       img = render_custom_card(card)
   ```

4. **Add card definitions** to `cards.yaml`

### Creating Custom Templates

Templates follow a consistent pattern:

```python
def render_card_type(card: CardType) -> Image.Image:
    # 1. Load design tokens
    tokens = load_design_tokens()
    
    # 2. Create card base
    img, draw = create_card_base(width, height, bg_color, corner_radius)
    
    # 3. Draw elements (borders, text, icons, etc.)
    # ...
    
    # 4. Return rendered image
    return img
```

## 🐛 Troubleshooting

### Font Issues

**Problem:** Fonts not loading
- **Solution:** Check that font files are in `src/assets/fonts/` and filenames match exactly
- **Fallback:** System fonts will be used if custom fonts aren't found

### Rendering Errors

**Problem:** Cards not rendering
- **Check:** Card definitions in `cards.yaml` are valid YAML
- **Check:** Required fields are present for each card type
- **Check:** Color names match those in `design_tokens.json`

### Dimension Issues

**Problem:** Cards have wrong size
- **Check:** `design_tokens.json` has correct dimensions
- **Check:** All templates use the same width/height from tokens

## 📚 Additional Resources

- **`IMPROVEMENTS.md`** - Roadmap and enhancement suggestions
- **`Cards.md`** - Reference card information
- **`analysis_results.json`** - Extracted design tokens from reference images

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Icon asset support
- Performance optimizations
- Additional card types
- Enhanced visual validation
- Better error handling

See `IMPROVEMENTS.md` for detailed suggestions.

## 📄 License

This project is for educational and personal use. Card designs are inspired by Business Deal card game mechanics.

## 🙏 Acknowledgments

- Built with [Pillow](https://python-pillow.org/) for image rendering
- Uses [uv](https://github.com/astral-sh/uv) for fast Python package management
- Design analysis based on reference card images
- Inspired by Business Deal card game mechanics

## 📞 Support

For issues, questions, or contributions:
1. Check existing documentation
2. Review `IMPROVEMENTS.md` for planned features
3. Run tests to verify your setup
4. Check card definitions and design tokens for errors

---

**Happy card generating! 🎴**
