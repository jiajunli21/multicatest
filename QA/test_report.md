# SRE/QA 审计报告 — Redis 限流器

**审计日期**: 2026-05-12
**审计人**: Agent C (SRE/QA)
**目标文件**: `src/limiter.py`

---

## 1. 漏洞发现

### 1.1 缺失 EXPIRE / TTL 逻辑

**严重级别**: 高危（内存泄露）

`src/limiter.py` 的 `RateLimiter.is_allowed()` 方法（第 15-18 行）在执行 `INCR` 后没有设置 `EXPIRE`：

```python
def is_allowed(self, user_id: str) -> bool:
    key = self._key(user_id)
    count = self._client.incr(key)
    return count <= self._threshold
```

**影响**: 每个限流 Key (`limit:user_id:<uid>`) 会被永久保留在 Redis 中，无法自动过期。随着用户量增长，Redis 内存将持续攀升，最终导致 OOM。

### 1.2 Key 格式验证

- PRD 要求: `limit:user_id:<uid>`
- 实际生成: `limit:user_id:{user_id}` (via `KEY_PREFIX = "limit:user_id"`)
- **结论**: ✅ 格式符合 PRD 规范

---

## 2. 修复方案

在 `INCR` 返回值为 1（首次请求）时，设置 60 秒 TTL：

```python
def is_allowed(self, user_id: str) -> bool:
    key = self._key(user_id)
    count = self._client.incr(key)
    if count == 1:
        self._client.expire(key, 60)
    return count <= self._threshold
```

**修复逻辑**: 当 `INCR` 返回 1 表示这是窗口期内的首次请求，此时对 Key 设置 `EXPIRE 60`。后续请求（`INCR` > 1）复用已有 Key，无需重复设置 TTL。60 秒后 Key 自动过期，计数器重置。

---

## 3. 测试建议

- [ ] 验证首次请求后 Key 存在且 TTL 为 60 秒
- [ ] 验证 TTL 过期后计数器归零
- [ ] 并发场景下 INCR + EXPIRE 的数据一致性（考虑使用 Lua 脚本原子化）
