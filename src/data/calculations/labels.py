"""标签计算。[default]/[mock]

AD-008: 谨慎参与/积极参与标签 — 基于20日动量中位数 [default]
  20日动量中位数 < -0.03 → "谨慎参与"
  20日动量中位数 >= -0.03 → "积极参与"

AD-009: 个基标签 — Mock静态标签 [mock]
  [pending: 真实AI标签]
"""

from typing import Optional


def calc_market_tag(momentum_median_20d: Optional[float]) -> str:
    """计算大盘标签。

    Args:
        momentum_median_20d: 20日动量中位数

    Returns:
        "谨慎参与" 或 "积极参与"

    边界兜底 [default]:
    - momentum_median_20d 为None时返回 "积极参与" (默认乐观)
    """
    if momentum_median_20d is None:
        return "积极参与"
    if momentum_median_20d < -0.03:
        return "谨慎参与"
    return "积极参与"


def get_mock_fund_tags(etf_code: str, tag_config: dict) -> list:
    """获取Mock个基标签。

    Args:
        etf_code: ETF代码
        tag_config: 标签配置 {etf_code: [tag1, tag2, ...]}

    Returns:
        标签列表, 未配置时返回空列表
    """
    return tag_config.get(etf_code, [])
