"""Data model for a character-specific battle move."""

from dataclasses import dataclass
from typing import Literal


MoveEffect = Literal["damage", "heal", "guard", "status"]
TYPES = {"Neutral", "Magic", "Physical", "Spirit"}
STATUS_MOVES = {"spores", "thorns", "mark", "paralyse", "confuse", "weaken", "expose"}
ATTACK_MECHANICS = {"", "echo", "drain", "exploit", "reprisal", "dread", "phase", "harvest"}


@dataclass(frozen=True)
class Move:
    """A typed attack, status, healing or guard action."""

    name: str
    power: int = 0
    effect: MoveEffect = "damage"
    effect_amount: int | None = None
    damage_type: str = "Neutral"
    contact: bool = False
    mechanic: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("move name must not be empty")
        if self.damage_type not in TYPES:
            raise ValueError("unknown damage type")
        if self.effect not in {"damage", "heal", "guard", "status"}:
            raise ValueError("effect must be damage, heal, or guard")
        if self.effect == "damage":
            if self.mechanic not in ATTACK_MECHANICS:
                raise ValueError("unknown attack mechanic")
            if self.power <= 0:
                raise ValueError("damage move power must be greater than zero")
            if self.effect_amount is not None:
                raise ValueError("damage move must not have an effect amount")
        elif self.effect == "status":
            if self.mechanic not in STATUS_MOVES or self.power < 0 or self.effect_amount is not None:
                raise ValueError("invalid status move")
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
        if self.effect in {"heal", "guard"} and self.mechanic:
            raise ValueError("healing and guard moves cannot have a mechanic")
