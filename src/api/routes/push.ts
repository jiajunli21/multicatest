import { Router, Response } from 'express';
import { mockPushEtfs, mockSubscriptionStore } from '../__mocks__';
import { isDbAvailable } from '../data/db';
import { buildTop5Result, getLatestCalcDate } from '../data/repository';
import { PushMessageBody, PushTriggerResponse, PushEtf } from '../types';

const router = Router();

/**
 * IA-006: 预警推送触发
 * POST /api/v1/morning-report/push/trigger
 *
 * 数据计算完成后推送消息给已订阅用户（内部触发）
 * [default] 暂默认有权限
 * Phase 2: 优先使用 DB 真实 ETF 数据构建推送消息，[mock] 兜底
 */
router.post('/push/trigger', (_req, res: Response) => {
  const subscribers = Array.from(mockSubscriptionStore.entries())
    .filter(([, v]) => v)
    .map(([k]) => k);

  if (subscribers.length === 0) {
    const resp: PushTriggerResponse = {
      status: 'no_subscribers',
      message: '无订阅用户，未触发推送',
      delivered_count: 0,
      failed_count: 0,
    };
    res.json(resp);
    return;
  }

  // 构建推送 ETF 列表
  let pushEtfs: PushEtf[];
  let signalDate: string;
  let marketTag: string;

  if (isDbAvailable()) {
    const calcDate = getLatestCalcDate()!;
    const result = buildTop5Result(calcDate);
    if (result) {
      pushEtfs = result.top5_etfs.map((e) => ({
        code: e.code,
        name: e.name,
        score: e.score,
        sector: e.sector,
      }));
      signalDate = result.signal_date;
      marketTag = result.market_tag;
    } else {
      pushEtfs = mockPushEtfs;
      signalDate = '2026-05-25';
      marketTag = '[default] 谨慎参与';
    }
  } else {
    pushEtfs = mockPushEtfs;
    signalDate = '2026-05-25';
    marketTag = '[default] 谨慎参与';
  }

  // 构建推送消息体
  const message: PushMessageBody = {
    title: '早盘宝每日关注',
    etfs: pushEtfs,
    signal_date: signalDate,
    market_tag: marketTag,
    generated_at: new Date().toISOString(),
  };

  // 模拟推送：所有用户视为成功
  const delivered = subscribers.length;
  const failed = 0;

  const resp: PushTriggerResponse = {
    status: 'ok',
    message: `推送完成：成功 ${delivered}，失败 ${failed}`,
    delivered_count: delivered,
    failed_count: failed,
  };
  res.json(resp);
});

export default router;
