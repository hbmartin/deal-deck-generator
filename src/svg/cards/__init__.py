"""Per-card-type SVG builders.

Each builder module registers itself in BUILDERS at import time via
register(). build_card() is the single entry point used by the pipeline.
"""

from collections.abc import Callable
from typing import Any, TypeVar, cast

from ...models import Card
from ..core import SVGDocument

Builder = Callable[[Card, Any], SVGDocument]  # (card, deck) -> document
CardT = TypeVar("CardT", bound=Card)
TypedBuilder = Callable[[CardT, Any], SVGDocument]

BUILDERS: dict[str, Builder] = {}


def register(card_type: str) -> Callable[[TypedBuilder[CardT]], TypedBuilder[CardT]]:
    def deco(fn: TypedBuilder[CardT]) -> TypedBuilder[CardT]:
        BUILDERS[card_type] = cast(Builder, fn)
        return fn

    return deco


def build_card(card: Card, deck) -> SVGDocument:
    try:
        builder = BUILDERS[card.card_type]
    except KeyError:
        raise NotImplementedError(
            f"no SVG builder registered for card type {card.card_type!r}"
        )
    return builder(card, deck)


def _load_builders() -> None:
    """Import builder modules for their registration side effects."""
    import importlib

    for mod in ("property_", "action", "rent", "wildcard", "money"):
        try:
            importlib.import_module(f".{mod}", __package__)
        except ModuleNotFoundError:
            # During scaffolding not all builder modules exist yet.
            pass


_load_builders()
