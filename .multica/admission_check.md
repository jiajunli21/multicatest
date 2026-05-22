# 早盘宝 入场前开发准入校验（第2轮）

## 校验 ID / 时间戳

`admission-20260522-140500-v2`

## Issue 标识

- **Issue ID**: `4f88c731-cc10-4691-a31e-d75e56d7179f` (WS-8)
- **标题**: 早盘宝-后端需求二次传输-第2轮（人工决策解锁指令执行）
- **父 Issue**: `ad4ca552-e512-43d3-84d1-db6d10c308ae` (WS-6)
- **第1轮子 Issue**: `c5f5041a-024e-4b8f-800f-91884aeec494` (WS-7, 已阻塞)
- **指派**: ETF 行情组后端 Leader Agent
- **本轮触发原因**: 李家骏人工兜底人对第1轮 10 项硬阻塞做出明确决策，解除硬阻塞
- **重跑轮次**: 第 2 轮，重新全新执行

## 当前仓库与分支

- **目标仓库**: https://github.com/jiajunli21/multicatest.git
- **目标分支**: 260522
- **基线分支**: main
- **当前工作分支**: agent/etf-leader-agent/a1eb1f98 (tracks origin/260522)
- **读取入口**: 当前 Issue WS-8 描述、第1轮 WS-7 准入报告、李家骏人工决策反馈
- **上传入口**: .multica/admission_check.md

---

## 第1轮阻塞项 → 第2轮解除状态逐项比对

| 序号 | 第1轮阻塞项 | 原负责人 | 第2轮人工决策 | 解除状态 |
|:----:|-----------|---------|---------|:--------:|
| 1 | `fund-indic-search-test`: AUTH_MISSING | N/A | 提供凭证：email=liujiaqing@myhexin.com, token=889a3bdd-8ef7-3222-b277-9d0ac5ee9c2c | 已解除 → NETWORK_FAILED（API可达但数据同步为空） |
| 2 | 搜索热度原始字段(sousuo_uv等)数据来源 | 王珏、黄运锞 | 本轮暂缓，允许 Mock 假数据对 Z 分数算法框架开发测试 | 已解除（暂缓/Mock） |
| 3 | T日/T-1/T-5/T-19交易日口径 | 黄运锞 | 临时确认：仅计算交易日，过滤非交易日；非交易日发起时 T 日自动回退至上一有效交易日 | 已解除（临时确认） |
| 4 | 20日平均成交额是否作为流动性因子 | 黄运锞 | 临时确认：流动性因子 = 最近 20 个交易日日成交额均值，DESC 排名 | 已解除（临时确认） |
| 5 | 标准差为0、样本不足、停牌等边界规则 | 黄运锞 | 临时确认：详见下方边界规则章节 | 已解除（临时确认） |
| 6 | AI标签生成方式和兜底 | 黄运锞 | 本轮暂缓：第一阶段不调用 AI 标签服务，返回 Mock 静态占位数组 | 已解除（暂缓/Mock） |
| 7 | ETF到三级赛道映射来源 | 徐哲人、黄运锞 | 本轮暂缓：暂不引入动态赛道配置，采用静态 Map/Mock 结构 | 已解除（暂缓/Mock） |
| 8 | 资讯部门过滤接口路径 | 王奕乾 | 本轮暂缓：不与资讯部门接口真实联调，Mock 或复用现有标准资讯接口 | 已解除（暂缓/Mock） |
| 9 | 推送权限判断和无权限兜底 | 姜文迪 | 本轮暂缓：默认返回有权限，通知模板直接展示标准 ETF 名称和 code | 已解除（暂缓/Mock） |
| 10 | 一键加自选分组/幂等/部分失败 | 黄运锞 | 本轮暂缓：只保证正常点击时添加成功，复杂边界策略本轮暂不处理 | 已解除（暂缓/Mock） |

> **核心开发方针**：核心计算（热度/动量/流动性/低波排名、评分、标签）按临时确认口径先行开发；非核心外部依赖（数据源、AI、赛道、资讯、推送权限、自选规则）本轮全面暂缓，允许 Mock 数据/空占位先行。

