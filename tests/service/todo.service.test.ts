import { describe, it, expect, beforeEach, vi } from "vitest";

vi.mock("../../src/repository/todo.repository.ts", () => ({
  insert: vi.fn(),
  findById: vi.fn(),
  findMany: vi.fn(),
  updateStatus: vi.fn(),
  deleteById: vi.fn(),
}));

import * as todoService from "../../src/service/todo.service.ts";
import * as repo from "../../src/repository/todo.repository.ts";

function makeTask(overrides: Record<string, unknown> = {}) {
  return {
    id: "550e8400-e29b-41d4-a716-446655440000",
    title: "Test Task",
    description: "A test task",
    status: "todo",
    created_at: "2026-05-15T08:00:00.000Z",
    updated_at: "2026-05-15T08:00:00.000Z",
    ...overrides,
  };
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("createTodo", () => {
  it("creates a task with valid input", () => {
    vi.mocked(repo.insert).mockImplementation((t: any) => t);
    const result = todoService.createTodo({
      title: "My Task",
      description: "Do something",
    });
    expect(result.title).toBe("My Task");
    expect(result.description).toBe("Do something");
    expect(result.status).toBe("todo");
    expect(result.id).toBeTruthy();
    expect(result.created_at).toBeTruthy();
    expect(result.updated_at).toBeTruthy();
    expect(repo.insert).toHaveBeenCalledTimes(1);
  });

  it("creates a task without description", () => {
    vi.mocked(repo.insert).mockImplementation((t: any) => t);
    const result = todoService.createTodo({ title: "Minimal Task" });
    expect(result.description).toBeNull();
  });

  it("trims whitespace from title", () => {
    vi.mocked(repo.insert).mockImplementation((t: any) => t);
    const result = todoService.createTodo({ title: "  Trimmed  " });
    expect(result.title).toBe("Trimmed");
  });

  it("throws ValidationError for empty title", () => {
    expect(() => todoService.createTodo({ title: "" })).toThrow("Title is required");
  });

  it("throws ValidationError for whitespace-only title", () => {
    expect(() => todoService.createTodo({ title: "   " })).toThrow("Title is required");
  });

  it("throws ValidationError for title > 200 chars", () => {
    expect(() => todoService.createTodo({ title: "x".repeat(201) })).toThrow(
      "Title must be at most 200 characters",
    );
  });

  it("allows title exactly 200 chars", () => {
    vi.mocked(repo.insert).mockImplementation((t: any) => t);
    const result = todoService.createTodo({ title: "x".repeat(200) });
    expect(result.title.length).toBe(200);
  });

  it("throws ValidationError for description > 2000 chars", () => {
    expect(() =>
      todoService.createTodo({ title: "OK", description: "x".repeat(2001) }),
    ).toThrow("Description must be at most 2000 characters");
  });

  it("allows description exactly 2000 chars", () => {
    vi.mocked(repo.insert).mockImplementation((t: any) => t);
    const result = todoService.createTodo({ title: "OK", description: "x".repeat(2000) });
    expect(result.description!.length).toBe(2000);
  });

  it("trims description whitespace", () => {
    vi.mocked(repo.insert).mockImplementation((t: any) => t);
    const result = todoService.createTodo({ title: "OK", description: "  desc  " });
    expect(result.description).toBe("desc");
  });

  it("sets default status to todo", () => {
    vi.mocked(repo.insert).mockImplementation((t: any) => t);
    const result = todoService.createTodo({ title: "New" });
    expect(result.status).toBe("todo");
  });

  it("generates unique IDs for different tasks", () => {
    vi.mocked(repo.insert).mockImplementation((t: any) => t);
    const r1 = todoService.createTodo({ title: "A" });
    const r2 = todoService.createTodo({ title: "B" });
    expect(r1.id).not.toBe(r2.id);
  });
});

describe("listTodos", () => {
  it("returns paginated list with defaults", () => {
    vi.mocked(repo.findMany).mockReturnValue({ items: [], total: 0 });
    const result = todoService.listTodos({});
    expect(result.items).toEqual([]);
    expect(result.total).toBe(0);
    expect(result.page).toBe(1);
    expect(result.page_size).toBe(20);
  });

  it("passes status filter to repository", () => {
    vi.mocked(repo.findMany).mockReturnValue({ items: [], total: 0 });
    todoService.listTodos({ status: "in_progress" as any });
    const call = vi.mocked(repo.findMany).mock.calls[0][0];
    expect(call.status).toBe("in_progress");
  });

  it("throws for invalid status filter", () => {
    expect(() => todoService.listTodos({ status: "archived" as any })).toThrow(
      'Invalid status filter: "archived"',
    );
  });

  it("throws for page_size > 100", () => {
    expect(() => todoService.listTodos({ page_size: 101 })).toThrow(
      "page_size must be at most 100",
    );
  });

  it("allows page_size exactly 100", () => {
    vi.mocked(repo.findMany).mockReturnValue({ items: [], total: 0 });
    const result = todoService.listTodos({ page_size: 100 });
    expect(result.page_size).toBe(100);
  });

  it("clamps page to minimum 1", () => {
    vi.mocked(repo.findMany).mockReturnValue({ items: [], total: 0 });
    const result = todoService.listTodos({ page: 0 });
    expect(result.page).toBe(1);
  });

  it("handles NaN page_size by defaulting to 20", () => {
    vi.mocked(repo.findMany).mockReturnValue({ items: [], total: 0 });
    const result = todoService.listTodos({ page_size: NaN });
    expect(result.page_size).toBe(20);
  });

  it("handles NaN page by defaulting to 1", () => {
    vi.mocked(repo.findMany).mockReturnValue({ items: [], total: 0 });
    const result = todoService.listTodos({ page: NaN });
    expect(result.page).toBe(1);
  });

  it("returns items mapped to TaskResponse", () => {
    const task = makeTask();
    vi.mocked(repo.findMany).mockReturnValue({ items: [task as any], total: 1 });
    const result = todoService.listTodos({});
    expect(result.items[0].id).toBe(task.id);
    expect(result.items[0].title).toBe(task.title);
    expect(result.items[0].status).toBe("todo");
  });
});

describe("getTodo", () => {
  it("returns task when found", () => {
    const task = makeTask();
    vi.mocked(repo.findById).mockReturnValue(task as any);
    const result = todoService.getTodo(task.id);
    expect(result.id).toBe(task.id);
    expect(result.title).toBe(task.title);
  });

  it("throws NotFoundError when task not found", () => {
    vi.mocked(repo.findById).mockReturnValue(undefined);
    expect(() => todoService.getTodo("missing-id")).toThrow("not found");
  });
});

describe("updateStatus", () => {
  it("updates status successfully", () => {
    const task = makeTask();
    vi.mocked(repo.findById).mockReturnValue(task as any);
    vi.mocked(repo.updateStatus).mockReturnValue({ ...task, status: "done" } as any);
    const result = todoService.updateStatus(task.id, { status: "done" });
    expect(result.status).toBe("done");
    expect(repo.updateStatus).toHaveBeenCalledWith(task.id, "done", expect.any(String));
  });

  it("throws ValidationError for invalid status", () => {
    expect(() =>
      todoService.updateStatus("id", { status: "archived" as any }),
    ).toThrow('Invalid status: "archived"');
  });

  it("throws NotFoundError for non-existent task", () => {
    vi.mocked(repo.findById).mockReturnValue(undefined);
    expect(() => todoService.updateStatus("missing", { status: "done" })).toThrow(
      "not found",
    );
  });

  it("allows all three valid statuses", () => {
    const task = makeTask();
    vi.mocked(repo.findById).mockReturnValue(task as any);
    vi.mocked(repo.updateStatus).mockImplementation(
      (_id: string, status: string) => ({ ...task, status }),
    );
    for (const status of ["todo", "in_progress", "done"] as const) {
      const result = todoService.updateStatus(task.id, { status });
      expect(result.status).toBe(status);
    }
  });

  it("allows transition from done back to todo", () => {
    const task = makeTask({ status: "done" });
    vi.mocked(repo.findById).mockReturnValue(task as any);
    vi.mocked(repo.updateStatus).mockReturnValue({ ...task, status: "todo" } as any);
    const result = todoService.updateStatus(task.id, { status: "todo" });
    expect(result.status).toBe("todo");
  });
});

describe("deleteTodo", () => {
  it("deletes existing task", () => {
    vi.mocked(repo.findById).mockReturnValue(makeTask() as any);
    vi.mocked(repo.deleteById).mockReturnValue(true);
    expect(() => todoService.deleteTodo("id")).not.toThrow();
    expect(repo.deleteById).toHaveBeenCalledWith("id");
  });

  it("throws NotFoundError for non-existent task", () => {
    vi.mocked(repo.findById).mockReturnValue(undefined);
    expect(() => todoService.deleteTodo("missing")).toThrow("not found");
    expect(repo.deleteById).not.toHaveBeenCalled();
  });
});
