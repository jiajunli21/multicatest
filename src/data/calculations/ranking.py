"""排名分数计算与ETF综合评分。[default]

AD-006: ETF综合评分 = 50%*热度排名分数 + 35%*动量排名分数 + 10%*流动性排名分数 + 5%*低波排名分数

排名方向:
- 热度排名: DESC (值越大排名越高)
- 动量排名: DESC (值越大排名越高)
- 流动性排名: DESC (值越大排名越高)
- 低波排名: ASC (值越小排名越高)

排名分数 = (总数 - 排名 + 1) / 总数  [default: 排名从1开始]

并列处理 [default]:
- 值相等时取相同排名，后续排名顺延 (如: 1,2,2,4)
- 排名分数基于实际排名计算

精度 [default]:
- ETF分数保留2位小数
- 内部计算保持高精度(6位)
"""

from typing import Optional


def rank_values(values: list, direction: str = "DESC") -> list:
    """对值序列进行排名。

    Args:
        values: 待排名值列表 [(etf_code, value), ...]
        direction: DESC(降序，值大排第1) 或 ASC(升序，值小排第1)

    Returns:
        [(etf_code, value, rank), ...] 按rank升序排列

    并列处理 [default]:
    - 值相等取相同排名
    - 后续排名顺延 (1,2,2,4)
    - None值排最后
    """
    # 分离有效值和None值
    valid = [(code, v) for code, v in values if v is not None]
    none_items = [(code, v) for code, v in values if v is None]

    if direction == "DESC":
        valid.sort(key=lambda x: x[1], reverse=True)
    else:
        valid.sort(key=lambda x: x[1])

    ranked = []
    current_rank = 1
    i = 0
    while i < len(valid):
        j = i
        while j < len(valid) and valid[j][1] == valid[i][1]:
            j += 1
        tie_count = j - i
        for k in range(i, j):
            ranked.append((valid[k][0], valid[k][1], current_rank))
        current_rank += tie_count
        i = j

    # None值排最后
    for code, v in none_items:
        ranked.append((code, v, current_rank))
        current_rank += 1

    ranked.sort(key=lambda x: x[2])
    return ranked


def calc_rank_score(rank: int, total_count: int) -> float:
    """计算排名分数 = (总数 - 排名 + 1) / 总数。

    Args:
        rank: 排名 (从1开始)
        total_count: 总样本数

    Returns:
        排名分数 [0, 1]
    """
    if total_count <= 0:
        return 0.0
    return (total_count - rank + 1) / total_count


def calc_composite_score(
    heat_rank_score: float,
    momentum_rank_score: float,
    liquidity_rank_score: float,
    lowvol_rank_score: float,
) -> float:
    """计算ETF综合评分 = 50%*热度 + 35%*动量 + 10%*流动性 + 5%*低波。

    Returns:
        ETF综合评分, 保留2位小数
    """
    score = (
        0.50 * heat_rank_score
        + 0.35 * momentum_rank_score
        + 0.10 * liquidity_rank_score
        + 0.05 * lowvol_rank_score
    )
    return round(score, 2)


def compute_all_rankings(
    heat_factors: dict,        # {etf_code: heat_factor}
    momentum_factors: dict,    # {etf_code: momentum_factor}
    liquidity_factors: dict,   # {etf_code: liquidity_factor}
    lowvol_factors: dict,      # {etf_code: lowvol_factor}
) -> dict:
    """计算完整的ETF排名与综合评分。

    Args:
        heat_factors: {etf_code: heat_factor_value}
        momentum_factors: {etf_code: momentum_factor_value}
        liquidity_factors: {etf_code: liquidity_factor_value}
        lowvol_factors: {etf_code: lowvol_factor_value}

    Returns:
        {etf_code: {heat_rank, momentum_rank, liquidity_rank, lowvol_rank,
                     heat_rank_score, momentum_rank_score, liquidity_rank_score,
                     lowvol_rank_score, composite_score, overall_rank}}
    """
    etf_codes = list(heat_factors.keys())
    total = len(etf_codes)

    # 各因子排名
    heat_ranked = rank_values(
        [(c, heat_factors.get(c)) for c in etf_codes], "DESC"
    )
    momentum_ranked = rank_values(
        [(c, momentum_factors.get(c)) for c in etf_codes], "DESC"
    )
    liquidity_ranked = rank_values(
        [(c, liquidity_factors.get(c)) for c in etf_codes], "DESC"
    )
    lowvol_ranked = rank_values(
        [(c, lowvol_factors.get(c)) for c in etf_codes], "ASC"
    )

    # 构建排名映射 {etf_code: rank}
    heat_rank_map = {code: rank for code, _, rank in heat_ranked}
    momentum_rank_map = {code: rank for code, _, rank in momentum_ranked}
    liquidity_rank_map = {code: rank for code, _, rank in liquidity_ranked}
    lowvol_rank_map = {code: rank for code, _, rank in lowvol_ranked}

    # 计算排名分数与综合评分
    results = {}
    for code in etf_codes:
        hr = heat_rank_map.get(code, total)
        mr = momentum_rank_map.get(code, total)
        lr = liquidity_rank_map.get(code, total)
        lvr = lowvol_rank_map.get(code, total)

        hrs = calc_rank_score(hr, total)
        mrs = calc_rank_score(mr, total)
        lrs = calc_rank_score(lr, total)
        lvrs = calc_rank_score(lvr, total)

        composite = calc_composite_score(hrs, mrs, lrs, lvrs)

        results[code] = {
            "heat_rank": hr,
            "momentum_rank": mr,
            "liquidity_rank": lr,
            "lowvol_rank": lvr,
            "heat_rank_score": round(hrs, 6),
            "momentum_rank_score": round(mrs, 6),
            "liquidity_rank_score": round(lrs, 6),
            "lowvol_rank_score": round(lvrs, 6),
            "composite_score": composite,
        }

    # 综合排名
    composite_items = [(c, r["composite_score"]) for c, r in results.items()]
    composite_ranked = rank_values(composite_items, "DESC")
    for code, _, rank in composite_ranked:
        results[code]["overall_rank"] = rank

    return results


def get_top_n(results: dict, n: int = 5) -> list:
    """获取Top N ETF。

    Returns:
        [{etf_code, ...ranking_fields}, ...] 按overall_rank升序
    """
    sorted_items = sorted(results.items(), key=lambda x: x[1]["overall_rank"])
    top = []
    for code, data in sorted_items[:n]:
        top.append({"etf_code": code, **data})
    return top
