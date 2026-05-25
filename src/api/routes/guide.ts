import { Router, Request, Response } from 'express';
import { mockGuideContent } from '../__mocks__';

const router = Router();

/**
 * IA-004: 指南内容
 * GET /api/v1/morning-report/guide
 *
 * 返回运营配置的指南内容
 * Phase 1: [mock] 返回预设 Mock 指南内容
 * Phase 2: 桥接运营配置读取
 */
router.get('/guide', (_req: Request, res: Response) => {
  // [mock] Phase 1 返回 Mock 指南
  res.json({
    guide: {
      content: mockGuideContent,
      update_time: new Date().toISOString(),
    },
  });
});

export default router;
