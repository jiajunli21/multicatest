import type { Context } from "hono";
import * as todoService from "../service/todo.service.ts";
import { AppError } from "../types/todo.ts";

export async function createTodo(c: Context): Promise<Response> {
  try {
    const body = await c.req.json();
    return c.json(todoService.createTodo(body as any), 201);
  } catch (e) {
    return handleError(e);
  }
}

export function listTodos(c: Context): Response {
  try {
    const statusParam = c.req.query("status");
    const pageParam = c.req.query("page");
    const pageSizeParam = c.req.query("page_size");
    const query: {
      status?: string;
      page?: number;
      page_size?: number;
    } = {
      status: statusParam ?? undefined,
      page: pageParam ? parseInt(pageParam, 10) : undefined,
      page_size: pageSizeParam ? parseInt(pageSizeParam, 10) : undefined,
    };
    if (query.page !== undefined && (isNaN(query.page) || query.page < 1)) {
      query.page = 1;
    }
    return c.json(todoService.listTodos(query as any));
  } catch (e) {
    return handleError(e);
  }
}

export function getTodo(c: Context): Response {
  try {
    const id = c.req.param("id")!;
    return c.json(todoService.getTodo(id));
  } catch (e) {
    return handleError(e);
  }
}

export async function updateTodoStatus(c: Context): Promise<Response> {
  try {
    const id = c.req.param("id")!;
    const body = await c.req.json();
    return c.json(todoService.updateStatus(id, body as any));
  } catch (e) {
    return handleError(e);
  }
}

export function deleteTodo(c: Context): Response {
  try {
    const id = c.req.param("id")!;
    todoService.deleteTodo(id);
    return new Response(null, { status: 204 });
  } catch (e) {
    return handleError(e);
  }
}

function handleError(e: unknown): Response {
  if (e instanceof AppError) {
    return new Response(
      JSON.stringify({ error: e.errorCode, message: e.message }),
      {
        status: e.statusCode,
        headers: { "Content-Type": "application/json" },
      },
    );
  }

  if (e instanceof SyntaxError) {
    return new Response(
      JSON.stringify({ error: "INVALID_JSON", message: "Invalid JSON in request body" }),
      {
        status: 400,
        headers: { "Content-Type": "application/json" },
      },
    );
  }

  console.error("Unexpected error:", e);
  return new Response(
    JSON.stringify({ error: "INTERNAL_ERROR", message: "An unexpected error occurred" }),
    {
      status: 500,
      headers: { "Content-Type": "application/json" },
    },
  );
}
