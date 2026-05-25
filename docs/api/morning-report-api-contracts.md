# 早盘宝 API 接口契约

> **版本**: v1.0-Phase1（契约先行）
> **状态**: 待审核冻结
> **方案引用**: `.multica/admission_check.md` (Round 2 / 2026-05-25)
> **分支**: `260525` / commit: `81c0c9e`
> **状态分类**: `[verified]` / `[mock]` / `[default]` / `[pending]`

---

## 通用约定

### Base URL

```
https://api.example.com/api/v1/morning-report
```

> 实际域名由部署环境决定，契约中以相对路径 `/api/v1/morning-report/...` 表述。

### 通用响应结构

```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "timestamp": 1716638400
}
```

### 通用错误码

| code | message | 说明 |
|------|---------|------|
| 0 | success | 成功 |
| 1001 | invalid parameter | 参数校验失败 |
| 1002 | data not ready | 数据未就绪（计算未完成） |
| 1003 | empty data | 数据为空（正常空态） |
| 1004 | internal error | 服务内部错误 |
| 2001 | subscribe failed | 订阅失败 |
| 2002 | unsubscribe failed | 取消订阅失败 |
| 2003 | push failed | 推送失败 |
| 3001 | watchlist add failed | 加自选失败 |
| 3002 | watchlist partial failed | 部分加自选失败 |

### 通用约定

- 时间字段统一使用 Unix 秒级时间戳（UTC）
- ETF 代码格式：`{market}:{code}`，如 `17:510050`
- 金额单位：元（CNY）
- 百分比字段：0-1 之间的小数或百分数字符串，以具体字段说明为准
- 空列表返回 `[]`，不返回 `null`

---

## IA-001: 早盘宝首页数据接口 `[default]` + `[mock]`

### 接口概览

- **Method**: `GET`
- **Path**: `/api/v1/morning-report/home`
- **说明**: 返回当日 ETF 分数 Top5、赛道分布、样本信号日、市场标签、个基标签
- **状态**: 综合评分/排名 [default]（公式和数据口径为默认假设），赛道/标签 [mock]，信号日/市场标签 [default]

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `date` | string | 否 | 最新计算日 | 日期，格式 `YYYY-MM-DD`，如 `2026-05-25` |

### 返回数据

| 字段 | 类型 | 说明 | 状态 |
|------|------|------|------|
| `top5_etfs` | array | Top5 ETF 列表 | [default] |
| `top5_etfs[].code` | string | ETF 代码，格式 `17:510050` | [default] |
| `top5_etfs[].name` | string | ETF 名称 | [default] |
| `top5_etfs[].score` | number | ETF 综合评分（0-1，保留2位小数） | [default] |
| `top5_etfs[].rank` | integer | 排名（1-5） | [default] |
| `top5_etfs[].sector` | string | 对应三级赛道名称 | [mock] |
| `top5_etfs[].tags` | array | 个基标签列表 | [mock] |
| `sectors` | array | 赛道分布（最多5个） | [mock] |
| `sectors[].name` | string | 赛道名称 | [mock] |
| `sectors[].etfs` | array | 该赛道下的 ETF 简要列表 | [mock] |
| `sectors[].etfs[].code` | string | ETF 代码 | [mock] |
| `sectors[].etfs[].name` | string | ETF 名称 | [mock] |
| `sectors[].etfs[].score` | number | ETF 评分 | [default] |
| `signal_date` | string | 样本信号日 `YYYY-MM-DD` | [default] |
| `market_tag` | string | 市场标签：`"谨慎参与"` 或 `"积极参与"` | [default] |
| `update_time` | integer | 数据更新时间（Unix 秒级时间戳） | [default] |

### 空态/错误态

- 数据未就绪：返回 `code=1002, data=null`
- 样本不足（< 5 个 ETF）：按实际数量返回，`insufficient_sample=true`
- 无有效数据：返回空列表 `top5_etfs=[]`，`code=1003`

### 权限

无需登录 [default]

### 示例请求

```bash
curl "https://api.example.com/api/v1/morning-report/home?date=2026-05-25"
```

### 示例响应

