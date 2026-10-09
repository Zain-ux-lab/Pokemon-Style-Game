# Working on Clashbound

## Branching
- `main` is always deployable/demoable. Never commit directly to it.
- Branch per issue: `feature/<short-name>` or `fix/<short-name>`,
  e.g. `feature/turn-engine`, `fix/websocket-disconnect`.
- Open a Pull Request into `main` when ready. At least 1 teammate
  reviews/approves before merging.

## Issues
- Every piece of work is a GitHub Issue, assigned to one person,
  attached to a Milestone (Phase 1-4).
- Reference the issue number in your PR (e.g. "Closes #12").

## Commits
- Small, frequent commits with clear messages beat one giant commit.
- Prefix with area when useful: `engine: add damage calculation`,
  `frontend: wire up move buttons`.

## Code ownership (subject to change as we go)
- Battle Engine (backend/engine/): Zain
- Backend/API/DB (backend/api/, backend/models/, backend/services/): Backend teammate
- Frontend (frontend/): Frontend teammate, UX direction from Zain

Cross-cutting changes (e.g. engine output format changing what the API
returns) should be flagged in the PR description so the other owner can review.
