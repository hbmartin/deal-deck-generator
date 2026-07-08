"""Deck container: all card instances plus deck-level configuration."""

from dataclasses import dataclass, field

from .card import Card


@dataclass(frozen=True)
class DeckConfig:
    footer_text: str = ""


@dataclass
class Deck:
    cards: list[Card]
    config: DeckConfig = field(default_factory=DeckConfig)

    def unique_designs(self) -> list[Card]:
        """First instance of each design (copies share a design_id)."""
        seen: set[str] = set()
        designs = []
        for card in self.cards:
            design_id = card.metadata.get("design_id", card.card_id)
            if design_id not in seen:
                seen.add(design_id)
                designs.append(card)
        return designs

    def quantity_of(self, design_id: str) -> int:
        return sum(
            1 for c in self.cards if c.metadata.get("design_id", c.card_id) == design_id
        )

    def by_type(self, card_type: str) -> list[Card]:
        return [c for c in self.cards if c.card_type == card_type]