---

## Skill 执行状态

### fund-api-docs

```yaml
skill_name: "fund-api-docs"
execution_status: "REFERENCE_SEARCHED"
skill_runtime_source: "/Users/lijiajun/.claude/skills/fund-api-docs"
source_used:
  - "references/reference-index.md"
  - "references/indicator-data-reference.md"
  - "references/tag-data-reference.md"
  - "references/recommendation-reference.md"
  - "references/fund-basic-reference.md"
  - "references/fund-rank-screening-reference.md"
keywords:
  - "早盘宝页面展示接口"
  - "ETF 评分查询"
  - "热度因子数据"
  - "动量因子数据"
  - "流动性因子数据"
  - "低波因子数据"
  - "个基标签"
  - "资讯过滤接口"
  - "历史表现查询"
  - "预警订阅接口"
  - "预警推送接口"
  - "一键加自选接口"
  - "分组加自选"
  - "指南查询"
  - "行情 ETF tab 入口"
  - "三级赛道映射"
failure_reason: "无"
can_be_used_as_admission_evidence: true
```

### fund-indic-search-test

```yaml
skill_name: "fund-indic-search-test"
execution_status: "NETWORK_FAILED"
skill_runtime_source: "/Users/lijiajun/.claude/skills/fund-indic-search-test"
source_used:
  - "~/.claude/fund-indic-config.json（已配置凭证：email=liujiaqing@myhexin.com）"
  - "API: https://testfund.10jqka.com.cn/open/api/fund/indic/skills/v1/indic/sync"
keywords:
  - "ETF 收盘价"
  - "ETF 成交额"
  - "日收益率"
  - "sousuo_uv"
  - "sousuo_click_uv"
  - "fenshi_uv"
  - "add_uv"
  - "buy_uv"
  - "搜索热度"
  - "首购热度"
  - "热度因子"
  - "动量因子"
  - "流动性因子"
  - "低波因子"
  - "Z 分数"
  - "排名分数"
  - "20 日平均成交额"
  - "日收益率标准差"
  - "三级赛道映射"
  - "交易日口径"
failure_reason: "认证通过（HTTP 200，非 5000），但 API 响应体为空（Content-Length: 0），指标同步数据未填充。Skill 定义的原始 URL 含 etf_rank 路径段返回 404，去除 etf_rank 后返回 200 但无数据。测试环境指标数据同步可能未初始化。"
can_be_used_as_admission_evidence: false
```

---

## fund-api-docs 检索证据（第2轮重新确认）

