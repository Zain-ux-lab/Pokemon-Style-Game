"""
Turn resolution engine.

Owner: Battle Engine (Zain)

Implements the sequence from the README:
    Receive both moves -> Determine move order -> Apply attacks
    -> Apply status effects -> Check knockouts -> End turn

TODO (Phase 1):
- resolve_turn(battle_state, move_a, move_b) -> new battle_state
- Determine order using speed + move priority
- Deterministic: same inputs always produce same outputs (needed for
  server-authoritative multiplayer + easy testing)
"""
