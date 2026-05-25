# Admission Check

## Current Effective Summary

- **current_effective_round**: `Round 1`
- **current_status**: `准入不通过`
- **current_decision_time**: `2026-05-25 15:45 CST`
- **current_issue_ref**: `WS-14（早盘宝-评分与数据准入-第1轮）` / `0cecd63c-b8e9-4b9b-8f58-d483e8a90b55`
- **current_branch_ref**: `260525` / `e7478f5` / `origin/260525`
- **effective_scope**: `无当前有效可开发范围（准入不通过）`
- **blocked_scope**: `全部业务板块均阻塞`
- **effective_contract_maps**: `无法形成能力-数据-接口映射关系`
- **next_step**: `等待 PM 补充阻塞项信息后重新触发准入`

---

## Round History

### Round 1

- **trigger_reason**: `首次准入 — PM Agent 通过 WS-14 子 Issue 触发`
- **input_delta**: `本子 Issue 完整描述 + 父 Issue 附件 morning-report-requirements.md`
- **evidence_delta**: `全新准入，无历史证据继承`
- **blockers**: `15 项硬阻塞（详见下方阻塞清单）`
- **decision**: `准入不通过 — 无法进入 backend-task-routing`
- **superseded_by**: `NOT_SUPERSEDED`

---

## 1. 校验 ID / 时间戳

- **admission_id**: `WS-14-R1-20260525-154500`
- **时间戳**: `2026-05-25T15:45:00+08:00`

## 2. Issue 标识和需求摘要

- **Issue 标识**: WS-14「早盘宝-评分与数据准入-第1轮」/ `0cecd63c-b8e9-4b9b-8f58-d483e8a90b55`
- **父 Issue**: WS-13「早盘宝测试」/ `0bb699b9-4825-4ba6-a250-60f6edca4616`
- **需求摘要**: C 端用户通过搜索或行情 ETF tab 宫格入口进入早盘宝页面，查看每日 ETF 早盘关注评分 Top5（热度/动量/流动性/低波四维加权）、对应三级赛道、资讯、历史表现、指南，并可订阅预警推送和一件加自选。运营侧配置 ETF 计算样本和推送模板。

## 3. 当前仓库、分支、读取入口和上传入口

- **目标仓库**: `https://github.com/jiajunli21/multicatest`
- **目标分支**: `260525`
- **基线分支**: `260525`
- **当前 HEAD**: `e7478f5 Delete src directory`
- **读取入口**: `morning-report-requirements.md`（已读取）/ 仓库几乎为空（仅 README.md）
- **上传入口**: `待确认`（新项目，无现有代码结构）

## 4. fund-api-docs 执行状态与检索证据

```yaml
skill_name: "fund-api-docs"
execution_status: "REFERENCE_SEARCHED"
skill_runtime_source: "fund-api-docs (Multica runtime skill)"
source_used:
  - "references/reference-index.md"
  - "references/fund-basic-reference.md"
  - "references/recommendation-reference.md"
  - "references/fund-rank-screening-reference.md"
  - "references/indicator-data-reference.md"
  - "references/tag-data-reference.md"
keywords:
  - "早盘宝"
  - "ETF 评分"
  - "资讯过滤"
  - "预警推送"
  - "订阅"
  - "一键加自选"
  - "历史表现查询"
  - "自选分组"
  - "推送模板"
  - "权限判断"
  - "用户订阅"
  - "ETF tab 宫格"
  - "C 端页面"
failure_reason: "无"
can_be_used_as_admission_evidence: true
```

### fund-api-docs 检索证据明细

