# Loadouts, stats and battle feedback — handoff to Abijeason

Zain owns gameplay; Abijeason owns presentation. This change includes a working
selection/feedback implementation so the new gameplay can be tested now. Keep
these behaviours when adapting menus, settings, music and visual styling.

## Selection contract
`GET /api/roster` now supplies `stats`, `signatureMoves` (two pool indices), and
`movePool` (six definitions). `moves` still contains the default four.
`POST /api/battle` accepts optional `loadouts: {characterId: [four pool indices]}`.
Selections must include both signatures and exactly two distinct alternatives.
Only chosen roster ids may appear. The server rejects invalid selections before
resetting any existing match. Old requests without loadouts use default moves.
Bot rosters remain disjoint and get two signatures plus two random alternatives.
Snapshots contain only the chosen four moves, in requested order, with full stats.

## Stats and scaling
HP, Power, Focus, Armour, Ward and Recovery differ per character. Physical attacks
use Power/Armour; Magic/Spirit use Focus/Ward, regardless of contact. Base damage
is floor(offense*move power/defense), minimum one for a damaging move. Type and
status modifiers follow afterward. Recovery uses baseline ten: a ten-HP heal
with Recovery twelve restores twelve (capped at missing HP). Drain restores
floor(actual damage*Recovery/40), still capped at four HP. No crit chance added.

## Feedback contract
Animation metadata adds `moveName` for damaging moves, otherwise null, plus
`hpChanges: [{player: 0|1, amount: signed net HP change}]`. Announce names for
attacks by either side; healing and pure protection do not announce move names.
HP changes are exact net action outcomes including recoil, lifesteal and echo.
The UI shows signed floating values and animates HP bars; reduced motion is
respected. Type icons: Magic ✦, Physical ◆, Spirit ◉, with hover/accessibility names.
Effects are not intentionally hidden, but only applications are logged today.
Persistent status badges (remaining actions and confused move slot) are pending
Abijeason's UI integration; guard is the only persistent HUD indicator currently.

## Homepage integration and release order
Merge gameplay PR #22 first. On homepage PR #23, update battle.html to preserve
#arena-name, #loadout-options and all battle client hooks before merging.
Use default builds immediately; the custom-build picker is an optional collapsed
advanced step. Character stats sit behind a separate disclosure. Playtest default
builds before expanding mechanics; no statuses have been removed.

## Files to coordinate
frontend/script.js, frontend/style.css, frontend/index.html and API snapshots.
Merge the gameplay branch before starting overlapping edits. Preserve signature
locking, four-move validation, accessible labels and server-authoritative damage.
README now describes the duo and shipped prototype without historical multiplayer
claims. No accounts, multiplayer or persistent database saves have been added.
