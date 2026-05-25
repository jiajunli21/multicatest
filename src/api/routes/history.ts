import { Router, Request, Response } from 'express';
import { query, validationResult } from 'express-validator';
import { mockHistory } from '../__mocks__';
import { isDbAvailable } from '../data/db';
import { buildHistory, buildHistoryForDate } from '../data/repository';
import { ApiError } from '../types';

const router = Router();

/**
 * IA-003: C端历史表现
 * GET /api/v1/morning-report/history
 *
 * 返回历史日期推送的5个ETF及涨幅
 * Phase 2: 优先读取 SQLite 历史数据，[mock] 兜底
 */
router.get(
  '/history',
  [
    query('date').optional().isISO8601().withMessage('日期格式无效，需为 ISO-8601'),
  ],
  (req: Request, res: Response) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      const err: ApiError = { error: '参数校验失败', code: 'INVALID_PARAMS', detail: JSON.stringify(errors.array()) };
      res.status(400).json(err);
      return;
    }

    const targetDate = req.query.date as string | undefined;

    if (isDbAvailable()) {
      if (targetDate) {
        const day = buildHistoryForDate(targetDate);
        res.json({ history: day ? [day] : [] });
      } else {
        res.json({ history: buildHistory() });
      }
      return;
    }

    // [mock] 降级兜底
    if (targetDate) {
      const day = mockHistory.find((h) => h.date === targetDate);
      if (!day) {
        res.json({ history: [] });
        return;
      }
      res.json({ history: [day] });
    } else {
      res.json({ history: mockHistory });
    }
  },
);

export default router;