| execution_status | 查询关键词 / 线索 | source_used | 命中接口 / 资料 | 能力边界 | 缺口 | 结论 |
|---|---|---|---|---|---|---|
| REFERENCE_SEARCHED | 资讯过滤、基金资讯 | fund-basic-reference.md | `GET /quotation/fund_content/v2/query` — 基金资讯查询 | 可按单个基金代码查询资讯，支持 limit 参数 | 无早盘宝专用资讯过滤能力；无跨 ETF 批量资讯过滤；资讯部门过滤接口路径、参数、响应字段均未知（待王奕乾确认） | 需新建或适配，当前阻塞 |
| REFERENCE_SEARCHED | ETF 评分、排名、排行 | fund-rank-screening-reference.md | `GET /fuyao/fund_rank/fund_rank/v1/fund_rank` — 基金榜单/筛选/排序 | 支持多维度筛选（收益、回撤、夏普、规模等）、多字段排序、ETF 类型筛选、分页 | 不支持热度/动量/流动性/低波四维加权评分；无 Z 分数计算；无早盘宝专用 Top5 筛选逻辑 | 需新建评分计算逻辑 |
| REFERENCE_SEARCHED | 历史表现、历史净值 | fund-basic-reference.md | `GET /quotation/fund_detail/v2/getNavData` — 历史净值查询 | 支持按基金代码、时间范围查询单位/复权净值 | 无早盘宝历史推送快照；无信号后 3 日涨幅；最晚展示规则需另行实现 | 需新建或组合 |
| REFERENCE_SEARCHED | ETF 推荐、关联基金 | recommendation-reference.md | `POST /quotation/etf_tab/hq_tab/v1/related_fund_list` — 关联基金列表 | 支持按板块/指数/期货/个股获取关联 ETF | 不覆盖早盘宝评分 Top5 逻辑；不覆盖赛道映射 | 可复用关联基金查询能力 |
| REFERENCE_SEARCHED | 标签、个基标签、赛道 | tag-data-reference.md | `POST /quotation/data/query/v1/tag_spec` — 标签明细；`GET /quotation/data/query/enhance/v1/tag/data_api/sync` — 标签数据同步 | 支持按基金代码列表查询标签明细 | 无 AI 生成标签；无早盘宝个基 15 标签；赛道映射来源不在接口覆盖范围内 | AI 标签阻塞（待黄运锞） |
| REFERENCE_SEARCHED | 预警推送 | — | 未命中 | — | 无预警订阅、推送、模板管理接口 | 需全新开发 |
| REFERENCE_SEARCHED | 一键加自选 | — | 未命中 | — | 无自选分组写入、幂等、分组命名接口 | 需全新开发或依赖已有自选服务 |
| REFERENCE_SEARCHED | 指南 | — | 未命中 | — | 无运营配置类指南接口 | 可极简实现（运营写死文本返回接口） |
| REFERENCE_SEARCHED | 指标/行情数据查询 | indicator-data-reference.md | `POST /quotation/data/query/v1/line` — 画线式指标；`POST /quotation/data/query/v1/table` — 表格式指标 | 支持按 index_id、时间范围、代码批量查询指标数据 | sousuo_uv/sousuo_click_uv/fenshi_uv/add_uv/buy_uv 不在已知 index_id 体系中 | 热度因子计算原始数据缺失 |
| REFERENCE_SEARCHED | 基金诊断/评分 | fund-basic-reference.md | `GET /hqapi/static/diagnosis/{fundCode}` — 基金诊断评分 | 提供业绩/抗风险/公司/基金经理四个维度评分 | 评分维度与早盘宝热度/动量/流动性/低波完全不同，不可复用 | 不适用 |
| REFERENCE_SEARCHED | ETF 资金流（热度代理） | indicator-data-reference.md + fund-rank-screening-reference.md | 多个 ETF 资金流指标（申购/主力/北向/融资） | 可通过 indicator/table 接口查询 | 仅能作为部分代理，无法完全替代 sousuo_uv 等原始数据 | 热度计算仍缺核心原始数据 |
| NO_MATCH | 预警订阅与推送 | — | — | — | 无接口覆盖 | 需全新开发 |
| NO_MATCH | 一键加自选分组 | — | — | — | 无接口覆盖 | 需全新开发或对接已有自选服务 |
| NO_MATCH | 三级赛道映射 | — | — | — | 映射数据来源不在接口覆盖 | 需徐哲人提供 |

### fund-api-docs 结论

