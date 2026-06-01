# Admission Check

## Current Effective Summary

- current_effective_round: `Round 2`
- current_status: `软阻塞通过`
- current_decision_time: `2026-06-01T11:55:00Z`
- current_issue_ref: `WS-34` (`019aeb45-3e45-42b6-8756-170ab9ff718e`)
- parent_issue_ref: `WS-32` (`b3783dd8-8238-488e-8ded-c68d5585c4e3`)
- current_branch_ref: `agent/etf-leader-agent/f57d678d` / `target_branch: 260601`
- delivery_target_type: `流程验证版`
- completion_type_ceiling: `流程验证版完成`
- effective_scope:
  - 定时任务 `BlockStatEtfTabTask` 开发（基金池拉取、扶摇查询（URL空缺使用查询码表请求体结构）、排序、成分股交集计算、Redis写入）
  - C端 ETF tab 业务接口开发（Caffeine → Redis 缓存链路）
  - 4个排序项（涨幅/涨速/量比/涨停数）各前9/后9共8份榜单
  - 成分股领涨/领跌股票计算
- blocked_scope:
  - 扶摇接口URL空缺（硬阻塞但人工已决策接受，按查询码表请求体结构开发）
  - 接口权限规则未确认（软阻塞，流程验证版默认无权限校验）
  - 除数为0兜底策略未确认（软阻塞，默认返回0）
  - cron配置中心化未确认（软阻塞，默认本地配置文件）
  - 三市场全量涨幅page_size未确认（软阻塞，默认100000）
- effective_contract_maps: `AD-001~AD-011`, `DI-001~DI-013`, `IA-001~IA-002`
- next_step: `进入 backend-task-routing`

---

## Round History

### Round 2

- trigger_reason: 第1轮WS-33阻塞后重新准入（PM新建WS-34子Issue），人工兜底人@李家骏已给出补充决策
- input_delta:
  - PM新建子Issue WS-34（替换已阻塞的WS-33）
  - 人工兜底人@李家骏 对首轮阻塞项的逐项决策（见Issue描述中的首轮→二轮变更记录）
  - SBLK-001~SBLK-012 在本轮确认接受
  - 扶摇URL空缺接受按查询码表请求体结构开发
  - C端接口契约由后端Leader在流程验证版内自行设计
  - ETF涨停数明确以基金池etfLimitUpStockCnt为准
- evidence_delta: 本轮重新执行 fund-api-docs 和 fund-indic-search-test
- blockers: 无硬阻塞；软阻塞4项（见当前有效摘要blocked_scope）
- decision: 软阻塞通过，可进入 backend-task-routing
- superseded_by: NOT_SUPERSEDED

### Round 1

- trigger_reason: 首次准入（PM创建WS-33子Issue）
- input_delta: PM首次提交板块统计新增ETF tab需求
- evidence_delta:
  - fund-api-docs: 已执行，命中基金池接口、基金关系数据接口、基金榜单接口等；扶摇实时行情接口不在fund-api-docs覆盖范围内
  - fund-indic-search-test: 已执行，确认fund-indic不覆盖实时行情指标（如price_change_ratio_pct等）
- blockers:
  - BLK-001: 扶摇涨幅查询URL待补充
  - BLK-002: 扶摇涨速查询URL待补充
  - BLK-003: 扶摇量比查询URL待补充
  - BLK-004: ETF tab C端接口路径/方法/请求参数待确认
  - BLK-005: 接口权限规则待确认
  - BLK-006: ETF涨停数来源未确认
  - BLK-007: fund-indic不覆盖实时行情指标
  - SBLK-001~SBLK-012: 12项软阻塞（缓存策略/TTL/分布式锁/排序并列规则/精度/停牌处理/非交易日/展示字段/一键加自选/运营配置/cron配置/代码目录）
- decision: 准入不通过，进入阻塞
- superseded_by: Round 2

---

## 业务目标摘要

用户在行情App进入A股→板块→板块统计页面，切换至新增的ETF tab，可查看4个排序项（涨幅、涨速、量比、涨停数）各自的前9/后9榜单，并展示每只ETF的成分股领涨/领跌股票信息。后端通过定时任务（每分钟）从基金池拉取行业主题ETF、通过扶摇查询实时行情并排序、查询成分股计算领涨/领跌，写入Redis；C端接口通过Caffeine→Redis缓存链路返回榜单数据。

