import { Router, Response } from 'express';
import { mockPushEtfs, mockSubscriptionStore } from '../__mocks__';
import { PushMessageBody, PushTriggerResponse } from '../types';

const router = Router();

/**
 * IA-006: 预警推送触发
 * POST /api/v1/morning-report/push/trigger
 *
 * 数据计算完成后推送消息给已订阅用户（内部触发）
 * [default] 暂默认有权限
 * Phase 1: 返回推送目标摘要，不实际推送
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

  // 构建推送消息体
  const message: PushMessageBody = {
    title: '[mock] 早盘宝每日关注',
    etfs: mockPushEtfs,
    signal_date: '2026-05-25',
    market_tag: '[default] 谨慎参与',
    generated_at: new Date().toISOString(),
  };

  // [mock] 模拟推送：所有用户视为成功
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
