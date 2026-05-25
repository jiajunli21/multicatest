import { Router, Request, Response } from 'express';
import { query, validationResult } from 'express-validator';
import { mockHistory } from '../__mocks__';
import { ApiError } from '../types';

const router = Router();

/**
 * IA-003: C端历史表现
 * GET /api/v1/morning-report/history
 *
 * 返回历史日期推送的5个ETF及涨幅
 * Phase 1: [mock] 返回预设 Mock 历史数据
 * Phase 2: 桥接真实历史数据（数据开发落库后）
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

    if (targetDate) {
      // 查找指定日期的历史记录
      const day = mockHistory.find((h) => h.date === targetDate);
      if (!day) {
        res.json({ history: [] });
        return;
      }
      res.json({ history: [day] });
    } else {
      // 无日期参数返回全部历史
      res.json({ history: mockHistory });
    }
  },
);

export default router;
