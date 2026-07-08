"""Pluggable SVG -> PNG rasterizer abstraction."""

import os
import subprocess
from pathlib import Path
from typing import Protocol


class RasterError(Exception):
    pass


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

    def rasterize(self, svg, png, width, height, fontconfig=None):
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

    def rasterize(self, svg, png, width, height, fontconfig=None):
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
    except KeyError:
        raise RasterError(
            f"unknown rasterizer {name!r}; options: {sorted(_RASTERIZERS)}"
        )