## 准入校验

### 触发唯一性校验：通过

- 当前唯一有效子Issue: WS-34
- 触发方式: Assignee=ETF行情组后端Leader Agent（自动触发）
- 无多触发冲突

### 1. 需求目标：明确

- 业务场景：板块统计页面新增ETF tab，展示4个排序项榜单和领涨/领跌成分股
- 后端职责：定时任务数据刷新 + C端接口数据返回
- 完成判定：Redis写入8份榜单 + C端接口可读取 + 缓存链路正常
- 不做范围：不涉及板块统计原有tab修改、不涉及前端UI、不涉及ETF tab之外功能

### 2. 接口来源：软阻塞通过

- fund-api-docs 已执行，execution_status=REFERENCE_SEARCHED
- 基金池接口 `POST /quotation/fund_pool/v2/query` 在YApi附录中有记录，请求参数以查询码表.md为准
- 扶摇实时行情接口：URL空缺（查询码表中标记为"待补充"），请求体结构（code_selectors/indexes/page_info/sort）和index_id已完整
- 成分股关系接口：外部接口 `http://thsjj-data-center.fund/dataapi/relationship/v1/fetch-data`（URL已明确），不在fund-api-docs覆盖范围
- ETF tab C端接口：需新建，由后端Leader设计最小闭环契约
- 接口权限规则：软阻塞（流程验证版默认无权限校验）

### 3. 指标与数据来源：软阻塞通过

- fund-indic-search-test 已执行，execution_status=NO_MATCH
- 确认fund-indic不覆盖实时行情指标（price_change_ratio_pct, price_change_speed_ratio_pct, hq-fncdict-1771976）
- ETF实时行情指标全部走扶摇系统（涨幅/涨速/量比）
- ETF涨停数走基金池 `etfLimitUpStockCnt`
- 成分股数据走外部成分股关系接口
- 三市场全量股票涨幅走扶摇系统

### 4. 公式与数据口径：明确

- ETF排序：按4个排序项在基金池行业主题ETF全集内排序，各取前9（DESC）和后9（ASC）
- 涨停数使用基金池etfLimitUpStockCnt排序
- 并列规则：stockCode字典序二级排序（SBLK-004）
- 成分股交集：入榜ETF成分股（仅17/33/177市场）与三市场全量涨幅做交集
- 领涨/领跌：取成分股涨幅前9第一只和后9第一只
- 精度：保留2位小数（SBLK-005）；涨停数为整数
- 缺失值：排序字段缺失跳过不入对应榜单；成分股字段缺失置空
- 时间窗口：定时任务每分钟执行一次，行情为实时快照
- 除数为0兜底：软阻塞（默认返回0）

### 5. 运营输入与前端展示：明确

- 运营配置：本轮使用硬编码（SBLK-010）
- 前端展示字段：已明确（name/tradeCode/changeRatio/speedRatio/volumeRatio/limitUpCount + 领涨/领跌成分股字段）
- 前端切换tab不触发新请求，服务端一次性返回8份榜单
- 不包含成交额/换手率/溢价率（SBLK-008）
- 空态：Redis和Caffeine均未命中时返回空榜单结构
- cron配置：本地配置文件（SBLK-011）

### 6. 推送、订阅、自选、历史和权限：明确/软阻塞

- 推送/订阅：不适用（需求文档未提及）
- 一键加自选：本轮暂不实现（SBLK-009）
- 历史数据：不适用（仅展示当前最新榜单快照）
- 接口权限规则：软阻塞（流程验证版默认无登录态、无行情权限校验）

### 7. 验收标准：明确

- 数据验收：Redis key plateStatEtf:rank:data 写入完整8份榜单
- 接口验收：C端接口正确返回8份榜单，缓存链路正确
- 性能验收：缓存命中毫秒级，定时任务单次执行不超30秒
- 联调验收：前端正确展示4个排序项并切换
- 不做范围验收：板块统计原有tab不受影响

### 8. 仓库与分支：已确认

