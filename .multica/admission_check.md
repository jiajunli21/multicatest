# Admission Check

## Current Effective Summary

- current_effective_round: `Round 1`
- current_status: `准入不通过`
- current_decision_time: `2026-06-01T11:45:00Z`
- current_issue_ref: `WS-33 (93d323a3-4c91-4cda-aff5-6722a1567b4e)`
- current_branch_ref: `agent/etf-leader-agent/6ebd3b81` / `target_branch: 260601`
- delivery_target_type: `流程验证版` (explicitly declared in Issue)
- effective_scope: 暂无（准入不通过）
- blocked_scope: 全部范围均处于阻塞状态
- effective_contract_maps: 暂无（准入不通过，无法形成完整映射）
- next_step: `等待 PM 补充后重新触发准入校验`

---

## Round History

### Round 1

- trigger_reason: `首次准入 — PM Agent 创建子 Issue WS-33 并 Assign 给 ETF 行情组后端 Leader Agent`
- trigger_source: `Assignee=ETF 行情组后端 Leader Agent via 子 Issue WS-33`
- trigger_conflict_check: `无多触发冲突`
- input_delta: `PM Issue WS-33 完整 Description（含业务背景、任务目标、接口信息、指标信息、公式口径、验收标准、待确认项）`
- evidence_delta: `fund-api-docs (REFERENCE_SEARCHED) + fund-indic-search-test (NO_MATCH)`
- blockers: 见下方阻塞项清单
- decision: `准入不通过 — 存在多项硬阻塞，无法进入 backend-task-routing`
- superseded_by: `NOT_SUPERSEDED`

---

## Skill Execution Evidence

### fund-api-docs

```yaml
skill_name: "fund-api-docs"
execution_status: "REFERENCE_SEARCHED"
skill_runtime_source: "/Users/lijiajun/.claude/skills/fund-api-docs"
source_used:
  - "references/reference-index.md"
  - "references/fund-rank-screening-reference.md"
  - "references/indicator-data-reference.md"
  - "references/recommendation-reference.md"
keywords:
  - "板块统计 ETF tab"
  - "行业主题 ETF"
  - "基金池 fund_pool/v2/query"
  - "uniqueType=etf_third_level_track_list"
  - "扶摇行情查询 stock_code"
  - "price_change_ratio_pct 涨幅"
  - "price_change_speed_ratio_pct 涨速"
  - "hq-fncdict-1771976 量比"
  - "etf_limit_up_stock_cnt 涨停数"
  - "成分股关系 etf_security"
  - "三市场全量股票涨幅 market_code 17/33/177"
  - "Redis 缓存 plateStatEtf:rank:data"
  - "BlockStatEtfTabTask"
evidence:
  - "命中: POST /quotation/data/query/v1/relation — ETF→成分股关系查询（stock_etf_subred），支持 etf_security_holdrate"
  - "命中: GET /quotation/data/query/gateway/cache/v1/relation/{code}/{type}/{relationships}/{entity_infos} — 网关缓存版关系查询"
  - "命中: POST /quotation/data/query/v1/table — 表格式指标查询（可用于查询成分股涨幅等）"
  - "命中: GET /quotation/data/query/gateway/cache/v1/table/{code}/{type}/{index_id} — 网关缓存版表格查询"
  - "命中: POST /quotation/etf_tab/hq_tab/v1/related_fund_list — ETF关联基金列表（板块→ETF映射）"
  - "命中: GET https://dq.10jqka.com.cn/fuyao/fund_rank/fund_rank/v1/fund_rank — 基金榜单/筛选"
  - "存在但未完整文档化: POST /quotation/fund_pool/v2/query — 基金池查询（仅 YApi 附录提及）"
  - "存在但未完整文档化: POST /quotation/fund_pool/v2/sort_filter_req — 基金池排序筛选"
  - "缺口: 扶摇(Fuyao)实时行情接口 — price_change_ratio_pct / price_change_speed_ratio_pct / hq-fncdict-1771976 / etf_limit_up_stock_cnt 等字段的查询接口 URL、请求体、响应结构均不在 fund-api-docs 覆盖范围内"
  - "缺口: 板块统计 ETF tab C 端业务接口 — 需新建，无现有接口可复用"
  - "缺口: 三市场(17/33/177)全量股票涨幅查询接口 — 不在 fund-api-docs 覆盖范围内"
failure_reason: "无"
can_be_used_as_admission_evidence: true
```

