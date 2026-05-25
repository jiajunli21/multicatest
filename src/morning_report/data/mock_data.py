"""Mock 数据生成器 — 为各因子计算提供模拟输入数据。

Status: [mock] for all generated data.
"""

import math
import random
from datetime import date, timedelta
from typing import Optional

from ..config import (
    MOCK_ETF_POOL,
    MOCK_SECTOR_MAP,
    MOCK_ETF_TAGS,
    MOCK_DEFAULT_TAGS,
    MockHeatFieldConfig,
    MockPriceConfig,
    MockTurnoverConfig,
)
from ..models import DailyPrice, ETFInfo, HeatRawFields, NewsItem, GuideContent


def _seeded_random(seed_str: str) -> random.Random:
    """确定性随机，同一ETF同一天生成一致Mock数据."""
    return random.Random(hash(seed_str))


def generate_etf_infos() -> list[ETFInfo]:
    """生成 ETF 基本信息列表."""
    result = []
    for etf in MOCK_ETF_POOL:
        code = etf["code"]
        sector = MOCK_SECTOR_MAP.get(code, "其他")
        tags = MOCK_ETF_TAGS.get(code, list(MOCK_DEFAULT_TAGS))
        result.append(ETFInfo(code=code, name=etf["name"], sector=sector, tags=tags))
    return result


def generate_heat_raw_fields(
    etf_code: str,
    target_date: date,
    config: Optional[MockHeatFieldConfig] = None,
) -> HeatRawFields:
    """为单个 ETF 生成单日热度原始字段 Mock 数据."""
    cfg = config or MockHeatFieldConfig()
    rng = _seeded_random(f"{etf_code}_{target_date.isoformat()}")

    # 用 lognormal 确保正值
    sousuo_uv = max(0, rng.gauss(cfg.sousuo_uv_mean, cfg.sousuo_uv_std))
    sousuo_click_uv = max(0, rng.gauss(cfg.sousuo_click_uv_mean, cfg.sousuo_click_uv_std))
    fenshi_uv = max(0, rng.gauss(cfg.fenshi_uv_mean, cfg.fenshi_uv_std))
    add_uv = max(0, rng.gauss(cfg.add_uv_mean, cfg.add_uv_std))
    buy_uv = max(0, rng.gauss(cfg.buy_uv_mean, cfg.buy_uv_std))

    return HeatRawFields(
        date=target_date,
        etf_code=etf_code,
        sousuo_uv=round(sousuo_uv, 2),
        sousuo_click_uv=round(sousuo_click_uv, 2),
        fenshi_uv=round(fenshi_uv, 2),
        add_uv=round(add_uv, 2),
        buy_uv=round(buy_uv, 2),
    )


def generate_heat_raw_fields_window(
    etf_code: str,
    end_date: date,
    window: int = 20,
    config: Optional[MockHeatFieldConfig] = None,
) -> list[HeatRawFields]:
    """生成 T-WINDOW+1 至 T 日的热度原始字段序列."""
    result = []
    for i in range(window - 1, -1, -1):
        d = end_date - timedelta(days=i)
        result.append(generate_heat_raw_fields(etf_code, d, config))
    return result


def generate_price_series(
    etf_code: str,
    end_date: date,
    window: int = 22,
    config: Optional[MockPriceConfig] = None,
) -> list[DailyPrice]:
    """生成收盘价序列 Mock 数据（几何随机游走）."""
    cfg = config or MockPriceConfig()
    rng = _seeded_random(f"{etf_code}_price_series")

    base_price = max(0.3, rng.gauss(cfg.base_price_mean, cfg.base_price_std))
    prices = []
    current_price = base_price

    today = date.today()
    for i in range(window - 1, -1, -1):
        d = end_date - timedelta(days=i)
        if d > today:
            continue
        daily_return = rng.gauss(cfg.daily_return_mean, cfg.daily_return_std)
        current_price = current_price * (1 + daily_return)
        prices.append(DailyPrice(
            date=d,
            etf_code=etf_code,
            close_price=round(current_price, 4),
            turnover=0.0,  # 成交额单独生成
        ))

    # 反转使最早日期在前
    prices.sort(key=lambda p: p.date)
    return prices


def generate_turnover_series(
    etf_code: str,
    price_series: list[DailyPrice],
    config: Optional[MockTurnoverConfig] = None,
) -> list[DailyPrice]:
    """为已有价格序列填充成交额 Mock 数据."""
    cfg = config or MockTurnoverConfig()
    rng = _seeded_random(f"{etf_code}_turnover")

    for p in price_series:
        turnover = max(0, rng.gauss(cfg.turnover_mean, cfg.turnover_std))
        p.turnover = round(turnover, 2)

    return price_series


def generate_mock_news(count: int = 10) -> list[NewsItem]:
    """生成 Mock 资讯列表."""
    templates = [
        ("A股早盘低开高走，ETF市场交投活跃", "今日A股三大指数低开后震荡走高，ETF市场成交额突破千亿"),
        ("政策利好持续释放，宽基ETF获资金青睐", "近期多项稳增长政策出台，沪深300ETF、中证500ETF等宽基产品持续获资金净申购"),
        ("科技创新主题ETF表现亮眼", "科创50ETF、芯片ETF等科技主题产品近一周涨幅居前"),
        ("港股ETF反弹，南向资金加速流入", "恒生科技ETF、港股消费ETF等产品近期表现强势，南向资金连续多日净流入"),
        ("黄金ETF避险需求上升", "国际金价高位震荡，黄金ETF成为资金避风港"),
        ("新能源板块回调，相关ETF承压", "光伏ETF、新能源车ETF今日出现调整，部分资金选择获利了结"),
        ("医药ETF底部反弹，机构看好后市", "医药板块经过前期调整后迎来反弹，医疗ETF、医药ETF成交放量"),
        ("红利策略ETF持续受捧", "在低利率环境下，红利ETF、银行ETF等高股息产品持续受到稳健资金关注"),
        ("ETF互联互通扩容，跨境产品迎新机", "ETF互联互通标的进一步扩大，为投资者提供更多跨境配置选择"),
        ("债券ETF规模突破新高", "国债ETF、短融ETF等固收类产品规模持续增长，反映市场避险情绪升温"),
    ]
    result = []
    today = date.today()
    rng = random.Random(42)
    for i, (title, summary) in enumerate(templates[:count]):
        t = datetime.combine(today, datetime.min.time()).replace(
            hour=8 + i % 12,
            minute=rng.randint(0, 59)
        )
        result.append(NewsItem(
            title=title,
            summary=summary,
            time=t,
            source="早盘宝资讯",
        ))
    return result


def generate_mock_guide() -> GuideContent:
    """生成 Mock 指南内容."""
    return GuideContent(
        content=(
            "# 早盘宝使用指南\n\n"
            "## 功能介绍\n"
            "早盘宝为您提供每个交易日的ETF早盘关注参考，"
            "基于热度、动量、流动性、低波四维因子综合评分，"
            "帮助您快速了解当日市场关注焦点。\n\n"
            "## 评分说明\n"
            "- 热度因子（50%）：反映市场搜索和关注热度\n"
            "- 动量因子（35%）：反映近期价格趋势\n"
            "- 流动性因子（10%）：反映成交活跃度\n"
            "- 低波因子（5%）：反映价格波动风险\n\n"
            "## 风险提示\n"
            "本内容仅供参考，不构成投资建议。投资有风险，入市需谨慎。"
        ),
        update_time=datetime.now(),
    )
