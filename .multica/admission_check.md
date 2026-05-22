# 早盘宝 入场前开发准入校验

## 校验 ID / 时间戳

`admission-20260522-132000`

## Issue 标识

- **Issue ID**: `c5f5041a-024e-4b8f-800f-91884aeec494` (WS-7)
- **标题**: 早盘宝-后端需求首次传输-第1轮
- **父 Issue**: `ad4ca552-e512-43d3-84d1-db6d10c308ae`
- **指派**: ETF 行情组后端 Leader Agent

## 当前仓库与分支

- **目标仓库**: https://github.com/jiajunli21/multicatest.git
- **目标分支**: 260522
- **基线分支**: main
- **当前工作分支**: agent/etf-leader-agent/e00d112c (tracks origin/260522)
- **读取入口**: morning-report-requirements.md（附件，当前仓库中未见）
- **上传入口**: .multica/admission_check.md

---

## Skill 执行状态

### fund-api-docs

```yaml
skill_name: "fund-api-docs"
execution_status: "REFERENCE_SEARCHED"
skill_runtime_source: "/Users/lijiajun/.claude/skills/fund-api-docs"
source_used:
  - "references/reference-index.md"
  - "references/fund-rank-screening-reference.md"
  - "references/tag-data-reference.md"
  - "references/fund-basic-reference.md"
  - "references/indicator-data-reference.md"
  - "references/recommendation-reference.md"
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
execution_status: "AUTH_MISSING"
skill_runtime_source: "/Users/lijiajun/.claude/skills/fund-indic-search-test"
source_used: []
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
failure_reason: "~/.claude/fund-indic-config.json 不存在，无法完成认证和指标数据同步/检索"
can_be_used_as_admission_evidence: false
```

---

## fund-api-docs 检索证据

| execution_status | 查询关键词 / 线索 | source_used | 命中接口 / 资料 | 能力边界 | 缺口 | 结论 |
|---|---|---|---|---|---|---|
| REFERENCE_SEARCHED | 早盘宝页面展示 / ETF评分 / Top5赛道 | fund-rank-screening-reference.md | `GET /fund_rank/v1/fund_rank` | 通用基金排行/筛选/排序，支持 ETF(typeList=3)筛选、收益排序、排名百分比、ETF特有指标 | 不支持自定义评分公式(50%热+35%动+10%流+5%低波)；不支持Top5赛道去重映射；无早盘宝专属评分字段 | 需新建早盘宝展示接口 |
| REFERENCE_SEARCHED | 热度因子数据 / sousuo_uv / 搜索热度 | indicator-data-reference.md | `POST /data/query/v1/line`、`POST /data/query/v1/table`、`GET /gateway/cache/v1/line` | 可获取ETF收盘价、成交额等画线/表格指标数据 | 不支持sousuo_uv、sousuo_click_uv、fenshi_uv、add_uv、buy_uv等搜索/首购热度原始字段 | 关键热度原始字段需新增数据源 |
| REFERENCE_SEARCHED | 动量因子 / 收盘价 | indicator-data-reference.md, fund-rank-screening-reference.md | `POST /data/query/v1/line`、`GET /fund_rank/v1/fund_rank`（chgpct等） | 可获取ETF日级收盘价(chgpct)和画线数据 | index_id 具体值待确认 | 收盘价数据可复用，需确认index_id |
| REFERENCE_SEARCHED | 流动性因子 / 成交额 | indicator-data-reference.md, fund-rank-screening-reference.md | `POST /data/query/v1/line`、`POST /data/query/v1/table` | 可获取ETF成交额等表格数据 | 具体成交额 index_id 待确认 | 成交额数据可复用，需确认index_id |
| REFERENCE_SEARCHED | 低波因子 / 日收益率标准差 | indicator-data-reference.md | `POST /data/query/v1/line` | 可获取ETF日收益率数据 | 标准差计算需后端自行实现 | 收盘价数据可复用，低波因子需后端计算 |
| REFERENCE_SEARCHED | 个基标签 (AI生成) | tag-data-reference.md | `POST /data/query/v1/tag_spec`、`GET /enhance/v1/tag/data_api/sync` | 预定义标签明细(连涨连跌、跟踪指数等)，标签模板固定 | 不支持AI动态生成标签(最多15个)；标签内容为固定模板非AI生成 | AI标签能力需新建 |
| REFERENCE_SEARCHED | 资讯过滤 | fund-basic-reference.md | `GET /fund_content/v2/query` | 按基金代码(hqcode)查询资讯列表，返回标题/摘要/时间/来源 | 不支持"资讯部门过滤接口"；无ETF相关性/早盘宝专属过滤逻辑 | 需改造或新建资讯过滤接口 |
| REFERENCE_SEARCHED | 历史表现 | fund-basic-reference.md | `GET /fund_detail/v2/getNavData` | 基金历史净值数据(单位净值/复权净值)，支持week/month/year等range | 不支持早盘宝推送记录存储、信号后3日涨幅计算、当前涨幅实时查询 | 需新建历史表现接口和数据存储 |
| REFERENCE_SEARCHED | 预警订阅与推送 | 全部5个reference | 无命中 | - | 无订阅管理/推送触发/消息模板/频控等相关接口 | 需全部新建 |
| REFERENCE_SEARCHED | 一键加自选(分组) | fund-rank-screening-reference.md | selectRankDay/Week/Month等(加自选排名统计指标) | 仅统计类排名指标，非操作类接口 | 无"一键加自选到分组"操作接口；无分组(年月日早盘宝分组)管理能力 | 需新建 |
| REFERENCE_SEARCHED | 指南查询 | 全部5个reference | 无命中 | - | 无静态配置/指南文案查询接口 | 需新建或复用运营配置读取 |
| REFERENCE_SEARCHED | ETF到三级赛道映射 | indicator-data-reference.md, recommendation-reference.md | `POST /data/query/v1/relation`、`POST /etf_tab/hq_tab/v1/related_fund_list` | 可通过关系数据查询ETF关联指数/板块(fundList中包含市场、名称) | 三级赛道具体层级定义和映射字段需确认；themeTypeList为行业列表可部分参考 | 可能可复用，需确认三级赛道定义 |
| REFERENCE_SEARCHED | 行情ETF tab入口 | recommendation-reference.md | `GET /fund/recommend/v1/entity/head/user` | ETF推荐/跳转 | 入口跳转非后端接口核心范畴，属前端路由 | 不适用 |

