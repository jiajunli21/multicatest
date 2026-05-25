import { Router, Request, Response } from 'express';
import { mockHomeResponse } from '../__mocks__';
import { isDbAvailable } from '../data/db';
import { buildTop5Result, getLatestCalcDate } from '../data/repository';

const router = Router();

/**
 * IA-001: C端早盘宝首页数据
 * GET /api/v1/morning-report/home
 *
 * 返回当日ETF分数Top5、赛道分布、信号日、市场标签
 * Phase 2: 优先读取 SQLite 真实计算数据，[mock] 兜底
 */
router.get('/home', (_req: Request, res: Response) => {
  if (isDbAvailable()) {
    const calcDate = getLatestCalcDate()!;
    const result = buildTop5Result(calcDate);
    if (result) {
      res.json(result);
      return;
    }
  }
  // [mock] 降级兜底
  res.json(mockHomeResponse);
});

export default router;
