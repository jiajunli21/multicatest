import request from 'supertest';
import app from '../../index';

describe('IA-002: GET /api/v1/morning-report/news', () => {
  it('默认分页应返回 news 列表和 total', async () => {
    const res = await request(app).get('/api/v1/morning-report/news');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('news');
    expect(res.body).toHaveProperty('total');
    expect(Array.isArray(res.body.news)).toBe(true);
  });

  it('news 每项应包含必要字段', async () => {
    const res = await request(app).get('/api/v1/morning-report/news');
    if (res.body.news.length > 0) {
      const item = res.body.news[0];
      expect(item).toHaveProperty('title');
      expect(item).toHaveProperty('summary');
      expect(item).toHaveProperty('time');
      expect(item).toHaveProperty('source');
      expect(item).toHaveProperty('url');
    }
  });

  it('应支持 limit 参数限制返回数量', async () => {
    const res = await request(app).get('/api/v1/morning-report/news?limit=2');
    expect(res.body.news.length).toBeLessThanOrEqual(2);
  });

  it('无效 limit 应返回 400', async () => {
    const res = await request(app).get('/api/v1/morning-report/news?limit=999');
    expect(res.status).toBe(400);
    expect(res.body.code).toBe('INVALID_PARAMS');
  });

  it('offset 应支持分页', async () => {
    const res = await request(app).get('/api/v1/morning-report/news?offset=2&limit=2');
    expect(res.status).toBe(200);
    expect(res.body.news.length).toBeLessThanOrEqual(2);
  });
});
