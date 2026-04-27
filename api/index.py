from __future__ import annotations

import json
from datetime import date

from flask import Flask, jsonify, render_template_string, request

from study_planner import Task, build_plan

app = Flask(__name__)

DEFAULT_PAYLOAD = {
    "week_of": "2026-04-20",
    "daily_study_hours": {
        "Monday": 2,
        "Tuesday": 2,
        "Wednesday": 1.5,
        "Thursday": 2,
        "Friday": 1,
        "Saturday": 4,
        "Sunday": 4,
    },
    "tasks": [
        {"name": "Biology lab report", "due": "2026-04-23", "hours_needed": 5},
        {"name": "Statistics problem set", "due": "2026-04-25", "hours_needed": 4},
        {"name": "History reading quiz", "due": "2026-04-27", "hours_needed": 2},
        {"name": "Physics midterm", "due": "2026-05-02", "hours_needed": 12},
    ],
}


@app.get("/")
def home():
    return render_template_string(
        """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Study Planner</title>
  <style>
    :root { color-scheme: dark; }
    body {
      margin: 0; font-family: Inter, system-ui, Arial, sans-serif;
      background: #0b0f14; color: #e8edf2;
    }
    .wrap { max-width: 1000px; margin: 0 auto; padding: 24px; }
    .card {
      background: #111923; border: 1px solid #233044; border-radius: 12px; padding: 16px;
      box-shadow: 0 6px 24px rgba(0,0,0,.25);
    }
    h1 { margin: 0 0 12px; font-size: 28px; }
    p { margin: 0 0 12px; color: #b8c4d3; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    textarea, pre {
      width: 100%; min-height: 420px; box-sizing: border-box; border-radius: 10px;
      border: 1px solid #2a3a53; background: #0a111a; color: #d4e0ef; padding: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px;
    }
    .actions { margin: 12px 0 16px; display: flex; gap: 10px; align-items: center; }
    button {
      border: 0; border-radius: 10px; background: #25c284; color: #052113; font-weight: 700;
      padding: 10px 14px; cursor: pointer;
    }
    button:hover { filter: brightness(1.08); }
    .status { color: #7ee6b7; font-size: 14px; }
    @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <main class="wrap">
    <h1>Study Planner</h1>
    <p>Edit input JSON, then click Generate Plan.</p>
    <div class="card">
      <div class="actions">
        <button id="run">Generate Plan</button>
        <span class="status" id="status">Ready</span>
      </div>
      <div class="grid">
        <div>
          <p><strong>Input</strong> (POST payload for <code>/api/plan</code>)</p>
          <textarea id="input"></textarea>
        </div>
        <div>
          <p><strong>Output</strong> (generated schedule)</p>
          <pre id="output">{}</pre>
        </div>
      </div>
    </div>
  </main>
  <script>
    const starter = {{ starter | safe }};
    const input = document.getElementById("input");
    const output = document.getElementById("output");
    const status = document.getElementById("status");
    const runBtn = document.getElementById("run");
    input.value = JSON.stringify(starter, null, 2);

    async function runPlan() {
      status.textContent = "Working...";
      runBtn.disabled = true;
      try {
        const payload = JSON.parse(input.value);
        const res = await fetch("/api/plan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        output.textContent = JSON.stringify(data, null, 2);
        status.textContent = res.ok ? "Done" : "Request failed";
      } catch (err) {
        status.textContent = "Invalid input or server error";
        output.textContent = String(err);
      } finally {
        runBtn.disabled = false;
      }
    }
    runBtn.addEventListener("click", runPlan);
  </script>
</body>
</html>
        """,
        starter=json.dumps(DEFAULT_PAYLOAD),
    )


@app.get("/api/health")
def health():
    return jsonify({"status": "healthy"})


@app.post("/api/plan")
def plan():
    payload = request.get_json(silent=True) or {}
    week_of_raw = payload.get("week_of")
    week_of = date.fromisoformat(week_of_raw) if week_of_raw else None
    daily_hours = payload.get("daily_study_hours", {})
    tasks_payload = payload.get("tasks", [])

    tasks = [
        Task(
            name=item["name"],
            hours_needed=float(item["hours_needed"]),
            due=date.fromisoformat(item["due"]) if item.get("due") else None,
        )
        for item in tasks_payload
    ]

    result = build_plan(tasks=tasks, daily_hours=daily_hours, week_of=week_of)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
