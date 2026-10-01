"""Data model for a character-specific battle move."""

from dataclasses import dataclass
from typing import Literal


MoveEffect = Literal["damage", "heal", "guard"]


@dataclass(frozen=True)
class Move:
    """A deterministic attack or one-turn healing/guard action."""

    name: str
    power: int = 0
    effect: MoveEffect = "damage"
    effect_amount: int | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("move name must not be empty")
        if self.effect not in {"damage", "heal", "guard"}:
            raise ValueError("effect must be damage, heal, or guard")
        if self.effect == "damage":
            if self.power <= 0:
                raise ValueError("damage move power must be greater than zero")
            if self.effect_amount is not None:
                raise ValueError("damage move must not have an effect amount")
        elif self.effect == "heal":
            if self.power != 0:
                raise ValueError("healing move must not have attack power")
            if self.effect_amount is None or self.effect_amount <= 0:
                raise ValueError("healing amount must be greater than zero")
        else:
            if self.power != 0:
                raise ValueError("guard move must not have attack power")
            if self.effect_amount is None or not 1 <= self.effect_amount <= 100:
                raise ValueError("guard amount must be between 1 and 100 percent")
