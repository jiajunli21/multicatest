# Admission Check

## Current Effective Summary

- **current_effective_round**: `Round 1`
- **current_status**: `软阻塞通过`
- **current_decision_time**: `2026-06-01T09:40:00+08:00`
- **current_issue_ref**: `WS-26` (e2db02bb-83ab-413c-90d9-3d7ce35dbefa)
- **current_branch_ref**: `agent/etf-leader-agent/1cba6221` (based on `origin/260529` at `e7478f5`)
- **effective_scope**:
  - 数据开发：`ifund-quotaiton-job` BlockStatEtfTabTask 定时任务实现（骨架阶段可并行）
  - 接口开发：`ifund-hq-project` ETF tab C 端业务接口实现（依赖数据方案稳定后开始）
  - 测试审核：定时任务自测、接口自测、缓存行为验证
- **blocked_scope**:
  - 扶摇接口具体路径/接口名（speedRatio/volumeRatio 字段）→ 负责人：依赖方接口负责人
  - 并列排名二级排序规则 → 负责人：黄运锞
  - 各字段精度 → 负责人：黄运锞
  - 非交易时段行为 → 负责人：黄运锞
  - ETF tab 权限控制 → 负责人：产品负责人
  - 错误码和错误响应结构 → 负责人：接口开发负责人
- **effective_contract_maps**: `AD-001` ~ `AD-004`, `DI-001` ~ `DI-008`, `IA-001` ~ `IA-002`
- **next_step**: `进入 backend-task-routing`

---

## Round History

### Round 1

- **trigger_reason**: `首次准入`
- **input_delta**: `PM Issue WS-26 (板块统计ETF tab-数据与接口准入-第1轮)，首轮全新执行`
- **decision**: `软阻塞通过`

#### 校验 ID

`ADM-20260601-001`

#### Issue 标识

- Issue: `WS-26` (e2db02bb-83ab-413c-90d9-3d7ce35dbefa)
- 父 Issue: WS-25 (e941425c-00b1-4236-b888-5b0beb821c5c)
- 标题: 板块统计ETF tab-数据与接口准入-第1轮
- 需求来源: FS-38132

#### 当前仓库与分支

- 目标仓库: `https://github.com/jiajunli21/multicatest.git`
- Remote: `origin` → `https://github.com/jiajunli21/multicatest.git`
- 目标分支: `260529` (remote: `e7478f5d668801831b486d1efcf2784b84a9f03c`)
- 当前工作分支: `agent/etf-leader-agent/1cba6221`
- 基线分支: `260529` (待确认基线分支名称，当前以 `origin/260529` 作为默认基线)

#### 准入读取阶段 repo-branch-safety-check

- 目标仓库：已确认 → `https://github.com/jiajunli21/multicatest.git`
- 当前仓库 remote：一致
- 当前工作分支：`agent/etf-leader-agent/1cba6221`，based on `origin/260529`
- 工作区：clean
- 冲突标记：无
- 敏感信息：无
- 路径污染检测：通过
- 风险等级：无 P0 / 无 P1
- 结果：`通过`

---

## Skill 检索证据

### fund-api-docs

```yaml
skill_name: "fund-api-docs"
execution_status: "REFERENCE_SEARCHED"
skill_runtime_source: "/Users/lijiajun/.claude/skills/fund-api-docs/"
source_used:
  - "references/reference-index.md"
  - "references/indicator-data-reference.md"
  - "references/fund-rank-screening-reference.md"
  - "references/recommendation-reference.md"
keywords:
  - "板块统计"
  - "ETF tab"
  - "基金池"
  - "行业主题ETF"
  - "etf_third_level_track_list"
  - "扶摇ETF行情"
  - "涨幅"
  - "涨速"
  - "量比"
  - "涨停数"
  - "changeRatio"
  - "speedRatio"
  - "volumeRatio"
  - "limitUpCount"
  - "成分股关系"
  - "市场17"
  - "市场33"
  - "市场177"
  - "全量股票涨幅"
  - "plateStatEtf"
  - "BlockStatEtfTabTask"
  - "ifund-hq-project"
  - "ifund-quotaiton-job"
evidence:
  - "基金池接口: POST /quotation/fund_pool/v2/query (YApi附录, 详细文档缺失)"
  - "基金池接口: POST /quotation/fund_pool/v2/sort_filter_req (YApi附录, 详细文档缺失)"
  - "ETF行情表格式数据: POST /quotation/data/query/v1/table (可用, index_id来自Tangram)"
  - "ETF行情网关缓存: GET /quotation/data/query/gateway/cache/v1/table/{code}/{type}/{index_id} (可用)"
  - "成分股关系: POST /quotation/data/query/v1/relation (可用, relationships: stock_etf_subred)"
  - "成分股关系网关缓存: GET /quotation/data/query/gateway/cache/v1/relation/{code}/{type}/{relationships}/{entity_infos}"
  - "ETF榜单/排行: GET https://dq.10jqka.com.cn/fuyao/fund_rank/fund_rank/v1/fund_rank (支持ETF筛选typeList=[3])"
  - "关联基金列表: POST /quotation/etf_tab/hq_tab/v1/related_fund_list"
failure_reason: "无"
can_be_used_as_admission_evidence: true
```