- 目标仓库：https://github.com/jiajunli21/multicatest.git
- 目标分支：260601
- 当前工作分支：agent/etf-leader-agent/f57d678d
- 分支模式：agent_branch_then_integrate
- repo-branch-safety-check：通过
- 读取入口：查询码表.md、FS-38132 板块统计新增ETF tab.md、板块统计新增ETFtab.png
- 上传入口：.multica/admission_check.md（Leader source branch）

### 9. 系统性风险：已评估

- 并发与幂等：Redis SETNX简单锁保障单实例执行（SBLK-003）
- 数据一致性：Redis和Caffeine最终一致（Caffeine 30s过期）
- 缓存策略：Caffeine 30s/100容量/LRU（SBLK-001）；Redis TTL 2分钟（SBLK-002）
- 兼容性：新增Redis key不与其他业务冲突，不影响板块统计原有tab
- 回滚方式：关闭定时任务可停止数据刷新

---

## fund-api-docs 检索证据

```yaml
skill_name: "fund-api-docs"
execution_status: "REFERENCE_SEARCHED"
skill_runtime_source: "/Users/lijiajun/.claude/skills/fund-api-docs/"
source_used:
  - "references/reference-index.md"
  - "references/fund-rank-screening-reference.md"
  - "references/indicator-data-reference.md"
  - "references/recommendation-reference.md"
keywords:
  - "板块统计 ETF tab"
  - "基金池 fund_pool/v2/query"
  - "uniqueType=etf_third_level_track_list"
  - "扶摇行情查询"
  - "price_change_ratio_pct"
  - "price_change_speed_ratio_pct"
  - "hq-fncdict-1771976"
  - "成分股 etf_security"
  - "stock_code 精确查询"
  - "market_code 17/33/177"
  - "Redis 缓存 plateStatEtf:rank:data"
  - "Caffeine 本地缓存"
failure_reason: "无"
can_be_used_as_admission_evidence: true
```

| execution_status | 查询关键词 | source_used | 命中接口/资料 | 能力边界 | 缺口 | 结论 |
|---|---|---|---|---|---|---|
| REFERENCE_SEARCHED | 基金池 fund_pool/v2/query | reference-index.md (YApi附录) | `POST /quotation/fund_pool/v2/query` (YApi ID: 705272) | fund-api-docs 中未收录完整请求参数和返回字段，实际以查询码表.md第1节为准；uniqueType参数由查询码表提供 | fund-api-docs缺少完整参数定义 | 复用（以查询码表为准） |
| REFERENCE_SEARCHED | 扶摇行情查询 price_change_ratio_pct | indicator-data-reference.md | `POST /quotation/data/query/v1/table`（通用表格查询） | 通用表格查询接口支持 code_selectors/indexes/page_info/sort 结构，可传入 stock_code 和 index_id 查询ETF指标 | 扶摇接口URL不在fund-api-docs覆盖范围内；实时行情指标（price_change_ratio_pct等）的扶摇请求体结构以查询码表第2/4/5/6/7节为准 | 需外部（扶摇系统）实现，请求体结构已知 |
| REFERENCE_SEARCHED | ETF量比 hq-fncdict-1771976 | indicator-data-reference.md | 同上 | 同上 | 同上（扶摇URL空缺） | 需外部（扶摇系统）实现 |
| REFERENCE_SEARCHED | 成分股 etf_security | indicator-data-reference.md | `POST /quotation/data/query/v1/relation`、`GET /quotation/data/query/gateway/cache/v1/relation/{code}/{type}/{relationships}/{entity_infos}` | 支持 stock_etf_subred 关系查询，可获取ETF关联成分股 | 外部接口 `http://thsjj-data-center.fund/dataapi/relationship/v1/fetch-data`（查询码表第3节）不在fund-api-docs覆盖范围 | 成分股关系查询可复用，但本轮使用查询码表中的外部接口URL |
| REFERENCE_SEARCHED | ETF榜单/排行 | fund-rank-screening-reference.md | `GET https://dq.10jqka.com.cn/fuyao/fund_rank/fund_rank/v1/fund_rank` | typeList=3（ETF基金），支持week/year/month等历史收益排序和筛选 | 不支持实时行情字段（price_change_ratio_pct/涨速/量比）排序；仅覆盖历史收益指标 | 不适用于实时行情榜单（本轮自行排序计算） |
| REFERENCE_SEARCHED | ETF tab关联基金 | recommendation-reference.md | `POST /quotation/etf_tab/hq_tab/v1/related_fund_list` | 支持指数/板块(plate)/港股板块(plate_HK)/美股板块(plate_US)关联ETF查询 | 与板块统计ETF tab需求不同，非榜单排序场景 | 不适用（不同业务场景） |