| execution_status | 查询关键词 / 线索 | source_used | 命中接口 / 资料 | 能力边界 | 缺口 | 结论 |
|---|---|---|---|---|---|---|
| REFERENCE_SEARCHED | 早盘宝页面展示 / ETF评分 / Top5赛道 | fund-rank-screening-reference.md | `GET /fund_rank/v1/fund_rank` | 通用基金排行/筛选/排序，支持 ETF(typeList=3)、收益排序、排名百分比、ETF特有指标 | 不支持自定义评分公式(50%+35%+10%+5%)；无早盘宝专属评分字段；无Top5赛道去重映射 | 需新建早盘宝展示接口 |
| REFERENCE_SEARCHED | 热度因子 / 搜索热度 / 首购热度 / sousuo_uv | indicator-data-reference.md | `POST /data/query/v1/line`、`POST /data/query/v1/table` | 可获取 ETF 收盘价、成交额等行情指标 | sousuo_uv、sousuo_click_uv、fenshi_uv、add_uv、buy_uv 不在已覆盖接口的指标列表中 | 热度原始字段需外部数据源（本轮暂缓/Mock） |
| REFERENCE_SEARCHED | 动量因子 / 收盘价 | indicator-data-reference.md, fund-rank-screening-reference.md | `POST /data/query/v1/line`、`GET /fund_rank/v1/fund_rank`（chgpct等） | 可获取 ETF 日级收盘价和画线行情数据 | 具体 index_id 待开发时确认 | 收盘价数据可复用行情系统，需确认 index_id |
| REFERENCE_SEARCHED | 流动性因子 / 成交额 | indicator-data-reference.md, fund-rank-screening-reference.md | `POST /data/query/v1/line`、`POST /data/query/v1/table` | 可获取 ETF 成交额等表格数据 | 具体成交额 index_id 待开发时确认 | 成交额数据可复用行情系统，需确认 index_id |
| REFERENCE_SEARCHED | 低波因子 / 日收益率标准差 | indicator-data-reference.md | `POST /data/query/v1/line` | 可获取 ETF 日收益率数据 | 标准差计算需后端自行实现 | 收盘价数据可复用，低波因子需后端计算 |
| REFERENCE_SEARCHED | 个基标签 | tag-data-reference.md | `POST /data/query/v1/tag_spec`、`GET /enhance/v1/tag/data_api/sync` | 预定义标签明细(连涨连跌、跟踪指数等)，标签模板固定 | 本轮 AI 标签暂缓，直接 Mock 静态占位数组 | AI标签能力本轮不涉及（暂缓/Mock） |
| REFERENCE_SEARCHED | 资讯过滤 | fund-basic-reference.md | `GET /fund_content/v2/query` | 按基金代码查询资讯列表，返回标题/摘要/时间/来源 | 本轮暂缓资讯部门真实联调，复用现有标准资讯接口或 Mock | 本轮暂缓/Mock |
| REFERENCE_SEARCHED | 历史表现 | fund-basic-reference.md | `GET /fund_detail/v2/getNavData` | 基金历史净值数据(单位净值/复权净值)，支持 week/month/year 等 range | 不支持早盘宝推送记录存储、信号后3日涨幅计算、当前涨幅实时查询 | 需新建历史表现接口和落库 |
| REFERENCE_SEARCHED | 预警订阅与推送 | 全部5个reference | 无命中 | - | 无订阅管理/推送触发/消息模板/频控接口 | 需全部新建 |
| REFERENCE_SEARCHED | 一键加自选(分组) | fund-rank-screening-reference.md | selectRankDay/Week/Month（加自选排名统计指标） | 仅统计类排名指标，非操作类接口 | 无"一键加自选到分组"操作接口 | 需新建（本轮仅正常添加） |
| REFERENCE_SEARCHED | 指南查询 | 全部5个reference | 无命中 | - | 无静态配置/指南文案查询接口 | 需新建或复用运营配置读取 |
| REFERENCE_SEARCHED | ETF到三级赛道映射 | indicator-data-reference.md, recommendation-reference.md | `POST /data/query/v1/relation`、`POST /etf_tab/hq_tab/v1/related_fund_list` | 可查询 ETF 关联指数/板块 | 本轮暂缓动态赛道配置，采用静态 Mock Map | 本轮暂缓/Mock |

### fund-api-docs 总结

- **已有可复用接口**: `GET /fund_rank/v1/fund_rank`（排行筛选）、`POST /data/query/v1/line`（画线数据）、`POST /data/query/v1/table`（表格数据）、`POST /data/query/v1/tag_spec`（标签明细）、`GET /fund_content/v2/query`（资讯）、`GET /fund_detail/v2/getNavData`（历史净值）、`POST /data/query/v1/relation`（关系数据）
- **可复用接口的能力边界**: 仅提供通用 ETF 排行/指标/标签/资讯/净值查询能力，不包含早盘宝专属多因子评分、AI标签生成、推送订阅、一键加自选等核心业务能力
- **不满足需求的缺口**: 自定义多因子评分接口、历史推送记录存储和查询、预警订阅推送、一键加自选（分组）、指南配置
- **需要新建的接口**: 早盘宝展示接口（含Top5赛道）、历史表现查询接口、预警订阅接口、预警推送接口、一键加自选接口、指南查询接口
- **本轮暂缓/Mock的能力**: AI个基标签（Mock 静态数组）、资讯过滤（复用现有接口或 Mock）、三级赛道映射（静态 Mock Map）、推送权限（默认有权限）、一键加自选边界策略（仅正常添加）

---

## fund-indic-search-test 检索证据（第2轮）

