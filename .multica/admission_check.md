# Admission Check

## Current Effective Summary

- current_effective_round: `Round 2`
- current_status: `软阻塞通过`
- current_decision_time: `2026-05-25T09:45:00+08:00`
- current_issue_ref: `WS-20 (e0365356-a25e-407d-86d8-537f48602b52)`
- current_branch_ref: `260525`
- effective_scope:
  - ETF 早盘关注评分计算（热度/动量/流动性/低波四因子 + 加权综合评分）
  - Top5 ETF 推荐 + 赛道分布展示（Mock 赛道映射）
  - 谨慎参与/积极参与标签计算
  - 个基标签（Mock 静态标签）
  - C 端早盘宝首页数据接口（新增）
  - C 端资讯过滤接口（Mock 响应）
  - C 端历史表现接口（新增）
  - C 端指南内容接口（新增/复用运营配置读取）
  - 预警订阅接口 + 推送触发（新增，暂默认有权限）
  - 一键加自选接口结构（新增，暂仅验证结构和幂等设计）
  - 数据落库与历史数据存储
- blocked_scope:
  - 真实 AI 标签生成 [pending]
  - 真实资讯部门接口接入 [pending]
  - 真实推送权限判断 [pending]
  - 真实一键加自选产品权限 [pending]
  - 运营平台真实配置入口 [pending]
  - 最终交易日口径 [pending]
  - 最终业务精度规则 [pending]
  - 真实 sousuo_uv/fenshi_uv/add_uv/buy_uv 数据源 [pending]
  - 真实 ETF→三级赛道映射 [pending]
- effective_contract_maps:
  - AD-001 ~ AD-015 (能力-数据映射)
  - DI-001 ~ DI-018 (数据-接口映射)
  - IA-001 ~ IA-008 (接口-能力映射)
- next_step: `进入 backend-task-routing`

---

## Round History

### Round 2

- trigger_reason: `人工决策解除首轮阻塞，二轮补充传输，新建子 Issue WS-20 重新准入`
- trigger_time: `2026-05-25T09:21:47Z`
- input_delta:
  - 二轮人工决策结论（@李家骏，2026-05-25）：12项首轮待确认项的处理结论
  - 本轮明确区分 [verified]/[mock]/[default]/[pending] 四类状态
  - 仓库访问问题已解决，`https://github.com/jiajunli21/multicatest` 分支 `260525` 可访问
- evidence_delta:
  - fund-api-docs: REFERENCE_SEARCHED，读取5个reference文件，命中行情数据查询、排行筛选、标签、推荐、资讯接口
  - fund-indic-search-test: SEARCH_COMPLETED，同步750条指标，命中 chgpct/heat/unitNav/etfNetBuyFlowAmount 等
- blockers: 无硬阻塞；11项 [pending] 待后续确认
- decision: `软阻塞通过`
- superseded_by: `NOT_SUPERSEDED`

---

### Round 1 (历史记录 — 来自 WS-18 / 首轮 commit 5404c87)

- trigger_reason: `首次准入`
- input_delta: `PM Issue WS-17 / WS-18 首轮需求`
- evidence_delta: `fund-api-docs + fund-indic-search-test 首轮检索`
- blockers: `12项硬阻塞（热度原始字段、交易日口径、流动性因子定义、边界行为、并列排名、AI标签、赛道映射、资讯接口、推送权限、一键加自选、运营配置、性能标准）`
- decision: `准入不通过`
- superseded_by: `Round 2`

---

## 业务目标摘要

为"早盘宝"业务模块提供后端能力：每个交易日计算 ETF 早盘关注评分（基于热度50%、动量35%、流动性10%、低波5%四因子加权），输出 Top5 ETF 推荐及赛道分布，提供资讯过滤、历史表现查询、预警订阅推送、一键加自选和指南内容服务。

## 可开发范围

- ETF 早盘关注评分计算（含热度/动量/流动性/低波排名分数 + 加权综合评分）
- Top5 ETF 推荐 + 赛道分布展示（Mock 赛道映射）
- 谨慎参与/积极参与标签计算（基于20日动量中位数）
- 个基标签（Mock 静态标签）
- C 端早盘宝首页数据接口（新增）
- C 端资讯过滤接口（Mock 响应）
- C 端历史表现接口（新增）
- C 端指南内容接口（新增/复用运营配置读取模式）
- 预警订阅接口 + 推送触发（新增，暂默认有权限）
- 一键加自选接口结构（新增，暂仅验证结构和幂等设计）
- 数据落库与历史数据存储

