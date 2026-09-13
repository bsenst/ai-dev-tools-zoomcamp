const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === "true";
const MOCK_KEY = "flowboard-mock-tasks";

const seedTasks = [
  { id: 1, title: "Sketch the first user flow", description: "Turn the loose ideas into a short, testable path.", priority: "high", status: "done", created_at: new Date().toISOString() },
  { id: 2, title: "Make the board feel calm", description: "Tune spacing, contrast, and the empty states.", priority: "medium", status: "in_progress", created_at: new Date().toISOString() },
  { id: 3, title: "Invite a teammate to review", description: "Ask for one sharp observation before shipping.", priority: "low", status: "todo", created_at: new Date().toISOString() },
];

function mockTasks() {
  const saved = localStorage.getItem(MOCK_KEY);
  if (!saved) localStorage.setItem(MOCK_KEY, JSON.stringify(seedTasks));
  return JSON.parse(localStorage.getItem(MOCK_KEY));
}

function saveMock(tasks) {
  localStorage.setItem(MOCK_KEY, JSON.stringify(tasks));
  return tasks;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error((await response.json()).detail || "Something went wrong");
  return response.status === 204 ? null : response.json();
}

export const api = {
  isMocked: USE_MOCKS,
  async listTasks() {
    return USE_MOCKS ? mockTasks() : request("/api/tasks");
  },
  async createTask(payload) {
    if (!USE_MOCKS) return request("/api/tasks", { method: "POST", body: JSON.stringify(payload) });
    return saveMock([{ ...payload, id: Date.now(), status: "todo", created_at: new Date().toISOString() }, ...mockTasks()])[0];
  },
  async updateTask(id, payload) {
    if (!USE_MOCKS) return request(`/api/tasks/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
    const tasks = mockTasks().map((task) => task.id === id ? { ...task, ...payload } : task);
    saveMock(tasks);
    return tasks.find((task) => task.id === id);
  },
  async deleteTask(id) {
    if (!USE_MOCKS) return request(`/api/tasks/${id}`, { method: "DELETE" });
    saveMock(mockTasks().filter((task) => task.id !== id));
  },
};