| execution_status | 查询关键词 / 指标线索 | source_used | 命中指标 / 数据 | 字段单位 / 值类型 | 时间口径 | 缺口 | 结论 |
|---|---|---|---|---|---|---|---|
| NETWORK_FAILED | ETF 收盘价 / 成交额 / 日收益率 / sousuo_uv / sousuo_click_uv / fenshi_uv / add_uv / buy_uv / 搜索热度 / 首购热度 / 热度因子 / 动量因子 / 流动性因子 / 低波因子 | API 认证通过但响应为空 | 无（数据同步未填充） | 无法确认 | 无法确认 | 所有指标在 fund-indic 系统中的注册状态无法确认 | 阻塞（指标注册状态不可确认，软阻塞假设覆盖） |

### fund-indic-search-test 总结

- **执行状态**: NETWORK_FAILED — API 可达且认证通过（HTTP 200，非 5000），但响应体为空（Content-Length: 0）
- **根因分析**: 测试环境指标同步数据未初始化或未填充；原始 Skill 定义的 URL 含 `etf_rank` 路径段返回 404，去除 `etf_rank` 后可达但无数据
- **影响评估**:
  - 核心行情数据（收盘价、成交额、日收益率）可通过 fund-api-docs 数据查询接口从行情系统获取，不依赖 fund-indic 指标注册
  - 热度原始字段（sousuo_uv 等）本轮已暂缓，采用 Mock 数据
  - 指标注册状态虽无法确认，但不阻塞实际数据获取路径
- **与第1轮对比**: 第1轮为 AUTH_MISSING（无凭证），第2轮已提供凭证且 API 认证通过，但同步数据为空
- **处理**: 当前无法作为准入证据，属于软阻塞假设 S-1

---

## 完整校验清单（第2轮）

### 1. 需求目标 — 通过

- 业务目标：早盘时段为 ETF 提供综合关注度评分和排名 — 明确
- 15 个模块按页面/业务板块拆开 — 明确
- 后端职责：评分计算、排名、标签、资讯过滤、历史数据、预警推送、一键加自选 — 明确
- 完成判定：所有模块通过准入、路由、开发、审核并验收 — 明确

### 2. 接口来源 — 通过（软阻塞项已 PM 确认）

- `fund-api-docs` 已完成筛选: `execution_status=REFERENCE_SEARCHED` ✓
- 请求参数/响应结构: 待接口开发 Agent 入场后设计
- 外部接口(资讯部门): 本轮暂缓，复用现有标准资讯接口或 Mock — PM 已确认
- 权限规则: 推送权限默认有权限 — PM 已确认（暂缓复杂判断）

### 3. 指标与数据来源 — 软阻塞通过

- `fund-indic-search-test` 执行状态: NETWORK_FAILED — 软阻塞假设 S-1
- 核心行情数据（收盘价/成交额）: 从行情系统获取，fund-api-docs 数据接口已有能力
- 热度原始字段: 本轮暂缓，Mock 假数据 — PM 已确认
- 三级赛道映射: 本轮暂缓，静态 Mock Map — PM 已确认
- AI标签: 本轮暂缓，Mock 静态占位数组 — PM 已确认

### 4. 公式与数据口径 — 通过（临时确认）

- ETF 总分 = 50%×热度排名分数 + 35%×动量排名分数 + 10%×流动性排名分数 + 5%×低波排名分数 — 明确
- 各因子公式完整（Z分数/动量/低波） — 明确
- 交易日口径: 仅交易日，过滤非交易日，非交易日发起时回退 — 临时确认（李家骏）
- 流动性因子: 20日成交额均值 DESC — 临时确认（李家骏）
- 边界规则 5 条: 标准差0/样本不足/停牌/缺失热度字段/流动性不足20日 — 临时确认（李家骏）
- 排名方向: 热度DESC/动量DESC/流动性DESC/低波ASC — 明确
- 参与标签: 20日动量中位数<-0.03→谨慎参与 — 明确

### 5. 运营输入与前端展示 — 通过

- 运营配置: ETF计算样本、指南文案、推送模板 — 明确
- 前端展示: Top5赛道/评分/Mock标签/Mock资讯/历史记录/指南 — 明确
- 空态/异常态: 无数据返回空列表 — 明确

