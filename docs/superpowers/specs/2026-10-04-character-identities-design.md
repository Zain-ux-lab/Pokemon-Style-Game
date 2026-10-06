# Character identities and gameplay rules

Implemented gameplay design, 4 October 2026. The user approved switching clearing
statuses and delegated remaining balance values. Zain owns gameplay; Abijeason
owns the interface. This change does not edit frontend files.

## Shared rules
- Three distinct characters per side; bot draws from the seven not picked by the
  human. Four fixed moves each. One active character and one action per turn.
- Voluntary switching costs a turn and clears all temporary conditions, guard,
  and stored reprisal damage on the departing character. Switching either party
  cancels a pending echo. Free knockout replacement does not age conditions.
- Magic beats Physical, Physical beats Spirit, Spirit beats Magic. Move type
  determines effectiveness against defender type: 125% strong, 80% resisted,
  100% same-type. Neutral supports old engine tests/callers. Contact is separate.
- Status durations count the holder's normal actions. Newly applied/refreshed
  effects do not age on their application action. Distinct conditions coexist;
  reapplying refreshes duration but never stacks strength.
- Resolve direct damage, drain healing, recoil/reflection, new statuses, then
  previously scheduled echo and expiry; then settle knockouts. Recoil/reflection
  never triggers additional reflection. Echo cancels if either participant falls
  before it fires. Values round down; healing and damage clamp to valid HP.
- Direct damage order: attack*power/defense (min 1), type (min 1), flat mechanic
  bonus, weaken (75%), expose (125%), guard (unless phase), cap to remaining HP.
  Floor after each division. Zero damage after guard/modifiers is allowed.
- If both active characters fall with reserves remaining, replacements happen
  human first, then bot, without using turns. If both final characters fall in
  one action, the acting player loses: recoil cannot secure a suicide win.
  This deliberately replaces the draft draw suggestion without changing the
  existing winner API (null, 0 or 1).
- No energy, cooldowns, random missed turns, online play or new dependencies.

## Effects
| Mechanic | Behaviour |
|---|---|
| echo | Deal 10 delayed damage after your next action; either character switching cancels it. |
| spores | For two actions, damaging moves cause 6 recoil. Switching clears it. |
| drain | Recover direct HP damage × Recovery / 40, rounded down, up to 4 HP and missing HP (25% at Recovery 10). |
| thorns | Reflect 14 damage from contact hits until after your next action. |
| mark | Mark for two actions. Piercing Volley consumes the mark for +18 damage. |
| exploit | Consume a mark for +18 damage. |
| paralyse | Prevent voluntary switching for one action. Moves remain usable. |
| reprisal | Add half the direct damage received last enemy action, capped at 15. |
| dread | If the target starts below half HP, weaken its next attack by 25%. |
| confuse | For two actions, the marked strongest attack causes 8 recoil. |
| phase | Ignore and consume guard. Type resistance still applies. |
| harvest | Consume spores for +10 damage, ending their ongoing pressure. |
| weaken | Next damaging move deals 25% less damage; expires after two actions. |
| expose | Next direct hit deals 25% more damage; expires after two actions. |

Thorns lasts through the holder's next normal action. Echo is stored on its
caster and fires after the caster's next move; repeated Echo fires the existing
one and schedules a fresh one. Spores, confusion, mark, weaken and expose last
up to two holder actions. Paralysis lasts one. Confusion marks the highest-power
damaging move (first slot breaks ties), retaining that slot on reapplication.
Reprisal remembers only direct damage from the preceding enemy normal action;
non-damaging enemy moves and voluntary switches reset it. Exploit/Harvest consume
mark/spores respectively; damaging moves consume weaken and expose and guard.
Status attacks apply their condition only to a surviving holder.

## Four-move roster
Offensive status moves have 10 base power, so setup does not sacrifice an entire
attack. Healing was reduced after repeatable 25-HP heals stalled test matches.
These are initial playtest values, not a claim of competitive balance.

### Mage — Magic, 100 HP

| Move | Power / recovery | Type | Effect |
|---|---|---|---|
| Arcane Bolt | 22 | Magic | Direct attack. |
| Staff Strike | 20 | Physical | Contact. Direct attack. |
| Spell Echo | 15 | Magic | Deal 10 delayed damage after your next action; either character switching cancels it. |
| Arcane Ward | 12 | Magic | Attack and protect against 30% of next hit. |

### Sporestag — Physical, 120 HP

| Move | Power / recovery | Type | Effect |
|---|---|---|---|
| Horn Jab | 22 | Physical | Contact. Direct attack. |
| Spore Cloud | 10 | Spirit | For two actions, damaging moves cause 6 recoil. Switching clears it. |
| Antler Harvest | 18 | Spirit | Contact. Consume spores for +10 damage, ending their ongoing pressure. |
| Chitin Shell | 12 | Physical | Contact attack and protect against 30% of next hit. |

