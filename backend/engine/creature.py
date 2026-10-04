"""Creature data and per-battle health state."""

from dataclasses import dataclass, field

from .moves import Move, TYPES
from .status_effects import Status


@dataclass
class Creature:
    """A reusable creature definition with health tracked for one battle."""

    name: str
    max_hp: int
    attack: int
    defense: int
    moves: tuple[Move, ...] = field(default_factory=tuple)
    current_hp: int | None = None
    guard_percent: int = 0
    battle_type: str = "Neutral"
    statuses: dict[str, Status] = field(default_factory=dict)
    last_damage: int = 0

    def __post_init__(self) -> None:
        if self.battle_type not in TYPES:
            raise ValueError("unknown creature type")
        if not self.name.strip():
            raise ValueError("creature name must not be empty")
        if self.max_hp <= 0:
            raise ValueError("max_hp must be greater than zero")
        if self.attack < 0:
            raise ValueError("attack must not be negative")
        if self.defense <= 0:
            raise ValueError("defense must be greater than zero")
        if self.current_hp is None:
            self.current_hp = self.max_hp
        elif not 0 <= self.current_hp <= self.max_hp:
            raise ValueError("current_hp must be between zero and max_hp")
        if isinstance(self.guard_percent, bool) or not 0 <= self.guard_percent <= 100:
            raise ValueError("guard_percent must be between zero and 100")

    @property
    def is_knocked_out(self) -> bool:
        """Whether this creature can no longer fight."""
        return self.current_hp == 0
