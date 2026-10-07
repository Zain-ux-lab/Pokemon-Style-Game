"""Deterministic two-action look-ahead for single-player battles."""

from backend.engine.turn_engine import BattleState
from backend.engine.damage import calculate_damage

from .adapter import Action, legal_actions, simulate


def choose_action(state: BattleState, bot_player: int) -> Action | None:
    """Choose a legal action by searching the bot action and the reply."""
    if bot_player not in (0, 1):
        raise ValueError("bot_player must be 0 or 1")
    if state.winner is not None:
        return None

    acting_player = (
        state.replacement_required
        if state.replacement_required is not None
        else state.current_player
    )
    if acting_player != bot_player:
        return None

    actions = legal_actions(state)
    if not actions:
        return None

    best_action = actions[0]
    best_score = float("-inf")
    for action in actions:
        next_state = simulate(state, action)
        turns_to_search = 2 if action.kind == "replace" else 1
        score = _search(next_state, bot_player, turns_to_search)
        if score > best_score:
            best_action = action
            best_score = score
    return best_action


def _search(state: BattleState, bot_player: int, turns_remaining: int) -> float:
    if state.winner is not None:
        return 10000 if state.winner == bot_player else -10000

    if state.replacement_required is not None:
        actions = legal_actions(state)
        if not actions:
            return _evaluate(state, bot_player)
        replacing_player = state.replacement_required
        values = (
            _search(simulate(state, action), bot_player, turns_remaining)
            for action in actions
        )
        return max(values) if replacing_player == bot_player else min(values)

    if turns_remaining == 0:
        return _evaluate(state, bot_player)

    actions = legal_actions(state)
    if not actions:
        return _evaluate(state, bot_player)

    player = state.current_player
    values = (
        _search(
            simulate(state, action),
            bot_player,
            turns_remaining - (action.kind != "replace"),
        )
        for action in actions
    )
    return max(values) if player == bot_player else min(values)


def _evaluate(state: BattleState, bot_player: int) -> float:
    bot_team = state.team(bot_player)
    opponent_team = state.team(1 - bot_player)
    living_difference = sum(not creature.is_knocked_out for creature in bot_team)
    living_difference -= sum(not creature.is_knocked_out for creature in opponent_team)
    hp_difference = sum(
        creature.current_hp / creature.max_hp
        for creature in bot_team
    ) - sum(
        creature.current_hp / creature.max_hp
        for creature in opponent_team
    )
    effect_difference = _effect_value(state, bot_player) - _effect_value(state, 1 - bot_player)
    # Value the continuing exchange as well as the immediate reply. The
    # engine supplies type/stat/status-aware damage; switch cost is already
    # paid in the searched state. One continuing exchange is a positional
    # estimate, not an additional simulated turn.
    active = state.active_creature(bot_player)
    enemy = state.active_creature(1 - bot_player)
    matchup = 0.0
    if not active.is_knocked_out and not enemy.is_knocked_out:
        outgoing = max((calculate_damage(active, enemy, m) for m in active.moves), default=0)
        incoming = max((calculate_damage(enemy, active, m) for m in enemy.moves), default=0)
        matchup = 20 * (outgoing / enemy.max_hp - incoming / active.max_hp)
    return 20 * living_difference + 20 * hp_difference + effect_difference + matchup


def _effect_value(state: BattleState, player: int) -> float:
    """Conservative HP-equivalent estimates beyond the two-action horizon.

    These are positional estimates, not extra simulated damage. Switching and
    safe moves can avoid conditions, so their potential is discounted by half.
    """
    active = state.active_creature(player)
    enemy = state.active_creature(1 - player)
    if active.is_knocked_out:
        return 0
    value = 0.0
    for name, status in active.statuses.items():
        if name == 'echo':
            value += min(10, enemy.current_hp) * 20 / enemy.max_hp
        elif name == 'thorns' and any(m.contact for m in enemy.moves):
            value += 7 * 20 / enemy.max_hp
        elif name == 'spores':
            value -= 3 * status.turns * 20 / active.max_hp
        elif name == 'confuse' and status.slot is not None:
            value -= 4 * status.turns * 20 / active.max_hp
        elif name == 'mark' and any(m.mechanic == 'exploit' for m in enemy.moves):
            value -= 9 * 20 / active.max_hp
        elif name == 'weaken':
            value -= max((m.power for m in active.moves), default=0) * .125 * 20 / enemy.max_hp
        elif name == 'expose':
            value -= max((m.power for m in enemy.moves), default=0) * .125 * 20 / active.max_hp
    return value