## 暂缓范围

| 暂缓项 | 暂缓原因 | 负责人 | 解除条件 |
|---|---|---|---|
| 真实 AI 标签生成 | 二轮人工决策：暂不处理 | 黄运锞 | PM 后续确认方案 |
| 真实资讯部门接口接入 | 二轮人工决策：暂不处理 | 王奕乾 | PM 后续确认接口 |
| 真实推送权限判断 | 二轮人工决策：暂不处理 | 姜文迪 | PM 后续确认权限规则 |
| 真实一键加自选产品权限 | 二轮人工决策：暂不处理 | 黄运锞 | PM 后续确认规则 |
| 运营平台真实配置入口 | 二轮人工决策：Mock | 黄运锞 | 运营平台就绪 |
| 最终交易日口径 | 二轮人工决策：暂自然日模拟 | 黄运锞 | 数据负责人确认 |
| 最终业务精度规则 | 二轮人工决策：暂默认假设 | 黄运锞/PM | 负责人确认 |
| 真实 sousuo_uv 等热度字段 | 二轮人工决策：优先真实验证/不可取时Mock | 王珏/黄运锞 | 数据源就绪或认证配置提供 |
| 真实 ETF→三级赛道映射 | 二轮人工决策：暂Mock | 徐哲人/黄运锞 | 映射表就绪 |

---

## fund-api-docs 检索证据

```yaml
skill_name: "fund-api-docs"
execution_status: "REFERENCE_SEARCHED"
skill_runtime_source: "Multica Runtime Skill: fund-api-docs (installed at ~/.claude/skills/fund-api-docs)"
source_used:
  - "references/reference-index.md"
  - "references/indicator-data-reference.md"
  - "references/fund-rank-screening-reference.md"
  - "references/fund-basic-reference.md"
  - "references/tag-data-reference.md"
  - "references/recommendation-reference.md"
keywords:
  - "早盘宝, ETF评分, ETF排名, 热度排名, 动量排名, 流动性排名, 低波排名, 资讯过滤, 预警订阅, 预警推送, 一键加自选, 历史表现, 自选分组, ETF赛道映射, 收盘价, 成交额, 搜索热度, 首购热度, 用户订阅, 推送模板, 产品权限"
failure_reason: "无"
can_be_used_as_admission_evidence: true
```

