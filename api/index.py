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
  <title>Study Planner // Rainbow Sparkle Mode</title>
  <style>
    :root { color-scheme: light; }
    body {
      margin: 0;
      font-family: "Comic Sans MS", "Trebuchet MS", "Segoe UI", sans-serif;
      min-height: 100vh;
      background:
        radial-gradient(circle at 12% 10%, rgba(255, 90, 196, 0.42), transparent 34%),
        radial-gradient(circle at 88% 16%, rgba(120, 248, 255, 0.4), transparent 30%),
        radial-gradient(circle at 78% 88%, rgba(171, 111, 255, 0.32), transparent 34%),
        linear-gradient(130deg, #ff9eea 0%, #ffd8a6 22%, #fff4a6 42%, #b8ffd1 61%, #b5e0ff 78%, #d7b8ff 100%);
      color: #45135f;
      letter-spacing: 0.2px;
      overflow-x: hidden;
    }
    body::before {
      content: "";
      position: fixed;
      inset: -100%;
      pointer-events: none;
      background:
        radial-gradient(circle, rgba(255, 255, 255, 0.92) 0 1px, transparent 2px),
        radial-gradient(circle, rgba(255, 255, 255, 0.78) 0 1px, transparent 2px);
      background-size: 120px 120px, 90px 90px;
      background-position: 0 0, 40px 30px;
      animation: sparkleFloat 12s linear infinite;
      z-index: -1;
      opacity: 0.6;
    }
    .wrap { max-width: 1160px; margin: 0 auto; padding: 24px; }
    .hero {
      margin-bottom: 16px;
      padding: 14px 16px;
      border-radius: 14px;
      border: 2px solid #ff57b4;
      background: linear-gradient(120deg, rgba(255, 255, 255, 0.66), rgba(255, 236, 250, 0.72));
      box-shadow: 0 10px 28px rgba(255, 86, 190, 0.28), inset 0 0 22px rgba(255, 255, 255, 0.55);
    }
    .card {
      background: linear-gradient(165deg, rgba(255, 255, 255, 0.7), rgba(255, 244, 251, 0.82));
      border: 2px solid #ff9dda;
      border-radius: 14px;
      padding: 16px;
      box-shadow: 0 10px 24px rgba(176, 67, 255, 0.16), 0 0 26px rgba(255, 255, 255, 0.34);
      backdrop-filter: blur(2px);
    }
    h1 {
      margin: 0 0 12px;
      font-size: 34px;
      text-transform: none;
      line-height: 1;
      color: #f4289a;
      text-shadow: 2px 2px 0 #fff4a8, 0 0 14px rgba(255, 255, 255, 0.88);
    }
    p { margin: 0 0 12px; color: #6d2282; font-weight: 600; }
    .layout { display: grid; grid-template-columns: 1.2fr 1fr; gap: 16px; }
    .section-title {
      margin: 0 0 10px;
      font-size: 16px;
      color: #d51d8c;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .inputs-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
    .field { display: flex; flex-direction: column; gap: 6px; }
    .field label { font-size: 13px; color: #8e1f8d; font-weight: 700; }
    input, select {
      width: 100%;
      box-sizing: border-box;
      border-radius: 10px;
      border: 2px solid #f8a9e5;
      background: rgba(255, 255, 255, 0.86);
      color: #5a1769;
      padding: 9px 10px; font-size: 13px;
      transition: border-color .15s ease, box-shadow .15s ease, transform .12s ease;
    }
    input:focus, select:focus {
      outline: none;
      border-color: #54d8ff;
      box-shadow: 0 0 0 3px rgba(255, 125, 198, 0.35), 0 0 12px rgba(84, 216, 255, 0.5);
      transform: translateY(-1px);
    }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 8px; border-bottom: 1px solid #ffc3e7; font-size: 13px; }
    th { color: #b02196; text-align: left; }
    .actions { margin: 12px 0 0; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    button {
      border: 2px solid #ff5ac1;
      border-radius: 10px;
      background: linear-gradient(115deg, #ff87d8, #ffd375, #b5ff91, #8ce4ff, #d7a6ff);
      color: #5b1d6d;
      font-weight: 800;
      padding: 10px 14px; cursor: pointer;
      text-transform: uppercase;
      letter-spacing: .7px;
      box-shadow: 0 4px 14px rgba(255, 123, 203, 0.42);
    }
    button.secondary {
      background: linear-gradient(120deg, #fff3b2, #ffc6f0, #caeaff);
      border: 2px solid #f58bd7;
      color: #8a218b;
      box-shadow: 0 0 12px rgba(249, 137, 220, 0.28);
    }
    button:hover { filter: brightness(1.04) saturate(1.15); transform: translateY(-1px) scale(1.01); }
    button:disabled { opacity: .6; cursor: not-allowed; }
    .status {
      color: #922587;
      font-size: 14px;
      padding: 3px 8px;
      border-radius: 999px;
      border: 2px solid rgba(255, 111, 196, 0.6);
      background: rgba(255, 255, 255, 0.72);
      font-weight: 700;
    }
    .result-meta { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-bottom: 10px; }
    .metric {
      background: linear-gradient(145deg, rgba(255, 255, 255, 0.72), rgba(255, 239, 250, 0.8));
      border: 2px solid #f6a0dc;
      border-radius: 12px;
      padding: 10px;
    }
    .metric .k { color: #c1269d; font-size: 12px; margin-bottom: 4px; text-transform: uppercase; }
    .metric .v { font-size: 18px; font-weight: 700; color: #5f1e86; }
    .day-block {
      border: 2px solid #f1abe2;
      border-radius: 12px;
      padding: 10px;
      margin-bottom: 8px;
      background: linear-gradient(170deg, rgba(255, 255, 255, 0.76), rgba(255, 241, 249, 0.84));
      box-shadow: inset 0 0 12px rgba(255, 149, 214, 0.18);
    }
    .day-title { font-size: 14px; margin-bottom: 6px; color: #a52395; letter-spacing: .4px; font-weight: 700; }
    .muted { color: #9447ab; font-size: 12px; }
    .sparkle-title {
      position: relative;
      display: inline-block;
    }
    .sparkle-title::before,
    .sparkle-title::after {
      content: "✨";
      position: absolute;
      pointer-events: none;
      font-size: 20px;
      animation: twinkle 2.2s ease-in-out infinite;
    }
    .sparkle-title::before {
      left: -24px;
      top: 2px;
    }
    .sparkle-title::after {
      right: -24px;
      top: 2px;
      animation-delay: .7s;
    }
    .cheer-tag {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
      padding: 6px 10px;
      font-size: 11px;
      letter-spacing: 1px;
      border-radius: 999px;
      text-transform: uppercase;
      color: #7a176f;
      background: linear-gradient(120deg, #ffcbf0, #fff5bf, #beecff);
      box-shadow: 0 0 18px rgba(255, 159, 222, 0.55);
      font-weight: 800;
    }
    @keyframes sparkleFloat {
      from { transform: translateY(0); }
      to { transform: translateY(40px); }
    }
    @keyframes twinkle {
      0%, 100% { opacity: 0.45; transform: scale(0.95) rotate(0deg); }
      50% { opacity: 1; transform: scale(1.2) rotate(20deg); }
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
      <div class="cheer-tag">rainbow mode // max sparkle</div>
      <h1 class="sparkle-title">Study Planner</h1>
      <p>You are doing amazing. Add your week and tasks, and this planner will build a cheerful game plan for you.</p>
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
          <span class="status" id="status">Ready to sparkle</span>
        </div>
      </div>
      </section>
      <section class="card">
        <h2 class="section-title">Recommended Schedule</h2>
        <div class="result-meta">
          <div class="metric"><div class="k">Week</div><div class="v" id="mWeek">-</div></div>
          <div class="metric"><div class="k">Task Slots</div><div class="v" id="mSlots">0</div></div>
          <div class="metric"><div class="k">Unallocated Hours</div><div class="v" id="mUnalloc">0.0</div></div>
        </div>
        <div id="planOutput" class="muted">Tap Make My Plan to see your personalized schedule.</div>
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
      status.textContent = "Ready to sparkle";
      planOutput.innerHTML = '<div class="muted">Tap Make My Plan to see your personalized schedule.</div>';
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

      planOutput.innerHTML = `
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