### fund-api-docs 结论

- **已有可复用接口**：基金池查询 `POST /quotation/fund_pool/v2/query`（YApi附录），通用表格查询 `POST /quotation/data/query/v1/table`，基金关系查询 `POST /quotation/data/query/v1/relation`
- **需要新建的接口**：ETF tab C端业务接口（板块统计ETF tab榜单数据接口），由后端Leader设计最小闭环契约
- **需要外部系统实现的接口**：扶摇实时行情查询（涨幅/涨速/量比/成分股涨幅），URL空缺但请求体结构已完整（以查询码表为准）；成分股关系接口 `http://thsjj-data-center.fund/dataapi/relationship/v1/fetch-data`（URL已明确）
- **不覆盖范围**：扶摇系统接口（不属于fund-api-docs覆盖范围）、外部dataapi接口

---

## fund-indic-search-test 检索证据

```yaml
skill_name: "fund-indic-search-test"
execution_status: "NO_MATCH"
skill_runtime_source: "/Users/lijiajun/.claude/skills/fund-indic-search-test/"
source_used:
  - "~/.claude/fund-indic-config.json (auth: liujiaqing@myhexin.com)"
  - "sync_api: https://testfund.10jqka.com.cn/open/api/etf_rank/skills/fund/indic/v1/indic/sync"
  - "scripts/query_indic.sh"
keywords:
  - "price_change_ratio_pct"
  - "price_change_speed_ratio_pct"
  - "hq-fncdict-1771976"
  - "security_name"
  - "etf_security_holdrate"
  - "snp_start_price"
  - "etf_limit_up_stock_cnt"
failure_reason: "无（同步成功，HTTP 200，751条指标数据可解析，检索完成但目标关键词无命中）"
can_be_used_as_admission_evidence: true
```

| execution_status | 查询关键词 | source_used | 命中指标/数据 | 字段单位/值类型 | 时间口径 | 缺口 | 结论 |
|---|---|---|---|---|---|---|---|
| NO_MATCH | price_change_ratio_pct | sync API (751 indicators) | 无精确命中 | — | — | fund-indic不覆盖实时行情指标 | 实时行情指标全部走扶摇系统 |
| NO_MATCH | price_change_speed_ratio_pct | sync API (751 indicators) | 无精确命中 | — | — | 同上 | 同上 |
| NO_MATCH | hq-fncdict-1771976 | sync API (751 indicators) | 无精确命中 | — | — | 同上 | 同上 |
| NO_MATCH | security_name | sync API (751 indicators) | 无精确命中 | — | — | fund-indic中证券名称不覆盖ETF实时行情中的security_name | 走扶摇系统 |
| NO_MATCH | etf_security_holdrate | sync API (751 indicators) | 无精确命中 | — | — | fund-indic不覆盖成分股持仓占比 | 走外部成分股关系接口 |
| NO_MATCH | snp_start_price | sync API (751 indicators) | 无精确命中 | — | — | 不在fund-indic覆盖范围 | 不适用（本轮不使用起始价） |

### fund-indic-search-test 结论

- **sync API结果**：HTTP 200，751条指标数据可解析，同步成功
- **目标关键词检索**：price_change_ratio_pct、price_change_speed_ratio_pct、hq-fncdict-1771976、security_name、etf_security_holdrate、snp_start_price **均无命中**
- **与Round 1一致**：fund-indic不覆盖实时行情指标
- **继续推进依据**：人工兜底人@李家骏已确认fund-indic不适用，实时行情指标全部走扶摇系统；涨停数使用基金池etfLimitUpStockCnt；成分股数据走外部关系接口

---

## 准入结论

