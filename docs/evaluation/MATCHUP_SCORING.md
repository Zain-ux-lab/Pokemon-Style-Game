# Matchup-aware bot scoring

The revised bot switches before imminent knockout when another character can
trade damage better. It remains deterministic, uses the same real engine and
searches its action plus an opponent reply. No battle rules or stats changed.

## What changed

The old leaf score was `100 × living difference + 20 × HP fraction difference
+ status value`. Its large living bonus treated a reserve on 1 HP almost like
a healthy reserve, encouraging expensive last-minute preservation.

The new score uses `20 × living difference + 20 × HP fraction difference
+ status value + matchup value`. Matchup value is:

```
20 × (best outgoing damage / enemy max HP − best incoming damage / own max HP)
```

Damage comes from the engine's type/stat/status-aware calculation. This term
estimates one continuing exchange; it does not simulate extra turns, temporary
guard protection, healing, recoil or future switching. The existing search
still simulates the immediate action and reply, including those effects and
switch costs. Actual victory/loss retains its terminal ±10,000 score.

## Before and after

Each row contains 40 games with identical builds/teams between policies and
both starting positions. Win rates include unfinished games in the denominator.
There were no unfinished games.

| Teams | Opponent | Original wins | Revised wins |
|---|---|---:|---:|
| Original seed 20261007 | Damage-only | 19/40 (47.5%) | 20/40 (50%) |
| Original seed 20261007 | Random | 37/40 (92.5%) | 35/40 (87.5%) |
| Fresh seed 20261009 | Damage-only | 16/40 (40%) | 20/40 (50%) |
| Fresh seed 20261009 | Random | 38/40 (95%) | 37/40 (92.5%) |

This is a **modest, mixed improvement**: better against damage-only on both
sets, slightly worse against random on both. It does not establish superiority
over damage-only, statistical significance, or strength against humans.
The original-team set was used during development; seed 20261009 was evaluated
once for the selected revised policy, with no subsequent tuning.

Revised decision latency (median / p95): 35.5 / 51.9 ms against damage-only on
original teams; 32.2 / 50.4 ms on fresh teams. Runs shared the local machine with
other evaluation processes, so these timings are illustrative, not a controlled
performance comparison or a deployed-server guarantee.

## Experiments we rejected

A stronger damage-rate weight (60) reduced original-set damage-only wins to
15/40. A remaining-hit-count estimate reduced them to 6/40 and encouraged
unhelpful guarding/switching. Neither policy is retained. A preliminary seed
20261008 also exposed regression in the first candidate; it was not used as
the final validation set. See [rejected summaries](rejected-matchup-candidates.json).

## Evidence and reproduction

- [Original revised results](matchup-original.json)
- [Fresh original-policy results](original-holdout.json)
- [Fresh revised-policy results](matchup-holdout.json)
- [Original initial results and method](BOT_EVALUATION.md)

Original policy: commit `6c5cf556d5b5067f4201a0ecb033bb2862e93f09`.
Revised policy: this PR's version of `backend/bot/search.py`.

```bash
python -m backend.bot.evaluation --fixtures 20 --seed 20261007 --output /tmp/original-teams.json
python -m backend.bot.evaluation --fixtures 20 --seed 20261009 --output /tmp/fresh-teams.json
```

To reproduce the original policy, run these commands from a separate checkout
of the original commit. Raw artifacts keep fixtures, outcomes and timing samples.

Two regression tests cover early beneficial switching and avoiding switches
when the reserve cannot improve the matchup. Existing tests retain finishing
attacks, survival healing/guarding, free replacements and live-state immutability.

## Next improvement

Inspect remaining losses and test deeper search with pruning against this
policy on new seeds. Keep the mixed random-opponent result visible. Human
playtesting and mirrored team assignments are still needed before claiming
robust playing strength. This version is ready for review, not an automatic merge.
