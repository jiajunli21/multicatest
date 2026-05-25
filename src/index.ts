import express from 'express';
import homeRouter from './api/routes/home';
import newsRouter from './api/routes/news';
import historyRouter from './api/routes/history';
import guideRouter from './api/routes/guide';
import subscribeRouter from './api/routes/subscribe';
import pushRouter from './api/routes/push';
import watchlistRouter from './api/routes/watchlist';
import configRouter from './api/routes/config';

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(express.json());

// 路由注册
// IA-001: 早盘宝首页数据
app.use('/api/v1/morning-report', homeRouter);
// IA-002: 资讯过滤
app.use('/api/v1/morning-report', newsRouter);
// IA-003: 历史表现
app.use('/api/v1/morning-report', historyRouter);
// IA-004: 指南内容
app.use('/api/v1/morning-report', guideRouter);
// IA-005: 预警订阅
app.use('/api/v1/morning-report', subscribeRouter);
// IA-006: 预警推送触发
app.use('/api/v1/morning-report', pushRouter);
// IA-007: 一键加自选
app.use('/api/v1/morning-report', watchlistRouter);
// IA-008: 运营配置读取
app.use('/api/v1/morning-report', configRouter);

// 健康检查
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 404
app.use((_req, res) => {
  res.status(404).json({ error: 'Not Found', code: 'NOT_FOUND' });
});

// 全局错误处理
app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error('[API Error]', err.message);
  res.status(500).json({ error: '服务内部错误', code: 'INTERNAL_ERROR' });
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`早盘宝 API 服务已启动: http://localhost:${PORT}`);
  });
}

export default app;
