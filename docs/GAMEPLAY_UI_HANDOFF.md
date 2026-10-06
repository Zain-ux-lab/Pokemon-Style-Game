# Gameplay handoff for Abijeason

Zain owns gameplay; Abijeason owns UI. Updated 6 October 2026: the homepage integration retains move arrays,
descriptions, turn logs and attack animations. Persistent effect labels,
remaining holder actions and confused-move warnings are now displayed.

## Battle snapshot additions
- `teams[p][i].statuses`: `{name, turnsRemaining, moveIndex, description}[]`.
  `moveIndex` is only meaningful for confusion and identifies the dangerous move.
- `switchBlockedReason`: a message during paralysis, otherwise null. Continue
  using `actions` as the authority for legal moves/switches/replacements.
- Four moves per creature. Each preview has `damageType`, `contact`, `mechanic`,
  `pendingEcho` and `delayedDamage`. Damage previews also have `healing`,
  `selfDamage` and `effectiveness` (80, 100 or 125 percent).
- `amount` remains direct damage, healing HP or guard percent according to `effect`.
  Damaging status moves use `effect: damage` in previews and attack animations.
  Their condition is identified by `mechanic`; descriptions explain its behaviour.
- `delayedDamage` is the exact pending echo expected after the current move.
  `pendingEcho` says one is armed, even if this move would defeat the target first
  or kill its caster through recoil, preventing the echo from firing.
- `/api/roster` keeps card-compatible power/heal/guard values and adds
  `appliesStatus` and `description` to damaging status moves.
- Effect events are readable log entries. HP and legal actions stay server-owned.

## UI integration — 6 October 2026
Effect labels now remain near HP, with remaining holder actions and expandable
explanations. Confused moves carry a recoil warning. Move details show base
damage, damage type, strong/resisted matchups and exact immediate damage;
drain recovery and pending echo are separate figures, and recoil remains in the
engine's description. Four move pills retain the responsive action rail.

## Run and test
Use the project virtual environment. Run `python -m pytest -q`, then
`node --test tests/test_client.cjs`. Start `python -m uvicorn backend.main:app`.
Restart once after pulling backend changes; existing in-memory matches are lost.
The new rules require a new battle. Do not enable reload while playtesting.

## 5 October preview update
Damage previews add `baseDamage` (before type, conditions, guard or HP capping).
`amount` retains exact resolved direct damage for API consumers and tests.
The hover display uses baseDamage and labels it base damage. Guard attacks are
`effect: damage` with `guardPercent: 30` and have attack animations.
Drain recovery is floor(direct HP damage × Recovery / 40), capped at 4 HP and missing HP. Recovery 10 gives 25%; Recovery 9 gives 22.5% before rounding.