见 `docs/api/examples/ia-001-home.json`

---

## IA-002: 资讯过滤接口 `[mock]`

### 接口概览

- **Method**: `GET`
- **Path**: `/api/v1/morning-report/news`
- **说明**: 返回早盘宝相关资讯列表。本轮使用 Mock 数据，真实资讯部门接口待后续接入
- **状态**: [mock]

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `limit` | integer | 否 | 20 | 每页条数，最大 50 |
| `offset` | integer | 否 | 0 | 偏移量 |

### 返回数据

| 字段 | 类型 | 说明 | 状态 |
|------|------|------|------|
| `total` | integer | 总条数 | [mock] |
| `news` | array | 资讯列表 | [mock] |
| `news[].title` | string | 资讯标题 | [mock] |
| `news[].summary` | string | 资讯摘要 | [mock] |
| `news[].time` | integer | 发布时间（Unix 秒级时间戳） | [mock] |
| `news[].source` | string | 来源 | [mock] |
| `news[].url` | string | 资讯链接 | [mock] |

### 空态/错误态

- 无资讯：返回 `news=[]`, `total=0`, `code=1003`

### 权限

无需登录 [default]

### 示例请求

```bash
curl "https://api.example.com/api/v1/morning-report/news?limit=10&offset=0"
```

### 示例响应

见 `docs/api/examples/ia-002-news.json`

---

## IA-003: 历史表现接口 `[default]`

### 接口概览

- **Method**: `GET`
- **Path**: `/api/v1/morning-report/history`
- **说明**: 返回历史早盘宝推送数据，包含每个日期推送的 5 个 ETF 及涨幅
- **状态**: [default]（暂按自然日模拟交易日口径）

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `date` | string | 否 | 最新 T-3 | 查询日期 `YYYY-MM-DD`。最晚展示 T-3 交易日数据 |
| `limit` | integer | 否 | 30 | 返回条数，最大 90 |

### 返回数据

| 字段 | 类型 | 说明 | 状态 |
|------|------|------|------|
| `history` | array | 历史记录列表 | [default] |
| `history[].date` | string | 信号日 `YYYY-MM-DD` | [default] |
| `history[].etfs` | array | 当日推送的 ETF 列表 | [default] |
| `history[].etfs[].code` | string | ETF 代码 | [default] |
| `history[].etfs[].name` | string | ETF 名称 | [default] |
| `history[].etfs[].score` | number | 当日评分 | [default] |
| `history[].etfs[].signal_3d_return` | string | 信号后3日涨幅。不足3交易日返回 `"--"` | [default] |
| `history[].etfs[].current_return` | string | 当前涨幅（实时） | [default] |

### 空态/错误态

- 无历史数据：返回 `history=[]`, `code=1003`
- 日期超出范围（晚于 T-3）：返回 `code=1001, message="date too recent"`

### 权限

无需登录 [default]

### 示例请求

```bash
curl "https://api.example.com/api/v1/morning-report/history?date=2026-05-22&limit=10"
```

### 示例响应

见 `docs/api/examples/ia-003-history.json`

---

## IA-004: 指南内容接口 `[mock]`

### 接口概览

- **Method**: `GET`
- **Path**: `/api/v1/morning-report/guide`
- **说明**: 返回运营配置的早盘宝指南内容。本轮使用 Mock 数据
- **状态**: [mock]

### 请求参数

无

### 返回数据

| 字段 | 类型 | 说明 | 状态 |
|------|------|------|------|
| `guide` | object | 指南内容 | [mock] |
| `guide.content` | string | 指南正文（支持 Markdown） | [mock] |
| `guide.update_time` | integer | 最后更新时间（Unix 秒级时间戳） | [mock] |

### 空态/错误态

- 无配置：返回 `guide=null`, `code=1003`

### 权限

无需登录 [default]

### 示例请求

```bash
curl "https://api.example.com/api/v1/morning-report/guide"
```

### 示例响应

见 `docs/api/examples/ia-004-guide.json`

---

## IA-005: 预警订阅接口 `[default]`

### 接口概览