| execution_status | 查询关键词/线索 | source_used | 命中接口/资料 | 能力边界 | 缺口 | 结论 |
|---|---|---|---|---|---|---|
| REFERENCE_SEARCHED | 基金池/行业主题ETF/etf_third_level_track_list | reference-index.md, indicator-data-reference.md | POST /quotation/fund_pool/v2/query, POST /quotation/fund_pool/v2/sort_filter_req | YApi附录中有记录，可查询基金池数据 | 详细请求/响应 schema 未在 reference 文件中；`uniqueType=etf_third_level_track_list` 参数未文档化 | 可用（需依赖方确认具体参数） |
| REFERENCE_SEARCHED | 扶摇ETF行情/changeRatio/speedRatio/volumeRatio/limitUpCount | reference-index.md, indicator-data-reference.md, fund-rank-screening-reference.md | POST /quotation/data/query/v1/table, GET .../gateway/cache/v1/table | 可通过 table 接口按 index_id 批量查询 ETF 指标 | 扶摇实时行情直连接口不在 fund-api-docs 覆盖范围；changeRatio/speedRatio/volumeRatio/limitUpCount 不是 fund-api-docs 中的标准 index_id | 扶摇接口需外部确认，本次准入以 table 接口 + Tangram index_id 作为兜底数据方案 |
| REFERENCE_SEARCHED | 成分股关系/市场17/33/177 | indicator-data-reference.md | POST /quotation/data/query/v1/relation (stock_etf_subred) | 可查 ETF 与成分股关系、持仓比例 | 文档未明确 market 17/33/177 过滤方式 | 可用（需在开发阶段确认过滤逻辑） |
| REFERENCE_SEARCHED | 板块统计ETF榜单/plateStatEtf | fund-rank-screening-reference.md | GET .../fund_rank?query={json} | 支持 ETF 类型筛选、多字段排序、分页 | 排序字段为基金收益类（week/month/year），不支持 changeRatio/speedRatio/volumeRatio/limitUpCount 直接排序 | 不适用于本次需求的排序维度，本次需自建排序逻辑 |
| REFERENCE_SEARCHED | ifund-hq-project/ifund-quotaiton-job/BlockStatEtfTabTask | N/A（工程模块，非业务接口） | 不适用 | 不适用 | 工程模块路径需在开发阶段确认 | 不适用 |

**接口结论**:
- **基金池接口**：已有接口（YApi 附录），需依赖方确认具体参数
- **扶摇ETF行情接口**：不在 fund-api-docs 覆盖范围，扶摇为独立行情系统
- **成分股关系接口**：已有接口，可用
- **ETF tab C 端业务接口**：需新建
- **三市场全量股票涨幅接口**：不在 fund-api-docs 覆盖范围，需确认扶摇或其他行情源

### fund-indic-search-test

