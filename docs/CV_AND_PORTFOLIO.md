# Clashbound — CV and interview pack

## CV entry — ready to copy

**Clashbound | Turn-based browser game | Python, FastAPI, JavaScript, HTML/CSS, GitHub**

- Co-developed a single-player battle game with a teammate, featuring ten characters, configurable four-move builds, type matchups and status effects.
- Focused on gameplay and backend integration: a shared combat engine for API resolution and deterministic tactical bot simulation, with validated actions and isolated battle sessions.
- Evaluated bot decisions using seeded teams and paired starting positions; added matchup-aware scoring and regression coverage for early beneficial switching.

Repository: https://github.com/Zain-ux-lab/Clashbound

Use the repository link now. Add a verified public demo link after deployment;
do not describe the project as deployed until that link works. These bullets
reflect the project's agreed ownership, not a claim that one person wrote every
component independently. Adjust any wording that exceeds what you can explain.

## Short project introduction

Clashbound is a two-person project I built to explore turn-based combat and game
AI. Players select three characters and customise their moves before facing a
bot. I focused on gameplay and backend integration, while my teammate focused
on the interface and presentation. The bot simulates legal actions using the
same engine as the game, then searches its move and an opponent reply. We used
AI coding assistance, pull-request reviews, automated tests and human playtests
to develop and validate the project.

## Engineering evidence

| Claim | Evidence |
|---|---|
| Shared rules for gameplay and AI | `backend/engine/`, `backend/bot/adapter.py` |
| Tactical search rather than random moves | `backend/bot/search.py` |
| Action validation and session consistency | `backend/api/routes.py`, API regression tests |
| Reproducible evaluation | `backend/bot/evaluation.py`, `docs/evaluation/` |
| Collaboration and independent validation | Merged PRs #24, #25 and #26, including Abi's review |
| Readable action sequencing | Pacing fix: HP numbers last 1.8 seconds and a 0.7-second inter-frame pause |

The current local verification is 80 Python tests and eight client tests. Test
counts are a dated snapshot, not a permanent guarantee. One existing
Starlette/httpx deprecation warning remains. Client tests use a minimal DOM;
they do not replace full browser testing.

## Interview questions to practise

**How does the bot decide?**
It enumerates legal moves and switches, simulates its action and the opponent's
reply, assumes the opponent chooses the worst reply for it, and scores the
result using surviving characters, HP fractions, statuses and active matchups.
Knockout replacement is free, so it does not consume a normal search action.
It is a deterministic search bot, not a trained machine-learning model.

**Why share the engine with the bot?**
A separate AI damage formula could disagree with the real game. Using the same
resolution functions keeps statuses, switching and damage rules consistent.
Simulation copies the state so evaluating candidates does not alter the live
battle. The tradeoff is copying and simulation cost.

**What bug or weakness did you investigate?**
Late switching was visible in playtests. The old score heavily valued keeping
any character alive, including a reserve on very low HP. Matchup-aware scoring
and a reduced living-character bonus improved damage-only results modestly,
but slightly reduced random-opponent results. We kept that tradeoff visible
instead of reporting only the best number.

**Is deeper search always better?**
No. A temporary four-action/pruned-search experiment won 14/24 direct matches
against the current bot, but had mixed baseline results and roughly five times
the local median decision time. It was not adopted into the game. Search depth,
scoring quality and response time all matter.

**How did you use AI?**
AI assisted implementation, debugging and test writing. We reviewed changes,
reproduced evaluations and played the game. Be ready to explain the code and
which decisions you personally made; do not describe assisted work as wholly
unaided implementation.

**What would you improve next?**
Use specific human-playtest positions to improve decisions, consider bounded
deeper search, and test the deployed demo. Persistent matches would require
storage beyond the current in-memory server state.

## Demo walkthrough — about two minutes

1. Show the homepage and pick three characters.
2. Show one optional move-build choice and enter combat.
3. Explain a type matchup, make a move and point out the HP change.
4. Demonstrate a turn-consuming switch; explain free knockout replacement.
5. Open the stats/type guide and finish with the engine/bot code map and evaluation report.

## Development after deployment

Keep developing locally on feature branches. Run tests, open a PR, have the
teammate review it, and merge into the deployed branch. Render can then deploy
the updated version automatically when connected to that Git branch, or through
a manual deploy. Local edits alone do not update the public game.

See https://render.com/docs/deploys for current deployment behaviour. Clashbound
matches are stored in server memory: restarting or redeploying clears active
matches. Use one worker with the current storage design.

## Boundaries of the project

Do not claim online multiplayer, persistent accounts/saves, a shipped database,
trained AI, human-level strength, or production scale. Do not describe the
temporary deeper-search experiment as part of the deployed/default bot.