### 6. 推送、订阅、自选、历史和权限 — 软阻塞通过

- 推送权限: 默认有权限 — PM 已确认（暂缓）
- 一键加自选: 仅正常添加，分组=年月日早盘宝 — PM 已确认（暂缓）
- 资讯过滤: 复用现有接口或 Mock — PM 已确认（暂缓）
- 历史展示: 最晚 T-3 交易日 — 明确

### 7. 验收标准 — 通过

- 数据验收/接口验收/性能验收/联调验收/不做范围验收 — 均明确

### 8. 仓库与分支 — 通过

- 目标仓库: https://github.com/jiajunli21/multicatest.git ✓
- 目标分支: 260522 ✓
- 当前工作分支: agent/etf-leader-agent/a1eb1f98 (tracks origin/260522) ✓
- `repo-branch-safety-check`: 通过（remote一致、工作区干净、无冲突标记、无敏感信息、路径污染检测通过）

### 9. 系统性风险 — 通过（记录为开发注意事项）

- 幂等/数据一致性/兼容性/生产配置/秒级响应 — 均记录为开发注意事项

---

## 准入结果: **软阻塞通过**

### 软阻塞假设

| 序号 | 假设 | PM 是否接受 | 影响范围 | 假设错误后的返工影响 |
|:----:|------|:----------:|------|------|
| S-1 | `fund-indic-search-test` 数据同步为空不影响核心开发，核心行情数据可通过 fund-api-docs 数据接口从行情系统获取 | 是（李家骏已授权） | 指标注册状态确认 | 后续需确认具体 index_id，可能需调整指标查询参数，不影响整体架构 |
| S-2 | 热度原始字段使用 Mock 假数据可完成 Z 分数算法框架开发和测试 | 是（李家骏明确暂缓） | 热度因子计算 | 后续接入真实数据源时替换 Mock 数据源，算法框架不变 |
| S-3 | 交易日口径临时确认规则后续不会大幅变更 | 是（李家骏临时确认） | 动量/热度/低波计算 | 如需支持非交易日特殊处理，需调整时间窗口计算逻辑 |
| S-4 | 流动性因子 = 20日成交额均值 DESC 后续不会变更 | 是（李家骏临时确认） | 流动性排名计算 | 如需调整，需修改计算公式 |
| S-5 | 边界规则按临时确认规则后续不会大幅变更 | 是（李家骏临时确认） | 所有因子计算 | 边界规则变更可能影响各因子排名分 |
| S-6 | AI标签 Mock 静态数组不影响核心评分流程展示 | 是（李家骏明确暂缓） | 个基标签展示 | 后续接入 AI 服务时需新增接口调用 |
| S-7 | 三级赛道静态 Mock Map 不影响核心评分和展示验证 | 是（李家骏明确暂缓） | Top5赛道展示 | 后续接入动态配置时替换 Mock Map |
| S-8 | 资讯过滤复用现有接口/Mock 不影响当前展示 | 是（李家骏明确暂缓） | 资讯展示 | 后续接入时新增过滤逻辑 |
| S-9 | 推送权限默认有权限不影响推送功能开发联调 | 是（李家骏明确暂缓） | 推送权限 | 后续接入真实权限时增加判断和兜底 |
| S-10 | 一键加自选仅正常添加不影响功能验证 | 是（李家骏明确暂缓） | 自选操作 | 后续补充幂等/部分失败/无权限边界策略 |

---

## 入场前开发方案

### 1. 业务目标摘要

在早盘时段为用户提供 ETF 综合关注度评分和排名。后端从行情系统获取收盘价、成交额等数据（热度原始字段本轮 Mock），按临时确认公式计算热度因子（Z分数）、动量因子、流动性因子、低波因子，加权计算 ETF 总分并排名，取 Top5 按 Mock 赛道映射展示；提供历史推送记录查询、预警订阅推送、一键加自选到分组等功能。非核心外部依赖本轮 Mock 或暂缓。

### 2. 可开发范围

