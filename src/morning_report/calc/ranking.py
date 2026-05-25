"""排名计算模块。

Status: [default]

排名规则 [default]:
- 热度：DESC（因子值越大排名越好）
- 动量：DESC（因子值越大排名越好）
- 流动性：DESC（因子值越大排名越好）
- 低波：ASC（因子值越小排名越好）
- 并列同名次，后续顺延
"""

from ..models import CalcStatus, RankScore


def calc_rank_scores(
    items: list[tuple[str, float, CalcStatus]],
    descending: bool = True,
) -> list[RankScore]:
    """计算排名分数.

    排名分数 = (总数 - 排名) / 总数

    Args:
        items: [(etf_code, factor_value, calc_status), ...]
        descending: True = 值越大排名越前 (DESC), False = 值越小排名越前 (ASC)

    Returns:
        按原始输入顺序排列的排名分数列表
    """
    if not items:
        return []

    total = len(items)

    # 只对可计算的 ETF 排序
    calculable = [(i, v, s) for i, (code, v, s) in enumerate(items) if s != CalcStatus.NOT_CALCULABLE]
    not_calculable = [(i, v, s) for i, (code, v, s) in enumerate(items) if s == CalcStatus.NOT_CALCULABLE]

    # 排序
    calculable.sort(key=lambda x: x[1], reverse=descending)

    # 分配排名（并列同名次）
    results: list[Optional[RankScore]] = [None] * total
    current_rank = 1
    idx_in_ranked = 0

    while idx_in_ranked < len(calculable):
        # 找同值区间
        j = idx_in_ranked
        while j + 1 < len(calculable) and calculable[j + 1][1] == calculable[idx_in_ranked][1]:
            j += 1

        # 同名次
        for k in range(idx_in_ranked, j + 1):
            orig_idx = calculable[k][0]
            results[orig_idx] = RankScore(
                etf_code=items[orig_idx][0],
                raw_value=calculable[k][1],
                rank=current_rank,
                total_count=total,
                rank_score=round((total - current_rank) / total, 6),
                status=calculable[k][2],
            )

        current_rank += (j - idx_in_ranked + 1)
        idx_in_ranked = j + 1

    # 不可计算的 ETF
    for orig_idx, val, status in not_calculable:
        results[orig_idx] = RankScore(
            etf_code=items[orig_idx][0],
            raw_value=val,
            rank=total,  # 排在最后
            total_count=total,
            rank_score=0.0,  # 不可计算，排名分数为 0
            status=status,
        )

    return [r for r in results if r is not None]
