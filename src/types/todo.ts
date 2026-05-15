export type TodoStatus = "todo" | "in_progress" | "done";

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TodoStatus;
  created_at: string;
  updated_at: string;
}

export interface CreateTodoInput {
  title: string;
  description?: string;
}

export interface UpdateStatusInput {
  status: TodoStatus;
}

export interface ListTodosQuery {
  status?: TodoStatus;
  page?: number;
  page_size?: number;
}

export interface TaskResponse {
  id: string;
  title: string;
  description: string | null;
  status: TodoStatus;
  created_at: string;
  updated_at: string;
}

export interface ListTodosResponse {
  items: TaskResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface ErrorResponse {
  error: string;
  message: string;
}

export const VALID_STATUSES: TodoStatus[] = ["todo", "in_progress", "done"];

export class AppError extends Error {
  constructor(
    public statusCode: number,
    public errorCode: string,
    message: string,
  ) {
    super(message);
    this.name = "AppError";
  }
}

export class ValidationError extends AppError {
  constructor(message: string) {
    super(400, "VALIDATION_ERROR", message);
  }
}

export class NotFoundError extends AppError {
  constructor(message: string) {
    super(404, "NOT_FOUND", message);
  }
}