### fund-api-docs 总结

- **已有可复用接口**: `GET /fund_rank/v1/fund_rank`(排行)、`POST /data/query/v1/line`(画线数据)、`POST /data/query/v1/table`(表格数据)、`POST /data/query/v1/tag_spec`(标签)、`GET /fund_content/v2/query`(资讯)、`GET /fund_detail/v2/getNavData`(历史净值)、`POST /data/query/v1/relation`(关系数据)
- **可复用接口的能力边界**: 仅提供通用ETF排行/指标/标签/资讯/净值查询能力，不包含早盘宝专属评分计算、AI标签生成、推送订阅、一键加自选等核心业务能力
- **不满足需求的缺口**: 自定义多因子评分接口、AI个基标签生成、资讯过滤、历史推送记录、预警订阅推送、一键加自选(分组)、指南配置、三级赛道映射
- **需要新建的接口**: 早盘宝展示接口(含Top5赛道)、历史表现查询接口、预警订阅接口、预警推送接口、一键加自选接口、指南查询接口
- **需要改造的接口**: 资讯过滤接口(基于现有资讯接口增加早盘宝过滤逻辑)

---

## fund-indic-search-test 检索证据

| execution_status | 查询关键词 / 指标线索 | source_used | 命中指标 / 数据 | 字段单位 / 值类型 | 时间口径 | 缺口 | 结论 |
|---|---|---|---|---|---|---|---|
| AUTH_MISSING | ETF 收盘价 / 成交额 / 日收益率 / sousuo_uv / sousuo_click_uv / fenshi_uv / add_uv / buy_uv | 无(认证缺失) | 无 | 无法确认 | 无法确认 | 全部指标可用性无法验证 | 阻塞 |

### fund-indic-search-test 总结

- **执行状态**: AUTH_MISSING — `~/.claude/fund-indic-config.json` 不存在
- **影响**: 无法确认以下指标/数据是否已在同花顺指标系统中注册可用：
  - ETF 收盘价(日级)、成交额(日级)、日收益率
  - sousuo_uv、sousuo_click_uv、fenshi_uv、add_uv、buy_uv（热度原始字段）
  - 三级赛道映射数据
  - 交易日历数据
- **处理**: 需要配置 `fund-indic-email` 和 `fund-indic-token` 后重新执行本 Skill

---

## 完整校验清单

### 1. 需求目标 — 部分明确，存在大量待确认项