| execution_status | 查询关键词/线索 | source_used | 命中接口/资料 | 能力边界 | 缺口 | 结论 |
|---|---|---|---|---|---|---|
| REFERENCE_SEARCHED | 收盘价、成交额、行情数据 | indicator-data-reference.md | `POST /quotation/data/query/v1/line`, `POST /quotation/data/query/v1/table`, Gateway Cache v1/v2 版本 | 可查询 ETF 历史画线/表格指标数据（需配合 Tangram index_id），可用于获取收盘价和成交额序列 | 具体 index_id 需在 Tangram 平台确认；本 Skill 只证明接口存在，不证明 index_id 可用 | 复用 — 行情数据取数 |
| REFERENCE_SEARCHED | ETF排名、排行、筛选 | fund-rank-screening-reference.md | `GET /fuyao/fund_rank/fund_rank/v1/fund_rank` | 提供 ETF 榜单/筛选/排序能力，含 week/month/year/sharpe/maxDrawDown 等标准指标 | 不支持自定义加权评分公式；不支持 sousuo_uv/fenshi_uv 等热度原始字段；不支持早盘宝专用综合评分排名 | 部分复用 — 可用于校验，但早盘宝专用评分需新建计算逻辑 |
| REFERENCE_SEARCHED | 历史净值、资讯、基金详情 | fund-basic-reference.md | `GET /quotation/fund_detail/v2/getNavData`, `GET /quotation/fund_content/v2/query`, `GET /quotation/fund_detail/v2/get`, `GET /hqapi/static/diagnosis/{fundCode}` | 可获取历史净值序列（用于计算日收益率、动量、低波）；可获取基金资讯；可获取基金基本信息和诊断评分 | 资讯接口需 hqcode 映射；诊断评分不等于早盘宝评分 | 复用 — 历史净值取数（收盘价替代源）、基金基本信息；资讯接口本轮 Mock |
| REFERENCE_SEARCHED | 标签、个基标签 | tag-data-reference.md | `POST /quotation/data/query/v1/tag_spec` | 可查询基金标签明细（如连涨连跌等），最大100个基金代码 | 标签类型为技术面/资金面等，不等同于早盘宝所需 AI 标签；无早盘宝专用标签 | 部分复用 — 标签接口可用于补充标签，但早盘宝 AI 标签本轮 Mock |
| REFERENCE_SEARCHED | ETF推荐 | recommendation-reference.md | `POST /quotation/index/buy/v2/recommend/info`, `GET /quotation/fund/recommend/v1/entity/head/user` 等 | 提供基于指数/板块/个股的 ETF 推荐能力 | 推荐逻辑不等于早盘宝四因子加权评分 Top5；无赛道映射 | 不直接复用 — 早盘宝 Top5 需新建评分+排序逻辑 |
| REFERENCE_SEARCHED | 订阅推送 | (全部 reference) | 无命中 | — | fund-api-docs 不覆盖订阅/推送相关接口 | 新建 |
| REFERENCE_SEARCHED | 一键加自选 | (全部 reference) | 无命中（仅有 selectRank* 自选排名指标） | — | fund-api-docs 不覆盖自选分组写入接口 | 新建 |
| REFERENCE_SEARCHED | ETF赛道映射 | (全部 reference) | 无命中 | — | fund-api-docs 不覆盖 ETF→三级赛道映射数据 | Mock |
| REFERENCE_SEARCHED | sousuo_uv/fenshi_uv/add_uv/buy_uv | (全部 reference) | 无命中 | — | fund-api-docs 不覆盖用户行为/流量原始字段 | Mock/优先真实验证 |

---

## fund-indic-search-test 检索证据

```yaml
skill_name: "fund-indic-search-test"
execution_status: "SEARCH_COMPLETED"
skill_runtime_source: "Multica Runtime Skill: fund-indic-search-test (installed at ~/.claude/skills/fund-indic-search-test)"
source_used:
  - "~/.claude/fund-indic-config.json"
  - "sync_api: https://testfund.10jqka.com.cn/open/api/etf_rank/skills/fund/indic/v1/indic/sync"
keywords:
  - "sousuo_uv, sousuo_click_uv, fenshi_uv, add_uv, buy_uv, 收盘价, 成交额, 20日平均成交额, 日收益率, 标准差, 20日动量, Z分数, 搜索热度, 首购热度, 热度因子, 动量因子, 流动性因子, 低波因子, ETF分数, 排名分数, T日, T-1日, T-5日, T-19日, 交易日, 三级赛道"
failure_reason: "无"
can_be_used_as_admission_evidence: true
```

