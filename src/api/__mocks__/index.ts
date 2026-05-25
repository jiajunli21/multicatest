// ============================================================
// 早盘宝 Mock 数据
// 所有 Mock 数据必须标注 [mock] 状态
// Phase 2 桥接真实数据后删除或替换本文件
// ============================================================

import {
  EtfBrief, SectorGroup, NewsItem, HistoryDay,
  PushEtf, EtfConfigItem, HomeResponse,
} from '../types';

// ---- IA-001 Mock: Top5 + 赛道 + 标签 (赛道和标签为 [mock]) ----

export const mockTop5Etfs: EtfBrief[] = [
  { code: '510050', name: '上证50ETF', score: 0.892, rank: 1, sector: '大金融', tags: ['[mock] 资金流入', '[mock] 低估值'] },
  { code: '510300', name: '沪深300ETF', score: 0.845, rank: 2, sector: '大金融', tags: ['[mock] 外资增持', '[mock] 低波动'] },
  { code: '159915', name: '创业板ETF', score: 0.798, rank: 3, sector: '科技成长', tags: ['[mock] 超跌反弹', '[mock] 高弹性'] },
  { code: '512880', name: '证券ETF', score: 0.756, rank: 4, sector: '大金融', tags: ['[mock] 券商异动'] },
  { code: '512100', name: '中证1000ETF', score: 0.712, rank: 5, sector: '中小盘', tags: ['[mock] 小盘活跃', '[mock] 资金关注'] },
];

export const mockSectors: SectorGroup[] = [
  { name: '大金融', etfs: [mockTop5Etfs[0], mockTop5Etfs[1], mockTop5Etfs[3]] },
  { name: '科技成长', etfs: [mockTop5Etfs[2]] },
  { name: '中小盘', etfs: [mockTop5Etfs[4]] },
];

export const mockHomeResponse: HomeResponse = {
  top5_etfs: mockTop5Etfs,
  sectors: mockSectors,
  signal_date: '2026-05-25',
  market_tag: '[default] 谨慎参与',
  update_time: new Date().toISOString(),
};

// ---- IA-002 Mock: 资讯列表 [mock] ----

export const mockNewsList: NewsItem[] = [
  {
    title: '[mock] ETF市场周报：资金持续流入宽基ETF',
    summary: '本周ETF市场整体呈现净流入态势，宽基ETF仍是资金主要配置方向...',
    time: '2026-05-25T08:30:00Z',
    source: '[mock] ETF资讯',
    url: 'https://example.com/news/1',
  },
  {
    title: '[mock] 早盘关注：科技板块ETF表现活跃',
    summary: '受隔夜美股科技股上涨带动，今日科技类ETF早盘表现活跃...',
    time: '2026-05-25T08:00:00Z',
    source: '[mock] 市场快讯',
    url: 'https://example.com/news/2',
  },
  {
    title: '[mock] 证券ETF获大额净申购',
    summary: '证券ETF连续3日获大额净申购，合计净流入超50亿元...',
    time: '2026-05-24T16:30:00Z',
    source: '[mock] 资金流向',
    url: 'https://example.com/news/3',
  },
  {
    title: '[mock] 创业板ETF波动率降至年内低位',
    summary: '创业板ETF近20日年化波动率降至15%以下，为年内最低水平...',
    time: '2026-05-24T15:00:00Z',
    source: '[mock] 量化观察',
    url: 'https://example.com/news/4',
  },
  {
    title: '[mock] 中证1000ETF成交额创阶段新高',
    summary: '中证1000ETF今日成交额突破30亿元，创近3个月新高...',
    time: '2026-05-24T14:00:00Z',
    source: '[mock] 成交龙虎榜',
    url: 'https://example.com/news/5',
  },
];

export const mockNewsTotal = 5;

// ---- IA-003 Mock: 历史表现 [mock] ----