- **业务目标**: 在早盘时段为用户提供 ETF 综合关注度评分和排名 — 明确
- **15 个模块拆分**: PM 已按页面/业务板块拆开描述 — 明确
- **后端职责**: 评分计算、排名、标签、资讯过滤、历史数据、预警推送、一键加自选 — 明确
- **完成判定**: 所有模块通过准入、路由、开发、审核并验收 — 明确

### 2. 接口来源 — 大量未确认

- `fund-api-docs` 已完成筛选: `execution_status=REFERENCE_SEARCHED`
- 请求参数/响应结构: 待确认（需新建接口设计）
- 接口调用方: C 端页面 / BFF — 明确
- 外部接口(资讯部门): 接口路径/参数/响应/兜底 均待确认 — **阻塞**
- 权限规则: 推送权限判断归口待确认(姜文迪) — **阻塞**

### 3. 指标与数据来源 — 大量未确认

- `fund-indic-search-test` 执行状态: `AUTH_MISSING` — **硬阻塞**
- 热度原始字段(sousuo_uv等): 数据来源/提供方式/刷新频率 待确认(王珏、黄运锞) — **阻塞**
- 三级赛道映射: 来源/维护人/缺失兜底 待确认(徐哲人、黄运锞) — **阻塞**
- AI标签生成: 方式/耗时/失败兜底 待确认(黄运锞) — **阻塞**
- 需要落库: 历史推送记录、用户订阅关系 — 明确
- 需要缓存: 待确认

### 4. 公式与数据口径 — 大量未确认

- 公式: ETF总分/热度因子/Z分数/动量因子/低波因子 — 明确
- 交易日口径: T日/T-1/T-5/T-19 的交易日/非交易日处理规则 待确认(黄运锞) — **阻塞**
- 流动性因子: 20日平均成交额是否作为流动性因子 待确认(黄运锞) — **阻塞**
- 边界规则: 标准差为0、样本不足、缺失字段、停牌等 待确认(黄运锞) — **阻塞**
- 并列规则: 待确认
- 排名方向: 热度DESC/动量DESC/流动性DESC/低波ASC — 明确(流动性待确认)

### 5. 运营输入与前端展示 — 部分明确

- 运营配置: ETF计算样本(运营平台)、指南文案(运营写死)、推送模板(运营编辑) — 明确
- 前端展示: Top5赛道/评分/标签/资讯/历史记录 — 明确
- 前端排序筛选: ETF总分Top5、赛道去重最多5个 — 明确
- 空态/异常态: 无数据返回空列表 — 明确

### 6. 推送、订阅、自选、历史和权限 — 大量未确认

- 推送权限: 用户当前指定产品权限判断/无权限模板返回 待确认(姜文迪) — **阻塞**
- 一键加自选: 分组命名规则/重复点击幂等/部分失败处理 待确认(黄运锞) — **阻塞**
- 资讯过滤接口: 路径/参数/响应/兜底 待确认(王奕乾) — **阻塞**
- 推送触发时机/频控/失败重试: 明确(用户订阅→数据计算完成→推送)
- 历史展示: 最晚展示T-3交易日数据 — 明确

### 7. 验收标准 — 明确

- 数据验收: 验证ETF总分、排名分数、Z分数等 — 明确
- 接口验收: 验证请求参数、响应字段、空态、错误态、权限兜底 — 明确
- 性能验收: 秒级响应 — 明确
- 联调验收: 前端展示验证 — 明确

### 8. 仓库与分支 — 明确

- 目标仓库: https://github.com/jiajunli21/multicatest.git — 明确
- 目标分支: 260522 — 明确
- 基线分支: main — 明确
- 当前工作分支: agent/etf-leader-agent/e00d112c (tracks origin/260522)
- `repo-branch-safety-check`: **通过**
  - Remote 一致: origin → https://github.com/jiajunli21/multicatest.git
  - 当前分支正确、执行环境正确
  - 无冲突标记、无敏感信息
  - push 条件: 待提交后确认

### 9. 系统性风险 — 存在

- 并发与幂等: 重复计算同一日数据是否幂等 — 待确认
- 数据一致性: 多层因子计算需保证同批次口径一致 — 待确认
- 兼容性: 新增模块不影响已有接口 — 待确认
- 生产配置: 功能开关/灰度 — 待确认

---

## 准入结果: **准入不通过**

### 硬阻塞项

