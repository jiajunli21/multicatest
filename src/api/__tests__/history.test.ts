import request from 'supertest';
import app from '../../index';

describe('IA-003: GET /api/v1/morning-report/history', () => {
  it('应返回 history 数组', async () => {
    const res = await request(app).get('/api/v1/morning-report/history');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('history');
    expect(Array.isArray(res.body.history)).toBe(true);
  });

  it('history 每项应包含 date 和 etfs', async () => {
    const res = await request(app).get('/api/v1/morning-report/history');
    if (res.body.history.length > 0) {
      const day = res.body.history[0];
      expect(day).toHaveProperty('date');
      expect(day).toHaveProperty('etfs');
      expect(Array.isArray(day.etfs)).toBe(true);
    }
  });

  it('etf 应包含 code, name, signal_3d_return, current_return', async () => {
    const res = await request(app).get('/api/v1/morning-report/history');
    if (res.body.history.length > 0 && res.body.history[0].etfs.length > 0) {
      const etf = res.body.history[0].etfs[0];
      expect(etf).toHaveProperty('code');
      expect(etf).toHaveProperty('name');
      expect(etf).toHaveProperty('signal_3d_return');
      expect(etf).toHaveProperty('current_return');
    }
  });

  it('支持按 date 查询', async () => {
    const res = await request(app).get('/api/v1/morning-report/history?date=2026-05-22');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body.history)).toBe(true);
  });

  it('不存在的日期返回空数组', async () => {
    const res = await request(app).get('/api/v1/morning-report/history?date=2020-01-01');
    expect(res.status).toBe(200);
    expect(res.body.history).toEqual([]);
  });
});