- **已有可复用接口**: 基金资讯查询、基金榜单/筛选、历史净值、关联基金列表、标签明细、指标数据查询（line/table）
- **需改造/包装接口**: 基金资讯（需增加早盘宝过滤逻辑）
- **需全新开发接口**: 早盘宝 Top5 评分页面接口、预警订阅与推送、一键加自选、指南接口
- **接口能力缺口**: 总共有 6 个接口场景需新建（Top5/赛道页面接口、资讯过滤、历史表现、指南、预警推送、一键加自选），0 个可完全复用
- **不可确认项**: 资讯过滤接口路径/参数/响应/兜底（王奕乾）、推送权限判断（姜文迪）、一键加自选副作用规则（黄运锞）

## 5. fund-indic-search-test 执行状态与检索证据

```yaml
skill_name: "fund-indic-search-test"
execution_status: "SEARCH_COMPLETED"
skill_runtime_source: "fund-indic-search-test (Multica runtime skill)"
source_used:
  - "~/.claude/fund-indic-config.json (认证配置：liujiaqing@myhexin.com)"
  - "sync_api: https://testfund.10jqka.com.cn/open/api/etf_rank/skills/fund/indic/v1/indic/sync (HTTP 200, SIZE:662539, 750 指标)"
keywords:
  - "热度因子"
  - "动量因子"
  - "流动性因子"
  - "低波因子"
  - "Z 分数"
  - "sousuo_uv"
  - "sousuo_click_uv"
  - "fenshi_uv"
  - "add_uv"
  - "buy_uv"
  - "收盘价"
  - "成交额"
  - "日收益率"
  - "标准差"
  - "20 日动量中位数"
  - "ETF 排名分数"
  - "搜索热度"
  - "首购热度"
  - "T 日"
  - "T-1 日"
  - "T-5 日"
  - "T-19 日"
  - "交易日口径"
  - "排名方向"
  - "20 日平均成交额"
failure_reason: "无（同步成功，检索完成）"
can_be_used_as_admission_evidence: true
```

### fund-indic-search-test 检索证据明细

