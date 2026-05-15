import { describe, it, expect, beforeEach, vi } from "vitest";
import { Hono } from "hono";

vi.mock("../../src/service/todo.service.ts", () => ({
  createTodo: vi.fn(),
  listTodos: vi.fn(),
  getTodo: vi.fn(),
  updateStatus: vi.fn(),
  deleteTodo: vi.fn(),
}));

import * as handler from "../../src/handler/todo.handler.ts";
import * as todoService from "../../src/service/todo.service.ts";

function setupApp() {
  const app = new Hono();
  app.post("/api/todos", handler.createTodo);
  app.get("/api/todos", handler.listTodos);
  app.get("/api/todos/:id", handler.getTodo);
  app.patch("/api/todos/:id/status", handler.updateTodoStatus);
  app.delete("/api/todos/:id", handler.deleteTodo);
  return app;
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("POST /api/todos", () => {
  it("returns 201 with created task", async () => {
    vi.mocked(todoService.createTodo).mockReturnValue({
      id: "id-1",
      title: "Test",
      description: null,
      status: "todo",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    });
    const app = setupApp();
    const res = await app.request("/api/todos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "Test" }),
    });
    expect(res.status).toBe(201);
    const body = await res.json();
    expect(body.title).toBe("Test");
  });

  it("returns 400 for VALIDATION_ERROR", async () => {
    const { ValidationError } = await import("../../src/types/todo.ts");
    vi.mocked(todoService.createTodo).mockImplementation(() => {
      throw new ValidationError("Title is required");
    });
    const app = setupApp();
    const res = await app.request("/api/todos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "" }),
    });
    expect(res.status).toBe(400);
    const body = await res.json();
    expect(body.error).toBe("VALIDATION_ERROR");
  });

  it("returns 400 for invalid JSON", async () => {
    const app = setupApp();
    const res = await app.request("/api/todos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "not json",
    });
    expect(res.status).toBe(400);
    const body = await res.json();
    expect(body.error).toBe("INVALID_JSON");
  });

  it("returns 500 for unexpected errors", async () => {
    vi.mocked(todoService.createTodo).mockImplementation(() => {
      throw new Error("DB connection failed");
    });
    const app = setupApp();
    const res = await app.request("/api/todos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "OK" }),
    });
    expect(res.status).toBe(500);
    const body = await res.json();
    expect(body.error).toBe("INTERNAL_ERROR");
  });
});

describe("GET /api/todos", () => {
  it("returns 200 with paginated list", async () => {
    vi.mocked(todoService.listTodos).mockReturnValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
    });
    const app = setupApp();
    const res = await app.request("/api/todos");
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.items).toEqual([]);
    expect(body.total).toBe(0);
  });

  it("passes query params to service", async () => {
    vi.mocked(todoService.listTodos).mockReturnValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 10,
    });
    const app = setupApp();
    await app.request("/api/todos?status=todo&page=2&page_size=10");
    const callArg = vi.mocked(todoService.listTodos).mock.calls[0][0];
    expect(callArg.status).toBe("todo");
    expect(callArg.page).toBe(2);
    expect(callArg.page_size).toBe(10);
  });

  it("corrects invalid page to 1", async () => {
    vi.mocked(todoService.listTodos).mockReturnValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
    });
    const app = setupApp();
    await app.request("/api/todos?page=abc");
    const callArg = vi.mocked(todoService.listTodos).mock.calls[0][0];
    expect(callArg.page).toBe(1);
  });

  it("corrects invalid page_size to 20", async () => {
    vi.mocked(todoService.listTodos).mockReturnValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
    });
    const app = setupApp();
    await app.request("/api/todos?page_size=abc");
    const callArg = vi.mocked(todoService.listTodos).mock.calls[0][0];
    expect(callArg.page_size).toBe(20);
  });

  it("corrects zero page to 1", async () => {
    vi.mocked(todoService.listTodos).mockReturnValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
    });
    const app = setupApp();
    await app.request("/api/todos?page=0");
    const callArg = vi.mocked(todoService.listTodos).mock.calls[0][0];
    expect(callArg.page).toBe(1);
  });

  it("corrects zero page_size to 20", async () => {
    vi.mocked(todoService.listTodos).mockReturnValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
    });
    const app = setupApp();
    await app.request("/api/todos?page_size=0");
    const callArg = vi.mocked(todoService.listTodos).mock.calls[0][0];
    expect(callArg.page_size).toBe(20);
  });

  it("returns 400 for VALIDATION_ERROR from service", async () => {
    const { ValidationError } = await import("../../src/types/todo.ts");
    vi.mocked(todoService.listTodos).mockImplementation(() => {
      throw new ValidationError("Invalid status");
    });
    const app = setupApp();
    const res = await app.request("/api/todos?status=bad");
    expect(res.status).toBe(400);
    const body = await res.json();
    expect(body.error).toBe("VALIDATION_ERROR");
  });
});

