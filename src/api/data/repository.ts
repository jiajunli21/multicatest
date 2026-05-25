import { getDb } from './db';
import type { EtfBrief, SectorGroup, HomeResponse, HistoryDay, HistoryEtf } from '../types';

// ---- DB 行类型 ----

interface DbEtfScoreRow {
  etf_code: string;
  etf_name: string;
  composite_score: number;
  rank: number;
  sector: string;
  tags: string;
  market_tag: string;
  calc_date: string;
  created_at: string;
}

interface DbHistoricalRow {
  record_date: string;
  etf_code: string;
  etf_name: string;
  signal_3d_return: number | null;
  current_return: number | null;
}

// ---- 辅助 ----

function parseTags(tagsJson: string): string[] {
  try {
    return JSON.parse(tagsJson);
  } catch {
    return [];
  }
}

function formatReturn(value: number | null): string | null {
  if (value === null || value === undefined) return null;
  const prefix = value >= 0 ? '+' : '';
  return `${prefix}${value.toFixed(2)}%`;
}

// ---- 数据查询 ----

export function getTop5Scores(calcDate: string): DbEtfScoreRow[] {
  const db = getDb();
  return db
    .prepare('SELECT etf_code, etf_name, composite_score, rank, sector, tags, market_tag, calc_date, created_at FROM etf_scores WHERE calc_date = ? ORDER BY rank ASC LIMIT 5')
    .all(calcDate) as DbEtfScoreRow[];
}

export function getEtfScores(calcDate: string): DbEtfScoreRow[] {
  const db = getDb();
  return db
    .prepare('SELECT etf_code, etf_name, composite_score, rank, sector, tags, market_tag, calc_date, created_at FROM etf_scores WHERE calc_date = ? ORDER BY rank ASC')
    .all(calcDate) as DbEtfScoreRow[];
}

export function getLatestCalcDate(): string | undefined {
  const db = getDb();
  const row = db.prepare('SELECT calc_date FROM etf_scores ORDER BY calc_date DESC LIMIT 1').get() as { calc_date: string } | undefined;
  return row?.calc_date;
}

export function getHistoricalRecords(startDate?: string, endDate?: string): DbHistoricalRow[] {
  const db = getDb();
  let query = 'SELECT record_date, etf_code, etf_name, signal_3d_return, current_return FROM historical_records WHERE 1=1';
  const params: string[] = [];
  if (startDate) {
    query += ' AND record_date >= ?';
    params.push(startDate);
  }
  if (endDate) {
    query += ' AND record_date <= ?';
    params.push(endDate);
  }
  query += ' ORDER BY record_date DESC, rank ASC';
  return db.prepare(query).all(...params) as DbHistoricalRow[];
}

// ---- 业务对象构建 ----

function rowToEtfBrief(row: DbEtfScoreRow): EtfBrief {
  return {
    code: row.etf_code,
    name: row.etf_name,
    score: Math.round(row.composite_score * 100) / 100,
    rank: row.rank,
    sector: row.sector || '',
    tags: parseTags(row.tags),
  };
}

export function buildTop5Result(calcDate: string): HomeResponse | null {
  const rows = getTop5Scores(calcDate);
  if (rows.length === 0) return null;

  const topEtfs = rows.map(rowToEtfBrief);

  // 赛道分布
  const sectorMap = new Map<string, EtfBrief[]>();
  for (const etf of topEtfs) {
    const sec = etf.sector || '其他';
    if (!sectorMap.has(sec)) sectorMap.set(sec, []);
    sectorMap.get(sec)!.push(etf);
  }
  const sectors: SectorGroup[] = Array.from(sectorMap.entries()).map(([name, etfs]) => ({ name, etfs }));

  return {
    top5_etfs: topEtfs,
    sectors,
    signal_date: calcDate,
    market_tag: rows[0]?.market_tag || '数据未就绪',
    update_time: rows[0]?.created_at || new Date().toISOString(),
  };
}

export function buildHistory(): HistoryDay[] {
  const records = getHistoricalRecords();
  const dayMap = new Map<string, HistoryEtf[]>();

  for (const r of records) {
    if (!dayMap.has(r.record_date)) dayMap.set(r.record_date, []);
    dayMap.get(r.record_date)!.push({
      code: r.etf_code,
      name: r.etf_name,
      signal_3d_return: formatReturn(r.signal_3d_return),
      current_return: formatReturn(r.current_return),
    });
  }

  const result: HistoryDay[] = [];
  for (const [date, etfs] of dayMap.entries()) {
    result.push({ date, etfs });
  }
  result.sort((a, b) => b.date.localeCompare(a.date));
  return result;
}

export function buildHistoryForDate(date: string): HistoryDay | null {
  const records = getHistoricalRecords(date, date);
  if (records.length === 0) return null;

  return {
    date,
    etfs: records.map((r) => ({
      code: r.etf_code,
      name: r.etf_name,
      signal_3d_return: formatReturn(r.signal_3d_return),
      current_return: formatReturn(r.current_return),
    })),
  };
}
