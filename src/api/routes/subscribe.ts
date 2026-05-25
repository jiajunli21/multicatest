import { Router, Request, Response } from 'express';
import { body, validationResult } from 'express-validator';
import { mockSubscriptionStore } from '../__mocks__';
import { SubscribeRequest, SubscribeResponse, ApiError } from '../types';

const router = Router();

/**
 * IA-005: 预警订阅
 * POST /api/v1/morning-report/subscribe
 *
 * 用户订阅/取消订阅早盘宝推送
 * [default] 暂默认有权限
 * 幂等设计：重复 subscribe/unsubscribe 返回 ok
 */
router.post(
  '/subscribe',
  [
    body('action').isIn(['subscribe', 'unsubscribe']).withMessage('action 必须为 subscribe 或 unsubscribe'),
    body('user_id').isString().notEmpty().withMessage('user_id 不能为空'),
  ],
  (req: Request, res: Response) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      const err: ApiError = { error: '参数校验失败', code: 'INVALID_PARAMS', detail: JSON.stringify(errors.array()) };
      res.status(400).json(err);
      return;
    }

    const { action, user_id }: SubscribeRequest = req.body;

    // [default] 暂默认有权限，不校验用户身份

    try {
      if (action === 'subscribe') {
        mockSubscriptionStore.set(user_id, true);
        const resp: SubscribeResponse = { status: 'ok', message: '订阅成功' };
        res.json(resp);
      } else {
        mockSubscriptionStore.delete(user_id);
        const resp: SubscribeResponse = { status: 'ok', message: '已取消订阅' };
        res.json(resp);
      }
    } catch {
      const err: ApiError = { error: '服务内部错误', code: 'INTERNAL_ERROR' };
      res.status(500).json(err);
    }
  },
);

export default router;