| execution_status | 查询关键词 / 指标线索 | source_used | 命中指标 / 数据 | 字段单位 / 值类型 | 时间口径 | 缺口 | 结论 |
|---|---|---|---|---|---|---|---|
| NO_MATCH | sousuo_uv | sync_api | 未命中 | — | — | 指标库中不存在 sousuo_uv、sousuo_click_uv、fenshi_uv、add_uv、buy_uv 任何字段 | 需王珏提供原始数据（硬阻塞） |
| NO_MATCH | sousuo_click_uv | sync_api | 未命中 | — | — | 同上 | 需王珏提供原始数据（硬阻塞） |
| NO_MATCH | fenshi_uv | sync_api | 未命中 | — | — | 同上 | 需王珏提供原始数据（硬阻塞） |
| NO_MATCH | add_uv | sync_api | 未命中 | — | — | 同上 | 需王珏提供原始数据（硬阻塞） |
| NO_MATCH | buy_uv | sync_api | 未命中 | — | — | 同上 | 需王珏提供原始数据（硬阻塞） |
| MATCHED | 收盘价、close、ETF 收盘价 | sync_api | `close_price_back_avg20d`（板块级）；可通过 `POST /quotation/data/query/v1/line` 以对应 index_id 获取日线行情收盘价 | — | 需明确 index_id | 收盘价作为行情基础数据可通过指标查询接口获取，但需确认对应的 ETF 收盘价 index_id | 可间接获取（需确认具体 index_id） |
| MATCHED | 成交额、turnover | sync_api | `turnover`（成交额，⚠️ deprecated）；`etf_max_turnover_since_ipo`（历史最高成交额）；`block_*_etf_turnover`（板块级） | 元（turnover） | — | turnover 状态为 deprecated，不可靠；20 日平均成交额需自行从历史数据计算 | 成交额数据需确认替代指标或从行情系统获取 |
| MATCHED | 日涨幅、chgpct | sync_api | `chgpct`（日涨幅，online）/ `chgpct_1`（日涨幅-2） | % | — | 仅提供日涨幅百分比，非收盘价绝对值 | 可辅助展示，但计算动量因子需要收盘价 |
| MATCHED | 分类、赛道、三级分类 | sync_api | `l1code`/`l2code`/`l3code`（一二三级分类，online）；`l1name`/`l2name`（planed） | select 类型 | — | l3name 不在指标库中；三级分类是否等于"三级赛道"需徐哲人确认 | 分类字段可用，但赛道映射关系待确认 |
| MATCHED | 资金流、申购（热度代理） | sync_api | `etfNetBuyFlowAmount`/`etfNetBuyFlowAmount5d`/`etfNetBuyFlowAmount20d`/...（多个 ETF 资金流指标，online）；`etf_main_*` 系列（大单流入流出，online） | 元 | 日级/5日/20日/60日/YTD | 可作为热度因子的部分代理，但无法替代 sousuo_uv 等原始用户行为数据 | 可辅助计算，不可完全替代 |
| MATCHED | 搜索排名 | sync_api | `searchRankDay`/`searchRankWeek`/.../`searchRankYear`（planed） | — | — | 全部 planed 状态，不可用 | 搜索排名暂不可用 |
| MATCHED | 加自选排名 | sync_api | `selectRankDay`/`selectRankWeek`/.../`selectRankYear`（planed） | — | — | 全部 planed 状态，不可用 | 自选排名暂不可用 |
| MATCHED | ETF 热度 | sync_api | `etfHot`（ETF热度值，planed） | — | — | planed 状态，不可用 | ETF 热度暂不可用 |
| MATCHED | 波动率 | sync_api | `annualizedVolatilityYear`（近1年年化波动率，online）；多个 planed 波动率指标 | — | — | 仅近1年年化波动率 online，其他周期 planed | 低波计算需 20 日波动率，online 指标不满足 |
| MATCHED | 夏普率 | sync_api | `sharpeYear`（online）；多个 planed 夏普指标 | — | — | 仅近1年夏普率 online，不直接用于低波因子 | 不直接适用 |
| MATCHED | 排名 | sync_api | `rateRank*` 系列（多个 planed 排名指标） | — | — | 大部分 planed | 现有 online 排名指标不足 |
| MATCHED | 基金规模 | sync_api | `fundScale`（online） | 元 | 日级快照 | — | 可辅助使用 |
| MATCHED | 单位净值 | sync_api | `unitNav`（online）；`adjNav`/`accuNav`（planed） | — | 日级快照 | 复权净值 planed | 可通过线式指标接口补充 |
| NO_MATCH | Z 分数 | sync_api | 未命中 | — | — | 无 Z 分数计算指标 | 需自行计算 |
| NO_MATCH | 动量因子 | sync_api | 未命中 | — | — | 无动量因子指标 | 需自行计算 |
| NO_MATCH | 低波因子 | sync_api | 未命中 | — | — | 无低波因子指标 | 需自行计算 |
| NO_MATCH | 热度因子 | sync_api | 未命中 | — | — | 无热度因子指标 | 需自行计算 |
| NO_MATCH | 20 日动量中位数 | sync_api | 未命中 | — | — | 无此指标 | 需自行计算 |
| NO_MATCH | 信号后 3 日涨幅 | sync_api | 未命中 | — | — | 无此指标 | 需自行计算 |

### fund-indic-search-test 结论

- **可直接使用的 online 指标**: `chgpct`（日涨幅）、`l1code`/`l2code`/`l3code`（分类）、`fundScale`（基金规模）、`unitNav`（单位净值）、`annualizedVolatilityYear`（近1年年化波动率）、`sharpeYear`（近1年夏普率）、`week`/`month`/`year` 等收益指标
- **关键缺失**: sousuo_uv、sousuo_click_uv、fenshi_uv、add_uv、buy_uv 五个原始热度字段全部不存在于指标库
- **需要自行计算**: 热度因子、动量因子、流动性因子、低波因子、Z 分数、ETF 分数、20 日动量中位数、信号后 3 日涨幅
- **可辅助但不可替代**: ETF 资金流指标（申购/主力/北向/融资）可作为热度参考维度，但不能替代 sousuo_uv 等原始用户行为数据
- **planed 不可用**: 搜索排名、自选排名、ETF 热度值等多项指标处于 planed 状态，当前不可用

