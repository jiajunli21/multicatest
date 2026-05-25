"""ETF综合评分计算模块。

Status: [default]

公式：
- ETF分数 = 50% * 热度排名分数 + 35% * 动量排名分数 + 10% * 流动性排名分数 + 5% * 低波排名分数
- 综合排名 DESC（分数越高越好）
"""

from datetime import date, datetime
from typing import Optional

from ..config import (
    WEIGHT_HEAT,
    WEIGHT_MOMENTUM,
    WEIGHT_LIQUIDITY,
    WEIGHT_LOW_VOL,
    DISPLAY_DECIMALS,
    MOCK_SECTOR_MAP,
    MOCK_ETF_TAGS,
    MOCK_DEFAULT_TAGS,
    MARKET_TAG_THRESHOLD,
)
from ..models import CalcStatus, ETFScore, MarketTag, RankScore, Top5Result


def calc_composite_scores(
    heat_ranks: list[RankScore],
    momentum_ranks: list[RankScore],
    liquidity_ranks: list[RankScore],
    low_vol_ranks: list[RankScore],
    calc_date: date,
    etf_name_map: dict[str, str],
    market_tag: Optional[MarketTag] = None,
) -> list[ETFScore]:
    """计算ETF综合评分.

    Args:
        heat_ranks: 热度排名分数列表
        momentum_ranks: 动量排名分数列表
        liquidity_ranks: 流动性排名分数列表
        low_vol_ranks: 低波排名分数列表
        calc_date: 计算日期
        etf_name_map: {code: name}
        market_tag: 市场标签（如已计算）

    Returns:
        按综合评分降序排列的 ETF 评分列表
    """
    # 建立 code -> rank_score 映射
    rank_maps = {
        "heat": {r.etf_code: r for r in heat_ranks},
        "momentum": {r.etf_code: r for r in momentum_ranks},
        "liquidity": {r.etf_code: r for r in liquidity_ranks},
        "low_vol": {r.etf_code: r for r in low_vol_ranks},
    }

    all_codes = set()
    for rm in rank_maps.values():
        all_codes.update(rm.keys())

    scores = []
    for code in all_codes:
        h = rank_maps["heat"].get(code)
        m = rank_maps["momentum"].get(code)
        lq = rank_maps["liquidity"].get(code)
        lv = rank_maps["low_vol"].get(code)

        h_score = h.rank_score if h else 0.0
        m_score = m.rank_score if m else 0.0
        lq_score = lq.rank_score if lq else 0.0
        lv_score = lv.rank_score if lv else 0.0

        composite = (
            WEIGHT_HEAT * h_score
            + WEIGHT_MOMENTUM * m_score
            + WEIGHT_LIQUIDITY * lq_score
            + WEIGHT_LOW_VOL * lv_score
        )

        has_not_calculable = any(
            r is None or r.status == CalcStatus.NOT_CALCULABLE
            for r in [h, m, lq, lv]
        )
        status = CalcStatus.SUCCESS if not has_not_calculable else CalcStatus.INSUFFICIENT_SAMPLE

        sector = MOCK_SECTOR_MAP.get(code, "其他")
        tags = MOCK_ETF_TAGS.get(code, list(MOCK_DEFAULT_TAGS))

        scores.append(ETFScore(
            etf_code=code,
            etf_name=etf_name_map.get(code, code),
            calc_date=calc_date,
            heat_rank_score=round(h_score, DISPLAY_DECIMALS),
            momentum_rank_score=round(m_score, DISPLAY_DECIMALS),
            liquidity_rank_score=round(lq_score, DISPLAY_DECIMALS),
            low_vol_rank_score=round(lv_score, DISPLAY_DECIMALS),
            composite_score=round(composite, DISPLAY_DECIMALS),
            rank=0,  # 后续填充
            sector=sector,
            tags=tags,
            market_tag=market_tag,
            status=status,
        ))

    # 按综合评分降序排
    scores.sort(key=lambda s: s.composite_score, reverse=True)

    # 填充排名（并列同分）
    current_rank = 1
    i = 0
    while i < len(scores):
        j = i
        while j + 1 < len(scores) and scores[j + 1].composite_score == scores[i].composite_score:
            j += 1
        for k in range(i, j + 1):
            scores[k].rank = current_rank
        current_rank += (j - i + 1)
        i = j + 1

    return scores


def build_top5_result(
    scores: list[ETFScore],
    signal_date: date,
    market_tag: MarketTag,
    total_count: int,
) -> Top5Result:
    """从评分列表构建 Top5 结果。

    Args:
        scores: 按排名升序排列的 ETF 评分列表
        signal_date: 样本信号日
        market_tag: 市场标签
        total_count: ETF 样本总数

    Returns:
        Top5Result
    """
    top5 = scores[:5]

    # 收集赛道（最多5个，去重，按出现顺序）
    seen_sectors = set()
    sector_etfs: dict[str, list[ETFScore]] = {}
    for s in top5:
        if s.sector not in seen_sectors and len(seen_sectors) < 5:
            seen_sectors.add(s.sector)
        if s.sector in seen_sectors:
            sector_etfs.setdefault(s.sector, []).append(s)

    sectors = [
        {
            "name": sector,
            "etfs": [
                {"code": e.etf_code, "name": e.etf_name, "score": e.composite_score}
                for e in etfs
            ]
        }
        for sector, etfs in sector_etfs.items()
    ][:5]

    return Top5Result(
        top_etfs=top5,
        sectors=sectors,
        signal_date=signal_date,
        market_tag=market_tag.value,
        update_time=datetime.now(),
        total_etf_count=total_count,
    )
