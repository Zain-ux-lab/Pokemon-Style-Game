# Arena artwork integration

All eight original opaque PNGs from issue #20's version-4 package are installed
unchanged in frontend/assets/arenas. Exact generation prompts are included.

The server picks an arena for each new battle, excluding that browser session's
previous arena. The chosen id/name/image are returned in every snapshot and frame.
Refresh and recovery preserve the selection; artwork has no combat effects.
Expired sessions and server restarts lose history, just as they lose battles.

The frontend uses cover sizing within the existing battlefield and displays the
arena name. Existing near-player/far-opponent positions are preserved. The review
gallery's nearly equal fighter depth was not adopted because the game uses the
user's previously approved perspective. Fine-tuning composition is future UI work.

Source: https://github.com/Zain-ux-lab/Pokemon-Style-Game/issues/20
Package: https://github.com/user-attachments/files/33037553/arena-art-cel-shaded-review-v4.zip
