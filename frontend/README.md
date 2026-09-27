# Battle screen prototype

Open `index.html` in a browser, or serve this folder with `python3 -m http.server 8080`.

This is a local, two-player pass-and-play prototype, not networked multiplayer.
After each action the controls belong to the next player. Hover or focus a move
to see exact demo damage. Click to act. Select a reserve portrait or Switch to
open a confirmation chooser. Knockout replacements do not consume a turn.
New battle resets the match.

Stats, damage and character SVG artwork are placeholders for interface testing.
The handcrafted geometric SVGs can be replaced with final pixel sprites later.
The colosseum background was generated with the built-in image generation tool
and copied into this folder. Fonts use Google Fonts with local sans-serif fallbacks.

The demo starts with fixed teams and a fixed first player. Team selection, roster
restrictions and the first-player rule are not implemented. No accounts, rooms,
or remote actions are connected. The duplicated local rules are for demonstration
only: replace them with authoritative server state during integration. The
backend teammate's engine files have not been changed.

The prototype branch starts from feature/project-setup, avoiding the divergent
engine branches. Merge setup into develop before opening this frontend PR there.

## Background generation prompt

Clean pixel-style ancient colosseum for a side-on one-on-one creature battle.
Warm sandstone arches, muted terracotta and teal accents, soft blue sky, and a
broad quiet sandy floor. Consistent pixel clusters, restrained palette, minimal
shading. No characters, HUD, text, glow, ornate detail, or foreground obstacles.
