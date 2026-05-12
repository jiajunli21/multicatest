# 任务列表 — Redis 计数限流器

## 待办事项

- [x] 实现基础限流逻辑 (Logic Builder 认领)
  - 使用 Redis `INCR` 指令实现计数
  - Key 格式为 `limit:user_id:<uid>`
  - 超过阈值（100 次/分钟）返回 HTTP 429

- [ ] 检查并实现 Redis TTL 过期逻辑 (SRE/QA 认领)
  - 确保 Key 在首次创建时正确设置 60 秒 TTL
  - 验证 TTL 过期后计数器正确重置
  - 边界测试：并发请求下的 INCR + EXPIRE 原子性
