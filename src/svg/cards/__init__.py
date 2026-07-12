"""Per-card-type SVG builders.

Each builder module registers itself in BUILDERS at import time via
register(). build_card() is the single entry point used by the pipeline.
"""

import contextlib
import importlib
from collections.abc import Callable
from typing import TypeVar, cast

from ...models import Card
from ...models.deck import Deck
from ...tokens import Tokens, load_tokens
from ..core import SVGDocument

Builder = Callable[[Card, Deck, Tokens], SVGDocument]
CardT = TypeVar("CardT", bound=Card)
TypedBuilder = Callable[[CardT, Deck, Tokens], SVGDocument]

BUILDERS: dict[str, Builder] = {}


def register(card_type: str) -> Callable[[TypedBuilder[CardT]], TypedBuilder[CardT]]:
    def deco(fn: TypedBuilder[CardT]) -> TypedBuilder[CardT]:
        BUILDERS[card_type] = cast("Builder", fn)
        return fn

    return deco


def build_card(card: Card, deck: Deck, tokens: Tokens | None = None) -> SVGDocument:
    """Build a card's SVG. `tokens` selects the theme palette; defaults to base."""
    try:
        builder = BUILDERS[card.card_type]
    except KeyError as error:
        raise NotImplementedError(
            f"no SVG builder registered for card type {card.card_type!r}"
        ) from error
    return builder(card, deck, tokens or load_tokens())


def _load_builders() -> None:
    """Import builder modules for their registration side effects."""
    for mod in ("property_", "action", "rent", "wildcard", "money"):
        with contextlib.suppress(ModuleNotFoundError):
            importlib.import_module(f".{mod}", __package__)


_load_builders()