- **准入结果**：`软阻塞通过`
- **接口结论**：
  - 基金池接口：复用 `POST /quotation/fund_pool/v2/query`（以查询码表第1节为准）
  - 扶摇行情查询：外部系统实现（请求体结构以查询码表第2/4/5/6/7节为准，URL空缺）
  - 成分股关系：外部接口 `http://thsjj-data-center.fund/dataapi/relationship/v1/fetch-data`（URL已明确）
  - ETF tab C端接口：新建（由后端Leader设计最小闭环契约）
- **指标/数据结论**：
  - fund-indic-search-test=NO_MATCH，实时行情指标全部走扶摇系统
  - 涨停数走基金池etfLimitUpStockCnt（人工已确认）
  - 成分股数据走外部关系接口
- **业务板块拆分**：
  - 板块A：定时榜单刷新任务 `BlockStatEtfTabTask`
  - 板块B：C端ETF tab业务接口
- **入场前开发方案**：`.multica/admission_check.md`
- **方案版本/时间戳**：`Round 2 / 2026-06-01T11:55:00Z`
- **工作分支**：`agent/etf-leader-agent/f57d678d`
- **target_branch**：`260601`
- **branch_mode**：`agent_branch_then_integrate`
- **commit SHA**：待 commit 后记录
- **push 结果**：待 push 后记录
- **剩余风险**：扶摇接口URL空缺（人工已接受），接口权限规则未确认（流程验证版默认无校验）
- **下一步**：`进入 backend-task-routing`

---

## 能力-数据映射表

| Row ID | 能力 | 需要的数据 | 数据用途 | 数据状态 | 公式/口径引用 | 是否阻塞 |
|---|---|---|---|---|---|---|
| AD-001 | 获取行业主题ETF范围 | 基金池行业主题ETF列表（uniqueType=etf_third_level_track_list） | 确定榜单计算范围 | 已有（基金池接口） | 查询码表第1节 | 否 |
| AD-002 | ETF涨幅排序（前9/后9） | ETF实时涨幅 price_change_ratio_pct | 榜单排序 | 需查询（扶摇系统） | 查询码表第2节；SBLK-004排序并列规则 | 否（URL空缺，人工已接受） |
| AD-003 | ETF涨速排序（前9/后9） | ETF实时涨速 price_change_speed_ratio_pct | 榜单排序 | 需查询（扶摇系统） | 查询码表第5节；SBLK-004 | 否（URL空缺，人工已接受） |
| AD-004 | ETF量比排序（前9/后9） | ETF实时量比 hq-fncdict-1771976 | 榜单排序 | 需查询（扶摇系统） | 查询码表第6节；SBLK-004 | 否（URL空缺，人工已接受） |
| AD-005 | ETF涨停数排序（前9/后9） | ETF涨停数 etfLimitUpStockCnt | 榜单排序 | 已有（基金池接口返回字段） | Round 2变更项#3：以基金池etfLimitUpStockCnt为准 | 否 |
| AD-006 | 查询入榜ETF成分股 | 成分股列表（code/name/etf_security_holdrate） | 领涨/领跌计算 | 需查询（外部成分股关系接口） | 查询码表第3节 | 否（URL已明确） |
| AD-007 | 获取三市场全量股票涨幅 | 全量股票涨幅 price_change_ratio_pct | 成分股涨幅交集计算 | 需查询（扶摇系统） | 查询码表第4节（market_code 17/33/177） | 否（URL空缺，人工已接受） |
| AD-008 | 计算成分股领涨/领跌股票 | 成分股涨幅列表与ETF成分股交集 | 展示领涨/领跌信息 | 需计算（本地交集） | 取成分股涨幅前9第一只(bottomLead)和后9第一只(topLead) | 否 |
| AD-009 | 组装8份榜单写入Redis | 4个排序项×前9/后9榜单数据 | Redis缓存供C端接口读取 | 需落盘（Redis） | SBLK-002（TTL 2分钟）；SBLK-005（精度2位小数） | 否 |
| AD-010 | C端接口读取榜单数据 | Redis key plateStatEtf:rank:data | C端接口返回数据 | 已有（Redis） | SBLK-001（Caffeine 30s）；SBLK-002（Redis TTL 2min） | 否 |
| AD-011 | Caffeine本地缓存 | ETF榜单数据 | 减少Redis访问 | 需配置（Caffeine） | SBLK-001（过期30s/最大容量100/LRU） | 否 |

---

## 数据-接口映射表

