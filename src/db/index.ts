import Database from "better-sqlite3";
import { drizzle } from "drizzle-orm/better-sqlite3";
import * as schema from "./schema.ts";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { mkdirSync } from "node:fs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const dataDir = join(__dirname, "..", "..", "data");
mkdirSync(dataDir, { recursive: true });

const sqlite = new Database(join(dataDir, "todos.db"));
sqlite.pragma("journal_mode = WAL");

export const db = drizzle(sqlite, { schema });
