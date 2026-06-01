# Admission Check

## Current Effective Summary

- current_effective_round: `Round 1`
- current_status: `准入不通过`
- current_decision_time: `2026-06-01T08:08:12Z`
- current_issue_ref: `WS-31 (dd5c4a66-a7be-4412-9ec6-b0097e47d853)`
- current_branch_ref: `agent/etf-leader-agent/70f37b7f` / `origin/260601`
- effective_scope: `无（准入未通过，无可开发范围）`
- blocked_scope: `全部范围（15 项待确认 + 指标系统 speedRatio/volumeRatio 缺失）`
- effective_contract_maps: `无法形成（准入未通过）`
- next_step: `等待 PM 补充，当前轮准入结束`

## Repo-Branch Safety Check

```
## repo-branch-safety-check 结果：通过（只读阶段）
- 目标仓库：https://github.com/jiajunli21/multicatest.git / 配置来源：Issue WS-31
- 当前仓库 remote：一致 / 基线分支：260601
- 当前工作分支：agent/etf-leader-agent/70f37b7f (tracking origin/260601)
- 分支模式：agent_branch_then_integrate / source branch 可消费 / 待 Leader 集成
- push 目标：origin / push 条件：具备
- 工作区：clean
- 冲突标记：无 / 敏感信息：无
- 路径污染检测：通过
- 扩展检查：不涉及（当前为只读准入阶段）
- 风险等级：无 P0 / 无 P1 / 无 P2
```

## Round History

### Round 1

- trigger_reason: `首次准入（PM Agent 创建子 Issue WS-31）`
- input_delta: `PM Issue WS-31 板块统计新增ETF tab-数据与接口准入-第1轮`
- decision: `准入不通过`
- superseded_by: `NOT_SUPERSEDED`

---

## 1. Skill 执行证据

### fund-api-docs

```yaml
skill_name: "fund-api-docs"
execution_status: "REFERENCE_SEARCHED"
skill_runtime_source: "Multica runtime Skill: /Users/lijiajun/.claude/skills/fund-api-docs"
source_used:
  - "references/reference-index.md"
  - "references/fund-rank-screening-reference.md"
  - "references/indicator-data-reference.md"
  - "references/recommendation-reference.md"
keywords:
  - "板块统计"
  - "ETF tab"
  - "ETF 榜单"
  - "ETF 排行"
  - "涨幅排名"
  - "涨速排名"
  - "量比排名"
  - "涨停数排名"
  - "基金池"
  - "行业主题 ETF"
  - "扶摇行情"
  - "成分股"
  - "成分股关系"
  - "plateStatEtf"
  - "BlockStatEtfTabTask"
failure_reason: "无"
can_be_used_as_admission_evidence: true
```

| execution_status | 查询关键词 / 线索 | source_used | 命中接口 / 资料 | 能力边界 | 缺口 | 结论 |
|---|---|---|---|---|---|---|
| REFERENCE_SEARCHED | 成分股、成分股关系 | indicator-data-reference.md | `POST /quotation/data/query/v1/relation` (stock_etf_subred)、`GET /quotation/data/query/gateway/cache/v1/relation/{code}/{type}/{relationships}/{entity_infos}` | 可查询 ETF 与成分股的关系数据（含持有比例等字段） | 不确认是否返回市场代码用于过滤 17/33/177 | 可复用（需确认返回字段是否含市场代码） |
| REFERENCE_SEARCHED | ETF 行情、扶摇行情 | indicator-data-reference.md | `POST /quotation/data/query/v1/table`、`GET /quotation/data/query/gateway/cache/v1/table/{code}/{type}/{index_id}` | 可批量查询 ETF 的表格类指标数据（需指定 index_id） | 不确认 changeRatio/speedRatio/volumeRatio/limitUpCount 对应的扶摇 index_id | 可复用（需确认 index_id 映射） |
| REFERENCE_SEARCHED | ETF 榜单、ETF 排行、涨幅排名 | fund-rank-screening-reference.md | `GET https://dq.10jqka.com.cn/fuyao/fund_rank/fund_rank/v1/fund_rank` | 按时间段收益（周/月/年）排序的基金榜单 | 不支持实时行情维度（涨速/量比/涨停数）排序，不支持领涨成分股 | 不适用（能力不匹配） |
| REFERENCE_SEARCHED | 基金池、行业主题 ETF | reference-index.md (YApi 附录) | `/quotation/fund_pool/v2/query`（YApi 提及但不在主覆盖范围）、`/quotation/fund_pool/v2/sort_filter_req`（同上） | 基金池查询和筛选 | 接口文档不在 fund-api-docs 主覆盖范围，参数和响应结构未确认 | 阻塞（接口文档缺失） |
| REFERENCE_SEARCHED | 市场全量股票涨幅 | indicator-data-reference.md | `POST /quotation/data/query/v1/table` | 可批量查询股票行情指标（需指定 index_id 和 codes） | 不确认"全量股票涨幅"对应的 index_id | 可复用（需确认 index_id） |
| REFERENCE_SEARCHED | ETF tab 业务接口 | fund-rank-screening-reference.md, recommendation-reference.md | 无直接匹配 | N/A | 无现有接口提供 "ETF tab 4维度 top/bottom 9 榜单 + 领涨成分股" 功能 | 需新建 |
| REFERENCE_SEARCHED | ETF tab 关联基金 | recommendation-reference.md | `POST /quotation/etf_tab/hq_tab/v1/related_fund_list` | 板块/指数 → 关联 ETF 列表 | 不支持按 changeRatio/speedRatio/volumeRatio/limitUpCount 排序 | 不适用（场景不同） |

