# Bot evaluation — 7 October 2026

The tactical bot beats a random opponent reliably in this sample, but **does not
outperform a damage-only opponent**. This is a baseline to improve, not evidence
that the bot is stronger than human players.

| Opponent | Games | Tactical wins | Losses | Unfinished | Win rate | Mean actions |
|---|---:|---:|---:|---:|---:|---:|
| Random legal action | 40 | 37 | 3 | 0 | 92.5% | 37.8 |
| Highest immediate damage | 40 | 19 | 21 | 0 | 47.5% | 28.2 |

An action means an attack, heal, status move or voluntary switch. Free knockout
replacements are counted separately. A battle stops at 200 actions; unfinished
battles never count as wins.

## How the comparison works

- Seed `20261007` generates 20 fixtures. Each has six distinct characters: three
  for the tactical bot, three for its opponent. Both keep the same teams against
  both baselines.
- Every character keeps its two signature moves and receives two seeded random
  alternatives. Builds stay identical when the starting player changes.
- Each fixture runs twice per baseline: tactical first, then opponent first.
  Tactical always occupies player slot zero; only the starting turn changes.
- Random chooses uniformly among legal actions, including switches. This is a
  weak baseline because it can switch unnecessarily.
- Damage-only chooses the move with the greatest actual immediate enemy team HP
  loss after engine resolution, including status ticks. It never voluntarily
  switches, uses the earliest move slot on ties, and replaces a knockout with
  the first living reserve. It does not look ahead or value its own healing.
- Tactical uses the existing `choose_action` function without modifications.
  All candidates and executed actions use the real engine, not a separate
  approximation of combat.

## Speed

| Opponent | Median tactical decision | 95th percentile |
|---|---:|---:|
| Random | 32.1 ms | 43.0 ms |
| Damage-only | 35.3 ms | 51.3 ms |

These are local wall-clock measurements on macOS/Python 3.14. They include
knockout replacement decisions, exclude rendering/network delays, and will vary
on a deployed server. Percentiles use the sorted sample's floor-index value.

## Reproduce

From the repository with dependencies installed:

```bash
python -m backend.bot.evaluation --fixtures 20 --seed 20261007 --max-actions 200 --output /tmp/bot-results.json
```

[Raw results](bot-results-2026-10-07.json) include every team, move selection,
starting player, outcome, action count and decision timing. The engine, roster
and tactical search were evaluated at commit `0125ca8832ec3543ee2117a66e93dddd438758ca`.
Timing values will differ on reruns; fixtures and outcomes are deterministic
with unchanged code and seed.

## What this tells us

The current bot's HP/status scoring and short lookahead are insufficient to
establish an advantage over simply attacking. This run does **not** isolate
whether losses come from scoring, switching, build quality or roster matchups.
Before changing the AI, inspect losing fixture traces, then compare changes on
these fixtures and on a separate seed to avoid tuning only to this sample.

Twenty paired fixtures are a small sample; the two games in each pair are
related, and rosters are not exhaustively balanced. No human playtesting,
self-play, difficulty comparison or production load test is included.
