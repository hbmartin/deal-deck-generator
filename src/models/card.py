"""
Card data models for the card rendering engine.
Defines base Card class and type-specific variants.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class Card:
    """Base card model with common attributes."""

    card_id: str
    card_type: Literal["property", "action", "rent", "wildcard", "money"]
    title: str
    value: Optional[int] = None
    description: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate card data after initialization."""
        if self.card_type not in ["property", "action", "rent", "wildcard", "money"]:
            raise ValueError(f"Invalid card_type: {self.card_type}")


@dataclass
class PropertyCard(Card):
    """Property card with rent table and color set."""

    color: str = ""
    property_name: str = ""
    rent_values: list[tuple[int, int]] = field(
        default_factory=list
    )  # [(num_properties, rent_value), ...]
    set_size: int = 0

    def __post_init__(self):
        super().__post_init__()
        self.card_type = "property"
        if not self.color:
            raise ValueError("PropertyCard requires a color")


@dataclass
class ActionCard(Card):
    """Action card with effect description."""

    action_name: str = ""

    def __post_init__(self):
        super().__post_init__()
        self.card_type = "action"


@dataclass
class RentCard(Card):
    """Rent card for charging rent on color sets."""

    colors: list[str] = field(default_factory=list)
    is_wild: bool = False  # True for all-color wild rent

    def __post_init__(self):
        super().__post_init__()
        self.card_type = "rent"


@dataclass
class WildcardCard(Card):
    """Wildcard property card that can be any color."""

    allowed_colors: list[str] = field(default_factory=list)
    is_multicolor: bool = False  # True for 10-color wildcard

    def __post_init__(self):
        super().__post_init__()
        self.card_type = "wildcard"


@dataclass
class MoneyCard(Card):
    """Money card with denomination value."""

    denomination: int = 0

    def __post_init__(self):
        super().__post_init__()
        self.card_type = "money"
        if not self.denomination:
            raise ValueError("MoneyCard requires a denomination")