## 6. 完整校验清单结果

### 6.1 需求目标

- **要解决什么 ETF 行情场景？** ✅ 明确：C 端早盘宝 ETF 评分展示、资讯、历史、预警、自选
- **是否已按页面模块或业务板块拆开描述？** ✅ 明确：15 个业务板块矩阵
- **要实现什么后端能力？** ✅ 明确：评分计算、Top5/赛道映射、资讯过滤、历史表现、预警推送、一键加自选、指南
- **后端需要承担哪些职责？** ✅ 明确：数据计算 + C 端接口 + 推送 + 自选
- **是否能判断任务完成与否？** ✅ 明确：验收标准已列出
- **是否存在多个互相冲突的目标？** ❌ 无冲突

### 6.2 接口来源

- **是否已使用 fund-api-docs 筛选？** ✅ 已完成
- **请求参数是否明确？** ❌ 不明确：具体请求/响应字段需前端对齐
- **响应结构是否明确？** ❌ 不明确：具体字段由接口开发 Agent 定义
- **接口调用方、前端页面、展示字段是否明确？** ⚠️ 部分明确：展示了需要的字段列表，但字段级别细节待确认
- **外部接口来源、鉴权、超时、重试、降级是否明确？** ❌ 不明确：资讯部门接口（王奕乾）未确认
- **权限规则和兜底规则是否明确？** ❌ 不明确：推送权限（姜文迪）未确认
- **是否需要维护接口契约？** ⚠️ 不明确：需新建接口，契约待定
- **结论**: 接口来源不明确，**准入不通过**

### 6.3 指标与数据来源

- **是否已使用 fund-indic-search-test 检索？** ✅ 已完成
- **指标是否已有？** ❌ 不明确：sousuo_uv 等五个核心字段缺失
- **数据来源是否明确？** ❌ 不明确：王珏原始数据提供方式/刷新频率/历史窗口未确认
- **是否需要造数、取数、清洗、聚合、计算、回填或落库？** ⚠️ 需落库历史快照，但规则未确认
- **是否需要缓存？** ⚠️ 需缓存计算结果，但刷新时机待确认
- **历史数据、实时数据、快照数据关系？** ❌ 不明确
- **结论**: 核心数据缺失，数据来源不明确，**准入不通过**

### 6.4 公式与数据口径

- **公式是否完整？** ⚠️ 部分完整：ETF 分数、排名分数、热度因子、动量因子公式已给，但流动性因子公式待确认
- **样本范围是否明确？** ⚠️ 运营配置，但配置入口和生效时间待确认
- **排名方向和排序规则是否明确？** ⚠️ 并列排名、稳定排序规则待确认
- **时间口径是否明确？** ❌ 不明确：T/T-1/T-5/T-19 交易日口径和非交易日处理待确认
- **单位精度是否明确？** ❌ 不明确：百分比精度、小数位、四舍五入待确认
- **缺失值规则是否明确？** ❌ 不明确：跳过/置0/返回--/不参与排名待确认
- **边界规则是否明确？** ❌ 不明确：标准差为0、样本不足、停牌等边界行为待确认
- **结论**: 公式口径不完整，**准入不通过**

### 6.5 运营输入与前端展示

- **运营平台输入项、维护人、维护频率是否明确？** ❌ 不明确：具体配置入口和生效时间待确认
- **人工写死内容是否明确？** ⚠️ 指南写死、推送模板运营编辑，但细节待确认
- **前端展示字段、排序、筛选、空态、异常态是否明确？** ⚠️ 列出了展示字段，但空态/异常态规则待确认
- **结论**: 运营配置和前端展示不完整，**准入不通过**

### 6.6 推送、订阅、自选、历史和权限