**fund-api-docs 结论**：
- 成分股关系查询接口：**可复用**，需确认返回字段是否含市场代码
- 行情数据查询接口（table）：**可复用**，需确认各字段对应的扶摇 index_id
- 基金池查询接口：**阻塞**，接口文档不在主覆盖范围
- ETF tab 业务接口：**需新建**，无现有接口
- 扶摇市场全量股票涨幅查询：**可复用** table 接口，需确认 index_id

### fund-indic-search-test

```yaml
skill_name: "fund-indic-search-test"
execution_status: "MATCHED"  # 部分关键词命中，speedRatio/volumeRatio 为 NO_MATCH
skill_runtime_source: "Multica runtime Skill: /Users/lijiajun/.claude/skills/fund-indic-search-test"
source_used:
  - "~/.claude/fund-indic-config.json"
  - "sync_api: https://testfund.10jqka.com.cn/open/api/etf_rank/skills/fund/indic/v1/indic/sync"
  - "indic_cache (750 indicators, last_fetch: 2026-06-01T09:38:00Z)"
keywords:
  - "changeRatio"
  - "涨幅"
  - "speedRatio"
  - "涨速"
  - "volumeRatio"
  - "量比"
  - "limitUpCount"
  - "涨停数"
  - "领涨股"
  - "成分股涨幅"
  - "chgpct"
failure_reason: "speedRatio 和 volumeRatio 在指标系统中无任何匹配"
can_be_used_as_admission_evidence: true  # 部分匹配，但 speedRatio/volumeRatio 的 NO_MATCH 状态本身也是证据
```

| execution_status | 查询关键词 / 指标线索 | source_used | 命中指标 / 数据 | 字段单位 / 值类型 | 时间口径 | 缺口 | 结论 |
|---|---|---|---|---|---|---|---|
| MATCHED | changeRatio, 涨幅, chgpct | indic_cache | `chgpct`（日涨幅）、`chgpct_1`（日涨幅-2） | unit=%, type=NUMBER | 日级别（SNAPSHOT） | changeRatio 是否等同于日涨幅 chgpct 需确认；若需实时涨幅需确认数据源 | 需确认口径后可用 |
| NO_MATCH | speedRatio, 涨速 | indic_cache | 无匹配 | N/A | N/A | 指标系统中不存在涨速指标 | 需从扶摇实时行情直接获取 |
| NO_MATCH | volumeRatio, 量比 | indic_cache | 无匹配 | N/A | N/A | 指标系统中不存在量比指标 | 需从扶摇实时行情直接获取 |
| MATCHED | limitUpCount, 涨停数 | indic_cache | `etfLimitUpStockCnt`（ETF涨停个股数）、`etfLimitUpStockPct`（ETF涨停含量占比） | unit=个/% | SNAPSHOT | `etfLimitUpStockCnt` 是 ETF 持仓股中涨停的个数，而非 ETF 自身的涨停数 | 可替代使用（需确认 PM 是否接受此口径） |
| NO_MATCH | 领涨股、topLeadStock | indic_cache | 无直接匹配 | N/A | N/A | 领涨成分股指标不存在于指标系统 | 需自行计算（成分股涨幅交集取前/后9第一只） |
| MATCHED | 重仓涨幅 | indic_cache | `heavyRate`（重仓涨幅） | unit=%, status=offline | SNAPSHOT | 状态为 offline，不可用于生产 | 不可用 |