describe("GET /api/todos/:id", () => {
  it("returns 200 with task details", async () => {
    vi.mocked(todoService.getTodo).mockReturnValue({
      id: "id-1",
      title: "Test",
      description: null,
      status: "todo",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    });
    const app = setupApp();
    const res = await app.request("/api/todos/id-1");
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.title).toBe("Test");
  });

  it("returns 404 for NOT_FOUND", async () => {
    const { NotFoundError } = await import("../../src/types/todo.ts");
    vi.mocked(todoService.getTodo).mockImplementation(() => {
      throw new NotFoundError("not found");
    });
    const app = setupApp();
    const res = await app.request("/api/todos/missing");
    expect(res.status).toBe(404);
    const body = await res.json();
    expect(body.error).toBe("NOT_FOUND");
  });
});

describe("PATCH /api/todos/:id/status", () => {
  it("returns 200 with updated task", async () => {
    vi.mocked(todoService.updateStatus).mockReturnValue({
      id: "id-1",
      title: "Test",
      description: null,
      status: "done",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    });
    const app = setupApp();
    const res = await app.request("/api/todos/id-1/status", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "done" }),
    });
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.status).toBe("done");
  });

  it("returns 400 for invalid JSON", async () => {
    const app = setupApp();
    const res = await app.request("/api/todos/id-1/status", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: "bad json",
    });
    expect(res.status).toBe(400);
    const body = await res.json();
    expect(body.error).toBe("INVALID_JSON");
  });

  it("returns 404 for not found", async () => {
    const { NotFoundError } = await import("../../src/types/todo.ts");
    vi.mocked(todoService.updateStatus).mockImplementation(() => {
      throw new NotFoundError("not found");
    });
    const app = setupApp();
    const res = await app.request("/api/todos/missing/status", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "done" }),
    });
    expect(res.status).toBe(404);
  });
});

describe("DELETE /api/todos/:id", () => {
  it("returns 204 on success", async () => {
    vi.mocked(todoService.deleteTodo).mockReturnValue(undefined);
    const app = setupApp();
    const res = await app.request("/api/todos/id-1", { method: "DELETE" });
    expect(res.status).toBe(204);
  });

  it("returns 404 for non-existent task", async () => {
    const { NotFoundError } = await import("../../src/types/todo.ts");
    vi.mocked(todoService.deleteTodo).mockImplementation(() => {
      throw new NotFoundError("not found");
    });
    const app = setupApp();
    const res = await app.request("/api/todos/missing", { method: "DELETE" });
    expect(res.status).toBe(404);
    const body = await res.json();
    expect(body.error).toBe("NOT_FOUND");
  });

  it("returns 500 for unexpected errors", async () => {
    vi.mocked(todoService.deleteTodo).mockImplementation(() => {
      throw new Error("DB failure");
    });
    const app = setupApp();
    const res = await app.request("/api/todos/id-1", { method: "DELETE" });
    expect(res.status).toBe(500);
    const body = await res.json();
    expect(body.error).toBe("INTERNAL_ERROR");
  });
});
