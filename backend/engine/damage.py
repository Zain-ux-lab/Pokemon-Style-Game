"""Shared deterministic type, modifier and guard damage calculations."""

from .creature import Creature
from .moves import Move
from .type_chart import effectiveness_percent


def base_damage(attacker: Creature, defender: Creature, move: Move) -> int:
    """Unmodified damage before matchup, conditions, guard or remaining HP."""
    return max(1, attacker.attack * move.power // defender.defense) if move.power else 0


def drain_healing(attacker: Creature, damage: int) -> int:
    return min(damage // 4, 4, attacker.max_hp - attacker.current_hp)


def calculate_damage(attacker: Creature, defender: Creature, move: Move) -> int:
    """Return typed damage with setup modifiers, before guard and HP capping."""
    if move.power == 0:
        return 0
    damage = base_damage(attacker, defender, move)
    damage = max(1, damage * effectiveness_percent(move.damage_type, defender.battle_type) // 100)
    if move.mechanic == 'exploit' and 'mark' in defender.statuses:
        damage += 18
    if move.mechanic == 'harvest' and 'spores' in defender.statuses:
        damage += 10
    if move.mechanic == 'reprisal':
        damage += min(15, attacker.last_damage // 2)
    if 'weaken' in attacker.statuses:
        damage = damage * 75 // 100
    if 'expose' in defender.statuses:
        damage = damage * 125 // 100
    return damage


def direct_damage(attacker: Creature, defender: Creature, move: Move) -> int:
    """Exact direct HP loss; used by resolution and API previews."""
    damage = calculate_damage(attacker, defender, move)
    if move.mechanic != 'phase':
        damage = damage * (100 - defender.guard_percent) // 100
    return min(defender.current_hp, damage)


def recoil_damage(attacker: Creature, defender: Creature, move: Move) -> int:
    if move.power == 0:
        return 0
    recoil = 6 if 'spores' in attacker.statuses else 0
    confused = attacker.statuses.get('confuse')
    if confused and attacker.moves.index(move) == confused.slot:
        recoil += 8
    if move.contact and 'thorns' in defender.statuses and direct_damage(attacker, defender, move) > 0:
        recoil += 14
    return recoil