| execution_status | 查询关键词/指标线索 | source_used | 命中指标/数据 | 字段单位/值类型 | 时间口径 | 缺口 | 结论 |
|---|---|---|---|---|---|---|---|
| MATCHED | 日涨幅 | sync_api + indic_cache | `chgpct` (日涨幅) | unit=% type=NUMBER | SNAPSHOT | — | 可直接使用 [verified] |
| MATCHED | 热度 | sync_api + indic_cache | `heat` (热度值) | type=number | SNAPSHOT | 不同于 sousuo_uv/fenshi_uv 原始字段；为综合热度值，公式可能不同 | 可作为参考热度指标，但早盘宝热度因子需按指定公式自行计算 [default] |
| MATCHED | 成交额 | sync_api + indic_cache | `turnover` (成交额) | unit=元 type=number status=deprecated ⚠️ | — | 状态为 deprecated，不推荐使用；且非20日均值 | 需确认替代数据源或从行情接口取原始成交额自行计算20日均值 [default] |
| MATCHED | 单位净值 | sync_api + indic_cache | `unitNav` (单位净值), `unit_nav` (单位净值历史) | type=number | SNAPSHOT | — | 可直接使用，用于计算日收益率和动量因子 [verified] |
| MATCHED | 涨幅(多周期) | sync_api + indic_cache | `week/month/tmonth/hyear/year/nowyear` | unit=% type=NUMBER | SNAPSHOT | — | 可用于交叉校验，但早盘宝需自行计算动量因子 [verified] |
| MATCHED | 波动率 | sync_api + indic_cache | `annualizedVolatilityYear` (近1年年化波动率), `rsi` (净值波动), `rsi_pct` | — | SNAPSHOT | 不等于"最近20个交易日日收益率标准差"（低波因子定义） | 不可直接替代低波因子；低波因子需自行计算 [default] |
| MATCHED | ETF资金流 | sync_api + indic_cache | `etfNetBuyFlowAmount`, `etfNetBuyFlowAmount20d/5d/60d/Ytd`, `etfNetBuyFlowStreakCount`, `etf_main_capital_inflow` 等 | unit=元 | SNAPSHOT | — | 可用于辅助分析，但不直接参与早盘宝评分公式 [verified] |
| MATCHED | 搜索排名/自选排名 | sync_api + indic_cache | `searchRankDay/Week/Month/...` (planed), `selectRankDay/Week/Month/...` (planed) | — | planed | 状态均为 planed，非 online；不等同于 sousuo_uv/fenshi_uv | 不可用 — 仅 planed [pending] |
| NO_MATCH | sousuo_uv | sync_api + indic_cache | 无命中 | — | — | 指标库中不存在此字段 | 二轮决策：优先真实验证/不可取时 Mock [mock] |
| NO_MATCH | sousuo_click_uv | sync_api + indic_cache | 无命中 | — | — | 指标库中不存在此字段 | Mock [mock] |
| NO_MATCH | fenshi_uv | sync_api + indic_cache | 无命中 | — | — | 指标库中不存在此字段 | Mock [mock] |
| NO_MATCH | add_uv | sync_api + indic_cache | 无命中 | — | — | 指标库中不存在此字段 | Mock [mock] |
| NO_MATCH | buy_uv | sync_api + indic_cache | 无命中 | — | — | 指标库中不存在此字段 | Mock [mock] |
| NO_MATCH | 收盘价(独立指标) | sync_api + indic_cache | 无独立命中 | — | — | 收盘价可通过 unitNav 序列替代计算 | 使用 unitNav/adjNav 序列作为收盘价替代源 [default] |
| NO_MATCH | 三级赛道 | sync_api + indic_cache | 无命中 | — | — | 指标库中无赛道映射数据 | Mock [mock] |

---

## 能力-数据映射表 (AD)