```yaml
skill_name: "fund-indic-search-test"
execution_status: "SEARCH_COMPLETED"
skill_runtime_source: "https://testfund.10jqka.com.cn/open/api/etf_rank/skills/fund/indic/v1/indic/sync"
source_used:
  - "sync_api: https://testfund.10jqka.com.cn/open/api/etf_rank/skills/fund/indic/v1/indic/sync"
  - "auth_config: ~/.claude/fund-indic-config.json (email: liujiaqing@myhexin.com)"
  - "cache: indic_cache (updated 2026-06-01)"
keywords:
  - "changeRatio"
  - "speedRatio"
  - "volumeRatio"
  - "limitUpCount"
  - "涨幅"
  - "涨速"
  - "量比"
  - "涨停数"
  - "chgpct"
  - "topLeadStockCode"
  - "topLeadStockName"
  - "topLeadStockChangeRatio"
  - "bottomLeadStockCode"
  - "bottomLeadStockName"
  - "bottomLeadStockChangeRatio"
  - "成分股涨幅"
  - "领涨股"
evidence:
  - "chgpct: 日涨幅, unit=%, dataValueType=NUMBER, status=online, dataTypes=[SNAPSHOT] → 可直接使用"
  - "chgpct_1: 日涨幅-2, unit=%, status=online → 可直接使用"
  - "etfLimitUpStockCnt: etf涨停个股数, unit=个, status=online → 可直接使用"
  - "etfLimitUpStockPct: etf涨停含量占比, unit=%, status=online → 可直接使用"
  - "etfLimitUpStockCodeList: ETF涨停股代码列表, status=planed → 不可用"
  - "etfLimitUpStockList: ETF涨停股列表, status=planed → 不可用"
  - "upTrendChangeRatio: ETF主升浪区间涨幅, status=planed → 不可用"
  - "speedRatio: 0 matches → fund-indic 中无此指标"
  - "volumeRatio: 0 matches → fund-indic 中无此指标"
  - "topLeadStockCode/Name/ChangeRatio: 无直接匹配"
  - "bottomLeadStockCode/Name/ChangeRatio: 无直接匹配"
  - "成分股涨幅: 无直接 fund-indic 指标"
  - "领涨股: leadDaysHyearYear (领涨天数), status=planed → 不可用"
failure_reason: "无（同步成功，检索完成）"
can_be_used_as_admission_evidence: true
```

| execution_status | 查询关键词/指标线索 | source_used | 命中指标/数据 | 字段单位/值类型 | 时间口径 | 缺口 | 结论 |
|---|---|---|---|---|---|---|---|
| MATCHED | changeRatio/涨幅/chgpct | sync_api cache | chgpct (日涨幅), chgpct_1 (日涨幅-2) | %, NUMBER/SELECT | SNAPSHOT | 指标名称为"日涨幅"而非 "changeRatio"；数据源来自扶摇，非 fund-indic | 可直接使用 chgpct 作为涨幅排序字段 |
| MATCHED | limitUpCount/涨停数 | sync_api cache | etfLimitUpStockCnt (etf涨停个股数), etfLimitUpStockPct (etf涨停含量占比) | 个/%, number | SNAPSHOT | 指标名称为"涨停个股数"而非 "limitUpCount"；数据源来自扶摇 | 可直接使用 etfLimitUpStockCnt 作为涨停数排序字段 |
| NO_MATCH | speedRatio/涨速 | sync_api cache | 无匹配 | 不适用 | 不适用 | fund-indic 中无涨速指标；PM Issue 标明来自扶摇 | 需从扶摇实时行情接口获取，fund-indic 无法提供 |
| NO_MATCH | volumeRatio/量比 | sync_api cache | 无匹配 | 不适用 | 不适用 | fund-indic 中无量比指标；PM Issue 标明来自扶摇 | 需从扶摇实时行情接口获取，fund-indic 无法提供 |
| NO_MATCH | topLeadStockCode/Name/ChangeRatio (领涨成分股) | sync_api cache | 无直接匹配 | 不适用 | 不适用 | fund-indic 中无领涨成分股相关指标；本次需自行计算 | 数据方案：从成分股关系接口取成分股 → 从扶摇取三市场全量涨幅 → 本地交集取前9/后9第一只 |

**指标/数据结论**:
- `chgpct`（对应 changeRatio/涨幅）：fund-indic 中有可用指标，可直接使用
- `etfLimitUpStockCnt`（对应 limitUpCount/涨停数）：fund-indic 中有可用指标，可直接使用
- `speedRatio`（涨速）：fund-indic 中不存在 → 数据方案：需从扶摇实时行情接口获取原始涨速数据
- `volumeRatio`（量比）：fund-indic 中不存在 → 数据方案：需从扶摇实时行情接口获取原始量比数据
- `topLeadStockCode/Name/ChangeRatio`（领涨成分股）：fund-indic 中不存在 → 数据方案：需从成分股关系 + 三市场全量涨幅自行计算
- `bottomLeadStockCode/Name/ChangeRatio`（领跌成分股）：fund-indic 中不存在 → 同领涨计算逻辑

