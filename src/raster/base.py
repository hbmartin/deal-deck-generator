"""Pluggable SVG -> PNG rasterizer abstraction."""

import os
import subprocess
from pathlib import Path
from typing import Protocol

from PIL import Image

# Print files are rendered at the full-bleed pixel size (732x1101), which is the
# card's physical size at 300 DPI. rsvg/inkscape don't write a resolution chunk,
# so MPC would read the file as 72 DPI; stamp the pHYs chunk explicitly.
PRINT_DPI = 300


class RasterError(Exception):
    pass


def stamp_png_dpi(path: Path, dpi: int = PRINT_DPI) -> None:
    """Write a PNG resolution (pHYs) chunk so the file declares `dpi`.

    Pixels are untouched — only the density metadata changes.
    """
    with Image.open(path) as im:
        im.load()
    im.save(path, dpi=(dpi, dpi))


class Rasterizer(Protocol):
    name: str

    def rasterize(
        self, svg: Path, png: Path, width: int, height: int, fontconfig: Path | None
    ) -> None: ...


def run_checked(cmd: list[str], fontconfig: Path | None) -> None:
    env = os.environ.copy()
    if fontconfig is not None:
        env["FONTCONFIG_FILE"] = str(fontconfig)
        # On macOS pango defaults to CoreText, which cannot see the bundled
        # fonts; force the fontconfig backend so FONTCONFIG_FILE is honored.
        env["PANGOCAIRO_BACKEND"] = "fc"
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RasterError(
            f"{cmd[0]} failed ({result.returncode}): {result.stderr.strip()}"
        )


class RsvgRasterizer:
    name = "rsvg"

    def rasterize(
        self,
        svg: Path,
        png: Path,
        width: int,
        height: int,
        fontconfig: Path | None = None,
    ) -> None:
        run_checked(
            [
                "rsvg-convert",
                "--width",
                str(width),
                "--height",
                str(height),
                "--output",
                str(png),
                str(svg),
            ],
            fontconfig,
        )


class InkscapeRasterizer:
    name = "inkscape"

    def rasterize(
        self,
        svg: Path,
        png: Path,
        width: int,
        height: int,
        fontconfig: Path | None = None,
    ) -> None:
        run_checked(
            [
                "inkscape",
                "--export-type=png",
                f"--export-filename={png}",
                f"--export-width={width}",
                f"--export-height={height}",
                str(svg),
            ],
            fontconfig,
        )


_RASTERIZERS = {"rsvg": RsvgRasterizer, "inkscape": InkscapeRasterizer}


def get_rasterizer(name: str = "rsvg") -> Rasterizer:
    try:
        return _RASTERIZERS[name]()
    except KeyError as error:
        raise RasterError(
            f"unknown rasterizer {name!r}; options: {sorted(_RASTERIZERS)}"
        ) from error