| Row ID | 能力 | 需要的数据 | 数据用途 | 数据状态 | 公式/口径引用 | 缺失影响 | 是否阻塞 |
|---|---|---|---|---|---|---|---|
| AD-001 | ETF计算样本管理 | Mock ETF 列表（100个） | 确定参与计算的 ETF 范围 | Mock [mock] | — | 无法确定计算范围 | 否（Mock） |
| AD-002 | 热度排名计算 | sousuo_uv, sousuo_click_uv, fenshi_uv, add_uv, buy_uv (T日至T-19日) | 计算搜索热度Z分数和首购热度Z分数 | Mock/优先真实验证 [mock] | 热度因子 = 0.55*搜索热度Z + 0.45*首购热度Z | 热度因子无法计算 | 否（Mock兜底） |
| AD-003 | 动量排名计算 | T日收盘价 C_t, C_t-1, C_t-5 | 计算动量因子 = C_t-1/C_t-5 - 1 | 需计算 [default] | 动量因子 = C_t-1/C_t-5 - 1 | 动量因子无法计算 | 否（可从 unitNav 序列计算） |
| AD-004 | 流动性排名计算 | 近20个可用交易日成交额 | 计算流动性因子 = 20日均成交额 | 需计算 [default] | 默认假设：近20日成交额均值 | 流动性因子无法计算 | 否（默认假设） |
| AD-005 | 低波排名计算 | 最近22个交易日收盘价（用于计算20个日收益率） | 计算低波因子 = std(日收益率_t-20,...,日收益率_t-1) | 需计算 [default] | 低波因子 = std(20个日收益率) | 低波因子无法计算 | 否（可从 unitNav 计算） |
| AD-006 | ETF综合评分计算 | 热度/动量/流动性/低波排名结果 | 加权计算 ETF 分数 | 需计算 [default] | ETF分数 = 50%*热度排名分数 + 35%*动量排名分数 + 10%*流动性排名分数 + 5%*低波排名分数 | 综合评分无法计算 | 否 |
| AD-007 | Top5推荐 + 赛道展示 | ETF 分数排名、赛道映射表(Mock) | 取 Top5 ETF + 对应赛道 | 需计算 + Mock [mock] | — | 无法展示推荐 | 否（Mock赛道） |
| AD-008 | 谨慎参与/积极参与标签 | 计算样本内所有 ETF 的 20 日动量中位数 | 判定标签 | 需计算 [default] | 20日动量中位数 < -0.03 → 谨慎参与 | 标签无法生成 | 否 |
| AD-009 | 个基标签 | Mock 标签数据 | 展示每个 ETF 的标签 | Mock [mock] | — | 标签无法展示 | 否（Mock） |
| AD-010 | 资讯过滤 | Mock 资讯数据 | 返回过滤后的资讯 | Mock [mock] | — | 资讯模块为空 | 否（Mock） |
| AD-011 | 历史表现查询 | 历史 ETF 分数、历史行情数据(T-3及之前) | 展示历史推送的5个ETF、信号后3日涨幅 | 需落库 + 需计算 [default] | — | 历史模块为空 | 否 |
| AD-012 | 指南内容 | Mock/运营配置 | 存储并返回指南内容 | Mock/运营配置 [mock]/[pending] | — | 指南模块为空 | 否（Mock） |
| AD-013 | 预警订阅 | 用户订阅状态 | 管理用户订阅关系 | 新建 [pending] | — | 订阅功能不可用 | 否（新建功能） |
| AD-014 | 预警推送 | 最新计算结果、订阅用户列表、推送模板 | 数据计算完成后推送 | 新建 [pending] | — | 推送功能不可用 | 否（新建功能） |
| AD-015 | 一键加自选 | 当日早盘宝 ETF 列表、用户自选分组 | 加到"年月日早盘宝"分组 | 新建 [pending] | — | 自选功能不可用 | 否（仅验证结构） |

---

## 数据-接口映射表 (DI)

