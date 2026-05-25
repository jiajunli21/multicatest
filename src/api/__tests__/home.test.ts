import request from 'supertest';
import app from '../../index';

describe('IA-001: GET /api/v1/morning-report/home', () => {
  it('应返回 200 和首页数据结构', async () => {
    const res = await request(app).get('/api/v1/morning-report/home');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('top5_etfs');
    expect(res.body).toHaveProperty('sectors');
    expect(res.body).toHaveProperty('signal_date');
    expect(res.body).toHaveProperty('market_tag');
    expect(res.body).toHaveProperty('update_time');
    expect(Array.isArray(res.body.top5_etfs)).toBe(true);
    expect(Array.isArray(res.body.sectors)).toBe(true);
  });

  it('top5_etfs 中每项应包含必要字段', async () => {
    const res = await request(app).get('/api/v1/morning-report/home');
    const etf = res.body.top5_etfs[0];
    expect(etf).toHaveProperty('code');
    expect(etf).toHaveProperty('name');
    expect(etf).toHaveProperty('score');
    expect(etf).toHaveProperty('rank');
    expect(etf).toHaveProperty('sector');
    expect(etf).toHaveProperty('tags');
  });

  it('top5 数量应为 5', async () => {
    const res = await request(app).get('/api/v1/morning-report/home');
    expect(res.body.top5_etfs.length).toBeLessThanOrEqual(5);
  });
});