- **推送触发时机、目标用户、消息模板、频控、失败重试是否明确？** ❌ 不明确：频控和重试规则待确认
- **历史数据展示范围、回填规则、缺失规则是否明确？** ❌ 不明确：快照存储、回填、缺失展示口径待确认
- **用户权限、产品权限、行情权限、自选分组权限是否明确？** ❌ 不明确：推送权限判断（姜文迪）待确认
- **一键加自选规则是否明确？** ❌ 不明确：分组命名、幂等、失败处理待确认
- **结论**: 推送/订阅/自选/权限规则不明确，**准入不通过**

### 6.7 验收标准

- **PM 如何验收？** ⚠️ 列出验收样例但部分边界样例待确认
- **数据验收样例是否明确？** ⚠️ 正常样例明确，边界样例待确认
- **接口验收样例是否明确？** ⚠️ 列出了验收维度，但具体接口字段待定
- **是否有明确的「不做什么」边界？** ✅ 已列出：不做前端/运营平台前端/资讯部门接口/AI标签基础设施
- **结论**: 验收标准部分明确，但受阻塞项影响，边界验收无法确认

### 6.8 仓库与分支

- **目标仓库是否明确？** ✅ `https://github.com/jiajunli21/multicatest`
- **目标分支/基线分支是否明确？** ✅ `260525`
- **读取入口是否明确？** ⚠️ morning-report-requirements.md 已读，但仓库几乎为空
- **上传入口是否明确？** ❌ 不明确：新项目，代码结构未建立
- **repo-branch-safety-check 是否通过？** ⚠️ 准入读取阶段已确认仓库和分支；涉及落盘、路由、提交或交付前需执行完整检查
- **结论**: 仓库和分支基本明确，但上传入口需后续确认

### 6.9 系统性风险

- **并发与竞态：是否存在并发写入、读写冲突风险？** ⚠️ 待确认：重复计算、重复推送安全性待确认
- **性能风险：是否存在 N+1 查询、慢查询、大事务、缓存击穿风险？** ⚠️ 首轮不设性能指标，但缓存策略待设计
- **数据一致性：是否涉及跨表/跨服务事务一致性？** ⚠️ 待确认：评分结果与缓存、历史快照与实时涨幅一致性
- **兼容性：是否与已有接口行为产生不可预期变化？** ⚠️ 全新功能，不涉及兼容性
- **生产配置变更：是否需要改环境变量、配置文件、开关？** ⚠️ 需要 ETF 计算样本/推送模板/指南配置

## 7. 阻塞清单

### 硬阻塞项（15 项）

| # | 阻塞项 | 负责人 | 影响范围 | 为什么阻塞 |
|---|---|---|---|---|
| 1 | sousuo_uv/sousuo_click_uv/fenshi_uv/add_uv/buy_uv 原始数据来源、提供方式、刷新频率和历史窗口 | 王珏、黄运锞 | 热度因子计算、Z 分数计算 | 热度因子公式直接依赖这五个字段，无替代方案 |
| 2 | T 日/T-1 日/T-5 日/T-19 日的交易日口径和非交易日处理规则 | 黄运锞 | 全部因子计算、历史展示 | 影响所有计算的时间窗口选取 |
| 3 | 20 日平均成交额作为流动性因子的确认和处理方式 | 黄运锞 | 流动性排名计算 | 公式为"待确认"状态 |
| 4 | 标准差为 0、样本不足、缺失热度字段、停牌/无行情数据的计算规则 | 黄运锞 | 评分边界行为 | 影响异常情况下的兜底逻辑 |
| 5 | AI 标签生成能力、生成 15 个标签耗时和失败兜底 | 黄运锞 | 个基标签展示 | 标签数据来源不明确 |
| 6 | ETF 到三级赛道的映射来源、维护人和缺失兜底 | 徐哲人、黄运锞 | Top5 赛道展示 | 无映射数据则无法展示赛道 |
| 7 | 资讯部门过滤接口路径、请求参数、响应字段、失败兜底 | 王奕乾 | 资讯过滤功能 | 外部接口依赖未满足 |
| 8 | 推送时用户当前指定产品权限判断规则和无权限兜底 | 姜文迪 | 预警推送功能 | 权限规则缺失导致推送逻辑无法实现 |
| 9 | 一键加自选分组命名规则、重复点击幂等、部分失败和无权限处理 | 黄运锞 | 一键加自选功能 | 自选接口副作用规则缺失 |
| 10 | 历史数据快照存储、回填、缺失展示口径 | 黄运锞 | 历史表现功能 | 历史数据方案未确定 |
| 11 | 并列排名、二级排序、稳定排序规则 | 黄运锞 | 排名结果确定性 | 影响 Top5 筛选结果 |
| 12 | 单位精度（百分比精度、小数位、四舍五入规则） | 黄运锞 | 展示结果 | 影响前后端数据一致性 |
| 13 | 缺失值处理规则（跳过/置 0/返回 --/不参与排名） | 黄运锞 | 评分计算和展示 | 影响所有计算逻辑 |
| 14 | 推送频控、失败重试规则 | 黄运锞 | 推送策略 | 影响推送系统设计 |
| 15 | 运营配置具体入口和生效时间 | 运营 | 配置上线时间 | 影响 ETF 计算样本和推送模板的可用性 |

