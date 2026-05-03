# Study Planner — AI Final Project

## Live application

**Public URL:** [https://aifinal-phi.vercel.app](https://aifinal-phi.vercel.app)

Open the link in a browser to use the scheduler—no command line or local install required for the deployed build.

**Source repository:** [github.com/Veloxinfestus/ai_final_project](https://github.com/Veloxinfestus/ai_final_project)

## Project purpose

This project is a Python web application that supports **student success** and **faculty-advising workflows** by turning coursework, due dates, daily availability, and priorities into a **weekly study schedule**.

The planner treats scheduling as a **constrained optimization** problem: it greedily allocates half-hour blocks to maximize an explicit **objective function** that rewards on-time, priority-weighted completion while penalizing late allocation—similar in spirit to heuristic search / iterative improvement used in operations research and ML-inspired scheduling, without requiring an external model runtime.

## Repository layout

| Path | Role |
|------|------|
| `study_planner.py` | Core scheduling, validation, and objective evaluation. |
| `api/index.py` | Flask API and browser UI (same deployment unit for Vercel). |
| `tests/test_study_planner.py` | Unit tests for planner behavior and objective semantics. |
| `tests/test_api.py` | HTTP contract tests (health, success paths, validation errors). |
| `vercel.json` | Serverless routing for production deployment. |
| `ROBOTS.md` | Machine-readable project map for AI-assisted tooling. |
| `requirements.txt` | Python dependencies. |

## Local development

1. Install **Python 3.11+**.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `python api/index.py`
4. Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) (UI) and [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health)

## Testing and reliability

Automated tests validate planner logic and the HTTP API (including error responses). **Continuous integration** runs the same suite on every push and pull request to `main` (see `.github/workflows/ci.yml`).

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

All AI-assisted or generated code in this repo was **reviewed by the authors**, exercised by the test suite, and smoke-tested on the live deployment before submission.

## API endpoints

- `GET /api/health` — health check.
- `POST /api/plan` — generate a plan from tasks and daily hours. Invalid input returns **HTTP 400** with an `error` message in JSON.

### Example request

```json
{
  "week_of": "2026-04-20",
  "daily_study_hours": {
    "Monday": 2,
    "Tuesday": 2,
    "Wednesday": 1.5,
    "Thursday": 2,
    "Friday": 1,
    "Saturday": 4,
    "Sunday": 4
  },
  "tasks": [
    { "name": "Biology lab report", "due": "2026-04-23", "hours_needed": 5 },
    { "name": "Statistics problem set", "due": "2026-04-25", "hours_needed": 4 }
  ]
}
```

### Example response

```json
{
  "week_of": "2026-04-20",
  "plan": {
    "Monday": { "Biology lab report": 2.0 }
  },
  "unallocated_hours": {},
  "metrics": {
    "total_requested_hours": 9.0,
    "total_available_hours": 16.5,
    "total_allocated_hours": 9.0,
    "allocation_rate": 1.0
  }
}
```

## Deploy to Vercel

1. Push this repo to GitHub.
2. Import the repo in Vercel as framework **Other**.
3. Deploy using the existing `vercel.json`.

## Acknowledgments and AI-assisted development

Tools such as **GitHub Copilot**, **Cursor**, and/or **ChatGPT** may have been used for scaffolding, refactoring, UI copy, or test cases—replace this sentence with the tools **you** actually used.

Per course policy: **list specific tools and how they were used**, and confirm that all suggestions were **human-reviewed**, **run against the test suite**, and **verified** in the running application. Generated code is not treated as authoritative without that review.

## Agent / automation notes

For AI coding agents and automation, see **`ROBOTS.md`** for repository structure, boundaries, and contribution expectations.
