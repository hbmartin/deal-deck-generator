"""
Card Image Analysis Script
Extracts design tokens from existing card images:
- Dimensions and geometry
- Color palettes
- Layout structure
- Typography estimates
"""

import json
from pathlib import Path
from PIL import Image, ImageStat
import statistics


def analyze_image_dimensions(image_path):
    """Extract basic dimensions and aspect ratio."""
    img = Image.open(image_path)
    width, height = img.size
    return {
        "width": width,
        "height": height,
        "aspect_ratio": round(width / height, 3),
    }


def extract_dominant_colors(image_path, num_colors=10):
    """Extract dominant colors from image using color quantization."""
    img = Image.open(image_path).convert("RGB")

    # Reduce to palette
    img_reduced = img.quantize(colors=num_colors)
    palette = img_reduced.getpalette()

    # Get color counts
    colors = []
    for i in range(num_colors):
        r = palette[i * 3]
        g = palette[i * 3 + 1]
        b = palette[i * 3 + 2]
        colors.append(f"#{r:02x}{g:02x}{b:02x}")

    return colors[:6]  # Return top 6


def analyze_brightness_regions(image_path):
    """Analyze brightness distribution to infer layout regions."""
    img = Image.open(image_path).convert("L")  # Grayscale
    width, height = img.size

    # Divide into horizontal bands
    bands = 10
    band_height = height // bands
    brightness_profile = []

    for i in range(bands):
        top = i * band_height
        bottom = min((i + 1) * band_height, height)
        band = img.crop((0, top, width, bottom))
        stat = ImageStat.Stat(band)
        brightness_profile.append(
            {
                "band": i,
                "y_range": [top, bottom],
                "mean_brightness": round(stat.mean[0], 1),
            }
        )

    return brightness_profile


def analyze_card_type(image_path):
    """Determine card type from filename."""
    name = Path(image_path).stem.lower()

    if "property" in name and "wildcard" not in name:
        return "property"
    elif "wildcard" in name:
        return "wildcard"
    elif "rent" in name:
        return "rent"
    elif "action" in name:
        return "action"
    elif "money" in name:
        return "money"
    else:
        return "unknown"


def analyze_all_cards(card_dir):
    """Analyze all cards and produce design token report."""
    card_dir = Path(card_dir)
    card_files = sorted(card_dir.glob("*.png"))

    results = {
        "global": {
            "dimensions": {},
            "color_tokens": {},
        },
        "cards": {},
        "by_type": {
            "property": [],
            "wildcard": [],
            "rent": [],
            "action": [],
            "money": [],
        },
    }

    all_dimensions = []

    print(f"Analyzing {len(card_files)} card images...\n")

    for card_file in card_files:
        card_name = card_file.stem
        print(f"Analyzing: {card_name}")

        card_type = analyze_card_type(card_file)
        dims = analyze_image_dimensions(card_file)
        colors = extract_dominant_colors(card_file)
        brightness = analyze_brightness_regions(card_file)

        card_analysis = {
            "filename": card_file.name,
            "type": card_type,
            "dimensions": dims,
            "dominant_colors": colors,
            "brightness_profile": brightness,
        }

        results["cards"][card_name] = card_analysis
        results["by_type"][card_type].append(card_name)
        all_dimensions.append(dims)

    # Compute global dimensions
    widths = [d["width"] for d in all_dimensions]
    heights = [d["height"] for d in all_dimensions]
    aspects = [d["aspect_ratio"] for d in all_dimensions]

    results["global"]["dimensions"] = {
        "typical_width": statistics.mode(widths) if widths else 0,
        "typical_height": statistics.mode(heights) if heights else 0,
        "width_range": [min(widths), max(widths)] if widths else [0, 0],
        "height_range": [min(heights), max(heights)] if heights else [0, 0],
        "typical_aspect_ratio": round(statistics.mean(aspects), 3) if aspects else 0,
    }

    print("\nAnalysis complete!")
    print(
        f"Typical dimensions: {results['global']['dimensions']['typical_width']}x{results['global']['dimensions']['typical_height']}"
    )
    print(
        f"Card types found: {[(t, len(cards)) for t, cards in results['by_type'].items() if cards]}"
    )

    return results


def main():
    card_dir = Path(__file__).parent / "Card Images"

    if not card_dir.exists():
        print(f"Error: Card Images directory not found at {card_dir}")
        return

    results = analyze_all_cards(card_dir)

    # Save analysis results
    output_file = Path(__file__).parent / "analysis_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total cards analyzed: {len(results['cards'])}")
    print("\nCard type distribution:")
    for card_type, cards in results["by_type"].items():
        if cards:
            print(f"  {card_type}: {len(cards)}")


if __name__ == "__main__":
    main()
