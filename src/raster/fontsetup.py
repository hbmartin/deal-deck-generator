"""Fontconfig plumbing so rasterizers see the right fonts.

Two modes:
- "system"  (default on macOS): bundled fonts + system font dirs; the SVG
  font stacks prefer Gill Sans, so the system face wins when present.
- "bundled": bundled fonts only; deterministic on any machine (used for
  CI golden renders and cross-machine reproduction).
"""

import platform
from pathlib import Path

from ..tokens import FONTS_DIR

_MAC_FONT_DIRS = [
    "/System/Library/Fonts",
    "/System/Library/Fonts/Supplemental",
    "/Library/Fonts",
    str(Path.home() / "Library" / "Fonts"),
]

_LINUX_FONT_DIRS = [
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    str(Path.home() / ".fonts"),
]


def write_fonts_conf(out_dir: Path, mode: str = "system") -> Path:
    """Write a fonts.conf and return its path (set as FONTCONFIG_FILE)."""
    dirs = [str(FONTS_DIR)]
    if mode == "system":
        extra = _MAC_FONT_DIRS if platform.system() == "Darwin" else _LINUX_FONT_DIRS
        dirs += [d for d in extra if Path(d).is_dir()]

    cache_dir = out_dir / ".fontconfig-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    dir_lines = "\n".join(f"  <dir>{d}</dir>" for d in dirs)
    conf = f"""<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
{dir_lines}
  <cachedir>{cache_dir}</cachedir>
</fontconfig>
"""
    conf_path = out_dir / f"fonts-{mode}.conf"
    conf_path.parent.mkdir(parents=True, exist_ok=True)
    conf_path.write_text(conf)
    return conf_path