| execution_status | 查询关键词 / 线索 | source_used | 命中接口 / 资料 | 能力边界 | 缺口 | 结论 |
|---|---|---|---|---|---|---|
| REFERENCE_SEARCHED | 基金池 fund_pool/v2/query, uniqueType=etf_third_level_track_list | fund-rank-screening-reference.md | fund_pool/v2/query (仅YApi附录) | 基金池查询接口存在但未完整文档化 | 缺少详细请求参数/响应结构文档 | 需 PM 确认基金池接口文档或提供接口负责人 |
| REFERENCE_SEARCHED | 扶摇行情查询 stock_code, price_change_ratio_pct, price_change_speed_ratio_pct, hq-fncdict-1771976, etf_limit_up_stock_cnt | indicator-data-reference.md, fund-rank-screening-reference.md | 无命中 | fund-api-docs 不覆盖扶摇实时行情系统 | 核心 ETF 实时行情字段的查询接口 URL 完全缺失 | 阻塞 — 需 PM 提供扶摇接口 URL 或接口负责人联系方式 |
| REFERENCE_SEARCHED | 成分股关系 etf_security, etf_security_holdrate | indicator-data-reference.md | POST /quotation/data/query/v1/relation (stock_etf_subred) | 可查询 ETF→成分股映射，支持持仓占比字段 | 成分股涨幅需额外从扶摇获取 | 可复用 relation API，但成分股涨幅仍需扶摇 |
| REFERENCE_SEARCHED | 三市场全量股票涨幅 market_code 17/33/177 | indicator-data-reference.md | POST /quotation/data/query/v1/table | 表格式接口可批量查询股票指标 | 三市场全量涨幅查询具体 index_id 和参数不在文档中 | 需确认具体 index_id 和调用方式 |
| REFERENCE_SEARCHED | 板块统计 ETF tab C 端接口 | 全部 references | 无命中 | 无现有接口可复用 | 需新建 ETF tab 榜单接口 | 新建 — 接口路径/方法/参数待 PM 确认 |
| REFERENCE_SEARCHED | ETF tab 关联基金 | recommendation-reference.md | POST /quotation/etf_tab/hq_tab/v1/related_fund_list | 板块→ETF 映射查询，支持多种板块类型 | 返回的是关联基金列表，非排序榜单 | 可参考但不可直接复用 |

### fund-indic-search-test

```yaml
skill_name: "fund-indic-search-test"
execution_status: "NO_MATCH"
skill_runtime_source: "/Users/lijiajun/.claude/skills/fund-indic-search-test"
source_used:
  - "~/.claude/fund-indic-config.json (auth: configured / email: liujiaqing@myhexin.com)"
  - "sync_api: https://testfund.10jqka.com.cn/open/api/etf_rank/skills/fund/indic/v1/indic/sync"
  - "cache: valid (last_fetch_time: 2026-06-01T09:38:00Z, within 30min window)"
keywords:
  - "price_change_ratio_pct"
  - "price_change_speed_ratio_pct"
  - "hq-fncdict-1771976"
  - "etf_limit_up_stock_cnt"
  - "etf_security_holdrate"
  - "security_name"
  - "price_change"
  - "涨速"
  - "量比"
  - "涨停"
  - "limit_up"
  - "change_ratio"
evidence:
  - "未命中: price_change_ratio_pct — 实时行情指标，不在 fund-indic 指标库覆盖范围"
  - "未命中: price_change_speed_ratio_pct — 实时行情指标，不在 fund-indic 指标库覆盖范围"
  - "未命中: hq-fncdict-1771976 — 实时行情指标，不在 fund-indic 指标库覆盖范围"
  - "未命中: etf_limit_up_stock_cnt — 实时行情指标，不在 fund-indic 指标库覆盖范围"
  - "未命中: etf_security_holdrate — 关系数据字段，不在 fund-indic 指标库覆盖范围"
  - "fund-indic 指标库覆盖范围为基金级指标（收益、夏普、回撤、规模、费率等），不覆盖实时行情快照类指标"
failure_reason: "无（检索完成，但指标不在覆盖范围内）"
can_be_used_as_admission_evidence: true
```