**继续推进依据**：
1. `fund-indic-search-test` 真实状态：`SEARCH_COMPLETED`，chgpct 和 etfLimitUpStockCnt 已命中，speedRatio 和 volumeRatio 为 `NO_MATCH`
2. 继续推进所依据的是人工确认的数据方案和软阻塞假设，不是替代 Skill 证据
3. speedRatio/volumeRatio 数据方案：由扶摇实时行情接口提供原始数据，定时任务直接拉取后排序；若扶摇接口暂不可用，允许先以 chgpct 和 etfLimitUpStockCnt 两维度开发验证，speedRatio/volumeRatio 维度后续补充
4. 领涨成分股数据方案：成分股关系接口（已有）→ 扶摇三市场全量涨幅接口（待确认路径）→ 本地交集排序取 top/bottom，不依赖 fund-indic

---

## 完整校验清单

### 1. 需求目标 → 通过

- ETF 行情场景：板块统计页面新增 ETF tab
- 已按页面模块拆分：定时刷新任务、C 端业务接口、前端展示
- 后端职责：定时任务（BlockStatEtfTabTask）+ 业务接口（ifund-hq-project）
- 完成判定：8 份榜单数据写入 Redis，业务接口正常返回，前端可展示
- 目标无冲突

### 2. 接口来源 → 软阻塞通过

- `fund-api-docs` 已执行（REFERENCE_SEARCHED）
- **已有可复用接口**：
  - 基金池：`POST /quotation/fund_pool/v2/query`
  - 成分股关系：`POST /quotation/data/query/v1/relation`（stock_etf_subred）
- **需外部确认接口**：
  - 扶摇实时行情接口（ETF changeRatio/speedRatio/volumeRatio/limitUpCount）
  - 扶摇三市场全量股票涨幅接口
- **需新建接口**：
  - ETF tab C 端业务接口（`ifund-hq-project`）
- 请求参数、响应结构：本轮暂以 FS-38132 第 4.1 节字段口径表作为默认契约
- 权限规则：待确认（软阻塞，不影响核心逻辑开发）

### 3. 指标与数据来源 → 软阻塞通过

- `fund-indic-search-test` 已执行（SEARCH_COMPLETED）
- 已有可用指标：chgpct（涨幅）、etfLimitUpStockCnt（涨停数）
- 缺失指标：speedRatio（涨速）、volumeRatio（量比）→ 来自扶摇，非 fund-indic 体系
- 领涨成分股字段：需自行计算，数据来源为成分股关系接口 + 三市场全量涨幅
- 缓存方案：Redis（key: `plateStatEtf:rank:data`）+ Caffeine 本地缓存
- 无 DB 落库需求

### 4. 公式与数据口径 → 软阻塞通过

- 公式：不涉及评分公式，排序逻辑明确（DESC/ASC 取前9后9）
- 样本范围：行业主题 ETF（约 90 条）
- 时间窗口：每分钟刷新（实时行情数据）
- 排序方向：4 维度 × 前9/后9，方向明确
- **待确认**：并列排名二级排序规则（软阻塞，不影响主逻辑）
- **待确认**：字段精度（软阻塞，开发阶段确认）
- **待确认**：非交易时段行为（软阻塞，开发阶段确认）

### 5. 运营输入与前端展示 → 通过（不适用）

- 运营配置：不适用
- 前端展示：8 份榜单数据（4 维度 × 前9/后9），字段明确
- 空态/异常态：缓存未命中返回空榜单结构

### 6. 推送、订阅、自选、历史和权限 → 软阻塞通过

- 推送触发：不适用
- 订阅：不适用
- 一键加自选：不适用
- 历史数据：不适用（每次覆盖最新数据）
- **待确认**：ETF tab 权限控制（软阻塞，不影响核心数据逻辑开发）

### 7. 验收标准 → 通过

- 数据验收：定时任务正常执行，Redis 8 份榜单数据可验证
- 接口验收：业务接口正常返回，缓存行为正确
- 性能验收：接口毫秒级响应，定时任务每分钟内完成
- 联调验收：前端可正常接入
- 不做范围明确：前端页面开发、运营平台配置

### 8. 仓库与分支 → 通过

- 目标仓库：`https://github.com/jiajunli21/multicatest.git` ✓
- 目标分支：`260529` ✓
- 当前工作分支：`agent/etf-leader-agent/1cba6221`（based on 260529）
- `repo-branch-safety-check`：通过

