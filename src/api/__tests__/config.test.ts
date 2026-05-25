import request from 'supertest';
import app from '../../index';

describe('IA-008: GET /api/v1/morning-report/config/etf-list', () => {
  it('应返回 etf_list 数组', async () => {
    const res = await request(app).get('/api/v1/morning-report/config/etf-list');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('etf_list');
    expect(Array.isArray(res.body.etf_list)).toBe(true);
  });

  it('etf_list 中每项应包含 code 和 name', async () => {
    const res = await request(app).get('/api/v1/morning-report/config/etf-list');
    expect(res.body.etf_list.length).toBeGreaterThan(0);
    const item = res.body.etf_list[0];
    expect(item).toHaveProperty('code');
    expect(item).toHaveProperty('name');
  });
});
