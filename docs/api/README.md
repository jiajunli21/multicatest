# 早盘宝 API 接口契约文档

> 版本: v1.0 | Phase 1 (接口契约先行) | 分支: 260525 | 准入: .multica/admission_check.md

## 状态标注说明

| 标注 | 含义 |
|------|------|
| `[verified]` | 已通过 fund-api-docs 或 fund-indic-search-test 验证 |
| `[mock]` | 当前使用 Mock 数据，Phase 2 替换 |
| `[default]` | 默认假设值，待确认后可能调整 |
| `[pending]` | 待后续确认 |

## 接口清单

| IA-ID | 接口 | 方法 | 路径 | 状态 |
|-------|------|------|------|------|
| IA-001 | 早盘宝首页数据 | GET | `/api/v1/morning-report/home` | [mock] 赛道/标签 |
| IA-002 | 资讯过滤 | GET | `/api/v1/morning-report/news` | [mock] |
| IA-003 | 历史表现 | GET | `/api/v1/morning-report/history` | [mock] |
| IA-004 | 指南内容 | GET | `/api/v1/morning-report/guide` | [mock] |
| IA-005 | 预警订阅 | POST | `/api/v1/morning-report/subscribe` | [default] 暂默认有权限 |
| IA-006 | 预警推送触发 | POST | `/api/v1/morning-report/push/trigger` | [default] 内部接口 |
| IA-007 | 一键加自选 | POST | `/api/v1/morning-report/watchlist/add` | [default] 暂仅验证结构 |
| IA-008 | 运营配置读取 | GET | `/api/v1/morning-report/config/etf-list` | [mock] 内部接口 |

## 通用约定

- 基础路径: `/api/v1/morning-report`
- 请求/响应格式: JSON (`Content-Type: application/json`)
- 编码: UTF-8
- 日期格式: ISO-8601 / YYYY-MM-DD
- 时间戳格式: ISO-8601 with timezone
- 权限标注 `[default]` 的接口暂默认有权限，真实权限规则待确认

## 通用错误码

| HTTP 状态码 | code | 说明 |
|-------------|------|------|
| 400 | `INVALID_PARAMS` | 请求参数校验失败 |
| 404 | `NOT_FOUND` | 路径不存在 |
| 500 | `INTERNAL_ERROR` | 服务内部错误 |

## 通用空态返回

```json
{
  "data": null,
  "message": "暂无数据"
}
```
