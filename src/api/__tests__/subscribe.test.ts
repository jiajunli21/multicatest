import request from 'supertest';
import app from '../../index';

describe('IA-005: POST /api/v1/morning-report/subscribe', () => {
  it('subscribe 应返回 ok', async () => {
    const res = await request(app)
      .post('/api/v1/morning-report/subscribe')
      .send({ action: 'subscribe', user_id: 'test_user_1' });
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body.message).toBe('订阅成功');
  });

  it('unsubscribe 应返回 ok', async () => {
    const res = await request(app)
      .post('/api/v1/morning-report/subscribe')
      .send({ action: 'unsubscribe', user_id: 'test_user_1' });
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body.message).toBe('已取消订阅');
  });

  it('重复 subscribe 应幂等', async () => {
    await request(app)
      .post('/api/v1/morning-report/subscribe')
      .send({ action: 'subscribe', user_id: 'test_user_2' });
    const res = await request(app)
      .post('/api/v1/morning-report/subscribe')
      .send({ action: 'subscribe', user_id: 'test_user_2' });
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
  });

  it('缺少 action 应返回 400', async () => {
    const res = await request(app)
      .post('/api/v1/morning-report/subscribe')
      .send({ user_id: 'test_user_1' });
    expect(res.status).toBe(400);
    expect(res.body.code).toBe('INVALID_PARAMS');
  });

  it('缺少 user_id 应返回 400', async () => {
    const res = await request(app)
      .post('/api/v1/morning-report/subscribe')
      .send({ action: 'subscribe' });
    expect(res.status).toBe(400);
    expect(res.body.code).toBe('INVALID_PARAMS');
  });

  it('无效 action 应返回 400', async () => {
    const res = await request(app)
      .post('/api/v1/morning-report/subscribe')
      .send({ action: 'invalid', user_id: 'test_user_1' });
    expect(res.status).toBe(400);
    expect(res.body.code).toBe('INVALID_PARAMS');
  });

  it('取消未订阅的用户应幂等', async () => {
    const res = await request(app)
      .post('/api/v1/morning-report/subscribe')
      .send({ action: 'unsubscribe', user_id: 'nonexistent_user' });
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
  });
});
