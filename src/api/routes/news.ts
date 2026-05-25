import { Router, Request, Response } from 'express';
import { query, validationResult } from 'express-validator';
import { mockNewsList, mockNewsTotal } from '../__mocks__';
import { ApiError, EmptyResponse } from '../types';

const router = Router();

/**
 * IA-002: C端资讯过滤
 * GET /api/v1/morning-report/news
 *
 * 返回早盘宝相关资讯列表
 * Phase 1: [mock] 返回预设 Mock 资讯数据
 * Phase 2: 桥接真实资讯接口
 */
router.get(
  '/news',
  [
    query('limit').optional().isInt({ min: 1, max: 50 }).toInt(),
    query('offset').optional().isInt({ min: 0 }).toInt(),
  ],
  (req: Request, res: Response) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      const err: ApiError = { error: '参数校验失败', code: 'INVALID_PARAMS', detail: JSON.stringify(errors.array()) };
      res.status(400).json(err);
      return;
    }

    const limit = req.query.limit ? Number(req.query.limit) : 10;
    const offset = req.query.offset ? Number(req.query.offset) : 0;

    // [mock] 分页切片
    const paged = mockNewsList.slice(offset, offset + limit);
    res.json({ news: paged, total: mockNewsTotal });
  },
);

export default router;