- **Method**: `POST`
- **Path**: `/api/v1/morning-report/subscribe`
- **说明**: 用户订阅/取消订阅早盘宝推送
- **幂等**: 重复订阅返回成功（状态不变）；重复取消订阅返回成功
- **状态**: [default]（暂默认有权限）

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `user_id` | string | 是 | 用户 ID |
| `action` | string | 是 | `"subscribe"` 或 `"unsubscribe"` |

### 返回数据

| 字段 | 类型 | 说明 | 状态 |
|------|------|------|------|
| `status` | string | 操作结果：`"subscribed"` / `"unsubscribed"` / `"unchanged"` | [default] |
| `message` | string | 可读描述 | [default] |

### 错误态

- `user_id` 为空：`code=1001, message="user_id required"`
- `action` 非法值：`code=1001, message="action must be subscribe or unsubscribe"`
- 内部错误：`code=2001`（订阅失败）/ `code=2002`（取消订阅失败）

### 权限

暂默认有权限 [default]。后续需接入真实权限判断 [pending]

### 示例请求

```bash
curl -X POST "https://api.example.com/api/v1/morning-report/subscribe" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_12345", "action": "subscribe"}'
```

### 示例响应

见 `docs/api/examples/ia-005-subscribe.json`

---

## IA-006: 预警推送触发 `[default]`

### 接口概览

- **Method**: `POST`
- **Path**: `/api/v1/morning-report/push/trigger` (内部接口)
- **说明**: 数据计算完成后，触发向已订阅用户推送消息。非 C 端直接调用，由定时任务/内部系统触发
- **状态**: [default]（暂默认有权限，推送模板包含具体 ETF 名称和 code）

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `signal_date` | string | 是 | 信号日 `YYYY-MM-DD` |

### 返回数据

| 字段 | 类型 | 说明 | 状态 |
|------|------|------|------|
| `status` | string | 推送结果：`"completed"` / `"partial"` | [default] |
| `total_subscribers` | integer | 总订阅用户数 | [default] |
| `success_count` | integer | 成功推送数 | [default] |
| `failed_count` | integer | 失败推送数 | [default] |
| `failed_users` | array | 失败用户列表（仅含前100条） | [default] |

### 推送消息体模板

```json
{
  "title": "早盘宝 · {signal_date}",
  "body": "今日关注：{etf_1_name}({etf_1_code})、{etf_2_name}({etf_2_code})、{etf_3_name}({etf_3_code})、{etf_4_name}({etf_4_code})、{etf_5_name}({etf_5_code})",
  "market_tag": "{market_tag}",
  "data": {
    "top5": [ ... ]
  }
}
```

> 模板由运营编辑，预留 5 个 ETF 名称和 code 占位。本轮暂默认有权限，模板包含具体 ETF。[pending] 权限判断后续确认

### 错误态

- 无订阅用户：`status="completed"`, `total_subscribers=0`（正常，不推送）
- 推送失败：记录日志 + 重试；返回 `status="partial"` 及失败列表

### 示例响应

见 `docs/api/examples/ia-006-push.json`

---

## IA-007: 一键加自选接口 `[pending]`

### 接口概览

- **Method**: `POST`
- **Path**: `/api/v1/morning-report/add-to-watchlist`
- **说明**: 将当日早盘宝推荐 ETF 一键添加到"年月日早盘宝"自选分组
- **幂等**: 重复调用对已添加的 ETF 返回成功（不重复添加）
- **状态**: [pending]（本轮仅验证接口结构和幂等设计，不接入真实自选）

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `user_id` | string | 是 | 用户 ID |
| `date` | string | 否 | 日期 `YYYY-MM-DD`，默认当日 |

### 返回数据

| 字段 | 类型 | 说明 | 状态 |
|------|------|------|------|
| `status` | string | 操作结果：`"success"` / `"partial"` | [pending] |
| `group_name` | string | 自选分组名，如 `"20260525早盘宝"` | [pending] |
| `added_count` | integer | 成功添加数量 | [pending] |
| `total_count` | integer | 待添加总数 | [pending] |
| `failed_list` | array | 添加失败的 ETF 列表 | [pending] |
| `failed_list[].code` | string | ETF 代码 | [pending] |
| `failed_list[].reason` | string | 失败原因 | [pending] |