| Row ID | 数据 | 获取方式 | 来源接口/指标/配置 | 计算/加工规则 | 计算责任方 | 是否加工 | 是否落库 | 是否缓存 | 是否阻塞 |
|---|---|---|---|---|---|---|---|---|---|
| DI-001 | 行业主题ETF列表 | 复用 | `POST /quotation/fund_pool/v2/query` (uniqueType=etf_third_level_track_list) | 解析返回的行业主题ETF列表（约90条），提取 stockCode/market/name/tradeCode/etfLimitUpStockCnt | 数据开发 | 是（解析+过滤） | 否 | 否 | 否 |
| DI-002 | ETF实时涨幅 | 新增（外部系统） | 扶摇接口（查询码表第2节，URL空缺，请求体结构完整） | 按 stockCode 批量查询 price_change_ratio_pct，timetype=SNAPSHOT | 数据开发 | 是（解析） | 否 | 否 | 否（URL空缺，人工已接受） |
| DI-003 | ETF实时涨速 | 新增（外部系统） | 扶摇接口（查询码表第5节，URL空缺，请求体结构完整） | 按 stockCode 批量查询 price_change_speed_ratio_pct，timetype=SNAPSHOT | 数据开发 | 是（解析） | 否 | 否 | 否（URL空缺，人工已接受） |
| DI-004 | ETF实时量比 | 新增（外部系统） | 扶摇接口（查询码表第6节，URL空缺，请求体结构完整） | 按 stockCode 批量查询 hq-fncdict-1771976，timetype=NOW | 数据开发 | 是（解析） | 否 | 否 | 否（URL空缺，人工已接受） |
| DI-005 | ETF涨停数 | 复用 | 基金池 etfLimitUpStockCnt 字段 | 直接从基金池返回中提取，无需额外查询 | 数据开发 | 否（直接提取） | 否 | 否 | 否 |
| DI-006 | ETF成分股列表 | 新增（外部系统） | `http://thsjj-data-center.fund/dataapi/relationship/v1/fetch-data` | 按入榜ETF的stockCode查询，过滤17/33/177市场，提取code/name/etf_security_holdrate | 数据开发 | 是（解析+市场过滤） | 否 | 否 | 否（URL已明确） |
| DI-007 | 三市场全量股票涨幅 | 新增（外部系统） | 扶摇接口（查询码表第4节，URL空缺，请求体结构完整） | 按market_code 17/33/177全量拉取 price_change_ratio_pct 和 security_name | 数据开发 | 是（解析） | 否 | 否 | 否（URL空缺，人工已接受；page_size软阻塞） |
| DI-008 | 成分股涨幅交集计算 | 计算 | 本地计算（DI-006 ∩ DI-007） | 每只入榜ETF的成分股与三市场全量涨幅做交集，得到成分股涨幅降序和升序列表 | 数据开发 | 是（交集计算） | 否 | 否 | 否 |
| DI-009 | 领涨/领跌股票 | 计算 | 本地计算（基于DI-008结果） | 取成分股涨幅前9第一只（topLead）和后9第一只（bottomLead） | 数据开发 | 是（取极值） | 否 | 否 | 否 |
| DI-010 | 8份榜单组装 | 计算 | 本地计算（基于DI-002~DI-005排序 + DI-009领涨/领跌） | 按4个排序项各取前9(DESC)和后9(ASC)，组装完整榜单条目（含ETF排名信息+领涨/领跌成分股信息）；SBLK-005精度保留2位小数 | 数据开发 | 是（组装+精度处理） | 否 | 否 | 否 |
| DI-011 | Redis写入 | 新增 | Redis key `plateStatEtf:rank:data` | 覆盖式写入JSON；SBLK-002 TTL 2分钟；SBLK-003 Redis SETNX锁 | 数据开发 | 否（直接写入） | 是（Redis） | 是（Redis） | 否 |
| DI-012 | Caffeine读取 | 新增 | 本地 Caffeine 缓存 | 优先读取 Caffeine，未命中回源 Redis 并回填；SBLK-001 过期30s/容量100/LRU | 接口开发 | 是（缓存读取+回填） | 否 | 是（Caffeine） | 否 |
| DI-013 | 接口响应组装 | 新增 | C端接口 Controller/Service | 从缓存读取8份榜单数据，按接口契约组装响应 | 接口开发 | 是（组装） | 否 | 否 | 否 |