### 9. 系统性风险 → 通过

- 并发：定时任务幂等/加锁需求已识别
- 缓存击穿：Caffeine + Redis 双层缓存，风险可控
- 数据一致性：1 分钟延迟窗口属设计内行为
- 兼容性：原有板块统计 tab 不受影响
- 回滚方式：关闭定时任务 + 接口开关

---

## 入场前开发方案

### 1. 业务目标摘要

用户在行情-A股-板块-板块统计页面进入新增的 ETF tab，查看按涨幅、涨速、量比、涨停数四个排序维度的 ETF 榜单（每维度前 9 和后 9）。后端通过 `ifund-quotaiton-job` 定时任务每分钟从基金池、扶摇、成分股关系接口拉取数据计算榜单并写入 Redis，`ifund-hq-project` 提供 C 端业务接口读取缓存返回榜单数据。

### 2. 可开发范围

- 数据开发：`BlockStatEtfTabTask` 定时任务实现（可先以 chgpct/etfLimitUpStockCnt 两维度骨架开发，speedRatio/volumeRatio 待扶摇接口确认后补充）
- 接口开发：ETF tab C 端业务接口实现（`ifund-hq-project`），含 Caffeine+Redis 双层缓存
- 测试审核：定时任务自测、接口自测、缓存行为验证

### 3. 暂缓范围

| 暂缓项 | 暂缓原因 | 负责人 | 解除条件 |
|---|---|---|---|
| speedRatio（涨速）排序维度 | 扶摇实时行情接口路径待确认；fund-indic 无此指标 | 依赖方接口负责人（扶摇团队） | 扶摇接口路径确认后补充 |
| volumeRatio（量比）排序维度 | 同上 | 依赖方接口负责人（扶摇团队） | 扶摇接口路径确认后补充 |
| ETF tab 权限控制 | 产品未确认是否需要单独权限 | 产品负责人 | 产品确认权限规则 |
| 并列排名二级排序规则 | 业务口径待确认 | 黄运锞 | 确认二级排序字段 |
| 非交易时段行为 | 业务口径待确认 | 黄运锞 | 确认非交易时段是否需要刷新 |

### 4. 能力-数据映射表

| Row ID | 能力 | 需要的数据 | 数据用途 | 数据状态 | 公式/口径引用 | 缺失影响 | 是否阻塞 |
|---|---|---|---|---|---|---|---|
| AD-001 | ETF 榜单排序（涨幅维度） | changeRatio（ETF 涨幅） | 排序（DESC/ASC 取前9后9） | 已有（fund-indic: chgpct，亦可通过扶摇获取） | FS-38132 第 4.1 节 | 无 | 否 |
| AD-002 | ETF 榜单排序（涨速维度） | speedRatio（ETF 涨速） | 排序（DESC/ASC 取前9后9） | 需确认（来自扶摇，fund-indic 无此指标） | FS-38132 第 4.1 节 | 涨速维度榜单暂时无法产出；可先以其余三维度运行 | 是（影响涨速维度） |
| AD-003 | ETF 榜单排序（量比维度） | volumeRatio（ETF 量比） | 排序（DESC/ASC 取前9后9） | 需确认（来自扶摇，fund-indic 无此指标） | FS-38132 第 4.1 节 | 量比维度榜单暂时无法产出；可先以其余三维度运行 | 是（影响量比维度） |
| AD-004 | ETF 榜单排序（涨停数维度） | limitUpCount（ETF 涨停数） | 排序（DESC/ASC 取前9后9） | 已有（fund-indic: etfLimitUpStockCnt） | FS-38132 第 4.1 节 | 无 | 否 |
| AD-005 | 领涨成分股计算 | ETF 成分股列表 + 三市场全量股票涨幅 | 每只入榜 ETF 取成分股涨幅前9/后9第一只 | 成分股列表：已有（成分股关系接口）；三市场全量涨幅：待确认（扶摇） | FS-38132 第 4.1 节 | 成分股接口失败时领涨字段置空（允许降级） | 否（有降级方案） |
| AD-006 | 基金池 ETF 列表获取 | 行业主题 ETF 全量列表 | 确定参与排序的 ETF 范围 | 已有接口（POST /quotation/fund_pool/v2/query, uniqueType=etf_third_level_track_list） | FS-38132 | 基金池返回空时本次不覆盖 Redis 老数据 | 否 |

