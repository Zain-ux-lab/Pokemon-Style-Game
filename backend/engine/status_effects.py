"""
Status effect system (Burn, Poison, Freeze, ...).

Owner: Battle Engine (Zain)

TODO (Phase 2):
- Represent a status as {name, turns_remaining}
- apply_status_effects(creature) -> mutates HP / skips turn as appropriate
- Called once per turn by turn_engine.py, after attacks resolve
"""