| 序号 | 阻塞项 | 类型 | 负责人 | 影响 |
|---|---|---|---|---|
| 1 | `fund-indic-search-test`: AUTH_MISSING — `~/.claude/fund-indic-config.json` 不存在 | 数据/指标 | 后端 Leader / 李家骏 | 无法确认任何指标/数据在系统中的可用性 |
| 2 | 搜索热度原始字段(sousuo_uv等)数据来源、提供方式、刷新频率 | 数据 | 王珏、黄运锞 | 无法确认热度因子计算能否落地 |
| 3 | T日/T-1/T-5/T-19交易日口径和非交易日处理规则 | 数据/计算 | 黄运锞 | 无法确认动量、热度Z分数、低波计算口径 |
| 4 | 20日平均成交额是否作为流动性因子、排名方向 | 数据/计算 | 黄运锞 | 无法确认流动性排名计算 |
| 5 | 标准差为0、样本不足、缺失字段、停牌等边界规则 | 计算 | 黄运锞 | 无法确认评分边界行为 |
| 6 | AI标签生成方式、耗时、失败兜底 | 数据/能力 | 黄运锞 | 无法确认个基标签能力 |
| 7 | ETF到三级赛道映射来源、维护人、缺失兜底 | 数据 | 徐哲人、黄运锞 | 无法确认Top5赛道展示结果 |
| 8 | 资讯部门过滤接口路径、参数、响应、兜底 | 接口 | 王奕乾 | 无法确认资讯过滤接口能力 |
| 9 | 推送权限判断和无权限兜底 | 权限 | 姜文迪 | 无法确认推送权限边界 |
| 10 | 一键加自选分组命名、幂等、部分失败处理 | 接口/能力 | 黄运锞 | 无法确认自选接口副作用规则 |

---

## 入场前开发方案

**准入不通过，暂时无法形成完整入场前开发方案。**

以下为基于当前已确认信息的部分能力-数据映射草案（供后续准入通过后参考）：

### 能力-数据映射表（草案）

| Row ID | 能力 | 需要的数据 | 数据用途 | 数据状态 | 是否阻塞 |
|---|---|---|---|---|---|
| AD-001 | ETF计算样本管理 | 运营配置ETF列表 | 确定计算范围 | 待确认(运营配置) | 否 |
| AD-002 | 热度因子计算 | sousuo_uv, sousuo_click_uv, fenshi_uv, add_uv, buy_uv (T日和T-19至T日) | 计算搜索热度Z分数、首购热度Z分数、热度因子 | **待确认** | 是 |
| AD-003 | 动量因子计算 | ETF收盘价(T-1日, T-5日) | 计算动量因子 | 待确认(index_id) | 是(交易日口径) |
| AD-004 | 流动性因子计算 | ETF日成交额(最近20个交易日) | 计算20日平均成交额 | 待确认(index_id) | 是(方案待确认) |
| AD-005 | 低波因子计算 | ETF日收益率(最近20个交易日) | 计算日收益率标准差 | 待确认(index_id) | 是(交易日口径) |
| AD-006 | ETF总分计算 | 热度/动量/流动性/低波排名分数 | 加权计算总分 | 需计算 | 否 |
| AD-007 | 排名计算 | 各因子值 | DESC/ASC排名 | 需计算 | 否 |
| AD-008 | 个基标签 | AI服务 | AI生成最多15个标签 | **待确认** | 是 |
| AD-009 | 参与标签计算 | 20日动量数据(全样本) | 计算中位数，判断谨慎/积极参与 | 需计算 | 否 |
| AD-010 | Top5赛道展示 | ETF总分排名 + ETF-三级赛道映射 | 确定展示赛道和对应评分 | 待确认(映射) | 是 |
| AD-011 | 资讯过滤 | 资讯部门过滤接口 | 返回早盘宝相关资讯 | **待确认** | 是 |
| AD-012 | 历史表现 | 历史推送记录(落库) + 实时涨幅 | 展示历史推送的ETF及涨跌幅 | 需新建 | 否 |
| AD-013 | 指南展示 | 运营指南配置 | 返回指南文案 | 待确认(配置) | 否 |
| AD-014 | 预警订阅 | 用户订阅关系 | 管理用户订阅状态 | 需新建 | 否 |
| AD-015 | 预警推送 | Top5 ETF数据 + 推送模板 + 用户订阅 | 推送消息 | 需新建 | 是(权限) |
| AD-016 | 一键加自选 | 用户ID + ETF code + 分组名 | 添加到年月日早盘宝分组 | 需新建 | 是(副作用规则) |

---

## 下一步

**等待 PM 补充阻塞项并配置 `fund-indic-search-test` 认证后，重新执行 `backend-entry-validation`。**

当前执行单元状态：**开发状态：已阻塞**。本轮准入到此结束。