### 5. 数据-接口映射表

| Row ID | 数据 | 获取方式 | 来源接口/指标/配置 | 计算/加工规则 | 公式/口径引用 | 计算责任方 | 是否加工 | 是否落库 | 是否缓存 | 是否阻塞 |
|---|---|---|---|---|---|---|---|---|---|---|
| DI-001 | 行业主题 ETF 列表 | 复用外部接口 | POST /quotation/fund_pool/v2/query (uniqueType=etf_third_level_track_list) | 直接获取 stockCode 列表 | NOT_APPLICABLE | 数据开发 | 否 | 否 | 否（每次拉取） | 否 |
| DI-002 | ETF changeRatio（涨幅） | 复用外部接口 或 fund-indic | 扶摇ETF实时行情接口 或 fund-indic: chgpct | 直接读取，用于涨幅维度的 DESC/ASC 排序 | FS-38132 第 4.1 节 | 数据开发 | 否（直接使用） | 否 | 否（每次拉取） | 否 |
| DI-003 | ETF speedRatio（涨速） | 需确认（复用外部接口） | 扶摇ETF实时行情接口（路径待确认） | 直接读取，用于涨速维度的 DESC/ASC 排序 | FS-38132 第 4.1 节 | 数据开发 | 否（直接使用） | 否 | 否（每次拉取） | 是 |
| DI-004 | ETF volumeRatio（量比） | 需确认（复用外部接口） | 扶摇ETF实时行情接口（路径待确认） | 直接读取，用于量比维度的 DESC/ASC 排序 | FS-38132 第 4.1 节 | 数据开发 | 否（直接使用） | 否 | 否（每次拉取） | 是 |
| DI-005 | ETF limitUpCount（涨停数） | 复用外部接口 或 fund-indic | 扶摇ETF实时行情接口 或 fund-indic: etfLimitUpStockCnt | 直接读取，用于涨停数维度的 DESC/ASC 排序 | FS-38132 第 4.1 节 | 数据开发 | 否（直接使用） | 否 | 否（每次拉取） | 否 |
| DI-006 | ETF 成分股关系 | 复用已有接口 | POST /quotation/data/query/v1/relation (stock_etf_subred) | 查询入榜 ETF 的成分股列表，按 market 17/33/177 过滤 | FS-38132 第 5.1 节 | 数据开发 | 是（过滤三市场） | 否 | 否（每次拉取） | 否 |
| DI-007 | 三市场全量股票涨幅 | 需确认（复用外部接口） | 扶摇全量股票涨幅接口（路径待确认） | 与成分股列表交集后排序取前9/后9第一只 | FS-38132 第 4.1 节 | 数据开发 | 是（交集+排序） | 否 | 否（每次拉取） | 否（有降级方案：置空） |
| DI-008 | 榜单数据聚合 | 计算产出 | 以上全部数据源 | 4 维度 × 前9/后9 = 8 份榜单，每份含 ETF 基本字段 + 领涨成分股字段，组装后写入 Redis key `plateStatEtf:rank:data` | FS-38132 第 5.1 节 | 数据开发 | 是（聚合+组装） | 否（Redis 缓存） | 是（Redis + Caffeine） | 否 |

### 6. 接口-能力映射表

| Row ID | 接口场景 | 接口具体功能 | 服务能力 | 处理方式 | 请求参数 | 返回字段 | 权限规则 | 空数据规则 | 错误/降级规则 | Mock |
|---|---|---|---|---|---|---|---|---|---|---|
| IA-001 | 板块统计 ETF tab 数据查询 | 一次性返回 8 份榜单数据（4 排序维度 × 前9/后9），含领涨成分股字段 | ETF 榜单展示 | 新增（ifund-hq-project） | 待确认：是否需要板块/行业筛选条件（当前默认无参数，全量返回） | 8 份榜单数据：changeRatio/speedRatio/volumeRatio/limitUpCount 各 top9/bottom9；每项含 ETF code/name + topLeadStockCode/Name/ChangeRatio + bottomLeadStockCode/Name/ChangeRatio | 待确认（软阻塞） | 缓存均未命中时返回 8 份空数组结构 | 接口异常时返回兜底错误结构；具体错误码待确认 | 否 |
| IA-002 | 板块统计 ETF tab 定时刷新 | 每分钟执行：拉取基金池 → 查扶摇行情 → 排序取前9/后9 → 查成分股 → 算领涨股 → 组装榜单 → 写入 Redis | ETF 榜单数据生产 | 新增（ifund-quotaiton-job, BeanName: BlockStatEtfTabTask） | 不适用（内部定时任务） | Redis key `plateStatEtf:rank:data` 存储 8 份榜单 JSON | 不适用（内部任务） | 基金池为空/扶摇失败时不覆盖 Redis 老数据 | 成分股失败允许领涨字段置空；三市场涨幅失败允许成分股字段置空 | 否 |