| Row ID | 数据 | 获取方式 | 来源接口/指标/配置 | 计算/加工规则 | 公式/口径引用 | 计算责任方 | 是否加工 | 是否落库 | 是否缓存 | 是否阻塞 |
|---|---|---|---|---|---|---|---|---|---|---|
| DI-001 | sousuo_uv等热度原始字段 | Mock/真实验证 | 外部数据源（待确认）/ Mock数据 | 若真实验证可用则直接读取；不可取时 Mock 生成 | — | 数据开发 | 是（清洗/格式化） | 是（历史回看需要T-19窗口） | 是 | 否（Mock兜底） |
| DI-002 | 收盘价（历史序列） | 复用 | `POST /quotation/data/query/v1/line` 或 `GET /quotation/fund_detail/v2/getNavData` (adjNav/unitNav) | 从行情接口按 ETF code + DAY_1 周期拉取 T-22 至 T 日数据 | — | 数据开发 | 是（提取收盘价序列） | 是 | 是 | 否 |
| DI-003 | 成交额（历史序列） | 复用/计算 | `POST /quotation/data/query/v1/table` (需确认 Tangram index_id) 或通过行情网关缓存接口 | 从行情接口拉取每日成交额 | — | 数据开发 | 是（计算20日均值） | 是 | 是 | 否 |
| DI-004 | 搜索热度Z分数 | 计算 | 基于 DI-001 (sousuo_uv, sousuo_click_uv) | T日搜索热度 = log(1+sousuo_uv+3*sousuo_click_uv); Z分数 = (T日值 - T-19至T日均值)/标准差 | 见 Issue 公式章节 | 数据开发 | 是 | 否（可即时计算） | 是（缓存中间结果） | 否 |
| DI-005 | 首购热度Z分数 | 计算 | 基于 DI-001 (fenshi_uv, add_uv, buy_uv) | T日首购热度 = log(1+fenshi_uv+5*add_uv+20*buy_uv); Z分数同上 | 见 Issue 公式章节 | 数据开发 | 是 | 否 | 是 | 否 |
| DI-006 | 热度因子 | 计算 | 基于 DI-004 + DI-005 | 热度因子 = 0.55*搜索热度Z + 0.45*首购热度Z | 见 Issue 公式章节 | 数据开发 | 是 | 是 | 是 | 否 |
| DI-007 | 动量因子 | 计算 | 基于 DI-002 (收盘价) | 动量因子 = C_t-1/C_t-5 - 1 | 见 Issue 公式章节 | 数据开发 | 是 | 是 | 是 | 否 |
| DI-008 | 流动性因子 | 计算 | 基于 DI-003 (成交额) | 流动性因子 = 近20个可用交易日成交额均值 | 默认假设 | 数据开发 | 是 | 是 | 是 | 否 |
| DI-009 | 低波因子 | 计算 | 基于 DI-002 (收盘价) | 日收益率_t = C_t/C_t-1 - 1; 低波因子 = std(20个日收益率) | 见 Issue 公式章节 | 数据开发 | 是 | 是 | 是 | 否 |
| DI-010 | ETF综合分数 | 计算 | 基于 DI-006~DI-009 排名结果 | 排名分数 = (总数-排名)/总数; ETF分数 = 加权求和 | 见 Issue 公式章节 | 数据开发 | 是 | 是 | 是 | 否 |
| DI-011 | ETF赛道映射 | Mock | Mock 映射表 | 本地静态映射表 | — | 数据开发 | 否 | 否（Mock配置） | 是 | 否 |
| DI-012 | 个基标签 | Mock | Mock 标签数据 | 静态标签配置 | — | 数据开发 | 否 | 否（Mock配置） | 是 | 否 |
| DI-013 | 资讯数据 | Mock | Mock 资讯响应 | Mock 生成 | — | 接口开发 | 否 | 否 | 否 | 否 |
| DI-014 | 历史表现数据 | 落库+查询 | 历史 ETF 分数表 + 历史行情数据 | 每日计算完成后落库；查询时读取历史记录 | — | 数据开发 | 是（落库+查询） | 是 | 是 | 否 |
| DI-015 | 指南内容 | Mock/运营配置 | Mock 配置或运营配置读取 | 存储并返回 | — | 接口开发 | 否 | 是 | 是 | 否 |
| DI-016 | 订阅关系 | 新建 | 新建订阅表 | 用户订阅/取消订阅 | — | 接口开发 | 是 | 是 | 是 | 否 |
| DI-017 | 推送模板 | Mock/运营配置 | Mock 推送模板 | 预留5个ETF名称和code占位 | — | 接口开发 | 否 | 是 | 是 | 否 |
| DI-018 | 自选分组 | 新建 | 新建自选分组接口 | 一键添加到"年月日早盘宝"分组；幂等设计 | — | 接口开发 | 是 | 是 | 否 | 否 |

---

## 接口-能力映射表 (IA)

| Row ID | 接口场景 | 接口具体功能 | 服务能力 | 处理方式 | 请求参数 | 返回字段 | 权限规则 | 空数据规则 | 错误/降级规则 | Mock |
|---|---|---|---|---|---|---|---|---|---|---|
| IA-001 | C端早盘宝首页数据 | 返回当日ETF分数Top5、赛道分布、样本信号日、谨慎参与/积极参与标签、个基标签 | AD-007, AD-008, AD-009 | 新增 | `date`(可选，默认最新) | `top5_etfs[]: {code, name, score, rank, sector, tags}`, `sectors[]: {name, etfs}`, `signal_date`, `market_tag`, `update_time` | 无需登录 [default] | 返回空列表 + 默认标签 | 数据未就绪返回特定状态码 | 否（真实计算+Mock赛道/标签） |
| IA-002 | C端资讯过滤 | 返回早盘宝相关资讯列表 | AD-010 | 新增 + Mock | `limit`, `offset` | `news[]: {title, summary, time, source, url}` | 无需登录 [default] | 返回空列表 | Mock 返回预设数据 | 是 |
| IA-003 | C端历史表现 | 返回历史日期推送的5个ETF及涨幅 | AD-011 | 新增 | `date` | `history[]: {date, etfs: [{code, name, signal_3d_return, current_return}]}` | 无需登录 [default] | 无历史数据返回空列表 | 不足3交易日涨幅返回"--" | 否 |
| IA-004 | 指南内容 | 返回运营配置的指南内容 | AD-012 | 新增/复用运营配置读取 | — | `guide: {content, update_time}` | 无需登录 [default] | 返回空 | 配置缺失返回空 | 是 |
| IA-005 | 预警订阅 | 用户订阅/取消订阅早盘宝推送 | AD-013 | 新增 | `action: subscribe/unsubscribe`, `user_id` | `status, message` | 暂默认有权限 [default] | — | 返回错误码 | 否 |
| IA-006 | 预警推送触发 | 数据计算完成后推送消息给已订阅用户 | AD-014 | 新增 | 内部触发（非C端直接调用） | 推送消息体（含5个ETF名称+code） | 暂默认有权限 [default] | 无订阅用户不推送 | 推送失败记录日志+重试 | 否 |
| IA-007 | 一键加自选 | 将当日早盘宝ETF加到自选分组 | AD-015 | 新增 | `user_id`, `date`(可选) | `status, added_count, failed_list` | 暂默认有权限 [default] | — | 部分失败返回明确错误；幂等设计 | 否（仅验证结构） |
| IA-008 | 运营配置读取 | 读取ETF计算样本配置 | AD-001 | 复用/新增 | — | `etf_list[]: {code, name}` | 内部接口 | 无配置返回空 | — | 是（Mock配置） |

