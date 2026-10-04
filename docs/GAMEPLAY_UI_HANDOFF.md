# Gameplay handoff for Abijeason

Zain owns gameplay; Abijeason owns UI. No frontend files changed in this branch.
The existing client still renders move arrays, descriptions, turn logs and attack
animations. Dedicated effect badges/type indicators are the remaining UI work.

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

## Suggested UI work
Show small hover/focus effect badges near HP, including remaining actions. Mark
the confused move and its recoil warning. Show damage type and strong/resisted
matchups in move details. Present immediate damage, drain recovery, recoil and
echo separately. Ensure four move pills fit on smaller screens. These are
integration suggestions, not interface changes included in this branch.

## Run and test
Use the project virtual environment. Run `python -m pytest -q`, then
`node --test tests/test_client.cjs`. Start `python -m uvicorn backend.main:app`.
Restart once after pulling backend changes; existing in-memory matches are lost.
The new rules require a new battle. Do not enable reload while playtesting.