| execution_status | 查询关键词 / 指标线索 | source_used | 命中指标 / 数据 | 字段单位 / 值类型 | 时间口径 | 缺口 | 结论 |
|---|---|---|---|---|---|---|---|
| NO_MATCH | price_change_ratio_pct | fund-indic cache (valid) | 无 | 不适用 | 不适用 | 实时行情指标不在 fund-indic 覆盖范围 | 需从扶摇实时行情系统获取，或通过 fund-api-docs 的 table API 自行查询行情数据后计算 |
| NO_MATCH | price_change_speed_ratio_pct | fund-indic cache (valid) | 无 | 不适用 | 不适用 | 同上 | 同上 |
| NO_MATCH | hq-fncdict-1771976 (量比) | fund-indic cache (valid) | 无 | 不适用 | 不适用 | 同上 | 同上 |
| NO_MATCH | etf_limit_up_stock_cnt | fund-indic cache (valid) | 无 | 不适用 | 不适用 | 同上 | 同上 |
| NO_MATCH | etf_security_holdrate | fund-indic cache (valid) | 无 | 不适用 | 不适用 | 关系数据字段 | 可从 fund-api-docs relation API (stock_etf_subred) 获取 |

**证据一致性自检**:
1. fund-api-docs.source_used 仅包含 reference 文件 (true)
2. fund-indic-search-test.source_used 仅包含认证配置和缓存来源 (true)
3. 无交叉引用情况 (true)
4. 无跨 Skill 替代情况 (true)
5. fund-indic-search-test 失败状态保留完整 (true)
6. 接口路径保留完整 /quotation 前缀 (true)

---

## 完整校验清单

### 1. 需求目标

- 业务场景: 用户在行情 App 进入 A 股→板块→板块统计页面，切换至新增的 ETF tab，查看 4 个排序项各自的前 9/后 9 榜单及领涨/领跌成分股信息
- 后端职责: 定时任务 BlockStatEtfTabTask 每分钟刷新榜单写入 Redis；C 端接口读取缓存返回榜单数据
- 能力边界: 仅 ETF tab，不涉及原有全部/行业/概念/风格 tab
- 完成判定: 定时任务可产出 8 份榜单写入 Redis；C 端接口可按排序项返回榜单；缓存链路正常
- 交付口径: 流程验证版
- **结论: 明确 ✓**

### 2. 接口来源

- fund-api-docs 已执行: REFERENCE_SEARCHED
- 已有可复用接口:
  - POST /quotation/data/query/v1/relation (成分股关系)
  - POST /quotation/etf_tab/hq_tab/v1/related_fund_list (板块→ETF 映射，可参考)
- 需要新建接口:
  - ETF tab C 端榜单业务接口 (路径/方法/参数待确认)
- 需要外部接口:
  - 扶摇实时行情查询 (URL 待补充)
  - 基金池 fund_pool/v2/query (接口存在但文档不全)
  - 三市场全量股票涨幅查询 (具体接口/index_id 待确认)
- 接口权限: 待确认
- **结论: 阻塞 ✗ — 扶摇接口 URL 完全缺失；ETF tab C 端接口契约未定义；接口权限规则未确认**

