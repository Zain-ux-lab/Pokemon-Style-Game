# BattleLab bot integration — proposed design

Prepared 29 September 2026. Design for review, not implemented.

## Goal and ownership

Build a tactical, deterministic bot for the single-player game. The player
selects three distinct characters from ten. The bot samples three distinct
characters from the remaining seven. Both teams are then visible.
Zain owns the bot and frontend; Abijeason owns the engine and character effects.
This document does not change engine files or assign unagreed work to Abijeason.

## Verified starting point

Inspected main at be3e5665ac7ef9a1211b066857eedfd37814414c and engine branch
aeee9b89f98d77b319e698a395569a4215b7b222. The engine exposes BattleState,
resolve_turn, switch_active and replace_knocked_out. These functions mutate
their supplied state. Python deepcopy can isolate a trial battle; a direct
check verified that an attack on a copy leaves the live state unchanged and
that a forced replacement preserves the next player's turn.

The current models have no character ID, category, charge, guard, healing,
or resource-cost fields. Move requires positive power, so a preparation-only
move cannot yet be represented. Team size is only checked for non-emptiness.
The existing pytest suite could not be run with the bundled Python because
pytest is absent. The direct simulation check is not a substitute for that suite.

## Recommended approach and alternatives

Use a small bot adapter that invokes the existing engine functions on copied
state. This lets bot development begin with ordinary attacks and switches while
Abijeason implements effects. Do not reimplement damage in the bot.

Waiting for a redesigned engine interface would reduce temporary adapter code
but block parallel work. A separate bot-only combat simulator would be faster
initially but duplicate rules and risk disagreement with real matches; reject it.

## Interface proposal

- Action(kind, index): kind is move, switch, or replace. Index selects an entry
  in the active character's move list or the relevant player's team.
- legal_actions(state): return actions for the player who must act, empty on
  terminal states. Pending replacement returns only living reserve choices.
- simulate(state, action): deepcopy state, apply the action through the engine,
  and return the resulting copy. Never change the input.
- choose_action(state, bot_player): return a legal action when the bot must act;
  return None on a finished match or when waiting for the human.

Initially the adapter can list candidates and filter them by the existing
engine's validation on copies. If adding effects makes separate move-legality
checks necessary, agree an engine-owned legal_actions helper with Abijeason.
The search and future server can then share it. Do not catch arbitrary errors
and silently treat engine bugs as illegal moves.

## Search and replacement handling

Search two normal actions: the bot action and the human response. Maximise the
bot's score; assume the human minimises it. Early terminal results stop search.
Forced replacements branch over eligible reserves but do not consume search
depth, because they do not use a turn. Resolve pending replacements before
evaluating a leaf. The replacing side chooses in its own interest.

The bot sees public battle state, never the human's future action. Equal-score
choices use stable ordering: move before switch, then lowest index. This avoids
random play and unnecessary switches on ties. It does not guarantee no cycles.

Proposed initial score, from the bot's perspective:
100 × (living bot characters − living human characters)
+ 20 × (sum of bot HP fractions − sum of human HP fractions).
Terminal win/loss scores are +10000/-10000. HP fraction is current_hp/max_hp.
These are tuning parameters, not a claim of optimal play. Category effects
enter via engine damage; preparation needs an additional value once the engine
defines it. Do not pretend this first score understands unimplemented effects.
One-exchange search can undervalue longer setups; address this with specific
test positions and later bounded deeper search if evidence warrants it.

## Files and boundaries

Propose new backend/bot/adapter.py, backend/bot/search.py and tests/test_bot.py
on feature/tactical-bot. Engine files stay with Abijeason. Team selection and
sampling belong to match setup, outside the search. Stable roster IDs and the
ten definitions must come from the agreed character data, not display names.
Web endpoints, frontend integration and deployment are separate subsequent work.

## Validation

Test winning moves, avoiding an immediate loss when a safe option exists,
choosing a useful switch, legal replacement, terminal states, stable tie breaks,
both player indices, and deep equality of live state before/after search.
Check that every simulated action uses the engine and consumes the correct depth.

After special moves are supported, add scenarios for preparing attacks,
protection expiry, resource costs, healing, and switching away from buffs.
Only then evaluate the completed roster against a random legal-action baseline.
Use seeded roster samples, reverse player order, and report wins, losses,
draws/capped matches, and decision latency. A benchmark action limit prevents
endless trials; it does not establish a new player-facing draw rule.

## Decisions to confirm before implementation

1. Start with the existing-engine adapter while character effects develop in
   parallel, or wait for Abijeason's expanded engine. Recommend the adapter.
2. Confirm the Action(kind, index) representation and engine-owned legality
   boundary with Abijeason.

This design uses the already approved one-exchange tactical search. It does
not approve final balancing values, change combat rules, or merge any branches.
