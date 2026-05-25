import Database from 'better-sqlite3';
import path from 'path';

let db: Database.Database | null = null;
let dbPath: string | null = null;

export function getDbPath(): string {
  if (dbPath) return dbPath;

  // 尝试多个路径查找数据库
  const candidates = [
    path.resolve(process.cwd(), 'morning_report.db'),
    path.resolve(__dirname, '..', '..', '..', 'morning_report.db'),
  ];

  const fs = require('fs');
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      dbPath = candidate;
      return dbPath;
    }
  }

  // 默认使用 cwd
  dbPath = candidates[0];
  return dbPath;
}

export function getDb(): Database.Database {
  if (db) return db;
  const dbFile = getDbPath();
  db = new Database(dbFile, { readonly: true });
  db.pragma('journal_mode = WAL');
  return db;
}

export function closeDb(): void {
  if (db) {
    db.close();
    db = null;
  }
}

/** 检查数据库是否可用（文件存在且有数据） */
export function isDbAvailable(): boolean {
  try {
    const p = getDbPath();
    const fs = require('fs');
    if (!fs.existsSync(p)) return false;
    const db = getDb();
    const row = db.prepare('SELECT count(*) as cnt FROM etf_scores').get() as { cnt: number };
    return row.cnt > 0;
  } catch {
    return false;
  }
}