### 3. 指标与数据来源

- fund-indic-search-test 已执行: NO_MATCH
- 核心实时行情指标(price_change_ratio_pct, price_change_speed_ratio_pct, hq-fncdict-1771976, etf_limit_up_stock_cnt)不在 fund-indic 指标库覆盖范围
- 这些指标需从扶摇实时行情系统获取，但扶摇接口 URL 待补充
- 成分股持仓占比(etf_security_holdrate)可从 fund-api-docs relation API 获取
- **结论: 阻塞 ✗ — 核心实时行情指标的数据来源(扶摇)URL 缺失**

### 4. 公式与数据口径

- 公式: 4 个排序项分别取前 9(DESC)和后 9(ASC)；成分股交集计算领涨/领跌
- 时间口径: 实时快照(SNAPSHOT)或当前值(NOW)，每分钟刷新
- 未确认项:
  - 排序并列规则 (二级排序字段)
  - 百分比精度和小数位数
  - 停牌 ETF 是否纳入榜单
  - 非交易日定时任务行为
  - ETF 涨停数来源(扶摇 vs 基金池)
  - 除数为0的兜底策略
- **结论: 部分阻塞 ✗ — 公式主结构明确，但并列规则/精度/边界规则待确认**

### 5. 运营输入与前端展示

- 前端展示: 4 个排序项 tab 切换，8 份榜单数据一次返回
- 未确认项:
  - 前端是否需要成交额/换手率/溢价率等额外字段
  - 运营配置需求(排序项展示顺序/缓存刷新频率是否可配置)
- **结论: 部分阻塞 ✗ — 前端额外字段影响扶摇查询指标范围**

### 6. 推送、订阅、自选、历史和权限

- 推送: 不适用
- 历史: 不适用(仅当前快照)
- 自选: 待确认 ETF tab 榜单中的 ETF 是否支持一键加自选
- 权限: 待确认是否需要登录态、行情权限
- **结论: 部分阻塞 ✗ — 权限规则未确认，影响接口权限校验实现**

### 7. 验收标准

- 数据验收: 定时任务产出 8 份榜单写入 Redis，排序正确，领涨/领跌计算一致
- 接口验收: C 端接口返回正确，缓存链路正常，空态/错误态符合预期
- 性能验收: C 端毫秒级响应，定时任务单次不超过 30 秒
- 联调验收: 前端可正确展示和切换
- 不做范围: 不修改原有 tab，不涉及前端开发
- **结论: 基本明确，但精度/并发/权限等细节依赖待确认项 ✓(有条件)**

### 8. 仓库与分支

- 目标仓库: https://github.com/jiajunli21/multicatest.git **已确认 ✓**
- 目标分支: 260601 **已确认 ✓**
- 当前工作分支: agent/etf-leader-agent/6ebd3b81
- 分支模式: agent_branch_then_integrate
- repo-branch-safety-check: **通过 ✓**
- 读取入口: 代码目录结构待确认
- **结论: 仓库/分支已确认，但代码目录结构待确认**

### 9. 系统性风险

- 并发: 定时任务单实例执行，分布式锁策略待确认
- 数据一致性: Redis 和 Caffeine 最终一致，每分钟全量刷新无增量问题
- 兼容性: 需确认不影响板块统计原有 tab
- 生产配置: cron 配置管理、缓存过期时间、环境差异化待确认
- 回滚: 关闭定时任务 + 关闭 ETF tab 接口即可
- **结论: 部分阻塞 ✗ — 分布式锁/生产配置管理待确认**

---

## 入场前开发方案

**状态: 无法形成完整入场前开发方案（准入不通过）**

以下为基于当前已知信息的初步框架，待阻塞项解除后完善。

### 业务目标摘要

