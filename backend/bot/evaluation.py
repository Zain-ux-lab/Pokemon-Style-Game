"""Reproducible headless evaluation using the real battle engine.

Run: python -m backend.bot.evaluation --fixtures 20 --output /tmp/bot-results.json
"""
import argparse
import json
import platform
import random
import statistics
from time import perf_counter

from backend.roster import ROSTER
from backend.engine.creature import Creature
from backend.engine.moves import Move
from backend.engine.turn_engine import BattleState
from backend.bot.adapter import legal_actions, simulate
from backend.bot.search import choose_action

BY_ID = {entry['id']: entry for entry in ROSTER}


def make_fixtures(seed, count):
    rng = random.Random(seed)
    fixtures = []
    for _ in range(count):
        ids = rng.sample(list(BY_ID), 6)
        teams = []
        for offset in (0, 3):
            team = []
            for identifier in ids[offset:offset + 3]:
                entry = BY_ID[identifier]
                fixed = entry['signatureMoves']
                moves = sorted(fixed + rng.sample([i for i in range(len(entry['movePool'])) if i not in fixed], 2))
                team.append({'id': identifier, 'moves': moves})
            teams.append(team)
        fixtures.append(teams)
    return fixtures


def baseline_action(state, strategy, rng):
    actions = legal_actions(state)
    if strategy == 'random':
        return rng.choice(actions)
    if state.replacement_required is not None:
        return actions[0]
    # Greedy baseline uses actual immediate enemy HP loss, including ticks.
    # It never voluntarily switches; ties use the earliest move slot.
    enemy = 1 - state.current_player
    before = sum(c.current_hp for c in state.team(enemy))
    return max((a for a in actions if a.kind == 'move'),
               key=lambda a: before - sum(c.current_hp for c in simulate(state, a).team(enemy)))


def play_match(fixture, baseline, first_player, seed, max_actions):
    teams = []
    for team in fixture:
        creatures = []
        for selected in team:
            entry = BY_ID[selected['id']]
            stats = entry['stats']
            creatures.append(Creature(entry['name'], entry['maxHp'], stats['power'], stats['armour'],
                tuple(Move(**entry['movePool'][i]) for i in selected['moves']),
                battle_type=entry['type'], focus=stats['focus'], ward=stats['ward'], recovery=stats['recovery']))
        teams.append(creatures)
    state = BattleState(*teams, current_player=first_player)
    rng = random.Random(seed)
    actions = replacements = 0
    timings = []
    while state.winner is None and actions < max_actions:
        player = state.replacement_required if state.replacement_required is not None else state.current_player
        started = perf_counter()
        action = choose_action(state, 0) if player == 0 else baseline_action(state, baseline, rng)
        if player == 0:
            timings.append((perf_counter() - started) * 1000)
        state = simulate(state, action)
        if action.kind == 'replace':
            replacements += 1
        else:
            actions += 1
    return {'baseline': baseline, 'first_player': first_player, 'winner': state.winner,
            'actions': actions, 'replacements': replacements, 'decision_ms': timings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', type=int, default=20)
    parser.add_argument('--seed', type=int, default=20261007)
    parser.add_argument('--max-actions', type=int, default=200)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if args.fixtures < 1 or args.max_actions < 1:
        parser.error('fixtures and max-actions must be positive')
    fixtures = make_fixtures(args.seed, args.fixtures)
    matches = []
    for baseline in ('random', 'damage'):
        for index, fixture in enumerate(fixtures):
            for first in (0, 1):
                result = play_match(fixture, baseline, first, args.seed + index * 2 + first, args.max_actions)
                result['fixture'] = index
                matches.append(result)
                print(f'{baseline} fixture {index + 1}/{args.fixtures} first={first} winner={result["winner"]} actions={result["actions"]}', flush=True)
    summaries = {}
    for baseline in ('random', 'damage'):
        games = [m for m in matches if m['baseline'] == baseline]
        times = sorted(t for m in games for t in m['decision_ms'])
        summaries[baseline] = {'games': len(games), 'wins': sum(m['winner'] == 0 for m in games),
            'losses': sum(m['winner'] == 1 for m in games), 'unfinished': sum(m['winner'] is None for m in games),
            'mean_actions': statistics.mean(m['actions'] for m in games),
            'decision_median_ms': statistics.median(times), 'decision_p95_ms': times[int((len(times)-1)*.95)]}
    report = {'seed': args.seed, 'max_actions': args.max_actions, 'python': platform.python_version(),
              'platform': platform.platform(), 'fixtures': fixtures, 'summary': summaries, 'matches': matches}
    with open(args.output, 'w') as file:
        json.dump(report, file, indent=2)
        file.write('\n')
    print(json.dumps(summaries, indent=2))


if __name__ == '__main__':
    main()
