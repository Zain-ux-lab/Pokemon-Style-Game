"""Basic deterministic damage calculation for Phase 1."""

from .creature import Creature
from .moves import Move


def calculate_damage(attacker: Creature, defender: Creature, move: Move) -> int:
    """Return base damage, with a minimum of one point for a valid attack.

    Phase 1 intentionally excludes random critical hits, accuracy rolls,
    type effectiveness, and status modifiers.
    """
    return max(1, attacker.attack * move.power // defender.defense)
