import * as repo from "../repository/todo.repository.ts";
import type {
  Task,
  CreateTodoInput,
  UpdateStatusInput,
  ListTodosQuery,
  ListTodosResponse,
  TaskResponse,
  TodoStatus,
} from "../types/todo.ts";
import { VALID_STATUSES, ValidationError, NotFoundError } from "../types/todo.ts";

function toResponse(task: Task): TaskResponse {
  return {
    id: task.id,
    title: task.title,
    description: task.description,
    status: task.status as TodoStatus,
    created_at: task.created_at,
    updated_at: task.updated_at,
  };
}

function now(): string {
  return new Date().toISOString();
}

export function createTodo(input: CreateTodoInput): TaskResponse {
  if (!input.title || input.title.trim().length === 0) {
    throw new ValidationError("Title is required");
  }
  if (input.title.length > 200) {
    throw new ValidationError("Title must be at most 200 characters");
  }
  if (input.description && input.description.length > 2000) {
    throw new ValidationError("Description must be at most 2000 characters");
  }

  const timestamp = now();
  const task: Task = {
    id: crypto.randomUUID(),
    title: input.title.trim(),
    description: input.description?.trim() ?? null,
    status: "todo",
    created_at: timestamp,
    updated_at: timestamp,
  };

  return toResponse(repo.insert(task));
}

export function listTodos(query: ListTodosQuery): ListTodosResponse {
  if (query.status && !VALID_STATUSES.includes(query.status as TodoStatus)) {
    throw new ValidationError(
      `Invalid status filter: "${query.status}". Must be todo, in_progress, or done`,
    );
  }
  if (query.page_size !== undefined && query.page_size > 100) {
    throw new ValidationError("page_size must be at most 100");
  }

  const page = Math.max(1, query.page ?? 1);
  const pageSize = Math.min(100, Math.max(1, query.page_size ?? 20));

  const { items, total } = repo.findMany({ ...query, page, page_size: pageSize });

  return {
    items: items.map(toResponse),
    total,
    page,
    page_size: pageSize,
  };
}

export function getTodo(id: string): TaskResponse {
  const task = repo.findById(id);
  if (!task) {
    throw new NotFoundError(`Todo with id "${id}" not found`);
  }
  return toResponse(task);
}

export function updateStatus(id: string, input: UpdateStatusInput): TaskResponse {
  if (!VALID_STATUSES.includes(input.status)) {
    throw new ValidationError(
      `Invalid status: "${input.status}". Must be todo, in_progress, or done`,
    );
  }

  const existing = repo.findById(id);
  if (!existing) {
    throw new NotFoundError(`Todo with id "${id}" not found`);
  }

  const updated = repo.updateStatus(id, input.status, now());
  return toResponse(updated!);
}

export function deleteTodo(id: string): void {
  const existing = repo.findById(id);
  if (!existing) {
    throw new NotFoundError(`Todo with id "${id}" not found`);
  }
  repo.deleteById(id);
}