**fund-indic-search-test 结论**：
- `chgpct`（日涨幅）可用但需确认是否等价于 changeRatio
- `etfLimitUpStockCnt`（ETF涨停个股数）可用，但含义是"持仓股中涨停个数"而非"ETF自身涨停数"
- `speedRatio`（涨速）：**完全缺失**，需从扶摇实时行情系统获取
- `volumeRatio`（量比）：**完全缺失**，需从扶摇实时行情系统获取
- 领涨成分股：**不存在**，需自行计算

### 证据一致性自检

1. fund-api-docs 的 source_used 只包含 reference 文件：✅
2. fund-indic-search-test 的 source_used 只包含认证配置、缓存来源：✅
3. 无 /quotation/... 接口路径填入 fund-indic-search-test：✅
4. 无 fund-indic-search-test 同步 URL 填入 fund-api-docs：✅
5. speedRatio/volumeRatio NO_MATCH 状态已保留，继续推进需人工确认数据方案：✅
6. 接口路径使用 fund-api-docs reference 中完整路径：✅

---

## 2. 完整校验清单

### 1. 需求目标 — 明确 ✅

- 场景：用户在行情 A 股板块统计页面新增 ETF tab
- 后端职责：定时任务（BlockStatEtfTabTask）+ 业务接口（ETF tab API）
- 完成判定：定时任务产出 Redis 数据 + 接口返回 8 份榜单 + 前端可展示

### 2. 接口来源 — 部分明确 ⚠️

- fund-api-docs 已执行：REFERENCE_SEARCHED
- 成分股关系接口：可复用，需确认返回字段含市场代码
- 行情数据查询：可复用 table 接口，需确认 index_id 映射
- 基金池查询接口：接口文档缺失，阻塞
- ETF tab 业务接口：需新建，请求参数/响应字段/路径均待确认
- **阻塞项**：基金池接口文档缺失、ETF tab 接口契约未确认、扶摇字段映射未确认

### 3. 指标与数据来源 — 部分明确 ⚠️

- fund-indic-search-test 已执行：部分 MATCHED / 部分 NO_MATCH
- chgpct（日涨幅）可用
- etfLimitUpStockCnt（ETF涨停个股数）可用
- speedRatio 完全缺失
- volumeRatio 完全缺失
- **阻塞项**：speedRatio/volumeRatio 在指标系统中不存在，需确认扶摇实时行情获取方式

### 4. 公式与数据口径 — 部分明确 ⚠️

- 排序规则：4 维度 DESC/ASC 取前 9/后 9 — 明确
- 样本范围：uniqueType=etf_third_level_track_list 约 90 条 — 明确
- 并列规则：待确认
- 字段单位精度：待确认
- 榜单不足 9 条规则：待确认
- 市场代码 17/33/177：待确认
- **阻塞项**：市场代码口径、字段单位精度、不足 9 条规则

### 5. 运营输入与前端展示 — 不适用（本次不涉及运营后台配置）

### 6. 推送、订阅、自选、历史和权限 — 部分明确 ⚠️

- 推送/订阅/自选：不适用
- 历史数据：不适用
- 权限规则：待确认（ETF tab 入口权限、无权限兜底）
- **阻塞项**：权限规则

### 7. 验收标准 — 明确 ✅

- 数据验收、接口验收、性能验收、联调验收均有样例

### 8. 仓库与分支 — 明确 ✅

- 目标仓库：https://github.com/jiajunli21/multicatest.git
- 目标分支：260601
- repo-branch-safety-check 只读阶段：通过

