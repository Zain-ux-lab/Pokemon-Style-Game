# Play against the tactical bot

Start the Python app from the repository root and open http://127.0.0.1:8000/:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app
```

The Python app serves both the screen and the battle API. Opening `index.html`
directly or using the old static server on port 8080 will not run battles.

Leave automatic reload off while playtesting: battles live in server memory,
and restarting the server ends active battles. Restart manually after backend edits.

Pick three different characters. Selection order determines your starting
character; you move first. The bot randomly draws three of the remaining seven.
Both rosters are revealed when the battle begins. Hover or focus a move to
see its damage, healing, or guard preview. Switching uses a turn. Replacing a
knocked-out character is free. The human always stays on the near side.

Combat and bot decisions run in Python. The browser displays returned battle
states and sends only the chosen action and expected match revision. This
revision rejects double clicks and actions from an outdated tab. If a response
is lost, the screen fetches the saved state instead of replaying an attack.

Each browser has a separate cookie-based session. Refresh resumes the match.
Matches live in memory, expire after 30 minutes without requests, and disappear
when the server restarts. Run one server worker for this local demo. There are
no accounts, persistent saves, or online multiplayer.

## Current limits

Each character has three move choices; a player uses one move per turn.
Glowmire and Hushwing can heal, while Bramblebelly and Bastion can guard
against the next hit. The bot considers those effects when choosing a move.
The ten names use temporary stats and share three placeholder sprites. The
original three keep their first attack names and HP; new entries reuse prototype stat ranges. Attack and defense are
both 10 until the engine's character data is integrated. Category labels have
no damage bonus yet. Charge, resource costs, and final balancing
remain engine follow-ups; they are not simulated in the browser.

The colosseum background was generated with the built-in image generation tool.
Fonts use Google Fonts with local sans-serif fallbacks. The geometric SVGs are
placeholder art and can be replaced with final pixel sprites.

## Tests

The client recovery test uses Node.js 18+ and its built-in test runner.

```bash
python -m pytest -q
node --test tests/test_client.cjs
```

`tests/test_battle_api.py` exercises team validation, disjoint bot rosters,
automatic bot turns, switching, free replacements, full match completion,
session isolation, and rejection of stale or invalid actions.

## Background generation prompt

Clean pixel-style ancient colosseum for a side-on one-on-one creature battle.
Warm sandstone arches, muted terracotta and teal accents, soft blue sky, and a
broad quiet sandy floor. Consistent pixel clusters, restrained palette, minimal
shading. No characters, HUD, text, glow, ornate detail, or foreground obstacles.