---

## 接口-能力映射表

| Row ID | 接口场景 | 接口具体功能 | 服务能力 | 处理方式 | 请求参数 | 返回字段 | 权限规则 | 空数据规则 | 错误/降级规则 | Mock |
|---|---|---|---|---|---|---|---|---|---|---|
| IA-001 | C端ETF tab业务接口 | 返回板块统计ETF tab的4个排序项各前9/后9共8份榜单数据及领涨/领跌成分股信息 | AD-010（C端接口读取榜单数据）、AD-011（Caffeine缓存） | 新增 | 由后端Leader设计最小闭环契约：建议 `GET /quotation/plate_stat/etf_tab/v1/rank`，无必填参数（返回全部8份榜单）；可选参数 `rankType`（changeRatio/speedRatio/volumeRatio/limitUpCount）按需筛选单个排序项 | stockCode/tradeCode/marketCode/securityCode/name/changeRatio/speedRatio/volumeRatio/limitUpCount/rankType/rankValue/rankOrder/topLeadStockCode/topLeadStockName/topLeadStockChangeRatio/topLeadStockHoldRate/bottomLeadStockCode/bottomLeadStockName/bottomLeadStockChangeRatio/bottomLeadStockHoldRate | 软阻塞（流程验证版默认无登录态、无行情权限校验，建议方案：`/quotation` 前缀默认走网关基础登录态，权限不足返回空榜单；后续确认权限口径后调整） | Redis和Caffeine均未命中返回8个空数组；部分字段缺失对应字段返回空/0 | Redis读取失败降级Caffeine；Caffeine和Redis均失败返回空榜单；不实时回源基金池/扶摇/成分股接口 | 否 |
| IA-002 | 定时任务内部调用 | 每分钟执行一次，从基金池拉取ETF范围→扶摇查询行情→排序→成分股交集→Redis写入 | AD-001~AD-009 | 新增（内部任务，非C端接口） | 无外部请求参数（定时触发，内部调用基金池/扶摇/成分股接口） | Redis key `plateStatEtf:rank:data` (JSON Value) | 不适用（内部任务） | 基金池返回空→不覆盖Redis；扶摇失败→不覆盖Redis；成分股接口失败→榜单主数据可写但领涨/领跌字段置空 | 基金池/扶摇失败不覆盖Redis老数据；成分股接口失败允许降级写入（领涨/领跌字段置空）；并发用Redis SETNX | 否 |

---

## 软阻塞假设

| 假设 | PM是否接受 | 影响范围 | 假设错误后的返工影响 |
|---|---|---|---|
| 扶摇接口URL空缺，请求体结构和index_id以查询码表.md为准 | 是（Round 2变更项#1） | 扶摇实时行情查询开发 | 联调时需替换为真实URL，影响HTTP client配置 |
| C端接口契约由后端Leader自行设计 | 是（Round 2变更项#2） | 接口路径/方法/请求参数 | 前端联调时需对齐契约，接口路径可能调整 |
| ETF涨停数以基金池etfLimitUpStockCnt为准 | 是（Round 2变更项#3） | 涨停数排序数据来源 | 低风险，人工已确认 |
| 接口权限默认无校验（流程验证版） | 否（Round 2变更项#4维持待确认） | C端接口权限逻辑 | 若后续需接入权限，需新增权限校验逻辑 |
| 除数为0返回0 | 否（首轮未覆盖） | 量比等极端计算场景 | 低风险，极端情况 |
| cron使用本地配置文件 | 是（SBLK-011） | 定时任务配置 | 若需配置中心化需迁移 |
| page_size默认100000 | 否（首轮未覆盖） | 三市场全量涨幅数据完整性 | 中等风险，若实际数据量超100000需调整分页 |
| 代码目录按现有项目约定 | 是（SBLK-012） | 文件路径 | 低风险 |

---

## 验收标准

