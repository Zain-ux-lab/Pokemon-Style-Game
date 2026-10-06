# BattleLab development and polish checklist

Reference reviewed: https://www.youtube.com/watch?v=6tef3Gs1AhU
Reviewed 6 October 2026 using the English auto-generated transcript; visual demonstrations and tool-quality claims were not independently verified.

## Techniques adopted from the video
- Agree on a visual concept before producing final assets.
- Include asset prompts and required animations in the design notes.
- Compare the running scene against its reference for proportions, composition and lighting.
- Iterate using screenshots and specific corrections.
- Use deliberate transitions between screens and test on the target device.
- Keep reusable workflow instructions with the project.

## How we apply them to this game
1. Before a feature, specify the player experience, acceptance checks and owner. Preserve server-authoritative combat and the approved rules.
2. Zain develops gameplay; Abi develops presentation. Agree on element IDs and API fields before touching shared files. Independent asset work can proceed alongside logic when coordinated.
3. For animated fighters, approve one character first: consistent scale, transparent background, fixed frame size, ground anchor and idle/attack/hit/knockout states. Reuse existing art as the reference. Validate before expanding to ten characters.
4. Check the actual browser at desktop and narrow widths. Compare approved references side by side; check character visibility, command placement, contrast and readable effect feedback.
5. Coordinate short screen fades with Abi; respect reduced motion. Animations display resolved outcomes and never determine damage or unlock inputs early.
6. Finish one complete playable flow before expanding: homepage, default team, battle, replacement, win/loss and replay. Test touch and keyboard controls, failed requests and missing assets.
7. Record screenshot evidence, relevant tests, asset provenance and unresolved limitations in the PR. Playtest clarity and balance with people.

## Decisions kept separate
The current implementation stays Python/FastAPI plus browser JavaScript. Godot migration, SpriteCook installation/account use, paid asset generation and new mechanics require a separate decision. The video is inspiration, not permission to change stack, overwrite Abi’s work or add every demonstrated feature.

Future gameplay and presentation PRs should consult this checklist. Persistent status badges and homepage integration remain the current priority.
