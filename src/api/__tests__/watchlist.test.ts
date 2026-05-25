import request from 'supertest';
import app from '../../index';

describe('IA-007: POST /api/v1/morning-report/watchlist/add', () => {
  it('正常请求应返回 ok 和 added_count', async () => {
    const res = await request(app)
      .post('/api/v1/morning-report/watchlist/add')
      .send({ user_id: 'test_user_wl' });
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body).toHaveProperty('added_count');
    expect(res.body).toHaveProperty('failed_list');
    expect(Array.isArray(res.body.failed_list)).toBe(true);
  });

  it('应支持 date 参数', async () => {
    const res = await request(app)
      .post('/api/v1/morning-report/watchlist/add')
      .send({ user_id: 'test_user_wl', date: '2026-05-22' });
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
  });

  it('缺少 user_id 应返回 400', async () => {
    const res = await request(app)
      .post('/api/v1/morning-report/watchlist/add')
      .send({});
    expect(res.status).toBe(400);
    expect(res.body.code).toBe('INVALID_PARAMS');
  });
});