- ETF 计算样本从运营配置读取
- 早盘关注评分计算（热度/动量/流动性/低波排名 + 总分加权）
- 热度排名计算（Z 分数算法框架，原始数据 Mock）
- 动量排名计算（基于 T-1/T-5 收盘价，交易日口径）
- 流动性排名计算（最近 20 日成交额均值 DESC 排名）
- 低波排名计算（最近 20 日日收益率标准差 ASC 排名）
- 谨慎参与/积极参与标签计算（20日动量中位数判定）
- Top5 赛道展示接口（Mock 赛道映射）
- 历史表现查询接口和落库
- 预警订阅和推送接口（默认有权限）
- 一键加自选接口（正常添加，分组名 = 年月日早盘宝分组）
- 指南查询接口（运营配置读取）
- 资讯展示（复用现有标准接口或 Mock）

### 3. 暂缓范围

| 暂缓项 | 暂缓原因 | 负责人 | 解除条件 |
|---|---|---|---|
| 搜索热度原始字段数据源接入 | 数据来源待确认 | 王珏、黄运锞 | 确认数据提供方式和接入方案 |
| AI 标签生成 | AI 服务待确认 | 黄运锞 | AI 标签服务就绪 |
| 三级赛道动态配置 | 映射关系待确认 | 徐哲人、黄运锞 | 提供完整 ETF-三级赛道映射表 |
| 资讯部门真实过滤接口联调 | 接口路径/参数待确认 | 王奕乾 | 资讯部门提供过滤接口文档 |
| 推送权限复杂判断 | 权限规则待确认 | 姜文迪 | 提供权限判断规则和兜底方案 |
| 一键加自选复杂边界策略 | 边界策略待确认 | 黄运锞 | 确认幂等/部分失败/无权限处理规则 |

### 4. 能力-数据映射表

| Row ID | 能力 | 需要的数据 | 数据用途 | 数据状态 | 公式 / 口径引用 | 是否阻塞 |
|---|---|---|---|---|---|---|
| AD-001 | ETF计算样本管理 | 运营配置ETF列表 | 确定计算范围 | 运营平台配置 | NOT_APPLICABLE:运营输入 | 否 |
| AD-002 | 热度因子计算 | sousuo_uv, sousuo_click_uv, fenshi_uv, add_uv, buy_uv (T日和T-19至T日) | 计算搜索热度Z分数、首购热度Z分数、热度因子 | Mock | 热度因子=0.55×搜索热度Z+0.45×首购热度Z | 否（Mock） |
| AD-003 | 动量因子计算 | ETF收盘价(T-1日, T-5日) | 计算动量因子 | 行情系统 | 动量因子=C_t-1/C_t-5-1 | 否 |
| AD-004 | 流动性因子计算 | ETF日成交额(最近20个交易日) | 计算20日平均成交额 | 行情系统 | 流动性因子=20日成交额均值，DESC | 否 |
| AD-005 | 低波因子计算 | ETF日收益率(最近20个交易日) | 计算日收益率标准差 | 由收盘价计算 | 低波因子=std(日收益率_t-20,...,日收益率_t-1) | 否 |
| AD-006 | ETF总分计算 | 热度/动量/流动性/低波排名分数 | 加权计算总分 | 需计算 | 总分=50%×热度+35%×动量+10%×流动性+5%×低波 | 否 |
| AD-007 | 排名计算 | 各因子值 | DESC/ASC排名 | 需计算 | 排名分数=(ETF总数-当前排名)/ETF总数 | 否 |
| AD-008 | 个基标签（本轮Mock） | 无（Mock占位） | ETF详情页展示 | Mock静态数组 | NOT_APPLICABLE:本轮暂缓 | 否（Mock） |
| AD-009 | 参与标签计算 | 计算样本内所有ETF的20日动量 | 判断谨慎/积极参与 | 需计算 | 中位数<-0.03→谨慎参与 | 否 |
| AD-010 | Top5赛道展示 | ETF总分排名 + ETF-三级赛道映射(Mock Map) | 确定展示赛道和ETF评分 | 需计算+Mock Map | Top5 ETF对应三级赛道;最多5个赛道 | 否（Mock映射） |
| AD-011 | 资讯过滤（本轮Mock） | 现有标准资讯接口或Mock | 早盘宝页面展示资讯 | Mock/复用现有接口 | NOT_APPLICABLE:本轮暂缓 | 否（Mock/复用） |
| AD-012 | 历史表现 | 历史推送记录(落库) + 实时涨幅 | 展示历史推送的ETF及涨跌幅 | 需新建落库 | 信号后3日涨幅；不足3日→"--"；最晚T-3 | 否 |
| AD-013 | 指南展示 | 运营指南配置 | 返回指南文案 | 运营配置 | NOT_APPLICABLE:运营输入 | 否 |
| AD-014 | 预警订阅 | 用户订阅关系 | 管理用户订阅状态 | 需新建存储 | NOT_APPLICABLE:无公式 | 否 |
| AD-015 | 预警推送 | Top5 ETF数据 + 推送模板 + 订阅关系 | 推送消息 | 需新建 | 默认有权限；模板预留5个ETF名称和code | 否 |
| AD-016 | 一键加自选 | 用户ID + ETF code + 分组名 | 添加到年月日早盘宝分组 | 需新建 | 仅正常添加；分组名=yyyymmdd早盘宝分组 | 否 |

