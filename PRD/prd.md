# Redis 计数限流器 — 产品需求文档 (PRD)

## 1. 概述

基于 Redis 原子计数器实现的 API 限流器，用于控制单个用户对系统的访问频率。

## 2. 核心逻辑

使用 Redis `INCR` 指令进行计数：

- `INCR` 是 Redis 原子操作，保证并发场景下计数准确
- 每次请求到达时，对对应 Key 执行 `INCR`
- 首次 `INCR` 返回 1 时，设置 Key 的 TTL 为 60 秒
- 若返回值超过阈值，拒绝请求并返回 HTTP 429

## 3. 限制规则

- **频率限制**：每个 user_id 在 1 分钟内最多访问 **100 次**
- **时间窗口**：固定窗口，60 秒后自动重置
- **超出处理**：返回 HTTP 429 Too Many Requests

## 4. Key 设计规范

- **Key 格式**：`limit:user_id:<uid>`
- **示例**：`limit:user_id:12345`
- **TTL**：60 秒（通过 `EXPIRE` 在首次 INCR 时设置）

## 5. 参考流程

```
1. INCR limit:user_id:<uid>
2. if result == 1 → EXPIRE limit:user_id:<uid> 60
3. if result > 100 → reject (HTTP 429)
4. else → allow
```
