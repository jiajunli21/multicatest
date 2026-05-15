import { eq, sql, and } from "drizzle-orm";
import { db } from "../db/index.ts";
import { todos } from "../db/schema.ts";
import type { Task, TodoStatus, ListTodosQuery } from "../types/todo.ts";

export function insert(task: Task): Task {
  db.insert(todos).values(task).run();
  return task;
}

export function findById(id: string): Task | undefined {
  return db.select().from(todos).where(eq(todos.id, id)).get() as Task | undefined;
}

export function findMany(query: ListTodosQuery): { items: Task[]; total: number } {
  const conditions = [];
  if (query.status) {
    conditions.push(eq(todos.status, query.status as TodoStatus));
  }

  const whereClause = conditions.length > 0 ? and(...conditions) : undefined;

  const totalRow = db
    .select({ count: sql<number>`count(*)` })
    .from(todos)
    .where(whereClause)
    .get();
  const total = totalRow?.count ?? 0;

  const page = Math.max(1, query.page ?? 1);
  const pageSize = Math.min(100, Math.max(1, query.page_size ?? 20));
  const offset = (page - 1) * pageSize;

  const items = db
    .select()
    .from(todos)
    .where(whereClause)
    .orderBy(sql`${todos.created_at} DESC`)
    .limit(pageSize)
    .offset(offset)
    .all() as Task[];

  return { items, total };
}

export function updateStatus(id: string, status: TodoStatus, updatedAt: string): Task | undefined {
  db
    .update(todos)
    .set({ status, updated_at: updatedAt })
    .where(eq(todos.id, id))
    .run();
  return findById(id);
}

export function deleteById(id: string): boolean {
  const result = db.delete(todos).where(eq(todos.id, id)).run();
  return result.changes > 0;
}