### 7. 软阻塞假设

| 假设 | PM 是否接受 | 影响范围 | 假设错误后的返工影响 |
|---|---|---|---|
| 扶摇实时行情接口可提供 changeRatio/speedRatio/volumeRatio/limitUpCount 四个字段 | 依赖方接口负责人确认中 | speedRatio/volumeRatio 维度的榜单产出 | 若扶摇字段名或路径不同，需修改定时任务中的数据拉取逻辑（1-2 个文件） |
| 扶摇三市场全量股票涨幅接口可用 | 依赖方接口负责人确认中 | 领涨成分股计算 | 若接口不可用，领涨成分股字段只能置空，前端需展示空态 |
| ETF tab 无需单独权限控制 | 产品负责人确认中 | 接口权限层 | 若需权限，需在业务接口增加权限校验逻辑 |
| 无请求参数（全量返回 8 份榜单） | 接口开发负责人确认中 | 接口契约 | 若需参数，需修改接口签名和缓存 key 策略 |
| Caffeine 缓存 TTL 默认 30s | 接口开发负责人确认中 | 缓存行为 | 修改 TTL 配置即可，不影响核心逻辑 |

### 8. 验收标准

- 定时任务正常执行 → Redis 中 8 份榜单数据可验证排序正确性
- 业务接口正常返回 8 份榜单数据 → Caffeine/Redis 缓存行为正确
- 业务接口毫秒级响应（缓存命中）
- 前端可正常接入并切换 4 个排序维度
- 原有板块统计 tab 不受影响

### 9. Routing 输入包

| 子任务 | 建议对象 | 输入 | 输出 | 串行依赖 |
|---|---|---|---|---|
| 数据开发：BlockStatEtfTabTask 定时任务 | 数据开发 Agent | .multica/admission_check.md（本文件），FS-38132 第 5.1 节伪代码 | 定时任务实现代码 + 自测报告 + handoff | 无（可独立开始） |
| 接口开发：ETF tab C 端业务接口 | 接口开发 Agent | .multica/admission_check.md（本文件），FS-38132 字段口径表，Redis key 契约 | 业务接口实现代码 + 自测报告 + handoff | 依赖数据方案稳定（数据开发完成后或并行开发以 Mock Redis 数据） |
| 测试与质量审核 | 测试与质量审核 Agent | 数据开发 handoff + 接口开发 handoff + 本文件验收标准 | 测试报告 + QA handoff | 依赖数据开发和接口开发均完成 |

---

## 准入结论

- **准入结果**: `软阻塞通过`
- **接口结论**: 复用（基金池、成分股关系）+ 外部确认（扶摇行情接口）+ 新建（ETF tab 业务接口）
- **指标/数据结论**: 已有（chgpct/日涨幅、etfLimitUpStockCnt/涨停数）+ 需外部确认（speedRatio、volumeRatio）+ 需自行计算（领涨成分股字段）
- **业务板块拆分**: ETF 榜单定时刷新任务、ETF tab C 端业务接口
- **入场前开发方案**: `.multica/admission_check.md`（本文件）
- **方案版本/时间戳**: v1.0 / 2026-06-01T09:40:00+08:00
- **工作分支**: `agent/etf-leader-agent/1cba6221`
- **commit SHA**: 待提交
- **remote**: origin → https://github.com/jiajunli21/multicatest.git
- **push 结果**: 待推送
- **剩余风险**:
  1. speedRatio/volumeRatio 扶摇接口路径未确认，可能影响涨速/量比两维度榜单开发
  2. 三市场全量股票涨幅接口未确认，影响领涨成分股计算
  3. ETF tab 权限规则未确认，可能需后期增加权限校验
- **下一步**: `进入 backend-task-routing`

---
- **superseded_by**: `NOT_SUPERSEDED`
