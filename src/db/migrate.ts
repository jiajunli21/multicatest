import Database from "better-sqlite3";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { mkdirSync, readFileSync } from "node:fs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const dataDir = join(__dirname, "..", "..", "data");
mkdirSync(dataDir, { recursive: true });

const sqlite = new Database(join(dataDir, "todos.db"));
sqlite.pragma("journal_mode = WAL");

const schemaPath = join(__dirname, "..", "..", "schema", "todos.sql");
const schemaSql = readFileSync(schemaPath, "utf-8");
sqlite.exec(schemaSql);

console.log("Migration completed successfully.");
sqlite.close();