export const mockHistory: HistoryDay[] = [
  {
    date: '2026-05-22',
    etfs: [
      { code: '510050', name: '上证50ETF', signal_3d_return: '+0.85%', current_return: '+1.23%' },
      { code: '159915', name: '创业板ETF', signal_3d_return: '+1.52%', current_return: '+2.10%' },
      { code: '510300', name: '沪深300ETF', signal_3d_return: '+0.63%', current_return: '+0.98%' },
      { code: '512880', name: '证券ETF', signal_3d_return: '-0.21%', current_return: '+0.15%' },
      { code: '588000', name: '科创50ETF', signal_3d_return: '+2.34%', current_return: '+3.01%' },
    ],
  },
  {
    date: '2026-05-21',
    etfs: [
      { code: '510050', name: '上证50ETF', signal_3d_return: '-0.32%', current_return: '+0.85%' },
      { code: '159915', name: '创业板ETF', signal_3d_return: '+1.10%', current_return: '+1.52%' },
      { code: '510300', name: '沪深300ETF', signal_3d_return: '+0.21%', current_return: '+0.63%' },
      { code: '512880', name: '证券ETF', signal_3d_return: '+0.45%', current_return: '-0.21%' },
      { code: '588000', name: '科创50ETF', signal_3d_return: null, current_return: '+2.34%' },
    ],
  },
];

// ---- IA-004 Mock: 指南内容 [mock] ----

export const mockGuideContent = `# [mock] 早盘宝使用指南

## 什么是早盘宝？

早盘宝是基于 ETF 多因子评分模型，在每个交易日开盘前为您筛选最具关注价值的 Top5 ETF 的工具。

## 评分模型

早盘宝采用四因子加权评分模型：

| 因子 | 权重 | 说明 |
|------|------|------|
| 热度因子 | 50% | 基于搜索热度和首购热度 |
| 动量因子 | 35% | 基于近期价格动量 |
| 流动性因子 | 10% | 基于成交额 |
| 低波因子 | 5% | 基于波动率（取反） |

## 使用建议

- 早盘宝信号仅供投资参考，不构成投资建议
- 请结合自身风险偏好和投资目标独立决策
- 市场有风险，投资需谨慎
`;

// ---- IA-006 Mock: 推送 ETF [mock] ----

export const mockPushEtfs: PushEtf[] = [
  { code: '510050', name: '上证50ETF', score: 0.892, sector: '[mock] 大金融' },
  { code: '510300', name: '沪深300ETF', score: 0.845, sector: '[mock] 大金融' },
  { code: '159915', name: '创业板ETF', score: 0.798, sector: '[mock] 科技成长' },
  { code: '512880', name: '证券ETF', score: 0.756, sector: '[mock] 大金融' },
  { code: '512100', name: '中证1000ETF', score: 0.712, sector: '[mock] 中小盘' },
];

// ---- IA-008 Mock: ETF 样本配置 [mock] ----

export const mockEtfConfig: EtfConfigItem[] = [
  { code: '510050', name: '上证50ETF' },
  { code: '510300', name: '沪深300ETF' },
  { code: '510500', name: '中证500ETF' },
  { code: '159915', name: '创业板ETF' },
  { code: '588000', name: '科创50ETF' },
  { code: '512880', name: '证券ETF' },
  { code: '512100', name: '中证1000ETF' },
  { code: '512690', name: '酒ETF' },
  { code: '512010', name: '医药ETF' },
  { code: '159949', name: '创业板50ETF' },
  { code: '512170', name: '医疗ETF' },
  { code: '515050', name: 'AI智能ETF' },
  { code: '512660', name: '军工ETF' },
  { code: '512800', name: '银行ETF' },
  { code: '159845', name: '中证1000ETF' },
  { code: '512720', name: '计算机ETF' },
  { code: '159995', name: '芯片ETF' },
  { code: '513100', name: '纳指ETF' },
  { code: '512980', name: '传媒ETF' },
  { code: '512580', name: '碳中和ETF' },
];

// ---- 订阅状态 Mock (内存) ----

export const mockSubscriptionStore = new Map<string, boolean>();
