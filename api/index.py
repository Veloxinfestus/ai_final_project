from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List

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
  <title>Study Planner Party</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #140f2b;
      --card: rgba(33, 25, 66, 0.84);
      --border: rgba(170, 123, 255, 0.45);
      --text: #f8efff;
      --muted: #ccb8e9;
      --accent: #6cf8d7;
      --accent2: #ffd166;
      --danger: #ff7e7e;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Trebuchet MS", "Comic Sans MS", Inter, system-ui, Arial, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at 12% 10%, rgba(255, 94, 196, 0.35), transparent 30%),
        radial-gradient(circle at 88% 8%, rgba(108, 248, 215, 0.35), transparent 26%),
        radial-gradient(circle at 50% 100%, rgba(255, 209, 102, 0.18), transparent 30%),
        linear-gradient(155deg, #1a1238 0%, #140f2b 40%, #1e0e2f 100%);
      background-attachment: fixed;
    }
    .wrap { max-width: 1180px; margin: 0 auto; padding: 28px 20px 36px; }
    .hero {
      border: 2px dashed rgba(255, 209, 102, 0.75);
      border-radius: 20px;
      padding: 18px 20px;
      margin-bottom: 16px;
      background: rgba(17, 12, 40, 0.65);
      position: relative;
      overflow: hidden;
    }
    .hero::after {
      content: "✨   🪩   ✨   🧠   ✨   📚   ✨";
      position: absolute;
      right: 12px;
      top: 8px;
      font-size: 18px;
      opacity: 0.55;
    }
    h1 {
      margin: 0 0 6px;
      font-size: clamp(1.8rem, 2.6vw, 2.7rem);
      letter-spacing: 0.4px;
    }
    .subtitle { margin: 0; color: var(--muted); font-size: 0.98rem; }
    .layout { display: grid; gap: 16px; grid-template-columns: minmax(0, 1.22fr) minmax(0, 1fr); }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 16px;
      box-shadow: 0 10px 28px rgba(0, 0, 0, 0.25);
      backdrop-filter: blur(2px);
      position: relative;
      overflow: hidden;
    }
    .card::before {
      content: "";
      position: absolute;
      width: 190px;
      height: 190px;
      border-radius: 999px;
      background: radial-gradient(circle, rgba(255, 209, 102, 0.18), transparent 70%);
      right: -88px;
      top: -90px;
      pointer-events: none;
    }
    .section-title { margin: 0 0 8px; font-size: 1.06rem; }
    .muted { color: var(--muted); font-size: 0.9rem; }
    .field { display: flex; flex-direction: column; gap: 6px; }
    .field label { font-size: 0.85rem; color: #f0dcff; }
    .inputs-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
    input, select {
      width: 100%;
      border: 1px solid rgba(229, 203, 255, 0.45);
      border-radius: 11px;
      background: rgba(15, 10, 37, 0.78);
      color: #f8f1ff;
      padding: 9px 10px;
      font-size: 13px;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    input:focus, select:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(108, 248, 215, 0.25);
    }
    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin: 10px 0 8px;
      gap: 8px;
      flex-wrap: wrap;
    }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 8px; border-bottom: 1px solid rgba(205, 173, 247, 0.25); font-size: 13px; }
    th { color: #f6de93; text-align: left; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .actions { margin-top: 12px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
    button {
      border: 0;
      border-radius: 11px;
      padding: 10px 13px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      color: #22152d;
      background: linear-gradient(135deg, #6cf8d7, #7efde2);
    }
    button:hover { filter: brightness(1.07); transform: translateY(-1px); }
    button:disabled { opacity: 0.65; cursor: not-allowed; transform: none; }
    button.secondary {
      background: linear-gradient(135deg, #ffd166, #ffb703);
      color: #3b2400;
    }
    button.ghost {
      background: rgba(240, 216, 255, 0.13);
      color: #f4e8ff;
      border: 1px solid rgba(240, 216, 255, 0.38);
    }
    .status-pill {
      margin-left: auto;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(108, 248, 215, 0.16);
      border: 1px solid rgba(108, 248, 215, 0.55);
      color: var(--accent);
      font-size: 12px;
    }
    .chaos-switch {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px dashed rgba(255, 209, 102, 0.6);
      background: rgba(255, 209, 102, 0.08);
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      color: #ffe7a7;
      margin-left: auto;
    }
    .chaos-switch input { width: auto; accent-color: #ff4dcc; }
    body.party-mode {
      animation: hueSpin 12s linear infinite;
    }
    body.party-mode .hero {
      animation: wiggle 1.4s ease-in-out infinite;
    }
    body.party-mode .card:nth-child(odd) {
      animation: bobble 2.6s ease-in-out infinite;
    }
    body.party-mode .card:nth-child(even) {
      animation: bobble 2.6s ease-in-out infinite 0.7s;
    }
    @keyframes hueSpin {
      0% { filter: hue-rotate(0deg); }
      100% { filter: hue-rotate(360deg); }
    }
    @keyframes wiggle {
      0%, 100% { transform: rotate(0deg); }
      50% { transform: rotate(0.6deg); }
    }
    @keyframes bobble {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-2px); }
    }
    .result-meta { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin: 10px 0 12px; }
    .metric {
      background: rgba(14, 9, 33, 0.65);
      border: 1px solid rgba(255, 209, 102, 0.35);
      border-radius: 12px;
      padding: 10px;
    }
    .metric .k { font-size: 12px; color: #f3dca0; }
    .metric .v { font-size: 20px; font-weight: 800; }
    .day-block {
      border: 1px solid rgba(210, 183, 245, 0.3);
      border-radius: 12px;
      padding: 10px;
      margin-bottom: 8px;
      background: rgba(13, 8, 30, 0.58);
    }
    .day-title { font-size: 14px; margin-bottom: 6px; color: #f5e4ff; font-weight: 700; }
    .empty { color: var(--muted); font-size: 13px; font-style: italic; }
    .error { color: var(--danger); }
    @media (max-width: 980px) {
      .layout { grid-template-columns: 1fr; }
      .inputs-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
  </style>
</head>
<body>
  <main class="wrap">
    <header class="hero">
      <h1>Study Planner Party <span aria-hidden="true">🎉📚</span></h1>
      <p class="subtitle">Turn chaos into a game plan. Feed your tasks, press the magic button, and let this nerdy gremlin organize your week.</p>
    </header>
    <div class="layout">
      <section class="card">
        <h2 class="section-title">1) Set Up Your Week</h2>
        <p class="muted">Enter your available hours and tasks. Keep it real; sleepy brains need breaks.</p>
        <div class="field" style="max-width:240px; margin: 12px 0 10px;">
          <label for="weekOf">Week Starting On</label>
          <input id="weekOf" type="date" />
        </div>
        <h3 class="section-title">Daily Study Hours</h3>
        <div class="inputs-grid" id="hoursGrid"></div>
        <div class="toolbar">
          <h3 class="section-title" style="margin:0;">Tasks</h3>
          <button type="button" class="ghost" id="addTask">+ Add another mission</button>
        </div>
        <table>
          <thead>
            <tr><th>Task Name</th><th>Due Date</th><th>Hours Needed</th><th></th></tr>
          </thead>
          <tbody id="taskRows"></tbody>
        </table>
        <div class="actions">
          <button type="button" id="run">Generate My Battle Plan</button>
          <button type="button" class="secondary" id="reset">Reset to Sample Data</button>
          <label class="chaos-switch">
            <input type="checkbox" id="partyMode" />
            Maximum chaos mode
          </label>
          <span class="status-pill" id="status">Ready to plan</span>
        </div>
      </section>
      <section class="card">
        <h2 class="section-title">2) Your Recommended Schedule</h2>
        <p class="muted">The planner prioritizes urgent work while trying to fit your weekly hour budget.</p>
        <div class="result-meta">
          <div class="metric"><div class="k">Week</div><div class="v" id="mWeek">-</div></div>
          <div class="metric"><div class="k">Task Slots</div><div class="v" id="mSlots">0</div></div>
          <div class="metric"><div class="k">Unallocated Hours</div><div class="v" id="mUnalloc">0.0</div></div>
        </div>
        <div id="planOutput" class="empty">Generate a plan and your colorful schedule appears here.</div>
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
    const partyMode = document.getElementById("partyMode");
    const successLines = [
      "Plan generated. Time to academically speedrun.",
      "Battle plan ready. Your deadlines are trembling.",
      "Math completed. Brain activated. Let's go.",
      "Schedule locked in. You are now 14% more wizard."
    ];
    const busyLines = [
      "Crunching numbers...",
      "Bribing the calendar goblins...",
      "Negotiating peace between tasks and free time...",
      "Summoning the productivity dragon..."
    ];
    const dayVibes = {
      Monday: " Monday mission mode",
      Tuesday: " Tuesday turbo",
      Wednesday: " Midweek mayhem",
      Thursday: " Thursday thunder",
      Friday: " Friday finish-line energy",
      Saturday: " Weekend grind (with snacks)",
      Sunday: " Sunday reset vibes",
    };
    const randomFrom = (list) => list[Math.floor(Math.random() * list.length)];

    function setStatus(text, isError = false) {
      status.textContent = text;
      status.classList.toggle("error", isError);
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
        <td><input type="text" placeholder="Example: Chemistry quiz prep" value="${task.name ?? ""}" /></td>
        <td><input type="date" value="${task.due ?? ""}" /></td>
        <td><input type="number" min="0.5" step="0.5" value="${task.hours_needed ?? 1}" /></td>
        <td><button type="button" class="ghost removeBtn">Delete</button></td>
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
      setStatus("Ready to plan");
      planOutput.innerHTML = '<div class="empty">Generate a plan and your colorful schedule appears here.</div>';
      document.getElementById("mWeek").textContent = "-";
      document.getElementById("mSlots").textContent = "0";
      document.getElementById("mUnalloc").textContent = "0.0";
      partyMode.checked = false;
      document.body.classList.remove("party-mode");
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
            : '<div class="empty">No study scheduled. Recharge your brain.</div>';
          return `<div class="day-block"><div class="day-title">${dayVibes[day] || day}</div>${tasksHtml}</div>`;
        })
        .join("");

      const unallocItems = Object.entries(unallocated)
        .map(([task, hours]) => `<div>${task}: <strong>${Number(hours).toFixed(1)}h</strong></div>`)
        .join("");

      planOutput.innerHTML = `
        ${daysHtml}
        <div class="day-block">
          <div class="day-title">Unallocated Hours</div>
          ${unallocItems || '<div class="empty">Everything fit. You are unstoppable.</div>'}
        </div>
      `;
    }

    async function runPlan() {
      setStatus(randomFrom(busyLines));
      runBtn.disabled = true;
      try {
        const payload = collectPayload();
        if (!payload.tasks.length) {
          throw new Error("Add at least one task with hours so I have something to plan.");
        }
        const res = await fetch("/api/plan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data?.error || "Request failed.");
        renderPlan(data);
        setStatus(randomFrom(successLines));
      } catch (err) {
        setStatus("Please fix inputs and try again.", true);
        planOutput.innerHTML = `<div class="empty error">${String(err)}</div>`;
      } finally {
        runBtn.disabled = false;
      }
    }

    addTaskBtn.addEventListener("click", () => makeTaskRow());
    resetBtn.addEventListener("click", loadDefaults);
    partyMode.addEventListener("change", () => {
      document.body.classList.toggle("party-mode", partyMode.checked);
      if (partyMode.checked) {
        setStatus("Chaos mode: ON. Hold onto your flashcards.");
      } else {
        setStatus("Chaos mode: OFF. Back to normal silliness.");
      }
    });
    runBtn.addEventListener("click", runPlan);
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


def _bad_request(message: str):
    return jsonify({"error": message}), 400


def _parse_plan_payload(payload: Dict[str, Any]) -> tuple[List[Task], Dict[str, float], date | None]:
    week_of_raw = payload.get("week_of")
    week_of = date.fromisoformat(week_of_raw) if week_of_raw else None

    daily_hours_raw = payload.get("daily_study_hours")
    if not isinstance(daily_hours_raw, dict):
        raise ValueError("'daily_study_hours' must be an object keyed by weekday.")

    tasks_payload = payload.get("tasks")
    if not isinstance(tasks_payload, list) or not tasks_payload:
        raise ValueError("'tasks' must be a non-empty list.")

    tasks: List[Task] = []
    for item in tasks_payload:
        if not isinstance(item, dict):
            raise ValueError("Each task must be an object.")
        name = item.get("name")
        hours_needed = item.get("hours_needed")
        if name is None or hours_needed is None:
            raise ValueError("Each task must include 'name' and 'hours_needed'.")
        tasks.append(
            Task(
                name=str(name),
                hours_needed=float(hours_needed),
                due=date.fromisoformat(item["due"]) if item.get("due") else None,
            )
        )

    return tasks, daily_hours_raw, week_of


@app.post("/api/plan")
def plan():
    payload = request.get_json(silent=True) or {}
    try:
        tasks, daily_hours, week_of = _parse_plan_payload(payload)
        result = build_plan(tasks=tasks, daily_hours=daily_hours, week_of=week_of)
    except (ValueError, TypeError) as exc:
        return _bad_request(str(exc))

    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)
