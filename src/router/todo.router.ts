import { Hono } from "hono";
import * as handler from "../handler/todo.handler.ts";

export const todoRouter = new Hono();

todoRouter.post("/", handler.createTodo);
todoRouter.get("/", handler.listTodos);
todoRouter.get("/:id", handler.getTodo);
todoRouter.patch("/:id/status", handler.updateTodoStatus);
todoRouter.delete("/:id", handler.deleteTodo);
