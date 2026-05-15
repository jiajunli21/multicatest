import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { todoRouter } from "./router/todo.router.ts";

const app = new Hono();

app.route("/api/todos", todoRouter);

const port = parseInt(process.env.PORT ?? "3000", 10);
console.log(`Server running on http://localhost:${port}`);

serve({ fetch: app.fetch, port });