在板块统计模块新增 ETF tab，通过离线定时任务(每分钟)从基金池拉取行业主题 ETF 列表，查询扶摇实时行情并按涨幅/涨速/量比/涨停数分别取前 9/后 9 排名，同时计算每只入榜 ETF 的领涨/领跌成分股，将 8 份榜单写入 Redis；C 端接口通过 Caffeine→Redis 缓存链路返回榜单数据。

### 能力-数据映射表（初步框架，待确认）

| Row ID | 能力 | 需要的数据 | 数据用途 | 数据状态 | 公式/口径引用 | 是否阻塞 |
|---|---|---|---|---|---|---|
| AD-001 | 拉取行业主题 ETF 范围 | 基金池行业主题 ETF 列表(约90条) | 确定榜单样本范围 | 待确认(fund_pool/v2/query 文档不全) | Issue 样本范围章节 | 是(基金池接口文档待确认) |
| AD-002 | 查询 ETF 涨幅排序 | price_change_ratio_pct (ETF 涨幅) | 涨幅榜排序 | 待确认(扶摇接口 URL 缺失) | 前9 DESC / 后9 ASC | 是(扶摇 URL 缺失) |
| AD-003 | 查询 ETF 涨速排序 | price_change_speed_ratio_pct (ETF 涨速) | 涨速榜排序 | 待确认(扶摇接口 URL 缺失) | 前9 DESC / 后9 ASC | 是(扶摇 URL 缺失) |
| AD-004 | 查询 ETF 量比排序 | hq-fncdict-1771976 (ETF 量比) | 量比榜排序 | 待确认(扶摇接口 URL 缺失) | 前9 DESC / 后9 ASC | 是(扶摇 URL 缺失) |
| AD-005 | 查询 ETF 涨停数排序 | etf_limit_up_stock_cnt (ETF 涨停数) | 涨停数榜排序 | 待确认(数据来源待定: 扶摇 vs 基金池) | 前9 DESC / 后9 ASC | 是(数据来源待确认) |
| AD-006 | 查询 ETF 成分股关系 | stock_etf_subred (ETF→成分股映射) | 获取入榜 ETF 的成分股列表 | 可复用(relation API ✓) | 仅保留 17/33/177 市场 | 否 |
| AD-007 | 查询成分股涨幅 | 成分股 price_change_ratio_pct | 计算领涨/领跌股票 | 待确认(扶摇接口 URL 缺失) | 取前9第一只/后9第一只 | 是(扶摇 URL 缺失) |
| AD-008 | 查询三市场全量股票涨幅 | 17/33/177 全量股票涨幅 | 与成分股做交集 | 待确认(具体接口/index_id) | 交集计算 | 是(接口待确认) |
| AD-009 | 组装榜单写入 Redis | 全部榜单数据 | 写入 plateStatEtf:rank:data | 待确认(Redis key TTL) | Issue 响应字段章节 | 是(Redis TTL 待确认) |
| AD-010 | C 端接口缓存读取 | Caffeine + Redis 缓存数据 | 返回榜单给前端 | 部分待确认(Caffeine 过期/容量) | Caffeine→Redis→空兜底 | 是(缓存策略待确认) |

### 数据-接口映射表（初步框架，待确认）

