import { Router, Request, Response } from 'express';
import { body, validationResult } from 'express-validator';
import { mockTop5Etfs } from '../__mocks__';
import { WatchlistAddResponse, ApiError } from '../types';

const router = Router();

/**
 * IA-007: 一键加自选
 * POST /api/v1/morning-report/watchlist/add
 *
 * 将当日早盘宝ETF加到自选分组"YYYY-MM-DD早盘宝"
 * [default] 暂默认有权限
 * 幂等设计：重复添加同一ETF返回 ok，不计入 added_count
 */
router.post(
  '/watchlist/add',
  [
    body('user_id').isString().notEmpty().withMessage('user_id 不能为空'),
    body('date').optional().isISO8601().withMessage('日期格式无效'),
  ],
  (req: Request, res: Response) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      const err: ApiError = { error: '参数校验失败', code: 'INVALID_PARAMS', detail: JSON.stringify(errors.array()) };
      res.status(400).json(err);
      return;
    }

    const { user_id } = req.body;

    // [default] 暂默认有权限，不校验用户身份
    // [mock] 暂仅验证结构，不实际调用自选接口

    try {
      // 模拟：将当日 Top5 ETF 添加到自选分组
      const addedCount = mockTop5Etfs.length;
      const failedList: { code: string; reason: string }[] = [];

      const resp: WatchlistAddResponse = {
        status: 'ok',
        added_count: addedCount,
        failed_list: failedList,
      };
      res.json(resp);
    } catch {
      const err: ApiError = { error: '服务内部错误', code: 'INTERNAL_ERROR' };
      res.status(500).json(err);
    }
  },
);

export default router;
