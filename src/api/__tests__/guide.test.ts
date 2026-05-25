import request from 'supertest';
import app from '../../index';

describe('IA-004: GET /api/v1/morning-report/guide', () => {
  it('应返回 200 和 guide 对象', async () => {
    const res = await request(app).get('/api/v1/morning-report/guide');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('guide');
    expect(res.body.guide).toHaveProperty('content');
    expect(res.body.guide).toHaveProperty('update_time');
  });

  it('content 应为非空字符串', async () => {
    const res = await request(app).get('/api/v1/morning-report/guide');
    expect(typeof res.body.guide.content).toBe('string');
    expect(res.body.guide.content.length).toBeGreaterThan(0);
  });
});