- 数据验收：定时任务执行后 Redis 中存在 key `plateStatEtf:rank:data`，数据包含4个排序项各前9和后9；涨停数按基金池 etfLimitUpStockCnt 排序
- 接口验收：C端接口返回8份榜单数据；缓存链路正确（Caffeine命中→Redis命中→空兜底）
- 性能验收：C端接口缓存命中场景毫秒级响应；定时任务单次执行不超30秒
- 联调验收：前端正确展示4个排序项并切换；字段映射与后端契约一致
- 不做范围验收：板块统计原有tab不受影响；ETF tab不实时回源基金池/扶摇/成分股接口

---

## Routing 输入包

### 1. 业务目标摘要

用户在行情App进入板块统计页面的ETF tab，查看4个排序项（涨幅/涨速/量比/涨停数）各自前9/后9的ETF榜单，以及每只ETF的成分股领涨/领跌股票。后端通过定时任务每分钟从基金池拉取行业主题ETF、通过扶摇查询实时行情并排序、查询成分股计算领涨/领跌、写入Redis；C端接口通过Caffeine→Redis缓存链路返回数据。交付目标为流程验证版。

### 2. 可开发范围

- 定时任务 `BlockStatEtfTabTask`（基金池拉取、扶摇查询、排序、成分股交集计算、Redis写入）
- C端 ETF tab 业务接口（Caffeine→Redis缓存读取链路）
- 4个排序项×前9/后9共8份榜单数据
- 成分股领涨/领跌股票计算
- Redis key `plateStatEtf:rank:data` JSON结构

### 3. 暂缓范围

| 暂缓项 | 暂缓原因 | 负责人 | 解除条件 |
|---|---|---|---|
| 扶摇接口URL | 查询码表中标记为"待补充" | 业务负责人（接口负责人） | 联调时提供真实URL |
| 接口权限规则 | 流程验证版默认无校验 | 业务负责人（接口负责人） | 确认登录态、行情权限、无权限兜底 |
| 除数为0兜底策略 | 极端情况未确认 | 业务负责人（数据负责人） | 确认兜底策略 |
| cron配置中心化 | 流程验证版使用本地配置 | 业务负责人（接口负责人） | 确认配置中心化方案 |
| 三市场page_size实际值 | 查询码表示例用100000 | 业务负责人（接口负责人） | 联调时确认 |
| 一键加自选 | 本轮暂不实现 | PM | 后续轮次需求 |
| 成交额/换手率/溢价率 | 本轮暂不实现 | PM | 后续轮次需求 |

### 4. 建议路由输入

| 子任务 | 建议对象 | 输入 | 输出 | 串行依赖 |
|---|---|---|---|---|
| 定时任务 `BlockStatEtfTabTask` 开发 | 数据开发 Agent | AD-001~AD-009, DI-001~DI-011, 查询码表.md第1-8节, SBLK-001~SBLK-012 | Java实现：BlockStatEtfTabTask.java + DTO/Service类，Redis写入 | 无（可独立开始） |
| C端 ETF tab 业务接口开发 | 接口开发 Agent | AD-010~AD-011, DI-012~DI-013, IA-001, SBLK-001~SBLK-002 | Java实现：Controller/Service + Caffeine配置 | 依赖数据开发完成（需确认Redis key结构和数据格式） |
| 测试与质量审核 | 测试与质量审核 Agent | 数据开发handoff + 接口开发handoff, IA-001契约 | 测试用例+执行结果+质量结论 | 依赖数据开发和接口开发均完成 |

---

## 分支模式

```yaml
branch_mode: "agent_branch_then_integrate"
source_branch_allowed: true
target_branch: "260601"
integration_required_before_qa: true
integration_required_before_final: true
integration_owner: "ETF 行情组后端 Leader Agent"
current_stage: "Leader admission (Round 2)"
```

---

## repo-branch-safety-check 结果

- 目标仓库：https://github.com/jiajunli21/multicatest.git / 配置来源：PM Issue 指定
- 当前仓库 remote：一致 (origin → github.com/jiajunli21/multicatest.git)
- 当前工作分支：agent/etf-leader-agent/f57d678d
- 目标分支：260601（远端存在，HEAD=e7478f5）
- 分支模式：agent_branch_then_integrate / source branch allowed / integration required
- 工作区状态：clean
- 冲突标记：无
- 敏感信息：无
- 路径污染检测：通过
- 风险等级：无 P0 / 无 P1 / 无 P2
- push 条件：具备 / push 后复核：待执行
