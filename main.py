"""Entry point for the deal-deck CLI. See `python main.py --help`."""

import sys

# pyrefly: ignore [missing-import]
from src.cli import main

if __name__ == "__main__":
    sys.exit(main())
