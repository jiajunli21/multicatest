import { Router, Request, Response } from 'express';
import { mockEtfConfig } from '../__mocks__';

const router = Router();

/**
 * IA-008: 运营配置读取
 * GET /api/v1/morning-report/config/etf-list
 *
 * 读取ETF计算样本配置（内部接口）
 * Phase 1: [mock] 返回 Mock ETF 样本列表
 * Phase 2: 桥接运营配置
 */
router.get('/config/etf-list', (_req: Request, res: Response) => {
  // [mock] Phase 1 返回 Mock 配置
  res.json({ etf_list: mockEtfConfig });
});

export default router;
