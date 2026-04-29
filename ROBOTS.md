# ROBOTS.md

This file defines how AI agents should contribute to the Study Planner final project.

## Project Goal
Build and maintain a professional Python study-planning web application that solves a useful student-success optimization task.

## Source of Truth Structure
- `study_planner.py`: core scheduling and optimization logic.
- `api/index.py`: Flask endpoints and minimal frontend UI.
- `tests/`: automated test suite for logic and API behavior.
- `README.md`: setup and usage docs for humans.
- `ROBOTS.md`: implementation guidance for AI agents.

## Agent Contribution Rules
1. Preserve the app scope: this remains a **study planner**.
2. Prioritize correctness, input validation, and deterministic behavior.
3. Add or update tests whenever planner or API behavior changes.
4. Keep interfaces backward-compatible unless a human asks for a breaking change.
5. Prefer Python standard library and existing dependencies.
6. Keep code readable and modular; avoid giant functions.
7. Update `README.md` when behavior, API contract, or setup steps change.

## Testing Expectations
- Before finalizing changes, run:
  - `python -m unittest discover -s tests -p "test_*.py" -v`
- If tests fail, fix code or tests before handing work back.

## API Expectations
- `GET /api/health` must remain stable.
- `POST /api/plan` must validate payloads and return useful 400 messages for invalid input.