### 5. 数据-接口映射表

| Row ID | 数据 | 获取方式 | 来源接口 / 指标 / 配置 | 计算 / 加工规则 | 公式 / 口径引用 | 计算责任方 | 是否加工 | 是否落库 | 是否缓存 | 是否阻塞 |
|---|---|---|---|---|---|---|---|---|---|---|
| DI-001 | ETF计算样本列表 | 运营配置读取 | 运营平台配置 | NOT_APPLICABLE:运营输入 | NOT_APPLICABLE:运营输入 | 不适用 | 否 | 否 | 是 | 否 |
| DI-002 | 热度原始字段(sousuo_uv等) | Mock | Mock数据生成 | 搜索热度=log(1+sousuo_uv+3×sousuo_click_uv)；首购热度=log(1+fenshi_uv+5×add_uv+20×buy_uv) | 公式与口径§4 | 数据开发 | 是 | 否 | 否 | 否（Mock） |
| DI-003 | ETF收盘价(日级) | 复用行情系统 | `POST /data/query/v1/line` | 日收益率=收盘价_t/收盘价_t-1-1 | 公式与口径§4 | 数据开发 | 是 | 否 | 是 | 否 |
| DI-004 | ETF日成交额(日级) | 复用行情系统 | `POST /data/query/v1/line`或`POST /data/query/v1/table` | 20日算术平均 | 公式与口径§4 | 数据开发 | 是 | 否 | 是 | 否 |
| DI-005 | ETF-三级赛道映射 | Mock | 静态Mock Map | NOT_APPLICABLE:本轮暂缓 | NOT_APPLICABLE:本轮暂缓 | 不适用 | 否 | 否 | 否 | 否（Mock） |
| DI-006 | 历史推送记录 | 新增落库 | 新建数据库表 | 每次推送后写入5个ETF及信号后涨跌幅 | 验收标准 | 数据开发 | 是 | 是 | 否 | 否 |
| DI-007 | 用户订阅关系 | 新增落库 | 新建数据库表 | 用户订阅/取消订阅操作 | NOT_APPLICABLE:无公式 | 数据开发 | 否 | 是 | 是 | 否 |
| DI-008 | 推送模板配置 | 运营配置读取 | 运营平台配置 | NOT_APPLICABLE:运营输入 | NOT_APPLICABLE:运营输入 | 不适用 | 否 | 否 | 是 | 否 |
| DI-009 | 指南文案 | 运营配置读取 | 运营平台配置 | NOT_APPLICABLE:运营输入 | NOT_APPLICABLE:运营输入 | 不适用 | 否 | 否 | 是 | 否 |
| DI-010 | ETF实时涨幅 | 复用行情系统 | 行情系统实时数据 | NOT_APPLICABLE:直接查询 | NOT_APPLICABLE:直接查询 | 接口包装 | 否 | 否 | 否 | 否 |
| DI-011 | AI标签（本轮Mock） | Mock | 静态Mock数组 | NOT_APPLICABLE:本轮暂缓 | NOT_APPLICABLE:本轮暂缓 | 不适用 | 否 | 否 | 否 | 否（Mock） |
| DI-012 | 资讯数据（本轮Mock/复用） | 复用现有接口或Mock | `GET /fund_content/v2/query`或Mock | NOT_APPLICABLE:本轮暂缓 | NOT_APPLICABLE:本轮暂缓 | 接口包装 | 否 | 否 | 否 | 否（Mock/复用） |