### 9. 系统性风险 — 部分明确 ⚠️

- 并发与幂等：无风险（每分钟覆盖同一 key）
- 数据一致性：Caffeine/Redis 短暂不一致可接受
- 回滚方式：待确认（功能开关）
- **阻塞项**：功能开关

---

## 3. 准入结果

**准入不通过**

### 硬阻塞项

| 序号 | 阻塞项 | 负责人 | 影响 |
|---|---|---|---|
| 1 | **speedRatio（涨速）在指标系统中不存在** | 扶摇负责人 / 黄运锞 | 无法确认涨速数据来源和字段映射 |
| 2 | **volumeRatio（量比）在指标系统中不存在** | 扶摇负责人 / 黄运锞 | 无法确认量比数据来源和字段映射 |
| 3 | **基金池接口文档缺失**（/quotation/fund_pool/v2/query 不在 fund-api-docs 主覆盖范围） | 基金池负责人 | 无法确定基金池调用方式（路径/参数/响应） |
| 4 | **扶摇 ETF 行情字段映射未确认**（changeRatio/speedRatio/volumeRatio/limitUpCount 对应扶摇字段名） | 扶摇负责人 | 无法确认行情字段获取方式 |
| 5 | **成分股关系接口返回字段未确认**（是否含市场代码用于过滤 17/33/177） | 成分股关系负责人 | 无法确认成分股过滤方式 |
| 6 | **市场代码 17/33/177 口径未确认** | 黄运锞 | 无法确认市场过滤规则 |
| 7 | **ETF tab 业务接口契约未确认**（路径/请求参数/响应字段完整定义） | 前端 + 后端接口负责人 | 无法确定接口契约 |
| 8 | **ETF tab 权限规则未确认**（登录态/产品权限/无权限兜底） | 姜文迪 | 无法确认权限兜底逻辑 |
| 9 | **ifund-quotaiton-job 和 ifund-hq-project 代码仓库路径未确认** | 后端接口负责人 | 无法定位代码入口 |

### 软阻塞项

| 序号 | 软阻塞项 | 负责人 | 影响 |
|---|---|---|---|
| 1 | 同值并列二级排序规则 | 黄运锞 | 不影响准入但影响排序确定性 |
| 2 | 榜单不足 9 条处理规则 | 黄运锞 | 无法确认榜单长度规则 |
| 3 | 字段单位精度 | 黄运锞 | 不影响准入但影响前端展示 |
| 4 | 非交易时段行为 | 黄运锞 | 无法确认非交易日行为 |
| 5 | Caffeine 缓存配置 | 后端接口负责人 | 不影响准入但影响上线稳定性 |
| 6 | 功能开关 | 后端接口负责人 | 不影响准入但影响上线安全 |
| 7 | 依赖方负责人和时间节点 | 王奕乾（PM） | 无法确认排期 |

### 阻塞项分类

- 数据来源阻塞（需外部负责人确认）：#1, #2, #3, #4, #5, #6
- 接口契约阻塞（需前端+后端确认）：#7
- 权限阻塞（需安全/产品确认）：#8
- 开发环境阻塞（需后端确认）：#9

## 4. 已确认信息

- 业务目标：板块统计页面新增 ETF tab，展示行业主题 ETF 4 维度前 9/后 9 榜单 + 领涨成分股
- 技术方案：定时任务拉取基金池→扶摇行情→排序→成分股交集→写 Redis；业务接口读 Caffeine→Redis
- 不做范围：前端 UI 开发、运营后台配置
- 期望交付口径：流程验证版
- 技术栈：Java
- 目标仓库：https://github.com/jiajunli21/multicatest.git
- 目标分支：260601
- fund-api-docs 已完成检索并给出可复用接口
- fund-indic-search-test 已完成检索并记录命中/缺失状态

## 5. 已有工作分支参考（非本轮产物）

在同一仓库中发现以下相关分支（来自可能的历史运行，本轮不依赖）：

- `agent/etf-leader-agent/1cba6221`：admission: Round 1 板块统计ETF tab 准入结论（软阻塞通过）
- `agent/data-dev/1f76844d`：feat: implement BlockStatEtfTabTask for ETF board statistics
- `agent/intf-dev/1d4fd289`：feat(ifund-hq-project): ETF tab C端业务接口实现