### 其他待确认项

| # | 待确认项 | 负责人 | 影响 |
|---|---|---|---|
| 16 | ETF 收盘价和成交额的 index_id（用于 line/table 接口查询历史数据） | 黄运锞 | 可通过指标查询接口获取，需确认具体 index_id |
| 17 | 前端展示字段、空态/异常态、排序/筛选/分页规则 | PM/前端 | 接口设计需要前端对齐 |
| 18 | 自选对接：是否已有自选服务接口可复用 | 黄运锞 | 接口方案选择 |
| 19 | ETF 计算样本运营配置方式 | 运营 | 数据方案 |
| 20 | 并发重跑幂等、回滚/降级方式 | 黄运锞 | 系统性风险 |

## 8. 准入结论

### 准入结果

**准入不通过** — 存在 15 项硬阻塞，无法形成能力-数据-接口映射关系，无法生成入场前开发方案和 Routing 输入包。

### 关键发现

1. **接口侧（fund-api-docs）**: 现有接口体系中有基金资讯查询、基金榜单筛选、历史净值、标签明细、指标数据查询等可复用能力。但早盘宝核心功能（评分计算、Top5 筛选、预警推送、一键加自选、指南）均需全新开发。资讯过滤依赖外部接口（王奕乾），预警推送依赖权限规则（姜文迪），均未确认。

2. **数据侧（fund-indic-search-test）**: 750 个指标中，可用的 online ETF 相关指标包括日涨幅、分类字段、资金流、基金规模、净值等。但最关键的五个热度原始字段（sousuo_uv/sousuo_click_uv/fenshi_uv/add_uv/buy_uv）完全不存在于指标库中。搜索排名、自选排名、ETF 热度值等潜在替代指标处于 planed 状态，不可用。

3. **公式口径侧**: 热度因子、动量因子公式已给，但流动性因子公式仍为"待确认"状态。全部因子的交易日口径、并列排名、精度、缺失值、边界规则均由黄运锞待确认。

4. **仓库侧**: 目标仓库 `260525` 分支几乎为空（仅 README.md），为全新项目。

### 无法形成的能力-数据-接口映射

由于核心数据缺失和公式口径未确认，当前无法建立能力-数据映射表（AD-*）、数据-接口映射表（DI-*）、接口-能力映射表（IA-*）。因此无法进入 `backend-task-routing`，无法路由子 Agent。

### 检索证据自检

1. ✅ `fund-api-docs` 的 source_used 只包含 reference 文件
2. ✅ `fund-indic-search-test` 的 source_used 只包含认证配置和同步接口
3. ✅ 不存在用 `/quotation/...` 接口路径替代 fund-indic-search-test 证据
4. ✅ 不存在用 fund-indic-search-test 同步接口替代 fund-api-docs 证据
5. ✅ 两 Skill 证据独立记录、独立判定
6. ✅ 接口路径保留原 reference 中的完整路径

### 下一步

等待 PM Agent 补充阻塞项信息（特别是王珏、黄运锞、徐哲人、王奕乾、姜文迪的确认），收到 PM 新 @ 或新子 Issue 触发后，重新执行 `backend-entry-validation`。