---

## 软阻塞假设及PM接受记录

| 假设 | PM是否接受 | 影响范围 | 假设错误后的返工影响 |
|---|---|---|---|
| 热度原始字段不可取时使用 Mock 数据 | 是（二轮人工决策 #1） | 热度因子计算 | Mock数据替换为真实数据源，公式不变，返工量中等 |
| 交易日口径暂按自然日或最近可用交易日模拟 | 是（二轮人工决策 #2，暂不处理） | 所有时间窗口计算 | 需替换交易日历模块，返工量较小 |
| 流动性因子 = 近20个可用交易日成交额均值 | 是（二轮人工决策 #3） | 流动性因子计算 | 公式可能调整，返工量较小 |
| 边界行为按默认工程兜底（标准差0→Z分数0等） | 是（二轮人工决策 #4） | 边界case处理 | 兜底逻辑可能需要调整，返工量较小 |
| 并列同名次、后续顺延；分数2位小数；内部高精度 | 是（二轮人工决策 #5） | 排名和精度 | 规则可能调整，返工量较小 |
| 推送权限默认有权限 | 是（二轮人工决策 #9，暂不处理） | 推送链路 | 需增加权限校验，返工量中等 |
| Mock ETF 样本池 | 是（二轮人工决策 #11） | ETF计算范围 | 切换为运营平台配置，返工量较小 |
| 性能标准：离线<30min, C端P95<500ms, 预警异步 | 是（二轮人工决策 #12） | 架构设计 | 可能需要优化/加缓存/异步化，返工量中等 |
| ETF→三级赛道使用 Mock 映射表 | 是（二轮人工决策 #7，暂不处理） | 赛道展示 | 需切换为真实映射源，返工量较小 |
| AI 标签使用静态 Mock | 是（二轮人工决策 #6，暂不处理） | 标签展示 | 需接入AI服务，返工量中等 |
| 资讯使用 Mock 响应 | 是（二轮人工决策 #8，暂不处理） | 资讯模块 | 需接入真实资讯部门接口，返工量中等 |

---

## 验收标准

- 数据验收：ETF分数公式计算结果与预期一致；排名方向正确（热度DESC、动量DESC、流动性DESC、低波ASC）；Z分数计算口径正确
- 接口验收：请求参数、响应字段结构合理；空态、错误态行为正确
- 性能验收（默认假设）：离线/定时计算任务 < 30min；C端首页聚合接口 P95 < 500ms；预警异步处理
- 联调验收：前端页面（待前端提供）
- 不做范围验收：真实AI标签、真实资讯、真实权限、真实运营平台、最终交易日口径

---

## Routing 输入包

### 建议路由输入