### Glowmire — Spirit, 90 HP

| Move | Power / recovery | Type | Effect |
|---|---|---|---|
| Ember Beam | 23 | Magic | Direct attack. |
| Soul Siphon | 16 | Spirit | Recover direct HP damage × Recovery / 40, rounded down, up to 4 HP and missing HP (25% at Recovery 10). |
| Lantern Flare | 12 HP | — | Uses one action. |
| Revealing Light | 10 | Spirit | Next direct hit deals 25% more damage; expires after two actions. |

### Bramblebelly — Physical, 120 HP

| Move | Power / recovery | Type | Effect |
|---|---|---|---|
| Bramble Bash | 24 | Physical | Contact. Direct attack. |
| Root Snare | 12 | Spirit | Attack and protect against 30% of next hit. |
| Thorn Burst | 20 | Spirit | Direct attack. |
| Thorn Coat | 10 | Physical | Reflect 14 damage from contact hits until after your next action. |

### Veyne — Physical, 100 HP

| Move | Power / recovery | Type | Effect |
|---|---|---|---|
| Steady Shot | 22 | Physical | Direct attack. |
| Runic Arrow | 20 | Magic | Direct attack. |
| Piercing Volley | 18 | Physical | Consume a mark for +18 damage. |
| Mark Prey | 10 | Physical | Mark for two actions. Piercing Volley consumes the mark for +18 damage. |

### Coil — Magic, 100 HP

| Move | Power / recovery | Type | Effect |
|---|---|---|---|
| Spark Bolt | 23 | Magic | Direct attack. |
| Coil Lash | 20 | Physical | Contact. Direct attack. |
| Static Lock | 10 | Magic | Prevent voluntary switching for one action. Moves remain usable. |
| Voltage Leak | 10 | Magic | Next damaging move deals 25% less damage; expires after two actions. |

### Bastion — Physical, 120 HP

| Move | Power / recovery | Type | Effect |
|---|---|---|---|
| Shield Bash | 12 | Physical | Contact attack and protect against 30% of next hit. |
| Stone Fist | 23 | Physical | Contact. Direct attack. |
| Reprisal | 14 | Physical | Contact. Add half the direct damage received last enemy action, capped at 15. |
| Rune Pulse | 20 | Magic | Direct attack. |

### Vesperfang — Magic, 100 HP

| Move | Power / recovery | Type | Effect |
|---|---|---|---|
| Dusk Bolt | 22 | Magic | Direct attack. |
| Night Fang | 21 | Spirit | Contact. Direct attack. |
| Dread | 18 | Magic | If the target starts below half HP, weaken its next attack by 25%. |
| Terrify | 10 | Magic | Next direct hit deals 25% more damage; expires after two actions. |

### Hushwing — Spirit, 90 HP

| Move | Power / recovery | Type | Effect |
|---|---|---|---|
| Echo Strike | 22 | Spirit | Direct attack. |
| Soft Wing | 10 HP | — | Uses one action. |
| Wing Buffet | 20 | Physical | Contact. Direct attack. |
| Disorient | 10 | Spirit | For two actions, the marked strongest attack causes 8 recoil. |

### Riftclaw — Spirit, 100 HP

| Move | Power / recovery | Type | Effect |
|---|---|---|---|
| Rift Slash | 24 | Spirit | Contact. Direct attack. |
| Phase Strike | 18 | Spirit | Contact. Ignore and consume guard. Type resistance still applies. |
| Reality Tear | 20 | Magic | Direct attack. |
| Fracture | 10 | Spirit | Next direct hit deals 25% more damage; expires after two actions. |

## Bot and verification
The deterministic search simulates its move and an opponent response using the
same engine. A conservative positional score values pending effects beyond
that horizon. It is not an optimal solver; deeper combo search remains a future
improvement. Illegal switches during paralysis are excluded by engine validation.

Regression tests cover all mechanics, durations, switching, replacement, double
knockouts, four-move API output and all 40 previews versus engine outcomes across
three defender types. Ten seeded bot-v-bot matches finished in 33–48 actions,
with a maximum observed decision time of 0.094 seconds on the test machine.

UI integration is intentionally separate: see docs/GAMEPLAY_UI_HANDOFF.md.

## 5 October playtest update
Move details display unmodified attack*power/defense base damage. Matchups,
conditional bonuses, guard and target remaining HP change resolved damage only.
All four guard moves now attack at 12 power and grant 30% next-hit protection.
Soul Siphon restores floor(actual direct damage/4), capped at 4 HP and missing HP.
