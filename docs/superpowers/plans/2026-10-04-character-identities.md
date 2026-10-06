# Character identities implementation plan

Goal: four coherent moves for ten characters, deterministic statuses and types.
Architecture: existing engine remains authoritative for API and bot simulation.
Tech stack: Python dataclasses, FastAPI, pytest; no new dependencies.
Spec: ../specs/2026-10-04-character-identities-design.md

User delegated remaining specifics and requested implementation in this chat.
Execute inline. Zain owns gameplay; Abijeason owns UI. Do not edit frontend files.

## Tasks
1. Engine: extend Move with type/contact/mechanic; Creature with type/statuses and
   last incoming damage. Implement type damage, status lifecycle, ten mechanics,
   switch clearing, multiple knockout handling. Test each effect and interactions.
2. Roster/API: extract forty move definitions to backend/roster.py. Share a pure
   move outcome function between engine and previews. Return effects, type,
   contact, self-damage and delayed-damage fields plus readable descriptions.
3. Bot: value statuses alongside health, retain deterministic lookahead and test
   setup, paralysis legality and switch escape. Benchmark complete matches.
4. Documentation: update rules and give Abijeason the additive API contract.
   Run Python/JS regression suites and an API match matrix before publishing.

Review focus: exact duration/refresh; no mutation on illegal moves; simultaneous
knockouts; preview versus actual damage; no infinite recoil or bot search loops.

Balance decisions: Magic > Physical > Spirit > Magic; 125% advantage, 80%
resistance, neutral same type. Neutral is retained for legacy engine callers.
If both final characters fall in one action, the acting player loses (prevents
suicide wins and preserves the existing winner contract). Document this change
from the initial draft's draw proposal. Guard and statuses clear on switching.
