import request from 'supertest';
import app from '../../index';

describe('IA-006: POST /api/v1/morning-report/push/trigger', () => {
  it('无订阅用户时应返回 no_subscribers', async () => {
    const res = await request(app).post('/api/v1/morning-report/push/trigger');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('no_subscribers');
    expect(res.body.delivered_count).toBe(0);
    expect(res.body.failed_count).toBe(0);
  });

  it('响应应包含必要字段', async () => {
    const res = await request(app).post('/api/v1/morning-report/push/trigger');
    expect(res.body).toHaveProperty('status');
    expect(res.body).toHaveProperty('message');
    expect(res.body).toHaveProperty('delivered_count');
    expect(res.body).toHaveProperty('failed_count');
  });

  it('有订阅用户时应推送成功', async () => {
    // 先订阅一个用户
    await request(app)
      .post('/api/v1/morning-report/subscribe')
      .send({ action: 'subscribe', user_id: 'push_test_user' });

    const res = await request(app).post('/api/v1/morning-report/push/trigger');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body.delivered_count).toBeGreaterThan(0);
  });
});
