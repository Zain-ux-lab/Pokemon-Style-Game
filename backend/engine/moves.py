"""Data model for a character-specific battle move."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Move:
    """A deterministic move whose power is used by the Phase 1 damage formula."""

    name: str
    power: int

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("move name must not be empty")
        if self.power <= 0:
            raise ValueError("move power must be greater than zero")
