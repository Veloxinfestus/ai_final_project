# Study Planner - AI Final Project

## Project Purpose
This project is a Python web app that helps student success by generating a weekly study schedule from tasks, due dates, and daily availability.  
It frames planning as an optimization problem: maximize on-time completion for urgent tasks while respecting a fixed weekly hour budget.

## Repository Layout
- `study_planner.py`: core scheduling and optimization logic.
- `api/index.py`: Flask API and lightweight browser UI.
- `tests/test_study_planner.py`: unit tests for planner behavior.
- `tests/test_api.py`: endpoint and payload-validation tests.
- `vercel.json`: Vercel routing for serverless deployment.
- `requirements.txt`: Python dependencies.

## Local Development
1. Install Python 3.11+.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run the app:
   - `python api/index.py`
4. Open:
   - `http://127.0.0.1:5000/` (UI)
   - `http://127.0.0.1:5000/api/health`

## Test Commands
- Run all tests:
  - `python -m unittest discover -s tests -p "test_*.py" -v`

## API Endpoints
- `GET /api/health`: health check.
- `POST /api/plan`: generate a plan from tasks and daily hours.

### Example Request
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

### Example Response
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

## Deploy To Vercel
1. Push this repo to GitHub.
2. Import the repo in Vercel as framework **Other**.
3. Deploy using existing `vercel.json`.