| Row ID | 数据 | 获取方式 | 来源接口/指标/配置 | 计算/加工规则 | 计算责任方 | 是否阻塞 |
|---|---|---|---|---|---|---|
| DI-001 | 行业主题 ETF 列表 | 新增(调用外部接口) | fund_pool/v2/query (uniqueType=etf_third_level_track_list) | 提取 stockCode/name/tradeCode | 数据开发 | 是(接口文档不全) |
| DI-002 | ETF 涨幅/涨速/量比/涨停数 | 新增(调用外部接口) | 扶摇实时行情查询(URL 待补充) | 直接使用 | 数据开发 | 是(URL 缺失) |
| DI-003 | ETF→成分股映射 | 复用 | /quotation/data/query/v1/relation (stock_etf_subred) | 过滤市场 17/33/177 | 数据开发 | 否 |
| DI-004 | 成分股涨幅 | 新增(调用外部接口) | 扶摇实时行情查询(URL 待补充) | 取前9第一只/后9第一只 | 数据开发 | 是(URL 缺失) |
| DI-005 | 三市场全量股票涨幅 | 新增(调用外部接口) | 待确认(表格查询或扶摇) | 与成分股做交集 | 数据开发 | 是(接口待确认) |
| DI-006 | 榜单数据 Redis 缓存 | 新增(写入) | Redis key: plateStatEtf:rank:data | 组装 8 份榜单 JSON | 数据开发 | 是(TTL 待确认) |
| DI-007 | Caffeine 本地缓存 | 新增(配置) | Caffeine Cache | Caffeine→Redis→空兜底 | 接口开发 | 是(过期/容量待确认) |

### 接口-能力映射表（初步框架，待确认）

| Row ID | 接口场景 | 接口具体功能 | 处理方式 | 请求参数 | 权限规则 | 是否阻塞 |
|---|---|---|---|---|---|---|
| IA-001 | ETF tab C 端榜单接口 | 返回 4 个排序项各前9/后9 共 8 份榜单数据 | 新增 | 待确认 | 待确认 | 是(路径/参数/权限均待确认) |

---

## 阻塞项清单

### 硬阻塞（必须 PM 确认后才能进入开发）

| # | 阻塞项 | 影响范围 | 负责人 | 为什么阻塞 |
|---|---|---|---|---|
| BLK-001 | 扶摇实时行情接口 URL 缺失 | 数据开发(定时任务核心数据源) | 业务负责人(接口负责人) | 无法确定 ETF 涨幅/涨速/量比/涨停数的查询目标、请求格式和响应结构；定时任务无法实现 |
| BLK-002 | 扶摇成分股涨幅接口 URL 缺失 | 数据开发(领涨/领跌计算) | 业务负责人(接口负责人) | 无法查询成分股涨幅数据，领涨/领跌股票计算无法实现 |
| BLK-003 | 三市场(17/33/177)全量股票涨幅查询接口未确认 | 数据开发(交集计算) | 业务负责人(接口负责人) | 无法获取全量股票涨幅与 ETF 成分股做交集 |
| BLK-004 | ETF tab C 端接口路径/方法/请求参数未定义 | 接口开发 | 业务负责人(接口负责人) | 无法定义接口契约，前后端无法并行开发 |
| BLK-005 | 接口权限规则未确认(登录态/行情权限/无权限兜底) | 接口开发(权限校验) | 业务负责人(接口负责人) | 无法实现权限校验逻辑 |
| BLK-006 | ETF 涨停数数据来源未确认(扶摇 vs 基金池) | 数据开发 | 业务负责人(数据负责人) | 数据来源不一致可能导致数值差异 |
| BLK-007 | fund-indic-search-test 核心行情指标 NO_MATCH | 数据开发 | 数据负责人 / 系统限制 | 实时行情指标不在 fund-indic 覆盖范围，需明确替代数据方案 |

### 软阻塞（可基于假设先行开发，但需 PM 确认假设）

