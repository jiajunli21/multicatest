// ============================================================
// 早盘宝接口 DTO / VO / 类型定义
// 来源：.multica/admission_check.md IA-001~IA-008
// ============================================================

// ---- IA-001: 早盘宝首页数据 ----

/** ETF 简要信息 */
export interface EtfBrief {
  code: string;
  name: string;
  score: number;
  rank: number;
  sector: string;       // [mock] 赛道名称
  tags: string[];        // [mock] 个基标签
}

/** 赛道分布 */
export interface SectorGroup {
  name: string;
  etfs: EtfBrief[];
}

export interface HomeResponse {
  top5_etfs: EtfBrief[];
  sectors: SectorGroup[];
  signal_date: string;    // YYYY-MM-DD
  market_tag: string;     // [default] "谨慎参与" | "积极参与"
  update_time: string;    // ISO-8601
}

// ---- IA-002: 资讯过滤 ----

export interface NewsItem {
  title: string;
  summary: string;
  time: string;           // ISO-8601
  source: string;
  url: string;
}

export interface NewsListResponse {
  news: NewsItem[];
  total: number;
}

// ---- IA-003: 历史表现 ----

export interface HistoryEtf {
  code: string;
  name: string;
  signal_3d_return: string | null;   // 不足3交易日为 null
  current_return: string | null;
}

export interface HistoryDay {
  date: string;
  etfs: HistoryEtf[];
}

export interface HistoryResponse {
  history: HistoryDay[];
}

// ---- IA-004: 指南内容 ----

export interface GuideResponse {
  guide: {
    content: string;      // [mock] Markdown 内容
    update_time: string;
  };
}

// ---- IA-005: 预警订阅 ----

export type SubscribeAction = 'subscribe' | 'unsubscribe';

export interface SubscribeRequest {
  action: SubscribeAction;
  user_id: string;
}

export interface SubscribeResponse {
  status: 'ok' | 'error';
  message: string;
}

// ---- IA-006: 预警推送触发 ----

export interface PushEtf {
  code: string;
  name: string;
  score: number;
  sector: string;
}

export interface PushMessageBody {
  title: string;
  etfs: PushEtf[];
  signal_date: string;
  market_tag: string;
  generated_at: string;
}

export interface PushTriggerResponse {
  status: 'ok' | 'error' | 'no_subscribers';
  message: string;
  delivered_count: number;
  failed_count: number;
}

// ---- IA-007: 一键加自选 ----

export interface WatchlistAddRequest {
  user_id: string;
  date?: string;          // YYYY-MM-DD，默认当日
}

export interface WatchlistAddResponse {
  status: 'ok' | 'partial' | 'error';
  added_count: number;
  failed_list: { code: string; reason: string }[];
}

// ---- IA-008: 运营配置读取 ----

export interface EtfConfigItem {
  code: string;
  name: string;
}

export interface EtfConfigResponse {
  etf_list: EtfConfigItem[];
}

// ---- 通用 ----

export interface ApiError {
  error: string;
  code: string;
  detail?: string;
}

export interface EmptyResponse {
  data: null;
  message: string;
}