本轮为全新执行，不继承上述分支结论。

## 6. 入场前开发方案

**准入未通过，无法形成入场前开发方案。**

以下仅为草案框架，待阻塞项解除后完善：

### 能力-数据映射表（草案）

| Row ID | 能力 | 需要的数据 | 数据用途 | 数据状态 | 公式 / 口径引用 | 是否阻塞 |
|---|---|---|---|---|---|---|
| AD-001 | ETF 涨幅排名（前9/后9） | ETF changeRatio | 排序 | 待确认（chgpct 可替代但口径待确认） | NOT_APPLICABLE: 直接排序 | 是 |
| AD-002 | ETF 涨速排名（前9/后9） | ETF speedRatio | 排序 | 待确认（指标系统无此指标） | NOT_APPLICABLE: 直接排序 | 是 |
| AD-003 | ETF 量比排名（前9/后9） | ETF volumeRatio | 排序 | 待确认（指标系统无此指标） | NOT_APPLICABLE: 直接排序 | 是 |
| AD-004 | ETF 涨停数排名（前9/后9） | ETF limitUpCount | 排序 | 待确认（etfLimitUpStockCnt 可替代但含义不同） | NOT_APPLICABLE: 直接排序 | 是 |
| AD-005 | 领涨成分股 | 成分股列表 + 三市场全量股票涨幅 | 展示 | 待确认（需成分股接口+涨幅数据+交集计算） | 成分股涨幅前9第一只=领涨；后9第一只=领跌 | 是 |
| AD-006 | 行业主题 ETF 列表获取 | 基金池 uniqueType=etf_third_level_track_list | 样本范围 | 待确认（基金池接口文档缺失） | NOT_APPLICABLE | 是 |
| AD-007 | ETF 行情数据批量查询 | 扶摇行情字段（changeRatio/speedRatio/volumeRatio/limitUpCount） | 排序输入 | 待确认（扶摇 index_id 映射未确认） | NOT_APPLICABLE | 是 |

### 数据-接口映射表（草案）

| Row ID | 数据 | 获取方式 | 来源接口 / 指标 / 配置 | 计算责任方 | 是否阻塞 |
|---|---|---|---|---|---|
| DI-001 | ETF 涨幅 | 复用（待确认 index_id） | /quotation/data/query/v1/table 或扶摇实时接口 | 数据开发 | 是 |
| DI-002 | ETF 涨速 | 待确认（指标系统无） | 扶摇实时行情接口（待确认） | 数据开发 | 是 |
| DI-003 | ETF 量比 | 待确认（指标系统无） | 扶摇实时行情接口（待确认） | 数据开发 | 是 |
| DI-004 | ETF 涨停数 | 复用（可替代 etfLimitUpStockCnt） | /quotation/data/query/v1/table + etfLimitUpStockCnt | 数据开发 | 是 |
| DI-005 | 成分股列表 | 复用 | /quotation/data/query/v1/relation (stock_etf_subred) | 数据开发 | 是 |
| DI-006 | 三市场全量股票涨幅 | 复用（待确认 index_id） | /quotation/data/query/v1/table | 数据开发 | 是 |
| DI-007 | 行业主题 ETF 列表 | 待确认 | /quotation/fund_pool/v2/query（文档缺失） | 数据开发 | 是 |

### 接口-能力映射表（草案）

| Row ID | 接口场景 | 服务能力 | 处理方式 | 是否阻塞 |
|---|---|---|---|---|
| IA-001 | ETF tab 数据查询接口 | 返回 8 份榜单（4维度×前后9）+ 领涨成分股 | **新建** | 是 |

---

## 7. Routing 输入包

**准入未通过，无法生成完整的 Routing 输入包。**

以下仅为草案：

- 业务目标摘要：板块统计页面新增 ETF tab，展示行业主题 ETF 按涨幅/涨速/量比/涨停数 4 维度各前 9/后 9 榜单，含每只 ETF 的领涨成分股信息
- 可开发范围：无（全部阻塞）
- 暂缓范围：全部
- 建议路由：待准入通过后：数据开发 → 接口开发 → 测试审核（串行）