| 子任务 | 建议对象 | 输入 | 输出 | 串行依赖 |
|---|---|---|---|---|
| 数据开发：评分计算+排名+标签+历史数据 | 数据开发 Agent | `.multica/admission_check.md` + Issue公式/口径 | ETF分数计算模块、排名模块、标签计算、历史数据落库/查询 | 无（可独立开始） |
| 接口开发：C端接口+订阅推送+一键加自选+指南 | 接口开发 Agent | `.multica/admission_check.md` + 接口契约 | 早盘宝首页接口、资讯Mock接口、历史表现接口、订阅/推送接口、一键加自选接口、指南接口 | 依赖数据开发产出 ETF分数/排名 数据（可先按Mock结构并行开发接口框架） |
| 测试与质量审核 | 测试与质量审核 Agent | 数据开发+接口开发产物 + `.multica/admission_check.md` | 测试报告、质量审核结论 | 依赖数据开发+接口开发完成 |

### 建议路由策略

- 数据开发与接口开发可并行启动（接口开发可先基于 Mock 数据定义接口结构，后续接入真实数据）
- 测试与质量审核必须在数据开发+接口开发均完成后执行
- 开发和测试必须区分 [verified]/[mock]/[default]/[pending] 四类状态

---

## 校验清单结果

### 1. 需求目标 — 通过
- ETF 早盘宝业务场景明确，已按页面模块/业务板块拆开（12个模块矩阵）
- 后端职责边界明确：评分计算、接口提供、资讯Mock、推送订阅、一键加自选
- 完成判定标准明确

### 2. 接口来源 — 软阻塞通过
- fund-api-docs 已完成筛选，命中5类reference
- 行情数据接口可复用；早盘宝C端接口需新建
- 订阅推送、一键加自选：无现有接口，需新建
- 资讯过滤：本轮Mock
- [pending] 真实资讯部门接口待确认

### 3. 指标与数据来源 — 软阻塞通过
- fund-indic-search-test 已完成检索，同步750条指标
- 收盘价/净值可复用 unitNav；热度原始字段 Mock
- 成交额指标 deprecated，需从行情接口取原始数据自行计算
- [pending] sousuo_uv等真实数据源待确认

### 4. 公式与数据口径 — 软阻塞通过
- 公式完整（ETF分数、热度因子、动量因子、流动性因子、低波因子、Z分数）
- 排名方向明确；精度/并列规则有默认假设
- [pending] 交易日口径、边界行为最终规则待确认

### 5. 运营输入与前端展示 — 软阻塞通过
- 运营配置本轮Mock
- 前端展示字段明确；空态/异常态有默认规则
- [pending] 运营平台真实配置入口

### 6. 推送、订阅、自选、历史和权限 — 软阻塞通过
- 推送触发时机、目标用户、消息模板明确
- 历史展示范围明确（T-3，最晚T-3）
- [pending] 真实权限判断、频控、失败重试

### 7. 验收标准 — 通过
- 数据验收、接口验收、性能验收标准明确
- 失败场景判断明确
- "不做什么"边界明确

### 8. 仓库与分支 — 通过
- 目标仓库: `https://github.com/jiajunli21/multicatest`
- 目标分支: `260525`
- repo-branch-safety-check: 待执行（准入读取已完成只读确认）

### 9. 系统性风险 — 软阻塞通过
- 并发幂等：评分计算幂等设计、一键加自选幂等设计已标记
- 数据一致性：落库与缓存一致性已标记
- [pending] 回滚方式待确认

---

## 准入结论

- 接口结论：部分复用（行情数据查询接口/基金详情接口/标签接口）+ 大量新增（早盘宝C端接口/订阅推送/一键加自选）
- 指标/数据结论：部分可直接使用（chgpct/unitNav/etfNetBuyFlowAmount等）+ 需自行计算（热度/动量/流动性/低波因子）+ Mock（sousuo_uv等/赛道映射/标签/资讯）
- 业务板块拆分：12个页面模块/业务板块
- 入场前开发方案：`.multica/admission_check.md`（本文件）
- 方案版本/时间戳：`Round 2 / 2026-05-25T09:45:00+08:00`
- 工作分支：`260525`
- commit SHA：`待生成`
- remote：`origin (https://github.com/jiajunli21/multicatest)`
- push 结果：`暂未推送`
- 剩余风险：
  - 11项 [pending] 待后续确认
  - 成交额指标 deprecated，需确认替代数据源
  - 所有使用 Mock/默认假设的项必须在输出中标记状态
- 下一步：`完成 commit+push 后进入 backend-task-routing`