| # | 阻塞项 | 影响范围 | 负责人 | 建议假设 |
|---|---|---|---|---|
| SBLK-001 | Caffeine 缓存过期时间/容量策略 | 接口开发 | 业务负责人(接口负责人) | 假设: 过期时间 30s，最大容量 100，LRU 淘汰 |
| SBLK-002 | Redis key TTL | 数据开发 | 业务负责人(接口负责人) | 假设: TTL 2 分钟(略大于任务间隔) |
| SBLK-003 | 定时任务分布式锁策略 | 数据开发 | 业务负责人(接口负责人) | 假设: 使用 Redis SETNX 简单分布式锁 |
| SBLK-004 | 排序并列规则(二级排序) | 数据开发 | 业务负责人(数据负责人) | 假设: 按 stockCode 字典序作为二级排序 |
| SBLK-005 | 百分比精度和小数位数 | 数据开发/接口开发 | 业务负责人(数据负责人) | 假设: 涨幅/涨速保留 2 位小数，量比保留 2 位，持仓占比保留 2 位 |
| SBLK-006 | 停牌 ETF 处理 | 数据开发 | 业务负责人(数据负责人) | 假设: 停牌 ETF 不纳入榜单(涨幅缺失则不入榜) |
| SBLK-007 | 非交易日行为 | 数据开发/接口开发 | 业务负责人(数据负责人) | 假设: 定时任务正常执行但可能无数据，接口返回空榜单 |
| SBLK-008 | 前端额外展示字段(成交额/换手率/溢价率) | 数据开发/接口开发 | 业务负责人(产品负责人) | 假设: 本轮暂不包含额外字段，仅实现 Issue 列出的核心字段 |
| SBLK-009 | 一键加自选需求 | 接口开发 | 业务负责人(产品负责人) | 假设: 本轮暂不实现加自选功能 |
| SBLK-010 | 运营配置需求 | 数据开发/接口开发 | 业务负责人(运营负责人) | 假设: 本轮使用硬编码配置，不接入运营平台 |
| SBLK-011 | 定时任务 cron 配置管理 | 数据开发 | 业务负责人(接口负责人) | 假设: 使用本地配置文件，不接入配置中心 |
| SBLK-012 | 现有代码目录结构(ifund-quotaiton-job/ifund-hq-project) | 数据开发/接口开发 | 业务负责人(接口负责人) | 假设: 在现有项目约定目录下新增类文件 |
| SBLK-013 | 基金池 fund_pool/v2/query 接口详细文档 | 数据开发 | 业务负责人(接口负责人) | 假设: 接口请求/响应格式与查询码表.md 描述一致 |

---

## 根据 PM Battle SOP 的已确认项

### 当前已确认

- 业务目标: 板块统计新增 ETF tab，展示 4 个排序项的前 9/后 9 榜单及领涨/领跌成分股
- 涉及能力: 定时任务(BlockStatEtfTabTask) + C 端接口(缓存读取链路)
- 已确认数据: 基金池行业主题 ETF 列表(约90条)；ETF 名称/代码来自基金池；成分股持仓占比来自 relation API
- 已确认接口场景: 板块→ETF 映射(related_fund_list 可参考)；ETF→成分股关系(relation API 可复用)；基金榜单(fund_rank 可参考)
- 已确认范围: 不做原有 tab 修改；不实时回源；目标为流程验证版；Java 技术栈
- 仓库/分支: github.com/jiajunli21/multicatest.git / 260601 **已确认**

### fund-api-docs 总结

- 可复用: relation API(成分股关系)、table API(批量查询)、fund_rank(基金榜单参考)
- 存在但未完整文档化: fund_pool/v2/query(基金池)
- 完全缺失: 扶摇实时行情接口(ETF 涨幅/涨速/量比/涨停数 + 成分股涨幅)
- 需新建: ETF tab C 端接口

### fund-indic-search-test 总结

- 核心实时行情指标(price_change_ratio_pct, price_change_speed_ratio_pct, hq-fncdict-1771976, etf_limit_up_stock_cnt)不在指标库覆盖范围
- fund-indic 覆盖基金级指标(收益、夏普、回撤、规模等)，不覆盖实时行情快照指标

---

## 校验结论

- admission_id: `ADM-20260601-001`
- admission_time: `2026-06-01T11:45:00Z`
- admission_result: **准入不通过**
- blockers: 7 个硬阻塞项 + 13 个软阻塞假设项
- completion_type_ceiling: N/A (准入未通过)
- next_step: 等待 PM 补充扶摇接口 URL、接口契约定义、权限规则等阻塞项后重新触发准入
