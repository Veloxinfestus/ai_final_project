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
  <title>Study Planner // Ritual Mode</title>
  <style>
    :root { color-scheme: dark; }
    body {
      margin: 0;
      font-family: "JetBrains Mono", "Fira Code", Consolas, monospace;
      min-height: 100vh;
      background:
        radial-gradient(circle at 15% 25%, rgba(255, 0, 153, 0.2), transparent 40%),
        radial-gradient(circle at 90% 10%, rgba(0, 255, 255, 0.12), transparent 30%),
        radial-gradient(circle at 65% 80%, rgba(179, 0, 255, 0.2), transparent 35%),
        linear-gradient(125deg, #07040f 0%, #120b1f 48%, #080512 100%);
      color: #ecf6ff;
      letter-spacing: 0.2px;
      overflow-x: hidden;
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
    }
    .wrap { max-width: 1160px; margin: 0 auto; padding: 24px; }
    .hero {
      margin-bottom: 16px;
      padding: 14px 16px;
      border-radius: 14px;
      border: 1px solid #5d2d7d;
      background: linear-gradient(120deg, rgba(46, 7, 62, 0.8), rgba(9, 16, 43, 0.75));
      box-shadow: 0 0 24px rgba(160, 77, 255, 0.3), inset 0 0 22px rgba(39, 200, 255, 0.1);
    }
    .card {
      background: linear-gradient(160deg, rgba(16, 8, 31, 0.88), rgba(6, 18, 34, 0.87));
      border: 1px solid #364468;
      border-radius: 14px;
      padding: 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,.4), 0 0 30px rgba(136, 43, 211, 0.18);
      backdrop-filter: blur(2px);
    }
    h1 {
      margin: 0 0 12px;
      font-size: 34px;
      text-transform: uppercase;
      line-height: 1;
      color: #f8dbff;
      text-shadow: 1px 0 #00eeff, -1px 0 #ff147f, 0 0 18px rgba(191, 89, 255, 0.65);
    }
    p { margin: 0 0 12px; color: #d2c4ec; }
    .layout { display: grid; grid-template-columns: 1.2fr 1fr; gap: 16px; }
    .section-title {
      margin: 0 0 10px;
      font-size: 16px;
      color: #7df4ff;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .inputs-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
    .field { display: flex; flex-direction: column; gap: 6px; }
    .field label { font-size: 13px; color: #d8a2ff; }
    input, select {
      width: 100%;
      box-sizing: border-box;
      border-radius: 10px;
      border: 1px solid #4b3a6c;
      background: rgba(9, 13, 33, 0.82);
      color: #d6fcff;
      padding: 9px 10px; font-size: 13px;
      transition: border-color .15s ease, box-shadow .15s ease, transform .12s ease;
    }
    input:focus, select:focus {
      outline: none;
      border-color: #4ffbff;
      box-shadow: 0 0 0 2px rgba(120, 20, 255, 0.35), 0 0 12px rgba(79, 251, 255, 0.35);
      transform: translateY(-1px);
    }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 8px; border-bottom: 1px solid #2f3656; font-size: 13px; }
    th { color: #f3bdff; text-align: left; }
    .actions { margin: 12px 0 0; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    button {
      border: 1px solid #2d8fc0;
      border-radius: 10px;
      background: linear-gradient(120deg, #28ffe0, #8de2ff);
      color: #0b0f2c;
      font-weight: 800;
      padding: 10px 14px; cursor: pointer;
      text-transform: uppercase;
      letter-spacing: .7px;
      box-shadow: 0 0 14px rgba(52, 231, 255, 0.38);
    }
    button.secondary {
      background: linear-gradient(120deg, #481766, #2d2d7f);
      border: 1px solid #8453c0;
      color: #f1e9ff;
      box-shadow: 0 0 12px rgba(163, 74, 255, 0.24);
    }
    button:hover { filter: brightness(1.08) saturate(1.2); transform: translateY(-1px); }
    button:disabled { opacity: .6; cursor: not-allowed; }
    .status {
      color: #a6f8ff;
      font-size: 14px;
      padding: 3px 8px;
      border-radius: 999px;
      border: 1px solid rgba(92, 195, 255, 0.45);
      background: rgba(12, 30, 54, 0.55);
    }
    .result-meta { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-bottom: 10px; }
    .metric {
      background: linear-gradient(145deg, rgba(11, 14, 38, 0.88), rgba(25, 11, 44, 0.85));
      border: 1px solid #3f3763;
      border-radius: 12px;
      padding: 10px;
    }
    .metric .k { color: #f2a2f4; font-size: 12px; margin-bottom: 4px; text-transform: uppercase; }
    .metric .v { font-size: 18px; font-weight: 700; color: #a8feff; }
    .day-block {
      border: 1px solid #37426b;
      border-radius: 12px;
      padding: 10px;
      margin-bottom: 8px;
      background: linear-gradient(170deg, rgba(9, 14, 37, 0.9), rgba(14, 9, 30, 0.92));
      box-shadow: inset 0 0 12px rgba(197, 82, 255, 0.08);
    }
    .day-title { font-size: 14px; margin-bottom: 6px; color: #8cefff; letter-spacing: .5px; }
    .muted { color: #93a7cc; font-size: 12px; }
    .glitch {
      position: relative;
      display: inline-block;
      isolation: isolate;
    }
    .glitch::before,
    .glitch::after {
      content: attr(data-text);
      position: absolute;
      inset: 0;
      pointer-events: none;
      mix-blend-mode: screen;
    }
    .glitch::before {
      color: #00f0ff;
      transform: translate(1px, 0);
      clip-path: polygon(0 0, 100% 0, 100% 43%, 0 58%);
      opacity: .7;
      animation: buzzA 2.8s steps(1) infinite;
    }
    .glitch::after {
      color: #ff3aa8;
      transform: translate(-1px, 0);
      clip-path: polygon(0 55%, 100% 40%, 100% 100%, 0 100%);
      opacity: .7;
      animation: buzzB 2.2s steps(1) infinite;
    }
    .weird-tag {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
      padding: 6px 10px;
      font-size: 11px;
      letter-spacing: 1px;
      border-radius: 999px;
      text-transform: uppercase;
      color: #140a2a;
      background: linear-gradient(120deg, #ff7ad4, #87f3ff);
      box-shadow: 0 0 18px rgba(247, 121, 219, 0.4);
      font-weight: 800;
    }
    @keyframes drift {
      from { transform: translateY(0); }
      to { transform: translateY(24px); }
    }
    @keyframes buzzA {
      0%, 16%, 100% { transform: translate(1px, 0); }
      5% { transform: translate(-1px, -1px); }
      7% { transform: translate(2px, 1px); }
    }
    @keyframes buzzB {
      0%, 12%, 100% { transform: translate(-1px, 0); }
      4% { transform: translate(1px, 1px); }
      8% { transform: translate(-2px, -1px); }
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
      <div class="weird-tag">anomaly stable // 93%</div>
      <h1 class="glitch" data-text="Study Planner">Study Planner</h1>
      <p>Feed it your deadlines and available hours. It whispers back a schedule from the neon void.</p>
    </header>
    <div class="layout">
      <section class="card">
        <h2 class="section-title">Ritual Inputs</h2>
        <div class="field" style="max-width:240px; margin-bottom: 10px;">
          <label for="weekOf">Week Of</label>
          <input id="weekOf" type="date" />
        </div>
        <h3 class="section-title">Daily Energy Supply</h3>
        <div class="inputs-grid" id="hoursGrid"></div>
        <h3 class="section-title" style="margin-top:14px;">Summoned Tasks</h3>
        <table>
          <thead>
            <tr><th>Quest</th><th>Doomsday</th><th>Hours</th><th></th></tr>
          </thead>
          <tbody id="taskRows"></tbody>
        </table>
        <div class="actions">
          <button type="button" class="secondary" id="addTask">+ Add Quest</button>
          <button type="button" id="run">Conjure Plan</button>
          <button type="button" class="secondary" id="reset">Reset Timeline</button>
          <span class="status" id="status">Portal Ready</span>
        </div>
      </div>
      </section>
      <section class="card">
        <h2 class="section-title">Recommended Timeline</h2>
        <div class="result-meta">
          <div class="metric"><div class="k">Time Loop</div><div class="v" id="mWeek">-</div></div>
          <div class="metric"><div class="k">Ritual Slots</div><div class="v" id="mSlots">0</div></div>
          <div class="metric"><div class="k">Escaped Hours</div><div class="v" id="mUnalloc">0.0</div></div>
        </div>
        <div id="planOutput" class="muted">Conjure a plan to reveal the timeline.</div>
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
        <td><input type="text" placeholder="Quest name" value="${task.name ?? ""}" /></td>
        <td><input type="date" value="${task.due ?? ""}" /></td>
        <td><input type="number" min="0.5" step="0.5" value="${task.hours_needed ?? 1}" /></td>
        <td><button type="button" class="secondary removeBtn">Banish</button></td>
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
      status.textContent = "Portal Ready";
      planOutput.innerHTML = '<div class="muted">Conjure a plan to reveal the timeline.</div>';
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
            : '<div class="muted">(silent void)</div>';
          return `<div class="day-block"><div class="day-title">${day}</div>${tasksHtml}</div>`;
        })
        .join("");

      const unallocItems = Object.entries(unallocated)
        .map(([task, hours]) => `<div>${task}: <strong>${Number(hours).toFixed(1)}h</strong></div>`)
        .join("");

      planOutput.innerHTML = `
        ${daysHtml}
        <div class="day-block">
          <div class="day-title">Escaped Hours</div>
          ${unallocItems || '<div class="muted">Nothing escaped. Full containment.</div>'}
        </div>
      `;
    }

    async function runPlan() {
      status.textContent = "Divining...";
      runBtn.disabled = true;
      try {
        const payload = collectPayload();
        if (!payload.tasks.length) {
          throw new Error("Add at least one quest with hours.");
        }
        const res = await fetch("/api/plan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error("Request failed.");
        renderPlan(data);
        status.textContent = res.ok ? "Anomaly Processed" : "Portal destabilized";
      } catch (err) {
        status.textContent = "Signal corrupted";
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