### 幂等规则

- 同一用户、同一日期、同一 ETF：多次添加只记录一次，返回 `"success"`
- 已存在同名分组：追加到已有分组，不创建重复分组
- 分组命名格式：`YYYYMMDD早盘宝`

### 错误态

- 全部失败：`status="failed"`, `code=3001`
- 部分失败：`status="partial"`, `code=3002`，`failed_list` 列出失败项
- 无早盘宝数据：`code=1002, message="no morning report data for this date"`

### 权限

暂默认有权限 [default]。真实产品权限判断待后续确认 [pending]

### 示例请求

```bash
curl -X POST "https://api.example.com/api/v1/morning-report/add-to-watchlist" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_12345", "date": "2026-05-25"}'
```

### 示例响应

见 `docs/api/examples/ia-007-watchlist.json`

---

## IA-008: 运营配置读取（ETF 样本配置） `[mock]`

### 接口概览

- **Method**: `GET`
- **Path**: `/api/v1/morning-report/config/etf-samples`
- **说明**: 返回参与早盘宝计算的 ETF 样本列表。本轮使用 Mock 配置
- **状态**: [mock]

### 请求参数

无

### 返回数据

| 字段 | 类型 | 说明 | 状态 |
|------|------|------|------|
| `total` | integer | ETF 总数 | [mock] |
| `etf_list` | array | ETF 样本列表 | [mock] |
| `etf_list[].code` | string | ETF 代码，格式 `17:510050` | [mock] |
| `etf_list[].name` | string | ETF 名称 | [mock] |
| `update_time` | integer | 配置更新时间 | [mock] |

### 空态/错误态

- 无配置：返回 `etf_list=[]`, `total=0`, `code=1003`

### 权限

内部接口，不对外暴露 [default]

### 示例请求

```bash
curl "https://api.example.com/api/v1/morning-report/config/etf-samples"
```

### 示例响应

见 `docs/api/examples/ia-008-config.json`

---

## 接口清单汇总

| Row ID | 接口 | Method | Path | 状态 |
|--------|------|--------|------|------|
| IA-001 | 早盘宝首页数据 | GET | `/api/v1/morning-report/home` | [default]+[mock] |
| IA-002 | 资讯过滤 | GET | `/api/v1/morning-report/news` | [mock] |
| IA-003 | 历史表现 | GET | `/api/v1/morning-report/history` | [default] |
| IA-004 | 指南内容 | GET | `/api/v1/morning-report/guide` | [mock] |
| IA-005 | 预警订阅 | POST | `/api/v1/morning-report/subscribe` | [default] |
| IA-006 | 预警推送触发 | POST | `/api/v1/morning-report/push/trigger` | [default] |
| IA-007 | 一键加自选 | POST | `/api/v1/morning-report/add-to-watchlist` | [pending] |
| IA-008 | 运营配置读取 | GET | `/api/v1/morning-report/config/etf-samples` | [mock] |

---

## 兼容性说明

- 所有接口为全新建设，无历史兼容性负担
- IA-001~IA-004 暂无破坏性变更风险（契约先行阶段）
- IA-005~IA-007 涉及用户状态变更（订阅/自选），后续权限规则变更可能影响请求参数和返回结构
- IA-007 仅验证接口结构和幂等设计，后续需对接真实自选服务

---

## 待确认项 `[pending]`

| # | 事项 | 影响接口 | 负责人 |
|---|------|----------|--------|
| 1 | 推送权限判断规则 | IA-006 | 姜文迪 |
| 2 | 一键加自选最终规则（分组命名、权限、部分失败处理） | IA-007 | 黄运锞 |
| 3 | 运营平台 ETF 样本配置真实入口 | IA-008 | 黄运锞 |
| 4 | 真实资讯部门接口接入 | IA-002 | 王奕乾 |
| 5 | 最终交易日口径 | IA-001/IA-003 | 黄运锞 |
| 6 | 资讯接口 hqcode 映射方式 | IA-002 | — |
