# 早盘宝数据层 — 接口开发 Agent 读取说明

## 状态分类

| 标记 | 说明 |
|------|------|
| `[verified]` | 已通过真实数据/接口验证 |
| `[mock]` | 使用 Mock 数据 |
| `[default]` | 基于默认假设，非最终口径 |
| `[pending]` | 待后续负责人确认 |

## 数据读取入口

### 1. 每日计算流程

入口模块：`src/morning_report/scheduler.py`
- `run_daily_calculation(calc_date)` — 执行全流程计算并返回 `Top5Result`
- `get_latest_result(calc_date)` — 获取最新结果（缓存 → DB → 计算）

### 2. 数据库访问

入口模块：`src/morning_report/data/repository.py`

```python
from src.morning_report.data.repository import get_top5_scores, get_etf_scores, get_historical_records

# 获取 Top5
top5 = get_top5_scores(date.today())

# 获取全部评分
scores = get_etf_scores(date.today())

# 获取历史记录
history = get_historical_records(start_date=..., end_date=...)
```

数据库文件：`morning_report.db` (SQLite)

## 数据对象和字段说明

### ETFScore（ETF 综合评分）

| 字段名 | 字段类型 | 单位 | 精度 | 说明 | 状态 |
|--------|---------|------|------|------|------|
| `etf_code` | str | — | — | ETF 代码 | [verified] |
| `etf_name` | str | — | — | ETF 名称 | [mock] |
| `calc_date` | date | — | — | 计算日期 (T 日) | [default] |
| `heat_rank_score` | float | 无 | 2 位小数 | 热度排名分数 (权重 50%) | [mock] |
| `momentum_rank_score` | float | 无 | 2 位小数 | 动量排名分数 (权重 35%) | [default] |
| `liquidity_rank_score` | float | 无 | 2 位小数 | 流动性排名分数 (权重 10%) | [default] |
| `low_vol_rank_score` | float | 无 | 2 位小数 | 低波排名分数 (权重 5%) | [default] |
| `composite_score` | float | 无 | 2 位小数 | 综合评分 = 加权求和 | [default] |
| `rank` | int | — | — | 综合排名 (1-based, DESC) | [default] |
| `sector` | str | — | — | 三级赛道名称 | [mock] |
| `tags` | list[str] | — | — | 个基标签列表 | [mock] |
| `market_tag` | str | — | — | "谨慎参与" / "积极参与" | [default] |
| `status` | str | — | — | "success" / "insufficient_sample" / "not_calculable" | [default] |

### Top5Result（Top5 推荐结果）

| 字段名 | 字段类型 | 说明 | 状态 |
|--------|---------|------|------|
| `top_etfs` | list[ETFScore] | Top5 ETF 列表（最多 5 个） | [default] |
| `sectors` | list[dict] | 赛道分布 `[{name, etfs: [{code, name, score}]}]` | [mock] |
| `signal_date` | date | 样本信号日（计算日期） | [default] |
| `market_tag` | str | 大盘标签 | [default] |
| `update_time` | datetime | 数据更新时间 | [default] |
| `total_etf_count` | int | 计算样本总数 | [mock] |

### HistoricalRecord（历史表现记录）

| 字段名 | 字段类型 | 单位 | 说明 | 状态 |
|--------|---------|------|------|------|
| `date` | date | — | 历史日期 | [default] |
| `etf_code` | str | — | ETF 代码 | [verified] |
| `etf_name` | str | — | ETF 名称 | [mock] |
| `composite_score` | float | 无 | 综合评分 | [default] |
| `rank` | int | — | 排名 | [default] |
| `signal_3d_return` | float | % | 信号后 3 日涨幅，None 表示不足 3 交易日 | [default] |
| `current_return` | float | % | 当前涨幅，None 表示暂无 | [default] |

## 正常样例

```json
{
  "top_etfs": [
    {
      "etf_code": "516020",
      "etf_name": "人工智能ETF",
      "composite_score": 0.92,
      "rank": 1,
      "sector": "科技-AI",
      "tags": ["ETF", "指数基金"],
      "market_tag": "积极参与"
    }
  ],
  "sectors": [
    {
      "name": "科技-AI",
      "etfs": [{"code": "516020", "name": "人工智能ETF", "score": 0.92}]
    }
  ],
  "signal_date": "2026-05-25",
  "market_tag": "积极参与",
  "total_etf_count": 100
}
```

## 边界样例

