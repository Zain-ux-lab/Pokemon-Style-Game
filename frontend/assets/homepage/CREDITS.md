# Homepage asset credits

Updated 9 October 2026.

## Artwork and identity

The skyship background (`skyship/skyship.png`), attack-ready Bastion
(`skyship/bastion-ready.png`) and lighter approaching Vesperfang
(`skyship/vesperfang-sunlit-approach.png`) were created with built-in image
generation for this project's selected homepage concept. Vesperfang's head
and front claws face down toward Bastion; the layered scene keeps its face
clear of the sword and shield. The gold C emblem is an original SVG drawn for
Clashbound. No artwork extracted from another game or reference website is
bundled. The references guided composition and visual direction.

The ten transparent character illustrations and eight arena backgrounds were
created with built-in image generation for the project's Issue #20 artwork.
Hushwing is a group of five spirit bats; Mistwater Citadel has a dry rocky
cliff above the water. The original generated Sunstone Colosseum is used in
the gallery. The homepage video is recorded from actual gameplay in Windscar Mesa. The playable battle now uses the same ten character designs and eight arenas
from its shared character and arena asset directories.

Generation records: `prompts.json`, `skyship/prompts.json`, and
`skyship/vesperfang-sunlit-approach-prompts.json`. Discarded local variants
and the wing-frame atlas are not distributed.

## Audio

`audio/heroic-age.mp3`: **Heroic Age** by Kevin MacLeod (incompetech.com).
Licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

- Source: https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1100848
- Download: https://incompetech.com/music/royalty-free/mp3-royaltyfree/Heroic%20Age.mp3
- License: https://creativecommons.org/licenses/by/4.0/

The recording is bundled unmodified. Attribution is also visible in the homepage/character-page audio settings and battle music settings. Music is enabled by default for new visitors; an explicit mute is remembered. Playback is attempted on load and retried on a click/tap/key interaction when the browser blocks autoplay. Homepage and battle pages pause music when hidden.

The previous original `audio/embers-before-battle.m4a` remains an unused historical asset. Click chimes are synthesized with Web Audio.

## Gameplay video

`video/clashbound-gameplay.mp4` and `video/gameplay-poster.jpg` were captured from the project's actual browser game on 9 October 2026. The 20-second clip shows Mage's attack/guard, a confirmed switch to Vesperfang, bot replies and Dusk Bolt in Windscar Mesa. It has no audio track, so music can be muted independently. Capture details: `video/RECORDING.md`.

## Fonts

Cinzel (The Cinzel Project Authors) and Barlow (The Barlow Project Authors) are
unmodified font files bundled under the SIL Open Font License 1.1. Their
copyright notices and full licences are included beside them:

- `fonts/Cinzel-Variable.ttf` and `fonts/Cinzel-OFL.txt`
- `fonts/Barlow-Regular.ttf`, `fonts/Barlow-SemiBold.ttf`, and `fonts/Barlow-OFL.txt`

Official sources:

- https://github.com/google/fonts/tree/main/ofl/cinzel
- https://github.com/google/fonts/tree/main/ofl/barlow

The personal-use MIDELTANK demo used in the earlier local mockup is excluded
from Git and is not referenced by the published pages. No paid font licence
is required for the bundled fonts.

## Design references

User-supplied references: Dribbble's Game Landing Page animation, ThreeUI,
TasteSkill, GSAP and 21st.dev. The implementation uses original CSS and
JavaScript; no code, music, brand assets or artwork from those sites is
bundled. No animation-library dependency is required.
