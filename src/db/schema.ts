import { sqliteTable, text, index } from "drizzle-orm/sqlite-core";

export const todos = sqliteTable(
  "todos",
  {
    id: text("id").primaryKey(),
    title: text("title").notNull(),
    description: text("description"),
    status: text("status").notNull().default("todo"),
    created_at: text("created_at").notNull(),
    updated_at: text("updated_at").notNull(),
  },
  (table) => [
    index("idx_todos_status").on(table.status),
    index("idx_todos_created_at").on(table.created_at),
  ],
);