### ETF 不足 5 个
- 按实际数量返回，赛道不足 5 个时省略
- `top_etfs` 长度 < 5

### 标准差为 0
- Z 分数记为 0，排名分数全部相同
- 低波排名分数全部相等

### 非交易日/无数据
- `status = "not_calculable"`
- 该 ETF 不进入 Top 推荐

### 样本不足
- `status = "insufficient_sample"`
- 按已有样本计算

## 缺失值规则

| 情况 | 处理 |
|------|------|
| 热度原始字段为 0（Mock 异常） | 计为 0，Z 分数正常计算 |
| 收盘价缺失 | status = "not_calculable"，不进入排名 |
| 成交额缺失 | status = "not_calculable" |
| 价格序列不足（< 2 个） | status = "not_calculable" |
| 标准差为 0 | Z 分数 = 0 |
| signal_3d_return 为 None | 前端展示 "--" |

## 缓存与刷新规则

| 项目 | 策略 |
|------|------|
| ETF 评分缓存 | 内存缓存 + TTL 300s |
| Top5 缓存 | 内存缓存 + TTL 300s |
| 历史数据 | 直接查询 DB |
| 数据刷新 | 每次 `run_daily_calculation()` 落库并刷新缓存 |

## 定时任务

- 建议触发时间：每个交易日早上 7:00
- 幂等：同一天重复计算会覆盖之前结果（INSERT OR REPLACE）
- 数据一致性：先计算 → 落库 → 刷新缓存

## 降级与兜底

| 场景 | 策略 |
|------|------|
| Mock 数据生成异常 | 使用默认值（全 0），标记 `status = not_calculable` |
| 数据库不可写 | 仅返回内存结果，不落库 |
| 所有 ETF 不可计算 | 返回空 Top5 列表，标记 `market_tag = "积极参与"` |

## `fund-indic-search-test` 检索证据

```yaml
execution_status: "SEARCH_COMPLETED"
skill_runtime_source: "Multica Runtime Skill: fund-indic-search-test"
source_used: "sync_api + indic_cache (750条指标)"
keywords:
  - "chgpct, heat, turnover, unitNav, sousuo_uv, sousuo_click_uv, fenshi_uv, add_uv, buy_uv"
命中:
  - chgpct [online]: 日涨幅, unit=%
  - heat [online]: 热度值
  - unitNav [online]: 单位净值
  - unit_nav [online]: 单位净值(历史)
  - turnover [deprecated]: 成交额 ⚠️
  - etfNetBuyFlowAmount [online]: ETF净申购流入金额
未命中:
  - sousuo_uv, sousuo_click_uv, fenshi_uv, add_uv, buy_uv: NO_MATCH → [mock]
  - adjNav: planed → 使用 unitNav 替代
```

## 数据来源决策

| 数据 | 来源 | 状态 |
|------|------|------|
| ETF 计算样本 | Mock 配置（100 个） | [mock] |
| 收盘价/净值 | unitNav 序列（本轮 Mock 模拟） | [mock] |
| 成交额 | 行情接口取原始数据（本轮 Mock 模拟） | [mock] |
| 热度原始字段 | Mock 生成（fund-indic-search-test 全部 NO_MATCH） | [mock] |
| 赛道映射 | Mock 静态映射表 | [mock] |
| 个基标签 | Mock 静态标签 | [mock] |
| 资讯数据 | Mock 生成 | [mock] |
| 指南内容 | Mock 生成 | [mock] |

## 公式一致性说明

所有公式严格按照 `.multica/admission_check.md` 和 WS-20 Issue 定义：

- ETF分数 = 50%*热度排名分数 + 35%*动量排名分数 + 10%*流动性排名分数 + 5%*低波排名分数
- 排名分数 = (总数 - 排名) / 总数
- 热度因子 = 0.55*搜索热度Z + 0.45*首购热度Z
- 动量因子 = C_t-1/C_t-5 - 1
- 流动性因子 = 近20个可用交易日成交额均值 [default]
- 低波因子 = std(20个日收益率)
- 20日动量中位数 < -0.03 → "谨慎参与" [default]

排名方向：
- 热度 DESC, 动量 DESC, 流动性 DESC, 低波 ASC

边界规则 [default]：
- 标准差为 0 → Z 分数 = 0
- 样本不足 → 按已有样本，标记 `insufficient_sample`
- 并列同名次，后续顺延
- 分数保留 2 位小数，内部高精度计算
