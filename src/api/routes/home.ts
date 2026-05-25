import { Router, Request, Response } from 'express';
import { mockHomeResponse } from '../__mocks__';

const router = Router();

/**
 * IA-001: C端早盘宝首页数据
 * GET /api/v1/morning-report/home
 *
 * 返回当日ETF分数Top5、赛道分布、信号日、市场标签
 * Phase 1: ETF分数使用 [mock] 数据，赛道和标签 [mock]
 * Phase 2: 桥接真实计算数据
 */
router.get('/home', (_req: Request, res: Response) => {
  // [mock] Phase 1 返回 Mock 数据
  // Phase 2 替换为真实数据查询
  res.json(mockHomeResponse);
});

export default router;