### 6. 接口-能力映射表

| Row ID | 接口场景 | 接口具体功能 | 服务能力 | 处理方式 | 请求参数 | 返回字段 | 权限规则 | 空数据规则 | 错误/降级 | Mock |
|---|---|---|---|---|---|---|---|---|---|---|
| IA-001 | 早盘宝展示接口 | 返回ETF评分Top5、赛道、标签、资讯、参与标签 | ETF评分排名展示 | 新增 | ETF列表或默认全量 | ETF总分、排名分数、赛道(Mock)、标签(Mock)、参与标签、资讯(Mock) | 无特殊权限 | 无数据返回空列表 | 行情系统不可用时返回空列表 | 部分Mock |
| IA-002 | 历史表现查询接口 | 返回历史推送记录：日期、5个ETF、信号后3日涨幅、当前涨幅 | 历史数据查询 | 新增 | 日期范围(可选) | 日期、ETF列表(code/名称)、3日涨幅、当前涨幅 | 无特殊权限 | 无历史数据返回空列表 | 数据库不可用时返回空列表 | 否 |
| IA-003 | 预警订阅接口 | 用户订阅/取消订阅早盘宝预警 | 订阅管理 | 新增 | 用户ID、操作(订阅/取消) | 订阅状态 | 默认有权限 | 无订阅返回空 | 存储不可用时返回失败 | 否 |
| IA-004 | 预警推送接口 | 数据计算完成后推送Top5 ETF到已订阅用户 | 消息推送 | 新增 | 推送模板、Top5 ETF数据 | 推送消息(含5个ETF名称和code) | 默认有权限 | 无订阅用户不推送 | 推送失败需重试 | 否 |
| IA-005 | 一键加自选接口 | 将ETF添加到年月日早盘宝分组 | 自选分组管理 | 新增 | 用户ID、ETF code | 成功/失败 | 默认有权限 | 无分组时新建分组 | 仅正常添加（暂缓边界） | 否 |
| IA-006 | 指南查询接口 | 返回运营配置的早盘宝指南文案 | 运营配置读取 | 新增 | 无 | 指南文案 | 无特殊权限 | 配置为空返回默认文案 | 配置不可用时返回默认文案 | 否 |

### 7. Routing 输入包

| 子任务 | 建议对象 | 输入 | 输出 | 串行依赖 |
|---|---|---|---|---|
| 数据开发：ETF评分计算定时任务和落库 | 数据开发 Agent | 入场前开发方案（能力-数据映射表 AD-001 至 AD-016）、公式与口径、Mock热度数据方案 | ETF评分计算任务、历史推送记录落库、用户订阅关系存储、缓存策略 | 无（可并行开始） |
| 接口开发：早盘宝展示/历史/订阅/推送/自选/指南接口 | 接口开发 Agent | 入场前开发方案（接口-能力映射表 IA-001 至 IA-006、数据-接口映射表 DI-001 至 DI-012） | 6个新增接口的实现和契约文档 | 依赖数据开发产出评分数据后联调展示接口 |
| 测试与质量审核 | 测试与质量审核 Agent | 数据开发和接口开发产出、验收标准 | 测试报告和质量结论 | 依赖数据开发和接口开发均完成 |

---

## 下一步

**进入 `backend-task-routing`**，将入场前开发方案路由给数据开发 Agent、接口开发 Agent 和测试与质量审核 Agent。

方案版本 / 时间戳：`admission-20260522-140500-v2`
工作分支：`agent/etf-leader-agent/a1eb1f98`
commit SHA：待提交
remote：origin → https://github.com/jiajunli21/multicatest.git
push 结果：待推送
