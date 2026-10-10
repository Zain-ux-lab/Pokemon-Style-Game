# Clashbound homepage and bot battles

Start the Python app from the repository root and open http://127.0.0.1:8000/:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app
```

The Python app serves both the screen and the battle API. Opening `index.html`
directly or using the old static server on port 8080 will not run battles.

The root URL opens the homepage. Select **Play now** to open the existing
team-selection and battle screen at `/battle.html`. The separate character page
is at `/characters.html`; its links also enter the same game.

## Homepage

Updated 6 October 2026. This skyship redesign is ready for team review.

- The hero features Bastion in a ready stance on the skyship deck and Vesperfang
  approaching through the bright sky. The hero features only this pair; all ten fighters have
  introductions on the separate Characters page.
- Vesperfang uses a large, crisp, sweeping flight silhouette with sunlit lavender scales, a lowered head and reaching claws. It approaches Bastion from above with space around the raised sword. Homepage text uses restrained shadows for contrast.
- Vesperfang uses a new, lighter lavender-and-slate flight pose, aimed toward
  Bastion. It holds that pose and gently hovers. A mouse hover adds
  a soft violet glow. The scene also adds sky drift, Bastion breathing,
  sword light and armour glints. The navigation
  includes a pause control. Reduced motion disables decorative animation;
  motion also pauses when the hero is off screen or the tab is hidden.
- Cinzel is the display font and Barlow is the reading font. Both are bundled
  under the SIL Open Font License, with their copyright notices and licences.
  The original gold C emblem matches the blue-and-gold scene. The personal-use
  MIDELTANK demo from the local mockup is not distributed or referenced.
- The blue **Play now** button with gold trim opens the existing battle
  screen. Navigation and buttons have hover glow and keyboard focus styles.
- Heroic Age by Kevin MacLeod is enabled by default, with attribution under
  CC BY 4.0. The navigation mute control remembers your choice across the
  homepage and battle. If autoplay is blocked, music starts after a click, tap
  or keypress. Audio settings has separate music and effects levels; playback
  pauses while the tab is hidden.
- **Every turn matters** contains a 20-second recording of the actual game in
  Windscar Mesa: Mage attacks/guards, the player confirms a switch to
  Vesperfang, and the bot replies. Native video controls support play/pause,
  replay and fullscreen. The clip has no audio track; background music remains
  independently controllable. See `assets/homepage/video/RECORDING.md`.
- The gallery shows the eight playable arenas, including Sunstone Colosseum and
  Mistwater Citadel's dry rocky cliff. A new match selects an arena; refresh keeps it.
- The homepage adapts to portrait and landscape screens. The Characters page
  retains its existing ten introductions with shared blue-and-gold styling.

The homepage integrates the gameplay merged in PR #22. Play now opens its
team selection, move builds, ten character sprites and eight arenas. Combat
rules, bot and API remain server-owned. Asset origins and generation prompts
are in `assets/homepage/CREDITS.md` and `assets/homepage/prompts.json`.

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

## Battle UI integration — 6 October 2026

- Choose three characters and enter immediately with default four-move builds.
  Open **Customise moves** to choose two alternatives alongside the two locked
  signatures. Detailed stats remain behind an expandable section.
- Both active characters display effect names and remaining holder actions beside
  HP. Open the labels for descriptions. Confusion identifies the affected move
  and warns that it causes eight recoil. Paralysis explains blocked switching.
- Move details keep base damage as the main figure and also show move type,
  matchup and direct damage. Healing, recoil and pending echo descriptions come
  from the engine. Both sides retain move announcements and signed HP feedback.
- The root page is the animated homepage; battle.html contains the latest game
  page, including arena-name, loadout-options and the original battle hooks.
- Battle typography uses the same bundled free Cinzel/Barlow fonts as the homepage.

## Current limits

Balance remains provisional. Six stats scale moves, and type advantages are
implemented: Magic beats Physical, Physical beats Spirit, Spirit beats Magic.
Artwork is static with CSS combat animations. No character limb rigging, energy,
cooldowns, progression, accounts or online multiplayer are included.
The homepage video is a recording of a real match; Play now opens the live game.

## Tests

The client recovery test uses Node.js 18+ and its built-in test runner.

```bash
python -m pytest -q
node --test tests/test_*.cjs
```

`tests/test_battle_api.py` exercises team validation, disjoint bot rosters,
automatic bot turns, switching, free replacements, full match completion,
session isolation, and rejection of stale or invalid actions.

## Artwork records

See `assets/homepage/CREDITS.md`, `assets/characters/SOURCE.md`,
`../docs/CHARACTER_ART.md` and `../docs/ARENA_ART.md` for artwork provenance.

## Presentation update · 9 October 2026

The hero title scales within its copy column, keeping the complete Clashbound
name away from the fighters. Standalone guide paragraphs use dark slate text
against the cream background; the embedded guide keeps its existing contrast.

Heroic Age by Kevin MacLeod replaces the earlier theme on the homepage,
character page and battle screen. New visitors have music enabled by default.
Browser autoplay restrictions may require a first click, tap or key interaction.
Muting is remembered across the homepage and battle screen. Attribution and the
CC BY 4.0 license link appear in music settings and asset credits.

### Consistent battle layout — 9 October 2026

`battle-layout.css` owns the battlefield's positions and proportional sizing.
The HP panels remain in the top corners, the opponent roster stays on the right,
the player roster stays bottom left, and all four moves stay in one right column.
Controls scale down on smaller landscape screens; the move column can scroll
when unusually long feedback needs more space. Individual body proportions,
foot anchors and shadows remain attached to the fighters. On portrait phones,
a rotation prompt asks for landscape; rotating preserves the current match.
The gameplay clip has been recorded again with this layout.
