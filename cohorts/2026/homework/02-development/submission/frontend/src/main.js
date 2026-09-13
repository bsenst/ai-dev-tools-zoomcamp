import "./styles.css";
import { api } from "./api.js";

const columns = [
  { id: "todo", label: "To do", note: "Up next" },
  { id: "in_progress", label: "In progress", note: "In motion" },
  { id: "done", label: "Done", note: "Shipped" },
];
const priorities = { low: "Low", medium: "Medium", high: "High" };
let tasks = [];
let busy = false;

document.querySelector("#app").innerHTML = `
  <main class="shell">
    <header class="topbar">
      <a class="brand" href="/" aria-label="Flowboard home"><span class="brand-mark">F</span><span>flowboard</span></a>
      <div class="topbar-meta"><span class="status-dot"></span><span>${api.isMocked ? "Prototype mode" : "Local workspace"}</span></div>
    </header>
    <section class="intro">
      <div><p class="eyebrow">MONDAY, SEPTEMBER 14 <span>•</span> PERSONAL BOARD</p><h1>Make room for<br><em>good work.</em></h1><p class="lede">A quiet place to see what is moving, what is next, and what you can let go of.</p></div>
      <button class="primary-button" id="new-task"><span>+</span> New task</button>
    </section>
    <section class="summary" aria-label="Board summary"><div><strong id="total-count">0</strong><span>tasks on board</span></div><div><strong id="active-count">0</strong><span>in motion</span></div><div><strong id="done-count">0</strong><span>shipped</span></div><div class="summary-rule"></div><p id="board-message">Loading your board...</p></section>
    <div id="error" class="error" role="alert" hidden></div>
    <section class="board" id="board" aria-label="Kanban board"></section>
    <p class="footer-note">Keep it small. Keep it moving.</p>
  </main>
  <dialog id="task-dialog"><form method="dialog" id="task-form"><button class="close-button" value="cancel" aria-label="Close">×</button><p class="eyebrow">ADD TO YOUR BOARD</p><h2>What needs your attention?</h2><label>Task title<input name="title" maxlength="120" required placeholder="e.g. Outline the next release" /></label><label>Context <span class="optional">Optional</span><textarea name="description" maxlength="500" rows="3" placeholder="A little context helps future you."></textarea></label><label>Priority<select name="priority"><option value="low">Low</option><option value="medium" selected>Medium</option><option value="high">High</option></select></label><div class="form-actions"><button class="secondary-button" value="cancel">Cancel</button><button class="primary-button" value="default">Add task</button></div></form></dialog>
`;

const board = document.querySelector("#board");
const dialog = document.querySelector("#task-dialog");

function render() {
  document.querySelector("#total-count").textContent = tasks.length;
  document.querySelector("#active-count").textContent = tasks.filter((task) => task.status === "in_progress").length;
  document.querySelector("#done-count").textContent = tasks.filter((task) => task.status === "done").length;
  document.querySelector("#board-message").textContent = tasks.length ? "A little progress is still progress." : "Your next clear step starts here.";
  board.innerHTML = columns.map((column) => {
    const columnTasks = tasks.filter((task) => task.status === column.id);
    return `<section class="column" data-column="${column.id}"><div class="column-heading"><div><h2>${column.label}</h2><span>${column.note}</span></div><b>${columnTasks.length}</b></div><div class="task-list">${columnTasks.length ? columnTasks.map(taskCard).join("") : `<div class="empty"><span>○</span><p>Nothing here yet</p><small>Move a task in when it feels right.</small></div>`}</div></section>`;
  }).join("");
  board.querySelectorAll("[data-action]").forEach((button) => button.addEventListener("click", handleAction));
}

function taskCard(task) {
  const index = columns.findIndex((column) => column.id === task.status);
  const previous = columns[index - 1];
  const next = columns[index + 1];
  return `<article class="task-card"><div class="task-card-top"><span class="priority ${task.priority}">${priorities[task.priority]}</span><button class="icon-button" data-action="delete" data-id="${task.id}" aria-label="Delete ${escapeHtml(task.title)}">×</button></div><h3>${escapeHtml(task.title)}</h3>${task.description ? `<p>${escapeHtml(task.description)}</p>` : ""}<div class="task-footer"><span>#${String(task.id).padStart(3, "0")}</span><div>${previous ? `<button class="move-button" data-action="move" data-id="${task.id}" data-status="${previous.id}" aria-label="Move to ${previous.label}">←</button>` : ""}${next ? `<button class="move-button" data-action="move" data-id="${task.id}" data-status="${next.id}" aria-label="Move to ${next.label}">→</button>` : ""}</div></div></article>`;
}

function escapeHtml(value) { return value.replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]); }

async function handleAction(event) {
  const button = event.currentTarget;
  const id = Number(button.dataset.id);
  try {
    if (button.dataset.action === "delete") await api.deleteTask(id);
    if (button.dataset.action === "move") await api.updateTask(id, { status: button.dataset.status });
    tasks = await api.listTasks();
    render();
  } catch (error) { showError(error.message); }
}

function showError(message) { const error = document.querySelector("#error"); error.textContent = message; error.hidden = false; }

document.querySelector("#new-task").addEventListener("click", () => { document.querySelector("#task-form").reset(); dialog.showModal(); });
document.querySelector("#task-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  busy = true;
  const data = new FormData(event.currentTarget);
  try { await api.createTask({ title: data.get("title"), description: data.get("description"), priority: data.get("priority") }); tasks = await api.listTasks(); dialog.close(); render(); } catch (error) { showError(error.message); } finally { busy = false; }
});

async function load() { try { tasks = await api.listTasks(); render(); } catch (error) { showError(`Could not load your board: ${error.message}`); } }
load();