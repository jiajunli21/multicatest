import { Router, Request, Response } from 'express';
import { mockEtfConfig } from '../__mocks__';
import { isDbAvailable } from '../data/db';
import { getEtfScores, getLatestCalcDate } from '../data/repository';

const router = Router();

/**
 * IA-008: 运营配置读取
 * GET /api/v1/morning-report/config/etf-list
 *
 * 读取ETF计算样本配置（内部接口）
 * Phase 2: 优先从 SQLite 读取实际计算样本，[mock] 兜底
 */
router.get('/config/etf-list', (_req: Request, res: Response) => {
  if (isDbAvailable()) {
    const calcDate = getLatestCalcDate()!;
    const rows = getEtfScores(calcDate);
    const etfList = rows.map((r) => ({ code: r.etf_code, name: r.etf_name }));
    if (etfList.length > 0) {
      res.json({ etf_list: etfList });
      return;
    }
  }
  // [mock] 降级兜底
  res.json({ etf_list: mockEtfConfig });
});

export default router;
