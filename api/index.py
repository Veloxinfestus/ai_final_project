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
    :root {
      --bg-main: #f2f5fb;
      --bg-grad-a: #eaf0ff;
      --bg-grad-b: #f5efff;
      --text-main: #1d2433;
      --text-muted: #57617a;
      --card-bg: rgba(255, 255, 255, 0.86);
      --card-border: #d9e2f3;
      --input-bg: #ffffff;
      --input-border: #c8d5ef;
      --accent: #5b6cff;
      --accent-strong: #4053f3;
      --accent-soft: #ecf0ff;
      --shadow: 0 12px 36px rgba(46, 63, 105, 0.12);
      color-scheme: light;
    }
    [data-theme="midnight"] {
      --bg-main: #0f1420;
      --bg-grad-a: #111a2a;
      --bg-grad-b: #172238;
      --text-main: #e8edf8;
      --text-muted: #aab5cf;
      --card-bg: rgba(20, 28, 42, 0.88);
      --card-border: #2d3a56;
      --input-bg: rgba(11, 18, 32, 0.9);
      --input-border: #334562;
      --accent: #7c8dff;
      --accent-strong: #98a4ff;
      --accent-soft: rgba(124, 141, 255, 0.14);
      --shadow: 0 14px 34px rgba(3, 8, 18, 0.55);
      color-scheme: dark;
    }
    [data-theme="sunset"] {
      --bg-main: #fff2ec;
      --bg-grad-a: #ffe4d8;
      --bg-grad-b: #fff3d6;
      --text-main: #3a2436;
      --text-muted: #715565;
      --card-bg: rgba(255, 255, 255, 0.88);
      --card-border: #ffd2b9;
      --input-bg: #fffdfa;
      --input-border: #ffc8ad;
      --accent: #ff6b72;
      --accent-strong: #e95a63;
      --accent-soft: #ffe9e2;
      --shadow: 0 12px 30px rgba(184, 104, 104, 0.2);
      color-scheme: light;
    }
    [data-theme="rainbow"] {
      --bg-main: #ffeefe;
      --bg-grad-a: #ffdff3;
      --bg-grad-b: #dff3ff;
      --text-main: #5f1e86;
      --text-muted: #9447ab;
      --card-bg: rgba(255, 255, 255, 0.78);
      --card-border: #f6a0dc;
      --input-bg: rgba(255, 255, 255, 0.9);
      --input-border: #f8a9e5;
      --accent: #ff5ac1;
      --accent-strong: #d4419f;
      --accent-soft: #fff2fb;
      --shadow: 0 14px 28px rgba(255, 123, 203, 0.32);
      color-scheme: light;
    }
    body {
      margin: 0;
      font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif;
      min-height: 100vh;
      background:
        radial-gradient(circle at 12% 10%, var(--bg-grad-a), transparent 38%),
        radial-gradient(circle at 85% 14%, var(--bg-grad-b), transparent 34%),
        var(--bg-main);
      color: var(--text-main);
      overflow-x: hidden;
      transition: background 0.25s ease, color 0.25s ease;
    }
    body::before {
      content: "";
      position: fixed;
      inset: -100%;
      pointer-events: none;
      background: repeating-linear-gradient(
        180deg,
        rgba(255, 255, 255, 0.03) 0 1px,
        transparent 1px 4px
      );
      animation: drift 18s linear infinite;
      z-index: -1;
      opacity: 0.28;
    }
    .wrap { max-width: 1180px; margin: 0 auto; padding: 24px; }
    .hero {
      margin-bottom: 16px;
      padding: 16px 18px;
      border-radius: 16px;
      border: 1px solid var(--card-border);
      background: var(--card-bg);
      box-shadow: var(--shadow);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 16px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(2px);
    }
    h1 {
      margin: 0 0 12px;
      font-size: 32px;
      text-transform: none;
      line-height: 1.05;
      color: var(--text-main);
    }
    p { margin: 0 0 12px; color: var(--text-muted); font-weight: 500; }
    .layout { display: grid; grid-template-columns: 1.2fr 1fr; gap: 16px; }
    .section-title {
      margin: 0 0 10px;
      font-size: 16px;
      color: var(--text-main);
      text-transform: uppercase;
      letter-spacing: 0.7px;
    }
    .inputs-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
    .field { display: flex; flex-direction: column; gap: 6px; }
    .field label { font-size: 13px; color: var(--text-muted); font-weight: 600; }
    input, select {
      width: 100%;
      box-sizing: border-box;
      border-radius: 10px;
      border: 1px solid var(--input-border);
      background: var(--input-bg);
      color: var(--text-main);
      padding: 9px 10px; font-size: 13px;
      transition: border-color .15s ease, box-shadow .15s ease, transform .12s ease;
    }
    input:focus, select:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 24%, transparent);
      transform: translateY(-1px);
    }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 8px; border-bottom: 1px solid var(--card-border); font-size: 13px; }
    th { color: var(--text-muted); text-align: left; }
    .actions { margin: 12px 0 0; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    button {
      border: 1px solid var(--accent);
      border-radius: 10px;
      background: var(--accent);
      color: #ffffff;
      font-weight: 800;
      padding: 10px 14px; cursor: pointer;
      text-transform: uppercase;
      letter-spacing: .7px;
      box-shadow: 0 6px 20px color-mix(in srgb, var(--accent) 32%, transparent);
    }
    button.secondary {
      background: var(--accent-soft);
      border: 1px solid var(--input-border);
      color: var(--text-main);
      box-shadow: none;
    }
    button:hover { filter: brightness(1.04) saturate(1.15); transform: translateY(-1px) scale(1.01); }
    button:disabled { opacity: .6; cursor: not-allowed; }
    .status {
      color: var(--text-main);
      font-size: 14px;
      padding: 3px 8px;
      border-radius: 999px;
      border: 1px solid var(--input-border);
      background: var(--input-bg);
      font-weight: 700;
    }
    .hero-copy { min-width: 280px; }
    .theme-switch {
      min-width: 220px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .theme-switch label {
      font-size: 13px;
      font-weight: 700;
      color: var(--text-muted);
    }
    .result-meta { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-bottom: 10px; }
    .metric {
      background: var(--input-bg);
      border: 1px solid var(--input-border);
      border-radius: 12px;
      padding: 10px;
    }
    .metric .k { color: var(--text-muted); font-size: 12px; margin-bottom: 4px; text-transform: uppercase; }
    .metric .v { font-size: 18px; font-weight: 700; color: var(--text-main); }
    .day-block {
      border: 1px solid var(--input-border);
      border-radius: 12px;
      padding: 10px;
      margin-bottom: 8px;
      background: var(--input-bg);
    }
    .day-title { font-size: 14px; margin-bottom: 6px; color: var(--text-main); letter-spacing: .4px; font-weight: 700; }
    .muted { color: var(--text-muted); font-size: 12px; }
    .schedule-summary {
      margin-bottom: 10px;
      padding: 10px;
      background: var(--accent-soft);
      border: 1px solid var(--input-border);
      border-radius: 12px;
      font-size: 13px;
      color: var(--text-main);
    }
    @keyframes drift {
      from { transform: translateY(0); }
      to { transform: translateY(24px); }
    }
    @media (max-width: 980px) {
      .layout { grid-template-columns: 1fr; }
      .inputs-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
  </style>
</head>
<body>
  <main class="wrap">
    <header class="hero">
      <div class="hero-copy">
        <h1>Study Planner</h1>
        <p>Build an optimized weekly schedule from your tasks, due dates, and available study hours.</p>
      </div>
      <div class="theme-switch">
        <label for="themeSelect">Theme</label>
        <select id="themeSelect">
          <option value="modern">Modern (Default)</option>
          <option value="midnight">Midnight</option>
          <option value="sunset">Sunset</option>
          <option value="rainbow">Rainbow Sparkle</option>
        </select>
      </div>
    </header>
    <div class="layout">
      <section class="card">
        <h2 class="section-title">Happy Inputs</h2>
        <div class="field" style="max-width:240px; margin-bottom: 10px;">
          <label for="weekOf">Week Of</label>
          <input id="weekOf" type="date" />
        </div>
        <h3 class="section-title">Daily Study Energy</h3>
        <div class="inputs-grid" id="hoursGrid"></div>
        <h3 class="section-title" style="margin-top:14px;">Your Tasks</h3>
        <table>
          <thead>
            <tr><th>Task</th><th>Due Date</th><th>Hours</th><th></th></tr>
          </thead>
          <tbody id="taskRows"></tbody>
        </table>
        <div class="actions">
          <button type="button" class="secondary" id="addTask">+ Add Task</button>
          <button type="button" id="run">Make My Plan</button>
          <button type="button" class="secondary" id="reset">Reset Defaults</button>
          <span class="status" id="status">Ready</span>
        </div>
      </div>
      </section>
      <section class="card">
        <h2 class="section-title">Final Optimized Schedule</h2>
        <div class="result-meta">
          <div class="metric"><div class="k">Week</div><div class="v" id="mWeek">-</div></div>
          <div class="metric"><div class="k">Task Slots</div><div class="v" id="mSlots">0</div></div>
          <div class="metric"><div class="k">Unallocated Hours</div><div class="v" id="mUnalloc">0.0</div></div>
        </div>
        <div id="planOutput" class="muted">Click Make My Plan to generate your optimized schedule.</div>
      </section>
    </div>
  </main>
  <script>
    const starter = {{ starter | safe }};
    const weekdays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
    const weekOf = document.getElementById("weekOf");
    const hoursGrid = document.getElementById("hoursGrid");
    const taskRows = document.getElementById("taskRows");
    const status = document.getElementById("status");
    const runBtn = document.getElementById("run");
    const addTaskBtn = document.getElementById("addTask");
    const resetBtn = document.getElementById("reset");
    const planOutput = document.getElementById("planOutput");
    const themeSelect = document.getElementById("themeSelect");
    const THEME_KEY = "studyPlannerTheme";

    function applyTheme(theme) {
      const selected = theme || "modern";
      if (selected === "modern") {
        document.documentElement.removeAttribute("data-theme");
      } else {
        document.documentElement.setAttribute("data-theme", selected);
      }
      themeSelect.value = selected;
      localStorage.setItem(THEME_KEY, selected);
    }

    function renderHours(hours) {
      hoursGrid.innerHTML = "";
      weekdays.forEach((day) => {
        const wrapper = document.createElement("div");
        wrapper.className = "field";
        wrapper.innerHTML = `
          <label for="h-${day}">${day}</label>
          <input id="h-${day}" type="number" min="0" step="0.5" value="${hours?.[day] ?? 0}" />
        `;
        hoursGrid.appendChild(wrapper);
      });
    }

    function makeTaskRow(task = {name: "", due: "", hours_needed: 1}) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><input type="text" placeholder="Task name" value="${task.name ?? ""}" /></td>
        <td><input type="date" value="${task.due ?? ""}" /></td>
        <td><input type="number" min="0.5" step="0.5" value="${task.hours_needed ?? 1}" /></td>
        <td><button type="button" class="secondary removeBtn">Remove</button></td>
      `;
      tr.querySelector(".removeBtn").addEventListener("click", () => tr.remove());
      taskRows.appendChild(tr);
    }

    function loadDefaults() {
      weekOf.value = starter.week_of || "";
      renderHours(starter.daily_study_hours || {});
      taskRows.innerHTML = "";
      (starter.tasks || []).forEach((task) => makeTaskRow(task));
      if (!taskRows.children.length) makeTaskRow();
      status.textContent = "Ready";
      planOutput.innerHTML = '<div class="muted">Click Make My Plan to generate your optimized schedule.</div>';
      document.getElementById("mWeek").textContent = "-";
      document.getElementById("mSlots").textContent = "0";
      document.getElementById("mUnalloc").textContent = "0.0";
    }

    function collectPayload() {
      const daily_study_hours = {};
      weekdays.forEach((day) => {
        const val = Number(document.getElementById(`h-${day}`).value || 0);
        daily_study_hours[day] = Number.isFinite(val) ? val : 0;
      });

      const tasks = Array.from(taskRows.querySelectorAll("tr"))
        .map((tr) => {
          const [nameInput, dueInput, hrsInput] = tr.querySelectorAll("input");
          return {
            name: (nameInput.value || "").trim(),
            due: dueInput.value || null,
            hours_needed: Number(hrsInput.value || 0),
          };
        })
        .filter((t) => t.name && t.hours_needed > 0);

      return {
        week_of: weekOf.value || null,
        daily_study_hours,
        tasks,
      };
    }

    function renderPlan(data) {
      const week = data.week_of || "-";
      const plan = data.plan || {};
      const unallocated = data.unallocated_hours || {};
      const metrics = data.metrics || {};
      const totalUnalloc = Object.values(unallocated).reduce((sum, v) => sum + Number(v || 0), 0);
      const slotCount = Object.values(plan).reduce((sum, dayMap) => sum + Object.keys(dayMap || {}).length, 0);

      document.getElementById("mWeek").textContent = week;
      document.getElementById("mSlots").textContent = String(slotCount);
      document.getElementById("mUnalloc").textContent = totalUnalloc.toFixed(1);

      const daysHtml = weekdays
        .map((day) => {
          const entries = Object.entries(plan[day] || {});
          const tasksHtml = entries.length
            ? entries.map(([task, hours]) => `<div>${task}: <strong>${Number(hours).toFixed(1)}h</strong></div>`).join("")
            : '<div class="muted">(rest day)</div>';
          return `<div class="day-block"><div class="day-title">${day}</div>${tasksHtml}</div>`;
        })
        .join("");

      const unallocItems = Object.entries(unallocated)
        .map(([task, hours]) => `<div>${task}: <strong>${Number(hours).toFixed(1)}h</strong></div>`)
        .join("");

      const allocationRate = Number(metrics.allocation_rate || 0) * 100;
      const allocated = Number(metrics.total_allocated_hours || 0);
      const requested = Number(metrics.total_requested_hours || 0);

      planOutput.innerHTML = `
        <div class="schedule-summary">
          <strong>Optimization Result:</strong>
          ${allocated.toFixed(1)}h allocated out of ${requested.toFixed(1)}h requested
          (${allocationRate.toFixed(0)}% allocation rate).
        </div>
        ${daysHtml}
        <div class="day-block">
          <div class="day-title">Unallocated Hours</div>
          ${unallocItems || '<div class="muted">Everything fits beautifully this week.</div>'}
        </div>
      `;
    }

    async function runPlan() {
      status.textContent = "Working magic...";
      runBtn.disabled = true;
      try {
        const payload = collectPayload();
        if (!payload.tasks.length) {
          throw new Error("Add at least one task with hours.");
        }
        const res = await fetch("/api/plan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error("Request failed.");
        renderPlan(data);
        status.textContent = res.ok ? "Plan complete - you got this!" : "Request failed";
      } catch (err) {
        status.textContent = "Please check inputs and try again";
        planOutput.innerHTML = `<div class="muted">${String(err)}</div>`;
      } finally {
        runBtn.disabled = false;
      }
    }

    addTaskBtn.addEventListener("click", () => makeTaskRow());
    resetBtn.addEventListener("click", loadDefaults);
    runBtn.addEventListener("click", runPlan);
    themeSelect.addEventListener("change", (e) => applyTheme(e.target.value));
    applyTheme(localStorage.getItem(THEME_KEY) || "modern");
    loadDefaults();
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
